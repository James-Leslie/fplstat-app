import { getSupabase } from '$lib/supabase';
import { fetchFixtures, fetchGameweekInfo, fetchTeamIdMap } from '$lib/data';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ setHeaders }) => {
	// Mirrors Streamlit's @st.cache_data(ttl=300): the matrix only changes when
	// the daily ETL refreshes fixtures, so 5 minutes of CDN/browser caching is safe.
	setHeaders({
		'cache-control': 'public, max-age=300'
	});

	const supabase = getSupabase();
	const [fixtures, teamMap, gwInfo] = await Promise.all([
		fetchFixtures(supabase),
		fetchTeamIdMap(supabase),
		fetchGameweekInfo(supabase)
	]);

	return {
		fixtures,
		// Maps don't survive SvelteKit's serialization → ship as entries array.
		teamEntries: Array.from(teamMap.entries()),
		gwInfo
	};
};
