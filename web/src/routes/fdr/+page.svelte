<script lang="ts">
	import { untrack } from 'svelte';
	import { FDR_COLOURS } from '$lib/style';
	import type { Fixture } from '$lib/data';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const teamMap = $derived(new Map<number, string>(data.teamEntries));
	const minGw = $derived(data.gwInfo.min_gw);
	const maxGw = $derived(data.gwInfo.max_gw);
	const fixtures = $derived(data.fixtures);

	// Slider state seeds from the server-provided next_gw on first mount, then
	// lives in component state. untrack tells Svelte the read is intentionally
	// non-reactive — we don't want the slider to jump back when load() reruns.
	let startGw = $state(untrack(() => data.gwInfo.next_gw));
	let endGw = $state(untrack(() => Math.min(data.gwInfo.next_gw + 7, data.gwInfo.max_gw)));

	type Cell = { display: string; fdr: number };
	type Row = { team: string; cells: Map<number, Cell>; avgFdr: number | null };

	function buildMatrix(
		fixtures: Fixture[],
		teamMap: Map<number, string>,
		startGw: number,
		endGw: number
	): { rows: Row[]; gws: number[] } {
		// Aggregate fixtures into one entry per (team, gameweek). For double GWs
		// the fragments are concatenated (matching the Streamlit version) and the
		// FDR used for colouring is the max across that GW's fixtures.
		// Plain Map is correct here: the entire result is recomputed inside $derived,
		// so reactivity flows through the derived value rather than the collections.
		// eslint-disable-next-line svelte/prefer-svelte-reactivity
		const cells = new Map<string, { fragments: string[]; fdr: number }>();
		for (const f of fixtures) {
			if (f.gameweek_id < startGw || f.gameweek_id > endGw) continue;
			const home = teamMap.get(f.team_h_id);
			const away = teamMap.get(f.team_a_id);
			if (!home || !away) continue;

			const homeKey = `${home}|${f.gameweek_id}`;
			const homeFrag = `${away} (H)`;
			const homeCur = cells.get(homeKey);
			if (homeCur) {
				homeCur.fragments.push(homeFrag);
				homeCur.fdr = Math.max(homeCur.fdr, f.team_h_difficulty);
			} else {
				cells.set(homeKey, { fragments: [homeFrag], fdr: f.team_h_difficulty });
			}

			const awayKey = `${away}|${f.gameweek_id}`;
			const awayFrag = `${home} (A)`;
			const awayCur = cells.get(awayKey);
			if (awayCur) {
				awayCur.fragments.push(awayFrag);
				awayCur.fdr = Math.max(awayCur.fdr, f.team_a_difficulty);
			} else {
				cells.set(awayKey, { fragments: [awayFrag], fdr: f.team_a_difficulty });
			}
		}

		const gws: number[] = [];
		for (let g = startGw; g <= endGw; g++) gws.push(g);

		// eslint-disable-next-line svelte/prefer-svelte-reactivity
		const teams = new Set<string>();
		for (const key of cells.keys()) {
			const team = key.split('|')[0];
			if (team) teams.add(team);
		}

		const rows: Row[] = [];
		for (const team of teams) {
			// eslint-disable-next-line svelte/prefer-svelte-reactivity
			const rowCells = new Map<number, Cell>();
			let sum = 0;
			let count = 0;
			for (const gw of gws) {
				const c = cells.get(`${team}|${gw}`);
				if (c) {
					rowCells.set(gw, {
						display: `${c.fragments.join('')} ${c.fdr}`,
						fdr: c.fdr
					});
					sum += c.fdr;
					count += 1;
				} else {
					rowCells.set(gw, { display: '', fdr: 0 });
				}
			}
			rows.push({ team, cells: rowCells, avgFdr: count > 0 ? sum / count : null });
		}

		// Sort by ascending average FDR (easiest schedules at top). Teams with no
		// fixtures in the window (null avg) sort to the bottom.
		rows.sort((a, b) => {
			if (a.avgFdr === null && b.avgFdr === null) return 0;
			if (a.avgFdr === null) return 1;
			if (b.avgFdr === null) return -1;
			return a.avgFdr - b.avgFdr;
		});

		return { rows, gws };
	}

	const matrix = $derived(buildMatrix(fixtures, teamMap, startGw, endGw));

	function cellStyle(fdr: number): string {
		const colours = FDR_COLOURS[fdr];
		return colours ? `background-color: ${colours.bg}; color: ${colours.fg};` : '';
	}
</script>

<svelte:head>
	<title>FDR matrix · fplstat</title>
</svelte:head>

<section>
	<h2>Fixtures</h2>
	<p class="caption">Sorted by average fixture difficulty — easiest schedules at the top</p>

	<div class="filters">
		<label>
			From GW
			<input type="number" min={minGw} max={maxGw} bind:value={startGw} />
		</label>
		<label>
			To GW
			<input type="number" min={minGw} max={maxGw} bind:value={endGw} />
		</label>
	</div>

	{#if matrix.rows.length === 0}
		<p class="info">No fixtures in the selected gameweek range.</p>
	{:else}
		<div class="table-wrap">
			<table>
				<thead>
					<tr>
						<th class="team-col">Team</th>
						{#each matrix.gws as gw (gw)}
							<th>{gw}</th>
						{/each}
					</tr>
				</thead>
				<tbody>
					{#each matrix.rows as row (row.team)}
						<tr>
							<th class="team-col" scope="row">{row.team}</th>
							{#each matrix.gws as gw (gw)}
								{@const cell = row.cells.get(gw)}
								<td style={cell ? cellStyle(cell.fdr) : ''}>{cell?.display ?? ''}</td>
							{/each}
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</section>

<style>
	section {
		max-width: 1200px;
		margin: 0 auto;
		padding: 1rem;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
	}

	h2 {
		margin: 0 0 0.25rem;
	}

	.caption {
		color: #666;
		margin: 0 0 1rem;
		font-size: 0.9rem;
	}

	.filters {
		display: flex;
		gap: 1rem;
		margin-bottom: 1rem;
	}

	.filters label {
		display: flex;
		flex-direction: column;
		font-size: 0.85rem;
		color: #444;
	}

	.filters input {
		width: 6rem;
		padding: 0.25rem 0.5rem;
		font-size: 1rem;
	}

	.info {
		padding: 0.75rem 1rem;
		background: #f3f4f6;
		border-radius: 4px;
		color: #444;
	}

	.table-wrap {
		overflow-x: auto;
	}

	table {
		border-collapse: collapse;
		width: 100%;
		font-size: 0.875rem;
	}

	th,
	td {
		padding: 0.5rem 0.75rem;
		border: 1px solid #e5e7eb;
		text-align: center;
		white-space: nowrap;
	}

	thead th {
		background: #f9fafb;
		font-weight: 600;
	}

	.team-col {
		text-align: left;
		font-weight: 600;
		background: #f9fafb;
		position: sticky;
		left: 0;
	}
</style>
