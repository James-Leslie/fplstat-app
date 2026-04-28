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
		// fixtures in the window (null avg) sort to the bottom. Ties break
		// alphabetically by team — matches the Streamlit version, which inherits
		// alphabetical order from pandas groupby.
		rows.sort((a, b) => {
			const av = a.avgFdr ?? Infinity;
			const bv = b.avgFdr ?? Infinity;
			if (av !== bv) return av - bv;
			return a.team.localeCompare(b.team);
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
		max-width: 1280px;
		margin: 0 auto;
		padding: 1.25rem 1rem 2rem;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
		color: #1f2937;
	}

	h2 {
		margin: 0 0 0.25rem;
		font-size: 1.5rem;
	}

	.caption {
		color: #6b7280;
		margin: 0 0 1rem;
		font-size: 0.85rem;
	}

	.filters {
		display: flex;
		gap: 0.75rem;
		margin-bottom: 0.75rem;
		align-items: flex-end;
	}

	.filters label {
		display: flex;
		flex-direction: column;
		gap: 0.2rem;
		font-size: 0.75rem;
		color: #6b7280;
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	.filters input {
		width: 5rem;
		padding: 0.35rem 0.5rem;
		font-size: 0.9rem;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		background: #fff;
		color: #111827;
	}

	.filters input:focus-visible {
		outline: 2px solid #2563eb;
		outline-offset: 1px;
		border-color: transparent;
	}

	.info {
		padding: 0.75rem 1rem;
		background: #f3f4f6;
		border-radius: 6px;
		color: #4b5563;
	}

	.table-wrap {
		overflow-x: auto;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
		background: #fff;
	}

	table {
		border-collapse: separate;
		border-spacing: 0;
		width: 100%;
		font-size: 0.8125rem;
		font-variant-numeric: tabular-nums;
	}

	th,
	td {
		padding: 0.4rem 0.625rem;
		text-align: left;
		white-space: nowrap;
		border-bottom: 1px solid #f1f5f9;
	}

	tbody tr:last-child th,
	tbody tr:last-child td {
		border-bottom: none;
	}

	thead th {
		background: #f9fafb;
		font-weight: 600;
		color: #6b7280;
		text-transform: uppercase;
		font-size: 0.7rem;
		letter-spacing: 0.05em;
		border-bottom: 1px solid #e5e7eb;
	}

	.team-col {
		font-weight: 600;
		font-size: 0.8125rem;
		color: #111827;
		background: #fff;
		position: sticky;
		left: 0;
		z-index: 1;
		/* Subtle shadow on the right edge separates the sticky column from the
		   horizontally scrolling fixtures, mirroring Streamlit's table chrome. */
		box-shadow: inset -1px 0 0 #e5e7eb;
	}

	thead .team-col {
		background: #f9fafb;
	}
</style>
