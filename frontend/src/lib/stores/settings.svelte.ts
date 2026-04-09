import type { LLMBackend } from '$lib/types';

class SettingsState {
	backend = $state<LLMBackend>('lmstudio');
	model = $state<string>('');
	baseUrl = $state<string>('http://localhost:1234/v1');
	host = $state<string>('http://localhost:11434');
	apiKey = $state<string>('');
	availableModels = $state.raw<string[]>([]);
	isWarmingUp = $state(false);
	warmupStatus = $state<string>('');
}

export const settingsState = new SettingsState();
