"""
Nubela (People Data Labs) API Client

Official API: https://nubela.co/nubela/
Cost: $0.02 per profile enrichment
Quality: Very Good (⭐⭐⭐⭐)
Coverage: 500M+ profiles

Rate Limits: 200 requests/minute
"""

import os
import aiohttp
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class NubelaClient:
    """Client for Nubela Person Enrichment API"""
    
    BASE_URL = "https://api.nubela.co/v1"
    
    def __init__(self):
        self.api_key = os.getenv("NUBELA_API_KEY", "")
        self.session: Optional[aiohttp.ClientSession] = None
        self.healthy = False
    
    async def initialize(self):
        """Initialize HTTP session"""
        if not self.api_key:
            logger.warning("NUBELA_API_KEY not set. Nubela disabled.")
            return
        
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        
        # Test API connection
        try:
            await self.test_connection()
            self.healthy = True
            logger.info("Nubela client initialized ✓")
        except Exception as e:
            logger.error(f"Nubela initialization failed: {str(e)}")
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
        
        # Test with account info endpoint
        async with self.session.get(f"{self.BASE_URL}/account") as response:
            if response.status != 200:
                raise Exception(f"API test failed: {response.status}")
            
            data = await response.json()
            logger.info(f"Nubela credits: {data.get('credits_remaining', 0)}")
    
    async def get_profile(self, linkedin_url: str) -> Dict:
        """
        Enrich profile from LinkedIn URL
        
        Args:
            linkedin_url: Full LinkedIn profile URL
        
        Returns:
            Enriched profile dict
        
        Cost: $0.02
        """
        if not self.session:
            raise Exception("Client not initialized. Call initialize() first.")
        
        endpoint = f"{self.BASE_URL}/person/linkedin"
        params = {
            "url": linkedin_url,
            "use_cache": "if-recent"
        }
        
        try:
            async with self.session.get(endpoint, params=params) as response:
                if response.status == 200:
                    profile = await response.json()
                    logger.info(f"Nubela: Enriched {linkedin_url}")
                    return self._transform_profile(profile)
                
                elif response.status == 402:
                    raise Exception("Nubela: Insufficient credits")
                
                elif response.status == 404:
                    logger.warning(f"Nubela: Profile not found {linkedin_url}")
                    raise Exception("Profile not found")
                
                else:
                    error_text = await response.text()
                    raise Exception(f"Nubela API error {response.status}: {error_text}")
        
        except aiohttp.ClientError as e:
            logger.error(f"Nubela network error: {str(e)}")
            raise
    
    def _transform_profile(self, raw_profile: Dict) -> Dict:
        """Transform Nubela response to standard format"""
        return {
            "source": "nubela",
            "linkedin_url": raw_profile.get("linkedin_url"),
            "full_name": raw_profile.get("full_name"),
            "first_name": raw_profile.get("first_name"),
            "last_name": raw_profile.get("last_name"),
            "headline": raw_profile.get("headline"),
            "summary": raw_profile.get("summary"),
            "location": {
                "city": raw_profile.get("city"),
                "state": raw_profile.get("state"),
                "country": raw_profile.get("country")
            },
            "experiences": raw_profile.get("experiences", []),
            "education": raw_profile.get("education", []),
            "skills": raw_profile.get("skills", []),
            "languages": raw_profile.get("languages", []),
            "certifications": raw_profile.get("certifications", []),
            "contact": {
                "email": raw_profile.get("emails", [None])[0],
                "phone": raw_profile.get("phone_numbers", [None])[0]
            },
            "social": {
                "twitter": raw_profile.get("twitter_url"),
                "github": raw_profile.get("github_url")
            },
            "profile_picture_url": raw_profile.get("profile_picture_url"),
            "connections": raw_profile.get("connections"),
            "raw": raw_profile
        }


if __name__ == "__main__":
    import asyncio
    
    async def test():
        client = NubelaClient()
        await client.initialize()
        
        profile = await client.get_profile(
            "https://www.linkedin.com/in/williamhgates"
        )
        
        print(f"Name: {profile['full_name']}")
        print(f"Headline: {profile['headline']}")
        
        await client.close()
    
    asyncio.run(test())
