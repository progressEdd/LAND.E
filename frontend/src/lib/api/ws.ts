import type { StoryAnalysis } from '$lib/types';

// Message types sent from client to server
export type WSClientMessage =
	| { type: 'generate'; story_id: string; node_id: string; model: string; seed?: string }
	| { type: 'cancel' }
	| { type: 'accept'; node_id: string; content: string; provenance_spans: ProvenanceSpanData[] }
	| { type: 'reject'; node_id: string }
	| { type: 'ping' };

// Message types received from server
export type WSServerMessage =
	| { type: 'token'; content: string }
	| { type: 'status'; message: string }
	| { type: 'draft_created'; node_id: string }
	| { type: 'complete'; node_id: string; analysis: StoryAnalysis }
	| { type: 'cancelled'; node_id: string }
	| { type: 'accepted'; node_id: string }
	| { type: 'rejected'; node_id: string }
	| { type: 'error'; message: string }
	| { type: 'pong' };

export interface ProvenanceSpanData {
	start_offset: number;
	end_offset: number;
	source: string;
}

export type ConnectionState = 'disconnected' | 'connecting' | 'connected';

class WebSocketClient {
	private ws: WebSocket | null = null;
	private reconnectAttempts = 0;
	private maxReconnectAttempts = 5;
	private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
	private onMessage: ((msg: WSServerMessage) => void) | null = null;
	private _connectionState: ConnectionState = 'disconnected';
	private onConnectionChange: ((state: ConnectionState) => void) | null = null;
	private heartbeatInterval: ReturnType<typeof setInterval> | null = null;
	private pongTimeout: ReturnType<typeof setTimeout> | null = null;
	private heartbeatIntervalMs = 25000;
	private pongTimeoutMs = 10000;

	get connectionState(): ConnectionState {
		return this._connectionState;
	}

	private setConnectionState(state: ConnectionState) {
		this._connectionState = state;
		this.onConnectionChange?.(state);
	}

	connect(
		onMessage: (msg: WSServerMessage) => void,
		onConnectionChange?: (state: ConnectionState) => void
	): void {
		this.onMessage = onMessage;
		this.onConnectionChange = onConnectionChange ?? null;
		this._connect();
	}

	private _connect(): void {
		if (this.ws?.readyState === WebSocket.OPEN) return;

		this.setConnectionState('connecting');

		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		const url = `${protocol}//${window.location.host}/ws/generate`;

		this.ws = new WebSocket(url);

		this.ws.onopen = () => {
			this.reconnectAttempts = 0;
			this.setConnectionState('connected');
			this.startHeartbeat();
		};

		this.ws.onmessage = (event) => {
			try {
				const msg: WSServerMessage = JSON.parse(event.data);
				if (msg.type === 'pong') {
					this.stopHeartbeat();
					this.startHeartbeat();
					return;
				}
				this.onMessage?.(msg);
			} catch {
				console.error('Failed to parse WebSocket message:', event.data);
			}
		};

		this.ws.onclose = () => {
			this.stopHeartbeat();
			this.setConnectionState('disconnected');
			this._attemptReconnect();
		};

		this.ws.onerror = () => {
			// onclose will fire after onerror, which handles reconnection
		};
	}

	private _attemptReconnect(): void {
		if (this.reconnectAttempts >= this.maxReconnectAttempts) {
			return;
		}

		// Exponential backoff: 1s, 2s, 4s, 8s, 16s
		const delay = Math.pow(2, this.reconnectAttempts) * 1000;
		this.reconnectAttempts++;

		this.reconnectTimer = setTimeout(() => {
			this._connect();
		}, delay);
	}

	reconnect(): void {
		// Stop any existing heartbeat
		this.stopHeartbeat();
		// Clear any pending reconnect timer
		if (this.reconnectTimer) {
			clearTimeout(this.reconnectTimer);
			this.reconnectTimer = null;
		}
		// Close existing socket if any
		this.ws?.close();
		this.ws = null;
		// Reset attempts and connect fresh
		this.reconnectAttempts = 0;
		this._connect();
	}

	resetReconnectAttempts(): void {
		this.reconnectAttempts = 0;
	}

	send(msg: WSClientMessage): void {
		if (this.ws?.readyState !== WebSocket.OPEN) {
			console.error('WebSocket not connected');
			return;
		}
		this.ws.send(JSON.stringify(msg));
	}

	private startHeartbeat(): void {
		this.stopHeartbeat();
		this.heartbeatInterval = setInterval(() => {
			if (this.ws?.readyState === WebSocket.OPEN) {
				this.send({ type: 'ping' });
				this.pongTimeout = setTimeout(() => {
					this.ws?.close();
				}, this.pongTimeoutMs);
			}
		}, this.heartbeatIntervalMs);
	}

	private stopHeartbeat(): void {
		if (this.heartbeatInterval) {
			clearInterval(this.heartbeatInterval);
			this.heartbeatInterval = null;
		}
		if (this.pongTimeout) {
			clearTimeout(this.pongTimeout);
			this.pongTimeout = null;
		}
	}

	disconnect(): void {
		this.stopHeartbeat();
		if (this.reconnectTimer) {
			clearTimeout(this.reconnectTimer);
			this.reconnectTimer = null;
		}
		this.reconnectAttempts = this.maxReconnectAttempts; // Prevent reconnect
		this.ws?.close();
		this.ws = null;
		this.setConnectionState('disconnected');
	}
}

export const wsClient = new WebSocketClient();
