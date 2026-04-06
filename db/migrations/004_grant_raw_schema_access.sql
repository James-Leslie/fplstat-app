-- Grant service_role full access to raw schema for the ETL pipeline.
-- The raw schema is not accessible to anon/authenticated via the REST API
-- by default; these grants cover the service_role key used by the ETL.
-- NOTE: You must also add "raw" to the exposed schemas in the Supabase
-- dashboard (Settings → API → Exposed schemas) for client.schema("raw") to work.

GRANT USAGE ON SCHEMA raw TO service_role;
GRANT ALL ON ALL TABLES IN SCHEMA raw TO service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA raw GRANT ALL ON TABLES TO service_role;
