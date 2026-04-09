<script lang="ts">
	import '../app.css';
	import { Splitpanes, Pane } from 'svelte-splitpanes';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import NodeGraph from '$lib/components/NodeGraph.svelte';
	import SettingsPanel from '$lib/components/SettingsPanel.svelte';
	import AnalysisPanel from '$lib/components/AnalysisPanel.svelte';
	import { themeState } from '$lib/stores/theme.svelte';

	let { children } = $props();

	let leftCollapsed = $state(false);
	let rightCollapsed = $state(false);
</script>

<div class="app-shell" class:dark={themeState.isDark}>
	<!-- Left Sidebar: Settings -->
	<Sidebar side="left" title="Settings" bind:collapsed={leftCollapsed}>
		<SettingsPanel />
	</Sidebar>

	<!-- Main Content: Split Pane (Editor + Graph) -->
	<div class="main-content">
		<!-- Top Bar -->
		<div class="top-bar">
			<span class="app-title">AI Story Writer</span>
			<button class="theme-toggle" onclick={() => themeState.toggle()} aria-label="Toggle theme">
				{themeState.isDark ? '\u2600\uFE0F' : '\uD83C\uDF19'}
			</button>
		</div>

		<!-- Split Pane Area -->
		<div class="split-area">
			<Splitpanes theme="custom-theme">
				<Pane minSize={30} size={60}>
					<div class="pane-content">
						{@render children()}
					</div>
				</Pane>
				<Pane minSize={20}>
					<div class="pane-content">
						<NodeGraph />
					</div>
				</Pane>
			</Splitpanes>
		</div>
	</div>

	<!-- Right Sidebar: Story Analysis -->
	<Sidebar side="right" title="Story Analysis" bind:collapsed={rightCollapsed}>
		<AnalysisPanel />
	</Sidebar>
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
	}

	.app-shell {
		display: flex;
		height: 100vh;
		overflow: hidden;
		background-color: #030712;
		color: #e5e7eb;
	}

	.app-shell:not(.dark) {
		background-color: #ffffff;
		color: #1f2937;
	}

	.main-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		min-width: 0;
		overflow: hidden;
	}

	.top-bar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 6px 16px;
		border-bottom: 1px solid #374151;
		background-color: #111827;
		flex-shrink: 0;
	}

	.app-shell:not(.dark) .top-bar {
		background-color: #f9fafb;
		border-bottom-color: #e5e7eb;
	}

	.app-title {
		font-size: 13px;
		font-weight: 600;
		color: #9ca3af;
		letter-spacing: 0.02em;
	}

	.app-shell:not(.dark) .app-title {
		color: #6b7280;
	}

	.theme-toggle {
		background: none;
		border: 1px solid #374151;
		border-radius: 6px;
		padding: 4px 10px;
		cursor: pointer;
		font-size: 14px;
		color: #e5e7eb;
		transition: background-color 150ms ease;
	}

	.theme-toggle:hover {
		background-color: #1f2937;
	}

	.app-shell:not(.dark) .theme-toggle {
		border-color: #d1d5db;
		color: #1f2937;
	}

	.app-shell:not(.dark) .theme-toggle:hover {
		background-color: #f3f4f6;
	}

	.split-area {
		flex: 1;
		overflow: hidden;
	}

	.pane-content {
		height: 100%;
		width: 100%;
		overflow: auto;
	}

	/* Splitpanes custom theme */
	:global(.custom-theme.splitpanes) {
		height: 100%;
	}

	:global(.custom-theme .splitpanes__splitter) {
		background-color: var(--border-color, #374151);
		width: 4px;
		border: none;
		margin: 0;
	}

	:global(.custom-theme .splitpanes__splitter:hover) {
		background-color: #6366f1;
	}

	:global(.custom-theme .splitpanes__splitter::before),
	:global(.custom-theme .splitpanes__splitter::after) {
		display: none;
	}

	/* Light theme sidebar overrides via CSS custom properties */
	.app-shell:not(.dark) {
		--sidebar-bg: #f9fafb;
		--border-color: #e5e7eb;
		--text-primary: #1f2937;
		--text-secondary: #4b5563;
		--text-muted: #6b7280;
		--text-faint: #9ca3af;
		--hover-bg: #f3f4f6;
		--panel-bg: #ffffff;
		--seed-stroke: #b45309;
		--seed-stroke-hover: #92400e;
		--seed-hover-bg: rgba(180, 83, 9, 0.15);
	}

	.app-shell.dark {
		--sidebar-bg: #111827;
		--border-color: #374151;
		--text-primary: #e5e7eb;
		--text-secondary: #d1d5db;
		--text-muted: #9ca3af;
		--text-faint: #6b7280;
		--hover-bg: #1f2937;
		--panel-bg: #030712;
		--seed-stroke: #fbbf24;
		--seed-stroke-hover: #f59e0b;
		--seed-hover-bg: rgba(251, 191, 36, 0.2);
	}
</style>
