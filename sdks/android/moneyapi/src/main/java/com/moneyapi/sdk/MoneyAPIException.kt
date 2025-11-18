package com.moneyapi.sdk

/**
 * Exceptions that can occur when using Money API
 */
sealed class MoneyAPIException(message: String, cause: Throwable? = null) :
    Exception(message, cause) {

    /**
     * Invalid API response
     */
    class InvalidResponse : MoneyAPIException("Invalid response from server")

    /**
     * HTTP error with status code
     */
    class HTTPError(val statusCode: Int) : MoneyAPIException("HTTP error: $statusCode")

    /**
     * API error with code and message
     */
    class APIError(
        val code: String,
        message: String,
        val statusCode: Int
    ) : MoneyAPIException("API error ($code, $statusCode): $message")

    /**
     * Network error
     */
    class NetworkError(cause: Throwable) :
        MoneyAPIException("Network error: ${cause.message}", cause)

    /**
     * Decoding error
     */
    class DecodingError(cause: Throwable) :
        MoneyAPIException("Failed to decode response: ${cause.message}", cause)

    /**
     * Invalid API key
     */
    class InvalidAPIKey : MoneyAPIException("Invalid API key")

    /**
     * Rate limit exceeded
     */
    class RateLimitExceeded : MoneyAPIException("Rate limit exceeded")

    /**
     * Insufficient credits
     */
    class InsufficientCredits : MoneyAPIException("Insufficient credits")

    /**
     * WebSocket error
     */
    class WebSocketError(message: String) : MoneyAPIException("WebSocket error: $message")
}
