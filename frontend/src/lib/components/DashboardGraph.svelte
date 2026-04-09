<script lang="ts">
	import { onMount } from 'svelte';
	import { forceSimulation, forceLink, forceManyBody, forceCenter, forceCollide } from 'd3-force';
	import type { StoryOverviewResponse, StoryOverviewStory, StoryOverviewCharacter } from '$lib/types';
	import { api } from '$lib/api/rest';
	import { storyState } from '$lib/stores/story.svelte';

	// ---- Types ----
	interface GraphNode {
		id: string;
		label: string;
		type: 'story' | 'character';
		x: number;
		y: number;
		fx?: number | null;
		fy?: number | null;
	}

	interface GraphLink {
		source: string | GraphNode;
		target: string | GraphNode;
	}

	interface SimNode {
		id: string;
		label: string;
		type: 'story' | 'character';
		x: number;
		y: number;
	}

	interface SimLink {
		source: SimNode | string;
		target: SimNode | string;
	}

	let nodes = $state<GraphNode[]>([]);
	let links = $state<GraphLink[]>([]);
	let isLoading = $state(true);
	let hoveredNode = $state<string | null>(null);

	// ---- Color palette for character nodes ----
	const PALETTE = [
		'#f87171', '#fb923c', '#fbbf24', '#34d399', '#22d3ee',
		'#60a5fa', '#a78bfa', '#f472b6', '#e879f9', '#94a3b8',
	];

	function getCharColor(index: number): string {
		return PALETTE[index % PALETTE.length];
	}

	async function loadGraph(): Promise<void> {
		isLoading = true;
		try {
			const response = await api.getStoriesOverview();
			buildGraph(response);
		} catch {
			// Graceful failure
			nodes = [];
			links = [];
		} finally {
			isLoading = false;
		}
	}

	function buildGraph(data: StoryOverviewResponse): void {
		if (data.stories.length === 0 && data.characters.length === 0) {
			nodes = [];
			links = [];
			return;
		}

		// Create nodes
		const graphNodes: SimNode[] = [
			...data.stories.map((s) => ({
				id: s.id,
				label: s.title,
				type: 'story' as const,
				x: 0,
				y: 0,
			})),
			...data.characters.map((c) => ({
				id: `char:${c.name}`,
				label: c.name,
				type: 'character' as const,
				x: 0,
				y: 0,
			})),
		];

		// Create links from character→story
		const graphLinks: SimLink[] = [];
		for (const c of data.characters) {
			for (const sid of c.story_ids) {
				graphLinks.push({
					source: `char:${c.name}`,
					target: sid,
				});
			}
		}

		// Run force simulation
		const simulation = forceSimulation<SimNode>(graphNodes as any)
			.force('link', forceLink<SimNode, SimLink>(graphLinks as any).id((d: any) => d.id).distance(100))
			.force('charge', forceManyBody().strength(-250))
			.force('center', forceCenter(300, 150))
			.force('collide', forceCollide<SimNode>().radius(60) as any)
			.stop();

		// Run simulation synchronously for 120 ticks (no animation needed)
		for (let i = 0; i < 120; i++) {
			simulation.tick();
		}

		// Extract positions
		const positioned: GraphNode[] = graphNodes.map((n) => ({
			id: n.id,
			label: n.label,
			type: n.type,
			x: n.x ?? 0,
			y: n.y ?? 0,
		}));

		// Normalize positions to start from padding
		const PAD = 40;
		const minX = Math.min(...positioned.map((n) => n.x));
		const minY = Math.min(...positioned.map((n) => n.y));
		for (const n of positioned) {
			n.x = n.x - minX + PAD + 30;
			n.y = n.y - minY + PAD + 30;
		}

		nodes = positioned;
		links = graphLinks.map((l) => ({
			source: typeof l.source === 'object' ? (l.source as SimNode).id : (l.source as string),
			target: typeof l.target === 'object' ? (l.target as SimNode).id : (l.target as string),
		}));
	}

	function getNodePos(id: string): { x: number; y: number } {
		const n = nodes.find((n) => n.id === id);
		return n ? { x: n.x, y: n.y } : { x: 0, y: 0 };
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
	let panStartPointerId = $state(-1);
	let graphEl = $state<HTMLDivElement | null>(null);

	const MIN_SCALE = 0.3;
	const MAX_SCALE = 3;
	const ZOOM_FACTOR = 0.001;

	function handleWheel(e: WheelEvent): void {
		e.preventDefault();
		const rect = graphEl?.getBoundingClientRect();
		if (!rect) return;

		const mx = e.clientX - rect.left;
		const my = e.clientY - rect.top;

		const gxBefore = (mx - panX) / scale;
		const gyBefore = (my - panY) / scale;

		const delta = -e.deltaY * ZOOM_FACTOR;
		const newScale = Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale * (1 + delta)));
		scale = newScale;

		panX = mx - gxBefore * newScale;
		panY = my - gyBefore * newScale;
	}

	let didDrag = $state(false);

	function handlePointerDown(e: PointerEvent): void {
		if (e.button === 0) {
			isPanning = true;
			didDrag = false;
			panStartX = e.clientX;
			panStartY = e.clientY;
			panStartPanX = panX;
			panStartPanY = panY;
			panStartPointerId = e.pointerId;
			// Do NOT capture pointer here — defer until drag is confirmed
			// Otherwise click events on child SVG nodes get suppressed
		}
	}

	function handlePointerMove(e: PointerEvent): void {
		if (!isPanning) return;
		const dx = e.clientX - panStartX;
		const dy = e.clientY - panStartY;
		if (!didDrag && (Math.abs(dx) > 3 || Math.abs(dy) > 3)) {
			didDrag = true;
			// Now safe to capture — user is definitely dragging
			graphEl?.setPointerCapture(panStartPointerId);
		}
		if (didDrag) {
			panX = panStartPanX + dx;
			panY = panStartPanY + dy;
		}
	}

	function handlePointerUp(): void {
		isPanning = false;
	}

	function handleNodeClick(node: GraphNode): void {
		if (didDrag) return; // Was a drag, not a click
		if (node.type === 'story') {
			storyState.setActiveStory(node.id);
		}
		// Character nodes don't navigate anywhere
	}

	function resetView(): void {
		scale = 1;
		panX = 0;
		panY = 0;
	}

	// Load on mount
	onMount(() => {
		loadGraph();
	});
</script>

<div class="dashboard-graph">
	{#if isLoading}
		<div class="graph-loading">
			<div class="spinner"></div>
			<p>Loading graph...</p>
		</div>
	{:else if nodes.length === 0}
		<!-- No graph when no stories exist (D-13) -->
	{:else}
		<h4 class="graph-title">Story Universe</h4>
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div
			class="graph-viewport"
			bind:this={graphEl}
			onwheel={handleWheel}
			onpointerdown={handlePointerDown}
			onpointermove={handlePointerMove}
			onpointerup={handlePointerUp}
			onpointerleave={handlePointerUp}
			class:viewport-panning={isPanning}
		>
			<svg class="graph-svg" viewBox="0 0 800 400" preserveAspectRatio="xMidYMid meet">
				<g transform="translate({panX}, {panY}) scale({scale})">
			<!-- Links -->
			{#each links as l, i}
				{@const sourcePos = getNodePos(typeof l.source === 'string' ? l.source : (l.source as GraphNode).id)}
				{@const targetPos = getNodePos(typeof l.target === 'string' ? l.target : (l.target as GraphNode).id)}
				<line
					x1={sourcePos.x} y1={sourcePos.y}
					x2={targetPos.x} y2={targetPos.y}
					class="dash-link"
				/>
			{/each}

			<!-- Nodes -->
			{#each nodes as n (n.id)}
				<!-- svelte-ignore a11y_click_events_have_key_events -->
				<!-- svelte-ignore a11y_no_static_element_interactions -->
				<g
					class="graph-node"
					class:graph-node-hovered={hoveredNode === n.id}
					onclick={() => handleNodeClick(n)}
					onmouseenter={() => (hoveredNode = n.id)}
					onmouseleave={() => (hoveredNode = null)}
				>
					{#if n.type === 'story'}
						<foreignObject x={n.x - 90} y={n.y - 40} width="180" height="80">
							<div class="story-node-card" title={n.label}>
								<span class="story-node-title">{n.label}</span>
							</div>
						</foreignObject>
					{:else}
						{@const charIdx = nodes.filter((nn) => nn.type === 'character').indexOf(n)}
						<circle
							cx={n.x} cy={n.y} r="20"
							fill={getCharColor(charIdx)}
							class="char-rect"
						/>
						<text
							x={n.x} y={n.y + 1}
							class="node-label char-graph-label"
							text-anchor="middle"
							dominant-baseline="middle"
						>
							{n.label.charAt(0).toUpperCase()}
						</text>
						<!-- Character name label on hover -->
						{#if hoveredNode === n.id}
							<text
								x={n.x} y={n.y + 30}
								class="char-hover-name"
								text-anchor="middle"
								dominant-baseline="hanging"
							>
								{n.label.length > 14 ? n.label.slice(0, 13) + '\u2026' : n.label}
							</text>
						{/if}
					{/if}
				</g>
			{/each}
				</g>
			</svg>

			<!-- Zoom controls -->
			<div class="zoom-controls">
				<button class="zoom-btn" onclick={() => { scale = Math.min(MAX_SCALE, scale * 1.25); }} title="Zoom in">+</button>
				<button class="zoom-btn" onclick={() => { scale = Math.max(MIN_SCALE, scale * 0.8); }} title="Zoom out">&minus;</button>
				<button class="zoom-btn zoom-reset" onclick={resetView} title="Reset view">1:1</button>
				<span class="zoom-level">{Math.round(scale * 100)}%</span>
			</div>
		</div>
	{/if}
</div>

<style>
	.dashboard-graph {
		margin-top: 32px;
		max-width: 1200px;
		margin-left: auto;
		margin-right: auto;
	}

	.graph-title {
		font-size: 12px;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--text-muted, #9ca3af);
		margin: 0 0 12px;
	}

	.graph-svg {
		width: 100%;
		height: 100%;
		min-height: 400px;
		background-color: var(--sidebar-bg, #111827);
	}

	.graph-viewport {
		position: relative;
		overflow: hidden;
		border: 1px solid var(--border-color, #374151);
		border-radius: 8px;
		cursor: grab;
		height: 500px;
	}

	.viewport-panning {
		cursor: grabbing;
	}

	.graph-loading {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 200px;
		gap: 8px;
		color: var(--text-muted, #9ca3af);
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

	/* ---- Links ---- */
	.dash-link {
		stroke: var(--text-faint, #6b7280);
		stroke-width: 1;
		opacity: 0.3;
	}

	/* ---- Nodes ---- */
	.graph-node {
		cursor: pointer;
		transition: opacity 150ms ease;
	}

	.story-node-card {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
		padding: 6px 10px;
		background-color: var(--hover-bg, #1f2937);
		border: 1px solid var(--border-color, #374151);
		border-radius: 6px;
		transition: background-color 150ms ease, border-color 150ms ease;
		box-sizing: border-box;
	}

	.graph-node:hover .story-node-card {
		background-color: #374151;
		border-color: #6366f1;
	}

	.story-node-title {
		font-size: 11px;
		font-weight: 600;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
		color: var(--text-primary, #e5e7eb);
		text-align: center;
		line-height: 1.3;
		word-wrap: break-word;
		overflow-wrap: break-word;
	}

	.char-rect {
		opacity: 0.85;
		stroke: var(--sidebar-bg, #111827);
		stroke-width: 2;
	}

	.graph-node:hover .char-rect {
		opacity: 1;
		stroke-width: 3;
	}

	.node-label {
		font-size: 11px;
		font-weight: 600;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
		pointer-events: none;
	}

	.char-graph-label {
		fill: #ffffff;
		font-size: 12px;
		font-weight: 700;
	}

	.char-hover-name {
		fill: var(--text-primary, #e5e7eb);
		font-size: 10px;
		font-weight: 600;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
		pointer-events: none;
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
