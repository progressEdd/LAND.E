import type {
	Story,
	StoryNode,
	LLMConfig,
	NodeType,
	ProvenanceSource,
	TreeResponse,
	StoryOverviewResponse,
	CanonicalCharacter,
	CanonicalCharacterSummary,
	CharacterCandidateGroup,
	LinkCharactersRequest,
	SplitCharactersRequest,
	UpdateCharacterRequest
} from '$lib/types';

/**
 * Typed REST API client for the FastAPI backend.
 * Uses Vite proxy so all URLs are relative (no base URL needed).
 */
class ApiClient {
	private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
		const res = await fetch(path, {
			headers: {
				'Content-Type': 'application/json',
				...options.headers
			},
			...options
		});

		if (!res.ok) {
			const detail = await res.text().catch(() => res.statusText);
			throw new Error(`API error ${res.status}: ${detail}`);
		}

		// Handle 204 No Content
		if (res.status === 204) {
			return undefined as T;
		}

		return res.json();
	}

	// ---------- Stories ----------

	async randomPremise(): Promise<string> {
		const result = await this.request<{ premise: string }>('/api/stories/random-premise');
		return result.premise;
	}

	async createStory(title: string, premise: string): Promise<Story> {
		return this.request<Story>('/api/stories', {
			method: 'POST',
			body: JSON.stringify({ title, premise })
		});
	}

	async listStories(): Promise<Story[]> {
		return this.request<Story[]>('/api/stories');
	}

	async getStoriesOverview(): Promise<StoryOverviewResponse> {
		return this.request<StoryOverviewResponse>('/api/stories/overview');
	}

	async getStory(id: string): Promise<Story> {
		return this.request<Story>(`/api/stories/${id}`);
	}

	async deleteStory(id: string): Promise<void> {
		return this.request<void>(`/api/stories/${id}`, {
			method: 'DELETE'
		});
	}

	// ---------- Nodes ----------

	async createNode(
		storyId: string,
		parentId: string,
		content: string,
		nodeType: NodeType,
		source: ProvenanceSource
	): Promise<StoryNode> {
		return this.request<StoryNode>(`/api/stories/${storyId}/nodes`, {
			method: 'POST',
			body: JSON.stringify({
				parent_id: parentId,
				content,
				node_type: nodeType,
				source
			})
		});
	}

	async updateNode(
		storyId: string,
		nodeId: string,
		content: string,
		spans: { start_offset: number; end_offset: number; source: ProvenanceSource }[]
	): Promise<StoryNode> {
		return this.request<StoryNode>(`/api/stories/${storyId}/nodes/${nodeId}`, {
			method: 'PATCH',
			body: JSON.stringify({
				content,
				provenance_spans: spans
			})
		});
	}

	async acceptNode(storyId: string, nodeId: string): Promise<StoryNode> {
		return this.request<StoryNode>(`/api/stories/${storyId}/nodes/${nodeId}/accept`, {
			method: 'POST'
		});
	}

	async rejectNode(storyId: string, nodeId: string): Promise<void> {
		return this.request<void>(`/api/stories/${storyId}/nodes/${nodeId}/reject`, {
			method: 'POST'
		});
	}

	// ---------- Graph / Tree ----------

	async getStoryTree(storyId: string): Promise<TreeResponse> {
		return this.request<TreeResponse>(`/api/stories/${storyId}/tree`);
	}

	async switchActivePath(storyId: string, targetNodeId: string): Promise<Story> {
		return this.request<Story>(`/api/stories/${storyId}/active-path`, {
			method: 'PATCH',
			body: JSON.stringify({ target_node_id: targetNodeId })
		});
	}

	// ---------- LLM Config ----------

	async getLLMConfig(): Promise<LLMConfig> {
		return this.request<LLMConfig>('/api/llm/config');
	}

	async setLLMConfig(config: LLMConfig): Promise<LLMConfig> {
		return this.request<LLMConfig>('/api/llm/config', {
			method: 'POST',
			body: JSON.stringify(config)
		});
	}

	async listModels(): Promise<{ models: string[]; error: string | null }> {
		return this.request<{ models: string[]; error: string | null }>('/api/llm/models');
	}

	async warmupModel(model: string): Promise<{ success: boolean; message: string; elapsed: number }> {
		return this.request<{ success: boolean; message: string; elapsed: number }>('/api/llm/warmup', {
			method: 'POST',
			body: JSON.stringify({ model })
		});
	}

	// ---------- Characters ----------

	async getCharacterCandidates(): Promise<{ candidates: CharacterCandidateGroup[] }> {
		return this.request<{ candidates: CharacterCandidateGroup[] }>('/api/characters/candidates');
	}

	async linkCharacters(request: LinkCharactersRequest): Promise<CanonicalCharacter> {
		return this.request<CanonicalCharacter>('/api/characters/link', {
			method: 'POST',
			body: JSON.stringify(request)
		});
	}

	async splitCharacter(canonicalId: string, request: SplitCharactersRequest): Promise<{ original: CanonicalCharacterSummary; new: CanonicalCharacterSummary }> {
		return this.request<{ original: CanonicalCharacterSummary; new: CanonicalCharacterSummary }>(`/api/characters/${canonicalId}/split`, {
			method: 'POST',
			body: JSON.stringify(request)
		});
	}

	async listCharacters(): Promise<CanonicalCharacterSummary[]> {
		return this.request<CanonicalCharacterSummary[]>('/api/characters');
	}

	async getCharacter(canonicalId: string): Promise<CanonicalCharacter> {
		return this.request<CanonicalCharacter>(`/api/characters/${canonicalId}`);
	}

	async updateCharacter(canonicalId: string, request: UpdateCharacterRequest): Promise<CanonicalCharacter> {
		return this.request<CanonicalCharacter>(`/api/characters/${canonicalId}`, {
			method: 'PATCH',
			body: JSON.stringify(request)
		});
	}

	async linkMention(canonicalId: string, rawName: string, storyId: string): Promise<CanonicalCharacter> {
		return this.request<CanonicalCharacter>(`/api/characters/${canonicalId}/link-mention`, {
			method: 'POST',
			body: JSON.stringify({ raw_name: rawName, story_id: storyId, canonical_id: canonicalId })
		});
	}

	async deleteCharacter(canonicalId: string): Promise<void> {
		return this.request<void>(`/api/characters/${canonicalId}`, {
			method: 'DELETE'
		});
	}
}

export const api = new ApiClient();
