# Money API iOS SDK

Official Swift SDK for Money API Service - AI API platform with cost tracking, usage analytics, and multi-provider support.

## Features

- 🚀 Modern async/await Swift API
- 📱 iOS, macOS, tvOS, watchOS support
- 🔄 Streaming text generation
- 📊 Usage analytics and cost tracking
- 🤖 AI model fine-tuning
- 📈 ML-based cost prediction
- ⚡ Batch processing
- 🔌 WebSocket real-time updates
- 💪 Type-safe with full Codable support

## Requirements

- iOS 13.0+ / macOS 10.15+ / tvOS 13.0+ / watchOS 6.0+
- Swift 5.5+
- Xcode 13.0+

## Installation

### Swift Package Manager

Add the following to your `Package.swift`:

```swift
dependencies: [
    .package(url: "https://github.com/money-api/ios-sdk.git", from: "2.0.0")
]
```

Or in Xcode:
1. File → Add Packages...
2. Enter: `https://github.com/money-api/ios-sdk.git`
3. Select version: 2.0.0+

## Quick Start

```swift
import MoneyAPI

// Initialize client
let client = MoneyAPIClient(apiKey: "your-api-key")

// Generate text
let completion = try await client.generateText(
    prompt: "Explain quantum computing in simple terms",
    model: "claude-3-sonnet",
    maxTokens: 500
)
print(completion.text)
print("Cost: $\(completion.cost)")

// Generate image
let image = try await client.generateImage(
    prompt: "A serene mountain landscape at sunset",
    model: "sdxl",
    width: 1024,
    height: 1024
)
print("Image URL: \(image.url)")

// Get usage analytics
let analytics = try await client.getAnalytics(
    startDate: Date().addingTimeInterval(-30*24*60*60),
    endDate: Date(),
    groupBy: "day"
)
print("Total requests: \(analytics.summary.totalRequests)")
print("Total cost: $\(analytics.summary.totalCost)")
```

## Streaming

Stream text generation in real-time:

```swift
try await client.streamText(
    prompt: "Write a short story about AI",
    model: "gpt-4"
) { chunk in
    print(chunk, terminator: "")
}
```

## Batch Processing

Process multiple requests efficiently:

```swift
let requests = [
    BatchTextRequest(prompt: "Explain AI", model: "claude-3-sonnet"),
    BatchTextRequest(prompt: "Explain ML", model: "gpt-4"),
    BatchTextRequest(prompt: "Explain DL", model: "claude-3-opus")
]

let batch = try await client.batchText(
    requests: requests,
    parallel: true
)

print("Successful: \(batch.successful)/\(batch.totalRequests)")
print("Total cost: $\(batch.totalCost)")

for result in batch.results {
    if result.success {
        print("✓ \(result.id)")
    } else {
        print("✗ \(result.id): \(result.error ?? "Unknown error")")
    }
}
```

## Fine-Tuning

Create and manage custom AI models:

```swift
// Create fine-tuning job
let job = try await client.createFineTuningJob(
    FineTuningJobCreate(
        trainingFileId: "file-abc123",
        model: "gpt-3.5-turbo",
        suffix: "my-custom-model"
    )
)

print("Job created: \(job.id)")
print("Status: \(job.status)")
print("Progress: \(job.progressPercentage)%")

// Check job status
let updated = try await client.getFineTuningJob(job.id)
if updated.status == "completed" {
    print("Fine-tuned model: \(updated.fineTunedModel ?? "N/A")")
}

// List all jobs
let jobs = try await client.listFineTuningJobs(limit: 20)
for job in jobs {
    print("\(job.id): \(job.status)")
}
```

## ML Predictions

Get AI-powered usage insights:

```swift
// Predict next month's cost
let prediction = try await client.predictCost()
print("Current month: $\(prediction.currentMonth)")
print("Predicted next month: $\(prediction.predictedNextMonth)")
print("Trend: \(prediction.trend)")
print("Confidence: \(prediction.confidence * 100)%")

// Detect anomalies
let anomalies = try await client.detectAnomalies(days: 30)
for anomaly in anomalies {
    print("Anomaly on \(anomaly.date):")
    print("  Actual: $\(anomaly.actualValue)")
    print("  Expected: $\(anomaly.expectedValue)")
    print("  Deviation: \(anomaly.deviationPercentage)%")
}

// Get usage insights
let insights = try await client.getUsageInsights()
for rec in insights.recommendations {
    print("[\(rec.priority)] \(rec.message)")
}
```

## WebSocket Real-Time Updates

Subscribe to real-time events:

```swift
let ws = client.createWebSocket()

ws.onConnect = {
    print("Connected!")
}

ws.onUsageUpdate = { update in
    print("Usage: \(update.endpoint) - $\(update.cost)")
}

ws.onBalanceUpdate = { update in
    print("Balance: $\(update.balance)")
}

ws.onAlert = { alert in
    print("[\(alert.severity)] \(alert.message)")
}

ws.onError = { error in
    print("Error: \(error)")
}

ws.connect()

// Later...
ws.disconnect()
```

## SwiftUI Example

```swift
import SwiftUI
import MoneyAPI

struct ContentView: View {
    @State private var prompt = ""
    @State private var response = ""
    @State private var isLoading = false

    let client = MoneyAPIClient(apiKey: "your-api-key")

    var body: some View {
        VStack {
            TextField("Enter prompt", text: $prompt)
                .textFieldStyle(.roundedBorder)
                .padding()

            Button("Generate") {
                Task {
                    isLoading = true
                    defer { isLoading = false }

                    do {
                        let completion = try await client.generateText(
                            prompt: prompt,
                            model: "claude-3-sonnet"
                        )
                        response = completion.text
                    } catch {
                        response = "Error: \(error.localizedDescription)"
                    }
                }
            }
            .disabled(isLoading)

            if isLoading {
                ProgressView()
            }

            ScrollView {
                Text(response)
                    .padding()
            }
        }
    }
}
```

## Error Handling

```swift
do {
    let completion = try await client.generateText(prompt: "Hello")
} catch MoneyAPIError.invalidAPIKey {
    print("Invalid API key - check your credentials")
} catch MoneyAPIError.rateLimitExceeded {
    print("Rate limit exceeded - please wait")
} catch MoneyAPIError.insufficientCredits {
    print("Insufficient credits - add funds to your account")
} catch let error as MoneyAPIError {
    print("API error: \(error.localizedDescription)")
} catch {
    print("Unexpected error: \(error)")
}
```

## Configuration

```swift
// Custom base URL
let client = MoneyAPIClient(
    apiKey: "your-api-key",
    baseURL: "https://api.custom-domain.com"
)

// Custom URLSession
let config = URLSessionConfiguration.default
config.timeoutIntervalForRequest = 60
let session = URLSession(configuration: config)

let client = MoneyAPIClient(
    apiKey: "your-api-key",
    session: session
)
```

## Documentation

Full API documentation: https://docs.money-api.com

## Support

- GitHub Issues: https://github.com/money-api/ios-sdk/issues
- Email: support@money-api.com
- Documentation: https://docs.money-api.com

## License

MIT License - see LICENSE file for details
