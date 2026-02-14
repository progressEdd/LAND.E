<script lang="ts">
	import { hierarchy, tree as d3tree } from 'd3-hierarchy';
	import type { HierarchyPointNode } from 'd3-hierarchy';
	import { graphState } from '$lib/stores/graph.svelte';
	import { storyState } from '$lib/stores/story.svelte';
	import { generationState } from '$lib/stores/generation.svelte';
	import type { TreeNode } from '$lib/types';

	// ---- Layout constants ----
	const NODE_W = 120;
	const NODE_H = 36;
	const NODE_RX = 6;
	const NODE_SPACING_X = 140;
	const NODE_SPACING_Y = 72;
	const PADDING = 40;
	const BADGE_R = 5;
	const MAX_BADGES = 4;

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

	// ---- Computed layout ----
	type LayoutNode = HierarchyPointNode<TreeNode>;

	interface LayoutResult {
		nodes: LayoutNode[];
		links: { source: LayoutNode; target: LayoutNode }[];
		width: number;
		height: number;
		offsetX: number;
		offsetY: number;
	}

	const layout = $derived.by((): LayoutResult | null => {
		const td = graphState.treeData;
		if (!td || !td.root) return null;

		const root = hierarchy(td.root, (d) => d.children);
		const treeLayout = d3tree<TreeNode>().nodeSize([NODE_SPACING_X, NODE_SPACING_Y]);
		treeLayout(root);

		const nodes = root.descendants() as LayoutNode[];
		const links = root.links() as { source: LayoutNode; target: LayoutNode }[];

		// Compute bounds
		let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
		for (const n of nodes) {
			if (n.x < minX) minX = n.x;
			if (n.x > maxX) maxX = n.x;
			if (n.y < minY) minY = n.y;
			if (n.y > maxY) maxY = n.y;
		}

		const w = maxX - minX + NODE_W + PADDING * 2;
		const h = maxY - minY + NODE_H + PADDING * 2;
		const offsetX = -minX + NODE_W / 2 + PADDING;
		const offsetY = -minY + NODE_H / 2 + PADDING;

		return { nodes, links, width: w, height: h, offsetX, offsetY };
	});

	const activePathSet = $derived(
		new Set(graphState.treeData?.active_path ?? [])
	);

	// ---- Character color mapping ----
	function getCharacterColor(name: string): string {
		const chars = graphState.treeData?.characters ?? [];
		const sorted = [...chars].sort((a, b) => a.name.localeCompare(b.name));
		const idx = sorted.findIndex((c) => c.name === name);
		return PALETTE[idx >= 0 ? idx % PALETTE.length : 0];
	}

	// ---- Helpers ----
	function truncate(text: string, max: number): string {
		if (text.length <= max) return text;
		return text.slice(0, max - 1) + '\u2026';
	}

	function edgePath(source: LayoutNode, target: LayoutNode, ox: number, oy: number): string {
		const sx = source.x + ox;
		const sy = source.y + oy + NODE_H / 2;
		const tx = target.x + ox;
		const ty = target.y + oy - NODE_H / 2;
		const my = (sy + ty) / 2;
		return `M ${sx} ${sy} C ${sx} ${my}, ${tx} ${my}, ${tx} ${ty}`;
	}

	function handleNodeClick(nodeId: string): void {
		if (activePathSet.has(nodeId)) return; // already on active path
		const storyId = storyState.activeStoryId;
		if (!storyId) return;
		graphState.switchBranch(storyId, nodeId);
	}

	// ---- Container sizing ----
	let containerW = $state(0);
	let containerH = $state(0);
</script>

<div class="node-graph" bind:clientWidth={containerW} bind:clientHeight={containerH}>
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
		<!-- SVG Tree Graph -->
		<svg
			class="tree-svg"
			viewBox="0 0 {layout.width} {layout.height}"
			preserveAspectRatio="xMidYMid meet"
		>
			<!-- Edges -->
			{#each layout.links as link (link.source.data.id + '-' + link.target.data.id)}
				<path
					class="edge"
					class:edge-active={activePathSet.has(link.source.data.id) && activePathSet.has(link.target.data.id)}
					d={edgePath(link.source, link.target, layout.offsetX, layout.offsetY)}
				/>
			{/each}

			<!-- Nodes -->
			{#each layout.nodes as node (node.data.id)}
				{@const nx = node.x + layout.offsetX - NODE_W / 2}
				{@const ny = node.y + layout.offsetY - NODE_H / 2}
				{@const isActive = activePathSet.has(node.data.id)}
				{@const isDraft = node.data.is_draft}
				{@const isGenerating = isDraft && generationState.isGenerating}
				{@const mentions = node.data.character_mentions ?? []}
				<!-- svelte-ignore a11y_click_events_have_key_events -->
				<!-- svelte-ignore a11y_no_static_element_interactions -->
				<g
					class="node-group"
					class:node-clickable={!isActive}
					onclick={() => handleNodeClick(node.data.id)}
				>
					<!-- Node rectangle -->
					<rect
						x={nx}
						y={ny}
						width={NODE_W}
						height={NODE_H}
						rx={NODE_RX}
						class="node-rect"
						class:node-active={isActive}
						class:node-branch={!isActive && !isDraft}
						class:node-draft={isDraft}
						class:node-generating={isGenerating}
					/>

					<!-- Position label -->
					<text
						x={nx + 8}
						y={ny + NODE_H / 2 + 1}
						class="node-position"
						dominant-baseline="middle"
					>
						{node.data.position}
					</text>

					<!-- Content preview -->
					<text
						x={nx + 24}
						y={ny + NODE_H / 2 + 1}
						class="node-label"
						class:label-active={isActive}
						dominant-baseline="middle"
					>
						{truncate(node.data.content, 14)}
					</text>

					<!-- Character badges -->
					{#if mentions.length > 0}
						{@const visibleBadges = mentions.slice(0, MAX_BADGES)}
						{#each visibleBadges as mention, i (mention.character_name)}
							<circle
								cx={nx + 10 + i * (BADGE_R * 2 + 3)}
								cy={ny + NODE_H + BADGE_R + 3}
								r={BADGE_R}
								fill={getCharacterColor(mention.character_name)}
								class="badge"
							>
								<title>{mention.character_name}{mention.role ? ` — ${mention.role}` : ''}</title>
							</circle>
						{/each}
						{#if mentions.length > MAX_BADGES}
							<text
								x={nx + 10 + MAX_BADGES * (BADGE_R * 2 + 3)}
								y={ny + NODE_H + BADGE_R + 4}
								class="badge-overflow"
								dominant-baseline="middle"
							>
								+{mentions.length - MAX_BADGES}
							</text>
						{/if}
					{/if}

					<!-- Tooltip on hover -->
					<title>{node.data.content}</title>
				</g>
			{/each}
		</svg>

		<!-- Character legend -->
		{#if graphState.treeData && graphState.treeData.characters.length > 0}
			<div class="character-legend">
				{#each graphState.treeData.characters as char (char.name)}
					<span class="legend-item">
						<span class="legend-dot" style="background-color: {getCharacterColor(char.name)}"></span>
						{char.name}
					</span>
				{/each}
			</div>
		{/if}
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
		position: relative;
	}

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

	/* SVG tree */
	.tree-svg {
		flex: 1;
		min-height: 0;
		width: 100%;
	}

	/* Edges */
	.edge {
		fill: none;
		stroke: var(--text-faint, #4b5563);
		stroke-width: 1.5;
		opacity: 0.4;
	}

	.edge-active {
		stroke: #6366f1;
		stroke-width: 2;
		opacity: 1;
	}

	/* Node rectangles */
	.node-rect {
		fill: var(--hover-bg, #1f2937);
		stroke: var(--border-color, #374151);
		stroke-width: 1;
		transition: fill 150ms ease, stroke 150ms ease;
	}

	.node-active {
		fill: #6366f1;
		stroke: #818cf8;
	}

	.node-branch {
		opacity: 0.6;
	}

	.node-draft {
		stroke-dasharray: 4 3;
		stroke: #fbbf24;
		fill: #292524;
	}

	.node-generating {
		animation: pulse 1.5s ease-in-out infinite;
	}

	@keyframes pulse {
		0%, 100% { opacity: 0.6; }
		50% { opacity: 1; }
	}

	/* Node text */
	.node-position {
		fill: var(--text-faint, #6b7280);
		font-size: 10px;
		font-weight: 600;
		font-family: monospace;
		pointer-events: none;
	}

	.node-label {
		fill: var(--text-secondary, #d1d5db);
		font-size: 10px;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
		pointer-events: none;
	}

	.label-active {
		fill: #ffffff;
		font-weight: 500;
	}

	/* Interaction */
	.node-clickable {
		cursor: pointer;
	}

	.node-clickable:hover .node-rect:not(.node-active) {
		fill: var(--border-color, #374151);
		stroke: #6366f1;
	}

	/* Character badges */
	.badge {
		opacity: 0.85;
		stroke: var(--panel-bg, #030712);
		stroke-width: 1;
	}

	.badge-overflow {
		fill: var(--text-faint, #6b7280);
		font-size: 8px;
		font-family: monospace;
		pointer-events: none;
	}

	/* Character legend */
	.character-legend {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		padding: 8px 12px;
		border-top: 1px solid var(--border-color, #374151);
		background-color: var(--sidebar-bg, #111827);
		font-size: 11px;
		color: var(--text-muted, #9ca3af);
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: 4px;
	}

	.legend-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		flex-shrink: 0;
	}
</style>
