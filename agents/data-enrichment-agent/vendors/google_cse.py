"""
Google Custom Search Engine (CSE) API Client

Official API: https://developers.google.com/custom-search
Cost: FREE (100 queries/day)
Quality: Basic (⭐⭐)
Coverage: Public web (Google index)

Rate Limits: 100 queries/day (free tier)
             10,000 queries/day (paid tier at $5/1000 queries)

Use Case: Free candidate discovery (X-Ray search)
"""

import logging
import os
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)


class GoogleCSEClient:
    """Client for Google Custom Search Engine API"""

    BASE_URL = "https://www.googleapis.com/customsearch/v1"

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_CSE_API_KEY", "")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")
        self.session: Optional[aiohttp.ClientSession] = None
        self.healthy = False
        self.daily_quota_used = 0
        self.daily_quota_limit = 100  # Free tier

    async def initialize(self):
        """Initialize HTTP session"""
        if not self.api_key or not self.search_engine_id:
            logger.warning("Google CSE credentials not set. Google search disabled.")
            return

        self.session = aiohttp.ClientSession()

        # Test API connection
        try:
            await self.test_connection()
            self.healthy = True
            logger.info("Google CSE client initialized ✓")
        except Exception as e:
            logger.error(f"Google CSE initialization failed: {str(e)}")
            self.healthy = False

    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()

    def is_healthy(self) -> bool:
        """Check if client is operational"""
        return self.healthy and bool(self.api_key) and bool(self.search_engine_id)

    async def test_connection(self):
        """Test API connection with a simple query"""
        if not self.session:
            raise Exception("Client not initialized")

        # Test with a simple search
        params = {"key": self.api_key, "cx": self.search_engine_id, "q": "test", "num": 1}

        async with self.session.get(self.BASE_URL, params=params) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"API test failed {response.status}: {error_text}")

            data = await response.json()
            logger.info(
                f"Google CSE test successful. Quota: {self.daily_quota_limit - self.daily_quota_used} remaining"
            )

    async def search(self, query: str, num_results: int = 10, start_index: int = 1) -> dict:
        """
        Execute Google Custom Search

        Args:
            query: Search query (supports X-Ray syntax)
            num_results: Number of results (1-10)
            start_index: Pagination start (1-based)

        Returns:
            Search results dict with items list

        Cost: FREE (counts against daily quota)
        """
        if not self.session:
            raise Exception("Client not initialized. Call initialize() first.")

        # Check quota
        if self.daily_quota_used >= self.daily_quota_limit:
            raise Exception(f"Daily quota exceeded ({self.daily_quota_limit} queries/day)")

        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": min(num_results, 10),  # Max 10 per request
            "start": start_index,
        }

        try:
            async with self.session.get(self.BASE_URL, params=params) as response:
                if response.status == 200:
                    results = await response.json()
                    self.daily_quota_used += 1
                    logger.info(
                        f"Google CSE: Query '{query}' returned {len(results.get('items', []))} results"
                    )
                    return results

                elif response.status == 429:
                    raise Exception("Rate limit exceeded")

                else:
                    error_text = await response.text()
                    raise Exception(f"Google CSE error {response.status}: {error_text}")

        except aiohttp.ClientError as e:
            logger.error(f"Google CSE network error: {str(e)}")
            raise

    async def xray_search_linkedin(
        self, skills: list[str], location: Optional[str] = None, company: Optional[str] = None
    ) -> list[dict]:
        """
        LinkedIn X-Ray search via Google CSE

        Example query:
        site:linkedin.com/in "software engineer" python django "San Francisco"

        Args:
            skills: List of skills/keywords
            location: Location filter
            company: Current/past company

        Returns:
            List of light profile dicts (name, title, URL)
        """
        # Build X-Ray query
        query_parts = ["site:linkedin.com/in"]

        # Add skills
        for skill in skills:
            query_parts.append(f'"{skill}"')

        # Add location
        if location:
            query_parts.append(f'"{location}"')

        # Add company
        if company:
            query_parts.append(f'"{company}"')

        query = " ".join(query_parts)

        # Execute search
        results = await self.search(query, num_results=10)

        # Parse results into light profiles
        light_profiles = []
        for item in results.get("items", []):
            profile = self._parse_linkedin_snippet(item)
            if profile:
                light_profiles.append(profile)

        return light_profiles

    def _parse_linkedin_snippet(self, search_result: dict) -> Optional[dict]:
        """
        Parse Google search result into light profile

        Example title: "John Doe - Software Engineer at Google - LinkedIn"
        Example snippet: "View John Doe's profile on LinkedIn. Experience: Google..."
        """
        try:
            url = search_result.get("link", "")
            if "linkedin.com/in" not in url:
                return None

            # Extract name from title
            title = search_result.get("title", "")
            name = title.split(" - ")[0] if " - " in title else ""

            # Extract job title from title
            job_title = ""
            if " - " in title:
                parts = title.split(" - ")
                if len(parts) >= 2:
                    job_title = parts[1].replace(" at Google", "").replace(" at ", " @ ")

            # Extract snippet
            snippet = search_result.get("snippet", "")

            return {
                "name": name,
                "title": job_title,
                "url": url,
                "snippet": snippet,
                "platform": "linkedin",
                "source": "google_xray",
            }

        except Exception as e:
            logger.error(f"Failed to parse LinkedIn snippet: {str(e)}")
            return None

    async def get_profile(self, linkedin_url: str) -> dict:
        """
        Get basic profile info from LinkedIn URL (via Google search)

        Note: This is NOT a real enrichment (just parses Google results)
        Use Proxycurl/Nubela for full profile data

        Cost: FREE
        """
        # Search for this specific profile
        query = f'site:linkedin.com/in "{linkedin_url.split("/in/")[-1]}"'

        results = await self.search(query, num_results=1)

        if not results.get("items"):
            raise Exception(f"Profile not found: {linkedin_url}")

        # Parse first result
        item = results["items"][0]
        profile = self._parse_linkedin_snippet(item)

        if not profile:
            raise Exception(f"Failed to parse profile: {linkedin_url}")

        return {
            "source": "google_cse",
            "linkedin_url": linkedin_url,
            "full_name": profile["name"],
            "headline": profile["title"],
            "snippet": profile["snippet"],
            "note": "Basic info only. Use Proxycurl/Nubela for full enrichment.",
        }


if __name__ == "__main__":
    import asyncio

    async def test():
        client = GoogleCSEClient()
        await client.initialize()

        # Test X-Ray search
        profiles = await client.xray_search_linkedin(
            skills=["python", "django"], location="San Francisco"
        )

        print(f"Found {len(profiles)} profiles:")
        for p in profiles[:3]:
            print(f"  - {p['name']} | {p['title']} | {p['url']}")

        await client.close()

    asyncio.run(test())
