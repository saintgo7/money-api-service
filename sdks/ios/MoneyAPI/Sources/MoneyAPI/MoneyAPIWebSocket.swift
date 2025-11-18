import Foundation

/// WebSocket manager for real-time Money API updates
@available(iOS 13.0, macOS 10.15, tvOS 13.0, watchOS 6.0, *)
public class MoneyAPIWebSocket: NSObject {

    // MARK: - Properties

    private let apiKey: String
    private let baseURL: URL
    private var webSocketTask: URLSessionWebSocketTask?
    private var session: URLSession?

    /// Connection state
    public private(set) var isConnected = false

    /// Event handlers
    public var onUsageUpdate: ((UsageUpdate) -> Void)?
    public var onBalanceUpdate: ((BalanceUpdate) -> Void)?
    public var onAlert: ((Alert) -> Void)?
    public var onError: ((Error) -> Void)?
    public var onConnect: (() -> Void)?
    public var onDisconnect: (() -> Void)?

    // MARK: - Initialization

    init(apiKey: String, baseURL: URL) {
        self.apiKey = apiKey
        self.baseURL = baseURL
        super.init()
    }

    // MARK: - Connection Management

    /// Connect to WebSocket
    public func connect() {
        guard !isConnected else { return }

        // Create WebSocket URL (ws:// or wss://)
        var components = URLComponents(url: baseURL, resolvingAgainstBaseURL: false)!
        components.scheme = components.scheme == "https" ? "wss" : "ws"
        components.path = "/v1/ws"

        var request = URLRequest(url: components.url!)
        request.addValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")

        let session = URLSession(configuration: .default, delegate: self, delegateQueue: nil)
        self.session = session

        webSocketTask = session.webSocketTask(with: request)
        webSocketTask?.resume()

        receiveMessage()
    }

    /// Disconnect from WebSocket
    public func disconnect() {
        webSocketTask?.cancel(with: .goingAway, reason: nil)
        webSocketTask = nil
        isConnected = false
        onDisconnect?()
    }

    /// Send message
    /// - Parameter message: Message to send
    public func send(_ message: String) {
        let message = URLSessionWebSocketTask.Message.string(message)
        webSocketTask?.send(message) { [weak self] error in
            if let error = error {
                self?.onError?(error)
            }
        }
    }

    // MARK: - Private Methods

    private func receiveMessage() {
        webSocketTask?.receive { [weak self] result in
            guard let self = self else { return }

            switch result {
            case .success(let message):
                self.handleMessage(message)
                self.receiveMessage() // Continue receiving

            case .failure(let error):
                self.onError?(error)
            }
        }
    }

    private func handleMessage(_ message: URLSessionWebSocketTask.Message) {
        guard case .string(let text) = message else { return }
        guard let data = text.data(using: .utf8) else { return }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601

        // Try to decode as different message types
        if let usageUpdate = try? decoder.decode(UsageUpdate.self, from: data) {
            onUsageUpdate?(usageUpdate)
        } else if let balanceUpdate = try? decoder.decode(BalanceUpdate.self, from: data) {
            onBalanceUpdate?(balanceUpdate)
        } else if let alert = try? decoder.decode(Alert.self, from: data) {
            onAlert?(alert)
        }
    }

    // MARK: - Message Types

    public struct UsageUpdate: Decodable {
        public let type: String
        public let endpoint: String
        public let cost: Double
        public let timestamp: Date
    }

    public struct BalanceUpdate: Decodable {
        public let type: String
        public let balance: Double
        public let timestamp: Date
    }

    public struct Alert: Decodable {
        public let type: String
        public let severity: String
        public let message: String
        public let timestamp: Date
    }
}

// MARK: - URLSessionWebSocketDelegate

@available(iOS 13.0, macOS 10.15, tvOS 13.0, watchOS 6.0, *)
extension MoneyAPIWebSocket: URLSessionWebSocketDelegate {
    public func urlSession(
        _ session: URLSession,
        webSocketTask: URLSessionWebSocketTask,
        didOpenWithProtocol protocol: String?
    ) {
        isConnected = true
        onConnect?()
    }

    public func urlSession(
        _ session: URLSession,
        webSocketTask: URLSessionWebSocketTask,
        didCloseWith closeCode: URLSessionWebSocketTask.CloseCode,
        reason: Data?
    ) {
        isConnected = false
        onDisconnect?()
    }
}
