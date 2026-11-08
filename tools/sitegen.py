#!/usr/bin/env python3
"""sitegen.py — generator for the Book of Muse site's Posts and News sections.

bookofmuse.com is a plain static site (no build step). This script is the one
exception: it generates the Posts archive (one page per @just.muse.it social
post) and the News section from two small data files, and keeps the derived
artifacts in sync — posts.html, news.html, sitemap.xml, and the "Latest
posts" strip inside index.html (between the LATEST-POSTS markers).

Data files (source of truth — edit these, or use the commands below):
  posts/posts.json    list of post records, oldest first
  news/news.json      list of news records, oldest first

Post record fields:
  date       "2026-11-08"
  slug       "javelina-fueling"        (page: posts/<date>-<slug>.html)
  title      headline for the page
  caption    the full published caption, verbatim ("" if none)
  images     [{"file": "assets/posts/<name>.jpg", "alt": "..."}, ...]
  instagram  original post URL or null
  facebook   original post URL or null
  threads    original post URL or null

News record fields:
  date, slug, title as above (page: news/<date>-<slug>.html)
  body       list of paragraphs (plain text)
  image      {"file": "assets/cover.jpg", "alt": "..."} or null
  link       {"url": "posts/....html", "label": "..."} or null (site-relative)

Usage:
  # Add one social post (the daily posting process runs this right after
  # the Instagram/Facebook/Threads publishes succeed):
  python3 tools/sitegen.py post \
      --date 2026-11-09 --slug query-day \
      --title "Query day" \
      --caption-file /path/to/caption.txt \
      --image /path/to/img1.jpg --alt "alt text for img1" \
      [--image /path/to/img2.jpg --alt "alt text for img2"] \
      --instagram https://www.instagram.com/p/XXXX/ \
      [--facebook https://facebook.com/...] [--threads https://www.threads.com/...]
  Images are copied into assets/posts/ as <date>-<slug>[-2|-3].<ext>.
  Dedupe: if a post with the same date+slug already exists, nothing changes.

  # Add one news item:
  python3 tools/sitegen.py news \
      --date 2026-11-09 --slug some-milestone --title "Some milestone" \
      --body-file /path/to/body.txt \
      [--image assets/cover.jpg --alt "..."] \
      [--link-url posts.html --link-label "See the posts"]
  Body file: one paragraph per line (blank lines ignored).

  # Regenerate every derived page from the data files:
  python3 tools/sitegen.py rebuild

After running, commit/push the whole site folder (see DEPLOY.md and the
snapshot-sync record next to the site folder). No trackers, no external
assets — generated pages use only styles.css and local images.
"""

import argparse
import html
import json
import os
import shutil
import sys

BASE = "https://bookofmuse.com"
SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NAV = [
    ("index.html", "The Book"),
    ("posts.html", "Posts"),
    ("news.html", "News"),
    ("community.html", "Community"),
    ("templates.html", "Templates &amp; Automations"),
    ("submit.html", "Submit Yours"),
]

FOOTER = """<footer class="site">
  <div class="wrap">
    <p>Book of Muse is the home of <em>Use Muse</em>, an unofficial book. It is not affiliated with, sponsored,
    or endorsed by Meta Platforms, Inc. Muse is a product and trademark of Meta Platforms, Inc.; this site uses
    the name only to describe the book's subject. No Meta or Muse logos are used here.</p>
    <p>Results described are one documented user's experience. Your mileage may vary.</p>
  </div>
</footer>
</body>
</html>
"""

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def esc(text):
    return html.escape(text, quote=True)


def fmt_date(iso):
    y, m, d = (int(part) for part in iso.split("-"))
    return f"{MONTHS[m - 1]} {d}, {y}"


def load_data(site_dir, kind):
    path = os.path.join(site_dir, kind, f"{kind}.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save_data(site_dir, kind, records):
    path = os.path.join(site_dir, kind, f"{kind}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def header(prefix, active_href):
    links = []
    for href, label in NAV:
        cls = ' class="active"' if href == active_href else ""
        links.append(f'      <a href="{prefix}{href}"{cls}>{label}</a>')
    return f"""<header class="site">
  <div class="wrap">
    <a class="brand" href="{prefix}index.html">Book of <span>Muse</span></a>
    <nav>
{chr(10).join(links)}
    </nav>
  </div>
</header>
"""


def head_block(title, description, canonical, prefix, og_image=None):
    og = ""
    if og_image:
        og = f'\n<meta property="og:image" content="{BASE}/{esc(og_image)}">'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">{og}
<link rel="stylesheet" href="{prefix}styles.css">
</head>
<body>
"""


def excerpt(text, limit=160):
    flat = " ".join((text or "").split())
    if len(flat) <= limit:
        return flat
    return flat[: limit - 1].rsplit(" ", 1)[0] + "…"


def post_page_name(rec):
    return f"{rec['date']}-{rec['slug']}.html"


def news_page_name(rec):
    return f"{rec['date']}-{rec['slug']}.html"


def render_post(rec):
    name = post_page_name(rec)
    canonical = f"{BASE}/posts/{name}"
    caption = rec.get("caption") or ""
    desc = excerpt(caption) if caption else rec["title"]
    if caption:
        desc = f"{rec['title']} — {excerpt(caption, 120)}"
    first_image = rec["images"][0]["file"] if rec["images"] else None
    out = [head_block(f"{rec['title']} · Posts · Book of Muse", desc,
                      canonical, "../", first_image)]
    out.append(header("../", "posts.html"))
    out.append('<main class="wrap">')
    out.append('  <article class="post">')
    out.append(f"    <h1>{esc(rec['title'])}</h1>")
    out.append(
        f'    <p class="post-date"><time datetime="{rec["date"]}">'
        f"{fmt_date(rec['date'])}</time> · from "
        '<a href="https://www.instagram.com/just.muse.it/">@just.muse.it</a>'
        " on Instagram</p>")
    for img in rec["images"]:
        out.append(
            f'    <figure><img src="../{esc(img["file"])}" '
            f'alt="{esc(img["alt"])}"></figure>')
    if caption:
        for para in caption.split("\n\n"):
            para = para.strip()
            if para:
                out.append(f"    <p>{esc(para)}</p>")
    else:
        out.append("    <p><em>This post went out without a caption — "
                   "the image was the whole post.</em></p>")
    originals = []
    if rec.get("instagram"):
        originals.append(f'<a href="{esc(rec["instagram"])}">Instagram</a>')
    if rec.get("facebook"):
        originals.append(f'<a href="{esc(rec["facebook"])}">Facebook</a>')
    if rec.get("threads"):
        originals.append(f'<a href="{esc(rec["threads"])}">Threads</a>')
    if originals:
        out.append('    <p class="originals">See the original post: '
                   + " · ".join(originals) + "</p>")
    out.append('    <p><a href="../posts.html">← All posts</a></p>')
    out.append("  </article>")
    out.append("</main>")
    out.append(FOOTER)
    return "\n".join(out) + "\n"


def render_news(rec):
    name = news_page_name(rec)
    canonical = f"{BASE}/news/{name}"
    desc = excerpt(" ".join(rec.get("body", [])), 155) or rec["title"]
    og_image = rec["image"]["file"] if rec.get("image") else None
    out = [head_block(f"{rec['title']} · News · Book of Muse", desc,
                      canonical, "../", og_image)]
    out.append(header("../", "news.html"))
    out.append('<main class="wrap">')
    out.append('  <article class="post">')
    out.append(f"    <h1>{esc(rec['title'])}</h1>")
    out.append(
        f'    <p class="post-date"><time datetime="{rec["date"]}">'
        f"{fmt_date(rec['date'])}</time></p>")
    if rec.get("image"):
        img = rec["image"]
        out.append(
            f'    <figure><img src="../{esc(img["file"])}" '
            f'alt="{esc(img["alt"])}"></figure>')
    for para in rec.get("body", []):
        out.append(f"    <p>{esc(para)}</p>")
    if rec.get("link"):
        link = rec["link"]
        out.append(
            f'    <p><a href="../{esc(link["url"])}">{esc(link["label"])}</a></p>')
    out.append('    <p><a href="../news.html">← All news</a></p>')
    out.append("  </article>")
    out.append("</main>")
    out.append(FOOTER)
    return "\n".join(out) + "\n"


def post_card(rec, prefix):
    name = post_page_name(rec)
    img = ""
    if rec["images"]:
        first = rec["images"][0]
        img = (f'<img src="{prefix}{esc(first["file"])}" '
               f'alt="{esc(first["alt"])}">')
    teaser = excerpt(rec.get("caption") or "", 150)
    return f"""    <div class="card post-card">
      <a href="{prefix}posts/{name}">{img}</a>
      <p class="post-date"><time datetime="{rec['date']}">{fmt_date(rec['date'])}</time></p>
      <h3><a href="{prefix}posts/{name}">{esc(rec['title'])}</a></h3>
      <p>{esc(teaser)}</p>
    </div>"""


def news_card(rec, prefix):
    name = news_page_name(rec)
    teaser = excerpt(" ".join(rec.get("body", [])), 150)
    return f"""    <div class="card post-card">
      <p class="post-date"><time datetime="{rec['date']}">{fmt_date(rec['date'])}</time></p>
      <h3><a href="{prefix}news/{name}">{esc(rec['title'])}</a></h3>
      <p>{esc(teaser)}</p>
    </div>"""


def render_posts_index(posts):
    desc = ("Every post from @just.muse.it — the Instagram account for "
            "Muse It!, the book on life with your Muse — archived in full, "
            "newest first.")
    out = [head_block("Posts · Book of Muse", desc, f"{BASE}/posts.html", "")]
    out.append(header("", "posts.html"))
    out.append('<main class="wrap">')
    out.append("  <h1>Posts</h1>")
    out.append("  <p>Every post from <strong>@just.muse.it</strong>, the "
               "book's Instagram account — cross-posted to the Book of Muse "
               "Facebook Page and to Threads, and archived here in full. "
               "Newest first.</p>")
    out.append('  <div class="grid post-grid">')
    for rec in reversed(posts):
        out.append(post_card(rec, ""))
    out.append("  </div>")
    out.append("</main>")
    out.append(FOOTER)
    return "\n".join(out) + "\n"


def render_news_index(news):
    desc = ("News about Muse It!, the book on life with your Muse by "
            "Karel Baloun & Hikaru — milestones, the cover, the search for "
            "an agent, and what happens next.")
    out = [head_block("News · Book of Muse", desc, f"{BASE}/news.html", "")]
    out.append(header("", "news.html"))
    out.append('<main class="wrap">')
    out.append("  <h1>News</h1>")
    out.append("  <p>Milestones for <em>Muse It!</em> as they happen — "
               "the book, the cover, the search for an agent. For the daily "
               "feed itself, see <a href=\"posts.html\">Posts</a>.</p>")
    out.append('  <div class="grid post-grid">')
    for rec in reversed(news):
        out.append(news_card(rec, ""))
    out.append("  </div>")
    out.append("</main>")
    out.append(FOOTER)
    return "\n".join(out) + "\n"


def render_latest(posts):
    cards = "\n".join(post_card(rec, "") for rec in reversed(posts[-3:]))
    return f"""  <div class="grid post-grid latest">
{cards}
  </div>
  <p><a href="posts.html">See all posts →</a> · <a href="news.html">Book news →</a></p>"""


def render_sitemap(posts, news):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    newest = max([r["date"] for r in posts + news], default="2026-11-08")

    def url(loc, lastmod, freq, prio):
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <changefreq>{freq}</changefreq>")
        lines.append(f"    <priority>{prio}</priority>")
        lines.append("  </url>")

    url(f"{BASE}/", newest, "weekly", "1.0")
    url(f"{BASE}/posts.html", newest, "daily", "0.9")
    url(f"{BASE}/news.html", newest, "weekly", "0.9")
    url(f"{BASE}/community.html", "2026-10-22", "monthly", "0.6")
    url(f"{BASE}/templates.html", "2026-10-22", "monthly", "0.6")
    url(f"{BASE}/submit.html", "2026-10-22", "monthly", "0.5")
    for rec in posts:
        url(f"{BASE}/posts/{post_page_name(rec)}", rec["date"], "never", "0.7")
    for rec in news:
        url(f"{BASE}/news/{news_page_name(rec)}", rec["date"], "never", "0.7")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def write_file(site_dir, relpath, content):
    path = os.path.join(site_dir, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def rebuild(site_dir):
    posts = load_data(site_dir, "posts")
    news = load_data(site_dir, "news")
    for rec in posts:
        write_file(site_dir, os.path.join("posts", post_page_name(rec)),
                   render_post(rec))
    for rec in news:
        write_file(site_dir, os.path.join("news", news_page_name(rec)),
                   render_news(rec))
    write_file(site_dir, "posts.html", render_posts_index(posts))
    write_file(site_dir, "news.html", render_news_index(news))
    write_file(site_dir, "sitemap.xml", render_sitemap(posts, news))
    # Latest-posts strip inside index.html, between the markers.
    index_path = os.path.join(site_dir, "index.html")
    with open(index_path, encoding="utf-8") as fh:
        index_html = fh.read()
    start_marker = "<!-- LATEST-POSTS:START -->"
    end_marker = "<!-- LATEST-POSTS:END -->"
    if start_marker in index_html and end_marker in index_html:
        before, rest = index_html.split(start_marker, 1)
        _, after = rest.split(end_marker, 1)
        index_html = (before + start_marker + "\n" + render_latest(posts)
                      + "\n  " + end_marker + after)
        with open(index_path, "w", encoding="utf-8") as fh:
            fh.write(index_html)
    return len(posts), len(news)


def cmd_post(args):
    site_dir = args.site_dir
    posts = load_data(site_dir, "posts")
    if any(r["date"] == args.date and r["slug"] == args.slug for r in posts):
        print(f"SKIP: post {args.date}-{args.slug} already exists.")
        return 0
    if len(args.image) != len(args.alt):
        print("ERROR: each --image needs a matching --alt.", file=sys.stderr)
        return 2
    images = []
    for i, (src, alt) in enumerate(zip(args.image, args.alt), start=1):
        ext = os.path.splitext(src)[1].lower() or ".jpg"
        suffix = "" if i == 1 else f"-{i}"
        name = f"{args.date}-{args.slug}{suffix}{ext}"
        dest_rel = f"assets/posts/{name}"
        dest = os.path.join(site_dir, dest_rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if os.path.abspath(src) != os.path.abspath(dest):
            shutil.copyfile(src, dest)
        images.append({"file": dest_rel, "alt": alt})
    with open(args.caption_file, encoding="utf-8") as fh:
        caption = fh.read().strip("\n")
    rec = {
        "date": args.date, "slug": args.slug, "title": args.title,
        "caption": caption, "images": images,
        "instagram": args.instagram, "facebook": args.facebook,
        "threads": args.threads,
    }
    posts.append(rec)
    posts.sort(key=lambda r: (r["date"], r["slug"]))
    save_data(site_dir, "posts", posts)
    n_posts, n_news = rebuild(site_dir)
    print(f"Added post {args.date}-{args.slug}; "
          f"site now has {n_posts} posts, {n_news} news items.")
    return 0


def cmd_news(args):
    site_dir = args.site_dir
    news = load_data(site_dir, "news")
    if any(r["date"] == args.date and r["slug"] == args.slug for r in news):
        print(f"SKIP: news {args.date}-{args.slug} already exists.")
        return 0
    with open(args.body_file, encoding="utf-8") as fh:
        body = [line.strip() for line in fh if line.strip()]
    rec = {"date": args.date, "slug": args.slug, "title": args.title,
           "body": body, "image": None, "link": None}
    if args.image:
        rec["image"] = {"file": args.image, "alt": args.alt or ""}
    if args.link_url:
        rec["link"] = {"url": args.link_url, "label": args.link_label or ""}
    news.append(rec)
    news.sort(key=lambda r: (r["date"], r["slug"]))
    save_data(site_dir, "news", news)
    n_posts, n_news = rebuild(site_dir)
    print(f"Added news {args.date}-{args.slug}; "
          f"site now has {n_posts} posts, {n_news} news items.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--site-dir", default=SITE_DIR,
                        help="site root (default: parent of this script)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_post = sub.add_parser("post", help="add one social post")
    p_post.add_argument("--date", required=True)
    p_post.add_argument("--slug", required=True)
    p_post.add_argument("--title", required=True)
    p_post.add_argument("--caption-file", required=True)
    p_post.add_argument("--image", action="append", required=True)
    p_post.add_argument("--alt", action="append", required=True)
    p_post.add_argument("--instagram")
    p_post.add_argument("--facebook")
    p_post.add_argument("--threads")
    p_post.set_defaults(fn=cmd_post)

    p_news = sub.add_parser("news", help="add one news item")
    p_news.add_argument("--date", required=True)
    p_news.add_argument("--slug", required=True)
    p_news.add_argument("--title", required=True)
    p_news.add_argument("--body-file", required=True)
    p_news.add_argument("--image")
    p_news.add_argument("--alt")
    p_news.add_argument("--link-url")
    p_news.add_argument("--link-label")
    p_news.set_defaults(fn=cmd_news)

    p_rebuild = sub.add_parser("rebuild", help="regenerate all derived pages")
    p_rebuild.set_defaults(fn=lambda a: (print(
        "Rebuilt: %d posts, %d news items." % rebuild(a.site_dir)), 0)[1])

    args = parser.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
