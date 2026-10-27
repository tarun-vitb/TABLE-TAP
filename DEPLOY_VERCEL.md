# Deploy TableTap on Vercel — step by step

## 1. Push the Vercel files to GitHub
Copy these new/changed files into your cloned TABLEE-TAP repo and push:
- vercel.json (new)
- api/index.py (new)
- qrtap/settings.py (changed: WhiteNoise, STATIC_ROOT, /tmp DB on Vercel, CSRF trusted origins)
- requirements.txt (changed: added whitenoise)
- .gitignore (changed: added staticfiles/, venv/)
- README.md (changed: added Vercel section)
Then: git add .  /  git commit -m "Add Vercel deployment"  /  git push

## 2. Import in Vercel
- Go to vercel.com → New Project → Import Git Repository → tarun-vitb/TABLEE-TAP
- Framework Preset: Other
- Root Directory: ./
- Build Command: python manage.py collectstatic --noinput
- Install Command: pip install -r requirements.txt
- Output Directory: leave blank
- Environment Variables:
  - VERCEL = 1
  - DJANGO_SECRET_KEY = (generate one: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
  - DJANGO_DEBUG = 0
- Deploy, wait for READY, open the URL Vercel gives you.

## 3. Check the live demo
- Home page should show Sri Sai Cafe.
- Login with owner / owner123, open Tables & QR, place an order, move it in KDS.
- If you see a Vercel login screen instead of the site, go to Project Settings → Deployment Protection and turn it off.

## 4. Know the limit (say this honestly in viva if asked)
Vercel serverless functions do not share a filesystem, so SQLite lives in
/tmp per instance and the demo data is re-seeded on each cold start.
The live link is for teammates to VIEW the app. It is not a production
database. The evaluation demo should still be run locally with runserver,
where orders persist in db.sqlite3. For real use, use a hosted Postgres
database and set DATABASE_URL (that change is not in this MVP).
