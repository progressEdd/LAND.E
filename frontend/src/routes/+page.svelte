<script lang="ts">
	import Editor from '$lib/components/Editor.svelte';
	import EditorToolbar from '$lib/components/EditorToolbar.svelte';
</script>

<div class="editor-pane">
	<EditorToolbar />
	<Editor />
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
