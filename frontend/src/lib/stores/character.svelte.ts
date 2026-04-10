import type { CanonicalCharacter, CanonicalCharacterSummary, CharacterCandidateGroup, UpdateCharacterRequest } from '$lib/types';
import { api } from '$lib/api/rest';

class CharacterState {
	canonicalCharacters = $state.raw<CanonicalCharacterSummary[]>([]);
	candidates = $state.raw<CharacterCandidateGroup[]>([]);
	selectedCharacter = $state<CanonicalCharacter | null>(null);
	showMatchPanel = $state(false);
	showProfilePanel = $state(false);
	isLoading = $state(false);
	error = $state<string | null>(null);

	async loadCandidates(): Promise<void> {
		this.isLoading = true;
		this.error = null;
		try {
			const response = await api.getCharacterCandidates();
			this.candidates = response.candidates;
			this.showMatchPanel = response.candidates.length > 0;
		} catch (e) {
			this.error = e instanceof Error ? e.message : String(e);
		} finally {
			this.isLoading = false;
		}
	}

	async loadCharacters(): Promise<void> {
		try {
			this.canonicalCharacters = await api.listCharacters();
		} catch {
			// Graceful failure
		}
	}

	async confirmLink(candidateGroup: CharacterCandidateGroup, canonicalName: string): Promise<void> {
		this.error = null;
		try {
			await api.linkCharacters({
				canonical_name: canonicalName,
				mentions: candidateGroup.mentions.map(m => ({ raw_name: m.raw_name, story_id: m.story_id }))
			});
			// Reload data
			await Promise.all([this.loadCandidates(), this.loadCharacters()]);
		} catch (e) {
			this.error = e instanceof Error ? e.message : String(e);
		}
	}

	async splitGroup(canonicalId: string, mentionsToSplit: { raw_name: string; story_id: string }[]): Promise<void> {
		this.error = null;
		try {
			await api.splitCharacter(canonicalId, { canonical_id: canonicalId, mentions_to_split: mentionsToSplit });
			await Promise.all([this.loadCandidates(), this.loadCharacters()]);
		} catch (e) {
			this.error = e instanceof Error ? e.message : String(e);
		}
	}

	async selectCharacter(canonicalId: string): Promise<void> {
		this.isLoading = true;
		this.error = null;
		try {
			this.selectedCharacter = await api.getCharacter(canonicalId);
			this.showProfilePanel = true;
		} catch (e) {
			this.error = e instanceof Error ? e.message : String(e);
		} finally {
			this.isLoading = false;
		}
	}

	async updateCharacter(canonicalId: string, request: UpdateCharacterRequest): Promise<void> {
		this.error = null;
		try {
			this.selectedCharacter = await api.updateCharacter(canonicalId, request);
			await this.loadCharacters();
		} catch (e) {
			this.error = e instanceof Error ? e.message : String(e);
		}
	}

	async deleteCharacter(canonicalId: string): Promise<void> {
		this.error = null;
		try {
			await api.deleteCharacter(canonicalId);
			this.selectedCharacter = null;
			this.showProfilePanel = false;
			await Promise.all([this.loadCandidates(), this.loadCharacters()]);
		} catch (e) {
			this.error = e instanceof Error ? e.message : String(e);
		}
	}

	closeProfilePanel(): void {
		this.showProfilePanel = false;
		this.selectedCharacter = null;
	}

	closeMatchPanel(): void {
		this.showMatchPanel = false;
	}
}

export const characterState = new CharacterState();
