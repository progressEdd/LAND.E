<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { Editor } from '@tiptap/core';
	import StarterKit from '@tiptap/starter-kit';
	import { Provenance } from '$lib/extensions/provenance';
	import { editorState } from '$lib/stores/editor.svelte';
	import { generationState } from '$lib/stores/generation.svelte';
	import { storyState } from '$lib/stores/story.svelte';
	import type { StoryNode } from '$lib/types';

	let { content = '', onUpdate }: { content?: string; onUpdate?: (html: string) => void } =
		$props();

	let element: HTMLDivElement;
	let editor: Editor | null = null;

	// Track how many draft characters have been inserted
	let insertedDraftLength = 0;
	let lastDraftContentLength = 0;

	// Track which story is currently loaded in the editor to avoid redundant loads
	let loadedStoryId: string | null = null;

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

	/**
	 * Load story nodes into the editor with provenance marks preserved.
	 * Each node's content is inserted as a paragraph with its provenance spans
	 * applied as marks at the correct character offsets.
	 */
	function loadContent(nodes: StoryNode[]): void {
		if (!editor) return;

		// Clear the editor
		editor.commands.clearContent();

		if (nodes.length === 0) return;

		// Build content array with provenance marks applied
		const contentBlocks: Array<{ type: string; content?: Array<{ type: string; text: string; marks?: Array<{ type: string; attrs: { source: string } }> }> }> = [];

		for (const node of nodes) {
			if (!node.content) continue;

			const spans = node.provenance_spans;
			if (spans && spans.length > 0) {
				// Apply provenance marks to character ranges
				const textParts: Array<{ type: string; text: string; marks: Array<{ type: string; attrs: { source: string } }> }> = [];

				// Sort spans by start_offset
				const sortedSpans = [...spans].sort((a, b) => a.start_offset - b.start_offset);

				let lastEnd = 0;
				for (const span of sortedSpans) {
					// Fill any gap before this span with the node's default source
					if (span.start_offset > lastEnd) {
						const gapText = node.content.slice(lastEnd, span.start_offset);
						if (gapText) {
							textParts.push({
								type: 'text',
								text: gapText,
								marks: [{ type: 'provenance', attrs: { source: node.source } }]
							});
						}
					}
					// Add the span's text with its source
					const spanText = node.content.slice(span.start_offset, span.end_offset);
					if (spanText) {
						textParts.push({
							type: 'text',
							text: spanText,
							marks: [{ type: 'provenance', attrs: { source: span.source } }]
						});
					}
					lastEnd = span.end_offset;
				}
				// Fill any remaining text after last span
				if (lastEnd < node.content.length) {
					const remainingText = node.content.slice(lastEnd);
					if (remainingText) {
						textParts.push({
							type: 'text',
							text: remainingText,
							marks: [{ type: 'provenance', attrs: { source: node.source } }]
						});
					}
				}

				if (textParts.length > 0) {
					contentBlocks.push({ type: 'paragraph', content: textParts });
				}
			} else {
				// No provenance spans — use the node's source for the whole content
				contentBlocks.push({
					type: 'paragraph',
					content: [{
						type: 'text',
						text: node.content,
						marks: [{ type: 'provenance', attrs: { source: node.source } }]
					}]
				});
			}
		}

		if (contentBlocks.length > 0) {
			editor.commands.setContent({ type: 'doc', content: contentBlocks });
		}

		// Position cursor at the end
		editor.commands.focus('end');
	}

	// Watch for active story changes and load content into editor
	$effect(() => {
		const activeId = storyState.activeStoryId;
		const activeStory = storyState.activeStory;

		if (!editor) return;

		if (!activeId) {
			// No active story — clear editor
			if (loadedStoryId !== null) {
				editor.commands.clearContent();
				loadedStoryId = null;
			}
			return;
		}

		// Only reload if the story changed or wasn't loaded yet
		if (activeId !== loadedStoryId && activeStory && activeStory.nodes) {
			const pathNodes = storyState.getActivePathNodes();
			loadContent(pathNodes);
			loadedStoryId = activeId;
		}
	});

	// Watch for draft content changes and append tokens to editor
	$effect(() => {
		const content = generationState.draftContent;
		const status = generationState.status;

		if (!editor) return;

		if ((status === 'generating' || status === 'analyzing') && content.length > lastDraftContentLength) {
			// New tokens arrived — append them with ai_generated provenance
			let newText = content.slice(lastDraftContentLength);

			// On the very first token, ensure there's a space separator from existing text
			if (lastDraftContentLength === 0) {
				const docSize = editor.state.doc.content.size;
				if (docSize > 2) {
					// Get the last character of existing text (docSize - 1 is the end-of-doc boundary)
					const lastChar = editor.state.doc.textBetween(docSize - 2, docSize - 1);
					if (lastChar && !/\s/.test(lastChar)) {
						newText = ' ' + newText;
					}
				}
			}

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
		const lastAction = generationState.lastAction;

		if (status === 'idle' && insertedDraftLength > 0 && lastDraftContentLength > 0) {
			if (lastAction === 'rejected') {
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
