<script lang="ts">
	let { title, warning = false, children } = $props<{
		title: string;
		warning?: boolean;
		children: import('svelte').Snippet;
	}>();

	let collapsed = $state(false);
</script>

<div class="card">
	<button class="card-header" onclick={() => (collapsed = !collapsed)}>
		<span class="card-title" class:warning>{title}</span>
		<span class="collapse-icon">{collapsed ? '\u25B6' : '\u25BC'}</span>
	</button>
	{#if !collapsed}
		<div class="card-content" class:warning>
			{@render children()}
		</div>
	{/if}
</div>

<style>
	.card {
		background-color: #1f2937;
		border: 1px solid #374151;
		border-radius: 8px;
		overflow: hidden;
	}

	.card-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		width: 100%;
		padding: 8px 12px;
		background: none;
		border: none;
		cursor: pointer;
		text-align: left;
	}

	.card-header:hover {
		background-color: #374151;
	}

	.card-title {
		font-size: 11px;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: #9ca3af;
	}

	.card-title.warning {
		color: #f59e0b;
	}

	.collapse-icon {
		font-size: 10px;
		color: #6b7280;
	}

	.card-content {
		padding: 8px 12px 12px;
		font-size: 13px;
		line-height: 1.6;
		color: #e5e7eb;
	}

	.card-content.warning {
		color: #fbbf24;
	}

	.card-content :global(ul) {
		margin: 0;
		padding-left: 16px;
		list-style: disc;
	}

	.card-content :global(li) {
		margin: 2px 0;
	}

	.card-content :global(ol) {
		margin: 0;
		padding-left: 16px;
	}

	.card-content :global(p) {
		margin: 0;
	}

	.card-content :global(strong) {
		color: #f3f4f6;
	}
</style>
