import { Mark } from '@tiptap/core';

export type ProvenanceSource = 'ai_generated' | 'user_written' | 'user_edited' | 'initial_prompt';

/**
 * Provenance styling: subtle background tints that work in both dark and light themes.
 * Text color inherits from the editor's theme; provenance is indicated by background only.
 */
export const PROVENANCE_STYLES: Record<ProvenanceSource, string> = {
	ai_generated: 'background-color: rgba(139, 92, 246, 0.12)',     // violet tint
	user_written: 'background-color: rgba(59, 130, 246, 0.12)',     // blue tint
	user_edited: 'background-color: rgba(244, 114, 182, 0.15)',     // pink tint
	initial_prompt: 'background-color: rgba(251, 191, 36, 0.12)',   // amber tint
};

export const Provenance = Mark.create({
	name: 'provenance',

	addAttributes() {
		return {
			source: {
				default: 'user_written' as ProvenanceSource,
				parseHTML: (element: HTMLElement) => element.getAttribute('data-source') as ProvenanceSource,
				renderHTML: (attributes: Record<string, string>) => ({
					'data-source': attributes.source,
					style: `${PROVENANCE_STYLES[attributes.source as ProvenanceSource] || ''}; border-radius: 2px; padding: 0 1px`,
				}),
			},
		};
	},

	parseHTML() {
		return [{ tag: 'span[data-source]' }];
	},

	renderHTML({ HTMLAttributes }) {
		return ['span', HTMLAttributes, 0];
	},
});
