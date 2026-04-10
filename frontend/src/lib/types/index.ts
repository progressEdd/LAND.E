// Provenance source types for text origin tracking
export type ProvenanceSource = 'ai_generated' | 'user_written' | 'user_edited' | 'initial_prompt';

// Story tree node granularity
export type NodeType = 'paragraph' | 'block' | 'sentence';

// Supported LLM backends
export type LLMBackend = 'lmstudio' | 'ollama' | 'openai' | 'llamacpp';

// A provenance span tracking text origin within a node
export interface ProvenanceSpan {
	start_offset: number;
	end_offset: number;
	source: ProvenanceSource;
}

// A character mention linked to a node
export interface CharacterMention {
	character_name: string;
	role: string | null;
}

// A node in the story tree (paragraph, block, or sentence)
export interface StoryNode {
	id: string;
	story_id: string;
	parent_id: string | null;
	position: number;
	content: string;
	node_type: NodeType;
	source: ProvenanceSource;
	is_draft: boolean;
	created_at: string;
	provenance_spans: ProvenanceSpan[];
	character_mentions: CharacterMention[];
	analysis: StoryAnalysis | null;
}

// A story with its tree of nodes
export interface Story {
	id: string;
	title: string;
	premise: string;
	created_at: string;
	updated_at: string;
	active_path: string[];
	nodes: StoryNode[];
}

// LLM backend configuration
export interface LLMConfig {
	backend: LLMBackend;
	base_url?: string;
	host?: string;
	api_key?: string;
}

// Structured story analysis from LLM
export interface StoryAnalysis {
	logline: string;
	cast: string[];
	world_rules: string[];
	pov_tense_tone: string;
	timeline: string[];
	current_situation: string;
	active_threads: string[];
	continuity_landmines: string[];
	ambiguities: string[];
	next_paragraph_seeds: string[];
}

// ---------- Graph visualizer types ----------

// Aggregated character data for supernode rendering
export interface CharacterSummary {
	name: string;
	node_ids: string[];
}

// A tree node with recursive children (for graph visualizer)
export interface TreeNode extends StoryNode {
	children: TreeNode[];
}

// Full tree response from the /tree endpoint
export interface TreeResponse {
	story_id: string;
	title: string;
	premise: string;
	active_path: string[];
	root: TreeNode | null;
	characters: CharacterSummary[];
}

// Request to switch active path to a different branch
export interface SwitchPathRequest {
	target_node_id: string;
}

// ---------- Dashboard overview types ----------

// A story in the overview with aggregated data
export interface StoryOverviewStory {
	id: string;
	title: string;
	premise: string;
	created_at: string;
	updated_at: string;
	character_names: string[];
	node_count: number;
}

// A character appearing across stories
export interface StoryOverviewCharacter {
	name: string;
	story_ids: string[];
}

// A canonical (linked) character with cross-story presence
export interface StoryOverviewCanonicalCharacter {
	id: string;
	canonical_name: string;
	story_ids: string[];
}

// Full overview response for dashboard
export interface StoryOverviewResponse {
	stories: StoryOverviewStory[];
	characters: StoryOverviewCharacter[];
	canonical_characters: StoryOverviewCanonicalCharacter[];
}

// ---------- Cross-story character identity types ----------

// A character alias mapping a per-story name to its canonical identity
export interface CharacterAlias {
	id: string;
	canonical_id: string;
	story_id: string;
	raw_name: string;
	normalized_name: string;
	status: string;
	role_in_story: string | null;
}

// A canonical character's appearance in a specific story
export interface CharacterAppearance {
	story_id: string;
	story_title: string;
	role: string | null;
	context: string | null;
	arc_notes: string | null;
}

// Full canonical character with aliases, appearances, and profile data
export interface CanonicalCharacter {
	id: string;
	canonical_name: string;
	description: string | null;
	traits: string[];
	arc_summary: string | null;
	aliases: CharacterAlias[];
	appearances: CharacterAppearance[];
	story_ids: string[];
}

// Summary of a canonical character for list views
export interface CanonicalCharacterSummary {
	id: string;
	canonical_name: string;
	story_count: number;
	story_ids: string[];
	raw_names: string[];
}

// A single character mention candidate found across stories
export interface CharacterMentionCandidate {
	raw_name: string;
	story_id: string;
	story_title: string;
}

// A group of character mentions that may be the same canonical character
export interface CharacterCandidateGroup {
	normalized_name: string;
	mentions: CharacterMentionCandidate[];
}

// Request to link multiple character mentions as the same canonical character
export interface LinkCharactersRequest {
	canonical_name: string;
	mentions: { raw_name: string; story_id: string }[];
}

// Request to split mentions from an existing canonical character
export interface SplitCharactersRequest {
	canonical_id: string;
	mentions_to_split: { raw_name: string; story_id: string }[];
}

// Request to update a canonical character's profile
export interface UpdateCharacterRequest {
	canonical_name?: string;
	description?: string;
	traits?: string[];
	arc_summary?: string;
}
