<script lang="ts">
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const sorted = $derived([...data.teams].sort((a, b) => a.name.localeCompare(b.name)));
</script>

<svelte:head>
	<title>Teams — fplstat</title>
</svelte:head>

<h1>Teams</h1>

<div class="grid">
	{#each sorted as team}
		<a href="/teams/{team.id}" class="team-card">
			<div class="team-name">{team.name}</div>
			<div class="team-short">{team.short_name}</div>
			{#if team.strength_overall_home !== null}
				<div class="strength">
					<span class="strength-label">ATK</span>
					<span>{team.strength_attack_home}</span>
					<span class="strength-label">DEF</span>
					<span>{team.strength_defence_home}</span>
				</div>
			{/if}
		</a>
	{/each}
</div>

<style>
	h1 {
		text-align: left;
		font-size: 1.6rem;
		margin-bottom: 1rem;
	}

	.grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(10rem, 1fr));
		gap: 0.75rem;
	}

	.team-card {
		background: rgba(255, 255, 255, 0.55);
		border-radius: 8px;
		padding: 0.9rem 1rem;
		text-decoration: none;
		color: inherit;
		box-shadow: 1px 1px 4px rgba(255, 255, 255, 0.3);
		transition: box-shadow 0.15s, transform 0.1s;
		display: flex;
		flex-direction: column;
		gap: 0.2rem;
	}

	.team-card:hover {
		box-shadow: 2px 4px 12px rgba(0, 0, 0, 0.1);
		transform: translateY(-1px);
		text-decoration: none;
	}

	.team-name {
		font-weight: 700;
		font-size: 0.85rem;
		color: var(--color-theme-2);
	}

	.team-short {
		font-size: 0.7rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: rgba(0, 0, 0, 0.4);
	}

	.strength {
		display: flex;
		gap: 0.3rem;
		align-items: center;
		margin-top: 0.3rem;
		font-size: 0.75rem;
	}

	.strength-label {
		font-size: 0.6rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: rgba(0, 0, 0, 0.4);
	}
</style>
