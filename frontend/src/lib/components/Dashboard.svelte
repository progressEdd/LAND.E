<script lang="ts">
	import { onMount } from 'svelte';
	import StoryCard from './StoryCard.svelte';
	import { storyState } from '$lib/stores/story.svelte';
	import { api } from '$lib/api/rest';
	import type { StoryOverviewStory } from '$lib/types';

	let overviewStories = $state<StoryOverviewStory[]>([]);
	let isLoading = $state(true);
	let showCreateForm = $state(false);
	let newTitle = $state('');
	let newPremise = $state('');
	let isCreating = $state(false);
	let isLoadingPremise = $state(false);

	async function loadOverview(): Promise<void> {
		isLoading = true;
		try {
			const response = await api.getStoriesOverview();
			overviewStories = response.stories;
		} catch {
			// Overview endpoint may fail — fall back gracefully
			overviewStories = [];
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		loadOverview();
	});

	async function feelingLucky(): Promise<void> {
		isLoadingPremise = true;
		try {
			const premise = await api.randomPremise();
			newPremise = premise;
			// Auto-generate title from premise
			const dashIdx = premise.indexOf(' — ');
			if (dashIdx > 0 && dashIdx <= 80) {
				newTitle = premise.slice(0, dashIdx);
			} else {
				const words = premise.split(/\s+/).slice(0, 6);
				newTitle = words.join(' ').replace(/[.,;:!?]+$/, '') + '...';
			}
			showCreateForm = true;
		} catch {
			// Silently fail
		} finally {
			isLoadingPremise = false;
		}
	}

	async function createStory(): Promise<void> {
		if (!newTitle.trim() || !newPremise.trim()) return;
		isCreating = true;
		try {
			await storyState.createStory(newTitle.trim(), newPremise.trim());
			// createStory auto-sets activeStoryId → triggers editor view (D-08: instant switch)
		} finally {
			isCreating = false;
		}
	}

	function cancelCreate(): void {
		showCreateForm = false;
		newTitle = '';
		newPremise = '';
	}
</script>

<div class="dashboard">
	{#if isLoading}
		<div class="loading-state">
			<div class="spinner"></div>
			<p>Loading stories...</p>
		</div>
	{:else if overviewStories.length === 0 && !showCreateForm}
		<!-- Empty state (D-11, D-13) -->
		<div class="empty-state">
			<h2 class="empty-title">Welcome to AI Story Writer</h2>
			<p class="empty-text">Create your first story to get started.</p>
			<div class="empty-actions">
				<button class="btn btn-primary" onclick={() => (showCreateForm = true)}>
					Create Your First Story
				</button>
				<button class="btn btn-lucky" onclick={feelingLucky} disabled={isLoadingPremise}>
					{isLoadingPremise ? 'Rolling...' : "I'm Feeling Lucky"}
				</button>
			</div>
		</div>
	{:else}
		<!-- Story grid with featured + grid layout (D-01) -->
		<div class="dashboard-content">
			<div class="dashboard-header">
				<h2 class="dashboard-title">Your Stories</h2>
				<div class="header-actions">
					{#if !showCreateForm}
						<button class="btn btn-primary btn-small" onclick={() => (showCreateForm = true)}>
							+ New Story
						</button>
						<button class="btn btn-lucky-inline" onclick={feelingLucky} disabled={isLoadingPremise}>
							{isLoadingPremise ? '...' : '\uD83C\uDFB0'}
						</button>
					{/if}
				</div>
			</div>

			{#if showCreateForm}
				<div class="create-card">
					<input
						type="text"
						class="input"
						bind:value={newTitle}
						placeholder="Story title"
					/>
					<textarea
						class="input textarea"
						bind:value={newPremise}
						placeholder="Story premise..."
						rows="3"
					></textarea>
					<div class="create-actions">
						<button class="btn btn-lucky btn-small" onclick={feelingLucky} disabled={isLoadingPremise}>
							{isLoadingPremise ? 'Rolling...' : "I'm Feeling Lucky"}
						</button>
						<div class="create-submit">
							<button class="btn btn-primary btn-small" onclick={createStory} disabled={isCreating || !newTitle.trim() || !newPremise.trim()}>
								{isCreating ? 'Creating...' : 'Create Story'}
							</button>
							<button class="btn btn-small" onclick={cancelCreate}>Cancel</button>
						</div>
					</div>
				</div>
			{/if}

			{#if overviewStories.length > 0}
				<div class="story-grid">
					{#each overviewStories as story (story.id)}
						<StoryCard {story} />
					{/each}
				</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	.dashboard {
		height: 100%;
		width: 100%;
		padding: 32px;
		box-sizing: border-box;
		overflow-y: auto;
		background-color: var(--panel-bg, #030712);
	}

	/* ---- Loading state ---- */
	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		gap: 12px;
		color: var(--text-muted, #9ca3af);
	}

	.spinner {
		width: 28px;
		height: 28px;
		border: 2px solid var(--text-faint, #6b7280);
		border-top-color: var(--text-primary, #e5e7eb);
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}

	/* ---- Empty state ---- */
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		text-align: center;
		gap: 16px;
	}

	.empty-title {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--text-primary, #e5e7eb);
		margin: 0;
	}

	.empty-text {
		font-size: 15px;
		color: var(--text-muted, #9ca3af);
		margin: 0;
	}

	.empty-actions {
		display: flex;
		gap: 12px;
		margin-top: 8px;
	}

	/* ---- Dashboard content ---- */
	.dashboard-content {
		max-width: 1200px;
		margin: 0 auto;
	}

	.dashboard-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 24px;
	}

	.dashboard-title {
		font-size: 1.25rem;
		font-weight: 700;
		color: var(--text-primary, #e5e7eb);
		margin: 0;
	}

	.header-actions {
		display: flex;
		gap: 8px;
	}

	/* ---- Story grid ---- */
	.story-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
		gap: 16px;
	}

	/* ---- Create card ---- */
	.create-card {
		display: flex;
		flex-direction: column;
		gap: 8px;
		padding: 16px;
		margin-bottom: 20px;
		background-color: var(--sidebar-bg, #111827);
		border: 2px dashed var(--border-color, #374151);
		border-radius: 8px;
	}

	.create-actions {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.create-submit {
		display: flex;
		gap: 8px;
	}

	/* ---- Shared button styles ---- */
	.btn {
		padding: 8px 16px;
		font-size: 14px;
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

	.btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
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

	.btn-lucky {
		border-style: dashed;
		color: var(--text-muted, #9ca3af);
	}

	.btn-lucky:hover:not(:disabled) {
		border-color: #6366f1;
		color: #a5b4fc;
	}

	.btn-lucky-inline {
		padding: 6px 10px;
		font-size: 16px;
		border: 1px solid var(--border-color, #374151);
		border-radius: 6px;
		background-color: var(--panel-bg, #030712);
		cursor: pointer;
		transition: background-color 150ms ease;
	}

	.btn-lucky-inline:hover:not(:disabled) {
		background-color: var(--hover-bg, #1f2937);
	}

	.btn-lucky-inline:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	/* ---- Shared input styles ---- */
	.input {
		width: 100%;
		padding: 8px 10px;
		font-size: 14px;
		background-color: var(--panel-bg, #030712);
		color: var(--text-primary, #e5e7eb);
		border: 1px solid var(--border-color, #374151);
		border-radius: 4px;
		outline: none;
		box-sizing: border-box;
	}

	.input:focus {
		border-color: #6366f1;
	}

	.textarea {
		resize: vertical;
		min-height: 70px;
		font-family: inherit;
	}
</style>
