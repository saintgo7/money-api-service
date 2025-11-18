"""Management API module."""
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from money_api.client import MoneyAPI


class ManagementAPI:
    """Account management operations."""

    def __init__(self, client: "MoneyAPI"):
        self.client = client

    def get_usage(self, period: str = "30d") -> Dict:
        """Get usage statistics.

        Args:
            period: Time period (24h, 7d, 30d, 90d)

        Returns:
            Usage statistics
        """
        return self.client.request(
            "GET",
            "/api/v1/manage/usage",
            params={"period": period}
        )

    def get_current_user(self) -> Dict:
        """Get current user information.

        Returns:
            User account details
        """
        return self.client.request("GET", "/api/v1/manage/users/me")

    def create_api_key(self, name: str) -> Dict:
        """Create new API key.

        Args:
            name: Name for the API key

        Returns:
            New API key details
        """
        return self.client.request(
            "POST",
            "/api/v1/manage/api-keys",
            json={"name": name}
        )

    def list_api_keys(self) -> Dict:
        """List all API keys.

        Returns:
            List of API keys
        """
        return self.client.request("GET", "/api/v1/manage/api-keys")
