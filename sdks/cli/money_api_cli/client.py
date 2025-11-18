"""Money API HTTP client."""
import requests
from typing import Dict, List, Any, Iterator


class MoneyAPIClient:
    """Client for Money API Service."""

    def __init__(self, api_key: str, base_url: str = "https://api.money-api.com"):
        """Initialize client.

        Args:
            api_key: API key
            base_url: Base API URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

    def generate_text(
        self,
        prompt: str,
        model: str = "claude-3-sonnet",
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Generate text completion."""
        response = self.session.post(
            f"{self.base_url}/v1/text/completions",
            json={
                "prompt": prompt,
                "model": model,
                "max_tokens": max_tokens,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()

    def stream_text(
        self,
        prompt: str,
        model: str = "claude-3-sonnet",
        max_tokens: int = 1000
    ) -> Iterator[str]:
        """Stream text completion."""
        response = self.session.post(
            f"{self.base_url}/v1/text/completions",
            json={
                "prompt": prompt,
                "model": model,
                "max_tokens": max_tokens,
                "stream": True
            },
            stream=True
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    chunk = line[6:]
                    if chunk != '[DONE]':
                        yield chunk

    def generate_image(
        self,
        prompt: str,
        model: str = "sdxl",
        width: int = 1024,
        height: int = 1024
    ) -> Dict[str, Any]:
        """Generate image."""
        response = self.session.post(
            f"{self.base_url}/v1/image/generate",
            json={
                "prompt": prompt,
                "model": model,
                "width": width,
                "height": height
            }
        )
        response.raise_for_status()
        return response.json()

    def batch_text(
        self,
        requests: List[Dict[str, Any]],
        parallel: bool = True
    ) -> Dict[str, Any]:
        """Process batch text requests."""
        response = self.session.post(
            f"{self.base_url}/v1/batch/text",
            json={
                "requests": requests,
                "parallel": parallel
            }
        )
        response.raise_for_status()
        return response.json()

    def create_finetune_job(
        self,
        training_file_id: str,
        model: str = "gpt-3.5-turbo",
        suffix: str = None
    ) -> Dict[str, Any]:
        """Create fine-tuning job."""
        payload = {
            "training_file_id": training_file_id,
            "model": model
        }
        if suffix:
            payload["suffix"] = suffix

        response = self.session.post(
            f"{self.base_url}/v1/fine-tuning/jobs",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def list_finetune_jobs(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List fine-tuning jobs."""
        response = self.session.get(
            f"{self.base_url}/v1/fine-tuning/jobs",
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json()

    def get_finetune_job(self, job_id: str) -> Dict[str, Any]:
        """Get fine-tuning job status."""
        response = self.session.get(
            f"{self.base_url}/v1/fine-tuning/jobs/{job_id}"
        )
        response.raise_for_status()
        return response.json()

    def predict_cost(self) -> Dict[str, Any]:
        """Predict monthly cost."""
        response = self.session.get(
            f"{self.base_url}/v1/ml/predict/cost"
        )
        response.raise_for_status()
        return response.json()

    def detect_anomalies(self, days: int = 30) -> List[Dict[str, Any]]:
        """Detect usage anomalies."""
        response = self.session.get(
            f"{self.base_url}/v1/ml/anomalies/detect",
            params={"days": days}
        )
        response.raise_for_status()
        return response.json()

    def get_insights(self) -> Dict[str, Any]:
        """Get usage insights."""
        response = self.session.get(
            f"{self.base_url}/v1/ml/insights/usage"
        )
        response.raise_for_status()
        return response.json()

    def get_balance(self) -> Dict[str, Any]:
        """Get account balance."""
        response = self.session.get(
            f"{self.base_url}/v1/account/balance"
        )
        response.raise_for_status()
        return response.json()

    def get_usage(self) -> Dict[str, Any]:
        """Get usage summary."""
        response = self.session.get(
            f"{self.base_url}/v1/account/usage"
        )
        response.raise_for_status()
        return response.json()
