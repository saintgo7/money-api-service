"""Image AI API module."""
from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from money_api.client import MoneyAPI


class ImageAPI:
    """Image AI operations."""

    def __init__(self, client: "MoneyAPI"):
        self.client = client

    def generate(
        self,
        prompt: str,
        model: str = "sdxl",
        size: str = "1024x1024",
        n: int = 1,
        style: Optional[str] = None
    ) -> Dict:
        """Generate images from text.

        Args:
            prompt: Text description
            model: Model to use (sdxl, dall-e-3)
            size: Image size
            n: Number of images
            style: Style preset

        Returns:
            Generated images and metadata
        """
        return self.client.request(
            "POST",
            "/api/v1/image/generate",
            json={
                "prompt": prompt,
                "model": model,
                "size": size,
                "n": n,
                "style": style
            }
        )
