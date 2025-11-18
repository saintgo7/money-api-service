package com.moneyapi.sdk

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// MARK: - Text Completion

@Serializable
data class TextCompletionRequest(
    val prompt: String,
    val model: String,
    @SerialName("max_tokens") val maxTokens: Int,
    val stream: Boolean = false
)

@Serializable
data class TextCompletion(
    val id: String,
    val text: String,
    val model: String,
    val usage: Usage,
    val cost: Double,
    val latency: Double
) {
    @Serializable
    data class Usage(
        @SerialName("prompt_tokens") val promptTokens: Int,
        @SerialName("completion_tokens") val completionTokens: Int,
        @SerialName("total_tokens") val totalTokens: Int
    )
}

// MARK: - Image Generation

@Serializable
data class ImageGenerationRequest(
    val prompt: String,
    val model: String,
    val width: Int,
    val height: Int
)

@Serializable
data class ImageGeneration(
    val id: String,
    val url: String,
    val model: String,
    val cost: Double,
    val width: Int,
    val height: Int
)

// MARK: - Batch Processing

@Serializable
data class BatchTextRequest(
    val id: String? = null,
    val prompt: String,
    val model: String = "claude-3-sonnet",
    @SerialName("max_tokens") val maxTokens: Int = 1000
)

@Serializable
data class BatchImageRequest(
    val id: String? = null,
    val prompt: String,
    val model: String = "sdxl",
    val width: Int = 1024,
    val height: Int = 1024
)

@Serializable
data class BatchTextRequestList(
    val requests: List<BatchTextRequest>,
    val parallel: Boolean = true
)

@Serializable
data class BatchImageRequestList(
    val requests: List<BatchImageRequest>,
    val parallel: Boolean = true
)

@Serializable
data class BatchResponse(
    @SerialName("batch_id") val batchId: String,
    @SerialName("total_requests") val totalRequests: Int,
    val successful: Int,
    val failed: Int,
    @SerialName("total_cost") val totalCost: Double,
    @SerialName("total_time") val totalTime: Double,
    val results: List<BatchResult>
) {
    @Serializable
    data class BatchResult(
        val id: String,
        val success: Boolean,
        val result: Map<String, String>? = null,
        val error: String? = null,
        @SerialName("processing_time") val processingTime: Double? = null
    )
}

// MARK: - Fine-Tuning

@Serializable
data class FineTuningJobCreate(
    @SerialName("training_file_id") val trainingFileId: String,
    @SerialName("validation_file_id") val validationFileId: String? = null,
    val model: String = "gpt-3.5-turbo",
    val hyperparameters: Map<String, String>? = null,
    val suffix: String? = null
)

@Serializable
data class FineTuningJob(
    val id: String,
    @SerialName("user_id") val userId: String,
    val status: String,
    val model: String,
    @SerialName("training_file_id") val trainingFileId: String,
    @SerialName("validation_file_id") val validationFileId: String? = null,
    @SerialName("fine_tuned_model") val fineTunedModel: String? = null,
    @SerialName("trained_tokens") val trainedTokens: Int,
    @SerialName("total_tokens") val totalTokens: Int? = null,
    @SerialName("progress_percentage") val progressPercentage: Double,
    @SerialName("training_loss") val trainingLoss: Double? = null,
    @SerialName("validation_loss") val validationLoss: Double? = null,
    @SerialName("estimated_cost") val estimatedCost: Double,
    @SerialName("actual_cost") val actualCost: Double? = null,
    @SerialName("created_at") val createdAt: String,
    @SerialName("started_at") val startedAt: String? = null,
    @SerialName("completed_at") val completedAt: String? = null,
    val error: String? = null
)

// MARK: - ML Predictions

@Serializable
data class CostPrediction(
    @SerialName("current_month") val currentMonth: Double,
    @SerialName("predicted_next_month") val predictedNextMonth: Double,
    @SerialName("predicted_daily_average") val predictedDailyAverage: Double,
    val trend: String,
    val confidence: Double,
    val forecasts: List<UsageForecast>
) {
    @Serializable
    data class UsageForecast(
        val date: String,
        @SerialName("predicted_requests") val predictedRequests: Double,
        @SerialName("predicted_cost") val predictedCost: Double,
        @SerialName("confidence_lower") val confidenceLower: Double,
        @SerialName("confidence_upper") val confidenceUpper: Double,
        @SerialName("confidence_interval") val confidenceInterval: Double
    )
}

@Serializable
data class AnomalyDetection(
    @SerialName("is_anomaly") val isAnomaly: Boolean,
    @SerialName("anomaly_score") val anomalyScore: Double,
    val threshold: Double,
    val date: String,
    @SerialName("actual_value") val actualValue: Double,
    @SerialName("expected_value") val expectedValue: Double,
    @SerialName("deviation_percentage") val deviationPercentage: Double
)

@Serializable
data class UsageInsights(
    val summary: Summary,
    val recommendations: List<Recommendation>,
    @SerialName("cost_breakdown") val costBreakdown: List<CostBreakdown>
) {
    @Serializable
    data class Summary(
        @SerialName("total_endpoints") val totalEndpoints: Int,
        @SerialName("analysis_period") val analysisPeriod: String
    )

    @Serializable
    data class Recommendation(
        val type: String,
        val priority: String,
        val message: String
    )

    @Serializable
    data class CostBreakdown(
        val endpoint: String,
        val requests: Int,
        val cost: Double,
        val percentage: Double,
        @SerialName("avg_latency") val avgLatency: Double
    )
}

// MARK: - Analytics

@Serializable
data class Analytics(
    val data: List<DataPoint>,
    val summary: Summary
) {
    @Serializable
    data class DataPoint(
        val timestamp: String,
        val requests: Int,
        val cost: Double,
        val latency: Double
    )

    @Serializable
    data class Summary(
        @SerialName("total_requests") val totalRequests: Int,
        @SerialName("total_cost") val totalCost: Double,
        @SerialName("average_latency") val averageLatency: Double
    )
}

// MARK: - Account

@Serializable
data class Balance(
    val balance: Double,
    val currency: String
)

@Serializable
data class UsageSummary(
    @SerialName("total_requests") val totalRequests: Int,
    @SerialName("total_cost") val totalCost: Double,
    val period: String
)

// MARK: - WebSocket Messages

@Serializable
data class UsageUpdate(
    val type: String,
    val endpoint: String,
    val cost: Double,
    val timestamp: String
)

@Serializable
data class BalanceUpdate(
    val type: String,
    val balance: Double,
    val timestamp: String
)

@Serializable
data class Alert(
    val type: String,
    val severity: String,
    val message: String,
    val timestamp: String
)

// MARK: - Error Response

@Serializable
internal data class ErrorResponse(
    val error: ErrorDetail
) {
    @Serializable
    data class ErrorDetail(
        val code: String,
        val message: String
    )
}
