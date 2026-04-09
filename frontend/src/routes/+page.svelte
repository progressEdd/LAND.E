<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import Editor from '$lib/components/Editor.svelte';
	import EditorToolbar from '$lib/components/EditorToolbar.svelte';
	import GenerationControls from '$lib/components/GenerationControls.svelte';
	import { generationState } from '$lib/stores/generation.svelte';
	import { storyState } from '$lib/stores/story.svelte';

	const ACTIVE_STORY_KEY = 'ai-invasion-active-story-id';

	onMount(async () => {
		// Connect WebSocket
		generationState.connect();

		// Load story list (needed for both dashboard and restoring active story)
		await storyState.loadStories();

		// Restore previously active story from localStorage
		const savedId = localStorage.getItem(ACTIVE_STORY_KEY);
		if (savedId && storyState.stories.some((s) => s.id === savedId)) {
			storyState.setActiveStory(savedId);
		}
		// NOTE: No auto-selection of first story — user lands on dashboard
	});

	// Persist activeStoryId to localStorage on change
	$effect(() => {
		const id = storyState.activeStoryId;
		if (id) {
			localStorage.setItem(ACTIVE_STORY_KEY, id);
		} else {
			localStorage.removeItem(ACTIVE_STORY_KEY);
		}
	});

	onDestroy(() => {
		generationState.disconnect();
	});
</script>

{#if storyState.activeStoryId}
	<div class="editor-pane">
		<EditorToolbar />
		<Editor />
		<GenerationControls />
	</div>
{:else}
	<!-- Dashboard placeholder — replaced by Dashboard.svelte in Plan 03 -->
	<div class="dashboard-placeholder">
		<div class="welcome-content">
			<h2 class="welcome-title">AI Story Writer</h2>
			<p class="welcome-text">Loading dashboard...</p>
		</div>
	</div>
{/if}

<style>
	.editor-pane {
		display: flex;
		flex-direction: column;
		height: 100%;
		width: 100%;
		background-color: var(--panel-bg, #030712);
	}

	.dashboard-placeholder {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
		width: 100%;
		background-color: var(--panel-bg, #030712);
	}

	.welcome-content {
		text-align: center;
		max-width: 400px;
		padding: 32px;
	}

	.welcome-title {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--text-primary, #e5e7eb);
		margin: 0 0 12px;
	}

	.welcome-text {
		color: var(--text-secondary, #d1d5db);
		font-size: 15px;
		margin: 0;
		line-height: 1.5;
	}
</style>
