# Money API Android SDK

Official Kotlin SDK for Money API Service - AI API platform with cost tracking, usage analytics, and multi-provider support.

## Features

- 🚀 Modern Kotlin Coroutines API
- 📱 Android 5.0+ support (API 21+)
- 🔄 Flow-based streaming
- 📊 Usage analytics and cost tracking
- 🤖 AI model fine-tuning
- 📈 ML-based cost prediction
- ⚡ Batch processing
- 🔌 WebSocket real-time updates
- 💪 Type-safe with Kotlin Serialization

## Requirements

- Android 5.0+ (API level 21+)
- Kotlin 1.9.0+
- Gradle 8.0+

## Installation

### Gradle (Kotlin DSL)

Add to your `build.gradle.kts`:

```kotlin
dependencies {
    implementation("com.moneyapi:sdk:2.0.0")
}
```

### Gradle (Groovy)

Add to your `build.gradle`:

```groovy
dependencies {
    implementation 'com.moneyapi:sdk:2.0.0'
}
```

### Maven

```xml
<dependency>
    <groupId>com.moneyapi</groupId>
    <artifactId>sdk</artifactId>
    <version>2.0.0</version>
</dependency>
```

## Quick Start

```kotlin
import com.moneyapi.sdk.MoneyAPIClient
import kotlinx.coroutines.runBlocking

// Initialize client
val client = MoneyAPIClient(apiKey = "your-api-key")

// Generate text
runBlocking {
    val completion = client.generateText(
        prompt = "Explain quantum computing in simple terms",
        model = "claude-3-sonnet",
        maxTokens = 500
    )
    println(completion.text)
    println("Cost: $${completion.cost}")
}

// Generate image
runBlocking {
    val image = client.generateImage(
        prompt = "A serene mountain landscape at sunset",
        model = "sdxl",
        width = 1024,
        height = 1024
    )
    println("Image URL: ${image.url}")
}
```

## Streaming

Stream text generation using Kotlin Flow:

```kotlin
import kotlinx.coroutines.flow.collect

lifecycleScope.launch {
    client.streamText(
        prompt = "Write a short story about AI",
        model = "gpt-4"
    ).collect { chunk ->
        print(chunk)
    }
}
```

## Batch Processing

Process multiple requests efficiently:

```kotlin
val requests = listOf(
    BatchTextRequest(prompt = "Explain AI", model = "claude-3-sonnet"),
    BatchTextRequest(prompt = "Explain ML", model = "gpt-4"),
    BatchTextRequest(prompt = "Explain DL", model = "claude-3-opus")
)

val batch = client.batchText(
    requests = requests,
    parallel = true
)

println("Successful: ${batch.successful}/${batch.totalRequests}")
println("Total cost: $${batch.totalCost}")

batch.results.forEach { result ->
    if (result.success) {
        println("✓ ${result.id}")
    } else {
        println("✗ ${result.id}: ${result.error}")
    }
}
```

## Fine-Tuning

Create and manage custom AI models:

```kotlin
// Create fine-tuning job
val job = client.createFineTuningJob(
    FineTuningJobCreate(
        trainingFileId = "file-abc123",
        model = "gpt-3.5-turbo",
        suffix = "my-custom-model"
    )
)

println("Job created: ${job.id}")
println("Status: ${job.status}")
println("Progress: ${job.progressPercentage}%")

// Check job status
val updated = client.getFineTuningJob(job.id)
if (updated.status == "completed") {
    println("Fine-tuned model: ${updated.fineTunedModel}")
}

// List all jobs
val jobs = client.listFineTuningJobs(limit = 20)
jobs.forEach { job ->
    println("${job.id}: ${job.status}")
}
```

## ML Predictions

Get AI-powered usage insights:

```kotlin
// Predict next month's cost
val prediction = client.predictCost()
println("Current month: $${prediction.currentMonth}")
println("Predicted next month: $${prediction.predictedNextMonth}")
println("Trend: ${prediction.trend}")
println("Confidence: ${prediction.confidence * 100}%")

// Detect anomalies
val anomalies = client.detectAnomalies(days = 30)
anomalies.forEach { anomaly ->
    println("Anomaly on ${anomaly.date}:")
    println("  Actual: $${anomaly.actualValue}")
    println("  Expected: $${anomaly.expectedValue}")
    println("  Deviation: ${anomaly.deviationPercentage}%")
}

// Get usage insights
val insights = client.getUsageInsights()
insights.recommendations.forEach { rec ->
    println("[${rec.priority}] ${rec.message}")
}
```

## WebSocket Real-Time Updates

Subscribe to real-time events using Kotlin Flow:

```kotlin
val ws = client.createWebSocket()

lifecycleScope.launch {
    launch {
        ws.connectionState.collect { state ->
            when (state) {
                ConnectionState.CONNECTED -> println("Connected!")
                ConnectionState.DISCONNECTED -> println("Disconnected")
                ConnectionState.CONNECTING -> println("Connecting...")
                ConnectionState.ERROR -> println("Connection error")
            }
        }
    }

    launch {
        ws.usageUpdates.collect { update ->
            println("Usage: ${update.endpoint} - $${update.cost}")
        }
    }

    launch {
        ws.balanceUpdates.collect { update ->
            println("Balance: $${update.balance}")
        }
    }

    launch {
        ws.alerts.collect { alert ->
            println("[${alert.severity}] ${alert.message}")
        }
    }

    launch {
        ws.errors.collect { error ->
            println("Error: ${error.message}")
        }
    }
}

ws.connect()

// Later...
ws.disconnect()
ws.close()
```

## Jetpack Compose Example

```kotlin
import androidx.compose.runtime.*
import androidx.compose.material3.*
import androidx.compose.foundation.layout.*
import com.moneyapi.sdk.MoneyAPIClient

@Composable
fun AIGenerationScreen() {
    var prompt by remember { mutableStateOf("") }
    var response by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }

    val client = remember { MoneyAPIClient(apiKey = "your-api-key") }
    val scope = rememberCoroutineScope()

    Column(modifier = Modifier.padding(16.dp)) {
        OutlinedTextField(
            value = prompt,
            onValueChange = { prompt = it },
            label = { Text("Enter prompt") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = {
                scope.launch {
                    isLoading = true
                    try {
                        val completion = client.generateText(
                            prompt = prompt,
                            model = "claude-3-sonnet"
                        )
                        response = completion.text
                    } catch (e: Exception) {
                        response = "Error: ${e.message}"
                    } finally {
                        isLoading = false
                    }
                }
            },
            enabled = !isLoading
        ) {
            Text("Generate")
        }

        if (isLoading) {
            CircularProgressIndicator()
        }

        Text(
            text = response,
            modifier = Modifier.padding(top = 16.dp)
        )
    }
}
```

## Error Handling

```kotlin
try {
    val completion = client.generateText(prompt = "Hello")
} catch (e: MoneyAPIException.InvalidAPIKey) {
    println("Invalid API key - check your credentials")
} catch (e: MoneyAPIException.RateLimitExceeded) {
    println("Rate limit exceeded - please wait")
} catch (e: MoneyAPIException.InsufficientCredits) {
    println("Insufficient credits - add funds to your account")
} catch (e: MoneyAPIException.APIError) {
    println("API error (${e.code}): ${e.message}")
} catch (e: MoneyAPIException) {
    println("Error: ${e.message}")
}
```

## Configuration

```kotlin
// Custom base URL
val client = MoneyAPIClient(
    apiKey = "your-api-key",
    baseUrl = "https://api.custom-domain.com"
)

// Custom OkHttpClient
val customClient = OkHttpClient.Builder()
    .connectTimeout(60, TimeUnit.SECONDS)
    .readTimeout(120, TimeUnit.SECONDS)
    .addInterceptor(LoggingInterceptor())
    .build()

val client = MoneyAPIClient(
    apiKey = "your-api-key",
    client = customClient
)
```

## ProGuard Rules

If using ProGuard, add these rules:

```proguard
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.AnnotationsKt
-keepclassmembers class kotlinx.serialization.json.** {
    *** Companion;
}
-keepclasseswithmembers class kotlinx.serialization.json.** {
    kotlinx.serialization.KSerializer serializer(...);
}
-keep,includedescriptorclasses class com.moneyapi.sdk.**$$serializer { *; }
-keepclassmembers class com.moneyapi.sdk.** {
    *** Companion;
}
-keepclasseswithmembers class com.moneyapi.sdk.** {
    kotlinx.serialization.KSerializer serializer(...);
}
```

## Documentation

Full API documentation: https://docs.money-api.com

## Support

- GitHub Issues: https://github.com/money-api/android-sdk/issues
- Email: support@money-api.com
- Documentation: https://docs.money-api.com

## License

MIT License - see LICENSE file for details
