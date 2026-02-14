import { Mark } from '@tiptap/core';

export type ProvenanceSource = 'ai_generated' | 'user_written' | 'user_edited' | 'initial_prompt';

export const PROVENANCE_COLORS: Record<ProvenanceSource, string> = {
	ai_generated: 'rgba(255, 255, 255, 0.9)',
	user_written: 'rgba(100, 149, 237, 0.9)',
	user_edited: 'rgba(255, 182, 193, 0.9)',
	initial_prompt: 'rgba(255, 253, 208, 0.9)',
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
					style: `color: ${PROVENANCE_COLORS[attributes.source as ProvenanceSource] || 'inherit'}`,
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
