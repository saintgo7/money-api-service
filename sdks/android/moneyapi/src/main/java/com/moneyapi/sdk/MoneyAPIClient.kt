package com.moneyapi.sdk

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.withContext
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import java.io.IOException
import java.util.concurrent.TimeUnit

/**
 * Main client for Money API Service
 *
 * @property apiKey Your API key from Money API dashboard
 * @property baseUrl Base URL (default: https://api.money-api.com)
 */
class MoneyAPIClient(
    private val apiKey: String,
    private val baseUrl: String = "https://api.money-api.com",
    private val client: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(60, TimeUnit.SECONDS)
        .build()
) {
    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
    }

    companion object {
        const val VERSION = "2.0.0"
    }

    // MARK: - Text Completion

    /**
     * Generate text completion
     *
     * @param prompt Text prompt
     * @param model Model name (default: claude-3-sonnet)
     * @param maxTokens Maximum tokens (default: 1000)
     * @param stream Enable streaming (default: false)
     * @return Completion response
     */
    suspend fun generateText(
        prompt: String,
        model: String = "claude-3-sonnet",
        maxTokens: Int = 1000,
        stream: Boolean = false
    ): TextCompletion = withContext(Dispatchers.IO) {
        val request = TextCompletionRequest(
            prompt = prompt,
            model = model,
            maxTokens = maxTokens,
            stream = stream
        )
        post("/v1/text/completions", request)
    }

    /**
     * Generate text completion with streaming
     *
     * @param prompt Text prompt
     * @param model Model name
     * @param maxTokens Maximum tokens
     * @return Flow of text chunks
     */
    fun streamText(
        prompt: String,
        model: String = "claude-3-sonnet",
        maxTokens: Int = 1000
    ): Flow<String> = flow {
        val request = TextCompletionRequest(
            prompt = prompt,
            model = model,
            maxTokens = maxTokens,
            stream = true
        )

        val httpRequest = buildRequest("/v1/text/completions", request)
        val response = client.newCall(httpRequest).execute()

        if (!response.isSuccessful) {
            throw parseError(response)
        }

        response.body?.byteStream()?.bufferedReader()?.use { reader ->
            reader.lineSequence().forEach { line ->
                if (line.startsWith("data: ")) {
                    val chunk = line.substring(6)
                    if (chunk != "[DONE]") {
                        emit(chunk)
                    }
                }
            }
        }
    }.flowOn(Dispatchers.IO)

    // MARK: - Image Generation

    /**
     * Generate image
     *
     * @param prompt Image description
     * @param model Model name (default: sdxl)
     * @param width Image width (default: 1024)
     * @param height Image height (default: 1024)
     * @return Image generation response
     */
    suspend fun generateImage(
        prompt: String,
        model: String = "sdxl",
        width: Int = 1024,
        height: Int = 1024
    ): ImageGeneration = withContext(Dispatchers.IO) {
        val request = ImageGenerationRequest(
            prompt = prompt,
            model = model,
            width = width,
            height = height
        )
        post("/v1/image/generate", request)
    }

    // MARK: - Batch Processing

    /**
     * Process batch text requests
     *
     * @param requests Array of text requests (max 100)
     * @param parallel Process in parallel (default: true)
     * @return Batch response with results
     */
    suspend fun batchText(
        requests: List<BatchTextRequest>,
        parallel: Boolean = true
    ): BatchResponse = withContext(Dispatchers.IO) {
        val body = BatchTextRequestList(requests, parallel)
        post("/v1/batch/text", body)
    }

    /**
     * Process batch image requests
     *
     * @param requests Array of image requests (max 50)
     * @param parallel Process in parallel (default: true)
     * @return Batch response with results
     */
    suspend fun batchImage(
        requests: List<BatchImageRequest>,
        parallel: Boolean = true
    ): BatchResponse = withContext(Dispatchers.IO) {
        val body = BatchImageRequestList(requests, parallel)
        post("/v1/batch/image", body)
    }

    // MARK: - Fine-Tuning

    /**
     * Create fine-tuning job
     *
     * @param request Job creation request
     * @return Created job
     */
    suspend fun createFineTuningJob(
        request: FineTuningJobCreate
    ): FineTuningJob = withContext(Dispatchers.IO) {
        post("/v1/fine-tuning/jobs", request)
    }

    /**
     * List fine-tuning jobs
     *
     * @param limit Maximum number of jobs (default: 20)
     * @return List of jobs
     */
    suspend fun listFineTuningJobs(
        limit: Int = 20
    ): List<FineTuningJob> = withContext(Dispatchers.IO) {
        get("/v1/fine-tuning/jobs?limit=$limit")
    }

    /**
     * Get fine-tuning job status
     *
     * @param jobId Job ID
     * @return Job details
     */
    suspend fun getFineTuningJob(
        jobId: String
    ): FineTuningJob = withContext(Dispatchers.IO) {
        get("/v1/fine-tuning/jobs/$jobId")
    }

    /**
     * Cancel fine-tuning job
     *
     * @param jobId Job ID
     */
    suspend fun cancelFineTuningJob(
        jobId: String
    ): Unit = withContext(Dispatchers.IO) {
        delete<Map<String, Any>>("/v1/fine-tuning/jobs/$jobId")
        Unit
    }

    // MARK: - ML Predictions

    /**
     * Predict monthly cost
     *
     * @return Cost prediction with forecasts
     */
    suspend fun predictCost(): CostPrediction = withContext(Dispatchers.IO) {
        get("/v1/ml/predict/cost")
    }

    /**
     * Detect usage anomalies
     *
     * @param days Number of days to analyze (default: 30)
     * @return List of detected anomalies
     */
    suspend fun detectAnomalies(
        days: Int = 30
    ): List<AnomalyDetection> = withContext(Dispatchers.IO) {
        get("/v1/ml/anomalies/detect?days=$days")
    }

    /**
     * Get usage insights
     *
     * @return AI-powered usage insights and recommendations
     */
    suspend fun getUsageInsights(): UsageInsights = withContext(Dispatchers.IO) {
        get("/v1/ml/insights/usage")
    }

    // MARK: - Analytics

    /**
     * Get usage analytics
     *
     * @param startDate Start date (ISO 8601)
     * @param endDate End date (ISO 8601)
     * @param groupBy Group by (hour, day, month)
     * @return Analytics data
     */
    suspend fun getAnalytics(
        startDate: String,
        endDate: String,
        groupBy: String = "day"
    ): Analytics = withContext(Dispatchers.IO) {
        get("/v1/analytics/usage?start_date=$startDate&end_date=$endDate&group_by=$groupBy")
    }

    // MARK: - Account Management

    /**
     * Get current balance
     *
     * @return Account balance
     */
    suspend fun getBalance(): Balance = withContext(Dispatchers.IO) {
        get("/v1/account/balance")
    }

    /**
     * Get usage summary
     *
     * @return Usage summary
     */
    suspend fun getUsage(): UsageSummary = withContext(Dispatchers.IO) {
        get("/v1/account/usage")
    }

    // MARK: - WebSocket Connection

    /**
     * Create WebSocket connection for real-time updates
     *
     * @return WebSocket manager
     */
    fun createWebSocket(): MoneyAPIWebSocket {
        return MoneyAPIWebSocket(apiKey, baseUrl, client)
    }

    // MARK: - Private Methods

    private inline fun <reified T> get(endpoint: String): T {
        val request = Request.Builder()
            .url("$baseUrl$endpoint")
            .header("Authorization", "Bearer $apiKey")
            .header("Content-Type", "application/json")
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw parseError(response)
            }

            val body = response.body?.string() ?: throw MoneyAPIException.InvalidResponse()
            return json.decodeFromString(body)
        }
    }

    private inline fun <reified T, reified U> post(endpoint: String, body: T): U {
        val httpRequest = buildRequest(endpoint, body)

        client.newCall(httpRequest).execute().use { response ->
            if (!response.isSuccessful) {
                throw parseError(response)
            }

            val responseBody = response.body?.string()
                ?: throw MoneyAPIException.InvalidResponse()
            return json.decodeFromString(responseBody)
        }
    }

    private inline fun <reified T> delete(endpoint: String): T {
        val request = Request.Builder()
            .url("$baseUrl$endpoint")
            .delete()
            .header("Authorization", "Bearer $apiKey")
            .header("Content-Type", "application/json")
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw parseError(response)
            }

            val body = response.body?.string() ?: throw MoneyAPIException.InvalidResponse()
            return json.decodeFromString(body)
        }
    }

    private inline fun <reified T> buildRequest(endpoint: String, body: T): Request {
        val jsonBody = json.encodeToString(body)
        val requestBody = jsonBody.toRequestBody("application/json".toMediaType())

        return Request.Builder()
            .url("$baseUrl$endpoint")
            .post(requestBody)
            .header("Authorization", "Bearer $apiKey")
            .header("Content-Type", "application/json")
            .build()
    }

    private fun parseError(response: Response): MoneyAPIException {
        val statusCode = response.code
        val body = response.body?.string()

        if (body != null) {
            try {
                val errorResponse = json.decodeFromString<ErrorResponse>(body)
                return MoneyAPIException.APIError(
                    code = errorResponse.error.code,
                    message = errorResponse.error.message,
                    statusCode = statusCode
                )
            } catch (e: Exception) {
                // Failed to parse error response
            }
        }

        return MoneyAPIException.HTTPError(statusCode)
    }
}
