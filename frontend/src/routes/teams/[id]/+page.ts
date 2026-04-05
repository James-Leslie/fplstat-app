import { getTeams, getPlayers } from '$lib/api/endpoints';
import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const teamId = Number(params.id);
	if (isNaN(teamId)) throw error(404, 'Team not found');

	const [teams, players] = await Promise.all([
		getTeams(),
		getPlayers({ team_id: teamId, limit: 100 })
	]);

	const team = teams.find((t) => t.id === teamId);
	if (!team) throw error(404, 'Team not found');

	return { team, players };
};
