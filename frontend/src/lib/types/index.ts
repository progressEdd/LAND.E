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
