<script lang="ts">
	import type { LLMBackend } from '$lib/types';
	import { settingsState } from '$lib/stores/settings.svelte';
	import { storyState } from '$lib/stores/story.svelte';
	import { api } from '$lib/api/rest';

	const backends: { value: LLMBackend; label: string }[] = [
		{ value: 'lmstudio', label: 'LM Studio' },
		{ value: 'ollama', label: 'Ollama' },
		{ value: 'openai', label: 'OpenAI' },
		{ value: 'llamacpp', label: 'llama.cpp' }
	];

	const defaultUrls: Record<LLMBackend, string> = {
		lmstudio: 'http://localhost:1234/v1',
		ollama: 'http://localhost:11434',
		openai: '',
		llamacpp: 'http://localhost:8080/v1'
	};

	let isLoadingModels = $state(false);
	let modelsError = $state<string | null>(null);
	let showNewStoryForm = $state(false);
	let newStoryTitle = $state('');
	let newStoryPremise = $state('');
	let isLoadingPremise = $state(false);

	async function onBackendChange(backend: LLMBackend) {
		settingsState.backend = backend;
		// Reset connection fields to defaults for the new backend
		if (backend === 'ollama') {
			settingsState.host = defaultUrls.ollama;
		} else if (backend === 'openai') {
			settingsState.apiKey = '';
		} else {
			settingsState.baseUrl = defaultUrls[backend];
		}
		settingsState.model = '';
		settingsState.availableModels = [];
		settingsState.warmupStatus = '';
		// Save config and refresh models
		await saveConfigAndRefreshModels();
	}

	async function saveConfigAndRefreshModels() {
		const config = buildConfig();
		try {
			await api.setLLMConfig(config);
		} catch {
			// Config save failed — still try to list models
		}
		await refreshModels();
	}

	function buildConfig() {
		const backend = settingsState.backend;
		return {
			backend,
			base_url: backend === 'lmstudio' || backend === 'llamacpp' ? settingsState.baseUrl : undefined,
			host: backend === 'ollama' ? settingsState.host : undefined,
			api_key: backend === 'openai' ? settingsState.apiKey : undefined
		};
	}

	async function refreshModels() {
		isLoadingModels = true;
		modelsError = null;
		try {
			const result = await api.listModels();
			settingsState.availableModels = result.models;
			modelsError = result.error;
			// Auto-select first model if none selected
			if (!settingsState.model && result.models.length > 0) {
				settingsState.model = result.models[0];
			}
		} catch (e) {
			modelsError = e instanceof Error ? e.message : String(e);
			settingsState.availableModels = [];
		} finally {
			isLoadingModels = false;
		}
	}

	async function warmup() {
		if (!settingsState.model) return;
		settingsState.isWarmingUp = true;
		settingsState.warmupStatus = 'Warming up...';
		try {
			const result = await api.warmupModel(settingsState.model);
			if (result.success) {
				settingsState.warmupStatus = `Ready (${result.elapsed.toFixed(1)}s)`;
			} else {
				settingsState.warmupStatus = `Failed: ${result.message}`;
			}
		} catch (e) {
			settingsState.warmupStatus = `Error: ${e instanceof Error ? e.message : String(e)}`;
		} finally {
			settingsState.isWarmingUp = false;
		}
	}

	async function createStory() {
		if (!newStoryTitle.trim() || !newStoryPremise.trim()) return;
		await storyState.createStory(newStoryTitle.trim(), newStoryPremise.trim());
		newStoryTitle = '';
		newStoryPremise = '';
		showNewStoryForm = false;
	}

	async function feelingLucky() {
		isLoadingPremise = true;
		try {
			const premise = await api.randomPremise();
			newStoryPremise = premise;
			// Auto-generate a title from the premise: use text before the em dash,
			// or the first 6 words, truncated to a clean title
			const dashIdx = premise.indexOf(' — ');
			if (dashIdx > 0 && dashIdx <= 80) {
				newStoryTitle = premise.slice(0, dashIdx);
			} else {
				const words = premise.split(/\s+/).slice(0, 6);
				newStoryTitle = words.join(' ').replace(/[.,;:!?]+$/, '') + '...';
			}
		} catch {
			// Silently fail — user can still type manually
		} finally {
			isLoadingPremise = false;
		}
	}

	// Load stories on mount
	$effect(() => {
		storyState.loadStories();
	});
</script>

<!-- LLM Configuration Section -->
<div class="section">
	<h4 class="section-title">LLM Backend</h4>

	<!-- Backend selector -->
	<div class="field">
		<label class="field-label" for="backend-select">Backend</label>
		<select
			id="backend-select"
			class="input"
			value={settingsState.backend}
			onchange={(e) => onBackendChange(e.currentTarget.value as LLMBackend)}
		>
			{#each backends as b}
				<option value={b.value}>{b.label}</option>
			{/each}
		</select>
	</div>

	<!-- Connection fields (conditional on backend) -->
	{#if settingsState.backend === 'lmstudio' || settingsState.backend === 'llamacpp'}
		<div class="field">
			<label class="field-label" for="base-url">Base URL</label>
			<input
				id="base-url"
				type="text"
				class="input"
				bind:value={settingsState.baseUrl}
				placeholder={defaultUrls[settingsState.backend]}
				onblur={saveConfigAndRefreshModels}
			/>
		</div>
	{:else if settingsState.backend === 'ollama'}
		<div class="field">
			<label class="field-label" for="ollama-host">Host</label>
			<input
				id="ollama-host"
				type="text"
				class="input"
				bind:value={settingsState.host}
				placeholder="http://localhost:11434"
				onblur={saveConfigAndRefreshModels}
			/>
		</div>
	{:else if settingsState.backend === 'openai'}
		<div class="field">
			<label class="field-label" for="api-key">API Key</label>
			<input
				id="api-key"
				type="password"
				class="input"
				bind:value={settingsState.apiKey}
				placeholder="sk-..."
				onblur={saveConfigAndRefreshModels}
			/>
		</div>
	{/if}

	<!-- Model selector -->
	<div class="field">
		<label class="field-label" for="model-select">Model</label>
		<div class="model-row">
			<select
				id="model-select"
				class="input model-select"
				bind:value={settingsState.model}
				disabled={settingsState.availableModels.length === 0}
			>
				{#if settingsState.availableModels.length === 0}
					<option value="">No models available</option>
				{/if}
				{#each settingsState.availableModels as m}
					<option value={m}>{m}</option>
				{/each}
			</select>
			<button
				class="btn btn-small"
				onclick={refreshModels}
				disabled={isLoadingModels}
				title="Refresh model list"
			>
				{isLoadingModels ? '...' : '\u21BB'}
			</button>
		</div>
		{#if modelsError}
			<p class="error-text">{modelsError}</p>
		{/if}
	</div>

	<!-- Warmup button -->
	<div class="field">
		<button
			class="btn btn-primary"
			onclick={warmup}
			disabled={!settingsState.model || settingsState.isWarmingUp}
		>
			{settingsState.isWarmingUp ? 'Warming up...' : 'Warm Up Model'}
		</button>
		{#if settingsState.warmupStatus}
			<p class="status-text" class:success={settingsState.warmupStatus.startsWith('Ready')}>
				{settingsState.warmupStatus}
			</p>
		{/if}
	</div>
</div>

<!-- Story Management Section -->
<div class="section">
	<h4 class="section-title">Stories</h4>

	<!-- New Story button / form -->
	{#if showNewStoryForm}
		<div class="new-story-form">
			<input
				type="text"
				class="input"
				bind:value={newStoryTitle}
				placeholder="Story title"
			/>
		<textarea
			class="input textarea"
			bind:value={newStoryPremise}
			placeholder="Story premise..."
			rows="3"
		></textarea>
		<button
			class="btn btn-lucky btn-small"
			onclick={feelingLucky}
			disabled={isLoadingPremise}
			title="Fill with a random story premise"
		>
			{isLoadingPremise ? 'Rolling...' : "I'm Feeling Lucky"}
		</button>
		<div class="form-actions">
				<button class="btn btn-primary btn-small" onclick={createStory} disabled={storyState.isLoading}>
					{storyState.isLoading ? 'Creating...' : 'Create'}
				</button>
				<button class="btn btn-small" onclick={() => (showNewStoryForm = false)}>Cancel</button>
			</div>
		</div>
	{:else}
		<button class="btn btn-primary" onclick={() => (showNewStoryForm = true)}>
			+ New Story
		</button>
	{/if}

	{#if storyState.error}
		<p class="error-text">{storyState.error}</p>
	{/if}

	<!-- Story list -->
	<div class="story-list">
		{#each storyState.stories as story (story.id)}
			<div
				class="story-item"
				class:active={storyState.activeStoryId === story.id}
				role="button"
				tabindex="0"
				onclick={() => storyState.setActiveStory(story.id)}
				onkeydown={(e) => e.key === 'Enter' && storyState.setActiveStory(story.id)}
			>
				<div class="story-info">
					<span class="story-title">{story.title}</span>
					<span class="story-date">{new Date(story.updated_at || story.created_at).toLocaleDateString()}</span>
				</div>
				<button
					class="delete-btn"
					onclick={(e) => { e.stopPropagation(); storyState.deleteStory(story.id); }}
					title="Delete story"
				>
					\u2715
				</button>
			</div>
		{/each}
		{#if storyState.stories.length === 0 && !storyState.isLoading}
			<p class="empty-text">No stories yet</p>
		{/if}
	</div>
</div>

<style>
	.section {
		margin-bottom: 20px;
	}

	.section-title {
		margin: 0 0 10px 0;
		font-size: 11px;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--text-muted, #9ca3af);
	}

	.field {
		margin-bottom: 10px;
	}

	.field-label {
		display: block;
		font-size: 12px;
		color: var(--text-muted, #9ca3af);
		margin-bottom: 4px;
	}

	.input {
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

	.input:focus {
		border-color: #6366f1;
	}

	.textarea {
		resize: vertical;
		min-height: 60px;
		font-family: inherit;
	}

	.model-row {
		display: flex;
		gap: 4px;
	}

	.model-select {
		flex: 1;
	}

	.btn {
		padding: 6px 12px;
		font-size: 13px;
		border: 1px solid var(--border-color, #374151);
		border-radius: 4px;
		background-color: var(--panel-bg, #030712);
		color: var(--text-primary, #e5e7eb);
		cursor: pointer;
		transition: background-color 150ms ease;
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
		padding: 4px 8px;
		font-size: 12px;
	}

	.btn-lucky {
		width: 100%;
		border-style: dashed;
		color: var(--text-muted, #9ca3af);
	}

	.btn-lucky:hover:not(:disabled) {
		border-color: #6366f1;
		color: #a5b4fc;
	}

	.error-text {
		font-size: 11px;
		color: #ef4444;
		margin: 4px 0 0 0;
	}

	.status-text {
		font-size: 11px;
		color: var(--text-muted, #9ca3af);
		margin: 4px 0 0 0;
	}

	.status-text.success {
		color: #22c55e;
	}

	.new-story-form {
		display: flex;
		flex-direction: column;
		gap: 6px;
		margin-bottom: 10px;
	}

	.form-actions {
		display: flex;
		gap: 6px;
	}

	.story-list {
		margin-top: 10px;
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.story-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 6px 8px;
		border-radius: 4px;
		cursor: pointer;
		transition: background-color 150ms ease;
	}

	.story-item:hover {
		background-color: var(--hover-bg, #1f2937);
	}

	.story-item.active {
		background-color: #1e1b4b;
		border: 1px solid #4f46e5;
	}

	.story-info {
		display: flex;
		flex-direction: column;
		gap: 2px;
		min-width: 0;
		flex: 1;
	}

	.story-title {
		font-size: 13px;
		color: var(--text-primary, #e5e7eb);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.story-date {
		font-size: 11px;
		color: var(--text-faint, #6b7280);
	}

	.delete-btn {
		background: none;
		border: none;
		color: var(--text-faint, #6b7280);
		cursor: pointer;
		font-size: 12px;
		padding: 2px 4px;
		border-radius: 2px;
		flex-shrink: 0;
	}

	.delete-btn:hover {
		color: #ef4444;
		background-color: rgba(239, 68, 68, 0.1);
	}

	.empty-text {
		font-size: 12px;
		color: var(--text-faint, #6b7280);
		font-style: italic;
		margin: 4px 0;
	}
</style>
