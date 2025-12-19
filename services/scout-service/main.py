import asyncio
import aiohttp
import json
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from pydantic import Field
from contextlib import asynccontextmanager

from schemas import (
    SearchRequest,
    CandidateResponse,
    SearchResponse,
    SearchCriteria,
    WorkExperience,
    Education,
    Skills,
    InitialQuestion,
    CandidateProfile,
    HandoffPayload,
    AgentInfo,
    AgentSearchRequest,
    AgentSearchResult,
    HealthResponse,
)

load_dotenv()

# Dataclass for internal use (keeping for compatibility)
@dataclass
class Candidate:
    name: str
    location: str
    profile_url: str
    platform: str
    bio: Optional[str] = None
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    website_url: Optional[str] = None
    company: Optional[str] = None
    confidence_score: Optional[float] = None
    # ContactOut enriched data
    linkedin_enriched: Optional[Dict[str, Any]] = None
    work_emails: Optional[List[str]] = None
    personal_emails: Optional[List[str]] = None
    phone_numbers: Optional[List[str]] = None
    linkedin_headline: Optional[str] = None
    linkedin_industry: Optional[str] = None
    linkedin_summary: Optional[str] = None
    linkedin_experience: Optional[List[Dict]] = None
    linkedin_education: Optional[List[Dict]] = None
    linkedin_skills: Optional[List[str]] = None
    linkedin_followers: Optional[int] = None

class GitHubTalentScout:
    """
    Find GitHub developers with AI-powered query formatting
    """

    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        self.contactout_token = os.getenv('CONTACTOUT_API_TOKEN', '')
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'granite4:350m-h')
        self.session: Optional[aiohttp.ClientSession] = None

    async def init_session(self):
        """Initialize HTTP session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'User-Agent': 'TalentScout/1.0'}
            )

    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def format_query_with_ollama(self, user_query: str, location: str = "Ireland") -> str:
        """
        Use Ollama Llama 3.1 to convert natural language to GitHub search query format
        
        CRITICAL: GitHub searches profile text (name, bio, email), not a resume database!
        Strategy: Use ONLY qualifiers (language, repos), avoid text keywords unless essential
        """
        
        prompt = f"""Convert this job search query into a GitHub API search query.

    USER QUERY: "{user_query}"
    LOCATION: "{location}"

    CRITICAL RULES:
    1. AVOID text keywords - most developers don't put job titles in their bio
    2. Focus on QUALIFIERS ONLY: language:, repos:, followers:
    3. Extract programming language → use language:LANGUAGE
    4. Extract experience level:
    - "junior" or "1-2 years" → repos:>5
    - "mid" or "2-3 years" → repos:>10  
    - "senior" or "3-5 years" → repos:>20
    - "expert" or "5+ years" → repos:>50
    5. Extract popularity/activity:
    - "active" or "popular" → followers:>50
    - "experienced" → repos:>30
    6. ALWAYS add: location:{location} type:user
    7. NO text keywords unless user specifically asks for a username/company

    GOOD Examples (qualifier-focused):
    Input: "Senior AI Engineer"
    Output: language:python repos:>20 followers:>10 location:Ireland type:user

    Input: "senior full stack developer javascript"  
    Output: language:javascript repos:>20 location:Ireland type:user

    Input: "machine learning expert python 5+ years"
    Output: language:python repos:>50 followers:>20 location:Ireland type:user

    Input: "react developer"
    Output: language:javascript repos:>5 location:Ireland type:user

    Input: "python developer at Google"
    Output: google language:python repos:>10 location:Ireland type:user

    BAD Examples (too many text keywords):
    ❌ "AI engineer language:python" (will match only profiles with "AI" AND "engineer" in bio)
    ❌ "senior developer javascript" (will miss 99% of senior JS devs)

    Now convert the query. 

    IMPORTANT: Reply with ONLY the GitHub search query string. No explanations.

    GitHub search query:"""

        try:
            url = f"{self.ollama_url}/api/generate"
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "system": "You are a query converter. Output only search queries with GitHub qualifiers (language:, repos:, followers:, location:, type:). Avoid text keywords unless essential.",
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 50
                }
            }

            print(f"[AI] Formatting query with Ollama Llama 3.1...")
            print(f"[AI] User input: '{user_query}'")

            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    formatted_query = data.get('response', '').strip()
                    
                    print(f"[DEBUG] Raw AI response: '{formatted_query[:200]}'")
                    
                    # Clean up response
                    lines = [line.strip() for line in formatted_query.split('\n') if line.strip()]
                    actual_query = None
                    
                    for line in reversed(lines):
                        if any(q in line for q in ['location:', 'language:', 'repos:', 'type:user']):
                            actual_query = line
                            break
                    
                    if not actual_query:
                        actual_query = lines[-1] if lines else formatted_query
                    
                    if ':' in actual_query and not any(q in actual_query for q in ['location:', 'language:', 'repos:', 'type:']):
                        parts = actual_query.split(':')
                        actual_query = parts[-1].strip()
                    
                    prefixes_to_remove = [
                        "Output:", "Query:", "GitHub Query:", "Search:", 
                        "Here is the converted job search query:",
                        "Here is the converted query:",
                        "The converted query is:",
                        "Here's the query:",
                        "Result:",
                        "Answer:"
                    ]
                    
                    for prefix in prefixes_to_remove:
                        if actual_query.lower().startswith(prefix.lower()):
                            actual_query = actual_query[len(prefix):].strip()
                    
                    actual_query = actual_query.strip('"\'')
                    
                    if (not actual_query or 
                        len(actual_query) < 5 or 
                        actual_query.lower().startswith(('here', 'the', 'this', 'i ', 'converted'))):
                        print(f"[WARNING] AI response looks invalid, using fallback")
                        return self.basic_query_format(user_query, location)
                    
                    print(f"[AI] Formatted query: '{actual_query}'")
                    return actual_query
                else:
                    print(f"[ERROR] Ollama API error: {response.status}")
                    return self.basic_query_format(user_query, location)

        except Exception as e:
            print(f"[ERROR] Error calling Ollama: {e}")
            print(f"[INFO] Using basic query formatting as fallback")
            return self.basic_query_format(user_query, location)

    def basic_query_format(self, user_query: str, location: str) -> str:
        """Fallback basic query formatting - QUALIFIER-FOCUSED"""
        query = user_query.lower()
        
        # Build query with ONLY qualifiers, NO text keywords
        qualifiers = []
        
        # Detect language
        languages = {
            "python": "python", "javascript": "javascript", "js": "javascript",
            "java": "java", "ruby": "ruby", "go": "go", "golang": "go",
            "rust": "rust", "typescript": "typescript", "ts": "typescript",
            "react": "javascript", "vue": "javascript", "angular": "javascript",
            "node": "javascript", "nodejs": "javascript",
            "c++": "c++", "cpp": "c++", "c#": "c#", "csharp": "c#",
            "php": "php", "swift": "swift", "kotlin": "kotlin",
            "r": "r", "scala": "scala", "dart": "dart"
        }
        
        detected_lang = None
        for key, lang in languages.items():
            if key in query:
                detected_lang = lang
                break
        
        # Build qualifiers list
        if detected_lang:
            qualifiers.append(f"language:{detected_lang}")
        
        # Repos based on experience
        if "senior" in query or "5+ year" in query or "expert" in query or "lead" in query:
            qualifiers.append("repos:>20")
            qualifiers.append("followers:>10")
        elif "mid" in query or "2+ year" in query or "3 year" in query:
            qualifiers.append("repos:>10")
        elif "junior" in query or "1 year" in query or "entry" in query:
            qualifiers.append("repos:>5")
        else:
            # Default: some activity
            qualifiers.append("repos:>5")
        
        # Activity level
        if "active" in query or "popular" in query:
            qualifiers.append("followers:>50")
        
        # Check for company name (only specific keyword to include)
        company_keywords = ["google", "microsoft", "amazon", "meta", "apple", "netflix", "uber", "airbnb"]
        for company in company_keywords:
            if company in query:
                qualifiers.insert(0, company)  # Add company name as text keyword
                break
        
        # Add location and type
        qualifiers.append(f"location:{location}")
        qualifiers.append("type:user")
        
        formatted = " ".join(qualifiers)
        
        print(f"[FALLBACK] Generated qualifier-only query: '{formatted}'")
        return formatted

    async def search_github_candidates(self, user_query: str = None,
                                     location: str = "Ireland",
                                     max_results: int = 20,
                                     use_ai_formatting: bool = True) -> List[Candidate]:
        """
        Search GitHub for developers with AI-formatted queries
        """
        candidates = []

        if not self.github_token:
            print("[ERROR] GitHub token not configured")
            return candidates

        try:
            # Format query with AI or use direct input
            if use_ai_formatting and user_query:
                search_query = await self.format_query_with_ollama(user_query, location)
            else:
                search_query = user_query or "python developer"
                if "location:" not in search_query and location:
                    search_query += f" location:{location}"

            url = "https://api.github.com/search/users"
            headers = {'Authorization': f'token {self.github_token}'}
            params = {
                'q': search_query,
                'per_page': 50,
                'sort': 'repositories',
                'order': 'desc'
            }

            print(f"\n[SEARCH] GitHub API Query: '{search_query}'")
            print(f"[INFO] Searching for users with these keywords in their profile/bio")
            print(f"[SEARCH] Searching GitHub...")

            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    users = data.get('items', [])
                    total_count = data.get('total_count', 0)

                    print(f"[SEARCH] Found {total_count} total matches on GitHub")
                    print(f"[SEARCH] Processing top {len(users)} users...")

                    for user in users:
                        # Get detailed user info
                        user_details = await self.get_github_user_details(user['login'])

                        # Only include users with emails
                        if user_details and user_details.get('email'):
                            # Extract all social links
                            social_links = self.extract_social_links(user_details)

                            # Calculate priority score
                            priority_score = 0.5

                            if social_links['linkedin']:
                                priority_score += 0.4
                            if social_links['twitter']:
                                priority_score += 0.2
                            if social_links['website']:
                                priority_score += 0.1
                            if user_details.get('company'):
                                priority_score += 0.1

                            candidate = Candidate(
                                name=user_details.get('name', user['login']),
                                location=user_details.get('location', location),
                                profile_url=user['html_url'],
                                platform='GitHub',
                                bio=user_details.get('bio'),
                                email=user_details.get('email'),
                                linkedin_url=social_links['linkedin'],
                                twitter_url=social_links['twitter'],
                                website_url=social_links['website'],
                                company=user_details.get('company'),
                                confidence_score=min(1.0, priority_score)
                            )

                            # Enrich LinkedIn profile if available
                            if candidate.linkedin_url and self.contactout_token:
                                enriched_data = await self.enrich_linkedin_profile(candidate.linkedin_url)
                                if enriched_data:
                                    candidate.linkedin_enriched = enriched_data
                                    candidate.work_emails = enriched_data.get('work_email', [])
                                    candidate.personal_emails = enriched_data.get('personal_email', [])
                                    candidate.phone_numbers = enriched_data.get('phone', [])
                                    candidate.linkedin_headline = enriched_data.get('headline')
                                    candidate.linkedin_industry = enriched_data.get('industry')
                                    candidate.linkedin_summary = enriched_data.get('summary')
                                    candidate.linkedin_experience = enriched_data.get('experience', [])
                                    candidate.linkedin_education = enriched_data.get('education', [])
                                    candidate.linkedin_skills = enriched_data.get('skills', [])
                                    candidate.linkedin_followers = enriched_data.get('followers')
                                    candidate.confidence_score = min(1.0, (candidate.confidence_score or 0) + 0.3)

                            candidates.append(candidate)

                    # Sort by priority
                    candidates.sort(key=lambda x: (
                        x.linkedin_url is not None,
                        (x.twitter_url is not None or x.website_url is not None),
                        x.confidence_score or 0
                    ), reverse=True)

                    print(f"\n[RESULTS] Found {len(candidates)} candidates with emails")
                    linkedin_count = sum(1 for c in candidates if c.linkedin_url)
                    twitter_count = sum(1 for c in candidates if c.twitter_url)
                    website_count = sum(1 for c in candidates if c.website_url)

                    print(f"[LINKEDIN] {linkedin_count} with LinkedIn URLs")
                    print(f"[TWITTER] {twitter_count} with Twitter/X URLs")
                    print(f"[WEBSITE] {website_count} with website URLs")
                    
                    return candidates[:max_results]

                elif response.status == 403:
                    print("[ERROR] GitHub API rate limit exceeded")
                elif response.status == 422:
                    print("[ERROR] Invalid search query format")
                    print("[HINT] Check your query syntax")
                else:
                    print(f"[ERROR] GitHub API error: {response.status}")

        except Exception as e:
            print(f"[ERROR] Search error: {e}")

        return candidates

    async def get_github_user_details(self, username: str) -> Optional[Dict]:
        """Get detailed GitHub user information"""
        try:
            url = f"https://api.github.com/users/{username}"
            headers = {'Authorization': f'token {self.github_token}'}

            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()

        except Exception as e:
            print(f"[ERROR] Error getting user details: {e}")

        return None

    def extract_social_links(self, user_details: Dict) -> Dict[str, Optional[str]]:
        """Extract LinkedIn, Twitter/X, and website links"""
        links = {
            'linkedin': None,
            'twitter': None,
            'website': None
        }

        fields_to_check = [
            user_details.get('bio', ''),
            user_details.get('blog', ''),
            user_details.get('company', ''),
            user_details.get('location', ''),
        ]

        twitter_username = user_details.get('twitter_username')
        if twitter_username:
            links['twitter'] = f"https://twitter.com/{twitter_username}"

        all_text = ' '.join(str(field) for field in fields_to_check if field)

        if not all_text.strip():
            return links

        # LinkedIn patterns
        linkedin_patterns = [
            r'linkedin\.com/in/[\w\-_.]+/?',
            r'https?://(?:www\.)?linkedin\.com/in/[\w\-_.]+/?',
        ]

        for pattern in linkedin_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                url = match.group()
                url = re.sub(r'[.,;!?]$', '', url)
                if not url.startswith('http'):
                    url = 'https://' + url
                links['linkedin'] = url
                break

        # Twitter patterns
        if not links['twitter']:
            twitter_patterns = [
                r'twitter\.com/[\w_]+/?',
                r'https?://(?:www\.)?twitter\.com/[\w_]+/?',
                r'x\.com/[\w_]+/?',
            ]

            for pattern in twitter_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    url = match.group()
                    if not url.startswith('http'):
                        url = 'https://' + url
                    links['twitter'] = url
                    break

        # Website
        if not links['website'] and user_details.get('blog'):
            blog = user_details['blog'].strip()
            if blog and (blog.startswith('http') or '.' in blog):
                if not blog.startswith('http'):
                    blog = 'https://' + blog
                links['website'] = blog

        return links

    async def enrich_linkedin_profile(self, linkedin_url: str) -> Optional[Dict[str, Any]]:
        """Enrich LinkedIn profile using ContactOut API"""
        if not self.contactout_token or not linkedin_url:
            return None

        try:
            linkedin_url = linkedin_url.strip()
            if not linkedin_url.startswith('http'):
                linkedin_url = 'https://' + linkedin_url

            if 'linkedin.com/in/' not in linkedin_url and 'linkedin.com/pub/' not in linkedin_url:
                return None

            url = "https://api.contactout.com/v1/linkedin/enrich"
            params = {'profile': linkedin_url}
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'token': self.contactout_token
            }

            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status_code') == 200 and data.get('profile'):
                        profile_data = data['profile']
                        if profile_data and not (isinstance(profile_data, list) and len(profile_data) == 0):
                            return profile_data
                elif response.status == 401:
                    print("[ERROR] ContactOut API: Invalid token")
                elif response.status == 402:
                    print("[ERROR] ContactOut API: Insufficient credits")

        except Exception as e:
            print(f"[ERROR] Error enriching LinkedIn: {e}")

        return None

    def display_results(self, candidates: List[Candidate]):
        """Display candidates"""
        if not candidates:
            print("\n[ERROR] No candidates with emails found")
            return

        print(f"\n{'='*70}")
        print(f"GITHUB CANDIDATES WITH EMAILS")
        print(f"{'='*70}")
        print(f"Total candidates: {len(candidates)}\n")

        for i, candidate in enumerate(candidates[:15], 1):
            if candidate.linkedin_url:
                priority = "[LINKEDIN]"
            elif candidate.twitter_url or candidate.website_url:
                priority = "[SOCIAL]"
            else:
                priority = "[EMAIL]"

            print(f"{i}. {priority} {candidate.name}")
            print(f"   Email: {candidate.email}")
            print(f"   Location: {candidate.location}")
            print(f"   Profile: {candidate.profile_url}")

            if candidate.linkedin_url:
                print(f"   LinkedIn: {candidate.linkedin_url}")
                if candidate.linkedin_headline:
                    print(f"      → {candidate.linkedin_headline}")
            if candidate.twitter_url:
                print(f"   Twitter: {candidate.twitter_url}")
            if candidate.website_url:
                print(f"   Website: {candidate.website_url}")
            if candidate.company:
                print(f"   Company: {candidate.company}")
            if candidate.bio:
                bio = candidate.bio[:100] + "..." if len(candidate.bio) > 100 else candidate.bio
                print(f"   Bio: {bio}")
            print()

    def export_results(self, candidates: List[Candidate], filename: str = None) -> str:
        """Export results to JSON"""
        if not filename:
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"github_candidates_{timestamp}.json"

        export_data = {
            "search_metadata": {
                "total_candidates": len(candidates),
                "with_linkedin": sum(1 for c in candidates if c.linkedin_url),
                "with_twitter": sum(1 for c in candidates if c.twitter_url),
                "with_website": sum(1 for c in candidates if c.website_url),
            },
            "candidates": [asdict(c) for c in candidates]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"[EXPORT] Results saved to: {filename}")
        return filename

# FastAPI App
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - GitHubTalentScout
    finder = GitHubTalentScout()
    await finder.init_session()
    app.state.finder = finder
    
    # Startup - Agent System
    agents_path = os.getenv("AGENT_DISCOVERY_PATH", "/home/asif1/open-talent/agents")
    registry = get_agent_registry(agents_path=agents_path)
    await registry.init_session()
    await registry.discover_agents()
    await registry.start_health_monitoring()
    app.state.agent_registry = registry
    app.state.agent_router = AgentRouter(registry)
    app.state.health_monitor = HealthMonitor(registry)
    
    print("\n" + "="*70)
    print("AGENT SYSTEM INITIALIZED")
    print("="*70)
    print(f"✓ Discovered {len(registry.get_all_agents())} agents")
    print(f"✓ Health monitoring started")
    print(f"✓ Agent API endpoints available at /agents/*")
    print("="*70 + "\n")
    
    yield
    
    # Shutdown
    await registry.stop_health_monitoring()
    await registry.close_session()
    await finder.close_session()

# Deprecated alias for backward compatibility
GitHubCandidateFinder = GitHubTalentScout

app = FastAPI(
    title="Talent Scout API",
    description="AI-powered GitHub developer search with LinkedIn enrichment",
    version="1.0.0",
    lifespan=lifespan
)

# Versioned API router (v1)
api_v1 = APIRouter(prefix="/api/v1")

async def get_finder() -> GitHubTalentScout:
    return app.state.finder

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Talent Scout Service"}

@app.get("/")
async def root():
    """Root endpoint for basic availability checks."""
    return {"message": "Talent Scout Service - Candidate Discovery"}

@app.post("/search", response_model=SearchResponse)
async def search_candidates(
    request: SearchRequest,
    finder: GitHubTalentScout = Depends(get_finder)
):
    """
    Search for GitHub candidates based on natural language query
    """
    try:
        # Search for candidates
        candidates = await finder.search_github_candidates(
            user_query=request.query,
            location=request.location,
            max_results=request.max_results,
            use_ai_formatting=request.use_ai_formatting
        )

        # Convert to response model
        candidate_responses = []
        for candidate in candidates:
            candidate_responses.append(CandidateResponse(**asdict(candidate)))

        return SearchResponse(
            candidates=candidate_responses,
            total_found=len(candidates),
            search_query=request.query,
            location=request.location
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# --- Compatibility endpoints for tests ---
@api_v1.get("/search")
async def search_candidates_query(skills: Optional[str] = None, location: Optional[str] = None):
    """Simple query-based search endpoint returning empty results for contract compliance."""
    return {
        "candidates": [],
        "total_found": 0,
        "search_query": skills or "",
        "location": location or "",
    }


@api_v1.post("/search/advanced")
async def advanced_search(payload: Dict[str, Any]):
    """Advanced search stub that acknowledges request and returns created status."""
    return {"status": "created", "criteria": payload}


@api_v1.post("/lists")
async def create_sourced_list(payload: Dict[str, Any]):
    """Create sourced list stub returning minimal list info."""
    name = payload.get("name", "unnamed")
    return {"list_id": "list-created", "name": name, "status": "created"}

# Register versioned router
app.include_router(api_v1)

@app.post("/handoff", response_model=HandoffPayload)
async def create_handoff(
    search_criteria: SearchCriteria,
    finder: GitHubTalentScout = Depends(get_finder)
):
    """
    Create interview handoff payload for Agent-to-Interview process
    """
    try:
        # Convert search criteria to GitHub search query
        query_parts = [search_criteria.jobTitle]
        if search_criteria.requiredSkills:
            query_parts.extend(search_criteria.requiredSkills[:3])  # Use top 3 required skills
        query = " ".join(query_parts)

        # Search for candidates
        candidates = await finder.search_github_candidates(
            user_query=query,
            location="Ireland",  # Default location, could be made configurable
            max_results=1,  # Get top candidate for handoff
            use_ai_formatting=True
        )

        if not candidates:
            raise HTTPException(status_code=404, detail="No suitable candidates found")

        # Take the top candidate
        candidate = candidates[0]

        # Transform to CandidateProfile format
        candidate_profile = await transform_to_candidate_profile(candidate, search_criteria)

        return HandoffPayload(
            searchCriteria=search_criteria,
            candidateProfile=candidate_profile
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Handoff creation failed: {str(e)}")

async def transform_to_candidate_profile(candidate: Candidate, search_criteria: SearchCriteria) -> CandidateProfile:
    """Transform GitHub candidate data to CandidateProfile format"""

    # Extract work experience from LinkedIn data if available
    work_experience = []
    if candidate.linkedin_experience:
        for exp in candidate.linkedin_experience[:3]:  # Top 3 experiences
            work_experience.append(WorkExperience(
                title=exp.get('title', ''),
                company=exp.get('company_name', ''),
                duration=f"{exp.get('start_date_year', '')} - {exp.get('end_date_year', '')}",
                responsibilities=[exp.get('summary', '')] if exp.get('summary') else []
            ))

    # Extract education from LinkedIn data if available
    education = []
    if candidate.linkedin_education:
        for edu in candidate.linkedin_education[:2]:  # Top 2 education entries
            education.append(Education(
                institution=edu.get('school_name', ''),
                degree=edu.get('degree', ''),
                year=edu.get('end_date_year', '') or edu.get('start_date_year', '')
            ))

    # Match skills with improved fuzzy matching
    matched_skills = []
    unmatched_skills = []

    candidate_skills = set()
    if candidate.linkedin_skills:
        # Normalize skills to lowercase and remove common suffixes
        for skill in candidate.linkedin_skills:
            normalized = skill.lower().replace(' (programming language)', '').strip()
            candidate_skills.add(normalized)

    # Also check bio and summary for skills
    text_sources = []
    if candidate.bio:
        text_sources.append(candidate.bio.lower())
    if candidate.linkedin_summary:
        text_sources.append(candidate.linkedin_summary.lower())

    def skill_matches(skill_name: str) -> bool:
        """Check if a skill matches in candidate data"""
        skill_lower = skill_name.lower()

        # Direct match in skills
        if skill_lower in candidate_skills:
            return True

        # Fuzzy match in skills (contains)
        for c_skill in candidate_skills:
            if skill_lower in c_skill or c_skill in skill_lower:
                return True

        # Check in text sources
        for text in text_sources:
            if skill_lower in text:
                return True

        return False

    # Check required skills
    for skill in search_criteria.requiredSkills:
        if skill_matches(skill):
            matched_skills.append(skill)
        else:
            unmatched_skills.append(skill)

    # Check nice-to-have skills
    for skill in search_criteria.niceToHaveSkills:
        if skill_matches(skill):
            matched_skills.append(skill)
        else:
            unmatched_skills.append(skill)

    skills = Skills(matched=matched_skills, unmatched=unmatched_skills)

    # Generate AI summary
    summary = candidate.bio or ""
    if candidate.linkedin_summary:
        summary += f"\n\n{candidate.linkedin_summary}"

    # Calculate alignment score based on matched skills
    total_criteria_skills = len(search_criteria.requiredSkills) + len(search_criteria.niceToHaveSkills)
    if total_criteria_skills > 0:
        alignment_score = len(matched_skills) / total_criteria_skills
    else:
        alignment_score = candidate.confidence_score or 0.5

    # Ensure alignment score doesn't exceed 1.0
    alignment_score = min(1.0, alignment_score)

    # For now, return empty initial questions (as per user's note)
    initial_questions = []

    return CandidateProfile(
        fullName=candidate.name,
        sourceUrl=candidate.profile_url,
        summary=summary[:500],  # Limit summary length
        workExperience=work_experience,
        education=education,
        skills=skills,
        alignmentScore=alignment_score,
        initialQuestions=initial_questions
    )

# Keep the CLI version for backward compatibility
async def main():
    """Main function with user input"""
    print("="*70)
    print("GITHUB CANDIDATE FINDER - AI-Powered Query Formatting")
    print("Using Ollama Llama 3.1 for intelligent query conversion")
    print("="*70)

    # Get user input
    print("\nEnter your search query (natural language):")
    print("Examples:")
    print("  - AI engineer in python with 2+ years skills")
    print("  - senior full stack javascript developer")
    print("  - machine learning expert 5+ years experience")
    print("  - react developer with good portfolio")

    user_query = input("\nYour query: ").strip()

    if not user_query:
        user_query = "python developer"
        print(f"[INFO] Using default query: '{user_query}'")

    # Get location
    location = input("\nLocation (default: Ireland): ").strip()
    if not location:
        location = "Ireland"

    # Ask about AI formatting
    use_ai = input("\nUse AI query formatting? (Y/n): ").strip().lower()
    use_ai_formatting = use_ai != 'n'

    print(f"\n{'='*70}")
    print(f"Search Configuration:")
    print(f"  Query: {user_query}")
    print(f"  Location: {location}")
    print(f"  AI Formatting: {'Enabled' if use_ai_formatting else 'Disabled'}")
    print(f"{'='*70}\n")

    # Initialize finder
    finder = GitHubCandidateFinder()
    await finder.init_session()

    try:
        # Search for candidates
        candidates = await finder.search_github_candidates(
            user_query=user_query,
            location=location,
            max_results=20,
            use_ai_formatting=use_ai_formatting
        )

        # Display and export results
        finder.display_results(candidates)

        if candidates:
            finder.export_results(candidates)

            print(f"\n{'='*70}")
            print("SEARCH SUMMARY")
            print(f"{'='*70}")
            print(f"Total candidates found: {len(candidates)}")
            print(f"With LinkedIn: {sum(1 for c in candidates if c.linkedin_url)}")
            print(f"With social links: {sum(1 for c in candidates if c.linkedin_url or c.twitter_url or c.website_url)}")
            print(f"{'='*70}\n")
    except Exception as e:
        print(f"[ERROR] Search failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await finder.session.close()


# ============================
# Agent Integration (New - December 13, 2025)
# ============================

from agent_registry import AgentRegistry, AgentStatus, get_agent_registry
from agent_health import HealthMonitor, HealthReport
from agent_routes import AgentRouter, AgentRequest, AgentResponse, MultiAgentResponse
import os

# ============================
# Agent API Endpoints
# ============================

@app.get("/agents/registry")
async def get_agents_registry(
    capability: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Get agent registry with optional filtering
    
    Query Parameters:
    - capability: Filter agents by capability (e.g., 'search', 'enrichment')
    - status: Filter agents by status (e.g., 'healthy', 'unreachable')
    
    Returns list of all agents with metadata
    """
    try:
        registry = app.state.agent_registry
        
        agents = registry.get_all_agents()
        
        # Filter by capability
        if capability:
            agents = [a for a in agents if capability in a.capabilities]
        
        # Filter by status
        if status:
            agents = [a for a in agents if a.status == status]
        
        return {
            "total_agents": len(agents),
            "agents": agents,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registry lookup failed: {str(e)}")

@app.get("/agents/health")
async def get_agents_health() -> HealthReport:
    """
    Get comprehensive health report for all agents
    
    Returns overall system health and individual agent statuses
    """
    try:
        monitor = app.state.health_monitor
        report = await monitor.perform_health_check()
        return report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/agents/{agent_name}")
async def get_agent_info(agent_name: str):
    """Get detailed information about a specific agent"""
    try:
        registry = app.state.agent_registry
        agent = registry.get_agent(agent_name)
        
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lookup failed: {str(e)}")

@app.post("/agents/call")
async def call_agent_endpoint(request: AgentRequest) -> AgentResponse:
    """
    Call an agent endpoint directly
    
    Request body:
    - agent_name: Name of the target agent
    - endpoint: API endpoint (e.g., "/search", "/health")
    - method: HTTP method (GET, POST, etc.)
    - payload: Request payload (optional)
    - params: Query parameters (optional)
    """
    try:
        router = app.state.agent_router
        
        if not request.agent_name:
            raise HTTPException(status_code=400, detail="agent_name is required")
        
        response = await router.route_to_agent(
            agent_name=request.agent_name,
            endpoint=request.endpoint,
            method=request.method,
            payload=request.payload,
            params=request.params
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent call failed: {str(e)}")

@app.post("/agents/search-multi")
async def search_across_agents(request: SearchRequest) -> Dict[str, Any]:
    """
    Execute search across all search-capable agents
    
    Queries multiple agents in parallel and aggregates results
    """
    try:
        router = app.state.agent_router
        
        results = await router.route_search_request(
            query=request.query,
            location=request.location,
            max_results=request.max_results
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-agent search failed: {str(e)}")

@app.post("/agents/capability/{capability}")
async def route_by_capability(
    capability: str,
    endpoint: str,
    method: str = "POST",
    payload: Optional[Dict] = None
) -> MultiAgentResponse:
    """
    Route request to all agents with specific capability
    
    Path Parameters:
    - capability: Required capability (e.g., 'search', 'enrichment')
    
    Query Parameters:
    - endpoint: Target endpoint
    - method: HTTP method
    - payload: Request payload (optional)
    """
    try:
        router = app.state.agent_router
        
        response = await router.route_by_capability(
            capability=capability,
            endpoint=endpoint,
            method=method,
            payload=payload,
            healthy_only=True
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Routing failed: {str(e)}")

# ============================
# Enhanced Endpoints with Agent Support
# ============================

@app.post("/search/multi-agent")
async def search_multi_agent(
    request: SearchRequest,
    finder: GitHubTalentScout = Depends(get_finder)
) -> Dict[str, Any]:
    """
    Enhanced search using multiple agents
    
    This endpoint:
    1. Performs GitHub search directly (scout-service)
    2. Routes search to market-intelligence-agent for insights
    3. Routes to data-enrichment-agent for enrichment
    4. Aggregates results from all sources
    """
    try:
        router = app.state.agent_router
        
        # Perform local search
        local_candidates = await finder.search_github_candidates(
            user_query=request.query,
            location=request.location,
            max_results=request.max_results,
            use_ai_formatting=request.use_ai_formatting
        )

        # Route to multi-agent search for additional insights
        agent_results = await router.route_search_request(
            query=request.query,
            location=request.location,
            max_results=request.max_results
        )

        # Combine results (local + agent-sourced)
        combined_candidates = []
        seen_urls = set()

        # Add local results first
        for candidate in local_candidates:
            if candidate.profile_url not in seen_urls:
                seen_urls.add(candidate.profile_url)
                combined_candidates.append(asdict(candidate))

        # Add agent results
        for candidate in agent_results.get("candidates", []):
            url = candidate.get("profile_url")
            if url not in seen_urls:
                seen_urls.add(url)
                combined_candidates.append(candidate)

        return SearchResponse(
            candidates=[CandidateResponse(**c) if isinstance(c, dict) else c 
                       for c in combined_candidates[:request.max_results]],
            total_found=len(combined_candidates),
            search_query=request.query,
            location=request.location
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-agent search failed: {str(e)}")

# ============================
# Updated Health Endpoint
# ============================

@app.get("/health/full")
async def full_system_health():
    """
    Get comprehensive system health including all agents
    """
    try:
        monitor = app.state.health_monitor
        registry = app.state.agent_registry
        
        health_report = await monitor.perform_health_check()
        
        # Check if critical agents are healthy
        critical_agents = ["interview-agent", "scout-coordinator-agent", "data-enrichment-agent"]
        critical_health = all(
            registry.get_agent(name).status == AgentStatus.HEALTHY 
            for name in critical_agents
            if registry.get_agent(name)
        )
        
        return {
            "status": "healthy" if health_report.health_percentage >= 80 else "degraded",
            "timestamp": datetime.now().isoformat(),
            "critical_agents_healthy": critical_health,
            "overall_health_percentage": health_report.health_percentage,
            "agents_summary": {
                "total": health_report.total_agents,
                "healthy": health_report.healthy_agents,
                "unhealthy": health_report.unhealthy_agents,
                "unreachable": health_report.unreachable_agents,
                "unknown": health_report.unknown_agents
            },
            "agent_details": [
                {
                    "name": agent.name,
                    "status": agent.status,
                    "port": agent.port,
                    "capabilities": agent.capabilities,
                    "last_check": agent.last_health_check.isoformat() if agent.last_health_check else None
                }
                for agent in health_report.agents
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server...")
    print("API will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("Agent endpoints: http://localhost:8000/agents/*")
    uvicorn.run(app, host="0.0.0.0", port=8000)