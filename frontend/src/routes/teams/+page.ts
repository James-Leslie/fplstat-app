import { getTeams } from '$lib/api/endpoints';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
	const teams = await getTeams();
	return { teams };
};
