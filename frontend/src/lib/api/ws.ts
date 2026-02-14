import type { StoryAnalysis } from '$lib/types';

// Message types sent from client to server
export type WSClientMessage =
	| { type: 'generate'; story_id: string; node_id: string; model: string }
	| { type: 'cancel' }
	| { type: 'accept'; node_id: string; content: string; provenance_spans: ProvenanceSpanData[] }
	| { type: 'reject'; node_id: string };

// Message types received from server
export type WSServerMessage =
	| { type: 'token'; content: string }
	| { type: 'draft_created'; node_id: string }
	| { type: 'complete'; node_id: string; analysis: StoryAnalysis }
	| { type: 'cancelled'; node_id: string }
	| { type: 'accepted'; node_id: string }
	| { type: 'rejected'; node_id: string }
	| { type: 'error'; message: string };

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
		};

		this.ws.onmessage = (event) => {
			try {
				const msg: WSServerMessage = JSON.parse(event.data);
				this.onMessage?.(msg);
			} catch {
				console.error('Failed to parse WebSocket message:', event.data);
			}
		};

		this.ws.onclose = () => {
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

	send(msg: WSClientMessage): void {
		if (this.ws?.readyState !== WebSocket.OPEN) {
			console.error('WebSocket not connected');
			return;
		}
		this.ws.send(JSON.stringify(msg));
	}

	disconnect(): void {
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
