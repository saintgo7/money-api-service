package com.moneyapi.sdk

import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.receiveAsFlow
import kotlinx.serialization.json.Json
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener

/**
 * WebSocket manager for real-time Money API updates
 */
class MoneyAPIWebSocket(
    private val apiKey: String,
    private val baseUrl: String,
    private val client: OkHttpClient
) {
    private var webSocket: WebSocket? = null
    private val json = Json { ignoreUnknownKeys = true }

    // Channels for different message types
    private val usageUpdateChannel = Channel<UsageUpdate>(Channel.UNLIMITED)
    private val balanceUpdateChannel = Channel<BalanceUpdate>(Channel.UNLIMITED)
    private val alertChannel = Channel<Alert>(Channel.UNLIMITED)
    private val errorChannel = Channel<Throwable>(Channel.UNLIMITED)
    private val connectionStateChannel = Channel<ConnectionState>(Channel.UNLIMITED)

    /**
     * Connection state
     */
    enum class ConnectionState {
        CONNECTED,
        DISCONNECTED,
        CONNECTING,
        ERROR
    }

    /**
     * Current connection state
     */
    var isConnected: Boolean = false
        private set

    /**
     * Flow of usage updates
     */
    val usageUpdates: Flow<UsageUpdate> = usageUpdateChannel.receiveAsFlow()

    /**
     * Flow of balance updates
     */
    val balanceUpdates: Flow<BalanceUpdate> = balanceUpdateChannel.receiveAsFlow()

    /**
     * Flow of alerts
     */
    val alerts: Flow<Alert> = alertChannel.receiveAsFlow()

    /**
     * Flow of errors
     */
    val errors: Flow<Throwable> = errorChannel.receiveAsFlow()

    /**
     * Flow of connection state changes
     */
    val connectionState: Flow<ConnectionState> = connectionStateChannel.receiveAsFlow()

    /**
     * Connect to WebSocket
     */
    fun connect() {
        if (isConnected) return

        connectionStateChannel.trySend(ConnectionState.CONNECTING)

        val wsUrl = baseUrl
            .replace("https://", "wss://")
            .replace("http://", "ws://") + "/v1/ws"

        val request = Request.Builder()
            .url(wsUrl)
            .header("Authorization", "Bearer $apiKey")
            .build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                isConnected = true
                connectionStateChannel.trySend(ConnectionState.CONNECTED)
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                handleMessage(text)
            }

            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                webSocket.close(1000, null)
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                isConnected = false
                connectionStateChannel.trySend(ConnectionState.DISCONNECTED)
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                isConnected = false
                connectionStateChannel.trySend(ConnectionState.ERROR)
                errorChannel.trySend(MoneyAPIException.WebSocketError(t.message ?: "Unknown error"))
            }
        })
    }

    /**
     * Disconnect from WebSocket
     */
    fun disconnect() {
        webSocket?.close(1000, "Client disconnect")
        webSocket = null
        isConnected = false
        connectionStateChannel.trySend(ConnectionState.DISCONNECTED)
    }

    /**
     * Send message
     *
     * @param message Message to send
     */
    fun send(message: String) {
        webSocket?.send(message)
    }

    /**
     * Close all channels
     */
    fun close() {
        disconnect()
        usageUpdateChannel.close()
        balanceUpdateChannel.close()
        alertChannel.close()
        errorChannel.close()
        connectionStateChannel.close()
    }

    private fun handleMessage(text: String) {
        try {
            // Try to decode as different message types
            when {
                text.contains("\"type\":\"usage\"") -> {
                    val update = json.decodeFromString<UsageUpdate>(text)
                    usageUpdateChannel.trySend(update)
                }
                text.contains("\"type\":\"balance\"") -> {
                    val update = json.decodeFromString<BalanceUpdate>(text)
                    balanceUpdateChannel.trySend(update)
                }
                text.contains("\"type\":\"alert\"") -> {
                    val alert = json.decodeFromString<Alert>(text)
                    alertChannel.trySend(alert)
                }
            }
        } catch (e: Exception) {
            errorChannel.trySend(MoneyAPIException.DecodingError(e))
        }
    }
}
