"""Text AI API module."""
from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from money_api.client import MoneyAPI


class TextAPI:
    """Text AI operations."""

    def __init__(self, client: "MoneyAPI"):
        self.client = client

    def complete(
        self,
        prompt: str,
        model: str = "claude-sonnet",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system: Optional[str] = None
    ) -> Dict:
        """Generate text completion.

        Args:
            prompt: Input prompt
            model: Model to use (claude-sonnet, gpt-4)
            max_tokens: Maximum tokens to generate
            temperature: Temperature for randomness
            system: System prompt

        Returns:
            Response with generated text and metadata
        """
        return self.client.request(
            "POST",
            "/api/v1/text/completions",
            json={
                "prompt": prompt,
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system
            }
        )

    def summarize(
        self,
        text: str,
        length: str = "medium"
    ) -> Dict:
        """Summarize text.

        Args:
            text: Text to summarize
            length: Summary length (short, medium, long)

        Returns:
            Summary and metadata
        """
        return self.client.request(
            "POST",
            "/api/v1/text/summarize",
            json={"text": text, "length": length}
        )

    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Dict:
        """Translate text.

        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            Translated text and metadata
        """
        return self.client.request(
            "POST",
            "/api/v1/text/translate",
            json={
                "text": text,
                "source_lang": source_lang,
                "target_lang": target_lang
            }
        )

    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze text sentiment.

        Args:
            text: Text to analyze

        Returns:
            Sentiment analysis results
        """
        return self.client.request(
            "POST",
            "/api/v1/text/sentiment",
            params={"text": text}
        )

    def extract_entities(self, text: str) -> Dict:
        """Extract named entities.

        Args:
            text: Text to process

        Returns:
            Extracted entities
        """
        return self.client.request(
            "POST",
            "/api/v1/text/entities",
            params={"text": text}
        )
