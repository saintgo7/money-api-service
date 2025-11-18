import Foundation

/// Errors that can occur when using Money API
public enum MoneyAPIError: Error, LocalizedError {
    /// Invalid API response
    case invalidResponse

    /// HTTP error with status code
    case httpError(statusCode: Int)

    /// API error with code and message
    case apiError(code: String, message: String, statusCode: Int)

    /// Network error
    case networkError(Error)

    /// Decoding error
    case decodingError(Error)

    /// Invalid API key
    case invalidAPIKey

    /// Rate limit exceeded
    case rateLimitExceeded

    /// Insufficient credits
    case insufficientCredits

    public var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "Invalid response from server"
        case .httpError(let statusCode):
            return "HTTP error: \(statusCode)"
        case .apiError(let code, let message, let statusCode):
            return "API error (\(code), \(statusCode)): \(message)"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        case .decodingError(let error):
            return "Failed to decode response: \(error.localizedDescription)"
        case .invalidAPIKey:
            return "Invalid API key"
        case .rateLimitExceeded:
            return "Rate limit exceeded"
        case .insufficientCredits:
            return "Insufficient credits"
        }
    }

    public var recoverySuggestion: String? {
        switch self {
        case .invalidAPIKey:
            return "Please check your API key in the Money API dashboard"
        case .rateLimitExceeded:
            return "Please wait before making more requests"
        case .insufficientCredits:
            return "Please add credits to your account"
        case .httpError(let statusCode) where statusCode >= 500:
            return "Server error, please try again later"
        default:
            return nil
        }
    }
}
