# Money API CLI

Official command-line interface for Money API Service - AI API platform with cost tracking and analytics.

## Features

- 🚀 Fast and intuitive CLI
- 📝 Text generation with streaming
- 🎨 Image generation
- ⚡ Batch processing
- 🤖 Fine-tuning management
- 📊 Usage analytics
- 📈 ML-based predictions
- 💰 Cost tracking
- 🎨 Beautiful terminal output with Rich

## Installation

### Via pip

```bash
pip install money-api
```

### From source

```bash
git clone https://github.com/money-api/cli.git
cd cli
pip install -e .
```

## Quick Start

### Configure API Key

```bash
# Set API key
money-api configure --api-key YOUR_API_KEY

# Or use environment variable
export MONEY_API_KEY=your-api-key
```

### Generate Text

```bash
# Simple text generation
money-api generate "Explain quantum computing in simple terms"

# With custom model and tokens
money-api generate "Write a haiku about AI" --model gpt-4 --max-tokens 100

# Streaming mode
money-api generate "Write a short story" --stream
```

### Generate Images

```bash
# Simple image generation
money-api image "A serene mountain landscape at sunset"

# With custom size and model
money-api image "Cyberpunk city at night" --model sdxl --width 1920 --height 1080

# Save to file
money-api image "Abstract art" --output image.png
```

### Account Management

```bash
# Check balance
money-api balance

# View usage statistics
money-api usage --days 30
```

## Commands

### Text Generation

```bash
# Generate text
money-api generate PROMPT [OPTIONS]

Options:
  --model TEXT          Model name (default: claude-3-sonnet)
  --max-tokens INTEGER  Maximum tokens (default: 1000)
  --stream             Enable streaming
```

### Image Generation

```bash
# Generate image
money-api image PROMPT [OPTIONS]

Options:
  --model TEXT     Model name (default: sdxl)
  --width INTEGER  Image width (default: 1024)
  --height INTEGER Image height (default: 1024)
  --output TEXT    Output file path
```

### Batch Processing

```bash
# Process batch text requests from file
money-api batch text FILE [OPTIONS]

# Create prompts.txt with one prompt per line
echo "Explain AI" > prompts.txt
echo "Explain ML" >> prompts.txt
echo "Explain DL" >> prompts.txt

# Process batch
money-api batch text prompts.txt --model claude-3-sonnet --parallel

Options:
  --model TEXT          Model name
  --max-tokens INTEGER  Maximum tokens
  --parallel           Process in parallel (default)
  --sequential         Process sequentially
```

### Fine-Tuning

```bash
# Create fine-tuning job
money-api finetune create --training-file file-abc123 --model gpt-3.5-turbo --suffix my-model

# List fine-tuning jobs
money-api finetune list --limit 20

# Get job status
money-api finetune status JOB_ID

# Cancel job
money-api finetune cancel JOB_ID
```

### ML Predictions

```bash
# Predict next month's cost
money-api ml predict-cost

# Detect usage anomalies
money-api ml detect-anomalies --days 30

# Get usage insights and recommendations
money-api ml insights
```

### Analytics

```bash
# Get usage statistics
money-api usage --days 30

# Check account balance
money-api balance
```

## Examples

### Example 1: Generate and Save Multiple Texts

```bash
# Create a batch file
cat > batch.txt << EOF
Explain quantum computing
Explain machine learning
Explain deep learning
EOF

# Process batch and save results
money-api batch text batch.txt --model claude-3-sonnet > results.json
```

### Example 2: Generate Images in Batch

```bash
# Create image prompts
cat > images.txt << EOF
A serene mountain landscape
A cyberpunk city at night
Abstract geometric art
EOF

# Generate images
while IFS= read -r prompt; do
  money-api image "$prompt" --output "${prompt// /_}.png"
done < images.txt
```

### Example 3: Monitor Costs

```bash
# Check current balance
money-api balance

# Predict future costs
money-api ml predict-cost

# Detect unusual spending
money-api ml detect-anomalies --days 30

# Get optimization recommendations
money-api ml insights
```

### Example 4: Fine-Tune Custom Model

```bash
# Upload training data (assuming file uploaded separately)
# Create fine-tuning job
money-api finetune create \
  --training-file file-abc123 \
  --model gpt-3.5-turbo \
  --suffix customer-support

# Monitor progress
watch -n 10 money-api finetune status JOB_ID

# List all jobs
money-api finetune list
```

### Example 5: Streaming Text Generation

```bash
# Stream response in real-time
money-api generate "Write a detailed explanation of neural networks" \
  --stream \
  --model claude-3-opus \
  --max-tokens 2000
```

## Configuration

### Configuration File

The CLI stores configuration in `~/.money-api/config.json`:

```json
{
  "api_key": "your-api-key",
  "base_url": "https://api.money-api.com"
}
```

### Environment Variables

```bash
# API key
export MONEY_API_KEY=your-api-key

# Base URL (optional)
export MONEY_API_BASE_URL=https://api.custom-domain.com

# Use in CLI
money-api generate "Hello, world!"
```

### Custom Base URL

```bash
# Configure custom base URL
money-api configure \
  --api-key YOUR_KEY \
  --base-url https://api.custom-domain.com
```

## Output Formats

### JSON Output

```bash
# Generate JSON output for scripting
money-api generate "Explain AI" --format json > output.json

# Parse with jq
money-api generate "Hello" --format json | jq '.text'
```

### Table Output

```bash
# View usage as table
money-api usage --days 30 --format table

# View fine-tuning jobs as table
money-api finetune list --format table
```

## Error Handling

```bash
# CLI provides helpful error messages
money-api generate "test"
# Error: API key not configured
# Run: money-api configure --api-key YOUR_KEY

# Check exit codes
money-api generate "test" && echo "Success" || echo "Failed"
```

## Tips & Tricks

### 1. Use Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias mai='money-api'
alias maig='money-api generate'
alias maib='money-api balance'

# Usage
maig "Explain quantum computing"
maib
```

### 2. Pipe Output

```bash
# Generate and process
money-api generate "List 5 ideas" | grep "^[0-9]"

# Save to file
money-api generate "Long article" > article.txt
```

### 3. Combine Commands

```bash
# Check balance before expensive operation
if [ $(money-api balance --format json | jq -r '.balance') -gt 10 ]; then
  money-api batch text large-batch.txt
else
  echo "Insufficient balance"
fi
```

### 4. Monitor in Real-Time

```bash
# Watch balance
watch -n 60 money-api balance

# Monitor fine-tuning job
watch -n 10 money-api finetune status JOB_ID
```

## Troubleshooting

### API Key Not Found

```bash
# Check configuration
cat ~/.money-api/config.json

# Reconfigure
money-api configure --api-key YOUR_KEY
```

### Connection Errors

```bash
# Test connection
money-api balance

# Use custom base URL
money-api configure --base-url https://api.custom-domain.com
```

### Rate Limiting

```bash
# Check error message
money-api generate "test"
# Error: Rate limit exceeded - please wait

# Wait and retry with exponential backoff
```

## Documentation

Full API documentation: https://docs.money-api.com

## Support

- GitHub Issues: https://github.com/money-api/cli/issues
- Email: support@money-api.com
- Documentation: https://docs.money-api.com

## License

MIT License - see LICENSE file for details
