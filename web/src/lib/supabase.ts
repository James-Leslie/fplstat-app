import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import { env } from '$env/dynamic/public';
import type { Database } from './types/database';

export type DB = SupabaseClient<Database>;

// Read at runtime rather than build time so CI (and any environment that
// doesn't pre-populate the vars) can still type-check and build the app.
// $env/dynamic/public is hydrated from process.env on the server and from a
// SvelteKit-injected snapshot in the browser. The publishable key is safe to
// expose to clients; service-role keys must never be set as PUBLIC_*.
const url = env.PUBLIC_SUPABASE_URL;
const key = env.PUBLIC_SUPABASE_PUBLISHABLE_KEY;

if (!url || !key) {
	throw new Error(
		'Missing PUBLIC_SUPABASE_URL or PUBLIC_SUPABASE_PUBLISHABLE_KEY. ' +
			'Copy web/.env.example to web/.env and fill in the publishable key.'
	);
}

export const supabase: DB = createClient<Database>(url, key, {
	auth: { persistSession: false }
});
