<script lang="ts">
	import type { LLMBackend } from '$lib/types';
	import { settingsState } from '$lib/stores/settings.svelte';
	import { generationState } from '$lib/stores/generation.svelte';
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

	function handleReconnect() {
		generationState.reconnect();
	}
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

	<!-- Reconnect button -->
	<div class="field">
		<button class="btn btn-primary" onclick={handleReconnect}>
			Reconnect WebSocket
		</button>
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
</style>
