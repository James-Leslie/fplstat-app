import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import { PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_PUBLISHABLE_KEY } from '$env/static/public';
import type { Database } from './types/database';

export type DB = SupabaseClient<Database>;

// Singleton typed client. The publishable key is safe to ship to the browser
// (it grants only the privileges the database's RLS policies allow), so we
// pull it from $env/static/public.
export const supabase: DB = createClient<Database>(
	PUBLIC_SUPABASE_URL,
	PUBLIC_SUPABASE_PUBLISHABLE_KEY,
	{
		auth: { persistSession: false }
	}
);
