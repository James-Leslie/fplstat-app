import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import { env } from '$env/dynamic/public';
import type { Database } from './types/database';

export type DB = SupabaseClient<Database>;

let _client: DB | undefined;

// Lazy singleton. Constructing eagerly at module load fails SvelteKit's
// post-build analyse step (which imports server modules to introspect
// exports) on environments without env vars, even when the route never runs.
// We only touch env when a request actually needs the client.
export function getSupabase(): DB {
	if (_client) return _client;

	const url = env.PUBLIC_SUPABASE_URL;
	const key = env.PUBLIC_SUPABASE_PUBLISHABLE_KEY;

	if (!url || !key) {
		throw new Error(
			'Missing PUBLIC_SUPABASE_URL or PUBLIC_SUPABASE_PUBLISHABLE_KEY. ' +
				'Copy web/.env.example to web/.env and fill in the publishable key. ' +
				'The publishable key is safe to expose; service-role keys must never be set as PUBLIC_*.'
		);
	}

	_client = createClient<Database>(url, key, {
		auth: { persistSession: false }
	});
	return _client;
}
