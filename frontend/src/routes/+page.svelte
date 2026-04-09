<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import Editor from '$lib/components/Editor.svelte';
	import EditorToolbar from '$lib/components/EditorToolbar.svelte';
	import GenerationControls from '$lib/components/GenerationControls.svelte';
	import Dashboard from '$lib/components/Dashboard.svelte';
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
	<Dashboard />
{/if}

<style>
	.editor-pane {
		display: flex;
		flex-direction: column;
		height: 100%;
		width: 100%;
		background-color: var(--panel-bg, #030712);
	}
</style>
