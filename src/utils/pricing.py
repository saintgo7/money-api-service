"""Pricing calculations."""
from decimal import Decimal
from typing import Dict


class PricingCalculator:
    """Calculate costs for various API operations."""

    def __init__(self, config: Dict[str, float]):
        self.config = config

    def calculate_text_cost(
        self,
        tokens: int,
        model: str = "claude-sonnet"
    ) -> Decimal:
        """Calculate cost for text operations."""
        if "claude" in model.lower():
            price_per_1k = self.config.get("price_text_claude", 0.003)
        elif "gpt" in model.lower():
            price_per_1k = self.config.get("price_text_gpt4", 0.006)
        else:
            price_per_1k = 0.003

        return Decimal(str((tokens / 1000) * price_per_1k))

    def calculate_image_cost(
        self,
        n_images: int,
        model: str = "sdxl"
    ) -> Decimal:
        """Calculate cost for image generation."""
        if "sdxl" in model.lower():
            price_per_image = self.config.get("price_image_sdxl", 0.02)
        elif "dall" in model.lower():
            price_per_image = self.config.get("price_image_dalle", 0.04)
        else:
            price_per_image = 0.02

        return Decimal(str(n_images * price_per_image))

    def calculate_audio_transcribe_cost(
        self,
        duration_seconds: float
    ) -> Decimal:
        """Calculate cost for audio transcription."""
        duration_minutes = duration_seconds / 60
        price_per_minute = self.config.get("price_audio_transcribe", 0.006)
        return Decimal(str(duration_minutes * price_per_minute))

    def calculate_audio_synthesize_cost(
        self,
        char_count: int
    ) -> Decimal:
        """Calculate cost for text-to-speech."""
        price_per_1k = self.config.get("price_audio_synthesize", 0.015)
        return Decimal(str((char_count / 1000) * price_per_1k))

    def estimate_monthly_cost(
        self,
        usage_stats: Dict
    ) -> Decimal:
        """Estimate monthly cost based on usage patterns."""
        total = Decimal("0")

        for endpoint, stats in usage_stats.get("by_endpoint", {}).items():
            total += Decimal(str(stats.get("cost", 0)))

        return total
