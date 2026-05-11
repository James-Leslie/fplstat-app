import type { DB } from './supabase';

export type Fixture = {
	gameweek_id: number;
	team_h_id: number;
	team_a_id: number;
	team_h_difficulty: number;
	team_a_difficulty: number;
	finished: boolean;
};

export type GameweekInfo = {
	min_gw: number;
	max_gw: number;
	next_gw: number;
};

// Team short codes (e.g. ARS, LIV) sourced from public.teams so the list
// stays accurate across promotions and relegations without touching this file.
export async function fetchTeams(client: DB): Promise<string[]> {
	const { data, error } = await client.from('teams').select('short_name');
	if (error) throw error;
	return data
		.map((r) => r.short_name)
		.filter((s): s is string => s !== null)
		.sort();
}

// Map team id → short_name (e.g. {1: 'ARS', 2: 'AVL', …}).
export async function fetchTeamIdMap(client: DB): Promise<Map<number, string>> {
	const { data, error } = await client.from('teams').select('id, short_name');
	if (error) throw error;
	const map = new Map<number, string>();
	for (const row of data) {
		if (row.id !== null && row.short_name !== null) map.set(row.id, row.short_name);
	}
	return map;
}

// All fixtures with the columns needed for the FDR matrix.
export async function fetchFixtures(client: DB): Promise<Fixture[]> {
	const { data, error } = await client
		.from('fixtures')
		.select('gameweek_id, team_h_id, team_a_id, team_h_difficulty, team_a_difficulty, finished');
	if (error) throw error;
	// Drop any rows where required fields are null (shouldn't happen in practice
	// but the view types are nullable because Postgres views can't carry NOT NULL).
	return data.filter(
		(r): r is Fixture =>
			r.gameweek_id !== null &&
			r.team_h_id !== null &&
			r.team_a_id !== null &&
			r.team_h_difficulty !== null &&
			r.team_a_difficulty !== null &&
			r.finished !== null
	);
}

// Min/max GW ids and the next GW id (for slider defaults).
export async function fetchGameweekInfo(client: DB): Promise<GameweekInfo> {
	const { data, error } = await client.from('gameweeks').select('id, is_next');
	if (error) throw error;
	const ids = data.map((r) => r.id).filter((id): id is number => id !== null);
	if (ids.length === 0) throw new Error('No gameweeks returned from database');
	const next = data.find((r) => r.is_next)?.id ?? Math.max(...ids);
	return {
		min_gw: Math.min(...ids),
		max_gw: Math.max(...ids),
		next_gw: next
	};
}

// Timestamp of the most recent successful ETL run, or null.
export async function fetchLastUpdated(client: DB): Promise<Date | null> {
	const { data, error } = await client.from('etl_last_updated').select('finished_at');
	if (error) throw error;
	const first = data[0];
	return first?.finished_at ? new Date(first.finished_at) : null;
}
