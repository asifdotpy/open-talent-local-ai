"""
Data Enrichment Agent (Port 8097)
Local-first profile enrichment + Optional vendor APIs

Purpose:
- FREE Tier: Browser automation + public APIs (Google X-Ray, GitHub, etc.)
- PAID Tier: Vendor APIs (Proxycurl, Nubela) - optional for premium users
- Zero external API costs for free users
- GDPR compliant audit logging
- Caching to avoid duplicate enrichments

Author: OpenTalent Team
Updated: December 10, 2025 (Local-first FREE tier)
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from enum import Enum

import aiohttp
from fastapi import FastAPI
from pydantic import BaseModel, Field, HttpUrl

# Browser automation for Google X-Ray
try:
    from playwright.async_api import async_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Additional search libraries
try:
    from duckduckgo_search import DDGS
    from fake_useragent import UserAgent

    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False

# Shared modules
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "shared"))
from message_bus import MessageBus

# ============================
# Logging Setup
# ============================

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ============================
# Enums & Data Models
# ============================


class SourceMethod(str, Enum):
    """Free, legal sourcing methods"""

    GOOGLE_XRAY = "google_xray"
    GITHUB_PUBLIC = "github_public"
    STACKOVERFLOW = "stackoverflow"
    LINKEDIN_PUBLIC = "linkedin_public"
    TWITTER_SEARCH = "twitter_search"


class EnrichmentStatus(str, Enum):
    """Enrichment request status"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class EnrichmentRequest(BaseModel):
    """Request to enrich profiles"""

    pipeline_id: str
    profile_urls: list[HttpUrl]
    user_id: str


class EnrichmentResponse(BaseModel):
    """Response from enrichment request"""

    request_id: str
    status: EnrichmentStatus
    profiles_queued: int
    estimated_time_seconds: int


class AuditLog(BaseModel):
    """GDPR audit log entry"""

    timestamp: datetime
    user_id: str
    profile_url: str
    method: SourceMethod
    success: bool
    data_extracted: bool
    legal_basis: str = "legitimate_interest"


# ============================
# Global State
# ============================

profile_cache: dict[str, dict] = {}
audit_logs: list[AuditLog] = []
user_credits: dict[str, float] = {}
message_bus = MessageBus()


async def enrich_via_github(url: str) -> dict:
    """GitHub API enrichment (FREE, 60 requests/hour)"""
    try:
        if "github.com" not in url:
            raise ValueError("Not a GitHub URL")

        username = url.rstrip("/").split("/")[-1]

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.github.com/users/{username}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    profile = {
                        "source_url": url,
                        "source_method": "github_public",
                        "full_name": data.get("name"),
                        "headline": data.get("bio"),
                        "location": data.get("location"),
                        "email": data.get("email"),
                        "social_links": {
                            "github": url,
                            "blog": data.get("blog"),
                            "twitter": data.get("twitter_username"),
                        },
                        "accuracy_score": 0.8,
                        "enrichment_timestamp": datetime.now().isoformat(),
                    }
                    logger.info(f"✅ GitHub enrichment (FREE): {username}")
                    return profile
                else:
                    raise Exception(f"GitHub API error: {resp.status}")
    except Exception as e:
        logger.error(f"❌ GitHub enrichment failed: {str(e)}")
        raise


async def enrich_via_stackoverflow(query: str) -> dict:
    """Stack Overflow API enrichment (FREE, public API)"""
    try:
        base_url = "https://api.stackexchange.com/2.3"

        # Check if query is a user ID (numeric)
        if query.isdigit():
            user_id = query
            # Get detailed user info directly
            user_url = f"{base_url}/users/{user_id}?site=stackoverflow"
            async with aiohttp.ClientSession() as session:
                async with session.get(user_url) as user_resp:
                    if user_resp.status == 200:
                        user_data = await user_resp.json()
                        if user_data.get("items"):
                            profile = user_data["items"][0]

                            result = {
                                "source_url": f"https://stackoverflow.com/users/{user_id}",
                                "source_method": "stackoverflow",
                                "full_name": profile.get("display_name"),
                                "headline": f"Stack Overflow user with {profile.get('reputation', 0)} reputation",
                                "location": profile.get("location"),
                                "social_links": {
                                    "stackoverflow": f"https://stackoverflow.com/users/{user_id}",
                                    "website": profile.get("website_url"),
                                },
                                "stackoverflow_data": {
                                    "reputation": profile.get("reputation", 0),
                                    "badge_counts": profile.get("badge_counts", {}),
                                    "accept_rate": profile.get("accept_rate"),
                                    "account_id": profile.get("account_id"),
                                },
                                "accuracy_score": 0.8,  # Direct user ID lookup is accurate
                                "enrichment_timestamp": datetime.now().isoformat(),
                            }
                            logger.info(f"✅ Stack Overflow enrichment (FREE): User {user_id}")
                            return result
            raise Exception(f"User {user_id} not found on Stack Overflow")

        # Otherwise, search by name
        search_url = (
            f"{base_url}/users?order=desc&sort=reputation&inname={query}&site=stackoverflow"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    users = data.get("items", [])

                    if users:
                        # Take the most relevant user (highest reputation)
                        user = users[0]
                        user_id = user["user_id"]

                        # Get detailed user info
                        user_url = f"{base_url}/users/{user_id}?site=stackoverflow"
                        async with session.get(user_url) as user_resp:
                            if user_resp.status == 200:
                                user_data = await user_resp.json()
                                if user_data.get("items"):
                                    profile = user_data["items"][0]

                                    result = {
                                        "source_url": f"https://stackoverflow.com/users/{user_id}",
                                        "source_method": "stackoverflow",
                                        "full_name": profile.get("display_name"),
                                        "headline": f"Stack Overflow user with {profile.get('reputation', 0)} reputation",
                                        "location": profile.get("location"),
                                        "social_links": {
                                            "stackoverflow": f"https://stackoverflow.com/users/{user_id}",
                                            "website": profile.get("website_url"),
                                        },
                                        "stackoverflow_data": {
                                            "reputation": profile.get("reputation", 0),
                                            "badge_counts": profile.get("badge_counts", {}),
                                            "accept_rate": profile.get("accept_rate"),
                                            "account_id": profile.get("account_id"),
                                        },
                                        "accuracy_score": 0.7,
                                        "enrichment_timestamp": datetime.now().isoformat(),
                                    }
                                    logger.info(f"✅ Stack Overflow enrichment (FREE): {query}")
                                    return result

        # No results found
        raise Exception(f"No Stack Overflow users found for: {query}")

    except Exception as e:
        logger.error(f"❌ Stack Overflow enrichment failed: {str(e)}")
        raise


async def enrich_via_google_xray(name: str, location: str = None) -> dict:
    """Google X-Ray search enrichment (FREE, browser automation)"""
    if not PLAYWRIGHT_AVAILABLE:
        raise Exception("Playwright not available for Google X-Ray search")

    try:
        # Build search query for LinkedIn profiles
        query = f'"{name}"'
        if location:
            query += f' "{location}"'
        query += " site:linkedin.com/in"

        search_url = f"https://www.google.com/search?q={query}&num=10"

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--no-first-run",
                    "--no-zygote",
                    "--single-process",  # <- this one doesn't work in Windows
                    "--disable-gpu",
                ],
            )
            try:
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = await context.new_page()

                # Add random delay to appear more human
                await asyncio.sleep(1 + (id(name) % 3))  # Random delay 1-3 seconds

                await page.goto(search_url, wait_until="domcontentloaded")

                # Wait for search results with longer timeout
                await page.wait_for_selector("div.g, div[data-ved]", timeout=15000)

                # Extract LinkedIn profile links from search results
                linkedin_links = await page.query_selector_all('a[href*="linkedin.com/in"]')

                if linkedin_links:
                    # Take the first LinkedIn profile link
                    first_link = linkedin_links[0]
                    profile_url = await first_link.get_attribute("href")

                    if profile_url:
                        # Clean up the URL (remove Google redirect)
                        if "url=" in profile_url:
                            profile_url = profile_url.split("url=")[1].split("&")[0]
                        elif profile_url.startswith("/url?"):
                            profile_url = profile_url.split("url=")[1].split("&")[0]

                        # Add delay before visiting LinkedIn
                        await asyncio.sleep(2)

                        # Visit the LinkedIn profile
                        await page.goto(profile_url, wait_until="domcontentloaded")
                        await page.wait_for_load_state("networkidle", timeout=10000)

                        # Extract public profile data
                        name_element = await page.query_selector(
                            'h1.text-heading-xlarge, h1[data-test-id="hero__page__title"]'
                        )
                        headline_element = await page.query_selector(
                            ".text-body-medium, .pv-text-details__left-panel .text-body-medium"
                        )
                        location_element = await page.query_selector(
                            ".text-body-small.inline.t-black--light.break-words, .pv-text-details__left-panel .text-body-small"
                        )

                        full_name = await name_element.text_content() if name_element else name
                        headline = (
                            await headline_element.text_content() if headline_element else None
                        )
                        location = (
                            await location_element.text_content() if location_element else location
                        )

                        # Try to extract email from public contact info
                        email = None
                        try:
                            contact_link = await page.query_selector('a[href*="mailto:"]')
                            if contact_link:
                                mailto_href = await contact_link.get_attribute("href")
                                if mailto_href and mailto_href.startswith("mailto:"):
                                    email = mailto_href.replace("mailto:", "")
                        except:
                            pass

                        result = {
                            "source_url": profile_url,
                            "source_method": "google_xray",
                            "full_name": full_name.strip() if full_name else name,
                            "headline": headline.strip() if headline else None,
                            "location": location.strip() if location else None,
                            "email": email,
                            "social_links": {"linkedin": profile_url},
                            "google_search_query": query,
                            "accuracy_score": 0.3,  # Lower confidence due to search results
                            "enrichment_timestamp": datetime.now().isoformat(),
                        }

                        logger.info(f"✅ Google X-Ray enrichment (FREE): {name}")
                        return result

                # No LinkedIn profiles found
                raise Exception(f"No LinkedIn profiles found in Google search for: {name}")

            finally:
                await browser.close()

    except Exception as e:
        logger.error(f"❌ Google X-Ray enrichment failed: {str(e)}")
        raise


async def candidate_search_duckduckgo(query: str, max_results: int = 5) -> list[dict]:
    """Search for candidates using DuckDuckGo (FREE, no blocks)"""
    if not DUCKDUCKGO_AVAILABLE:
        raise Exception("DuckDuckGo search not available")

    try:
        candidates = []

        with DDGS() as ddgs:
            # Search for LinkedIn profiles - use broader search terms
            linkedin_query = f"{query} linkedin profile"
            linkedin_results = list(
                ddgs.text(linkedin_query, max_results=max_results * 2)
            )  # Get more results to filter

            logger.info(
                f"DuckDuckGo LinkedIn search: '{linkedin_query}' found {len(linkedin_results)} results"
            )

            for result in linkedin_results:
                logger.info(f"LinkedIn result: {result}")

                if isinstance(result, dict):
                    title = result.get("title", "").strip()
                    href = result.get("href", "").strip()
                    body = result.get("body", "").strip()

                    # Look for LinkedIn profile URLs
                    if "linkedin.com/in/" in href or "linkedin.com/pub/" in href:
                        # Extract name from title or URL
                        name = title.replace(" | LinkedIn", "").replace(" - LinkedIn", "").strip()
                        if not name or name in ["LinkedIn", "Python Developer"]:
                            # Try to extract from URL
                            if "linkedin.com/in/" in href:
                                path_parts = (
                                    href.split("linkedin.com/in/")[1].split("/")[0].split("?")[0]
                                )
                                name = path_parts.replace("-", " ").title()

                        if name and len(name) > 2:  # Avoid very short names
                            candidate = {
                                "name": name,
                                "headline": body,
                                "linkedin_url": href,
                                "source": "duckduckgo_linkedin",
                                "search_query": linkedin_query,
                                "accuracy_score": 0.4,
                            }
                            candidates.append(candidate)

            # Search for GitHub profiles
            github_query = f"{query} github"
            github_results = list(ddgs.text(github_query, max_results=max_results))

            logger.info(
                f"DuckDuckGo GitHub search: '{github_query}' found {len(github_results)} results"
            )

            for result in github_results:
                logger.info(f"GitHub result: {result}")

                if isinstance(result, dict):
                    href = result.get("href", "").strip()
                    body = result.get("body", "").strip()

                    if "github.com/" in href:
                        username = href.split("github.com/")[1].split("/")[0].split("?")[0]
                        if username and username != query.lower() and len(username) > 2:
                            candidate = {
                                "name": username,
                                "headline": body,
                                "github_url": f"https://github.com/{username}",
                                "source": "duckduckgo_github",
                                "search_query": github_query,
                                "accuracy_score": 0.5,
                            }
                            candidates.append(candidate)

        logger.info(
            f"✅ DuckDuckGo candidate search: Found {len(candidates)} candidates for '{query}'"
        )
        return candidates

    except Exception as e:
        logger.error(f"❌ DuckDuckGo candidate search failed: {str(e)}")
        raise


async def candidate_search_combined(
    query: str, location: str = None, skills: str = None, max_results: int = 10
) -> list[dict]:
    """
    Comprehensive candidate search using multiple FREE methods
    Returns list of potential candidates with their profiles
    """
    candidates = []
    search_terms = [query]

    if location:
        search_terms.append(location)
    if skills:
        search_terms.append(skills)

    full_query = " ".join(search_terms)

    try:
        # Method 1: DuckDuckGo search (most reliable) - DISABLED for now due to LinkedIn blocking
        if DUCKDUCKGO_AVAILABLE and False:  # Temporarily disabled
            try:
                ddg_candidates = await candidate_search_duckduckgo(
                    full_query, max_results=max_results // 2
                )
                candidates.extend(ddg_candidates)
            except Exception as e:
                logger.warning(f"DuckDuckGo search failed: {str(e)}")

        # Method 2: Stack Overflow user search
        try:
            # For complex queries, try searching by individual skills
            query_parts = full_query.split()
            search_terms = []

            # Extract potential skills (programming languages, frameworks, etc.)
            skills_keywords = [
                "python",
                "django",
                "react",
                "javascript",
                "java",
                "c++",
                "c#",
                "php",
                "ruby",
                "go",
                "rust",
                "tensorflow",
                "pytorch",
                "machine learning",
                "ml",
                "ai",
                "data science",
                "web development",
            ]

            for part in query_parts:
                if part.lower() in skills_keywords:
                    search_terms.append(part)

            # If we found skills, search for users with those skills
            if search_terms:
                found_candidates = []
                for skill in search_terms[:3]:  # Limit to 3 skills to avoid too broad search
                    try:
                        so_results = await enrich_via_stackoverflow(skill)
                        if so_results and so_results.get("full_name"):
                            candidate = {
                                "name": so_results.get("full_name", "Unknown"),
                                "headline": f"Developer skilled in {skill}",
                                "location": so_results.get("location", ""),
                                "stackoverflow_url": so_results.get("source_url", ""),
                                "stackoverflow_data": so_results.get("stackoverflow_data", {}),
                                "source": "stackoverflow_search",
                                "search_query": full_query,
                                "accuracy_score": 0.6,
                            }
                            found_candidates.append(candidate)
                            if len(found_candidates) >= 2:  # Get a few candidates
                                break
                    except Exception as e:
                        logger.warning(f"Stack Overflow skill search failed for {skill}: {str(e)}")

                candidates.extend(found_candidates)
            else:
                # Fallback to direct search
                try:
                    so_results = await enrich_via_stackoverflow(full_query)
                    if so_results:
                        candidate = {
                            "name": so_results.get("full_name", "Unknown"),
                            "headline": so_results.get("headline", ""),
                            "location": so_results.get("location", ""),
                            "stackoverflow_url": so_results.get("source_url", ""),
                            "stackoverflow_data": so_results.get("stackoverflow_data", {}),
                            "source": "stackoverflow_search",
                            "search_query": full_query,
                            "accuracy_score": so_results.get("accuracy_score", 0.7),
                        }
                        candidates.append(candidate)
                except Exception as e:
                    logger.warning(f"Stack Overflow direct search failed: {str(e)}")
        except Exception as e:
            logger.warning(f"Stack Overflow search failed: {str(e)}")

        # Method 3: Google X-Ray (last resort, may be blocked) - IMPROVED
        if PLAYWRIGHT_AVAILABLE and len(candidates) < max_results:
            try:
                # Try multiple search strategies
                search_queries = [
                    f'"{query}" {location or ""} site:linkedin.com/in',
                    f"{query} {location or ''} linkedin developer",
                    f"{query} {skills or ''} profile linkedin",
                ]

                for search_query in search_queries:
                    if len(candidates) >= max_results:
                        break
                    try:
                        logger.info(f"Trying Google X-Ray with: {search_query}")
                        xray_result = await enrich_via_google_xray(search_query.strip(), None)
                        if xray_result:
                            candidate = {
                                "name": xray_result.get("full_name", query),
                                "headline": xray_result.get("headline", ""),
                                "location": xray_result.get("location", ""),
                                "linkedin_url": xray_result.get("source_url", ""),
                                "email": xray_result.get("email"),
                                "source": "google_xray",
                                "search_query": full_query,
                                "accuracy_score": 0.3,
                            }
                            candidates.append(candidate)
                            logger.info(f"Google X-Ray found candidate: {candidate['name']}")
                            break  # Found one, move on
                    except Exception as e:
                        logger.warning(
                            f"Google X-Ray attempt failed for '{search_query}': {str(e)}"
                        )
                        continue

            except Exception as e:
                logger.warning(f"Google X-Ray search failed: {str(e)}")

        # Remove duplicates based on name similarity
        unique_candidates = []
        seen_names = set()

        for candidate in candidates:
            name_key = candidate.get("name", "").lower().strip()
            if name_key and name_key not in seen_names:
                seen_names.add(name_key)
                unique_candidates.append(candidate)

        # Sort by accuracy score
        unique_candidates.sort(key=lambda x: x.get("accuracy_score", 0), reverse=True)

        logger.info(
            f"✅ Combined candidate search: Found {len(unique_candidates)} unique candidates for '{full_query}'"
        )
        return unique_candidates[:max_results]

    except Exception as e:
        logger.error(f"❌ Combined candidate search failed: {str(e)}")
        return []


async def enrich_profile_auto(url: str, user_id: str) -> dict:
    """
    Auto-enrich using best available method
    Priority: Cache → GitHub → Stack Overflow → Google X-Ray → Fallback
    """
    # Check cache first
    cache_key = f"profile:{url}"
    if cache_key in profile_cache:
        cached = profile_cache[cache_key]
        if cached["expires_at"] > datetime.now():
            logger.info(f"✅ Cache HIT: {url}")
            return cached["data"]

    # Try GitHub
    if "github.com" in url:
        try:
            profile = await enrich_via_github(url)
            # Cache it
            profile_cache[cache_key] = {
                "data": profile,
                "tier": "free",
                "cost": 0.0,
                "cached_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(days=30),
            }
            log_enrichment(
                user_id, url, SourceMethod.GITHUB_PUBLIC, success=True, data_extracted=True
            )
            return profile
        except Exception as e:
            logger.error(f"GitHub failed, trying other methods: {str(e)}")

    # Try Stack Overflow (for developer profiles)
    if "stackoverflow.com" in url:
        try:
            # Extract user ID from Stack Overflow URL
            if "/users/" in url:
                # URL format: https://stackoverflow.com/users/12345/username
                user_path = url.split("/users/")[1]
                user_id = user_path.split("/")[0]  # Extract the numeric ID
                if user_id.isdigit():
                    profile = await enrich_via_stackoverflow(user_id)
                else:
                    # Fallback to search if not a numeric ID
                    profile = await enrich_via_stackoverflow(user_path)
            else:
                # Not a user URL, search by the URL as name
                profile = await enrich_via_stackoverflow(url)

            profile_cache[cache_key] = {
                "data": profile,
                "tier": "free",
                "cost": 0.0,
                "cached_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(days=30),
            }
            log_enrichment(
                user_id, url, SourceMethod.STACKOVERFLOW, success=True, data_extracted=True
            )
            return profile
        except Exception as e:
            logger.error(f"Stack Overflow failed, trying Google X-Ray: {str(e)}")

    # Try Stack Overflow for non-HTTP URLs (names)
    if not url.startswith("http"):
        try:
            profile = await enrich_via_stackoverflow(url)
            profile_cache[cache_key] = {
                "data": profile,
                "tier": "free",
                "cost": 0.0,
                "cached_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(days=30),
            }
            log_enrichment(
                user_id, url, SourceMethod.STACKOVERFLOW, success=True, data_extracted=True
            )
            return profile
        except Exception as e:
            logger.error(f"Stack Overflow failed, trying Google X-Ray: {str(e)}")

    # Try Google X-Ray (for LinkedIn profiles or general search)
    try:
        # Extract name from LinkedIn URL or use as search term
        if "linkedin.com/in/" in url:
            # Extract name from LinkedIn URL
            path_parts = url.rstrip("/").split("/")
            if len(path_parts) > 0:
                name = path_parts[-1].replace("-", " ").title()
            else:
                name = "linkedin_user"
        else:
            name = url  # Use as search term

        profile = await enrich_via_google_xray(name)
        profile_cache[cache_key] = {
            "data": profile,
            "tier": "free",
            "cost": 0.0,
            "cached_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(days=30),
        }
        log_enrichment(user_id, url, SourceMethod.GOOGLE_XRAY, success=True, data_extracted=True)
        return profile
    except Exception as e:
        logger.error(f"Google X-Ray failed, using fallback: {str(e)}")

    # Fallback: minimal profile
    profile = {
        "source_url": url,
        "source_method": "unknown",
        "accuracy_score": 0.0,
        "enrichment_timestamp": datetime.now().isoformat(),
    }

    profile_cache[cache_key] = {
        "data": profile,
        "tier": "free",
        "cost": 0.0,
        "cached_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(days=30),
    }

    log_enrichment(user_id, url, SourceMethod.LINKEDIN_PUBLIC, success=False, data_extracted=False)
    return profile


# ============================
# Logging (GDPR)
# ============================


def log_enrichment(
    user_id: str,
    profile_url: str,
    method: SourceMethod,
    success: bool,
    data_extracted: bool = False,
    cost: float = 0.0,
):
    """Log enrichment for GDPR compliance"""
    log_entry = AuditLog(
        timestamp=datetime.now(),
        user_id=user_id,
        profile_url=profile_url,
        method=method,
        success=success,
        data_extracted=data_extracted,
    )
    audit_logs.append(log_entry)
    tier = "FREE" if cost == 0 else "PAID"
    status = "✅" if success else "❌"
    logger.info(f"{status} Audit: {user_id} → {profile_url} ({method.value}, {tier})")


# ============================
# Candidate Search Pipeline
# ============================


class PipelineStatus(str, Enum):
    """Pipeline execution status"""

    PENDING = "pending"
    SOURCING = "sourcing"
    ENRICHING = "enriching"
    COMPLETING = "completing"
    COMPLETED = "completed"
    FAILED = "failed"


class CandidateSearchPipeline:
    """Asynchronous pipeline for candidate search with progress tracking"""

    def __init__(self, request_id: str, pipeline_id: str, user_id: str):
        self.request_id = request_id
        self.pipeline_id = pipeline_id
        self.user_id = user_id
        self.status = PipelineStatus.PENDING
        self.start_time = datetime.now()
        self.end_time = None
        self.progress = {
            "sourcing_complete": False,
            "enrichment_complete": False,
            "presentation_complete": False,
        }
        self.results = {
            "candidates": [],
            "sources_searched": [],
            "errors": [],
            "stats": {"total_searched": 0, "total_enriched": 0, "total_failed": 0},
        }
        self.tasks = []  # Track running tasks

    async def update_status(self, new_status: PipelineStatus, message: str = None):
        """Update pipeline status and publish progress"""
        self.status = new_status
        progress_data = {
            "request_id": self.request_id,
            "pipeline_id": self.pipeline_id,
            "status": self.status.value,
            "progress": self.progress,
            "results": {
                "candidates_found": len(self.results["candidates"]),
                "sources_completed": len(self.results["sources_searched"]),
                "errors": len(self.results["errors"]),
            },
            "elapsed_seconds": (datetime.now() - self.start_time).total_seconds(),
        }

        if message:
            progress_data["message"] = message

        # Publish progress update
        await message_bus.publish_event(
            topic="agents:quality",
            source_agent="data-enrichment",
            message_type="candidate_search_progress",
            payload=progress_data,
        )

        logger.info(
            f"📊 Pipeline {self.request_id}: {self.status.value} - {len(self.results['candidates'])} candidates"
        )

    async def phase_sourcing(
        self, query: str, location: str = None, skills: str = None, max_results: int = 10
    ):
        """Phase 1: Concurrent data sourcing from multiple sources"""
        await self.update_status(PipelineStatus.SOURCING, "Starting multi-source candidate search")

        # Prepare search queries
        search_terms = [query]
        if location:
            search_terms.append(location)
        if skills:
            search_terms.append(skills)
        full_query = " ".join(search_terms)

        # Concurrent sourcing tasks
        sourcing_tasks = []

        # Task 1: Stack Overflow search (most reliable)
        if True:  # Always try Stack Overflow
            task = asyncio.create_task(self._source_stackoverflow(full_query, max_results))
            sourcing_tasks.append(task)
            self.tasks.append(task)

        # Task 2: Google X-Ray search (may be blocked)
        if PLAYWRIGHT_AVAILABLE:
            task = asyncio.create_task(self._source_google_xray(query, location, max_results))
            sourcing_tasks.append(task)
            self.tasks.append(task)

        # Task 3: DuckDuckGo search (if available)
        if DUCKDUCKGO_AVAILABLE:
            task = asyncio.create_task(self._source_duckduckgo(full_query, max_results))
            sourcing_tasks.append(task)
            self.tasks.append(task)

        # Wait for all sourcing to complete (with timeout)
        try:
            await asyncio.wait_for(
                asyncio.gather(*sourcing_tasks, return_exceptions=True), timeout=30.0
            )
        except TimeoutError:
            logger.warning(
                f"Pipeline {self.request_id}: Sourcing timeout, proceeding with partial results"
            )

        # Mark sourcing complete
        self.progress["sourcing_complete"] = True
        await self.update_status(
            PipelineStatus.SOURCING,
            f"Sourcing complete: {len(self.results['candidates'])} candidates found",
        )

    async def _source_stackoverflow(self, query: str, max_results: int):
        """Source candidates from Stack Overflow"""
        try:
            logger.info(f"🔍 Stack Overflow search: {query}")

            # Extract skills from query
            query_parts = query.split()
            skills_keywords = [
                "python",
                "django",
                "react",
                "javascript",
                "java",
                "c++",
                "c#",
                "php",
                "ruby",
                "go",
                "rust",
                "tensorflow",
                "pytorch",
                "machine learning",
                "ml",
                "ai",
                "data science",
                "web development",
            ]

            found_candidates = []
            skills_found = [part.lower() for part in query_parts if part.lower() in skills_keywords]

            if skills_found:
                # Search for top users in each skill
                for skill in skills_found[:3]:  # Limit to 3 skills
                    try:
                        so_results = await enrich_via_stackoverflow(skill)
                        if so_results and so_results.get("full_name"):
                            candidate = {
                                "name": so_results.get("full_name", "Unknown"),
                                "headline": f"Developer skilled in {skill}",
                                "location": so_results.get("location", ""),
                                "stackoverflow_url": so_results.get("source_url", ""),
                                "stackoverflow_data": so_results.get("stackoverflow_data", {}),
                                "source": "stackoverflow_search",
                                "search_query": query,
                                "accuracy_score": 0.6,
                                "needs_enrichment": True,
                            }
                            found_candidates.append(candidate)
                    except Exception as e:
                        logger.warning(f"Stack Overflow {skill} search failed: {str(e)}")
                        self.results["errors"].append(f"Stack Overflow {skill}: {str(e)}")

            # Add found candidates
            self.results["candidates"].extend(found_candidates)
            self.results["sources_searched"].append("stackoverflow")
            self.results["stats"]["total_searched"] += len(found_candidates)

            logger.info(f"✅ Stack Overflow: Found {len(found_candidates)} candidates")

        except Exception as e:
            logger.error(f"❌ Stack Overflow sourcing failed: {str(e)}")
            self.results["errors"].append(f"Stack Overflow: {str(e)}")

    async def _source_google_xray(self, query: str, location: str = None, max_results: int = 10):
        """Source candidates via Google X-Ray"""
        try:
            logger.info(f"🔍 Google X-Ray search: {query}")

            # Try multiple search strategies
            search_queries = [
                f'"{query}" site:linkedin.com/in',
                f"{query} linkedin developer",
                f"{query} profile linkedin",
            ]

            if location:
                search_queries = [f"{q} {location}" for q in search_queries]

            found_candidates = []
            for search_query in search_queries[:2]:  # Try first 2 strategies
                try:
                    logger.info(f"Trying Google X-Ray: {search_query}")
                    xray_result = await enrich_via_google_xray(search_query, None)
                    if xray_result:
                        candidate = {
                            "name": xray_result.get("full_name", query),
                            "headline": xray_result.get("headline", ""),
                            "location": xray_result.get("location", ""),
                            "linkedin_url": xray_result.get("source_url", ""),
                            "email": xray_result.get("email"),
                            "source": "google_xray",
                            "search_query": search_query,
                            "accuracy_score": 0.3,
                            "needs_enrichment": True,
                        }
                        found_candidates.append(candidate)
                        break  # Found one, that's enough
                except Exception as e:
                    logger.warning(f"Google X-Ray attempt failed for '{search_query}': {str(e)}")

            # Add found candidates
            self.results["candidates"].extend(found_candidates)
            self.results["sources_searched"].append("google_xray")
            self.results["stats"]["total_searched"] += len(found_candidates)

            logger.info(f"✅ Google X-Ray: Found {len(found_candidates)} candidates")

        except Exception as e:
            logger.error(f"❌ Google X-Ray sourcing failed: {str(e)}")
            self.results["errors"].append(f"Google X-Ray: {str(e)}")

    async def _source_duckduckgo(self, query: str, max_results: int = 10):
        """Source candidates via DuckDuckGo (currently disabled due to LinkedIn blocking)"""
        # DuckDuckGo LinkedIn search is currently not working due to LinkedIn blocking
        # This could be re-enabled if we find alternative search strategies
        self.results["sources_searched"].append("duckduckgo")
        logger.info("ℹ️ DuckDuckGo sourcing skipped (LinkedIn blocking)")

    async def phase_enrichment(self):
        """Phase 2: Enrich found candidates with additional data"""
        await self.update_status(PipelineStatus.ENRICHING, "Enriching candidate profiles")

        if not self.results["candidates"]:
            logger.info("No candidates to enrich")
            return

        # Enrich candidates that need it
        enrichment_tasks = []
        for i, candidate in enumerate(self.results["candidates"]):
            if candidate.get("needs_enrichment", False):
                task = asyncio.create_task(self._enrich_candidate(candidate, i))
                enrichment_tasks.append(task)
                self.tasks.append(task)

        # Wait for enrichment to complete
        if enrichment_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*enrichment_tasks, return_exceptions=True), timeout=20.0
                )
            except TimeoutError:
                logger.warning(f"Pipeline {self.request_id}: Enrichment timeout")

        self.progress["enrichment_complete"] = True
        await self.update_status(
            PipelineStatus.ENRICHING,
            f"Enrichment complete: {len(self.results['candidates'])} candidates enriched",
        )

    async def _enrich_candidate(self, candidate: dict, index: int):
        """Enrich a single candidate"""
        try:
            # Try to enrich via the candidate's URL if available
            enrichment_url = (
                candidate.get("linkedin_url")
                or candidate.get("github_url")
                or candidate.get("stackoverflow_url")
            )

            if enrichment_url:
                enriched_data = await enrich_profile_auto(enrichment_url, self.user_id)
                if enriched_data:
                    # Update candidate with enriched data
                    candidate.update(
                        {
                            "enriched_data": enriched_data,
                            "enrichment_timestamp": datetime.now().isoformat(),
                            "accuracy_score": min(
                                1.0, candidate.get("accuracy_score", 0) + 0.2
                            ),  # Boost accuracy
                        }
                    )
                    self.results["stats"]["total_enriched"] += 1
                    logger.info(f"✅ Enriched candidate {index}: {candidate.get('name')}")
                else:
                    self.results["stats"]["total_failed"] += 1
            else:
                self.results["stats"]["total_failed"] += 1

        except Exception as e:
            logger.error(f"❌ Failed to enrich candidate {index}: {str(e)}")
            self.results["stats"]["total_failed"] += 1

    async def phase_presentation(self, query: str, location: str = None, skills: str = None):
        """Phase 3: Format and present final results"""
        await self.update_status(PipelineStatus.COMPLETING, "Formatting final results")

        # Remove duplicates and sort by accuracy
        unique_candidates = []
        seen_names = set()

        for candidate in self.results["candidates"]:
            name_key = candidate.get("name", "").lower().strip()
            if name_key and name_key not in seen_names and len(name_key) > 2:
                seen_names.add(name_key)
                unique_candidates.append(candidate)

        # Sort by accuracy score (highest first)
        unique_candidates.sort(key=lambda x: x.get("accuracy_score", 0), reverse=True)

        # Limit results and update
        self.results["candidates"] = unique_candidates[:10]  # Max 10 results

        self.progress["presentation_complete"] = True
        self.end_time = datetime.now()

        await self.update_status(
            PipelineStatus.COMPLETED,
            f"Search complete: {len(self.results['candidates'])} unique candidates found",
        )

    async def execute(
        self, query: str, location: str = None, skills: str = None, max_results: int = 10
    ):
        """Execute the complete pipeline"""
        try:
            # Phase 1: Data Sourcing
            await self.phase_sourcing(query, location, skills, max_results)

            # Phase 2: Enrichment
            await self.phase_enrichment()

            # Phase 3: Presentation
            await self.phase_presentation(query, location, skills)

            # Publish final results
            await self._publish_final_results(query, location, skills)

        except Exception as e:
            logger.error(f"❌ Pipeline {self.request_id} failed: {str(e)}")
            self.status = PipelineStatus.FAILED
            await self._publish_error(str(e))

    async def _publish_final_results(self, query: str, location: str, skills: str):
        """Publish final search results"""
        await message_bus.publish_event(
            topic="agents:quality",
            source_agent="data-enrichment",
            message_type="candidate_search_complete",
            payload={
                "request_id": self.request_id,
                "pipeline_id": self.pipeline_id,
                "candidates": self.results["candidates"],
                "search_query": query,
                "search_filters": {"location": location, "skills": skills},
                "total_found": len(self.results["candidates"]),
                "sources_searched": self.results["sources_searched"],
                "stats": self.results["stats"],
                "errors": self.results["errors"],
                "execution_time_seconds": (self.end_time - self.start_time).total_seconds(),
                "source": "candidate_search",
                "tier": "free",
                "cost": 0.0,
            },
        )

        logger.info(
            f"✅ Pipeline {self.request_id} complete: {len(self.results['candidates'])} candidates found in {(self.end_time - self.start_time).total_seconds():.1f}s"
        )

    async def _publish_error(self, error: str):
        """Publish error results"""
        await message_bus.publish_event(
            topic="agents:quality",
            source_agent="data-enrichment",
            message_type="candidate_search_failed",
            payload={
                "request_id": self.request_id,
                "pipeline_id": self.pipeline_id,
                "error": error,
                "sources_searched": self.results["sources_searched"],
                "errors": self.results["errors"],
            },
        )


# Global pipeline registry
active_pipelines: dict[str, CandidateSearchPipeline] = {}


async def handle_enrichment_request(message: dict):
    """Handle enrichment request from message bus"""
    pipeline_id = message.get("pipeline_id")
    profile_urls = message.get("profile_urls", [])
    user_id = message.get("user_id")

    logger.info(f"📨 Enrichment request: {len(profile_urls)} profiles for pipeline {pipeline_id}")

    # Process each profile URL
    enriched_profiles = []
    for url in profile_urls:
        try:
            profile = await enrich_profile_auto(url, user_id)
            enriched_profiles.append(profile)
            logger.info(f"✅ Enriched: {url}")
        except Exception as e:
            logger.error(f"❌ Failed to enrich {url}: {str(e)}")
            # Add minimal profile for failed enrichments
            enriched_profiles.append(
                {
                    "source_url": url,
                    "source_method": "unknown",
                    "accuracy_score": 0.0,
                    "enrichment_timestamp": datetime.now().isoformat(),
                    "error": str(e),
                }
            )

    # Publish results
    await message_bus.publish_event(
        topic="agents:quality",
        source_agent="data-enrichment",
        message_type="enrichment_complete",
        payload={
            "pipeline_id": pipeline_id,
            "enriched_profiles": enriched_profiles,
            "total_processed": len(enriched_profiles),
            "tier": "free",
            "cost": 0.0,
        },
    )

    logger.info(
        f"✅ Enrichment complete: {len(enriched_profiles)} profiles for pipeline {pipeline_id}"
    )


async def handle_candidate_search_request(message: dict):
    """Handle candidate search request with pipeline"""
    query = message.get("query")
    location = message.get("location")
    skills = message.get("skills")
    max_results = message.get("max_results", 10)
    pipeline_id = message.get("pipeline_id")
    user_id = message.get("user_id")
    request_id = message.get("request_id", f"search_{pipeline_id}_{datetime.now().timestamp()}")

    logger.info(
        f"🔍 Starting candidate search pipeline: '{query}' (location: {location}, skills: {skills})"
    )

    # Create and register pipeline
    pipeline = CandidateSearchPipeline(request_id, pipeline_id, user_id)
    active_pipelines[request_id] = pipeline

    # Execute pipeline asynchronously
    asyncio.create_task(pipeline.execute(query, location, skills, max_results))

    logger.info(f"📊 Pipeline {request_id} started - will report progress asynchronously")


# ============================
# Application Lifecycle
# ============================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown"""
    logger.info("🚀 Data Enrichment Agent starting on port 8097...")

    await message_bus.connect()
    await message_bus.subscribe(topics=["agents:enrichment"], callback=handle_enrichment_request)

    # Start pipeline cleanup task
    cleanup_task = asyncio.create_task(pipeline_cleanup_worker())

    logger.info("✅ FREE Tier: Browser-based enrichment (Google X-Ray, GitHub, etc.)")
    logger.info("💰 PAID Tier: Vendor APIs (optional - coming soon)")
    logger.info("✅ Data Enrichment Agent ready!")

    yield

    logger.info("Shutting down...")

    # Cancel cleanup task
    cleanup_task.cancel()

    # Cancel all active pipelines
    for pipeline in active_pipelines.values():
        for task in pipeline.tasks:
            if not task.done():
                task.cancel()

    await message_bus.disconnect()


async def pipeline_cleanup_worker():
    """Background task to clean up completed pipelines"""
    while True:
        try:
            # Clean up completed/failed pipelines older than 5 minutes
            cutoff_time = datetime.now() - timedelta(minutes=5)
            to_remove = []

            for req_id, pipeline in active_pipelines.items():
                if pipeline.status in [PipelineStatus.COMPLETED, PipelineStatus.FAILED]:
                    if pipeline.end_time and pipeline.end_time < cutoff_time:
                        to_remove.append(req_id)
                elif pipeline.start_time < (datetime.now() - timedelta(hours=1)):
                    # Also clean up stuck pipelines after 1 hour
                    to_remove.append(req_id)

            for req_id in to_remove:
                del active_pipelines[req_id]
                logger.info(f"🧹 Cleaned up pipeline {req_id}")

            await asyncio.sleep(60)  # Check every minute

        except Exception as e:
            logger.error(f"Pipeline cleanup error: {str(e)}")
            await asyncio.sleep(60)


app = FastAPI(
    title="Data Enrichment Agent",
    description="Local-first profile enrichment (FREE) + Vendor APIs (PAID optional)",
    lifespan=lifespan,
)


# ============================
# REST API Endpoints
# ============================


@app.get("/health")
async def health_check():
    """Health check"""
    playwright_status = "✅ Available" if PLAYWRIGHT_AVAILABLE else "❌ Not installed"
    duckduckgo_status = "✅ Available" if DUCKDUCKGO_AVAILABLE else "❌ Not installed"
    candidate_search_status = (
        "✅ Ready" if (PLAYWRIGHT_AVAILABLE and DUCKDUCKGO_AVAILABLE) else "⚠️ Limited"
    )

    return {
        "status": "✅ healthy",
        "agent": "data-enrichment",
        "port": 8097,
        "active_pipelines": len(active_pipelines),
        "tiers": {
            "free": {
                "status": "✅ Available",
                "methods": {
                    "github_public": "✅ Ready",
                    "stackoverflow": "✅ Ready",
                    "google_xray": playwright_status,
                    "duckduckgo_search": duckduckgo_status,
                    "candidate_search_pipeline": "✅ Ready",
                },
            },
            "paid": {"status": "🔄 Coming soon", "vendors": ["proxycurl", "nubela"]},
        },
    }


@app.post("/enrich", response_model=EnrichmentResponse)
async def enrich_profiles(request: EnrichmentRequest):
    """
    Enrich profiles using FREE methods

    Cost: $0.00
    Speed: 2-5 seconds per profile
    No API keys required
    """
    request_id = f"enrich_{request.pipeline_id}_{datetime.now().timestamp()}"

    asyncio.create_task(
        handle_enrichment_request(
            {
                "pipeline_id": request.pipeline_id,
                "profile_urls": [str(url) for url in request.profile_urls],
                "user_id": request.user_id,
            }
        )
    )

    return EnrichmentResponse(
        request_id=request_id,
        status=EnrichmentStatus.PENDING,
        profiles_queued=len(request.profile_urls),
        estimated_time_seconds=len(request.profile_urls) * 3,
    )


class CandidateSearchRequest(BaseModel):
    """Request to search for candidates"""

    query: str = Field(..., description="Search query (name, skills, etc.)")
    location: str | None = Field(None, description="Location filter")
    skills: str | None = Field(None, description="Skills filter")
    max_results: int = Field(10, description="Maximum results to return")
    pipeline_id: str = Field(..., description="Pipeline ID for tracking")
    user_id: str = Field(..., description="User ID for audit logging")


class CandidateSearchResponse(BaseModel):
    """Response from candidate search"""

    request_id: str
    status: EnrichmentStatus
    candidates_found: int
    estimated_time_seconds: int
    pipeline_status_url: str


@app.post("/search/candidates", response_model=CandidateSearchResponse)
async def search_candidates(request: CandidateSearchRequest):
    """
    Search for candidates using asynchronous pipeline

    Pipeline Phases:
    1. Data Sourcing: Concurrent search across Stack Overflow, Google X-Ray
    2. Enrichment: Profile enrichment and data validation
    3. Presentation: Results formatting and deduplication

    Returns: Pipeline request ID for status tracking
    Cost: $0.00
    """
    request_id = f"search_{request.pipeline_id}_{datetime.now().timestamp()}"

    # Start pipeline asynchronously
    asyncio.create_task(
        handle_candidate_search_request(
            {
                "query": request.query,
                "location": request.location,
                "skills": request.skills,
                "max_results": request.max_results,
                "pipeline_id": request.pipeline_id,
                "user_id": request.user_id,
                "request_id": request_id,
            }
        )
    )

    return CandidateSearchResponse(
        request_id=request_id,
        status=EnrichmentStatus.PENDING,
        candidates_found=0,  # Will be updated as pipeline progresses
        estimated_time_seconds=30,  # Pipeline takes longer but provides progress
        pipeline_status_url=f"/pipeline/{request_id}/status",
    )


@app.get("/methods")
async def list_methods():
    """List enrichment methods"""
    playwright_status = "✅ Ready" if PLAYWRIGHT_AVAILABLE else "❌ Playwright not installed"
    duckduckgo_status = "✅ Ready" if DUCKDUCKGO_AVAILABLE else "❌ DuckDuckGo not installed"
    candidate_search_status = (
        "✅ Ready" if (PLAYWRIGHT_AVAILABLE and DUCKDUCKGO_AVAILABLE) else "⚠️ Limited"
    )

    return {
        "free_tier": [
            {
                "method": "github_public",
                "cost": "$0.00",
                "quality": "⭐⭐⭐⭐ (High)",
                "speed": "1-2 sec",
                "coverage": "500M+ profiles",
                "status": "✅ Ready",
                "legal": "✅ GDPR compliant",
            },
            {
                "method": "stackoverflow",
                "cost": "$0.00",
                "quality": "⭐⭐⭐ (Good)",
                "speed": "2-3 sec",
                "coverage": "20M+ profiles",
                "status": "✅ Ready",
                "legal": "✅ GDPR compliant",
            },
            {
                "method": "google_xray",
                "cost": "$0.00",
                "quality": "⭐⭐ (Basic)",
                "speed": "3-5 sec",
                "coverage": "Public LinkedIn",
                "status": playwright_status,
                "legal": "✅ GDPR compliant",
            },
            {
                "method": "duckduckgo_search",
                "cost": "$0.00",
                "quality": "⭐⭐⭐ (Good)",
                "speed": "2-4 sec",
                "coverage": "Web-wide search",
                "status": duckduckgo_status,
                "legal": "✅ GDPR compliant",
            },
            {
                "method": "candidate_search_pipeline",
                "cost": "$0.00",
                "quality": "⭐⭐⭐⭐ (Very Good)",
                "speed": "10-30 sec",
                "coverage": "Multi-source search",
                "status": candidate_search_status,
                "description": "Asynchronous pipeline: Phase 1 (Sourcing) → Phase 2 (Enrichment) → Phase 3 (Presentation). Provides real-time progress updates.",
                "features": [
                    "Concurrent multi-source search",
                    "Real-time progress tracking",
                    "Automatic deduplication",
                    "Profile enrichment",
                ],
                "legal": "✅ GDPR compliant",
            },
        ],
        "paid_tier": [
            {
                "vendor": "proxycurl",
                "cost": "$0.04/profile",
                "quality": "⭐⭐⭐⭐⭐ (Excellent)",
                "status": "🔄 Coming soon",
            },
            {
                "vendor": "nubela",
                "cost": "$0.02/profile",
                "quality": "⭐⭐⭐⭐ (Very Good)",
                "status": "🔄 Coming soon",
            },
        ],
    }


@app.get("/credits/{user_id}")
async def get_credits(user_id: str):
    """Get user credit balance (PAID tier)"""
    return {
        "user_id": user_id,
        "balance": user_credits.get(user_id, 0.0),
        "tier": "free",
        "message": "FREE tier - no credits needed",
    }


@app.get("/audit-logs")
async def get_audit_logs(user_id: str | None = None, limit: int = 100):
    """Get GDPR audit logs"""
    logs = audit_logs
    if user_id:
        logs = [log for log in logs if log.user_id == user_id]

    return {"total": len(logs[-limit:]), "logs": logs[-limit:]}


@app.get("/cache/stats")
async def cache_stats():
    """Cache statistics"""
    return {"cached_profiles": len(profile_cache), "total_savings_usd": 0.0, "tier": "free"}


@app.get("/pipeline/{request_id}/status")
async def get_pipeline_status(request_id: str):
    """Get status of a running pipeline"""
    if request_id not in active_pipelines:
        return {"error": "Pipeline not found", "request_id": request_id}

    pipeline = active_pipelines[request_id]
    return {
        "request_id": request_id,
        "pipeline_id": pipeline.pipeline_id,
        "status": pipeline.status.value,
        "progress": pipeline.progress,
        "candidates_found": len(pipeline.results["candidates"]),
        "sources_completed": len(pipeline.results["sources_searched"]),
        "errors_count": len(pipeline.results["errors"]),
        "elapsed_seconds": (datetime.now() - pipeline.start_time).total_seconds(),
        "estimated_completion_seconds": max(
            0, 30 - (datetime.now() - pipeline.start_time).total_seconds()
        ),
    }


@app.get("/pipelines/active")
async def list_active_pipelines():
    """List all active pipelines"""
    return {
        "active_pipelines": [
            {
                "request_id": req_id,
                "pipeline_id": pipeline.pipeline_id,
                "status": pipeline.status.value,
                "candidates_found": len(pipeline.results["candidates"]),
                "elapsed_seconds": (datetime.now() - pipeline.start_time).total_seconds(),
                "progress": pipeline.progress,
            }
            for req_id, pipeline in active_pipelines.items()
        ],
        "total_active": len(active_pipelines),
    }


@app.delete("/pipeline/{request_id}")
async def cancel_pipeline(request_id: str):
    """Cancel a running pipeline"""
    if request_id not in active_pipelines:
        return {"error": "Pipeline not found", "request_id": request_id}

    pipeline = active_pipelines[request_id]

    # Cancel all running tasks
    for task in pipeline.tasks:
        if not task.done():
            task.cancel()

    # Remove from active pipelines
    del active_pipelines[request_id]

    return {
        "request_id": request_id,
        "status": "cancelled",
        "candidates_found": len(pipeline.results["candidates"]),
    }
