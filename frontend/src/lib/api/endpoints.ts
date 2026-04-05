import { apiFetch } from './client';
import type { Team, Gameweek, Player, Fixture, PlayerGameweekStats, LeaderboardEntry } from './types';

export const getTeams = () => apiFetch<Team[]>('/teams');

export const getGameweeks = () => apiFetch<Gameweek[]>('/gameweeks');

export const getFixtures = (gameweek_id?: number) =>
	apiFetch<Fixture[]>('/fixtures', gameweek_id !== undefined ? { gameweek_id } : undefined);

export const getPlayers = (opts?: {
	team_id?: number;
	position?: number;
	limit?: number;
	offset?: number;
}) => apiFetch<Player[]>('/players', opts as Record<string, number | undefined>);

export const getPlayer = (id: number) => apiFetch<Player>(`/players/${id}`);

export const getPlayerStats = (id: number) =>
	apiFetch<PlayerGameweekStats[]>(`/players/${id}/stats`);

export const getLeaderboard = (opts?: { last_n?: number; limit?: number; offset?: number }) =>
	apiFetch<LeaderboardEntry[]>('/leaderboard', opts as Record<string, number | undefined>);
