<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { Editor } from '@tiptap/core';
	import StarterKit from '@tiptap/starter-kit';
	import { Provenance } from '$lib/extensions/provenance';
	import { editorState } from '$lib/stores/editor.svelte';
	import { generationState } from '$lib/stores/generation.svelte';

	let { content = '', onUpdate }: { content?: string; onUpdate?: (html: string) => void } =
		$props();

	let element: HTMLDivElement;
	let editor: Editor | null = null;

	// Track how many draft characters have been inserted
	let insertedDraftLength = 0;
	let lastDraftContentLength = 0;

	onMount(() => {
		editor = new Editor({
			element: element,
			extensions: [StarterKit, Provenance],
			content: content,
			editorProps: {
				attributes: {
					class: 'editor-content'
				},
				// Apply user_written provenance to user-typed text
				handleTextInput: (_view, from, to, text) => {
					// Let Tiptap handle the insertion, then mark it
					// We use a small timeout to apply the mark after Tiptap processes the input
					const ed = editor;
					if (!ed) return false;

					// Insert the text with user_written provenance mark
					ed.chain()
						.focus()
						.deleteRange({ from, to })
						.insertContentAt(from, {
							type: 'text',
							text: text,
							marks: [{ type: 'provenance', attrs: { source: 'user_written' } }]
						})
						.run();

					return true; // We handled the input
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

	// Watch for draft content changes and append tokens to editor
	$effect(() => {
		const content = generationState.draftContent;
		const status = generationState.status;

		if (!editor) return;

		if (status === 'generating' && content.length > lastDraftContentLength) {
			// New tokens arrived — append them with ai_generated provenance
			const newText = content.slice(lastDraftContentLength);
			lastDraftContentLength = content.length;
			insertedDraftLength += newText.length;

			editor
				.chain()
				.focus('end')
				.insertContent({
					type: 'text',
					text: newText,
					marks: [{ type: 'provenance', attrs: { source: 'ai_generated' } }]
				})
				.run();
		}
	});

	// Watch for draft completion (accept/reject)
	$effect(() => {
		const status = generationState.status;

		if (status === 'idle' && insertedDraftLength > 0 && lastDraftContentLength > 0) {
			// Check if it was a reject — if draftContent is empty, remove
			if (generationState.draftContent === '') {
				// Reject: remove the draft text from editor
				removeDraftText(insertedDraftLength);
			}
			// Accept: text stays in editor (already there with ai_generated marks)

			// Reset tracking
			insertedDraftLength = 0;
			lastDraftContentLength = 0;
		}
	});

	function removeDraftText(charCount: number) {
		if (!editor || charCount <= 0) return;
		const endPos = editor.state.doc.content.size;
		const from = Math.max(1, endPos - charCount);
		editor.chain().deleteRange({ from, to: endPos }).run();
	}

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
