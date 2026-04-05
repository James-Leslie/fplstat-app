import { getLeaderboard, getTeams } from '$lib/api/endpoints';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url }) => {
	const lastN = Math.min(38, Math.max(1, Number(url.searchParams.get('last_n') ?? 5)));
	const [entries, teams] = await Promise.all([
		getLeaderboard({ last_n: lastN, limit: 50 }),
		getTeams()
	]);
	return { entries, teams, lastN };
};
