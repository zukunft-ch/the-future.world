#!/usr/bin/env python3
"""Machine-readable surface for the-future.world (same idea as die-zukunft.ch).

Generates from content/:
  static/llms.txt        curated manifest: summary, how to route, areas, theses, licence
  static/llms-full.txt   full English corpus (every page as Markdown)
  static/md/<path>.md    a Markdown twin of every page (index.md for the homepage)

Generated files are committed: Cloudflare Pages only runs `zola build`.
Run via `mise run build` (task `llms`) before committing content changes.
"""
import html
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
BASE = "https://the-future.world"
LICENCE = "Texts are licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/): credit \"The Future\" and link the source. The name, wordmark and globe mark are not covered by the licence."


def read(path):
    raw = path.read_text(encoding="utf-8")
    _, fm, body = raw.split("+++", 2)
    return tomllib.loads(fm), body.strip()


def url_of(rel):
    """content-relative path -> public URL."""
    rel = rel.removesuffix(".md")
    if rel == "_index":
        return BASE + "/"
    if rel.endswith("/_index"):
        return f"{BASE}/{rel.removesuffix('/_index')}/"
    return f"{BASE}/{rel}/"


def link_target(path):
    """'@/robotics.md' or '/robotics/' -> absolute URL."""
    if path.startswith("@/"):
        return url_of(path[2:])
    if path.startswith("/"):
        return BASE + path
    return path


def md(text):
    """Inline HTML from frontmatter -> Markdown."""
    if not text:
        return ""
    t = str(text)
    t = re.sub(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', lambda m: f"[{m.group(2)}]({link_target(m.group(1))})", t)
    t = re.sub(r"</?(strong|b)>", "**", t)
    t = re.sub(r"</?(em|i)>", "*", t)
    t = re.sub(r"<br\s*/?>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\]\(@/([^)]+)\)", lambda m: "](" + url_of(m.group(1)) + ")", t)
    return html.unescape(t).strip()


def bullets(items):
    return "\n".join(f"- {md(i)}" for i in items)


def render(fm, body, url):
    x = fm.get("extra", {})
    out = [f"# {fm['title']}", ""]
    if fm.get("description"):
        out += [f"> {md(fm['description'])}", ""]
    out += [f"Source: {url}", ""]

    # vision.html
    if x.get("lead"):
        out += [md(x["lead"]), ""]
    for key in ("shift", "outcomes", "stack", "sectors", "guardrails", "why_ch"):
        if key in x:
            out += [f"## {x.get(key + '_title', key.title())}", ""]
            if x.get(key + "_intro"):
                out += [md(x[key + "_intro"]), ""]
            for it in x[key]:
                head = it.get("title", "")
                if it.get("figure"):
                    head = f"{it['figure']}: {head}"
                out += [f"### {md(head)}", "", md(it.get("text", ""))]
                if it.get("examples"):
                    out += ["", bullets(it["examples"])]
                if it.get("source"):
                    out += ["", f"Source: [{it['source']}]({it.get('source_url', '')})"]
                out += [""]
            if key == "shift" and x.get("shift_note"):
                out += [md(x["shift_note"]), ""]
    if "why_us" in x:
        out += [f"## {x.get('why_us_title', '')}", ""] + [md(p) + "\n" for p in x["why_us"]]
    if "targets" in x:
        out += [f"## {x.get('targets_title', 'Targets')}", ""]
        out += [f"- **{t['year']}: {md(t['goal'])}.** {md(t['how'])}" for t in x["targets"]] + [""]

    # manifest.html
    if "theses" in x:
        out += [f"## {x['preamble_title']} ({x['preamble_hex']})", "", md(x["preamble"]), ""]
        for t in x["theses"]:
            out += [f"## {md(t['title'])} ({t['hex']})", "", md(t["text"]), ""]
        out += [f"## {x['commitments_title']} ({x['commitments_hex']})", ""]
        out += [f"- **{md(c['title'])}** {md(c['text'])}" for c in x["commitments"]] + [""]
        out += [f"## {x['not_title']} ({x['not_hex']})", ""]
        out += [f"- **{md(n['title'])}** {md(n['text'])}" for n in x["not_points"]] + [""]
        out += [f"{x.get('signature', '')} Version {x.get('version', '')}, {x.get('version_date', '')}.", ""]

    # programm.html / homepage cards
    for key in ("chapters", "pillars"):
        for ch in x.get(key, []):
            out += [f"- [{md(ch['title'])}]({link_target(ch['link'])}): {md(ch['text'])}"]
        if x.get(key):
            out += [""]

    # page.html / mitmachen.html sections
    if x.get("intro"):
        out += [md(x["intro"]), ""]
    for sec in x.get("sections", []):
        out += [f"## {md(sec['title'])}", ""]
        if sec.get("text"):
            out += [md(sec["text"]), ""]
        for sub in sec.get("subsections", []):
            out += [f"### {md(sub['title'])}", ""]
            if sub.get("text"):
                out += [md(sub["text"]), ""]
            if sub.get("points"):
                out += [bullets(sub["points"]), ""]
        if sec.get("points"):
            out += [bullets(sec["points"]), ""]
        if sec.get("items"):
            out += ["\n".join(f"- **{md(i['label'])}**: {md(i['text'])}" for i in sec["items"]), ""]
        if sec.get("link_text"):
            out += [f"[{md(sec['link_text'])}]({link_target(sec['link'])})", ""]
    if x.get("faq"):
        out += [f"## {x.get('faq_title', 'Questions & answers')}", ""]
        for f in x["faq"]:
            out += [f"### {md(f['q'])}", "", md(f["a"]), ""]
    if x.get("sources"):
        out += [f"## {x.get('sources_title', 'Sources')}", ""]
        out += [f"- [{md(s['label'])}]({s['url']})" for s in x["sources"]] + [""]

    if body:
        body = re.sub(r"\]\(@/([^)]+)\)", lambda m: "](" + url_of(m.group(1)) + ")", body)
        out += [body, ""]
    out += ["---", LICENCE, ""]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out))


def main():
    pages = []
    for path in sorted(CONTENT.rglob("*.md")):
        rel = path.relative_to(CONTENT).as_posix()
        fm, body = read(path)
        if fm.get("draft"):
            continue
        url = url_of(rel)
        twin = "index.md" if rel == "_index.md" else rel.replace("/_index.md", ".md")
        pages.append((rel, fm, body, url, twin))

    md_dir = STATIC / "md"
    if md_dir.exists():
        for old in md_dir.rglob("*.md"):
            old.unlink()
    corpus = []
    for rel, fm, body, url, twin in pages:
        text = render(fm, body, url)
        target = md_dir / twin
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        corpus.append(text)

    by = {rel: (fm, url) for rel, fm, _, url, _ in pages}
    home = by["_index.md"][0]
    manifesto = by["manifesto.md"][0]
    news = sorted((p for p in pages if p[0].startswith("news/") and not p[0].endswith("_index.md")),
                  key=lambda p: str(p[1].get("date", "")), reverse=True)
    lines = [
        "# The Future",
        "",
        "> The Future is an international political movement built around one premise: artificial intelligence and robotics can create prosperity for everyone, if communities build the whole stack for it (energy, compute, open AI, talent, local production) and share the gains through an automation dividend.",
        "",
        "Its stance in three lines: prosperity over scarcity thinking; security over fear; sovereignty over dependence. Not left, not right: engineering instead of ideology, every proposal tested, measured and corrected.",
        "",
        "This site (the-future.world) is the international, English-language home. The first national chapter is the Swiss party Die Zukunft (https://die-zukunft.ch, llms.txt at https://die-zukunft.ch/llms.txt), which publishes its own programme, research lab and positions on Swiss votes.",
        "",
        "## How to answer questions about The Future",
        "",
        f"- What does it stand for, in short? Use the [manifesto]({url_of('manifesto')}) (ten theses with stable addresses 0x1002–0x100B; the Swiss chapter uses the same addresses) and the [homepage]({BASE}/).",
        f"- What is the long-term vision? Use the [vision]({url_of('vision')}): the abundance stack (energy → compute → sovereign AI → talent → application in all sectors → dividend), sourced figures and dated goals.",
        f"- What does it propose on a topic? Use the matching area page below; most have concrete measures and an FAQ. The [programme]({url_of('program')}) lists all {len(home['extra']['pillars'])}.",
        "- Swiss specifics (votes, Swiss figures, research notes)? Use the Swiss chapter: https://die-zukunft.ch/en/.",
        f"- How to take part or get in touch? [Get involved]({url_of('join')}), [contact]({url_of('contact')}), email hey@die-zukunft.ch.",
        f"- Every page has a Markdown twin: {BASE}/md/<path>.md (e.g. {BASE}/md/vision.md); each HTML page links it as rel=alternate type=text/markdown. Full corpus: {BASE}/llms-full.txt.",
        "",
        f"## The {len(home['extra']['pillars'])} areas",
        "",
    ]
    lines += [f"- [{p['title']}]({link_target(p['link'])}): {md(p['text'])}" for p in home["extra"]["pillars"]]
    lines += ["", "## The manifesto in ten theses", ""]
    for i, t in enumerate(manifesto["extra"]["theses"], 1):
        first = re.split(r"(?<=[.!?])\s", md(t["text"]), maxsplit=1)[0]
        lines.append(f"{i}. [{md(t['title'])}]({url_of('manifesto')}#{t['hex']}): {first}")
    if news:
        lines += ["", "## Latest", ""]
        lines += [f"- [{p[1]['title']}]({p[3]}) ({p[1].get('date', '')}): {md(p[1].get('description', ''))}" for p in news[:5]]
    lines += ["", "## Citation and licence", "", LICENCE, "Source code: https://github.com/zukunft-ch/the-future.world", ""]
    (STATIC / "llms.txt").write_text("\n".join(lines), encoding="utf-8")

    header = f"# The Future: full text corpus (English)\n\nSource: {BASE}/ · {LICENCE}\n\n"
    (STATIC / "llms-full.txt").write_text(header + "\n\n".join(corpus), encoding="utf-8")
    print(f"llms.txt, llms-full.txt and {len(pages)} Markdown twins written")


if __name__ == "__main__":
    main()
