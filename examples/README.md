# Money API Examples

Collection of example applications demonstrating Money API usage.

## Examples

### 1. Python Client (`python_client.py`)

Basic Python client demonstrating all API features.

```bash
python examples/python_client.py
```

### 2. Node.js Client (`nodejs_client.js`)

Basic Node.js client with async/await.

```bash
node examples/nodejs_client.js
```

### 3. Simple Chatbot (`simple_chatbot.py`)

Interactive chatbot with conversation history.

```bash
python examples/simple_chatbot.py
```

**Features:**
- Conversation history (last 5 messages)
- Credit balance checking
- Cost tracking per message

### 4. Batch Translation (`batch_translation.py`)

Translate CSV files between languages.

```bash
# Create sample input.csv:
# text
# "Hello, world!"
# "How are you?"

python examples/batch_translation.py sk_your_key input.csv output.csv en es
```

**Use Cases:**
- Translate product catalogs
- Localize marketing content
- Process customer feedback

### 5. Content Generator (`content_generator.py`)

Generate complete marketing content packages.

```bash
python examples/content_generator.py
```

**Generates:**
- 3 catchy headlines
- 2-paragraph product description
- 3 social media posts
- 5 email subject lines

**Output:** JSON file with all generated content

### 6. Batch Image Generator (`image_batch_generator.py`)

Generate multiple images from prompts file.

```bash
# Create prompts.json:
{
  "prompts": [
    "A sunset over mountains",
    "A futuristic city",
    "A peaceful forest"
  ]
}

python examples/image_batch_generator.py sk_your_key prompts.json ./output
```

**Use Cases:**
- Generate product mockups
- Create marketing visuals
- Batch illustration generation

## Installation

```bash
# Install dependencies
pip install requests

# Or install Money API SDK
pip install money-api-client
```

## Configuration

All examples require a Money API key:

```bash
export MONEY_API_KEY=sk_your_api_key_here
```

Or pass as command-line argument.

## Error Handling

All examples include:
- Rate limit handling
- Insufficient credits detection
- Automatic retry logic
- Detailed error messages

## Cost Tracking

Each example displays:
- Cost per operation
- Total cost for batch operations
- Remaining credit balance

## Best Practices

1. **Batch Operations**: Use batch examples for bulk processing
2. **Error Handling**: Always handle RateLimitError and InsufficientCreditsError
3. **Cost Monitoring**: Track costs before large operations
4. **Context Management**: Use `with` statement for auto-cleanup

```python
with MoneyAPI(api_key=key) as client:
    response = client.text.complete(prompt="...")
```

## Advanced Examples

For more advanced examples, see:
- `/examples/web-app/` - Flask web application
- `/examples/discord-bot/` - Discord integration
- `/examples/slack-bot/` - Slack integration

## Support

- Documentation: https://docs.moneyapi.example.com
- Examples Repository: https://github.com/yourusername/money-api-examples
- Issues: https://github.com/yourusername/money-api-service/issues
