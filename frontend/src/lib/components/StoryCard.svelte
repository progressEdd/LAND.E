<script lang="ts">
	import type { StoryOverviewStory } from '$lib/types';
	import { storyState } from '$lib/stores/story.svelte';

	let { story }: { story: StoryOverviewStory } = $props();

	async function handleOpen(): Promise<void> {
		await storyState.setActiveStory(story.id);
	}

	function formatDate(dateStr: string): string {
		const d = new Date(dateStr);
		const now = new Date();
		const diffMs = now.getTime() - d.getTime();
		const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
		if (diffDays === 0) return 'Today';
		if (diffDays === 1) return 'Yesterday';
		if (diffDays < 7) return `${diffDays} days ago`;
		return d.toLocaleDateString();
	}
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="story-card" onclick={handleOpen} role="button" tabindex="0">
	<div class="card-header">
		<h3 class="card-title">{story.title}</h3>
		<span class="card-date">{formatDate(story.updated_at || story.created_at)}</span>
	</div>
	<p class="card-premise">{story.premise}</p>
	<div class="card-footer">
		<div class="card-characters">
			{#each story.character_names.slice(0, 5) as name}
				<span class="char-badge">{name}</span>
			{/each}
			{#if story.character_names.length > 5}
				<span class="char-badge char-more">+{story.character_names.length - 5}</span>
			{/if}
		</div>
		<span class="card-nodes">{story.node_count} paragraphs</span>
	</div>
</div>

<style>
	.story-card {
		display: flex;
		flex-direction: column;
		padding: 16px;
		background-color: var(--sidebar-bg, #111827);
		border: 1px solid var(--border-color, #374151);
		border-radius: 8px;
		cursor: pointer;
		transition: border-color 150ms ease, background-color 150ms ease;
		min-height: 140px;
	}

	.story-card:hover {
		border-color: #6366f1;
		background-color: var(--hover-bg, #1f2937);
	}

	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 8px;
		gap: 8px;
	}

	.card-title {
		margin: 0;
		font-size: 15px;
		font-weight: 600;
		color: var(--text-primary, #e5e7eb);
		line-height: 1.3;
		flex: 1;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.card-date {
		font-size: 11px;
		color: var(--text-faint, #6b7280);
		white-space: nowrap;
		flex-shrink: 0;
	}

	.card-premise {
		margin: 0 0 12px;
		font-size: 13px;
		color: var(--text-muted, #9ca3af);
		line-height: 1.5;
		display: -webkit-box;
		-webkit-line-clamp: 3;
		-webkit-box-orient: vertical;
		overflow: hidden;
		flex: 1;
	}

	.card-footer {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 8px;
		overflow: hidden;
	}

	.card-characters {
		display: flex;
		flex-wrap: wrap;
		gap: 4px;
		min-width: 0;
		flex: 1;
		overflow: hidden;
	}

	.char-badge {
		font-size: 10px;
		padding: 2px 6px;
		border-radius: 10px;
		background-color: rgba(99, 102, 241, 0.15);
		color: #a5b4fc;
		white-space: nowrap;
	}

	.char-more {
		background-color: rgba(107, 114, 128, 0.2);
		color: var(--text-faint, #6b7280);
	}

	.card-nodes {
		font-size: 11px;
		color: var(--text-faint, #6b7280);
		white-space: nowrap;
		flex-shrink: 0;
	}
</style>
