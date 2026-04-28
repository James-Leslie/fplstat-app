# web

SvelteKit frontend for fplstat. Coexists with the Streamlit app at `app/` during the migration (issues #11–#14).

## Prerequisites

Node 22 and pnpm 10 — both managed by `mise` from the repo-root `mise.toml`. From the repo root:

```bash
mise install
```

(One-time per machine; installs the Python, Node, and pnpm versions pinned in `mise.toml`. See the root `README.md` for how to install `mise` itself.)

## Setup

```bash
cd web
cp .env.example .env   # then fill in PUBLIC_SUPABASE_PUBLISHABLE_KEY
pnpm install
```

The Supabase URL and **publishable** key (not service-role) live in `web/.env` because SvelteKit's `$env/static/public` requires the `PUBLIC_` prefix. The publishable key is safe to ship to the browser; service-role keys must never be set here.

## Common commands

| Task                     | Command         |
| ------------------------ | --------------- |
| Dev server (with HMR)    | `pnpm dev`      |
| Production build         | `pnpm build`    |
| Preview production build | `pnpm preview`  |
| Type-check (svelte-check)| `pnpm check`    |
| Lint (Prettier + ESLint) | `pnpm lint`     |
| Auto-format              | `pnpm format`   |

The repo's `prek` hooks invoke `lint` and `check` automatically on commit when files under `web/` are staged.

## Regenerating Supabase types

`src/lib/types/database.ts` is generated from the live Supabase schema. After any migration to `public.*`, regenerate via the Supabase MCP (`generate_typescript_types`) or:

```bash
pnpm dlx supabase gen types typescript --project-id kxmthvesycgcgevlpqvi --schema public > src/lib/types/database.ts
```

## Layout

```
src/
├── lib/
│   ├── data.ts              # Stateless Supabase fetchers (port of app/data.py)
│   ├── style.ts             # FDR colour map (port of app/style.py)
│   ├── supabase.ts          # Typed Supabase client (singleton)
│   └── types/database.ts    # Generated DB types — do not edit by hand
└── routes/
    ├── +layout.svelte
    ├── +page.svelte         # Landing page
    └── fdr/
        ├── +page.server.ts  # Server-side load with 5-min cache header
        └── +page.svelte     # FDR matrix UI (port of app/pages/fdr_matrix.py)
```
