<script lang="ts">
	import { hierarchy, tree as d3tree } from 'd3-hierarchy';
	import type { HierarchyPointNode } from 'd3-hierarchy';
	import { graphState } from '$lib/stores/graph.svelte';
	import { storyState } from '$lib/stores/story.svelte';
	import { generationState } from '$lib/stores/generation.svelte';
	import type { TreeNode, CharacterSummary } from '$lib/types';

	// ---- Layout constants ----
	const P_RADIUS = 14;                // paragraph node radius
	const CHAR_RADIUS = 18;             // character supernode radius
	const TREE_SPACING_X = 50;          // horizontal gap between sibling branches
	const TREE_SPACING_Y = 52;          // vertical gap between tree levels
	const CHAR_COLUMN_X_OFFSET = 120;   // character column offset from rightmost paragraph node
	const CHAR_SPACING_Y = 48;          // vertical gap between character supernodes
	const PADDING = 30;

	// ---- Character color palette (10 distinct hues) ----
	const PALETTE = [
		'#f87171', // red
		'#fb923c', // orange
		'#fbbf24', // amber
		'#34d399', // emerald
		'#22d3ee', // cyan
		'#60a5fa', // blue
		'#a78bfa', // violet
		'#f472b6', // pink
		'#e879f9', // fuchsia
		'#94a3b8', // slate
	];

	// ---- Reactive: load tree when active story changes ----
	$effect(() => {
		const id = storyState.activeStoryId;
		if (id) {
			graphState.loadTree(id);
		} else {
			graphState.clear();
		}
	});

	// ---- Reactive: reload tree after accept/reject ----
	let prevStatus = $state(generationState.status);
	$effect(() => {
		const status = generationState.status;
		const action = generationState.lastAction;
		if (prevStatus !== 'idle' && status === 'idle' && (action === 'accepted' || action === 'rejected')) {
			const id = storyState.activeStoryId;
			if (id) graphState.loadTree(id);
		}
		prevStatus = status;
	});

	// ---- Types ----
	type LayoutNode = HierarchyPointNode<TreeNode>;

	interface PositionedParagraph {
		id: string;
		x: number;
		y: number;
		position: number;
		content: string;
		isActive: boolean;
		isDraft: boolean;
		isGenerating: boolean;
		characterNames: string[];
	}

	interface PositionedCharacter {
		name: string;
		x: number;
		y: number;
		color: string;
		nodeIds: string[];
	}

	interface TreeEdge {
		x1: number; y1: number;
		x2: number; y2: number;
		isActive: boolean;
	}

	interface CharEdge {
		px: number; py: number; // paragraph position
		cx: number; cy: number; // character position
		color: string;
	}

	interface GraphLayout {
		paragraphs: PositionedParagraph[];
		characters: PositionedCharacter[];
		treeEdges: TreeEdge[];
		charEdges: CharEdge[];
		width: number;
		height: number;
	}

	// ---- Computed layout ----
	const activePathSet = $derived(
		new Set(graphState.treeData?.active_path ?? [])
	);

	function getCharacterColor(name: string, characters: CharacterSummary[]): string {
		const sorted = [...characters].sort((a, b) => a.name.localeCompare(b.name));
		const idx = sorted.findIndex((c) => c.name === name);
		return PALETTE[idx >= 0 ? idx % PALETTE.length : 0];
	}

	const layout = $derived.by((): GraphLayout | null => {
		const td = graphState.treeData;
		if (!td || !td.root) return null;

		// 1. Use d3-hierarchy to compute tree positions for paragraph nodes
		const root = hierarchy(td.root, (d) => d.children);
		const treeLayout = d3tree<TreeNode>().nodeSize([TREE_SPACING_X, TREE_SPACING_Y]);
		treeLayout(root);

		const descendants = root.descendants() as LayoutNode[];
		const links = root.links() as { source: LayoutNode; target: LayoutNode }[];

		// Compute tree bounds for offset
		let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
		for (const n of descendants) {
			if (n.x < minX) minX = n.x;
			if (n.x > maxX) maxX = n.x;
			if (n.y < minY) minY = n.y;
			if (n.y > maxY) maxY = n.y;
		}

		const ox = -minX + PADDING + P_RADIUS;
		const oy = -minY + PADDING + P_RADIUS;

		// 2. Build positioned paragraphs
		const paragraphs: PositionedParagraph[] = descendants.map((n) => ({
			id: n.data.id,
			x: n.x + ox,
			y: n.y + oy,
			position: n.depth,
			content: n.data.content,
			isActive: activePathSet.has(n.data.id),
			isDraft: n.data.is_draft,
			isGenerating: n.data.is_draft && generationState.isGenerating,
			characterNames: (n.data.character_mentions ?? []).map((m) => m.character_name),
		}));

		// 3. Build tree edges
		const treeEdges: TreeEdge[] = links.map((l) => ({
			x1: l.source.x + ox,
			y1: l.source.y + oy,
			x2: l.target.x + ox,
			y2: l.target.y + oy,
			isActive: activePathSet.has(l.source.data.id) && activePathSet.has(l.target.data.id),
		}));

		// 4. Position character supernodes in a column to the right
		const treeRight = maxX + ox + P_RADIUS;
		const charX = treeRight + CHAR_COLUMN_X_OFFSET;
		const totalCharHeight = (td.characters.length - 1) * CHAR_SPACING_Y;
		const treeHeight = maxY - minY;
		const charStartY = oy + (treeHeight - totalCharHeight) / 2; // center vertically

		const charMap = new Map<string, PositionedCharacter>();
		const characters: PositionedCharacter[] = td.characters.map((c, i) => {
			const pc: PositionedCharacter = {
				name: c.name,
				x: charX,
				y: Math.max(PADDING + CHAR_RADIUS, charStartY + i * CHAR_SPACING_Y),
				color: getCharacterColor(c.name, td.characters),
				nodeIds: c.node_ids,
			};
			charMap.set(c.name, pc);
			return pc;
		});

		// 5. Build cross-edges from paragraphs to their characters
		const charEdges: CharEdge[] = [];
		for (const p of paragraphs) {
			for (const cname of p.characterNames) {
				const c = charMap.get(cname);
				if (c) {
					charEdges.push({ px: p.x, py: p.y, cx: c.x, cy: c.y, color: c.color });
				}
			}
		}

		// 6. Compute total SVG dimensions
		const rightmost = characters.length > 0 ? charX + CHAR_RADIUS + PADDING : treeRight + PADDING;
		const bottomPara = Math.max(...paragraphs.map((p) => p.y)) + P_RADIUS + PADDING;
		const bottomChar = characters.length > 0 ? Math.max(...characters.map((c) => c.y)) + CHAR_RADIUS + PADDING : 0;
		const w = rightmost;
		const h = Math.max(bottomPara, bottomChar, 100);

		return { paragraphs, characters, treeEdges, charEdges, width: w, height: h };
	});

	// ---- Helpers ----
	function truncate(text: string, max: number): string {
		if (text.length <= max) return text;
		return text.slice(0, max - 1) + '\u2026';
	}

	function handleNodeClick(nodeId: string): void {
		if (activePathSet.has(nodeId)) return;
		const storyId = storyState.activeStoryId;
		if (!storyId) return;
		graphState.switchBranch(storyId, nodeId);
	}
</script>

<div class="node-graph">
	{#if graphState.isLoading}
		<div class="graph-status">
			<div class="spinner"></div>
			<p>Loading graph&hellip;</p>
		</div>
	{:else if graphState.error}
		<div class="graph-status error">
			<p>Error: {graphState.error}</p>
		</div>
	{:else if !storyState.activeStoryId}
		<div class="graph-status">
			<p class="hint">Select a story to view its node graph</p>
		</div>
	{:else if !layout}
		<div class="graph-status">
			<p class="hint">No nodes yet &mdash; generate some content first</p>
		</div>
	{:else}
		<div class="graph-scroll">
			<svg
				class="graph-svg"
				width={layout.width}
				height={layout.height}
				viewBox="0 0 {layout.width} {layout.height}"
			>
				<!-- Character cross-edges (draw first, behind everything) -->
				{#each layout.charEdges as ce, i (i)}
					<line
						x1={ce.px} y1={ce.py}
						x2={ce.cx} y2={ce.cy}
						class="char-edge"
						stroke={ce.color}
					/>
				{/each}

				<!-- Tree edges (paragraph flow) -->
				{#each layout.treeEdges as te, i (i)}
					<line
						x1={te.x1} y1={te.y1}
						x2={te.x2} y2={te.y2}
						class="tree-edge"
						class:tree-edge-active={te.isActive}
					/>
				{/each}

				<!-- Paragraph nodes -->
				{#each layout.paragraphs as p (p.id)}
					<!-- svelte-ignore a11y_click_events_have_key_events -->
					<!-- svelte-ignore a11y_no_static_element_interactions -->
					<g
						class="para-group"
						class:para-clickable={!p.isActive}
						onclick={() => handleNodeClick(p.id)}
					>
						<circle
							cx={p.x} cy={p.y} r={P_RADIUS}
							class="para-circle"
							class:para-active={p.isActive}
							class:para-branch={!p.isActive && !p.isDraft}
							class:para-draft={p.isDraft}
							class:para-generating={p.isGenerating}
						/>
						<text
							x={p.x} y={p.y + 1}
							class="para-label"
							class:para-label-active={p.isActive}
							text-anchor="middle"
							dominant-baseline="middle"
						>
							{p.position + 1}
						</text>
						<title>{p.content}</title>
					</g>
				{/each}

				<!-- Character supernodes -->
				{#each layout.characters as c (c.name)}
					<g class="char-group">
						<circle
							cx={c.x} cy={c.y} r={CHAR_RADIUS}
							fill={c.color}
							class="char-circle"
						/>
						<text
							x={c.x} y={c.y + 1}
							class="char-label"
							text-anchor="middle"
							dominant-baseline="middle"
						>
							{truncate(c.name, 3).toUpperCase()}
						</text>
						<text
							x={c.x + CHAR_RADIUS + 6}
							y={c.y + 1}
							class="char-name"
							dominant-baseline="middle"
						>
							{c.name}
						</text>
						<title>{c.name} — appears in {c.nodeIds.length} paragraph{c.nodeIds.length !== 1 ? 's' : ''}</title>
					</g>
				{/each}
			</svg>
		</div>
	{/if}
</div>

<style>
	.node-graph {
		display: flex;
		flex-direction: column;
		height: 100%;
		width: 100%;
		background-color: var(--panel-bg, #030712);
		overflow: hidden;
	}

	.graph-scroll {
		flex: 1;
		overflow: auto;
		min-height: 0;
	}

	.graph-svg {
		display: block;
	}

	/* Status / empty states */
	.graph-status {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		gap: 8px;
		color: var(--text-faint, #6b7280);
	}

	.graph-status.error {
		color: #f87171;
	}

	.graph-status .hint {
		font-size: 13px;
		margin: 0;
	}

	.spinner {
		width: 24px;
		height: 24px;
		border: 2px solid var(--text-faint, #6b7280);
		border-top-color: var(--text-primary, #e5e7eb);
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}

	/* ---- Tree edges (paragraph→paragraph) ---- */
	.tree-edge {
		stroke: var(--text-faint, #4b5563);
		stroke-width: 1.5;
		opacity: 0.3;
	}

	.tree-edge-active {
		stroke: #6366f1;
		stroke-width: 2;
		opacity: 1;
	}

	/* ---- Character cross-edges (paragraph→character) ---- */
	.char-edge {
		stroke-width: 1;
		opacity: 0.18;
	}

	/* ---- Paragraph nodes ---- */
	.para-circle {
		fill: var(--hover-bg, #1f2937);
		stroke: var(--border-color, #374151);
		stroke-width: 1.5;
		transition: fill 150ms ease, stroke 150ms ease;
	}

	.para-active {
		fill: #6366f1;
		stroke: #818cf8;
	}

	.para-branch {
		opacity: 0.5;
	}

	.para-draft {
		stroke-dasharray: 3 2;
		stroke: #fbbf24;
		fill: #292524;
	}

	.para-generating {
		animation: pulse 1.5s ease-in-out infinite;
	}

	@keyframes pulse {
		0%, 100% { opacity: 0.5; }
		50% { opacity: 1; }
	}

	.para-label {
		fill: var(--text-muted, #9ca3af);
		font-size: 10px;
		font-weight: 600;
		font-family: monospace;
		pointer-events: none;
	}

	.para-label-active {
		fill: #ffffff;
	}

	.para-clickable {
		cursor: pointer;
	}

	.para-clickable:hover .para-circle:not(.para-active) {
		fill: var(--border-color, #374151);
		stroke: #6366f1;
	}

	/* ---- Character supernodes ---- */
	.char-circle {
		opacity: 0.85;
		stroke: var(--panel-bg, #030712);
		stroke-width: 2;
	}

	.char-label {
		fill: #ffffff;
		font-size: 8px;
		font-weight: 700;
		font-family: monospace;
		pointer-events: none;
		letter-spacing: 0.5px;
	}

	.char-name {
		fill: var(--text-muted, #9ca3af);
		font-size: 10px;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
		pointer-events: none;
	}

	.char-group {
		cursor: default;
	}
</style>
