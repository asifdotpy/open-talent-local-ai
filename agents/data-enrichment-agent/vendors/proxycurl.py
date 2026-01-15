"""
Proxycurl API Client

Official API: https://nubela.co/proxycurl/
Cost: $0.04 per profile enrichment
Quality: Excellent (⭐⭐⭐⭐⭐)
Coverage: 800M+ LinkedIn profiles

Rate Limits: 100 requests/minute
"""

import logging
import os

import aiohttp

logger = logging.getLogger(__name__)


class ProxycurlClient:
    """Client for Proxycurl LinkedIn API"""

    BASE_URL = "https://nubela.co/proxycurl/api/v2"

    def __init__(self):
        self.api_key = os.getenv("PROXYCURL_API_KEY", "")
        self.session: aiohttp.ClientSession | None = None
        self.healthy = False

    async def initialize(self):
        """Initialize HTTP session"""
        if not self.api_key:
            logger.warning("PROXYCURL_API_KEY not set. Proxycurl disabled.")
            return

        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        )

        # Test API connection
        try:
            await self.test_connection()
            self.healthy = True
            logger.info("Proxycurl client initialized ✓")
        except Exception as e:
            logger.error(f"Proxycurl initialization failed: {str(e)}")
            self.healthy = False

    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()

    def is_healthy(self) -> bool:
        """Check if client is operational"""
        return self.healthy and bool(self.api_key)

    async def test_connection(self):
        """Test API connection"""
        if not self.session:
            raise Exception("Client not initialized")

        # Test with a cheap endpoint (credit check)
        async with self.session.get(f"{self.BASE_URL}/credit-balance") as response:
            if response.status != 200:
                raise Exception(f"API test failed: {response.status}")

            data = await response.json()
            logger.info(f"Proxycurl credits: {data.get('credit_balance', 0)}")

    async def get_profile(self, linkedin_url: str) -> dict:
        """
        Enrich LinkedIn profile

        Args:
            linkedin_url: Full LinkedIn profile URL
                Examples:
                - https://www.linkedin.com/in/williamhgates
                - https://linkedin.com/in/john-doe-123456

        Returns:
            Enriched profile dict with:
            - first_name, last_name
            - headline, summary
            - experiences (list of jobs)
            - education (list of schools)
            - skills (list of skill names)
            - certifications
            - contact info (email, phone if available)

        Cost: $0.04
        """
        if not self.session:
            raise Exception("Client not initialized. Call initialize() first.")

        endpoint = f"{self.BASE_URL}/linkedin"
        params = {
            "url": linkedin_url,
            "use_cache": "if-recent",  # Use cached data if < 30 days old
            "fallback_to_cache": "on-error",  # Use cache if profile unavailable
        }

        try:
            async with self.session.get(endpoint, params=params) as response:
                if response.status == 200:
                    profile = await response.json()
                    logger.info(f"Proxycurl: Enriched {linkedin_url}")
                    return self._transform_profile(profile)

                elif response.status == 402:
                    # Insufficient credits
                    raise Exception("Proxycurl: Insufficient credits")

                elif response.status == 404:
                    # Profile not found
                    logger.warning(f"Proxycurl: Profile not found {linkedin_url}")
                    raise Exception("Profile not found")

                else:
                    error_text = await response.text()
                    raise Exception(f"Proxycurl API error {response.status}: {error_text}")

        except aiohttp.ClientError as e:
            logger.error(f"Proxycurl network error: {str(e)}")
            raise

    def _transform_profile(self, raw_profile: dict) -> dict:
        """
        Transform Proxycurl response to standard profile format

        Standardizes field names across vendors for consistency
        """
        return {
            "source": "proxycurl",
            "linkedin_url": raw_profile.get("public_identifier"),
            "full_name": f"{raw_profile.get('first_name', '')} {raw_profile.get('last_name', '')}".strip(),
            "first_name": raw_profile.get("first_name"),
            "last_name": raw_profile.get("last_name"),
            "headline": raw_profile.get("headline"),
            "summary": raw_profile.get("summary"),
            "location": {
                "city": raw_profile.get("city"),
                "state": raw_profile.get("state"),
                "country": raw_profile.get("country_full_name"),
            },
            "experiences": [
                {
                    "title": exp.get("title"),
                    "company": exp.get("company"),
                    "company_linkedin_url": exp.get("company_linkedin_profile_url"),
                    "start_date": exp.get("starts_at"),
                    "end_date": exp.get("ends_at"),
                    "description": exp.get("description"),
                    "location": exp.get("location"),
                }
                for exp in raw_profile.get("experiences", [])
            ],
            "education": [
                {
                    "school": edu.get("school"),
                    "degree": edu.get("degree_name"),
                    "field_of_study": edu.get("field_of_study"),
                    "start_date": edu.get("starts_at"),
                    "end_date": edu.get("ends_at"),
                }
                for edu in raw_profile.get("education", [])
            ],
            "skills": raw_profile.get("skills", []),
            "languages": raw_profile.get("languages", []),
            "certifications": [
                {
                    "name": cert.get("name"),
                    "authority": cert.get("authority"),
                    "start_date": cert.get("starts_at"),
                    "end_date": cert.get("ends_at"),
                    "url": cert.get("url"),
                }
                for cert in raw_profile.get("certifications", [])
            ],
            "contact": {
                "email": raw_profile.get("personal_emails", [None])[0],
                "phone": raw_profile.get("personal_numbers", [None])[0],
            },
            "social": {
                "twitter": raw_profile.get("twitter_handle"),
                "github": raw_profile.get("github_profile_url"),
            },
            "profile_picture_url": raw_profile.get("profile_pic_url"),
            "connections": raw_profile.get("connections"),
            "follower_count": raw_profile.get("follower_count"),
            "raw": raw_profile,  # Keep original for debugging
        }

    async def search_profiles(
        self,
        keywords: str | None = None,
        location: str | None = None,
        current_company: str | None = None,
        past_company: str | None = None,
        current_title: str | None = None,
        page: int = 1,
    ) -> dict:
        """
        Search LinkedIn profiles

        Cost: $0.04 per profile returned (NOT per search)

        Example:
            results = await client.search_profiles(
                keywords="python developer",
                location="San Francisco",
                current_company="Google"
            )
        """
        if not self.session:
            raise Exception("Client not initialized")

        endpoint = f"{self.BASE_URL}/linkedin/profile/search"
        params = {"page": page}

        if keywords:
            params["keywords"] = keywords
        if location:
            params["location"] = location
        if current_company:
            params["current_company"] = current_company
        if past_company:
            params["past_company"] = past_company
        if current_title:
            params["current_title"] = current_title

        async with self.session.get(endpoint, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"Search failed {response.status}: {error_text}")


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test():
        client = ProxycurlClient()
        await client.initialize()

        # Test profile enrichment
        profile = await client.get_profile("https://www.linkedin.com/in/williamhgates")

        print(f"Name: {profile['full_name']}")
        print(f"Headline: {profile['headline']}")
        print(f"Skills: {', '.join(profile['skills'][:5])}")

        await client.close()

    asyncio.run(test())
