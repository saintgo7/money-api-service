# Money API VS Code Extension

Official VS Code extension for Money API Service - AI API platform with cost tracking, usage analytics, and multi-provider support.

## Features

- 🚀 Generate text directly in VS Code
- 🎨 Generate images from prompts
- 💰 Real-time balance and usage tracking
- 📊 Usage insights and cost predictions
- 🔍 Anomaly detection
- 📈 Cost breakdown by endpoint
- ⚡ Smart recommendations
- 🎯 Context menu integration

## Installation

### From VS Code Marketplace

1. Open VS Code
2. Press `Ctrl+P` (or `Cmd+P` on Mac)
3. Type: `ext install money-api.money-api`
4. Press Enter

### From VSIX

1. Download the latest `.vsix` file from releases
2. Open VS Code
3. Go to Extensions view (`Ctrl+Shift+X`)
4. Click "..." menu → "Install from VSIX..."
5. Select the downloaded file

## Quick Start

### 1. Configure API Key

Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac) and run:

```
Money API: Configure API Key
```

Enter your Money API key when prompted.

### 2. Generate Text

**Method 1: Command Palette**
- Press `Ctrl+Shift+P`
- Type: `Money API: Generate Text`
- Enter your prompt

**Method 2: Context Menu**
- Select text in editor
- Right-click → "Money API: Generate Text"
- The selected text will be used as prompt

**Method 3: Keyboard Shortcut**
- Select text (optional)
- Press `Ctrl+Alt+G` (or `Cmd+Alt+G` on Mac)

### 3. Generate Image

Press `Ctrl+Shift+P` and run:

```
Money API: Generate Image
```

Enter your image description.

## Commands

All commands are available via Command Palette (`Ctrl+Shift+P`):

| Command | Description | Shortcut |
|---------|-------------|----------|
| `Money API: Configure API Key` | Set your API key | - |
| `Money API: Generate Text` | Generate text completion | `Ctrl+Alt+G` |
| `Money API: Generate Image` | Generate image | - |
| `Money API: Show Balance` | Display current balance | - |
| `Money API: Show Usage Statistics` | View usage summary | - |
| `Money API: Predict Monthly Cost` | ML cost prediction | - |
| `Money API: Detect Anomalies` | Find unusual patterns | - |

## Sidebar

The extension adds a Money API sidebar with two panels:

### Account Overview

- **Account Balance**: Current balance in real-time
- **Usage Statistics**: Requests and costs for current period
- **Cost Prediction**: ML-based monthly predictions

### Usage Insights

- **Recommendations**: AI-powered optimization tips
- **Top Endpoints by Cost**: Cost breakdown by endpoint

Click the refresh icon (⟳) to update data manually.

## Configuration

Access settings via `File → Preferences → Settings` (or `Code → Preferences → Settings` on Mac), then search for "Money API":

| Setting | Description | Default |
|---------|-------------|---------|
| `moneyApi.apiKey` | Your Money API key | (empty) |
| `moneyApi.baseUrl` | Base API URL | `https://api.money-api.com` |
| `moneyApi.defaultModel` | Default text model | `claude-3-sonnet` |
| `moneyApi.maxTokens` | Maximum tokens | `1000` |
| `moneyApi.showCostNotifications` | Show cost after generation | `true` |
| `moneyApi.autoRefreshInterval` | Auto-refresh interval (seconds) | `60` |

### Example settings.json

```json
{
  "moneyApi.apiKey": "your-api-key",
  "moneyApi.defaultModel": "gpt-4",
  "moneyApi.maxTokens": 2000,
  "moneyApi.showCostNotifications": true,
  "moneyApi.autoRefreshInterval": 30
}
```

## Usage Examples

### Example 1: Code Explanation

1. Select code snippet in editor
2. Right-click → "Money API: Generate Text"
3. Or press `Ctrl+Alt+G`
4. The AI will explain the selected code

### Example 2: Generate Documentation

1. Select function/class
2. Press `Ctrl+Shift+P`
3. Run "Money API: Generate Text"
4. Type: "Generate documentation for this code"

### Example 3: Code Refactoring

1. Select code to refactor
2. Right-click → "Money API: Generate Text"
3. Type prompt: "Refactor this code to use async/await"

### Example 4: Generate Test Cases

1. Select function
2. Generate with prompt: "Write unit tests for this function"

### Example 5: Create README

1. Create new file `README.md`
2. Generate with prompt: "Create a comprehensive README for [project description]"

### Example 6: Image Generation for Documentation

1. Run "Money API: Generate Image"
2. Enter: "Architecture diagram for microservices system"
3. Get URL to include in documentation

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Alt+G` | Generate Text |
| `Ctrl+Alt+I` | Generate Image |
| `Ctrl+Alt+B` | Show Balance |

Customize shortcuts via `File → Preferences → Keyboard Shortcuts`.

## Tips & Tricks

### 1. Quick Text Generation

Select any text and press `Ctrl+Alt+G` to use it as a prompt.

### 2. Monitor Costs

Enable auto-refresh to keep track of spending in real-time:

```json
{
  "moneyApi.autoRefreshInterval": 30,
  "moneyApi.showCostNotifications": true
}
```

### 3. Use Different Models

Change default model for specific use cases:

```json
{
  "moneyApi.defaultModel": "gpt-4"  // For complex tasks
}
```

### 4. Multi-line Prompts

Use selection as prompt for multi-line generation:

```
1. Select text
2. Ctrl+Alt+G
3. Response replaces selection
```

### 5. View Insights

Open the sidebar to see:
- Cost optimization recommendations
- Anomaly detection results
- Endpoint cost breakdown

## Troubleshooting

### API Key Not Working

1. Verify key in settings: `moneyApi.apiKey`
2. Check key is valid on Money API dashboard
3. Try reconfiguring: `Money API: Configure API Key`

### Connection Errors

1. Check base URL: `moneyApi.baseUrl`
2. Verify network connection
3. Check firewall settings

### No Cost Notifications

Enable in settings:

```json
{
  "moneyApi.showCostNotifications": true
}
```

### Sidebar Not Showing

1. View → Open View → Money API
2. Or click Money API icon in Activity Bar

## Privacy & Security

- API keys are stored in VS Code settings (encrypted)
- No data is sent to third parties
- All API calls are direct to Money API servers
- Telemetry can be disabled in VS Code settings

## Support

- 📧 Email: support@money-api.com
- 🐛 Issues: https://github.com/money-api/vscode-extension/issues
- 📚 Documentation: https://docs.money-api.com
- 💬 Discord: https://discord.gg/money-api

## Release Notes

### 2.0.0

- ✨ Initial release
- 🚀 Text and image generation
- 💰 Balance and usage tracking
- 📊 ML-based predictions
- 🔍 Anomaly detection
- 📈 Usage insights
- 🎯 Context menu integration
- ⚡ Auto-refresh

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.

---

Made with ❤️ by the Money API team
