<script lang="ts">
	import PositionBadge from '$lib/components/PositionBadge.svelte';
	import StatusBadge from '$lib/components/StatusBadge.svelte';
	import type { PageData } from './$types';
	import type { Player, Position } from '$lib/api/types';

	let { data }: { data: PageData } = $props();

	const positionOrder: Position[] = [1, 2, 3, 4];
	const positionNames: Record<Position, string> = {
		1: 'Goalkeepers',
		2: 'Defenders',
		3: 'Midfielders',
		4: 'Forwards'
	};

	const byPosition = $derived(
		positionOrder.reduce(
			(acc, pos) => {
				acc[pos] = data.players
					.filter((p) => p.element_type === pos)
					.sort((a, b) => b.total_points - a.total_points);
				return acc;
			},
			{} as Record<Position, Player[]>
		)
	);
</script>

<svelte:head>
	<title>{data.team.name} — fplstat</title>
</svelte:head>

<div class="back">
	<a href="/teams">← All Teams</a>
</div>

<div class="team-header">
	<h1>{data.team.name}</h1>
	<span class="short">{data.team.short_name}</span>
</div>

{#each positionOrder as pos}
	{@const players = byPosition[pos]}
	{#if players.length > 0}
		<p class="section-heading">{positionNames[pos]}</p>
		<div class="table-wrap">
			<table class="data-table">
				<thead>
					<tr>
						<th>Player</th>
						<th>Price</th>
						<th>Pts</th>
						<th>Form</th>
						<th>Pts/GW</th>
						<th>Sel%</th>
						<th>Goals</th>
						<th>Ast</th>
						<th>CS</th>
						<th>Mins</th>
					</tr>
				</thead>
				<tbody>
					{#each players as p}
						<tr>
							<td class="name">
								<a href="/players/{p.id}">{p.web_name}</a>
								<StatusBadge status={p.status} news={p.news} />
							</td>
							<td>£{p.price.toFixed(1)}m</td>
							<td class="num fw">{p.total_points}</td>
							<td class="num">{p.form ?? '—'}</td>
							<td class="num">{p.points_per_game ?? '—'}</td>
							<td class="num">{p.selected_by_percent ?? '—'}%</td>
							<td class="num">{p.goals_scored}</td>
							<td class="num">{p.assists}</td>
							<td class="num">{p.clean_sheets}</td>
							<td class="num">{p.minutes}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
{/each}

<style>
	.back {
		margin-bottom: 1rem;
		font-size: 0.85rem;
	}

	.back a {
		color: rgba(0, 0, 0, 0.5);
		text-decoration: none;
	}

	.back a:hover {
		color: var(--color-theme-1);
	}

	.team-header {
		display: flex;
		align-items: baseline;
		gap: 0.75rem;
		margin-bottom: 1rem;
	}

	.team-header h1 {
		margin: 0;
		font-size: 1.6rem;
		text-align: left;
	}

	.short {
		font-size: 0.85rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: rgba(0, 0, 0, 0.4);
		font-weight: 700;
	}

	.table-wrap {
		overflow-x: auto;
		margin-bottom: 0.5rem;
	}

	.name {
		display: flex;
		align-items: center;
		gap: 0.4rem;
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

	.fw {
		font-weight: 700;
	}
</style>
