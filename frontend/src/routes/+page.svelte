<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import Editor from '$lib/components/Editor.svelte';
	import EditorToolbar from '$lib/components/EditorToolbar.svelte';
	import GenerationControls from '$lib/components/GenerationControls.svelte';
	import { generationState } from '$lib/stores/generation.svelte';

	onMount(() => {
		generationState.connect();
	});

	onDestroy(() => {
		generationState.disconnect();
	});
</script>

<div class="editor-pane">
	<EditorToolbar />
	<Editor />
	<GenerationControls />
</div>

<style>
	.editor-pane {
		display: flex;
		flex-direction: column;
		height: 100%;
		width: 100%;
		background-color: var(--panel-bg, #030712);
	}
</style>
