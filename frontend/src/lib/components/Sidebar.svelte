<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		children,
		side = 'left',
		title = '',
		collapsed = $bindable(false),
		width = '280px'
	}: {
		children: Snippet;
		side?: 'left' | 'right';
		title?: string;
		collapsed?: boolean;
		width?: string;
	} = $props();
</script>

<div
	class="sidebar {side}"
	class:collapsed
	style:width={collapsed ? '40px' : width}
>
	<button
		class="toggle-btn"
		onclick={() => (collapsed = !collapsed)}
		aria-label={collapsed ? `Expand ${title}` : `Collapse ${title}`}
	>
		{#if side === 'left'}
			{collapsed ? '\u25B6' : '\u25C0'}
		{:else}
			{collapsed ? '\u25C0' : '\u25B6'}
		{/if}
	</button>
	{#if !collapsed}
		<div class="sidebar-header">
			<h3>{title}</h3>
		</div>
		<div class="sidebar-content">
			{@render children()}
		</div>
	{/if}
</div>

<style>
	.sidebar {
		display: flex;
		flex-direction: column;
		height: 100%;
		transition: width 200ms ease;
		overflow: hidden;
		flex-shrink: 0;
	}

	.sidebar.left {
		border-right: 1px solid var(--border-color, #374151);
		background-color: var(--sidebar-bg, #111827);
	}

	.sidebar.right {
		border-left: 1px solid var(--border-color, #374151);
		background-color: var(--sidebar-bg, #111827);
	}

	.sidebar.collapsed {
		align-items: center;
	}

	.toggle-btn {
		width: 100%;
		padding: 8px;
		background: none;
		border: none;
		color: var(--text-muted, #9ca3af);
		cursor: pointer;
		font-size: 12px;
		text-align: center;
		flex-shrink: 0;
	}

	.toggle-btn:hover {
		color: var(--text-primary, #e5e7eb);
		background-color: var(--hover-bg, #1f2937);
	}

	.sidebar-header {
		padding: 8px 12px;
		border-bottom: 1px solid var(--border-color, #374151);
		flex-shrink: 0;
	}

	.sidebar-header h3 {
		margin: 0;
		font-size: 12px;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--text-muted, #9ca3af);
	}

	.sidebar-content {
		flex: 1;
		overflow-y: auto;
		padding: 12px;
		color: var(--text-secondary, #d1d5db);
		font-size: 14px;
	}
</style>
