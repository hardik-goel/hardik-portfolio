#!/usr/bin/env python3
"""Build per-post static pages under /blog from Substack + Medium RSS.

Makes hardik-portfolio-rho.vercel.app the canonical source of truth for
each post: every page owns its <head> (canonical=self, OG, Twitter,
BlogPosting JSON-LD) and republishes the full content. Cross-posted
duplicates are merged; both platform URLs are kept as sameAs + read-on links.

Run:  python3 build_blog.py
Output: blog/index.html, blog/<slug>.html, blog/blog.css, sitemap.xml
"""
import os
import re
import glob
import html
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

SITE = "https://hardik-portfolio-rho.vercel.app"
AUTHOR = "Hardik Goel"
PROFILE_IMG = f"{SITE}/resources/hardik.jpg"
OUT_DIR = "blog"

FEEDS = {
    "Substack": "https://goelh.substack.com/feed",
    "Medium": "https://medium.com/feed/@hardik.goel214",
}
FALLBACK = {
    "Substack": "https://goelh.substack.com/",
    "Medium": "https://medium.com/@hardik.goel214",
}

NS = {"content": "http://purl.org/rss/1.0/modules/content/"}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=20).read()


def slugify(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return (s[:80]).strip("-") or "post"


def norm_title(title):
    return re.sub(r"[^a-z0-9]", "", title.lower())


def first_image(body):
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', body or "")
    return m.group(1) if m else PROFILE_IMG


def to_iso(pubdate):
    try:
        return parsedate_to_datetime(pubdate).date().isoformat()
    except Exception:
        return ""


def fmt_date(pubdate):
    try:
        return parsedate_to_datetime(pubdate).strftime("%b %-d, %Y")
    except Exception:
        return ""


def parse_feed(platform, url):
    posts = []
    try:
        root = ET.fromstring(fetch(url))
    except Exception as e:
        print(f"  ! {platform} fetch failed: {e}")
        return posts
    for it in root.findall(".//item"):
        title = (it.findtext("title") or "Untitled").strip()
        link = (it.findtext("link") or "").strip()
        pub = it.findtext("pubDate") or ""
        ce = it.find("content:encoded", NS)
        body = ce.text if (ce is not None and ce.text) else (it.findtext("description") or "")
        posts.append({
            "platform": platform,
            "title": html.unescape(title),
            "link": link,
            "pubDate": pub,
            "iso": to_iso(pub),
            "date": fmt_date(pub),
            "body": body or "",
        })
    print(f"  {platform}: {len(posts)} posts")
    return posts


def merge(all_posts):
    """Dedup cross-posted items by normalized title. Prefer longer body.
    Collect every platform link as sources."""
    by_key = {}
    for p in all_posts:
        k = norm_title(p["title"])
        if k not in by_key:
            p = dict(p)
            p["sources"] = {p["platform"]: p["link"]}
            by_key[k] = p
        else:
            cur = by_key[k]
            cur["sources"][p["platform"]] = p["link"]
            if len(p["body"]) > len(cur["body"]):
                cur["body"] = p["body"]
            if not cur["iso"] and p["iso"]:
                cur["iso"], cur["date"], cur["pubDate"] = p["iso"], p["date"], p["pubDate"]
    posts = list(by_key.values())
    posts.sort(key=lambda p: p["pubDate"] and parsedate_to_datetime(p["pubDate"]) or 0, reverse=True)
    for p in posts:
        p["slug"] = slugify(p["title"])
        p["url"] = f"{SITE}/{OUT_DIR}/{p['slug']}.html"
        p["image"] = first_image(p["body"])
    # guard against slug collisions
    seen = {}
    for p in posts:
        s = p["slug"]
        if s in seen:
            seen[s] += 1
            p["slug"] = f"{s}-{seen[s]}"
            p["url"] = f"{SITE}/{OUT_DIR}/{p['slug']}.html"
        else:
            seen[s] = 1
    return posts


CSS = """:root{--bg:#06101e;--bg2:#0b1828;--bg3:#101f33;--blue:#4a8cf7;--teal:#2dd4bf;
--text:#ccd8eb;--text2:#7e94b0;--bdr:rgba(255,255,255,.08);}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
line-height:1.7;font-size:17px}
a{color:var(--blue);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:720px;margin:0 auto;padding:32px 20px 80px}
.top{display:flex;justify-content:space-between;align-items:center;gap:16px;
padding-bottom:20px;border-bottom:1px solid var(--bdr);margin-bottom:32px;flex-wrap:wrap}
.top .home{color:var(--text2);font-weight:600}
.badge{font-size:12px;color:var(--teal);border:1px solid var(--bdr);
border-radius:999px;padding:4px 12px}
h1{font-size:2rem;line-height:1.25;margin:0 0 12px}
.meta{color:var(--text2);font-size:14px;margin-bottom:8px}
.sources{margin:20px 0 36px;display:flex;gap:10px;flex-wrap:wrap}
.sources a{border:1px solid var(--bdr);border-radius:8px;padding:7px 14px;
color:var(--text);font-size:14px}
.sources a:hover{border-color:var(--blue);text-decoration:none}
article img{max-width:100%;height:auto;border-radius:10px;margin:20px 0}
article h2,article h3{margin-top:36px;line-height:1.3}
article pre{background:var(--bg3);padding:16px;border-radius:10px;overflow-x:auto}
article code{background:var(--bg3);padding:2px 6px;border-radius:5px;font-size:.9em}
article blockquote{border-left:3px solid var(--blue);margin:20px 0;padding:4px 20px;
color:var(--text2)}
article a{text-decoration:underline}
.foot{margin-top:56px;padding-top:24px;border-top:1px solid var(--bdr);
color:var(--text2);font-size:14px}
.postlist{list-style:none;padding:0;margin:0}
.postlist li{padding:20px 0;border-bottom:1px solid var(--bdr)}
.postlist h2{margin:0 0 6px;font-size:1.25rem}
.postlist .meta{margin:0}
"""


def head(title, desc, canonical, image, jsonld):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="author" content="{AUTHOR}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="{image}">
<meta property="og:site_name" content="{AUTHOR}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="{image}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/blog/blog.css">
<script type="application/ld+json">
{jsonld}
</script>
</head>
<body>
<div class="wrap">
<div class="top"><a class="home" href="/">← Hardik Goel</a><span class="badge">Writing</span></div>
"""


def excerpt(body, n=160):
    text = re.sub(r"<[^>]+>", " ", body)
    text = html.unescape(re.sub(r"\s+", " ", text)).strip()
    return (text[:n].rsplit(" ", 1)[0] + "…") if len(text) > n else text


def build_post_page(p):
    desc = excerpt(p["body"])
    same_as = ",\n    ".join(f'"{u}"' for u in p["sources"].values())
    jsonld = f"""{{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": {json_str(p['title'])},
  "description": {json_str(desc)},
  "image": "{p['image']}",
  "datePublished": "{p['iso']}",
  "dateModified": "{p['iso']}",
  "url": "{p['url']}",
  "mainEntityOfPage": {{ "@type": "WebPage", "@id": "{p['url']}" }},
  "author": {{ "@type": "Person", "@id": "{SITE}/#person", "name": "{AUTHOR}", "url": "{SITE}/" }},
  "publisher": {{ "@type": "Person", "@id": "{SITE}/#person", "name": "{AUTHOR}" }},
  "sameAs": [
    {same_as}
  ]
}}"""
    src_links = "".join(
        f'<a href="{u}" target="_blank" rel="noopener noreferrer">Read on {plat} ↗</a>'
        for plat, u in p["sources"].items()
    )
    return head(p["title"], desc, p["url"], p["image"], jsonld) + f"""<article>
<h1>{html.escape(p['title'])}</h1>
<div class="meta">{p['date']} · by {AUTHOR}</div>
<div class="sources">{src_links}</div>
{p['body']}
</article>
<div class="foot">Originally shared on {', '.join(p['sources'].keys())}. Canonical home: this page.<br>
More at <a href="/">hardikgoel portfolio</a>.</div>
</div>
</body>
</html>"""


def build_index_page(posts):
    desc = "Essays by Hardik Goel on AI, data systems, and digital cognition — canonical home for posts also on Substack and Medium."
    jsonld = f"""{{
  "@context": "https://schema.org",
  "@type": "Blog",
  "url": "{SITE}/{OUT_DIR}/",
  "name": "Hardik Goel — Writing",
  "author": {{ "@type": "Person", "@id": "{SITE}/#person", "name": "{AUTHOR}" }},
  "blogPost": [
{",".join(chr(10) + '    { "@type": "BlogPosting", "headline": ' + json_str(p['title']) + ', "url": "' + p['url'] + '", "datePublished": "' + p['iso'] + '" }' for p in posts)}
  ]
}}"""
    items = "\n".join(
        f'<li><h2><a href="{p["url"]}">{html.escape(p["title"])}</a></h2>'
        f'<div class="meta">{p["date"]}</div></li>'
        for p in posts
    )
    return head("Writing — Hardik Goel", desc, f"{SITE}/{OUT_DIR}/", PROFILE_IMG, jsonld) + f"""<article>
<h1>Writing</h1>
<div class="meta">Canonical home for essays also published on Substack &amp; Medium.</div>
<ul class="postlist">
{items}
</ul>
</article>
<div class="foot">Back to <a href="/">portfolio</a>.</div>
</div>
</body>
</html>"""


def json_str(s):
    import json
    return json.dumps(s, ensure_ascii=False)


def write_sitemap(posts):
    urls = [f"{SITE}/", f"{SITE}/{OUT_DIR}/"] + [p["url"] for p in posts]
    lastmods = {u: "" for u in urls}
    for p in posts:
        lastmods[p["url"]] = p["iso"]
    body = "\n".join(
        f"  <url>\n    <loc>{u}</loc>"
        + (f"\n    <lastmod>{lastmods[u]}</lastmod>" if lastmods.get(u) else "")
        + "\n  </url>"
        for u in urls
    )
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + body + "\n</urlset>\n")


def main():
    print("Fetching feeds...")
    allp = []
    for plat, url in FEEDS.items():
        allp += parse_feed(plat, url)
    posts = merge(allp)
    # Drop thin/placeholder posts (e.g. Substack "Coming soon") — thin pages hurt SEO.
    MIN_CHARS = 400
    kept = [p for p in posts if len(excerpt(p["body"], 100000)) >= MIN_CHARS]
    dropped = len(posts) - len(kept)
    posts = kept
    print(f"Merged -> {len(posts)} unique posts ({dropped} thin dropped)")

    os.makedirs(OUT_DIR, exist_ok=True)
    for stale in glob.glob(os.path.join(OUT_DIR, "*.html")):
        os.remove(stale)
    with open(os.path.join(OUT_DIR, "blog.css"), "w", encoding="utf-8") as f:
        f.write(CSS)
    for p in posts:
        with open(os.path.join(OUT_DIR, f"{p['slug']}.html"), "w", encoding="utf-8") as f:
            f.write(build_post_page(p))
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_index_page(posts))
    write_sitemap(posts)
    print(f"Wrote {len(posts)} post pages + blog/index.html + blog/blog.css + sitemap.xml")


if __name__ == "__main__":
    main()
