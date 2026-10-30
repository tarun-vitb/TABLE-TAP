# TableTap customer UI — design notes

## Premium SaaS pass (29 Oct 2026, localhost demo)
This pass builds on the customer-UI pattern below; it does not replace
it. The customer menu, stepper, toast and bottom bar are unchanged in
behaviour — they now sit in a new shell.

- Palette changed (the old teal is gone): warm paper background
  #FAF8F5, stone ink #1C1917, burnt-orange accent #EA580C (hover
  #C2410C, soft #FFF1E8), hairline border #E7E2DC. One accent, no
  gradients, no glassmorphism.
- Fonts: Plus Jakarta Sans for headings, Inter for body, loaded from
  Google Fonts with system fallbacks if the font service is unreachable.
- Logo: `static/img/logo.svg` — a rounded orange square with three
  QR corner squares, data dots and a centre plate dot. Used in the
  header, footer and as the favicon. It is TableTap's own mark, not
  copied from any reference.
- Icons: small inline SVGs (QR, kitchen, bill, clock, card, phone) —
  no emoji as icons, no icon font to load.
- Animation: page entrance fade + rise, a 160 ms fade on internal
  link clicks (`static/js/site.js`), scroll-reveal on landing sections,
  cart-bar slide-up and stepper pop. All progressive enhancement:
  with JavaScript off, pages load normally and every action still
  works as a plain form POST/GET. `prefers-reduced-motion` disables it.
- Negative space: landing sections have 64–72 px vertical padding,
  content capped at 1080 px, customer pages at 720 px.
- Product home page (`/`): hero, 4-step how-it-works, 6-feature grid,
  pricing (Starter ₹499 / Growth ₹999 / Scale ₹1,999 — illustrative,
  not enforced in code), FAQ, final call to action. Top nav carries
  Log in and Sign up for owners; customers never need an account.
- Owner signup (`/signup/`): creates an account and lands on the
  owner home (`/dashboard/`), which is now a proper home page:
  greeting, per-restaurant cards with item/table/order counts and
  links to Dashboard, Menu & photos, Tables & QR, Kitchen display
  and Customer menu. Log in (`/login/`) redirects there too.
- Item photos: `MenuItem.image` (migration
  `0002_menuitem_image.py`, upload to `menu_items/`, served from
  `/media/` in DEBUG). The owner adds a photo in the menu page
  (the form is now multipart). The customer menu shows the photo
  next to the dish name, above the Add/stepper, and the cart shows a
  small thumb. Items without a photo show a clean placeholder tile
  with the dish initial — never a broken image.
- Demo photos: `demo_images/` holds 9 generic web photos that the
  seed script attaches to the demo menu. They are labelled in the
  seed script and on the landing page as demo photos, NOT Sri Sai
  Cafe's own food photos. A real restaurant replaces them by
  uploading its own photos from the menu page.

## Chosen pattern (customer UI, 28–29 Oct)

## Chosen pattern
Reference 1 is the primary pattern: a menu list with an inline − qty +
stepper on each item and a bottom cart bar. Reference 4's bottom bar
(items in cart + total + action) is merged into that same bar. The two
references are patterns only — no brand, logo, colour, or image from
either is copied into TableTap.

## UX rules applied
- Feedback on every action: Add turns into a stepper in place, a toast
  says what was added, and the bottom cart bar appears with the new
  count and total. No silent reloads.
- Thumb reach: the cart action lives in a fixed bottom bar, not at the
  top of the page. The top of the menu is for choosing food.
- No dead ends: search and Veg-only filters are preserved across
  Add/Remove, and Add returns to the same item via an anchor.
- State is always visible: quantity is on the item row itself, and on
  the cart page as a stepper, not hidden behind a separate screen.
- Honest visuals (superseded by the premium pass above): the original
  build was text-first because there was no image field in the model,
  so no stock food photos were used to fake one. The premium pass
  added a real image field; demo photos are labelled as demo.
- One theme: one accent, hairline borders, no gradients, no
  glassmorphism, no emoji as icons. Owner pages and KDS share the
  same tokens (accent and type changed in the premium pass).
- Accessibility: 44px minimum tap targets, visible focus outlines,
  veg/non-veg shown as a square dot plus the word Veg/Non-veg (not
  colour alone), and a `prefers-reduced-motion` rule.

## Tech stack (unchanged)
Django server-rendered templates + one custom CSS file
(`static/css/style.css`) + one small progressive-enhancement JS file
(`static/js/customer.js`). No React, no Tailwind, no new build step, no
database change. Every customer action still works as a plain form
POST/GET if JavaScript is off; the JS only adds chip highlighting on
scroll, Veg-toggle auto-submit, and toast auto-dismiss.

## Files changed in this pass
`core/views.py` (menu search/Veg filter, cart totals, Add returns to
the same item, cart stepper), `templates/core/base.html` (minimal
header; owner login moved to the footer so customers do not see it
first), `templates/core/public_menu.html`, `templates/core/cart.html`,
`templates/core/track.html`, `static/css/style.css`,
`static/js/customer.js` (new).

## Test bar (must still pass)
Full order on a real phone, stepper up and down on menu and cart,
bottom bar appearing and disappearing, search and Veg-only surviving an
Add, and GST math ₹150.00 + ₹7.50 = ₹157.50 for Veg Manchuria +
Filter Coffee. Owner dashboard, KDS, and billing are untouched in
behaviour and must still load.
