<script lang="ts">
	import { onMount } from 'svelte';
	import { forceSimulation, forceLink, forceManyBody, forceCenter, forceCollide } from 'd3-force';
	import type { StoryOverviewResponse, StoryOverviewStory, StoryOverviewCharacter, StoryOverviewCanonicalCharacter } from '$lib/types';
	import { api } from '$lib/api/rest';
	import { storyState } from '$lib/stores/story.svelte';
	import { characterState } from '$lib/stores/character.svelte';

	// ---- Types ----
	interface GraphNode {
		id: string;
		label: string;
		type: 'story' | 'character' | 'linked_character';
		x: number;
		y: number;
		fx?: number | null;
		fy?: number | null;
		canonical_id?: string;
		story_count?: number;
		color?: string;
	}

	interface GraphLink {
		source: string | GraphNode;
		target: string | GraphNode;
	}

	interface SimNode {
		id: string;
		label: string;
		type: 'story' | 'character' | 'linked_character';
		x: number;
		y: number;
		canonical_id?: string;
		story_count?: number;
		color?: string;
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

	let colorIdx = 0;
	function nextColor(): string {
		return PALETTE[colorIdx++ % PALETTE.length];
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

	// Expose refresh for parent components
	export function refreshGraph(): void {
		loadGraph();
	}

	function buildGraph(data: StoryOverviewResponse): void {
		if (data.stories.length === 0 && data.characters.length === 0 && (data.canonical_characters ?? []).length === 0) {
			nodes = [];
			links = [];
			return;
		}

		colorIdx = 0;

		// Create nodes
		const graphNodes: SimNode[] = [
			...data.stories.map((s) => ({
				id: s.id,
				label: s.title,
				type: 'story' as const,
				x: 0,
				y: 0,
			})),
		];

		const graphLinks: SimLink[] = [];

		// Process canonical (linked) characters FIRST — they get colors first
		for (const cc of data.canonical_characters ?? []) {
			const color = nextColor();
			graphNodes.push({
				id: `canonical:${cc.id}`,
				label: cc.canonical_name,
				type: 'linked_character',
				x: 0,
				y: 0,
				canonical_id: cc.id,
				story_count: cc.story_ids.length,
				color,
			});
			// Links to all stories
			for (const sid of cc.story_ids) {
				graphLinks.push({
					source: `canonical:${cc.id}`,
					target: sid,
				});
			}
		}

		// Process remaining (unlinked) raw characters
		for (const c of data.characters) {
			const color = nextColor();
			graphNodes.push({
				id: `char:${c.name}`,
				label: c.name,
				type: 'character' as const,
				x: 0,
				y: 0,
				color,
			});
			for (const sid of c.story_ids) {
				graphLinks.push({
					source: `char:${c.name}`,
					target: sid,
				});
			}
		}

		// Adaptive force parameters based on graph size
		const nodeCount = graphNodes.length;
		const isLargeGraph = nodeCount > 15;
		const baseLinkDistance = isLargeGraph ? 120 : 100;
		const chargeStrength = isLargeGraph ? -200 : -120;

		// Run force simulation with adjusted parameters
		const simulation = forceSimulation<SimNode>(graphNodes as any)
			.force('link', forceLink<SimNode, SimLink>(graphLinks as any)
				.id((d: any) => d.id)
				.distance((d: any) => {
					const sourceId = typeof d.source === 'object' ? d.source.id : d.source;
				return sourceId.startsWith('canonical:') ? baseLinkDistance * 0.8 : baseLinkDistance;
				})
			)
			.force('charge', forceManyBody().strength((d: any) => {
				if (d.type === 'story') return chargeStrength;
				if (d.type === 'linked_character') return chargeStrength * 0.8;
				return chargeStrength * 0.6; // Raw characters: less repulsion
			}))
			.force('center', forceCenter(isLargeGraph ? 400 : 300, isLargeGraph ? 200 : 150))
			.force('collide', forceCollide<SimNode>().radius((d: any) => {
				if (d.type === 'story') return 95;  // story card is 180×80, so diagonal ≈ 99
				if (d.type === 'linked_character') return 40;  // outer ring r=34
				return 28;
			}).strength(0.9) as any)
			.stop();

		// Increase tick count for larger graphs
		const tickCount = isLargeGraph ? 200 : 120;
		for (let i = 0; i < tickCount; i++) {
			simulation.tick();
		}

		// Extract positions
		const positioned: GraphNode[] = graphNodes.map((n) => ({
			id: n.id,
			label: n.label,
			type: n.type,
			x: n.x ?? 0,
			y: n.y ?? 0,
			canonical_id: n.canonical_id,
			story_count: n.story_count,
			color: n.color,
		}));

		// Offset positions to start from (50, 50)
		const PAD = 50;
		const minX = Math.min(...positioned.map((n) => n.x));
		const minY = Math.min(...positioned.map((n) => n.y));
		for (const n of positioned) {
			n.x = n.x - minX + PAD;
			n.y = n.y - minY + PAD;
		}

		// Auto-fit: scale so the graph fills ~70% of the viewport (comfortable zoom,
		// some characters may flow off-screen — user can pan to explore)
		const maxX = Math.max(...positioned.map((n) => n.x));
		const maxY = Math.max(...positioned.map((n) => n.y));
		const graphW = maxX + PAD;
		const graphH = maxY + PAD;

		const vpW = 800;
		const vpH = 500;

		const fitScaleX = vpW / graphW;
		const fitScaleY = vpH / graphH;
		// Use 0.7 of the full fit — intentionally clips edges for a comfortable zoom
		const rawFit = Math.min(fitScaleX, fitScaleY, 1.0);
		autoFitScale = Math.min(rawFit / 0.7, 1.0);

		// Center the graph
		const scaledW = graphW * autoFitScale;
		const scaledH = graphH * autoFitScale;
		autoFitPanX = (vpW - scaledW) / 2;
		autoFitPanY = (vpH - scaledH) / 2;

		scale = autoFitScale;
		panX = autoFitPanX;
		panY = autoFitPanY;

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

	function getNodeColor(n: GraphNode): string {
		return n.color ?? '#94a3b8';
	}

	// ---- Zoom & Pan state ----
	let scale = $state(1);
	let panX = $state(0);
	let panY = $state(0);
	let autoFitScale = 1;
	let autoFitPanX = 0;
	let autoFitPanY = 0;
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
	let activeMenuNodeId = $state<string | null>(null);
	let activeMenuPos = $state<{ x: number; y: number }>({ x: 0, y: 0 });
	let showLinkDropdown = $state(false);

	// Extract raw name and story IDs from character node
	function getCharNodeDetails(node: GraphNode): { rawName: string; storyIds: string[] } | null {
		if (node.type !== 'character') return null;
		// node.id is "char:Name" and node.label is the full raw name
		// Find story IDs from links
		const storyIds = links
			.filter(l => {
				const src = typeof l.source === 'string' ? l.source : (l.source as GraphNode).id;
				return src === node.id;
			})
			.map(l => {
				const tgt = typeof l.target === 'string' ? l.target : (l.target as GraphNode).id;
				return tgt;
			});
		return { rawName: node.label, storyIds };
	}

	async function linkToExisting(canonicalId: string): Promise<void> {
		if (!activeMenuNodeId) return;
		const node = nodes.find(n => n.id === activeMenuNodeId);
		if (!node) return;
		const details = getCharNodeDetails(node);
		if (!details || details.storyIds.length === 0) return;

		try {
			await api.linkMention(canonicalId, details.rawName, details.storyIds[0]);
			activeMenuNodeId = null;
			showLinkDropdown = false;
			await Promise.all([characterState.loadCandidates(), characterState.loadCharacters()]);
			loadGraph();
			refreshAfterGraphOp?.();
		} catch (e) {
			characterState.error = e instanceof Error ? e.message : String(e);
		}
	}

	async function createAsNew(): Promise<void> {
		if (!activeMenuNodeId) return;
		const node = nodes.find(n => n.id === activeMenuNodeId);
		if (!node) return;
		const details = getCharNodeDetails(node);
		if (!details || details.storyIds.length === 0) return;

		try {
			await api.linkCharacters({
				canonical_name: details.rawName,
				mentions: details.storyIds.map(sid => ({ raw_name: details.rawName, story_id: sid }))
			});
			activeMenuNodeId = null;
			showLinkDropdown = false;
			await characterState.loadCandidates();
			await characterState.loadCharacters();
			loadGraph();
			refreshAfterGraphOp?.();
		} catch (e) {
			characterState.error = e instanceof Error ? e.message : String(e);
		}
	}

	function closeMenu(): void {
		activeMenuNodeId = null;
		showLinkDropdown = false;
	}

	// Optional callback for Dashboard to refresh after graph operations
	let refreshAfterGraphOp: (() => void) | undefined = $state(undefined);

	function handlePointerDown(e: PointerEvent): void {
		if (e.button === 0) {
			isPanning = true;
			didDrag = false;
			panStartX = e.clientX;
			panStartY = e.clientY;
			panStartPanX = panX;
			panStartPanY = panY;
			panStartPointerId = e.pointerId;
		}
	}

	function handlePointerMove(e: PointerEvent): void {
		if (!isPanning) return;
		const dx = e.clientX - panStartX;
		const dy = e.clientY - panStartY;
		if (!didDrag && (Math.abs(dx) > 3 || Math.abs(dy) > 3)) {
			didDrag = true;
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
		if (didDrag) return;
		if (node.type === 'story') {
			storyState.setActiveStory(node.id);
		} else if (node.type === 'linked_character' && node.canonical_id) {
			characterState.selectCharacter(node.canonical_id);
		} else if (node.type === 'character') {
			// Show context menu for unlinked character
			activeMenuNodeId = node.id;
			activeMenuPos = { x: node.x + 20, y: node.y };
			showLinkDropdown = false;
		}
		// Close any other open menus
		if (node.type !== 'character') {
			closeMenu();
		}
	}

	function resetView(): void {
		scale = autoFitScale;
		panX = autoFitPanX;
		panY = autoFitPanY;
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
		<!-- No graph when no stories exist -->
	{:else}
		<h4 class="graph-title">Story Universe</h4>
		{#if !nodes.some(n => n.type === 'character' || n.type === 'linked_character')}
			<p class="graph-empty-msg">Generate stories to see character connections</p>
		{/if}
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
			<svg class="graph-svg" viewBox="0 0 800 500" preserveAspectRatio="xMidYMid meet">
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
					{:else if n.type === 'linked_character'}
						<!-- Outer ring (double-ring effect) -->
						<circle
							cx={n.x} cy={n.y} r="34"
							fill="none"
							stroke={getNodeColor(n)}
							stroke-width="2"
							opacity="0.4"
							class="char-rect"
						/>
						<!-- Main circle -->
						<circle
							cx={n.x} cy={n.y} r="28"
							fill={getNodeColor(n)}
							class="char-rect linked-char"
						/>
						<!-- First letter label -->
						<text
							x={n.x} y={n.y + 1}
							class="node-label char-graph-label linked-label"
							text-anchor="middle"
							dominant-baseline="middle"
						>
							{n.label.charAt(0).toUpperCase()}
						</text>
						<!-- Story count badge -->
						{#if n.story_count && n.story_count > 1}
							<circle
								cx={n.x + 22} cy={n.y - 22} r="10"
								fill="#4f46e5"
								class="count-badge-bg"
							/>
							<text
								x={n.x + 22} y={n.y - 21}
								class="count-badge-text"
								text-anchor="middle"
								dominant-baseline="middle"
							>
								{n.story_count}
							</text>
						{/if}
						<!-- Hover name -->
						{#if hoveredNode === n.id}
							<text
								x={n.x} y={n.y + 44}
								class="char-hover-name"
								text-anchor="middle"
								dominant-baseline="hanging"
							>
								{n.label.length > 18 ? n.label.slice(0, 17) + '\u2026' : n.label} ({n.story_count} stories)
							</text>
						{/if}
					{:else}
						<!-- Regular (unlinked) character node -->
						<circle
							cx={n.x} cy={n.y} r="20"
							fill={getNodeColor(n)}
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

			<!-- Character context menu (for unlinked characters) -->
			{#if activeMenuNodeId}
				<div class="char-menu" style="left: {activeMenuPos.x * scale + panX}px; top: {activeMenuPos.y * scale + panY}px">
					<button class="menu-item" onclick={() => (showLinkDropdown = true)}>
						Link to existing character
					</button>
					{#if showLinkDropdown}
						<div class="link-dropdown">
							{#if characterState.canonicalCharacters.length === 0}
								<div class="dropdown-empty">No existing characters — use "Create as new" first</div>
							{:else}
								{#each characterState.canonicalCharacters as cc}
									<button class="dropdown-item" onclick={() => linkToExisting(cc.id)}>
										{cc.canonical_name} ({cc.story_count} stories)
									</button>
								{/each}
							{/if}
						</div>
					{/if}
					{#if characterState.error}
						<div class="menu-error">{characterState.error}</div>
					{/if}
					<button class="menu-item" onclick={createAsNew}>
						Create as new character
					</button>
					<button class="menu-item menu-cancel" onclick={closeMenu}>
						Cancel
					</button>
				</div>
			{/if}
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

	.graph-empty-msg {
		font-size: 13px;
		color: var(--text-faint, #6b7280);
		margin: 0 0 8px;
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

	.linked-char {
		opacity: 0.9;
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

	.linked-label {
		font-size: 15px;
	}

	.char-hover-name {
		fill: var(--text-primary, #e5e7eb);
		font-size: 10px;
		font-weight: 600;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
		pointer-events: none;
	}

	.count-badge-bg {
		pointer-events: none;
	}

	.count-badge-text {
		fill: #ffffff;
		font-size: 9px;
		font-weight: 700;
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

	/* ---- Character context menu ---- */
	.char-menu {
		position: absolute;
		z-index: 20;
		min-width: 180px;
		background-color: var(--sidebar-bg, #111827);
		border: 1px solid var(--border-color, #374151);
		border-radius: 6px;
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
		padding: 4px 0;
	}

	.menu-item {
		display: block;
		width: 100%;
		padding: 8px 12px;
		font-size: 13px;
		text-align: left;
		background: none;
		border: none;
		color: var(--text-primary, #e5e7eb);
		cursor: pointer;
	}

	.menu-item:hover {
		background-color: var(--hover-bg, #1f2937);
	}

	.menu-cancel {
		color: var(--text-muted, #9ca3af);
		border-top: 1px solid var(--border-color, #374151);
		margin-top: 4px;
		padding-top: 8px;
	}

	.link-dropdown {
		max-height: 150px;
		overflow-y: auto;
		border-top: 1px solid var(--border-color, #374151);
	}

	.dropdown-item {
		display: block;
		width: 100%;
		padding: 6px 12px;
		font-size: 12px;
		text-align: left;
		background: none;
		border: none;
		color: var(--text-secondary, #d1d5db);
		cursor: pointer;
	}

	.dropdown-item:hover {
		background-color: var(--hover-bg, #1f2937);
		color: var(--text-primary, #e5e7eb);
	}

	.dropdown-empty {
		padding: 8px 12px;
		font-size: 12px;
		color: var(--text-faint, #6b7280);
	}

	.menu-error {
		padding: 8px 12px;
		font-size: 12px;
		color: #ef4444;
		background: rgba(239, 68, 68, 0.1);
	}
</style>
