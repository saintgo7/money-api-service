import Foundation

// MARK: - Text Completion

public struct TextCompletionRequest: Encodable {
    public let prompt: String
    public let model: String
    public let maxTokens: Int
    public let stream: Bool

    enum CodingKeys: String, CodingKey {
        case prompt
        case model
        case maxTokens = "max_tokens"
        case stream
    }

    public init(prompt: String, model: String, maxTokens: Int, stream: Bool) {
        self.prompt = prompt
        self.model = model
        self.maxTokens = maxTokens
        self.stream = stream
    }
}

public struct TextCompletion: Decodable {
    public let id: String
    public let text: String
    public let model: String
    public let usage: Usage
    public let cost: Double
    public let latency: Double

    public struct Usage: Decodable {
        public let promptTokens: Int
        public let completionTokens: Int
        public let totalTokens: Int

        enum CodingKeys: String, CodingKey {
            case promptTokens = "prompt_tokens"
            case completionTokens = "completion_tokens"
            case totalTokens = "total_tokens"
        }
    }
}

// MARK: - Image Generation

public struct ImageGenerationRequest: Encodable {
    public let prompt: String
    public let model: String
    public let width: Int
    public let height: Int

    public init(prompt: String, model: String, width: Int, height: Int) {
        self.prompt = prompt
        self.model = model
        self.width = width
        self.height = height
    }
}

public struct ImageGeneration: Decodable {
    public let id: String
    public let url: String
    public let model: String
    public let cost: Double
    public let width: Int
    public let height: Int
}

// MARK: - Batch Processing

public struct BatchTextRequest: Encodable {
    public let id: String?
    public let prompt: String
    public let model: String
    public let maxTokens: Int

    enum CodingKeys: String, CodingKey {
        case id
        case prompt
        case model
        case maxTokens = "max_tokens"
    }

    public init(id: String? = nil, prompt: String, model: String = "claude-3-sonnet", maxTokens: Int = 1000) {
        self.id = id
        self.prompt = prompt
        self.model = model
        self.maxTokens = maxTokens
    }
}

public struct BatchImageRequest: Encodable {
    public let id: String?
    public let prompt: String
    public let model: String
    public let width: Int
    public let height: Int

    public init(id: String? = nil, prompt: String, model: String = "sdxl", width: Int = 1024, height: Int = 1024) {
        self.id = id
        self.prompt = prompt
        self.model = model
        self.width = width
        self.height = height
    }
}

struct BatchTextRequestList: Encodable {
    let requests: [BatchTextRequest]
    let parallel: Bool
}

struct BatchImageRequestList: Encodable {
    let requests: [BatchImageRequest]
    let parallel: Bool
}

public struct BatchResponse: Decodable {
    public let batchId: String
    public let totalRequests: Int
    public let successful: Int
    public let failed: Int
    public let totalCost: Double
    public let totalTime: Double
    public let results: [BatchResult]

    enum CodingKeys: String, CodingKey {
        case batchId = "batch_id"
        case totalRequests = "total_requests"
        case successful
        case failed
        case totalCost = "total_cost"
        case totalTime = "total_time"
        case results
    }

    public struct BatchResult: Decodable {
        public let id: String
        public let success: Bool
        public let result: [String: AnyCodable]?
        public let error: String?
        public let processingTime: Double?

        enum CodingKeys: String, CodingKey {
            case id
            case success
            case result
            case error
            case processingTime = "processing_time"
        }
    }
}

// MARK: - Fine-Tuning

public struct FineTuningJobCreate: Encodable {
    public let trainingFileId: String
    public let validationFileId: String?
    public let model: String
    public let hyperparameters: [String: AnyCodable]?
    public let suffix: String?

    enum CodingKeys: String, CodingKey {
        case trainingFileId = "training_file_id"
        case validationFileId = "validation_file_id"
        case model
        case hyperparameters
        case suffix
    }

    public init(
        trainingFileId: String,
        validationFileId: String? = nil,
        model: String = "gpt-3.5-turbo",
        hyperparameters: [String: AnyCodable]? = nil,
        suffix: String? = nil
    ) {
        self.trainingFileId = trainingFileId
        self.validationFileId = validationFileId
        self.model = model
        self.hyperparameters = hyperparameters
        self.suffix = suffix
    }
}

public struct FineTuningJob: Decodable {
    public let id: String
    public let userId: String
    public let status: String
    public let model: String
    public let trainingFileId: String
    public let validationFileId: String?
    public let fineTunedModel: String?
    public let trainedTokens: Int
    public let totalTokens: Int?
    public let progressPercentage: Double
    public let trainingLoss: Double?
    public let validationLoss: Double?
    public let estimatedCost: Double
    public let actualCost: Double?
    public let createdAt: Date
    public let startedAt: Date?
    public let completedAt: Date?
    public let error: String?

    enum CodingKeys: String, CodingKey {
        case id
        case userId = "user_id"
        case status
        case model
        case trainingFileId = "training_file_id"
        case validationFileId = "validation_file_id"
        case fineTunedModel = "fine_tuned_model"
        case trainedTokens = "trained_tokens"
        case totalTokens = "total_tokens"
        case progressPercentage = "progress_percentage"
        case trainingLoss = "training_loss"
        case validationLoss = "validation_loss"
        case estimatedCost = "estimated_cost"
        case actualCost = "actual_cost"
        case createdAt = "created_at"
        case startedAt = "started_at"
        case completedAt = "completed_at"
        case error
    }
}

// MARK: - ML Predictions

public struct CostPrediction: Decodable {
    public let currentMonth: Double
    public let predictedNextMonth: Double
    public let predictedDailyAverage: Double
    public let trend: String
    public let confidence: Double
    public let forecasts: [UsageForecast]

    enum CodingKeys: String, CodingKey {
        case currentMonth = "current_month"
        case predictedNextMonth = "predicted_next_month"
        case predictedDailyAverage = "predicted_daily_average"
        case trend
        case confidence
        case forecasts
    }

    public struct UsageForecast: Decodable {
        public let date: Date
        public let predictedRequests: Double
        public let predictedCost: Double
        public let confidenceLower: Double
        public let confidenceUpper: Double
        public let confidenceInterval: Double

        enum CodingKeys: String, CodingKey {
            case date
            case predictedRequests = "predicted_requests"
            case predictedCost = "predicted_cost"
            case confidenceLower = "confidence_lower"
            case confidenceUpper = "confidence_upper"
            case confidenceInterval = "confidence_interval"
        }
    }
}

public struct AnomalyDetection: Decodable {
    public let isAnomaly: Bool
    public let anomalyScore: Double
    public let threshold: Double
    public let date: Date
    public let actualValue: Double
    public let expectedValue: Double
    public let deviationPercentage: Double

    enum CodingKeys: String, CodingKey {
        case isAnomaly = "is_anomaly"
        case anomalyScore = "anomaly_score"
        case threshold
        case date
        case actualValue = "actual_value"
        case expectedValue = "expected_value"
        case deviationPercentage = "deviation_percentage"
    }
}

public struct UsageInsights: Decodable {
    public let summary: Summary
    public let recommendations: [Recommendation]
    public let costBreakdown: [CostBreakdown]

    enum CodingKeys: String, CodingKey {
        case summary
        case recommendations
        case costBreakdown = "cost_breakdown"
    }

    public struct Summary: Decodable {
        public let totalEndpoints: Int
        public let analysisPeriod: String

        enum CodingKeys: String, CodingKey {
            case totalEndpoints = "total_endpoints"
            case analysisPeriod = "analysis_period"
        }
    }

    public struct Recommendation: Decodable {
        public let type: String
        public let priority: String
        public let message: String
    }

    public struct CostBreakdown: Decodable {
        public let endpoint: String
        public let requests: Int
        public let cost: Double
        public let percentage: Double
        public let avgLatency: Double

        enum CodingKeys: String, CodingKey {
            case endpoint
            case requests
            case cost
            case percentage
            case avgLatency = "avg_latency"
        }
    }
}

// MARK: - Analytics

public struct Analytics: Decodable {
    public let data: [DataPoint]
    public let summary: Summary

    public struct DataPoint: Decodable {
        public let timestamp: Date
        public let requests: Int
        public let cost: Double
        public let latency: Double
    }

    public struct Summary: Decodable {
        public let totalRequests: Int
        public let totalCost: Double
        public let averageLatency: Double

        enum CodingKeys: String, CodingKey {
            case totalRequests = "total_requests"
            case totalCost = "total_cost"
            case averageLatency = "average_latency"
        }
    }
}

// MARK: - Account

public struct Balance: Decodable {
    public let balance: Double
    public let currency: String
}

public struct UsageSummary: Decodable {
    public let totalRequests: Int
    public let totalCost: Double
    public let period: String

    enum CodingKeys: String, CodingKey {
        case totalRequests = "total_requests"
        case totalCost = "total_cost"
        case period
    }
}

// MARK: - Helper Types

public struct AnyCodable: Codable {
    public let value: Any

    public init(_ value: Any) {
        self.value = value
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()

        if let bool = try? container.decode(Bool.self) {
            value = bool
        } else if let int = try? container.decode(Int.self) {
            value = int
        } else if let double = try? container.decode(Double.self) {
            value = double
        } else if let string = try? container.decode(String.self) {
            value = string
        } else if let array = try? container.decode([AnyCodable].self) {
            value = array.map { $0.value }
        } else if let dict = try? container.decode([String: AnyCodable].self) {
            value = dict.mapValues { $0.value }
        } else {
            value = NSNull()
        }
    }

    public func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()

        switch value {
        case let bool as Bool:
            try container.encode(bool)
        case let int as Int:
            try container.encode(int)
        case let double as Double:
            try container.encode(double)
        case let string as String:
            try container.encode(string)
        case let array as [Any]:
            try container.encode(array.map { AnyCodable($0) })
        case let dict as [String: Any]:
            try container.encode(dict.mapValues { AnyCodable($0) })
        default:
            try container.encodeNil()
        }
    }
}
