"""Main Money API client."""
import requests
from typing import Optional, Dict, List
from money_api.text import TextAPI
from money_api.image import ImageAPI
from money_api.audio import AudioAPI
from money_api.document import DocumentAPI
from money_api.management import ManagementAPI
from money_api.exceptions import MoneyAPIError, RateLimitError, InsufficientCreditsError


class MoneyAPI:
    """Main client for Money API Service."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.moneyapi.example.com"
    ):
        """Initialize Money API client.

        Args:
            api_key: Your Money API key
            base_url: Base URL for the API
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "money-api-python/1.0.0"
        })

        # Initialize API modules
        self.text = TextAPI(self)
        self.image = ImageAPI(self)
        self.audio = AudioAPI(self)
        self.document = DocumentAPI(self)
        self.management = ManagementAPI(self)

    def request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict:
        """Make HTTP request to API.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional arguments for requests

        Returns:
            Response data as dict

        Raises:
            MoneyAPIError: On API errors
            RateLimitError: On rate limit exceeded
            InsufficientCreditsError: On insufficient credits
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(method, url, **kwargs)

            # Check for rate limiting
            if response.status_code == 429:
                raise RateLimitError(
                    "Rate limit exceeded",
                    retry_after=int(response.headers.get("X-RateLimit-Reset", 0))
                )

            # Check for insufficient credits
            if response.status_code == 402:
                raise InsufficientCreditsError("Insufficient credits")

            # Raise for other errors
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            raise MoneyAPIError(f"Request failed: {str(e)}") from e

    def close(self):
        """Close the client session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
