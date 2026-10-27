# TableTap — Fix Blocker 1: one shared Postgres database

## The problem, in one paragraph

Vercel runs the app as serverless functions. Each function instance has its
own `/tmp` folder, so SQLite in `/tmp` is a *different* database per instance.
Requests are routed randomly, so: you add a table on instance A, the next page
load hits instance B (fresh seed, no new table, no login session) and it looks
like "add table didn't work" and "everything asks for owner login again".
QR images break the same way (the image request hits an instance where you
are not logged in, so it gets a login page instead of a PNG).

## The fix

One database *outside* Vercel that every instance shares: hosted Postgres.
With it, the first cold start migrates + seeds the demo once (see
`api/index.py`: it seeds only when no restaurant exists), and after that
orders, table tokens, and login sessions persist across cold starts and
instances. The code already supports this: `qrtap/settings.py` reads
`DATABASE_URL`, falling back to `POSTGRES_URL` (the name Vercel's Neon
integration creates). Local runs without either variable still use local
SQLite, so nothing changes for local development.

**Never commit a database URL to GitHub.** It goes in Vercel Environment
Variables only, for Production (and Preview if you want previews to share it).

## Option A — recommended: Vercel Storage + Neon (no manual copy-paste)

1. Vercel Dashboard → project `table-tap` → **Storage** tab → **Create Database**
   → choose **Neon Postgres** → Create and link it to the project.
2. Vercel will add `POSTGRES_URL`, `POSTGRES_URL_NON_POOLING`, etc. to the
   project's Environment Variables automatically.
3. Make sure the existing variables are still there: `VERCEL=1`,
   `DJANGO_SECRET_KEY` (your generated key), `DJANGO_DEBUG=0`.
4. **Deployments → Redeploy** the latest production deployment (env changes
   need a redeploy to take effect).

## Option B — manual: neon.tech

1. Sign up at neon.tech → New Project → copy the connection string
   (it looks like `postgres://user:password@host/db?sslmode=require`).
2. Vercel Dashboard → project `table-tap` → Settings → Environment Variables
   → Add `DATABASE_URL` = that connection string, Environment: Production.
3. Redeploy as in Option A step 4.

## Verify the fix (do all of these, in order)

1. Open the live site, log in as `owner`, add **Table 5** on the Tables page.
2. Reload the Tables page 3 times, then log out and log back in — Table 5
   must still be there, and you must stay logged in.
3. Copy Table 1's menu link, open it in a private/incognito window — it must
   show "Table 1", not "No table selected".
4. Place a test order, wait 10 minutes (forces a cold start), reload the
   dashboard — the order must still be there.
5. If any step fails, the database URL is not reaching the deployment:
   check Vercel → Settings → Environment Variables, then redeploy again.

## After this fix, what stays true

- The live link is now safe for a multi-step demo, not just viewing.
- The local `runserver` demo is still the safest evaluation fallback
  (no network, no cold start). Keep both ready.
- If you ever reset the Neon database, the demo re-seeds itself on the
  next cold start (owner / owner123, Sri Sai Cafe, 9 items, Tables 1–4).
