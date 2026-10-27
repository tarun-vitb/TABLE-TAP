# TableTap — Team contribution plan (lead has done the MVP)

Lead's part, already done: working Django MVP, GitHub lead repo
`tarun-vitb/TABLEE-TAP`, Vercel live link, end-to-end + stress test,
Fix Pack 1 (menu-item bug, GST formatting, cart remove, tracking note,
admin CSS) and Fix Pack 2 (shared Postgres — see POSTGRES_SETUP.md, plus a
light UI foundation in `static/css/style.css` and `templates/core/base.html`).

**Rules for everyone:** fork the lead repo, work on ONE branch, open ONE pull
request, lead merges and re-tests `runserver` after every merge. Never commit
`env/`, `venv/`, `db.sqlite3`, `staticfiles/`, a `SECRET_KEY`, or a
`DATABASE_URL`. Test locally with: venv → `pip install -r requirements.txt`
→ `python manage.py migrate` → `python seed_demo.py` → `python manage.py runserver`.
Demo login: `owner` / `owner123`. Evaluation date is NOT 28 Oct 2026 anymore
(lead to confirm the new date) — no rush, but freeze code once the lead sets
a freeze date.

## Teammate A — Postgres deploy + stability proof (backend)

Branch: `feature/postgres-deploy`
Files: `qrtap/settings.py`, `api/index.py`, `requirements.txt`, `POSTGRES_SETUP.md`
Work: push Fix Pack 2, create the Neon database (Option A in
POSTGRES_SETUP.md), redeploy on Vercel, run the 5-step verification there
(add Table 5 persists, login persists, table token stable, order survives a
cold start). Fix any deploy error and document it in POSTGRES_SETUP.md.
Done when: all 5 verification steps pass on the live link, and you can show
the same table token before and after a 10-minute gap.

## Teammate B — Customer UI (menu, cart, tracking)

Branch: `feature/customer-ui`
Files: `templates/core/public_menu.html`, `templates/core/cart.html`,
`templates/core/track.html`, `static/css/style.css`
Work, in this order:
1. Menu: sticky category chips, Veg-only toggle, search by item name,
   quantity +/− on each item (not just Add).
2. Cart: sticky bottom bar on mobile (items + total + View cart), quantity
   +/− and Remove per line (Remove already exists — keep it working).
3. Tracking: status timeline Placed → Accepted → Preparing → Ready → Served
   with a progress bar, auto-refresh every 30 seconds, bill link when billed.
   Kitchen note is already shown — keep it.
Done when: a customer can order entirely on a phone (test on a real phone,
not just a desktop browser resized), and the GST math still shows
₹150.00 + ₹7.50 = ₹157.50 for Veg Manchuria + Filter Coffee.

## Teammate C — Owner UI + Kitchen Display (owner side)

Branch: `feature/owner-ui`
Files: `templates/core/restaurant_dashboard.html`, `templates/core/kds.html`,
`templates/core/tables.html`, `templates/core/order_detail.html`
Work, in this order:
1. Dashboard: stat cards (Orders today, Paid sales today, Active orders),
   today's orders table with status pills and a status filter.
2. KDS: auto-refresh every 15 seconds (use the `extra_head` block in
   `base.html` for a meta refresh), elapsed minutes per order, colour by age
   (under 10 min normal, 10–20 min amber, over 20 min red).
3. Tables: a Print QR button (print-friendly page, one QR per table) and a
   Copy menu link button.
Done when: the kitchen flow (place order → KDS → Ready → bill) can be demoed
from two devices at once (phone as customer, laptop as kitchen) without
refreshing by hand.

## Teammate D — New features + documentation + PPT

Branch: `feature/billing-docs`
Files: `templates/core/order_detail.html`, `core/views.py` (search/filter only),
`docs/` (new folder), PPT (new file, not in the code repo's root)
Work, in this order:
1. Printable bill: a Print button on the bill page that prints a clean
   receipt (restaurant name, items, subtotal, GST 5%, total, payment mode).
2. Owner order search/filter: filter today's orders by status and by
   payment mode (Cash / UPI).
3. Documentation in the same format as the earlier DTI documentation
   (spiral-bound hard copy, one per team). **Leave the mentor field blank**
   until after the evaluation — do not invent a mentor name.
4. PPT (compulsory): title, problem, objectives, existing vs proposed,
   tech stack, architecture, data model, customer demo, kitchen/billing demo,
   revenue model, testing, conclusion / future scope.
5. LinkedIn: every member posts the project on their own profile, linking
   their own fork and naming their own module.
Done when: the bill prints cleanly, the filters work, the doc + PPT are
reviewed by the lead, and every member's LinkedIn post is live.

## If you get stuck

- "Add table/menu didn't work" on the live link: check first whether the
  Postgres fix (Teammate A) is deployed — before that fix, live data
  switches instances and looks broken even when the code is fine.
  Locally, the same actions already work.
- "It works locally but not on Vercel": check Vercel env vars and redeploy
  after any env change; env changes alone do not redeploy.
- Ask the lead before changing the demo restaurant name, the demo owner
  password, prices in the seed data, or the pricing tiers — those are
  shared demo facts.
