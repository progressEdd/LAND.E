import type { Story } from '$lib/types';
import { api } from '$lib/api/rest';

class StoryState {
	stories = $state.raw<Story[]>([]);
	activeStoryId = $state<string | null>(null);
	isLoading = $state(false);
	error = $state<string | null>(null);

	get activeStory(): Story | null {
		return this.stories.find((s) => s.id === this.activeStoryId) ?? null;
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

	async createStory(title: string, premise: string): Promise<Story | null> {
		this.isLoading = true;
		this.error = null;
		try {
			const story = await api.createStory(title, premise);
			this.stories = [story, ...this.stories];
			this.activeStoryId = story.id;
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
			if (this.activeStoryId === id) {
				this.activeStoryId = this.stories.length > 0 ? this.stories[0].id : null;
			}
		} catch (e) {
			this.error = e instanceof Error ? e.message : String(e);
		}
	}

	setActiveStory(id: string): void {
		this.activeStoryId = id;
	}
}

export const storyState = new StoryState();
