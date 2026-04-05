<script lang="ts">
	import PositionBadge from '$lib/components/PositionBadge.svelte';
	import StatusBadge from '$lib/components/StatusBadge.svelte';
	import FdrBadge from '$lib/components/FdrBadge.svelte';
	import type { PageData } from './$types';
	import type { Team } from '$lib/api/types';

	let { data }: { data: PageData } = $props();

	const teamMap = $derived(new Map<number, Team>(data.teams.map((t) => [t.id, t])));

	const playerTeam = $derived(teamMap.get(data.player.team_id));

	const positionNames: Record<number, string> = {
		1: 'Goalkeeper',
		2: 'Defender',
		3: 'Midfielder',
		4: 'Forward'
	};
</script>

<svelte:head>
	<title>{data.player.web_name} — fplstat</title>
</svelte:head>

<div class="back">
	<a href="/leaderboard">← Leaderboard</a>
</div>

<!-- Player header card -->
<div class="player-card">
	<div class="player-identity">
		<div class="name-row">
			<h1>{data.player.first_name} {data.player.last_name}</h1>
			<PositionBadge position={data.player.element_type} />
			<StatusBadge status={data.player.status} news={data.player.news} />
		</div>
		<div class="meta">
			<a href="/teams/{data.player.team_id}">{playerTeam?.name ?? '—'}</a>
			&nbsp;·&nbsp;
			{positionNames[data.player.element_type]}
			&nbsp;·&nbsp;
			£{data.player.price.toFixed(1)}m
		</div>
		{#if data.player.news}
			<p class="news">{data.player.news}</p>
		{/if}
	</div>

	<div class="season-stats">
		<div class="stat-card">
			<span class="value">{data.player.total_points}</span>
			<span class="label">Points</span>
		</div>
		<div class="stat-card">
			<span class="value">{data.player.goals_scored}</span>
			<span class="label">Goals</span>
		</div>
		<div class="stat-card">
			<span class="value">{data.player.assists}</span>
			<span class="label">Assists</span>
		</div>
		<div class="stat-card">
			<span class="value">{data.player.clean_sheets}</span>
			<span class="label">CS</span>
		</div>
		<div class="stat-card">
			<span class="value">{data.player.bonus}</span>
			<span class="label">Bonus</span>
		</div>
		<div class="stat-card">
			<span class="value">{data.player.form ?? '—'}</span>
			<span class="label">Form</span>
		</div>
		<div class="stat-card">
			<span class="value">{data.player.points_per_game ?? '—'}</span>
			<span class="label">Pts/GW</span>
		</div>
		<div class="stat-card">
			<span class="value">{data.player.selected_by_percent ?? '—'}%</span>
			<span class="label">Owned</span>
		</div>
	</div>
</div>

<!-- Gameweek breakdown -->
<p class="section-heading">Gameweek Breakdown</p>

{#if data.stats.length === 0}
	<p class="empty">No gameweek data yet.</p>
{:else}
	<div class="table-wrap">
		<table class="data-table">
			<thead>
				<tr>
					<th>GW</th>
					<th>Opponent</th>
					<th>H/A</th>
					<th>Mins</th>
					<th>Pts</th>
					<th>Goals</th>
					<th>Ast</th>
					<th>CS</th>
					<th>Bonus</th>
					<th>BPS</th>
					<th>xPts</th>
					<th>FDR</th>
					<th>Price</th>
				</tr>
			</thead>
			<tbody>
				{#each data.stats as s}
					{@const opponent = teamMap.get(s.opponent_team_id)}
					{@const didNotPlay = s.minutes === 0}
					<tr class:dnp={didNotPlay}>
						<td>{s.gameweek_id}</td>
						<td>
							<a href="/teams/{s.opponent_team_id}">{opponent?.short_name ?? '—'}</a>
						</td>
						<td class:dim={didNotPlay}>{s.was_home ? 'H' : 'A'}</td>
						<td class:dim={didNotPlay}>{s.minutes}</td>
						<td class:dim={didNotPlay} class="num fw">{s.total_points}</td>
						<td class:dim={didNotPlay} class="num">{s.goals_scored}</td>
						<td class:dim={didNotPlay} class="num">{s.assists}</td>
						<td class:dim={didNotPlay} class="num">{s.clean_sheets}</td>
						<td class:dim={didNotPlay} class="num">{s.bonus}</td>
						<td class:dim={didNotPlay} class="num">{s.bps}</td>
						<td class:dim={didNotPlay} class="num">{s.xpts?.toFixed(1) ?? '—'}</td>
						<td><FdrBadge fdr={s.fdr} /></td>
						<td class:dim={didNotPlay}>
							{#if s.price !== null}£{s.price.toFixed(1)}m{:else}—{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}

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

	.player-card {
		background: rgba(255, 255, 255, 0.5);
		border-radius: 10px;
		padding: 1.25rem 1.5rem;
		box-shadow: 2px 2px 6px rgba(255, 255, 255, 0.25);
		margin-bottom: 1.5rem;
	}

	.name-row {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		flex-wrap: wrap;
	}

	.name-row h1 {
		margin: 0;
		font-size: 1.5rem;
		text-align: left;
	}

	.meta {
		font-size: 0.85rem;
		color: rgba(0, 0, 0, 0.55);
		margin-top: 0.3rem;
	}

	.meta a {
		color: var(--color-theme-2);
		text-decoration: none;
	}

	.meta a:hover {
		text-decoration: underline;
	}

	.news {
		font-size: 0.8rem;
		color: #ff8f00;
		margin: 0.4rem 0 0;
	}

	.season-stats {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-top: 1rem;
	}

	.table-wrap {
		overflow-x: auto;
	}

	.empty {
		color: rgba(0, 0, 0, 0.4);
		font-style: italic;
	}

	tr.dnp td {
		opacity: 0.4;
	}

	.num {
		text-align: right;
	}

	.fw {
		font-weight: 700;
	}
</style>
