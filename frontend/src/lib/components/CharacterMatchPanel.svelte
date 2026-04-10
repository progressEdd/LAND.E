<script lang="ts">
	import { characterState } from '$lib/stores/character.svelte';
	import { onMount } from 'svelte';

	let dismissedGroups = $state<Set<string>>(new Set());

	let visibleCandidates = $derived(
		characterState.candidates.filter(g => !dismissedGroups.has(g.normalized_name))
	);

	onMount(() => {
		characterState.loadCandidates();
	});

	function confirmGroup(group: typeof characterState.candidates[0]) {
		const name = group.normalized_name;
		characterState.confirmLink(group, name);
	}

	function dismissGroup(group: typeof characterState.candidates[0]) {
		dismissedGroups = new Set([...dismissedGroups, group.normalized_name]);
	}

	function close() {
		characterState.closeMatchPanel();
	}
</script>

<div class="match-panel">
	<div class="match-header">
		<h3>Character Matches</h3>
		<span class="match-count">{visibleCandidates.length} group{visibleCandidates.length !== 1 ? 's' : ''}</span>
		<button class="close-btn" onclick={close} title="Close">&times;</button>
	</div>

	{#if characterState.error}
		<div class="error-msg">{characterState.error}</div>
	{/if}

	{#if characterState.isLoading}
		<div class="loading">Loading matches...</div>
	{:else if visibleCandidates.length === 0}
		<div class="empty-state">No character matches found</div>
	{:else}
		<div class="candidate-list">
			{#each visibleCandidates as group}
				<div class="candidate-card">
					<h4 class="candidate-name">{group.normalized_name}</h4>
					<ul class="mention-list">
						{#each group.mentions as mention}
							<li>
								<span class="raw-name">{mention.raw_name}</span>
								<span class="in-story">in</span>
								<span class="story-title">{mention.story_title}</span>
							</li>
						{/each}
					</ul>
					<div class="candidate-actions">
						<button class="btn btn-primary btn-small" onclick={() => confirmGroup(group)}>
							Link as same character
						</button>
						<button class="btn btn-small" onclick={() => dismissGroup(group)}>
							Different characters
						</button>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	.match-panel {
		width: 380px;
		max-height: calc(100vh - 40px);
		background-color: var(--panel-bg, #030712);
		border: 1px solid var(--border-color, #374151);
		border-radius: 8px;
		display: flex;
		flex-direction: column;
		overflow: hidden;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
	}

	.match-header {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 12px 16px;
		border-bottom: 1px solid var(--border-color, #374151);
	}

	.match-header h3 {
		margin: 0;
		font-size: 15px;
		color: var(--text-primary, #e5e7eb);
	}

	.match-count {
		font-size: 12px;
		color: var(--text-muted, #9ca3af);
	}

	.close-btn {
		margin-left: auto;
		background: none;
		border: none;
		color: var(--text-muted, #9ca3af);
		font-size: 20px;
		cursor: pointer;
		padding: 0 4px;
		line-height: 1;
	}

	.close-btn:hover {
		color: var(--text-primary, #e5e7eb);
	}

	.error-msg {
		padding: 8px 16px;
		background: rgba(239, 68, 68, 0.1);
		color: #ef4444;
		font-size: 13px;
	}

	.loading, .empty-state {
		padding: 24px 16px;
		text-align: center;
		color: var(--text-muted, #9ca3af);
		font-size: 14px;
	}

	.candidate-list {
		flex: 1;
		overflow-y: auto;
		padding: 8px;
	}

	.candidate-card {
		padding: 12px;
		border: 1px solid var(--border-color, #374151);
		border-radius: 6px;
		margin-bottom: 8px;
		background-color: var(--hover-bg, #1f2937);
	}

	.candidate-name {
		margin: 0 0 8px;
		font-size: 14px;
		color: var(--text-primary, #e5e7eb);
	}

	.mention-list {
		list-style: none;
		padding: 0;
		margin: 0 0 10px;
	}

	.mention-list li {
		font-size: 13px;
		color: var(--text-secondary, #d1d5db);
		padding: 2px 0;
	}

	.raw-name {
		font-weight: 500;
	}

	.in-story {
		color: var(--text-muted, #9ca3af);
		margin: 0 4px;
	}

	.story-title {
		color: var(--text-faint, #6b7280);
		font-style: italic;
	}

	.candidate-actions {
		display: flex;
		gap: 8px;
	}

	.btn {
		padding: 6px 12px;
		font-size: 13px;
		border: 1px solid var(--border-color, #374151);
		border-radius: 6px;
		background-color: var(--panel-bg, #030712);
		color: var(--text-primary, #e5e7eb);
		cursor: pointer;
		transition: background-color 150ms ease, border-color 150ms ease;
	}

	.btn:hover:not(:disabled) {
		background-color: var(--hover-bg, #1f2937);
	}

	.btn-primary {
		background-color: #4f46e5;
		border-color: #4f46e5;
		color: #fff;
	}

	.btn-primary:hover:not(:disabled) {
		background-color: #4338ca;
	}

	.btn-small {
		padding: 5px 10px;
		font-size: 12px;
	}
</style>
