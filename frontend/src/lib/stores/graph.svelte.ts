import type { TreeResponse } from '$lib/types';
import { api } from '$lib/api/rest';
import { storyState } from '$lib/stores/story.svelte';

class GraphState {
	treeData = $state<TreeResponse | null>(null);
	isLoading = $state(false);
	error = $state<string | null>(null);

	async loadTree(storyId: string): Promise<void> {
		this.isLoading = true;
		this.error = null;
		try {
			this.treeData = await api.getStoryTree(storyId);
		} catch (e) {
			this.error = e instanceof Error ? e.message : String(e);
			this.treeData = null;
		} finally {
			this.isLoading = false;
		}
	}

	async switchBranch(storyId: string, targetNodeId: string): Promise<void> {
		this.error = null;
		try {
			// Switch the active path on the backend
			await api.switchActivePath(storyId, targetNodeId);
			// Refresh the story state (updates editor content)
			await storyState.refreshActiveStory();
			// Reload the tree data to reflect new active path
			await this.loadTree(storyId);
		} catch (e) {
			this.error = e instanceof Error ? e.message : String(e);
		}
	}

	clear(): void {
		this.treeData = null;
		this.error = null;
		this.isLoading = false;
	}
}

export const graphState = new GraphState();
