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
			.force('link', forceLink<SimNode, SimLink>(graphLinks as any).id((d: any) => d.id).distance(80))
			.force('charge', forceManyBody().strength(-200))
			.force('center', forceCenter(300, 150))
			.force('collide', forceCollide<SimNode>().radius(40) as any)
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

	function handleNodeClick(node: GraphNode): void {
		if (node.type === 'story') {
			storyState.setActiveStory(node.id);
		}
		// Character nodes don't navigate anywhere
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
		<svg class="graph-svg" viewBox="0 0 600 300" preserveAspectRatio="xMidYMid meet">
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
						<rect
							x={n.x - 40} y={n.y - 16}
							width="80" height="32"
							rx="6"
							class="story-rect"
						/>
						<text
							x={n.x} y={n.y + 1}
							class="node-label story-label"
							text-anchor="middle"
							dominant-baseline="middle"
						>
							{n.label.length > 12 ? n.label.slice(0, 11) + '\u2026' : n.label}
						</text>
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
					{/if}
				</g>
			{/each}
		</svg>
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
		height: 300px;
		background-color: var(--sidebar-bg, #111827);
		border: 1px solid var(--border-color, #374151);
		border-radius: 8px;
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

	.story-rect {
		fill: var(--hover-bg, #1f2937);
		stroke: var(--border-color, #374151);
		stroke-width: 1.5;
		transition: fill 150ms ease, stroke 150ms ease;
	}

	.graph-node:hover .story-rect {
		fill: #374151;
		stroke: #6366f1;
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

	.story-label {
		fill: var(--text-primary, #e5e7eb);
	}

	.char-graph-label {
		fill: #ffffff;
		font-size: 12px;
		font-weight: 700;
	}
</style>
