"""
Example Python client for Money API Service

Install dependencies:
    pip install requests
"""

import requests
import json
from typing import Optional


class MoneyAPIClient:
    """Simple client for Money API Service."""

    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def text_completion(
        self,
        prompt: str,
        model: str = "claude-sonnet",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system: Optional[str] = None
    ) -> dict:
        """Generate text completion."""
        response = requests.post(
            f"{self.base_url}/api/v1/text/completions",
            headers=self.headers,
            json={
                "prompt": prompt,
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system
            }
        )
        response.raise_for_status()
        return response.json()

    def summarize(self, text: str, length: str = "medium") -> dict:
        """Summarize text."""
        response = requests.post(
            f"{self.base_url}/api/v1/text/summarize",
            headers=self.headers,
            json={"text": text, "length": length}
        )
        response.raise_for_status()
        return response.json()

    def translate(self, text: str, source_lang: str, target_lang: str) -> dict:
        """Translate text."""
        response = requests.post(
            f"{self.base_url}/api/v1/text/translate",
            headers=self.headers,
            json={
                "text": text,
                "source_lang": source_lang,
                "target_lang": target_lang
            }
        )
        response.raise_for_status()
        return response.json()

    def generate_image(
        self,
        prompt: str,
        model: str = "sdxl",
        size: str = "1024x1024",
        n: int = 1
    ) -> dict:
        """Generate images."""
        response = requests.post(
            f"{self.base_url}/api/v1/image/generate",
            headers=self.headers,
            json={
                "prompt": prompt,
                "model": model,
                "size": size,
                "n": n
            }
        )
        response.raise_for_status()
        return response.json()

    def get_usage_stats(self, period: str = "30d") -> dict:
        """Get usage statistics."""
        response = requests.get(
            f"{self.base_url}/api/v1/manage/usage",
            headers=self.headers,
            params={"period": period}
        )
        response.raise_for_status()
        return response.json()


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = MoneyAPIClient(api_key="sk_your_api_key_here")

    # Text completion example
    print("=== Text Completion ===")
    result = client.text_completion(
        prompt="Write a haiku about artificial intelligence",
        max_tokens=100
    )
    print(f"Generated: {result['content']}")
    print(f"Cost: ${result['cost']:.4f}")

    # Summarization example
    print("\n=== Summarization ===")
    long_text = """
    Artificial intelligence (AI) is transforming industries across the globe.
    From healthcare to finance, AI systems are helping humans make better decisions,
    automate repetitive tasks, and unlock new insights from data. Machine learning,
    a subset of AI, enables computers to learn from experience without being explicitly
    programmed. Deep learning, using neural networks, has achieved remarkable results
    in image recognition, natural language processing, and game playing.
    """
    summary = client.summarize(long_text, length="short")
    print(f"Summary: {summary['summary']}")

    # Translation example
    print("\n=== Translation ===")
    translation = client.translate(
        text="Hello, how are you?",
        source_lang="en",
        target_lang="es"
    )
    print(f"Translated: {translation['translated_text']}")

    # Usage stats
    print("\n=== Usage Statistics ===")
    stats = client.get_usage_stats(period="30d")
    print(f"Total requests: {stats['total_requests']}")
    print(f"Total cost: ${stats['total_cost']:.2f}")
    print(f"Total tokens: {stats['total_tokens']}")
