import type {
	Story,
	StoryNode,
	LLMConfig,
	NodeType,
	ProvenanceSource
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
}

export const api = new ApiClient();
