<script lang="ts">
	import type { StoryOverviewStory } from '$lib/types';
	import { storyState } from '$lib/stores/story.svelte';

	let {
		story,
		batchMode = false,
		selected = false,
		onselect,
		ondelete,
		onedit,
		onenterbatch,
	}: {
		story: StoryOverviewStory;
		batchMode?: boolean;
		selected?: boolean;
		onselect?: (id: string, multi: boolean) => void;
		ondelete?: (id: string) => void;
		onedit?: (id: string, title: string, premise: string) => void;
		onenterbatch?: () => void;
	} = $props();

	let isFlipped = $state(false);
	let isEditing = $state(false);
	let editTitle = $state('');
	let editPremise = $state('');
	let longPressTimer: ReturnType<typeof setTimeout> | null = $state(null);

	function handleOpen(): void {
		if (batchMode) {
			onselect?.(story.id, false);
		} else {
			storyState.setActiveStory(story.id);
		}
	}

	function handleTrashClick(e: MouseEvent): void {
		e.stopPropagation();
		isFlipped = true;
	}

	function handleDelete(): void {
		ondelete?.(story.id);
	}

	function handleEditClick(): void {
		editTitle = story.title;
		editPremise = story.premise;
		isEditing = true;
	}

	function handleSaveEdit(): void {
		onedit?.(story.id, editTitle, editPremise);
		isEditing = false;
		isFlipped = false;
	}

	function handleCancelEdit(): void {
		isEditing = false;
	}

	function handleCancelFlip(): void {
		isFlipped = false;
		isEditing = false;
	}

	function handleSelectMultiple(): void {
		onenterbatch?.();
		isFlipped = false;
	}

	function handleCheckboxClick(e: MouseEvent): void {
		e.stopPropagation();
		onselect?.(story.id, false);
	}

	function handlePointerDown(): void {
		if (batchMode || isFlipped) return;
		longPressTimer = setTimeout(() => {
			onenterbatch?.();
			onselect?.(story.id, false);
		}, 300);
	}

	function handlePointerUp(): void {
		if (longPressTimer) {
			clearTimeout(longPressTimer);
			longPressTimer = null;
		}
	}

	function handlePointerMove(): void {
		if (longPressTimer) {
			clearTimeout(longPressTimer);
			longPressTimer = null;
		}
	}

	function handleKeydown(e: KeyboardEvent): void {
		if (e.key === 'Escape') {
			isFlipped = false;
			isEditing = false;
		}
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

	// Click outside to unflip
	$effect(() => {
		if (isFlipped) {
			const container = document.querySelector('.story-card-container.flipped');
			const handler = (e: MouseEvent) => {
				if (container && !container.contains(e.target as Node)) {
					isFlipped = false;
					isEditing = false;
				}
			};
			document.addEventListener('mousedown', handler);
			return () => document.removeEventListener('mousedown', handler);
		}
	});
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
	class="story-card-container"
	class:flipped={isFlipped}
	class:batch-mode={batchMode}
	class:selected={selected}
	onclick={(e) => {
		if (e.shiftKey) {
			e.stopPropagation();
			onselect?.(story.id, true);
		}
	}}
	onpointerdown={handlePointerDown}
	onpointerup={handlePointerUp}
	onpointermove={handlePointerMove}
>
	<div class="card-inner">
		<!-- FRONT FACE -->
		<div class="card-front" onclick={handleOpen} role="button" tabindex="0" onkeydown={handleKeydown}>
			{#if batchMode}
				<div class="batch-checkbox" onclick={handleCheckboxClick} role="checkbox" aria-checked={selected} aria-label="Select {story.title}">
					{#if selected}
						<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
							<rect x="0.5" y="0.5" width="15" height="15" rx="3" fill="#6366f1" stroke="#6366f1" stroke-width="1"/>
							<path d="M4 8L7 11L12 5" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					{:else}
						<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
							<rect x="0.5" y="0.5" width="15" height="15" rx="3" stroke="#6b7280" stroke-width="1"/>
						</svg>
					{/if}
				</div>
			{/if}
			<div class="card-header">
				<h3 class="card-title">{story.title}</h3>
				<button class="trash-btn" onclick={handleTrashClick} aria-label="Delete story" title="Delete story">
					<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
						<path d="M2.5 3.5H13.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
						<path d="M5.5 3.5V2.5C5.5 2.22386 5.72386 2 6 2H10C10.2761 2 10.5 2.22386 10.5 2.5V3.5" stroke="currentColor" stroke-width="1.2"/>
						<path d="M4 3.5L4.5 13C4.52174 13.2761 4.72386 13.5 5 13.5H11C11.2761 13.5 11.4783 13.2761 11.5 13L12 3.5" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>
					</svg>
				</button>
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
				<span class="card-meta">{formatDate(story.updated_at || story.created_at)} · {story.node_count} paragraphs</span>
			</div>
		</div>

		<!-- BACK FACE -->
		<div class="card-back" role="dialog" aria-label="Story actions for {story.title}">
			{#if isEditing}
				<div class="edit-form">
					<label class="edit-label">Title
						<input type="text" class="edit-input" bind:value={editTitle} />
					</label>
					<label class="edit-label">Premise
						<textarea class="edit-input edit-textarea" bind:value={editPremise} rows="3"></textarea>
					</label>
					<div class="edit-actions">
						<button class="btn btn-primary btn-small" onclick={handleSaveEdit}>Save Changes</button>
						<button class="btn btn-small" onclick={handleCancelEdit}>Cancel</button>
					</div>
				</div>
			{:else}
				<div class="back-actions">
					<h3 class="back-title">Delete "{story.title}"?</h3>
					<button class="btn btn-destructive btn-small" onclick={handleDelete} aria-label="Delete story permanently">
						🗑 Delete
					</button>
					<button class="btn btn-small" onclick={handleEditClick} aria-label="Edit story title and premise">
						✏ Edit
					</button>
					<button class="btn btn-small" onclick={handleSelectMultiple} aria-label="Select multiple stories for batch actions">
						☑ Select Multiple
					</button>
				</div>
			{/if}
			{#if !isEditing}
				<button class="back-cancel" onclick={handleCancelFlip} aria-label="Cancel">✕ Cancel</button>
			{/if}
		</div>
	</div>
</div>

<style>
	.story-card-container {
		perspective: 1000px;
		min-height: 140px;
	}

	.card-inner {
		position: relative;
		transition: transform 0.4s ease-in-out;
		transform-style: preserve-3d;
	}

	.story-card-container.flipped .card-inner {
		transform: rotateY(180deg);
	}

	.card-front,
	.card-back {
		backface-visibility: hidden;
	}

	/* ---- FRONT FACE ---- */
	.card-front {
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

	.card-front:hover {
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

	.trash-btn {
		opacity: 0;
		transition: opacity 150ms ease;
		background: none;
		border: none;
		cursor: pointer;
		color: var(--text-faint, #6b7280);
		padding: 4px;
		flex-shrink: 0;
	}

	.story-card-container:not(.batch-mode) .card-front:hover .trash-btn {
		opacity: 1;
	}

	.story-card-container.batch-mode .trash-btn {
		display: none;
	}

	.trash-btn:hover {
		color: #ef4444;
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

	.card-meta {
		font-size: 11px;
		color: var(--text-faint, #6b7280);
		white-space: nowrap;
		flex-shrink: 0;
	}

	/* ---- BACK FACE ---- */
	.card-back {
		position: absolute;
		inset: 0;
		transform: rotateY(180deg);
		display: flex;
		flex-direction: column;
		justify-content: center;
		padding: 16px;
		background-color: var(--sidebar-bg, #111827);
		border: 1px solid var(--border-color, #374151);
		border-radius: 8px;
		gap: 6px;
	}

	.back-actions {
		display: flex;
		flex-direction: column;
		gap: 8px;
		align-items: stretch;
	}

	.back-title {
		margin: 0 0 8px;
		font-size: 15px;
		font-weight: 600;
		color: var(--text-primary, #e5e7eb);
	}

	.back-cancel {
		margin-top: 4px;
		background: none;
		border: none;
		color: var(--text-faint, #6b7280);
		cursor: pointer;
		font-size: 12px;
		padding: 4px 0;
		text-align: left;
	}

	.back-cancel:hover {
		color: var(--text-primary, #e5e7eb);
	}

	/* ---- BATCH MODE ---- */
	.batch-checkbox {
		position: absolute;
		top: 8px;
		left: 8px;
		z-index: 2;
		cursor: pointer;
	}

	.story-card-container.batch-mode .card-front {
		border-color: var(--border-color, #374151);
	}

	.story-card-container.selected .card-front {
		border-color: #6366f1;
		border-width: 2px;
		background-color: rgba(99, 102, 241, 0.08);
	}

	/* ---- SHARED BUTTON ---- */
	.btn {
		padding: 6px 12px;
		font-size: 13px;
		border: 1px solid var(--border-color, #374151);
		border-radius: 6px;
		background-color: var(--panel-bg, #030712);
		color: var(--text-primary, #e5e7eb);
		cursor: pointer;
		transition: background-color 150ms ease, border-color 150ms ease;
	}

	.btn:hover:not(:disabled) {
		background-color: var(--hover-bg, #1f2937);
	}

	.btn-primary {
		background-color: #4f46e5;
		border-color: #4f46e5;
		color: #fff;
	}

	.btn-primary:hover:not(:disabled) {
		background-color: #4338ca;
	}

	.btn-small {
		padding: 6px 12px;
		font-size: 13px;
	}

	.btn-destructive {
		color: #ef4444;
		border-color: #ef4444;
	}

	.btn-destructive:hover:not(:disabled) {
		background-color: #ef4444;
		color: #fff;
	}

	/* ---- EDIT FORM ---- */
	.edit-form {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.edit-label {
		font-size: 11px;
		color: var(--text-muted, #9ca3af);
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.edit-input {
		width: 100%;
		padding: 6px 8px;
		font-size: 13px;
		background-color: var(--panel-bg, #030712);
		color: var(--text-primary, #e5e7eb);
		border: 1px solid var(--border-color, #374151);
		border-radius: 4px;
		outline: none;
		box-sizing: border-box;
	}

	.edit-input:focus {
		border-color: #6366f1;
	}

	.edit-textarea {
		resize: none;
		font-family: inherit;
	}

	.edit-actions {
		display: flex;
		gap: 8px;
		margin-top: 4px;
	}
</style>
