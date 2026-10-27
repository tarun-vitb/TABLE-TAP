# TableTap — QR Restaurant Ordering SaaS (MVP for evaluation, 2026-10-28)

Customers scan a QR on their table, order from their phone, the kitchen
sees it live, and the bill is ready at the table. No app install, no
hardware to buy. The restaurant owner pays a monthly subscription;
customers do not pay the platform.

## Run it (5 minutes)
```bash
python -m venv env
# Windows: env\Scripts\activate  |  Mac/Linux: source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python seed_demo.py
python manage.py runserver
# open http://127.0.0.1:8000/
```
Demo owner login: `owner` / `owner123`
Demo restaurant: Sri Sai Cafe — http://127.0.0.1:8000/r/sri-sai-cafe/
Demo tables: open Dashboard → Tables & QR, print a QR, scan it with a phone.

Change the demo password and the SECRET_KEY in `qrtap/settings.py`
before any real use. The seed password is for evaluation demo only.

## 5-minute demo script (rehearse exactly this)
1. Owner login → Dashboard → Tables & QR → open Table 1 QR as a customer.
2. Customer menu: add Veg Manchuria + Filter Coffee, note "less spicy", place order.
3. Kitchen display (Dashboard → Kitchen display): order appears live → Accept → Preparing → Ready.
4. Customer tracking page: refresh, status is Ready.
5. Owner bill page: subtotal ₹150, GST 5% ₹7.50, total ₹157.50 → mark Paid by UPI.
   Note: UPI in this MVP is the restaurant's own UPI ID. This system never
   holds customer money.

## What is in this MVP
- Restaurant signup/profile, menu builder (categories, items, veg flag,
  availability toggle), tables with a unique QR code per table
- Public mobile menu, session cart, place order, order tracking
- Kitchen Display System with status transitions and waiter/owner views
- Billing: subtotal + 5% GST + total, Cash/UPI, paid status, daily sales
  on the owner dashboard
- Django admin at /admin/

## What is deliberately NOT in this MVP (say this in viva, don't hide it)
Delivery/riders, aggregator integrations, inventory, loyalty/coupons,
table reservations, multi-branch analytics, and payment-gateway money
handling. Those are Phase 2. The subscription pricing in the business
plan (₹499 / ₹999 / ₹1,999 per month) is the proposed model — this MVP
does not yet enforce paid subscriptions or trial expiry.

## Stack
Python, Django, SQLite, Bootstrap, qrcode + Pillow for QR images.
Database tables: Restaurant, Table, Category, MenuItem, Order, OrderItem.

## Deploy on Vercel (for teammates to view)
Vercel files are included: `vercel.json` + `api/index.py`. Push them to
GitHub first, then in Vercel: New Project → Import `tarun-vitb/TABLEE-TAP`
→ Framework Preset: Other → Root Directory: ./ → Build Command:
`python manage.py collectstatic --noinput` → Install Command:
`pip install -r requirements.txt` → Environment Variables: `VERCEL=1`,
`DJANGO_SECRET_KEY=<a fresh random key>`, `DJANGO_DEBUG=0` → Deploy.
IMPORTANT LIMIT: Vercel's filesystem is read-only, so this deployment
uses SQLite in /tmp and re-seeds the demo restaurant on each cold start.
Orders on the live link do NOT persist across cold starts. Use the live
link for viewing/demoing, and the local `runserver` demo for the actual
evaluation. For real multi-user use, switch SQLite to a hosted Postgres
database. If teammates see a Vercel login screen, turn off Deployment
Protection in the Vercel project settings.

## Tonight: 5-member GitHub split (safe, low-risk commits)
Lead: create a new GitHub repo, push this code as the first commit.
Then each member forks the lead repo, makes ONE small change on a branch,
opens a PR, and the lead merges and re-tests `runserver` after every merge.
1. Member 1 — rebrand: project name, home-page text, and demo restaurant
   name/menu for a real local cafe (templates/core/home.html, seed_demo.py)
2. Member 2 — customer menu polish: veg-only filter and better mobile
   layout (templates/core/public_menu.html)
3. Member 3 — KDS polish: auto-refresh every 15 seconds and elapsed-time
   colour (templates/core/kds.html)
4. Member 4 — billing polish: printable bill view and payment-mode filter
   on the dashboard (templates/core/order_detail.html)
5. Member 5 — docs + PPT + demo video + final end-to-end test
Freeze code once the demo works. Do not start a new feature after that.

## Evaluation checklist (same requirements as before)
- [ ] Runs on the evaluation laptop, demo order placed live
- [ ] Every member's fork shows their own commit; every member posts on LinkedIn
- [ ] 1 spiral-bound documentation copy, DTI format, mentor field LEFT BLANK
- [ ] 12-slide PPT ready on pen drive + backup copy
- [ ] 2-minute screen recording of the demo as backup
