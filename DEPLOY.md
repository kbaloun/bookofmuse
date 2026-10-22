# Deploying bookofmuse.com

Status: **v1 source built (Oct 21, 2026). Not deployed.** Deployment is a separate,
Karel-approved step. Domain: bookofmuse.com, Porkbun order #12219767 (registered
Oct 21, 2026, expires Oct 22, 2027, WHOIS privacy ON, auto-renew enrolled at
Porkbun — billed to the on-file card until cancelled on Porkbun's Domain
Management page).

## Constraints (decide nothing against these)

- The submissions form must actually save submissions into a **private review
  queue**. Nothing is ever auto-published (standing vetting rule — see README).
- No third-party trackers, analytics beacons, or ad pixels at launch. Privacy
  posture is part of the brand.
- Cost should stay at or near zero until traffic justifies otherwise.
- Karel's registrar pattern: domains at Porkbun; previous sites (Safer Together,
  Sunnytize) used a GitHub repo checkpoint + GitHub Pages + registrar DNS.

## Hosting options (the static pages)

| Option | Cost | Notes |
|---|---|---|
| **GitHub Pages** (recommended for launch) | Free | Matches Karel's existing pattern; deploy-by-push doubles as a versioned checkpoint of the site. Custom domain + automatic HTTPS. Static only — form backend is separate (below). |
| Vercel | Free tier | Equally fine; nicer if the form backend becomes a Vercel serverless function (same repo, one platform). GitHub-push deploys. |
| Netlify | Free tier | Its built-in form handling is tempting (see below) but adds a vendor-specific form mechanism the source deliberately avoids. |
| Porkbun hosting | Paid add-on | No advantage; skip. |

**Recommendation: GitHub Pages for the pages + a separate tiny form backend**
(option B below), because it keeps the static site portable (the same files move
to Vercel/Netlify later with only a DNS change) and matches how Karel's other
sites are already run. If we later want pages + backend on one platform, moving
the whole repo to Vercel is an afternoon, not a rewrite.

## Form-backend options (the submissions queue)

The form POSTs JSON to `SUBMIT_ENDPOINT` (set in `submit.js`). Pick one:

**A. Form service (e.g. Formspree / Web3Forms) — fastest launch**
- Form POSTs to the service; submissions land in a dashboard + email notification.
- Pros: zero code, spam filtering included, live in an hour.
- Cons: a third party holds submitters' names/emails (disclose in the privacy
  note); free tiers cap volume (~50/month); another account to manage.
- Fits the rule fine: submissions go to a private inbox/queue, never public.

**B. Serverless function + private storage (recommended)**
- A small function (Vercel/Netlify/Cloudflare Worker) validates the JSON,
  stores it in private storage (e.g. a private repo issue queue, a database
  table, or simply emails it to the review inbox), and returns 200.
- Pros: our code, our data, no per-submission vendor; scales trivially at this
  volume; the validation step is where rate-limiting and spam checks live.
- Cons: an hour or two of setup; we own uptime (at this scale, negligible).

**C. Google Form + Sheets — zero-code fallback**
- Replace `submit.html`'s form with a linked Google Form feeding a private Sheet.
- Pros: nothing to maintain. Cons: worst look/feel, leaves the site's design,
  and Google branding on a credibility-sensitive page. Only if A/B both stall.

**Recommendation: B** for the real launch (data stays ours; the review queue is
exactly the vetting pipeline), with **A as the acceptable fast path** if Karel
wants submissions live the same day the site launches.

Either way: on receipt, submissions enter the existing guest-story workflow
(`hidden_files/guest-story-candidates.md` pattern) — permission + verification
before any use, security validation for scripts/automations.

## DNS steps (Porkbun → GitHub Pages)

1. In the GitHub repo: Settings → Pages → set custom domain `bookofmuse.com`
   (creates the `CNAME` file; the source folder already anticipates this).
2. At Porkbun → bookofmuse.com → DNS records:
   - Apex (`@`) A records → GitHub Pages: `185.199.108.153`, `185.199.109.153`,
     `185.199.110.153`, `185.199.111.153` (confirm current values in GitHub's
     Pages docs at deploy time).
   - `www` CNAME → `<github-username>.github.io`.
   - Remove any Porkbun parking/redirect records that conflict.
3. Wait for DNS propagation, then in GitHub Pages settings enable
   **Enforce HTTPS** once the certificate issues.
4. If the form backend lives elsewhere (option B on Vercel/Cloudflare), add a
   subdomain instead, e.g. `api.bookofmuse.com` CNAME → the function's host,
   and set `SUBMIT_ENDPOINT` to `https://api.bookofmuse.com/submit`.
   (If the function is on the same host, a relative `/api/submit` path works.)

## Launch checklist

- [ ] Karel approves host + form backend choices
- [ ] Repo created, source pushed (checkpoint commit)
- [ ] Pages enabled, custom domain set, DNS at Porkbun updated (steps above)
- [ ] `SUBMIT_ENDPOINT` set in `submit.js`; a test submission arrives in the
      review queue and is NOT visible anywhere public
- [ ] HTTPS enforced; both `bookofmuse.com` and `www.bookofmuse.com` resolve
- [ ] Disclaimer footer verified on every page; no Meta/Muse logos anywhere
- [ ] DiMona letter task (Oct 22) told the site is live before the letter sends
