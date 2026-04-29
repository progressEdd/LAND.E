<script lang="ts">
	import { onMount } from 'svelte';
	import { generationState } from '$lib/stores/generation.svelte';
	import { storyState } from '$lib/stores/story.svelte';
	import { settingsState } from '$lib/stores/settings.svelte';

	const statusMessages: Record<string, string> = {
		idle: '',
		generating: 'Generating...',
		draft_ready: 'Draft ready — accept or reject',
		accepting: 'Accepting...',
		rejecting: 'Rejecting...'
	};

	function getLastNodeId(): string | null {
		const story = storyState.activeStory;
		if (!story?.active_path?.length) return null;
		return story.active_path[story.active_path.length - 1];
	}

	function handleGenerate() {
		const storyId = storyState.activeStoryId;
		const nodeId = getLastNodeId();
		if (!storyId || !nodeId) return;
		generationState.startGeneration(storyId, nodeId);
	}

	function handleCancel() {
		generationState.cancelGeneration();
	}

	function handleAccept() {
		// Send accept with the draft content and a single provenance span
		const content = generationState.draftContent;
		generationState.acceptDraft(content, [
			{ start_offset: 0, end_offset: content.length, source: 'ai_generated' }
		]);
	}

	function handleReject() {
		generationState.rejectDraft();
	}

	onMount(() => {
		if (generationState.connectionState !== 'connected') {
			generationState.reconnect();
		}
	});

	function handleIndicatorClick() {
		generationState.reconnect();
	}

	const canGenerate = $derived(
		generationState.status === 'idle' &&
			!!storyState.activeStoryId &&
			!!settingsState.model &&
			generationState.isConnected
	);
</script>

<div class="generation-controls">
	<div class="controls-left">
		<!-- Connection indicator -->
		<div
			class="connection-indicator"
			title="Click to reconnect · {generationState.connectionState}"
			onclick={handleIndicatorClick}
			role="button"
			tabindex="0"
			onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') handleIndicatorClick(); }}
		>
			<span
				class="dot"
				class:connected={generationState.connectionState === 'connected'}
				class:connecting={generationState.connectionState === 'connecting'}
				class:disconnected={generationState.connectionState === 'disconnected'}
			></span>
			<span class="connection-text">{generationState.connectionState}</span>
		</div>

		<!-- Status text -->
		{#if generationState.status === 'generating'}
			<span class="status-text generating">
				<span class="generating-dot"></span>
				Generating...
			</span>
		{:else if statusMessages[generationState.status]}
			<span class="status-text">{statusMessages[generationState.status]}</span>
		{/if}

		{#if generationState.error}
			<span class="error-text">{generationState.error}</span>
		{/if}
	</div>

	<div class="controls-right">
		{#if generationState.status === 'idle'}
			<button class="btn btn-generate" onclick={handleGenerate} disabled={!canGenerate}>
				Generate
			</button>
		{/if}

		{#if generationState.status === 'generating'}
			<button class="btn btn-cancel" onclick={handleCancel}>Cancel</button>
		{/if}

		{#if generationState.status === 'draft_ready'}
			<button class="btn btn-reject" onclick={handleReject}>Reject</button>
			<button class="btn btn-accept" onclick={handleAccept}>Accept</button>
		{/if}
	</div>
</div>

<style>
	.generation-controls {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 8px 16px;
		background-color: var(--sidebar-bg, #111827);
		border-top: 1px solid var(--border-color, #374151);
		flex-shrink: 0;
		gap: 12px;
	}

	.controls-left {
		display: flex;
		align-items: center;
		gap: 12px;
		min-width: 0;
	}

	.controls-right {
		display: flex;
		align-items: center;
		gap: 8px;
		flex-shrink: 0;
	}

	.connection-indicator {
		display: flex;
		align-items: center;
		gap: 6px;
		cursor: pointer;
	}

	.connection-indicator:hover .connection-text {
		color: var(--text-secondary, #d1d5db);
	}

	.dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		flex-shrink: 0;
	}

	.dot.connected {
		background-color: #22c55e;
	}

	.dot.connecting {
		background-color: #eab308;
		animation: pulse 1s infinite;
	}

	.dot.disconnected {
		background-color: #ef4444;
	}

	@keyframes pulse {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0.4;
		}
	}

	.connection-text {
		font-size: 11px;
		color: var(--text-faint, #6b7280);
		text-transform: capitalize;
	}

	.status-text {
		font-size: 12px;
		color: var(--text-secondary, #d1d5db);
	}

	.status-text.generating {
		display: flex;
		align-items: center;
		gap: 6px;
		color: #a5b4fc;
	}

	.generating-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background-color: #6366f1;
		animation: pulse 1s infinite;
		flex-shrink: 0;
	}

	.error-text {
		font-size: 12px;
		color: #ef4444;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.btn {
		padding: 6px 14px;
		border: none;
		border-radius: 6px;
		font-size: 12px;
		font-weight: 500;
		cursor: pointer;
		transition:
			background-color 100ms ease,
			opacity 100ms ease;
	}

	.btn:disabled {
		opacity: 0.4;
		cursor: default;
	}

	.btn-generate {
		background-color: #4f46e5;
		color: #fff;
	}

	.btn-generate:hover:not(:disabled) {
		background-color: #4338ca;
	}

	.btn-cancel {
		background-color: #6b7280;
		color: #fff;
	}

	.btn-cancel:hover {
		background-color: #4b5563;
	}

	.btn-accept {
		background-color: #16a34a;
		color: #fff;
	}

	.btn-accept:hover {
		background-color: #15803d;
	}

	.btn-reject {
		background-color: #dc2626;
		color: #fff;
	}

	.btn-reject:hover {
		background-color: #b91c1c;
	}
</style>
