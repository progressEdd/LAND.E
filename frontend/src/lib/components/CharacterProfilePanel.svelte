<script lang="ts">
	import { characterState } from '$lib/stores/character.svelte';

	let editName = $state('');
	let editDescription = $state('');
	let editTraits = $state('');
	let editArcSummary = $state('');
	let isEditing = $state(false);
	let isSaving = $state(false);

	// Reset edit state when selected character changes
	$effect(() => {
		const char = characterState.selectedCharacter;
		if (char) {
			editName = char.canonical_name;
			editDescription = char.description ?? '';
			editTraits = char.traits.join(', ');
			editArcSummary = char.arc_summary ?? '';
			isEditing = false;
		}
	});

	function startEdit() {
		const char = characterState.selectedCharacter;
		if (!char) return;
		editName = char.canonical_name;
		editDescription = char.description ?? '';
		editTraits = char.traits.join(', ');
		editArcSummary = char.arc_summary ?? '';
		isEditing = true;
	}

	function cancelEdit() {
		isEditing = false;
	}

	async function saveEdit() {
		const char = characterState.selectedCharacter;
		if (!char) return;
		isSaving = true;
		try {
			await characterState.updateCharacter(char.id, {
				canonical_name: editName.trim() || undefined,
				description: editDescription.trim() || undefined,
				traits: editTraits.split(',').map(t => t.trim()).filter(Boolean),
				arc_summary: editArcSummary.trim() || undefined
			});
			isEditing = false;
		} finally {
			isSaving = false;
		}
	}

	async function deleteCharacter() {
		const char = characterState.selectedCharacter;
		if (!char) return;
		if (confirm(`Delete "${char.canonical_name}"? This cannot be undone.`)) {
			await characterState.deleteCharacter(char.id);
		}
	}

	function close() {
		characterState.closeProfilePanel();
	}
</script>

{#if characterState.selectedCharacter}
	<div class="profile-panel">
		<div class="profile-header">
			<h2>{characterState.selectedCharacter.canonical_name}</h2>
			<button class="close-btn" onclick={close} title="Close">&times;</button>
		</div>

		{#if characterState.error}
			<div class="error-msg">{characterState.error}</div>
		{/if}

		<div class="profile-body">
			{#if isEditing}
				<!-- Edit mode -->
				<div class="field-group">
					<label for="edit-name">Name</label>
					<input id="edit-name" class="input" type="text" bind:value={editName} placeholder="Character name" />
				</div>

				<div class="field-group">
					<label for="edit-desc">Description</label>
					<textarea id="edit-desc" class="input textarea" bind:value={editDescription} placeholder="Character description..."></textarea>
				</div>

				<div class="field-group">
					<label for="edit-traits">Traits <span class="hint">(comma-separated)</span></label>
					<input id="edit-traits" class="input" type="text" bind:value={editTraits} placeholder="brave, curious, stubborn" />
				</div>

				<div class="field-group">
					<label for="edit-arc">Arc Summary</label>
					<textarea id="edit-arc" class="input textarea" bind:value={editArcSummary} placeholder="Character arc across stories..."></textarea>
				</div>

				<div class="actions">
					<button class="btn btn-primary btn-small" onclick={saveEdit} disabled={isSaving}>
						{isSaving ? 'Saving...' : 'Save'}
					</button>
					<button class="btn btn-small" onclick={cancelEdit} disabled={isSaving}>Cancel</button>
				</div>
			{:else}
				<!-- Display mode -->
				<section class="section">
					<h3>Description</h3>
					<p class="body-text">
						{characterState.selectedCharacter.description || 'No description yet'}
					</p>
				</section>

				{#if characterState.selectedCharacter.traits.length > 0}
					<section class="section">
						<h3>Traits</h3>
						<div class="traits-list">
							{#each characterState.selectedCharacter.traits as trait}
								<span class="trait-pill">{trait}</span>
							{/each}
						</div>
					</section>
				{/if}

				<section class="section">
					<h3>Arc Summary</h3>
					<p class="body-text">
						{characterState.selectedCharacter.arc_summary || 'No arc summary yet'}
					</p>
				</section>

				{#if characterState.selectedCharacter.appearances.length > 0}
					<section class="section">
						<h3>Appearances</h3>
						<ul class="appearance-list">
							{#each characterState.selectedCharacter.appearances as appearance}
								<li class="appearance-card">
									<span class="appearance-title">{appearance.story_title}</span>
									{#if appearance.role}
										<span class="appearance-role"> — {appearance.role}</span>
									{/if}
								</li>
							{/each}
						</ul>
					</section>
				{/if}

				{#if characterState.selectedCharacter.aliases.length > 0}
					<section class="section">
						<h3>Aliases</h3>
						<ul class="alias-list">
							{#each characterState.selectedCharacter.aliases as alias}
								<li>
									<span class="alias-name">{alias.raw_name}</span>
									<span class="alias-status {alias.status}">{alias.status}</span>
								</li>
							{/each}
						</ul>
					</section>
				{/if}

				<div class="actions">
					<button class="btn btn-primary btn-small" onclick={startEdit}>Edit</button>
					<button class="btn btn-danger btn-small" onclick={deleteCharacter}>Delete</button>
				</div>
			{/if}
		</div>
	</div>
{/if}

<style>
	.profile-panel {
		width: 400px;
		max-height: calc(100vh - 40px);
		background-color: var(--panel-bg, #030712);
		border: 1px solid var(--border-color, #374151);
		border-radius: 8px;
		display: flex;
		flex-direction: column;
		overflow: hidden;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
	}

	.profile-header {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 14px 16px;
		border-bottom: 1px solid var(--border-color, #374151);
	}

	.profile-header h2 {
		margin: 0;
		font-size: 17px;
		color: var(--text-primary, #e5e7eb);
		flex: 1;
	}

	.close-btn {
		background: none;
		border: none;
		color: var(--text-muted, #9ca3af);
		font-size: 22px;
		cursor: pointer;
		padding: 0 4px;
		line-height: 1;
	}

	.close-btn:hover {
		color: var(--text-primary, #e5e7eb);
	}

	.error-msg {
		padding: 8px 16px;
		background: rgba(239, 68, 68, 0.1);
		color: #ef4444;
		font-size: 13px;
	}

	.profile-body {
		flex: 1;
		overflow-y: auto;
		padding: 12px 16px;
	}

	.section {
		margin-bottom: 16px;
	}

	.section h3 {
		margin: 0 0 6px;
		font-size: 12px;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		color: var(--text-muted, #9ca3af);
	}

	.body-text {
		margin: 0;
		font-size: 14px;
		color: var(--text-secondary, #d1d5db);
		line-height: 1.5;
	}

	.traits-list {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
	}

	.trait-pill {
		display: inline-block;
		padding: 3px 10px;
		font-size: 12px;
		border-radius: 12px;
		background-color: rgba(99, 102, 241, 0.15);
		color: #a5b4fc;
		border: 1px solid rgba(99, 102, 241, 0.3);
	}

	.appearance-list {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.appearance-card {
		padding: 8px 10px;
		margin-bottom: 4px;
		border-radius: 4px;
		background-color: var(--hover-bg, #1f2937);
		font-size: 13px;
	}

	.appearance-title {
		color: var(--text-primary, #e5e7eb);
		font-weight: 500;
	}

	.appearance-role {
		color: var(--text-muted, #9ca3af);
	}

	.alias-list {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.alias-list li {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 4px 0;
		font-size: 13px;
	}

	.alias-name {
		color: var(--text-secondary, #d1d5db);
	}

	.alias-status {
		font-size: 11px;
		padding: 2px 6px;
		border-radius: 8px;
		text-transform: capitalize;
	}

	.alias-status.confirmed {
		background: rgba(34, 197, 94, 0.15);
		color: #86efac;
	}

	.alias-status.suggested {
		background: rgba(234, 179, 8, 0.15);
		color: #fde047;
	}

	.alias-status.split {
		background: rgba(239, 68, 68, 0.15);
		color: #fca5a5;
	}

	.alias-status.rejected {
		background: rgba(107, 114, 128, 0.15);
		color: #9ca3af;
	}

	.field-group {
		margin-bottom: 12px;
	}

	.field-group label {
		display: block;
		font-size: 12px;
		font-weight: 500;
		margin-bottom: 4px;
		color: var(--text-muted, #9ca3af);
	}

	.hint {
		font-weight: 400;
		color: var(--text-faint, #6b7280);
	}

	.input {
		width: 100%;
		padding: 8px 10px;
		font-size: 14px;
		background-color: var(--panel-bg, #030712);
		color: var(--text-primary, #e5e7eb);
		border: 1px solid var(--border-color, #374151);
		border-radius: 4px;
		outline: none;
		box-sizing: border-box;
	}

	.input:focus {
		border-color: #6366f1;
	}

	.textarea {
		resize: vertical;
		min-height: 70px;
		font-family: inherit;
	}

	.actions {
		display: flex;
		gap: 8px;
		margin-top: 16px;
	}

	.btn {
		padding: 6px 12px;
		font-size: 13px;
		border: 1px solid var(--border-color, #374151);
		border-radius: 6px;
		background-color: var(--panel-bg, #030712);
		color: var(--text-primary, #e5e7eb);
		cursor: pointer;
		transition: background-color 150ms ease, border-color 150ms ease;
	}

	.btn:hover:not(:disabled) {
		background-color: var(--hover-bg, #1f2937);
	}

	.btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-primary {
		background-color: #4f46e5;
		border-color: #4f46e5;
		color: #fff;
	}

	.btn-primary:hover:not(:disabled) {
		background-color: #4338ca;
	}

	.btn-danger {
		border-color: #dc2626;
		color: #fca5a5;
	}

	.btn-danger:hover:not(:disabled) {
		background-color: rgba(220, 38, 38, 0.15);
	}

	.btn-small {
		padding: 5px 10px;
		font-size: 12px;
	}
</style>
