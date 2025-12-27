"""Constants for the Scout Service.

Contains central configuration values, hardware requirements,
and magic numbers used across the service.
"""

# GitHub Search Keywords
COMPANY_KEYWORDS = ["google", "microsoft", "amazon", "meta", "apple", "netflix", "uber", "airbnb"]

# Agent Configuration
CRITICAL_AGENTS = ["interview-agent", "scout-coordinator-agent", "data-enrichment-agent"]

# Programming Language Mapping
LANGUAGE_MAPPING = {
    "python": "python",
    "javascript": "javascript",
    "js": "javascript",
    "java": "java",
    "ruby": "ruby",
    "go": "go",
    "golang": "go",
    "rust": "rust",
    "typescript": "typescript",
    "ts": "typescript",
    "react": "javascript",
    "vue": "javascript",
    "angular": "javascript",
    "node": "javascript",
    "nodejs": "javascript",
    "c++": "c++",
    "cpp": "c++",
    "c#": "c#",
    "csharp": "c#",
    "php": "php",
    "swift": "swift",
    "kotlin": "kotlin",
    "r": "r",
    "scala": "scala",
    "dart": "dart",
}

# Timeout Configuration (Seconds)
DEFAULT_TIMEOUT = 30.0
OLLAMA_TIMEOUT = 300
GITHUB_API_TIMEOUT = 30.0
CONTACTOUT_API_TIMEOUT = 20.0
