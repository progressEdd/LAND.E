import type { Story, StoryNode, StoryAnalysis } from '$lib/types';
import { api } from '$lib/api/rest';

class StoryState {
	stories = $state.raw<Story[]>([]);
	activeStoryId = $state<string | null>(null);
	isLoading = $state(false);
	error = $state<string | null>(null);
	lastAnalysis = $state<StoryAnalysis | null>(null);

	/** Map of story ID → full Story data (with nodes loaded) */
	private loadedStories = $state.raw<Record<string, Story>>({});

	get activeStory(): Story | null {
		if (!this.activeStoryId) return null;
		// Prefer the fully-loaded version with nodes
		return this.loadedStories[this.activeStoryId] ?? this.stories.find((s) => s.id === this.activeStoryId) ?? null;
	}

	/**
	 * Returns the nodes along the active path in order.
	 * These are the non-draft nodes that form the current story content.
	 */
	getActivePathNodes(): StoryNode[] {
		const story = this.activeStory;
		if (!story || !story.active_path || !story.nodes) return [];

		const nodeMap = new Map(story.nodes.map((n) => [n.id, n]));
		const pathNodes: StoryNode[] = [];
		for (const nodeId of story.active_path) {
			const node = nodeMap.get(nodeId);
			if (node && !node.is_draft) {
				pathNodes.push(node);
			}
		}
		return pathNodes;
	}

	async loadStories(): Promise<void> {
		this.isLoading = true;
		this.error = null;
		try {
			this.stories = await api.listStories();
		} catch (e) {
			this.error = e instanceof Error ? e.message : String(e);
		} finally {
			this.isLoading = false;
		}
	}

	/**
	 * Load a story with its full node tree and provenance spans.
	 * Caches the loaded story so subsequent calls don't re-fetch.
	 */
	async loadStory(id: string): Promise<Story | null> {
		this.isLoading = true;
		this.error = null;
		try {
			const story = await api.getStory(id);
			this.loadedStories = { ...this.loadedStories, [id]: story };
			// Also update the summary in stories array
			this.stories = this.stories.map((s) => (s.id === id ? story : s));
			return story;
		} catch (e) {
			this.error = e instanceof Error ? e.message : String(e);
			return null;
		} finally {
			this.isLoading = false;
		}
	}

	async createStory(title: string, premise: string): Promise<Story | null> {
		this.isLoading = true;
		this.error = null;
		try {
			const story = await api.createStory(title, premise);
			this.stories = [story, ...this.stories];
			this.loadedStories = { ...this.loadedStories, [story.id]: story };
			this.activeStoryId = story.id;
			this.lastAnalysis = null;
			return story;
		} catch (e) {
			this.error = e instanceof Error ? e.message : String(e);
			return null;
		} finally {
			this.isLoading = false;
		}
	}

	async deleteStory(id: string): Promise<void> {
		this.error = null;
		try {
			await api.deleteStory(id);
			this.stories = this.stories.filter((s) => s.id !== id);
			const { [id]: _, ...rest } = this.loadedStories;
			this.loadedStories = rest;
			if (this.activeStoryId === id) {
				this.activeStoryId = this.stories.length > 0 ? this.stories[0].id : null;
				this.lastAnalysis = null;
			}
		} catch (e) {
			this.error = e instanceof Error ? e.message : String(e);
		}
	}

	/**
	 * Set the active story and load its full data if not already loaded.
	 */
	async setActiveStory(id: string): Promise<void> {
		this.activeStoryId = id;
		this.lastAnalysis = null;
		// Load full story data if we don't have it yet (or if it has no nodes)
		const cached = this.loadedStories[id];
		if (!cached || !cached.nodes || cached.nodes.length === 0) {
			await this.loadStory(id);
		}
	}

	/**
	 * Clear the active story and return to dashboard.
	 */
	clearActiveStory(): void {
		this.activeStoryId = null;
		this.lastAnalysis = null;
	}

	/**
	 * Refresh the active story data from the server (e.g., after accepting a node).
	 */
	async refreshActiveStory(): Promise<void> {
		if (!this.activeStoryId) return;
		await this.loadStory(this.activeStoryId);
	}
}

export const storyState = new StoryState();
