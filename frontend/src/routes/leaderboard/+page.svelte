<script lang="ts">
	import { goto } from '$app/navigation';
	import PositionBadge from '$lib/components/PositionBadge.svelte';
	import type { PageData } from './$types';
	import type { Team } from '$lib/api/types';

	let { data }: { data: PageData } = $props();

	const teamMap = $derived(
		new Map<number, Team>(data.teams.map((t) => [t.id, t]))
	);

	function onNChange(e: Event) {
		const val = Math.min(38, Math.max(1, Number((e.target as HTMLInputElement).value)));
		goto(`?last_n=${val}`, { replaceState: true });
	}
</script>

<svelte:head>
	<title>Leaderboard — fplstat</title>
</svelte:head>

<div class="page-header">
	<h1>Top Performers</h1>
	<div class="controls">
		<label for="last-n">Last</label>
		<input
			id="last-n"
			type="number"
			min="1"
			max="38"
			value={data.lastN}
			onchange={onNChange}
		/>
		<span>gameweek{data.lastN === 1 ? '' : 's'}</span>
	</div>
</div>

<div class="table-wrap">
	<table class="data-table">
		<thead>
			<tr>
				<th>#</th>
				<th>Player</th>
				<th>Pos</th>
				<th>Team</th>
				<th>Price</th>
				<th>GWs</th>
				<th>Pts</th>
			</tr>
		</thead>
		<tbody>
			{#each data.entries as entry, i}
				{@const team = teamMap.get(entry.team_id)}
				<tr>
					<td class="rank">{i + 1}</td>
					<td class="name">
						<a href="/players/{entry.player_id}">{entry.web_name}</a>
					</td>
					<td><PositionBadge position={entry.element_type} /></td>
					<td>{team?.short_name ?? '—'}</td>
					<td>£{entry.price.toFixed(1)}m</td>
					<td class="num">{entry.gameweeks_played}</td>
					<td class="num pts">{entry.points}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>

<style>
	.page-header {
		display: flex;
		align-items: baseline;
		gap: 1.5rem;
		margin-bottom: 1rem;
		flex-wrap: wrap;
	}

	.page-header h1 {
		margin: 0;
		font-size: 1.6rem;
		text-align: left;
	}

	.controls {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.9rem;
		color: rgba(0, 0, 0, 0.6);
	}

	.controls input {
		width: 4rem;
		padding: 0.25rem 0.5rem;
		border: 1px solid rgba(0, 0, 0, 0.2);
		border-radius: 6px;
		background: rgba(255, 255, 255, 0.6);
		text-align: center;
		font-size: 0.9rem;
	}

	.table-wrap {
		overflow-x: auto;
	}

	.rank {
		color: rgba(0, 0, 0, 0.35);
		font-size: 0.8rem;
		width: 2rem;
	}

	.name a {
		font-weight: 600;
		color: var(--color-theme-2);
		text-decoration: none;
	}

	.name a:hover {
		text-decoration: underline;
	}

	.num {
		text-align: right;
	}

	.pts {
		font-weight: 700;
		font-size: 1rem;
	}
</style>
