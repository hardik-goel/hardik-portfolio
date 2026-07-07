#!/usr/bin/env python3
"""Vendor web fonts locally to drop external CDN calls (perf + privacy).

- Google Fonts (Inter, JetBrains Mono): downloads the *latin* woff2 subsets
  and emits local @font-face rules.
- Tabler Icons: subsets the 829KB webfont down to only the icons actually
  used in index.html, and emits just those .ti-* class rules.

Output: resources/fonts/*.woff2 + resources/fonts/vendor.css
Then index.html links /resources/fonts/vendor.css instead of googleapis /
jsdelivr. Rerun if you add new icons or font weights.

Requires fonttools + brotli:  pip install fonttools brotli
Run:  python3 build_fonts.py
"""
import os
import re
import urllib.request
from fontTools import subset
from fontTools.ttLib import TTFont

FONTS_DIR = "resources/fonts"
UA = {"User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")}
GF_URL = ("https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700"
          "&family=JetBrains+Mono:wght@400;500&display=swap")
TABLER_VER = "3.34.0"
TABLER_CSS = f"https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@{TABLER_VER}/dist/tabler-icons.min.css"
TABLER_WOFF2 = f"https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@{TABLER_VER}/dist/fonts/tabler-icons.woff2"


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()


def build_google():
    css = get(GF_URL).decode()
    blocks = re.findall(r'/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{.*?\})', css, re.S)
    out = []
    for subset_name, block in blocks:
        if subset_name != "latin":
            continue
        fam = re.search(r"font-family:\s*'([^']+)'", block).group(1)
        wt = re.search(r"font-weight:\s*(\d+)", block).group(1)
        url = re.search(r"url\((https[^)]+\.woff2)\)", block).group(1)
        rng = re.search(r"unicode-range:\s*([^;]+);", block).group(1)
        fn = f"{fam.lower().replace(' ', '')}-{wt}.woff2"
        with open(os.path.join(FONTS_DIR, fn), "wb") as f:
            f.write(get(url))
        out.append(
            f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{wt};"
            f"font-display:swap;src:url('/resources/fonts/{fn}') format('woff2');"
            f"unicode-range:{rng};}}"
        )
        print("  google:", fn)
    return "\n".join(out)


def used_icons():
    h = open("index.html").read()
    names = set(re.findall(r'\bti-([a-z0-9-]+)', h))
    return {n for n in names if n != "icons"}


def build_tabler(used):
    css = get(TABLER_CSS).decode()
    rules, codepoints, missing = [], set(), []
    for name in sorted(used):
        m = re.search(r'\.ti-' + re.escape(name) + r':before\{content:"\\([0-9a-fA-F]+)"\}', css)
        if not m:
            missing.append(name)
            continue
        codepoints.add(int(m.group(1), 16))
        rules.append(f'.ti-{name}:before{{content:"\\{m.group(1)}"}}')
    if missing:
        print("  ! not real tabler icons (skipped):", ", ".join(missing))

    full = os.path.join(FONTS_DIR, "_tabler-full.woff2")
    with open(full, "wb") as f:
        f.write(get(TABLER_WOFF2))
    before = os.path.getsize(full)
    out = os.path.join(FONTS_DIR, "tabler-icons.woff2")
    font = TTFont(full)
    ss = subset.Subsetter()
    ss.populate(unicodes=codepoints)
    ss.subset(font)
    font.flavor = "woff2"
    font.save(out)
    os.remove(full)
    print(f"  tabler: {len(codepoints)} glyphs, {before}b -> {os.path.getsize(out)}b")

    face = ("@font-face{font-family:'tabler-icons';font-style:normal;font-weight:400;"
            "font-display:swap;src:url('/resources/fonts/tabler-icons.woff2') format('woff2');}")
    base = ('.ti{font-family:"tabler-icons" !important;speak:none;font-style:normal;'
            'font-weight:normal;font-variant:normal;text-transform:none;line-height:1;'
            '-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}')
    return "\n".join([face, base] + rules)


def main():
    os.makedirs(FONTS_DIR, exist_ok=True)
    print("Google Fonts (latin subset):")
    g = build_google()
    print("Tabler Icons (subset to used):")
    t = build_tabler(used_icons())
    with open(os.path.join(FONTS_DIR, "vendor.css"), "w", encoding="utf-8") as f:
        f.write("/* Vendored by build_fonts.py — do not edit by hand */\n" + g + "\n" + t + "\n")
    print("Wrote resources/fonts/vendor.css")


if __name__ == "__main__":
    main()
