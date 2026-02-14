<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { Editor } from '@tiptap/core';
	import StarterKit from '@tiptap/starter-kit';
	import { Provenance } from '$lib/extensions/provenance';
	import { editorState } from '$lib/stores/editor.svelte';

	let { content = '', onUpdate }: { content?: string; onUpdate?: (html: string) => void } =
		$props();

	let element: HTMLDivElement;
	let editor: Editor | null = null;

	onMount(() => {
		editor = new Editor({
			element: element,
			extensions: [StarterKit, Provenance],
			content: content,
			editorProps: {
				attributes: {
					class: 'editor-content'
				}
			},
			onTransaction: () => {
				// Reassign to trigger Svelte 5 reactivity in editorState
				editorState.editor = editor;
			},
			onUpdate: ({ editor: e }) => {
				onUpdate?.(e.getHTML());
			}
		});

		editorState.editor = editor;
	});

	onDestroy(() => {
		editor?.destroy();
		editorState.editor = null;
	});
</script>

<div class="editor-wrapper">
	<div class="editor-element" bind:this={element}></div>
</div>

<style>
	.editor-wrapper {
		flex: 1;
		overflow-y: auto;
		background-color: var(--panel-bg, #030712);
	}

	.editor-element {
		height: 100%;
	}

	/* ProseMirror styles */
	.editor-element :global(.ProseMirror) {
		min-height: 100%;
		padding: 24px 32px;
		outline: none;
		color: var(--text-primary, #e5e7eb);
		font-size: 15px;
		line-height: 1.7;
		caret-color: #a5b4fc;
	}

	.editor-element :global(.ProseMirror:focus) {
		outline: none;
	}

	/* Headings */
	.editor-element :global(.ProseMirror h1) {
		font-size: 1.75em;
		font-weight: 700;
		margin: 1em 0 0.5em;
		color: var(--text-primary, #e5e7eb);
	}

	.editor-element :global(.ProseMirror h2) {
		font-size: 1.4em;
		font-weight: 600;
		margin: 0.8em 0 0.4em;
		color: var(--text-primary, #e5e7eb);
	}

	.editor-element :global(.ProseMirror h3) {
		font-size: 1.15em;
		font-weight: 600;
		margin: 0.6em 0 0.3em;
		color: var(--text-primary, #e5e7eb);
	}

	/* Paragraphs */
	.editor-element :global(.ProseMirror p) {
		margin: 0.5em 0;
	}

	/* Blockquote */
	.editor-element :global(.ProseMirror blockquote) {
		border-left: 3px solid #4b5563;
		padding-left: 16px;
		margin: 0.8em 0;
		color: var(--text-secondary, #d1d5db);
		font-style: italic;
	}

	/* Code block */
	.editor-element :global(.ProseMirror pre) {
		background-color: #1f2937;
		border-radius: 6px;
		padding: 12px 16px;
		margin: 0.8em 0;
		overflow-x: auto;
		font-family: 'SF Mono', 'Fira Code', monospace;
		font-size: 0.9em;
	}

	.editor-element :global(.ProseMirror code) {
		background-color: #1f2937;
		border-radius: 3px;
		padding: 2px 5px;
		font-family: 'SF Mono', 'Fira Code', monospace;
		font-size: 0.9em;
	}

	/* Lists */
	.editor-element :global(.ProseMirror ul),
	.editor-element :global(.ProseMirror ol) {
		padding-left: 24px;
		margin: 0.5em 0;
	}

	.editor-element :global(.ProseMirror li) {
		margin: 0.2em 0;
	}

	/* Horizontal rule */
	.editor-element :global(.ProseMirror hr) {
		border: none;
		border-top: 1px solid #374151;
		margin: 1.5em 0;
	}

	/* Placeholder when empty */
	.editor-element :global(.ProseMirror p.is-editor-empty:first-child::before) {
		content: 'Start writing your story...';
		color: var(--text-faint, #6b7280);
		font-style: italic;
		pointer-events: none;
		float: left;
		height: 0;
	}
</style>
