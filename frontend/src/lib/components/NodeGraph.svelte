<script lang="ts">
	import { hierarchy, tree as d3tree } from 'd3-hierarchy';
	import type { HierarchyPointNode } from 'd3-hierarchy';
	import { graphState } from '$lib/stores/graph.svelte';
	import { storyState } from '$lib/stores/story.svelte';
	import { generationState } from '$lib/stores/generation.svelte';
	import type { TreeNode, CharacterSummary } from '$lib/types';

	// ---- Layout constants ----
	const P_RADIUS = 20;                // paragraph node radius
	const CHAR_RADIUS = 26;             // character supernode radius
	const SEED_RADIUS = 14;             // seed node radius
	const TREE_SPACING_X = 72;          // horizontal gap between sibling branches
	const TREE_SPACING_Y = 72;          // vertical gap between tree levels
	const SEED_SPACING_X = 56;          // horizontal gap between seed nodes
	const SEED_OFFSET_Y = 60;           // vertical offset of seeds below their parent
	const CHAR_COLUMN_X_OFFSET = 80;    // character column offset from rightmost paragraph node
	const CHAR_SPACING_Y = 64;          // vertical gap between character supernodes
	const PADDING = 40;

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

	interface PositionedSeed {
		index: number;
		text: string;
		x: number;
		y: number;
		parentX: number;
		parentY: number;
		parentId: string;
	}

	interface GraphLayout {
		paragraphs: PositionedParagraph[];
		characters: PositionedCharacter[];
		seeds: PositionedSeed[];
		treeEdges: TreeEdge[];
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

		// 1b. Post-layout pass: push children down when a parent has seeds
		// so seed nodes don't overlap the next paragraph level.
		const SEED_EXTRA = SEED_OFFSET_Y + SEED_RADIUS + 12; // total extra space a seed row needs
		function pushSubtreeDown(node: LayoutNode, delta: number): void {
			node.y += delta;
			for (const child of (node.children ?? [])) {
				pushSubtreeDown(child, delta);
			}
		}
		// Process top-down (BFS order — descendants are already in that order)
		for (const n of descendants) {
			const hasSeeds = (n.data.analysis?.next_paragraph_seeds?.length ?? 0) > 0;
			if (hasSeeds && n.children) {
				for (const child of n.children) {
					// Only add extra if the gap between parent and child isn't already big enough
					const gap = child.y - n.y;
					if (gap < SEED_EXTRA + TREE_SPACING_Y * 0.5) {
						const needed = SEED_EXTRA + TREE_SPACING_Y * 0.5 - gap;
						pushSubtreeDown(child, needed);
					}
				}
			}
		}

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

		// 5. Position seed nodes below every paragraph node that has persisted analysis seeds
		const seeds: PositionedSeed[] = [];
		const paraMap = new Map(paragraphs.map((p) => [p.id, p]));

		for (const n of descendants) {
			const nodeSeeds = n.data.analysis?.next_paragraph_seeds ?? [];
			if (nodeSeeds.length === 0) continue;

			const para = paraMap.get(n.data.id);
			if (!para) continue;

			const seedCount = nodeSeeds.length;
			const totalWidth = (seedCount - 1) * SEED_SPACING_X;
			const startX = para.x - totalWidth / 2;

			for (let i = 0; i < seedCount; i++) {
				seeds.push({
					index: i,
					text: nodeSeeds[i],
					x: startX + i * SEED_SPACING_X,
					y: para.y + SEED_OFFSET_Y,
					parentX: para.x,
					parentY: para.y,
					parentId: n.data.id,
				});
			}
		}

		// 6. Compute total SVG dimensions
		const rightmost = characters.length > 0 ? charX + CHAR_RADIUS + PADDING : treeRight + PADDING;
		const bottomPara = Math.max(...paragraphs.map((p) => p.y)) + P_RADIUS + PADDING;
		const bottomChar = characters.length > 0 ? Math.max(...characters.map((c) => c.y)) + CHAR_RADIUS + PADDING : 0;
		const bottomSeed = seeds.length > 0 ? Math.max(...seeds.map((s) => s.y)) + SEED_RADIUS + PADDING : 0;
		const w = rightmost;
		const h = Math.max(bottomPara, bottomChar, bottomSeed, 100);

		return { paragraphs, characters, seeds, treeEdges, width: w, height: h };
	});

	// ---- Helpers ----
	function truncate(text: string, max: number): string {
		if (text.length <= max) return text;
		return text.slice(0, max - 1) + '\u2026';
	}

	/** First letter of a character name, uppercased */
	function initial(name: string): string {
		return name.trim().charAt(0).toUpperCase();
	}

	function handleNodeClick(nodeId: string): void {
		if (activePathSet.has(nodeId)) return;
		const storyId = storyState.activeStoryId;
		if (!storyId) return;
		graphState.switchBranch(storyId, nodeId);
	}

	function handleSeedClick(seed: PositionedSeed): void {
		const storyId = storyState.activeStoryId;
		if (!storyId) return;
		generationState.startGeneration(storyId, seed.parentId, seed.text);
	}

	// ---- Tooltip state ----
	interface TooltipData {
		x: number;
		y: number;
		title: string;
		body: string;
		color?: string;
	}

	let tooltip = $state<TooltipData | null>(null);
	let graphScrollEl = $state<HTMLDivElement | null>(null);

	function showParaTooltip(e: MouseEvent, p: PositionedParagraph): void {
		const rect = graphScrollEl?.getBoundingClientRect();
		if (!rect) return;
		tooltip = {
			x: e.clientX - rect.left + graphScrollEl!.scrollLeft,
			y: e.clientY - rect.top + graphScrollEl!.scrollTop,
			title: `Paragraph ${p.position + 1}`,
			body: truncate(p.content, 200),
		};
	}

	function showCharTooltip(e: MouseEvent, c: PositionedCharacter): void {
		const rect = graphScrollEl?.getBoundingClientRect();
		if (!rect) return;
		tooltip = {
			x: e.clientX - rect.left + graphScrollEl!.scrollLeft,
			y: e.clientY - rect.top + graphScrollEl!.scrollTop,
			title: c.name,
			body: `Appears in ${c.nodeIds.length} paragraph${c.nodeIds.length !== 1 ? 's' : ''}`,
			color: c.color,
		};
	}

	function showSeedTooltip(e: MouseEvent, s: PositionedSeed): void {
		const rect = graphScrollEl?.getBoundingClientRect();
		if (!rect) return;
		tooltip = {
			x: e.clientX - rect.left + graphScrollEl!.scrollLeft,
			y: e.clientY - rect.top + graphScrollEl!.scrollTop,
			title: `Seed ${s.index + 1}`,
			body: s.text,
		};
	}

	function hideTooltip(): void {
		tooltip = null;
	}

	// ---- Zoom & Pan state ----
	let scale = $state(1);
	let panX = $state(0);
	let panY = $state(0);
	let isPanning = $state(false);
	let panStartX = $state(0);
	let panStartY = $state(0);
	let panStartPanX = $state(0);
	let panStartPanY = $state(0);

	const MIN_SCALE = 0.3;
	const MAX_SCALE = 3;
	const ZOOM_FACTOR = 0.001;

	// Reset zoom/pan when tree data changes
	$effect(() => {
		if (graphState.treeData) {
			scale = 1;
			panX = 0;
			panY = 0;
		}
	});

	function handleWheel(e: WheelEvent): void {
		e.preventDefault();
		const rect = graphScrollEl?.getBoundingClientRect();
		if (!rect) return;

		// Mouse position relative to the scroll container
		const mx = e.clientX - rect.left;
		const my = e.clientY - rect.top;

		// Point in graph space under the cursor before zoom
		const gxBefore = (mx - panX) / scale;
		const gyBefore = (my - panY) / scale;

		// Apply zoom
		const delta = -e.deltaY * ZOOM_FACTOR;
		const newScale = Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale * (1 + delta)));
		scale = newScale;

		// Adjust pan so the point under the cursor stays fixed
		panX = mx - gxBefore * newScale;
		panY = my - gyBefore * newScale;
	}

	function handlePointerDown(e: PointerEvent): void {
		// Middle mouse or left mouse on empty area
		if (e.button === 1 || (e.button === 0 && e.target === graphScrollEl?.querySelector('.graph-svg'))) {
			isPanning = true;
			panStartX = e.clientX;
			panStartY = e.clientY;
			panStartPanX = panX;
			panStartPanY = panY;
			(e.currentTarget as HTMLElement)?.setPointerCapture(e.pointerId);
			e.preventDefault();
		}
	}

	function handlePointerMove(e: PointerEvent): void {
		if (!isPanning) return;
		panX = panStartPanX + (e.clientX - panStartX);
		panY = panStartPanY + (e.clientY - panStartY);
	}

	function handlePointerUp(): void {
		isPanning = false;
	}

	function resetView(): void {
		scale = 1;
		panX = 0;
		panY = 0;
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
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div
			class="graph-viewport"
			bind:this={graphScrollEl}
			onwheel={handleWheel}
			onpointerdown={handlePointerDown}
			onpointermove={handlePointerMove}
			onpointerup={handlePointerUp}
			onpointerleave={handlePointerUp}
			class:viewport-panning={isPanning}
		>
			<svg
				class="graph-svg"
				width="100%"
				height="100%"
			>
				<g transform="translate({panX}, {panY}) scale({scale})">
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
							onmouseenter={(e) => showParaTooltip(e, p)}
							onmouseleave={hideTooltip}
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
						</g>
					{/each}

					<!-- Character supernodes -->
					{#each layout.characters as c (c.name)}
						<!-- svelte-ignore a11y_no_static_element_interactions -->
						<g
							class="char-group"
							onmouseenter={(e) => showCharTooltip(e, c)}
							onmouseleave={hideTooltip}
						>
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
								{initial(c.name)}
							</text>

						</g>
					{/each}

				<!-- Seed edges (rendered first so circles paint on top) -->
				{#each layout.seeds as s, i (`${s.parentId}-edge-${s.index}`)}
					<line
						x1={s.parentX} y1={s.parentY}
						x2={s.x} y2={s.y}
						class="seed-edge"
					/>
				{/each}

				<!-- Seed nodes -->
				{#each layout.seeds as s, i (`${s.parentId}-node-${s.index}`)}
					<!-- svelte-ignore a11y_click_events_have_key_events -->
					<!-- svelte-ignore a11y_no_static_element_interactions -->
					<g
						class="seed-group"
						onclick={() => handleSeedClick(s)}
						onmouseenter={(e) => showSeedTooltip(e, s)}
						onmouseleave={hideTooltip}
					>
						<circle
							cx={s.x} cy={s.y} r={SEED_RADIUS}
							class="seed-circle"
						/>
						<text
							x={s.x} y={s.y + 1}
							class="seed-label"
							text-anchor="middle"
							dominant-baseline="middle"
						>
							{s.index + 1}
						</text>
					</g>
				{/each}
				</g>
			</svg>

			<!-- Custom tooltip -->
			{#if tooltip}
				<div
					class="graph-tooltip"
					style="left: {tooltip.x + 12}px; top: {tooltip.y - 8}px"
				>
					<div class="tooltip-title">
						{#if tooltip.color}
							<span class="tooltip-dot" style="background-color: {tooltip.color}"></span>
						{/if}
						{tooltip.title}
					</div>
					<div class="tooltip-body">{tooltip.body}</div>
				</div>
			{/if}
		</div>

		<!-- Zoom controls -->
		<div class="zoom-controls">
			<button class="zoom-btn" onclick={() => { scale = Math.min(MAX_SCALE, scale * 1.25); }} title="Zoom in">+</button>
			<button class="zoom-btn" onclick={() => { scale = Math.max(MIN_SCALE, scale * 0.8); }} title="Zoom out">&minus;</button>
			<button class="zoom-btn zoom-reset" onclick={resetView} title="Reset view">1:1</button>
			<span class="zoom-level">{Math.round(scale * 100)}%</span>
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
		position: relative;
	}

	.graph-viewport {
		flex: 1;
		overflow: hidden;
		min-height: 0;
		position: relative;
		cursor: grab;
	}

	.viewport-panning {
		cursor: grabbing;
	}

	.graph-svg {
		display: block;
		width: 100%;
		height: 100%;
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

	/* ---- Tree edges (paragraph->paragraph) ---- */
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
		font-size: 13px;
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
		font-size: 12px;
		font-weight: 700;
		font-family: monospace;
		pointer-events: none;
		letter-spacing: 0.5px;
	}

	.char-group {
		cursor: default;
	}

	/* ---- Seed nodes ---- */
	.seed-edge {
		stroke: var(--seed-stroke, #fbbf24);
		stroke-width: 1;
		stroke-dasharray: 3 3;
		opacity: 0.7;
	}

	.seed-circle {
		fill: var(--hover-bg, #1f2937);
		stroke: var(--seed-stroke, #fbbf24);
		stroke-width: 1.5;
		stroke-dasharray: 3 2;
		transition: fill 150ms ease, stroke 150ms ease;
	}

	.seed-label {
		fill: var(--seed-stroke, #fbbf24);
		font-size: 11px;
		font-weight: 700;
		font-family: monospace;
		pointer-events: none;
	}

	.seed-group {
		cursor: pointer;
	}

	.seed-group:hover .seed-circle {
		fill: var(--seed-hover-bg, rgba(251, 191, 36, 0.2));
		stroke: var(--seed-stroke-hover, #f59e0b);
	}

	/* ---- Custom tooltip ---- */
	.graph-tooltip {
		position: absolute;
		pointer-events: none;
		z-index: 10;
		max-width: 280px;
		background: var(--sidebar-bg, #111827);
		border: 1px solid var(--border-color, #374151);
		border-radius: 6px;
		padding: 8px 10px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
	}

	.tooltip-title {
		display: flex;
		align-items: center;
		gap: 6px;
		font-size: 11px;
		font-weight: 600;
		color: var(--text-primary, #e5e7eb);
		margin-bottom: 4px;
	}

	.tooltip-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		flex-shrink: 0;
	}

	.tooltip-body {
		font-size: 10px;
		color: var(--text-muted, #9ca3af);
		line-height: 1.4;
		white-space: pre-wrap;
		word-break: break-word;
	}

	/* ---- Zoom controls ---- */
	.zoom-controls {
		position: absolute;
		bottom: 8px;
		right: 8px;
		display: flex;
		align-items: center;
		gap: 4px;
		z-index: 5;
	}

	.zoom-btn {
		width: 26px;
		height: 26px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--sidebar-bg, #111827);
		border: 1px solid var(--border-color, #374151);
		border-radius: 4px;
		color: var(--text-muted, #9ca3af);
		font-size: 13px;
		font-weight: 600;
		cursor: pointer;
		padding: 0;
		line-height: 1;
	}

	.zoom-btn:hover {
		background: var(--hover-bg, #1f2937);
		color: var(--text-primary, #e5e7eb);
	}

	.zoom-reset {
		width: auto;
		padding: 0 6px;
		font-size: 10px;
		font-family: monospace;
	}

	.zoom-level {
		font-size: 10px;
		font-family: monospace;
		color: var(--text-faint, #6b7280);
		min-width: 32px;
		text-align: right;
	}
</style>
