# Contributing to Money API Service

Thank you for your interest in contributing to Money API Service! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/money-api-service/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)
   - Error messages or logs

### Suggesting Features

1. Check existing feature requests in Issues
2. Create a new issue with:
   - Clear use case
   - Expected behavior
   - Potential implementation approach
   - Examples from other projects (if applicable)

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/money-api-service.git
   cd money-api-service
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```

3. **Make your changes**
   - Follow the code style guidelines
   - Add tests for new features
   - Update documentation

4. **Run tests**
   ```bash
   make test
   ```

5. **Format code**
   ```bash
   make format
   ```

6. **Commit changes**
   ```bash
   git add .
   git commit -m "Add: Brief description of changes"
   ```

   Commit message format:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for improvements
   - `Docs:` for documentation
   - `Refactor:` for code refactoring
   - `Test:` for test additions/changes

7. **Push to your fork**
   ```bash
   git push origin feature/my-feature
   ```

8. **Create Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template

## Development Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL, Redis (via Docker)

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/money-api-service.git
cd money-api-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Start services
docker-compose up -d postgres redis

# Run migrations
alembic upgrade head

# Run development server
make dev
```

## Code Style

### Python

- Follow PEP 8
- Use Black for formatting (100 character line length)
- Use type hints
- Write docstrings for functions and classes

Example:
```python
def calculate_cost(tokens: int, price_per_1k: float) -> Decimal:
    """Calculate cost based on token usage.

    Args:
        tokens: Number of tokens used
        price_per_1k: Price per 1000 tokens

    Returns:
        Total cost as Decimal
    """
    return Decimal(str((tokens / 1000) * price_per_1k))
```

### TypeScript/JavaScript

- Use ESLint with Airbnb config
- Use Prettier for formatting
- Prefer async/await over callbacks
- Use TypeScript for type safety

## Testing

### Writing Tests

```python
# tests/test_text_api.py
import pytest
from fastapi.testclient import TestClient

def test_text_completion(client: TestClient, api_key: str):
    response = client.post(
        "/api/v1/text/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "prompt": "Hello",
            "model": "claude-sonnet",
            "max_tokens": 10
        }
    )
    assert response.status_code == 200
    assert "content" in response.json()
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_text_api.py

# Run with coverage
pytest --cov=src tests/
```

## Documentation

- Update README.md for major changes
- Add/update API documentation in docs/
- Include code examples
- Update CHANGELOG.md

## Review Process

1. Maintainers review PRs within 3-5 business days
2. Address review comments
3. Once approved, maintainers will merge
4. Delete your feature branch after merge

## Release Process

Maintainers follow semantic versioning:

- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

## Questions?

- Open an issue with the "question" label
- Join our Discord community
- Email: contribute@moneyapi.example.com

Thank you for contributing! 🎉
