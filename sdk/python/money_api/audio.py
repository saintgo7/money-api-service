"""Audio AI API module."""
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from money_api.client import MoneyAPI


class AudioAPI:
    """Audio AI operations."""

    def __init__(self, client: "MoneyAPI"):
        self.client = client

    def synthesize(
        self,
        text: str,
        voice: str = "alloy",
        speed: float = 1.0,
        format: str = "mp3"
    ) -> Dict:
        """Convert text to speech.

        Args:
            text: Text to synthesize
            voice: Voice ID
            speed: Speech speed
            format: Audio format

        Returns:
            Audio URL and metadata
        """
        return self.client.request(
            "POST",
            "/api/v1/audio/synthesize",
            json={
                "text": text,
                "voice": voice,
                "speed": speed,
                "format": format
            }
        )
