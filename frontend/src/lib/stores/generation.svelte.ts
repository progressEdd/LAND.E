import type { StoryAnalysis } from '$lib/types';
import { wsClient, type WSServerMessage } from '$lib/api/ws';
import { storyState } from '$lib/stores/story.svelte';
import { settingsState } from '$lib/stores/settings.svelte';
import type { ConnectionState } from '$lib/api/ws';

export type GenerationStatus = 'idle' | 'generating' | 'draft_ready' | 'accepting' | 'rejecting';
export type DraftAction = 'accepted' | 'rejected' | null;

class GenerationState {
	status = $state<GenerationStatus>('idle');
	draftNodeId = $state<string | null>(null);
	draftContent = $state('');
	lastAction = $state<DraftAction>(null);
	lastAnalysis = $state<StoryAnalysis | null>(null);
	error = $state<string | null>(null);
	connectionState = $state<ConnectionState>('disconnected');

	get isGenerating(): boolean {
		return this.status === 'generating';
	}

	get hasDraft(): boolean {
		return this.status === 'draft_ready';
	}

	get isConnected(): boolean {
		return this.connectionState === 'connected';
	}

	connect(): void {
		wsClient.connect(
			(msg: WSServerMessage) => this.handleMessage(msg),
			(state: ConnectionState) => {
				this.connectionState = state;
			}
		);
	}

	disconnect(): void {
		wsClient.disconnect();
	}

	startGeneration(storyId: string, nodeId: string, seed?: string): void {
		this.status = 'generating';
		this.draftContent = '';
		this.draftNodeId = null;
		this.lastAction = null;
		this.lastAnalysis = null;
		this.error = null;

		const model = settingsState.model;

		const msg: { type: 'generate'; story_id: string; node_id: string; model: string; seed?: string } = {
			type: 'generate',
			story_id: storyId,
			node_id: nodeId,
			model
		};
		if (seed) msg.seed = seed;

		wsClient.send(msg);
	}

	cancelGeneration(): void {
		wsClient.send({ type: 'cancel' });
	}

	acceptDraft(content: string, provenanceSpans: { start_offset: number; end_offset: number; source: string }[]): void {
		if (!this.draftNodeId) return;
		this.status = 'accepting';
		wsClient.send({
			type: 'accept',
			node_id: this.draftNodeId,
			content,
			provenance_spans: provenanceSpans
		});
	}

	rejectDraft(): void {
		if (!this.draftNodeId) return;
		this.status = 'rejecting';
		wsClient.send({
			type: 'reject',
			node_id: this.draftNodeId
		});
	}

	private handleMessage(msg: WSServerMessage): void {
		switch (msg.type) {
			case 'token':
				this.draftContent += msg.content;
				break;

			case 'draft_created':
				this.draftNodeId = msg.node_id;
				break;

			case 'complete':
				this.draftNodeId = msg.node_id;
				this.lastAnalysis = msg.analysis;
				this.status = 'draft_ready';
				break;

			case 'cancelled':
				this.draftNodeId = msg.node_id;
				this.status = 'draft_ready';
				break;

			case 'accepted':
				this.lastAction = 'accepted';
				this.status = 'idle';
				this.draftNodeId = null;
				this.draftContent = '';
				// Refresh the active story to get updated active_path and nodes
				storyState.refreshActiveStory();
				break;

			case 'rejected':
				this.lastAction = 'rejected';
				this.status = 'idle';
				this.draftNodeId = null;
				this.draftContent = '';
				break;

			case 'error':
				this.error = msg.message;
				this.status = 'idle';
				break;
		}
	}
}

export const generationState = new GenerationState();
