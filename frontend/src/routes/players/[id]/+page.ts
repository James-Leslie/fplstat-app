import { getPlayer, getPlayerStats, getTeams } from '$lib/api/endpoints';
import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const id = Number(params.id);
	if (isNaN(id)) throw error(404, 'Player not found');

	const [player, stats, teams] = await Promise.all([
		getPlayer(id),
		getPlayerStats(id),
		getTeams()
	]);
	return { player, stats, teams };
};
