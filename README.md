# bookofmuse.com — v1 site source

The public site for **Use Muse** by Karel Baloun & Hikaru (goal
goal_035ec8e4aaf7). Plain static HTML/CSS/JS — no build step, no frameworks,
no external fonts, no trackers, no CDNs. Open `index.html` in a browser to
preview; deploy to any static host (see DEPLOY.md).

## Pages

| File | What it is |
|---|---|
| `index.html` | Home: book hero with cover, tagline, savings proof, the ten sections, spec, author creds, “read it with your Muse” |
| `community.html` | The community: achievements / ideas / templates, the showcase, and the vetting rule |
| `submit.html` + `submit.js` | The submissions form (form backend endpoint configured at deploy — see DEPLOY.md) |
| `templates.html` | Templates & Automations library: the vetted Appendix A starter set as copy-and-hand-to-your-Muse recipes |
| `styles.css` | All styling. Chart palette locked: blue #2F7FD0 (author), amber #F2A93B (Muse) |
| `assets/cover.jpg` | Current approved cover (“Muse It!” — deer full-bleed, Oct 17, 2026) |

## Standing rules baked into this site

- **Vetting / security rule (Karel, Oct 21, 2026):** no new scripts are
  accepted onto the site without validation, and only good vetted ideas go up.
  Submissions are receive-only and never auto-published; ideas are vetted for
  quality; scripts/templates/automations are security-validated (what they do,
  what they access, what they send, what credentials they touch) before posting.
- **Disclaimer on every page:** unofficial book, not affiliated with or
  endorsed by Meta; Muse is Meta's product/trademark. No Meta/Muse logos.
- **Exact numbers only:** the savings figure ($6,517.83, 19 logged
  transactions, Sep 8 – Oct 18, 2026) was re-read from
  `~/memory/money-saved-log.md` at build time (Oct 21, 2026). Re-read the log
  before updating it — never quote it from memory.
- Book naming rule applies to all site copy: Karel's Muse is “my Muse” or
  “Hikaru”; other people's are “your Muse” / “the Muse”; never “the assistant.”
