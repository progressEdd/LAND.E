<script lang="ts">
	import { editorState } from '$lib/stores/editor.svelte';
	import { storyState } from '$lib/stores/story.svelte';

	type ToolbarButton = {
		label: string;
		title: string;
		action: () => void;
		isActive: () => boolean;
		isDisabled?: () => boolean;
	};

	const formatButtons: ToolbarButton[] = [
		{
			label: 'B',
			title: 'Bold (Ctrl+B)',
			action: () => editorState.editor?.chain().focus().toggleBold().run(),
			isActive: () => editorState.isBold
		},
		{
			label: 'I',
			title: 'Italic (Ctrl+I)',
			action: () => editorState.editor?.chain().focus().toggleItalic().run(),
			isActive: () => editorState.isItalic
		},
		{
			label: 'S',
			title: 'Strikethrough',
			action: () => editorState.editor?.chain().focus().toggleStrike().run(),
			isActive: () => editorState.isStrike
		}
	];

	const headingButtons: ToolbarButton[] = [
		{
			label: 'H1',
			title: 'Heading 1',
			action: () => editorState.editor?.chain().focus().toggleHeading({ level: 1 }).run(),
			isActive: () => editorState.isHeading1
		},
		{
			label: 'H2',
			title: 'Heading 2',
			action: () => editorState.editor?.chain().focus().toggleHeading({ level: 2 }).run(),
			isActive: () => editorState.isHeading2
		},
		{
			label: 'H3',
			title: 'Heading 3',
			action: () => editorState.editor?.chain().focus().toggleHeading({ level: 3 }).run(),
			isActive: () => editorState.isHeading3
		}
	];

	const blockButtons: ToolbarButton[] = [
		{
			label: '•',
			title: 'Bullet List',
			action: () => editorState.editor?.chain().focus().toggleBulletList().run(),
			isActive: () => editorState.isBulletList
		},
		{
			label: '1.',
			title: 'Ordered List',
			action: () => editorState.editor?.chain().focus().toggleOrderedList().run(),
			isActive: () => editorState.isOrderedList
		},
		{
			label: '"',
			title: 'Blockquote',
			action: () => editorState.editor?.chain().focus().toggleBlockquote().run(),
			isActive: () => editorState.isBlockquote
		},
		{
			label: '</>',
			title: 'Code Block',
			action: () => editorState.editor?.chain().focus().toggleCodeBlock().run(),
			isActive: () => editorState.isCodeBlock
		}
	];

	const historyButtons: ToolbarButton[] = [
		{
			label: '↩',
			title: 'Undo (Ctrl+Z)',
			action: () => editorState.editor?.chain().focus().undo().run(),
			isActive: () => false,
			isDisabled: () => !editorState.canUndo
		},
		{
			label: '↪',
			title: 'Redo (Ctrl+Shift+Z)',
			action: () => editorState.editor?.chain().focus().redo().run(),
			isActive: () => false,
			isDisabled: () => !editorState.canRedo
		}
	];

	let activeStoryTitle = $derived(storyState.activeStory?.title ?? '');
</script>

<div class="toolbar">
	<button
		class="toolbar-btn home-btn"
		onclick={() => storyState.clearActiveStory()}
		title="Back to Dashboard (Home)"
	>
		&#x2302;
	</button>
	<div class="separator"></div>
	{#if activeStoryTitle}
		<span class="story-title-breadcrumb">{activeStoryTitle}</span>
		<div class="separator"></div>
	{/if}

	<div class="button-group">
		{#each formatButtons as btn}
			<button
				class="toolbar-btn"
				class:active={btn.isActive()}
				title={btn.title}
				onclick={btn.action}
				disabled={!editorState.editor}
			>
				{#if btn.label === 'B'}
					<strong>{btn.label}</strong>
				{:else if btn.label === 'I'}
					<em>{btn.label}</em>
				{:else if btn.label === 'S'}
					<s>{btn.label}</s>
				{:else}
					{btn.label}
				{/if}
			</button>
		{/each}
	</div>

	<div class="separator"></div>

	<div class="button-group">
		{#each headingButtons as btn}
			<button
				class="toolbar-btn"
				class:active={btn.isActive()}
				title={btn.title}
				onclick={btn.action}
				disabled={!editorState.editor}
			>
				{btn.label}
			</button>
		{/each}
	</div>

	<div class="separator"></div>

	<div class="button-group">
		{#each blockButtons as btn}
			<button
				class="toolbar-btn"
				class:active={btn.isActive()}
				title={btn.title}
				onclick={btn.action}
				disabled={!editorState.editor}
			>
				{btn.label}
			</button>
		{/each}
	</div>

	<div class="separator"></div>

	<div class="button-group">
		{#each historyButtons as btn}
			<button
				class="toolbar-btn"
				class:active={btn.isActive()}
				title={btn.title}
				onclick={btn.action}
				disabled={!editorState.editor || btn.isDisabled?.()}
			>
				{btn.label}
			</button>
		{/each}
	</div>
</div>

<style>
	.toolbar {
		display: flex;
		align-items: center;
		gap: 4px;
		padding: 6px 12px;
		background-color: var(--sidebar-bg, #111827);
		border-bottom: 1px solid var(--border-color, #374151);
		flex-shrink: 0;
	}

	.button-group {
		display: flex;
		gap: 2px;
	}

	.separator {
		width: 1px;
		height: 20px;
		background-color: var(--border-color, #374151);
		margin: 0 4px;
	}

	.toolbar-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		min-width: 28px;
		height: 28px;
		padding: 0 6px;
		border: none;
		border-radius: 4px;
		background: transparent;
		color: var(--text-secondary, #d1d5db);
		font-size: 12px;
		font-family: inherit;
		cursor: pointer;
		transition:
			background-color 100ms ease,
			color 100ms ease;
	}

	.toolbar-btn:hover:not(:disabled) {
		background-color: var(--hover-bg, #1f2937);
		color: var(--text-primary, #e5e7eb);
	}

	.toolbar-btn.active {
		background-color: #374151;
		color: #a5b4fc;
	}

	.toolbar-btn:disabled {
		opacity: 0.3;
		cursor: default;
	}

	.home-btn {
		font-size: 16px;
		color: var(--text-muted, #9ca3af);
	}

	.home-btn:hover {
		color: #a5b4fc;
	}

	.story-title-breadcrumb {
		font-size: 13px;
		font-weight: 600;
		color: var(--text-primary, #e5e7eb);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		max-width: 200px;
	}
</style>
