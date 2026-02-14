<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import Editor from '$lib/components/Editor.svelte';
	import EditorToolbar from '$lib/components/EditorToolbar.svelte';
	import GenerationControls from '$lib/components/GenerationControls.svelte';
	import { generationState } from '$lib/stores/generation.svelte';
	import { storyState } from '$lib/stores/story.svelte';

	const ACTIVE_STORY_KEY = 'ai-invasion-active-story-id';

	let hasStory = $derived(!!storyState.activeStoryId);

	onMount(async () => {
		// Connect WebSocket
		generationState.connect();

		// Load story list
		await storyState.loadStories();

		// Restore previously active story from localStorage
		const savedId = localStorage.getItem(ACTIVE_STORY_KEY);
		if (savedId && storyState.stories.some((s) => s.id === savedId)) {
			storyState.setActiveStory(savedId);
		} else if (storyState.stories.length > 0) {
			// Auto-select first story if no saved selection
			storyState.setActiveStory(storyState.stories[0].id);
		}
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

{#if hasStory}
	<div class="editor-pane">
		<EditorToolbar />
		<Editor />
		<GenerationControls />
	</div>
{:else}
	<div class="welcome-state">
		<div class="welcome-content">
			<h2 class="welcome-title">AI Story Writer</h2>
			<p class="welcome-text">Create a new story in the Settings panel to get started.</p>
			<p class="welcome-hint">Use the left sidebar to create stories, configure your LLM backend, and manage your writing.</p>
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

	.welcome-state {
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
		margin: 0 0 8px;
		line-height: 1.5;
	}

	.welcome-hint {
		color: var(--text-muted, #9ca3af);
		font-size: 13px;
		margin: 0;
		line-height: 1.5;
	}
</style>
