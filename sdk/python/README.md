# Money API Python SDK

Official Python client for Money API Service.

## Installation

```bash
pip install money-api-client
```

## Quick Start

```python
from money_api import MoneyAPI

# Initialize client
client = MoneyAPI(api_key="sk_your_api_key")

# Generate text
response = client.text.complete(
    prompt="Write a haiku about AI",
    model="claude-sonnet",
    max_tokens=100
)
print(response["content"])

# Generate image
image = client.image.generate(
    prompt="A sunset over mountains",
    model="sdxl"
)
print(image["images"][0])

# Get usage stats
stats = client.management.get_usage(period="30d")
print(f"Total cost: ${stats['total_cost']:.2f}")
```

## Documentation

Full documentation available at: https://docs.moneyapi.example.com

## License

MIT
