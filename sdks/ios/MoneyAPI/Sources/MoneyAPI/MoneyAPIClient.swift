import Foundation

/// Main client for Money API Service
@available(iOS 13.0, macOS 10.15, tvOS 13.0, watchOS 6.0, *)
public class MoneyAPIClient {

    // MARK: - Properties

    private let apiKey: String
    private let baseURL: URL
    private let session: URLSession

    /// API version
    public static let version = "2.0.0"

    // MARK: - Initialization

    /// Initialize Money API client
    /// - Parameters:
    ///   - apiKey: Your API key from Money API dashboard
    ///   - baseURL: Base URL (default: https://api.money-api.com)
    ///   - session: URLSession to use (default: .shared)
    public init(
        apiKey: String,
        baseURL: String = "https://api.money-api.com",
        session: URLSession = .shared
    ) {
        self.apiKey = apiKey
        self.baseURL = URL(string: baseURL)!
        self.session = session
    }

    // MARK: - Text Completion

    /// Generate text completion
    /// - Parameters:
    ///   - prompt: Text prompt
    ///   - model: Model name (default: claude-3-sonnet)
    ///   - maxTokens: Maximum tokens (default: 1000)
    ///   - stream: Enable streaming (default: false)
    /// - Returns: Completion response
    public func generateText(
        prompt: String,
        model: String = "claude-3-sonnet",
        maxTokens: Int = 1000,
        stream: Bool = false
    ) async throws -> TextCompletion {
        let request = TextCompletionRequest(
            prompt: prompt,
            model: model,
            maxTokens: maxTokens,
            stream: stream
        )

        return try await post(endpoint: "/v1/text/completions", body: request)
    }

    /// Generate text completion with streaming
    /// - Parameters:
    ///   - prompt: Text prompt
    ///   - model: Model name
    ///   - maxTokens: Maximum tokens
    ///   - onChunk: Callback for each chunk
    public func streamText(
        prompt: String,
        model: String = "claude-3-sonnet",
        maxTokens: Int = 1000,
        onChunk: @escaping (String) -> Void
    ) async throws {
        let request = TextCompletionRequest(
            prompt: prompt,
            model: model,
            maxTokens: maxTokens,
            stream: true
        )

        try await streamPost(
            endpoint: "/v1/text/completions",
            body: request,
            onChunk: onChunk
        )
    }

    // MARK: - Image Generation

    /// Generate image
    /// - Parameters:
    ///   - prompt: Image description
    ///   - model: Model name (default: sdxl)
    ///   - width: Image width (default: 1024)
    ///   - height: Image height (default: 1024)
    /// - Returns: Image generation response
    public func generateImage(
        prompt: String,
        model: String = "sdxl",
        width: Int = 1024,
        height: Int = 1024
    ) async throws -> ImageGeneration {
        let request = ImageGenerationRequest(
            prompt: prompt,
            model: model,
            width: width,
            height: height
        )

        return try await post(endpoint: "/v1/image/generate", body: request)
    }

    // MARK: - Batch Processing

    /// Process batch text requests
    /// - Parameters:
    ///   - requests: Array of text requests (max 100)
    ///   - parallel: Process in parallel (default: true)
    /// - Returns: Batch response with results
    public func batchText(
        requests: [BatchTextRequest],
        parallel: Bool = true
    ) async throws -> BatchResponse {
        let body = BatchTextRequestList(requests: requests, parallel: parallel)
        return try await post(endpoint: "/v1/batch/text", body: body)
    }

    /// Process batch image requests
    /// - Parameters:
    ///   - requests: Array of image requests (max 50)
    ///   - parallel: Process in parallel (default: true)
    /// - Returns: Batch response with results
    public func batchImage(
        requests: [BatchImageRequest],
        parallel: Bool = true
    ) async throws -> BatchResponse {
        let body = BatchImageRequestList(requests: requests, parallel: parallel)
        return try await post(endpoint: "/v1/batch/image", body: body)
    }

    // MARK: - Fine-Tuning

    /// Create fine-tuning job
    /// - Parameter request: Job creation request
    /// - Returns: Created job
    public func createFineTuningJob(
        _ request: FineTuningJobCreate
    ) async throws -> FineTuningJob {
        return try await post(endpoint: "/v1/fine-tuning/jobs", body: request)
    }

    /// List fine-tuning jobs
    /// - Parameter limit: Maximum number of jobs (default: 20)
    /// - Returns: Array of jobs
    public func listFineTuningJobs(limit: Int = 20) async throws -> [FineTuningJob] {
        return try await get(endpoint: "/v1/fine-tuning/jobs?limit=\(limit)")
    }

    /// Get fine-tuning job status
    /// - Parameter jobId: Job ID
    /// - Returns: Job details
    public func getFineTuningJob(_ jobId: String) async throws -> FineTuningJob {
        return try await get(endpoint: "/v1/fine-tuning/jobs/\(jobId)")
    }

    /// Cancel fine-tuning job
    /// - Parameter jobId: Job ID
    public func cancelFineTuningJob(_ jobId: String) async throws {
        let _: EmptyResponse = try await delete(endpoint: "/v1/fine-tuning/jobs/\(jobId)")
    }

    // MARK: - ML Predictions

    /// Predict monthly cost
    /// - Returns: Cost prediction with forecasts
    public func predictCost() async throws -> CostPrediction {
        return try await get(endpoint: "/v1/ml/predict/cost")
    }

    /// Detect usage anomalies
    /// - Parameter days: Number of days to analyze (default: 30)
    /// - Returns: Array of detected anomalies
    public func detectAnomalies(days: Int = 30) async throws -> [AnomalyDetection] {
        return try await get(endpoint: "/v1/ml/anomalies/detect?days=\(days)")
    }

    /// Get usage insights
    /// - Returns: AI-powered usage insights and recommendations
    public func getUsageInsights() async throws -> UsageInsights {
        return try await get(endpoint: "/v1/ml/insights/usage")
    }

    // MARK: - Analytics

    /// Get usage analytics
    /// - Parameters:
    ///   - startDate: Start date
    ///   - endDate: End date
    ///   - groupBy: Group by (hour, day, month)
    /// - Returns: Analytics data
    public func getAnalytics(
        startDate: Date,
        endDate: Date,
        groupBy: String = "day"
    ) async throws -> Analytics {
        let formatter = ISO8601DateFormatter()
        let start = formatter.string(from: startDate)
        let end = formatter.string(from: endDate)

        return try await get(
            endpoint: "/v1/analytics/usage?start_date=\(start)&end_date=\(end)&group_by=\(groupBy)"
        )
    }

    // MARK: - Account Management

    /// Get current balance
    /// - Returns: Account balance
    public func getBalance() async throws -> Balance {
        return try await get(endpoint: "/v1/account/balance")
    }

    /// Get usage summary
    /// - Returns: Usage summary
    public func getUsage() async throws -> UsageSummary {
        return try await get(endpoint: "/v1/account/usage")
    }

    // MARK: - WebSocket Connection

    /// Create WebSocket connection for real-time updates
    /// - Returns: WebSocket manager
    public func createWebSocket() -> MoneyAPIWebSocket {
        return MoneyAPIWebSocket(apiKey: apiKey, baseURL: baseURL)
    }

    // MARK: - Private Methods

    private func get<T: Decodable>(endpoint: String) async throws -> T {
        var request = URLRequest(url: baseURL.appendingPathComponent(endpoint))
        request.httpMethod = "GET"
        request.addValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")

        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw MoneyAPIError.invalidResponse
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            throw try parseError(from: data, statusCode: httpResponse.statusCode)
        }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode(T.self, from: data)
    }

    private func post<T: Encodable, U: Decodable>(
        endpoint: String,
        body: T
    ) async throws -> U {
        var request = URLRequest(url: baseURL.appendingPathComponent(endpoint))
        request.httpMethod = "POST"
        request.addValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")

        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        request.httpBody = try encoder.encode(body)

        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw MoneyAPIError.invalidResponse
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            throw try parseError(from: data, statusCode: httpResponse.statusCode)
        }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode(U.self, from: data)
    }

    private func delete<T: Decodable>(endpoint: String) async throws -> T {
        var request = URLRequest(url: baseURL.appendingPathComponent(endpoint))
        request.httpMethod = "DELETE"
        request.addValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")

        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw MoneyAPIError.invalidResponse
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            throw try parseError(from: data, statusCode: httpResponse.statusCode)
        }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode(T.self, from: data)
    }

    private func streamPost<T: Encodable>(
        endpoint: String,
        body: T,
        onChunk: @escaping (String) -> Void
    ) async throws {
        var request = URLRequest(url: baseURL.appendingPathComponent(endpoint))
        request.httpMethod = "POST"
        request.addValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")

        let encoder = JSONEncoder()
        request.httpBody = try encoder.encode(body)

        let (asyncBytes, response) = try await session.bytes(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw MoneyAPIError.invalidResponse
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            throw MoneyAPIError.httpError(statusCode: httpResponse.statusCode)
        }

        for try await line in asyncBytes.lines {
            if line.hasPrefix("data: ") {
                let chunk = String(line.dropFirst(6))
                if chunk != "[DONE]" {
                    onChunk(chunk)
                }
            }
        }
    }

    private func parseError(from data: Data, statusCode: Int) throws -> MoneyAPIError {
        if let errorResponse = try? JSONDecoder().decode(ErrorResponse.self, from: data) {
            return MoneyAPIError.apiError(
                code: errorResponse.error.code,
                message: errorResponse.error.message,
                statusCode: statusCode
            )
        }
        return MoneyAPIError.httpError(statusCode: statusCode)
    }
}

// MARK: - Error Response

private struct ErrorResponse: Decodable {
    let error: ErrorDetail

    struct ErrorDetail: Decodable {
        let code: String
        let message: String
    }
}

private struct EmptyResponse: Decodable {}
