<script lang="ts">
	// Placeholder for v2 node graph (Svelte Flow integration)
</script>

<div class="graph-placeholder">
	<div class="placeholder-content">
		<svg
			xmlns="http://www.w3.org/2000/svg"
			width="48"
			height="48"
			viewBox="0 0 24 24"
			fill="none"
			stroke="currentColor"
			stroke-width="1"
			stroke-linecap="round"
			stroke-linejoin="round"
		>
			<circle cx="6" cy="6" r="2" />
			<circle cx="18" cy="6" r="2" />
			<circle cx="6" cy="18" r="2" />
			<circle cx="18" cy="18" r="2" />
			<line x1="8" y1="6" x2="16" y2="6" />
			<line x1="6" y1="8" x2="6" y2="16" />
			<line x1="18" y1="8" x2="18" y2="16" />
			<line x1="8" y1="18" x2="16" y2="18" />
		</svg>
		<p class="placeholder-title">Node Graph</p>
		<p class="placeholder-subtitle">Coming in v2</p>
	</div>
</div>

<style>
	.graph-placeholder {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
		width: 100%;
		background-color: var(--panel-bg, #030712);
	}

	.placeholder-content {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 8px;
		color: var(--text-faint, #6b7280);
	}

	.placeholder-title {
		margin: 0;
		font-size: 16px;
		font-weight: 500;
	}

	.placeholder-subtitle {
		margin: 0;
		font-size: 12px;
		opacity: 0.7;
	}
</style>
