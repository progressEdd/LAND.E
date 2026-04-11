<script lang="ts">
	import AnalysisCard from '$lib/components/AnalysisCard.svelte';
	import { generationState } from '$lib/stores/generation.svelte';
	import { storyState } from '$lib/stores/story.svelte';

	let analysis = $derived(generationState.lastAnalysis);
	let hasActiveStory = $derived(!!storyState.activeStoryId);

	function handleExport() {
		if (!storyState.activeStoryId) return;
		window.open(`/api/stories/${storyState.activeStoryId}/export`, '_blank');
	}
</script>

<div class="analysis-panel">
	{#if analysis}
		<div class="cards">
			<!-- 1. Logline -->
			<AnalysisCard title="Logline">
				<p>{analysis.logline}</p>
			</AnalysisCard>

			<!-- 2. Cast -->
			{#if analysis.cast.length > 0}
				<AnalysisCard title="Cast">
					<ul>
						{#each analysis.cast as member}
							<li>
								<strong>{member.name}</strong>
								{#if member.role}
									 — {member.role}
								{/if}
							</li>
						{/each}
					</ul>
				</AnalysisCard>
			{/if}

			<!-- 3. World Rules -->
			{#if analysis.world_rules.length > 0}
				<AnalysisCard title="World Rules">
					<ul>
						{#each analysis.world_rules as rule}
							<li>{rule}</li>
						{/each}
					</ul>
				</AnalysisCard>
			{/if}

			<!-- 4. POV & Tone -->
			<AnalysisCard title="POV & Tone">
				<p>{analysis.pov_tense_tone}</p>
			</AnalysisCard>

			<!-- 5. Timeline -->
			{#if analysis.timeline.length > 0}
				<AnalysisCard title="Timeline">
					<ul>
						{#each analysis.timeline as event}
							<li>{event}</li>
						{/each}
					</ul>
				</AnalysisCard>
			{/if}

			<!-- 6. Current Situation -->
			<AnalysisCard title="Current Situation">
				<p>{analysis.current_situation}</p>
			</AnalysisCard>

			<!-- 7. Active Threads -->
			{#if analysis.active_threads.length > 0}
				<AnalysisCard title="Active Threads">
					<ul>
						{#each analysis.active_threads as thread}
							<li>{thread}</li>
						{/each}
					</ul>
				</AnalysisCard>
			{/if}

			<!-- 8. Continuity Landmines -->
			{#if analysis.continuity_landmines.length > 0}
				<AnalysisCard title="Continuity Landmines" warning>
					<ul>
						{#each analysis.continuity_landmines as mine}
							<li>{mine}</li>
						{/each}
					</ul>
				</AnalysisCard>
			{/if}

			<!-- 9. Ambiguities -->
			{#if analysis.ambiguities.length > 0}
				<AnalysisCard title="Ambiguities">
					<ul>
						{#each analysis.ambiguities as ambiguity}
							<li>{ambiguity}</li>
						{/each}
					</ul>
				</AnalysisCard>
			{/if}

			<!-- 10. Next Paragraph Seeds -->
			{#if analysis.next_paragraph_seeds.length > 0}
				<AnalysisCard title="Next Paragraph Seeds">
					<ol>
						{#each analysis.next_paragraph_seeds as seed}
							<li>{seed}</li>
						{/each}
					</ol>
				</AnalysisCard>
			{/if}
		</div>

		<!-- Export button -->
		<div class="export-section">
			<button
				class="export-btn"
				onclick={handleExport}
				disabled={!hasActiveStory}
			>
				Export Markdown
			</button>
		</div>
	{:else}
		<div class="empty-state">
			<p class="empty-text">Generate a continuation to see story analysis</p>
			{#if hasActiveStory}
				<div class="export-section">
					<button
						class="export-btn"
						onclick={handleExport}
					>
						Export Markdown
					</button>
				</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	.analysis-panel {
		height: 100%;
		overflow-y: auto;
		padding: 0 4px 16px;
	}

	.cards {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 16px;
		padding: 24px 8px;
	}

	.empty-text {
		color: #6b7280;
		font-size: 13px;
		font-style: italic;
		text-align: center;
		margin: 0;
	}

	.export-section {
		padding: 12px 0;
		margin-top: 8px;
	}

	.export-btn {
		width: 100%;
		padding: 8px 16px;
		font-size: 13px;
		font-weight: 500;
		background-color: #4f46e5;
		color: #fff;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		transition: background-color 150ms ease;
	}

	.export-btn:hover:not(:disabled) {
		background-color: #6366f1;
	}

	.export-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
</style>
