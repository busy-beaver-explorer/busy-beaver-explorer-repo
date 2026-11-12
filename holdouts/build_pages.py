"""Build the site in pages/ from the machines' status.json files.

usage: python3 holdouts/build_pages.py

For every folder holdouts/M with a status.json this writes pages/holdouts/M/explainer.html (the interactive page:
the machine running in the browser, the step-by-step proof walkthrough, the ledger of results) and
pages/holdouts/M/proof-status.html (every claim sorted by what it rests on), and then pages/index.html, the landing
page that links to them. The pages are plain HTML with no build step of their own; .github/workflows/pages.yml
publishes the pages/ folder to GitHub Pages.

A machine's walkthrough lives in holdouts/M/py/proof_page.html and is copied into its status.json by
holdouts/M/py/proof_page.py, so after editing the walkthrough run that script first, then this one.
scripts/check_generated.sh checks that the committed pages are what this script writes.
"""
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "tools", "py"))
sys.path.insert(0, os.path.join(REPO, "tools", "pages"))

import build_explainer  # noqa: E402
import build_status  # noqa: E402

PAGES = os.path.join(REPO, "pages")
GITHUB = "https://github.com/busy-beaver-explorer/busy-beaver-explorer-repo"


def specs():
    for name in sorted(os.listdir(HERE)):
        p = os.path.join(HERE, name, "status.json")
        if os.path.isfile(p):
            with open(p) as f:
                yield name, json.load(f)


def triage():
    with open(os.path.join(HERE, "triage.json")) as f:
        return {r["machine"]: r for r in json.load(f)}


INDEX = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Busy Beaver Explorer</title>
<meta name="description" content="Two six-state Turing machines that bbchallenge left open, proved never to halt in Lean and in Coq, with pages that run them and walk through the proofs.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Martian+Mono:wght@400;500;700&display=swap">
<style>
:root {
  --paper: #EEF1F5; --surface: #FFFFFF; --ink: #142033; --muted: #5A6679; --rule: #D0D8E2; --link: #2B59CF;
  --kernel: #1F7A4D; --kernel-bg: #E2F3EA;
  --font-display: "Martian Mono", ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
  --font-body: "Atkinson Hyperlegible", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper: #0E131A; --surface: #161E29; --ink: #E5EBF3; --muted: #95A2B4; --rule: #2B3644; --link: #7C9DFF;
    --kernel: #6FD3A0; --kernel-bg: #15301F; color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --paper: #0E131A; --surface: #161E29; --ink: #E5EBF3; --muted: #95A2B4; --rule: #2B3644; --link: #7C9DFF;
  --kernel: #6FD3A0; --kernel-bg: #15301F; color-scheme: dark;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--paper); color: var(--ink); font-family: var(--font-body); font-size: 16px; line-height: 1.6; }
.wrap { max-width: 860px; margin: 0 auto; padding: 40px 16px 56px; display: grid; gap: 28px; }
h1, h2 { font-family: var(--font-display); margin: 0; letter-spacing: -0.01em; }
h1 { font-size: clamp(1.45rem, 3.2vw, 2.1rem); line-height: 1.2; }
h2 { font-size: 1rem; overflow-wrap: anywhere; }
p { margin: 0; max-width: 72ch; }
a { color: var(--link); }
code { font-family: var(--font-display); font-size: 0.86em; overflow-wrap: anywhere; }
.card { background: var(--surface); border: 1px solid var(--rule); border-radius: 8px; padding: 18px; display: grid; gap: 10px; }
.meta { color: var(--muted); font-size: 0.9rem; }
.tag { display: inline-block; font-size: 0.78rem; padding: 1px 8px; border-radius: 999px; color: var(--kernel); background: var(--kernel-bg); font-weight: 700; margin-right: 6px; }
.links { display: flex; flex-wrap: wrap; gap: 8px 18px; font-weight: 700; }
footer { color: var(--muted); font-size: 0.9rem; display: grid; gap: 8px; }
</style>
</head>
<body>
<main class="wrap">
<header style="display:grid;gap:12px">
 <h1>Busy Beaver Explorer</h1>
 <p>The <a href="https://bbchallenge.org">bbchallenge</a> project has sorted almost every six-state, two-symbol Turing
 machine into those that halt from a blank tape and those that never do. A few hundred <i>holdouts</i> are still
 open. This site covers two of them. Each is proved never to halt twice, once in Lean and once in Coq on top of
 <a href="https://github.com/meithecatte/busycoq">busycoq</a>. Each has a page that runs the machine in your browser
 and walks through the proof step by step, and a page that sorts every result by what it rests on.</p>
</header>
__CARDS__
<footer>
 <p>Everything here is built from the repository <a href="__GITHUB__">__GITHUB_SHORT__</a>: the Lean proofs, the Coq
 proofs, the scripts that generate them and the pages. Its README explains how to check each proof yourself.</p>
</footer>
</main>
</body>
</html>
"""


def card(name, spec, tri):
    r = tri.get(name, {})
    mid = f'bbchallenge machine #{r["id"]:,}' if r else ""
    return (f'<section class="card">\n'
            f' <h2><code>{html.escape(name)}</code></h2>\n'
            f' <p class="meta">{mid}</p>\n'
            f' <p><span class="tag">never halts</span>{spec.get("summary", "")}</p>\n'
            f' <p class="links"><a href="holdouts/{name}/explainer.html">Explainer and proof walkthrough</a>'
            f'<a href="holdouts/{name}/proof-status.html">What is proved, and how</a>'
            f'<a href="{GITHUB}/tree/main/holdouts/{name}">Source</a></p>\n'
            f'</section>')


def main():
    tri = triage()
    cards = []
    for name, spec in specs():
        d = os.path.join(PAGES, "holdouts", name)
        os.makedirs(d, exist_ok=True)
        home = spec.get("home", "../../index.html")
        with open(os.path.join(d, "explainer.html"), "w") as f:
            f.write(build_explainer.build(spec, home))
        with open(os.path.join(d, "proof-status.html"), "w") as f:
            f.write(build_status.build(spec, home))
        cards.append(card(name, spec, tri))
        print("wrote", os.path.relpath(d, REPO))
    page = (INDEX.replace("__CARDS__", "\n".join(cards)).replace("__GITHUB_SHORT__", GITHUB.split("github.com/")[1])
            .replace("__GITHUB__", GITHUB))
    with open(os.path.join(PAGES, "index.html"), "w") as f:
        f.write(page)
    print("wrote pages/index.html")


if __name__ == "__main__":
    main()
