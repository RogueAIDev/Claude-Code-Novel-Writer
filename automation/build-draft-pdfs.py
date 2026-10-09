#!/usr/bin/env python3
"""Build reading PDFs of the manuscript in the author's template layout.

For every current chapter draft in manuscript/chapters, this writes:

  manuscript/<Ordinal> Draft/Scenes/CH<n>_S<s>_Draft<d>.pdf     one file per scene
  manuscript/<Ordinal> Draft/Chapters/Chapter<n>_Draft<book>.pdf  the whole chapter
  manuscript/<Ordinal> Draft/Full Draft/Draft<book>_Whole_Manuscript_So_Far.pdf

The layout follows templates/*.pdf: US Letter, 1-inch margins, Times New
Roman 12pt justified with first-line indents, a large chapter number, the
chapter title, an italic grey place-and-date line, centred *** scene breaks,
and each chapter starting on a new page. Scene PDFs end with an "Added
Details not in Scene Packet" appendix read from manuscript/added-details/.

Rendering uses headless Google Chrome, which macOS users usually have.

Usage:
  python3 automation/build-draft-pdfs.py [--book-draft 1]
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHAPTERS_DIR = ROOT / "manuscript" / "chapters"
DETAILS_DIR = ROOT / "manuscript" / "added-details"
OUTLINE = ROOT / "planning" / "novel-outline.json"
CHAPTER_RE = re.compile(r"^chapter-(\d+)(?:_draft-(\d+))?\.md$")
ORDINALS = {1: "First", 2: "Second", 3: "Third", 4: "Fourth", 5: "Fifth",
            6: "Sixth", 7: "Seventh", 8: "Eighth", 9: "Ninth", 10: "Tenth"}
CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]

CSS = """
@page { size: Letter; margin: 1in; }
html, body { margin: 0; padding: 0; }
body { font-family: "Times New Roman", Times, serif; font-size: 12pt;
       line-height: 1.65; color: #000; }
.prose p { text-indent: 0.5in; margin: 0 0 9pt 0; text-align: justify; }
.chapter { break-before: page; }
.chapter:first-child { break-before: auto; }
.chapnum { font-size: 40pt; font-weight: bold; text-align: center;
           margin: 0.55in 0 26pt 0; line-height: 1; }
.chaptitle { font-size: 22pt; text-align: center; margin: 0 0 14pt 0; line-height: 1.2; }
.place { font-size: 15pt; font-style: italic; color: #6b6b6b; text-align: center;
         margin: 0 0 8pt 0; line-height: 1.3; }
.scenelabel { font-size: 11pt; text-align: center; letter-spacing: 0.06em;
              font-variant: small-caps; margin: 0 0 22pt 0; }
.headgap { height: 18pt; }
.prose p.break { text-align: center; text-indent: 0; margin: 10pt 0 26pt 0;
         font-size: 10pt; }
.titlepage { text-align: center; padding-top: 3.1in; break-after: page; }
.titlepage .t { font-size: 26pt; margin-bottom: 14pt; }
.titlepage .s { font-size: 16pt; font-style: italic; color: #6b6b6b; margin-bottom: 18pt; }
.titlepage .b { font-size: 11pt; }
.appendix { break-before: page; font-size: 11.5pt; line-height: 1.6; }
.appendix h1 { font-size: 22pt; font-weight: normal; margin: 0.3in 0 30pt 0; }
.appendix p { margin: 0 0 12pt 0; text-align: left; }
.appendix h3 { font-size: 11.5pt; font-weight: bold; margin: 14pt 0 6pt 0; }
.appendix ul { margin: 0 0 6pt 0; padding-left: 0.55in; }
.appendix li { margin: 0 0 2pt 0; }
.appendix .decided { font-style: italic; color: #555; }
"""


def inline(text: str) -> str:
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"\*(.+?)\*", r"<em>\1</em>", out)
    return out


def parse_chapter(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    number = title = place = None
    body: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            text = stripped.lstrip("#").strip().strip("*").strip()
            text = text.replace("\\-", "-").replace("\\*", "*")
            m = re.match(r"Chapter\s+(\d+)", text)
            if m and number is None:
                number = int(m.group(1))
            elif stripped.startswith("##") and place is None and text not in ("***",):
                place = re.sub(r"\s+-\s+", ", ", text)
            elif title is None and not stripped.startswith("##"):
                title = text
            continue
        body.append(stripped)
    # A "***" followed by an HTML comment containing "same scene" is a viewpoint
    # change inside one scene: it prints as a break but does not start a new scene.
    scenes: list[list[str]] = [[]]
    for idx, line in enumerate(body):
        if line == "***":
            following = next((l for l in body[idx + 1:] if l), "")
            if following.startswith("<!--") and "same scene" in following:
                scenes[-1].append("***")
            elif scenes[-1]:
                scenes.append([])
            continue
        if line.startswith("<!--"):
            continue
        if line:
            scenes[-1].append(line)
    scenes = [s for s in scenes if s]
    return {"number": number, "title": title or "", "place": place or "", "scenes": scenes}


def parse_details(chapter: int) -> dict[int, dict]:
    path = DETAILS_DIR / f"chapter-{chapter}.md"
    result: dict[int, dict] = {}
    if not path.exists():
        return result
    current = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        m = re.match(r"^## Scene (\d+)\s*\(Draft (\d+)\)", line)
        if m:
            current = {"draft": int(m.group(2)), "sections": []}
            result[int(m.group(1))] = current
            continue
        if current is None:
            continue
        if line.startswith("### "):
            current["sections"].append({"heading": line[4:].strip(), "items": []})
        elif line.startswith("- "):
            if not current["sections"]:
                current["sections"].append({"heading": "", "items": []})
            current["sections"][-1]["items"].append(line[2:].strip())
    return result


def scene_titles(chapter: int) -> list[str]:
    try:
        data = json.loads(OUTLINE.read_text(encoding="utf-8"))
        return [s["title"] for s in data["chapters"][str(chapter)]["scenes"]]
    except (OSError, KeyError, ValueError):
        return []


def heading_html(ch: dict, scene_label: str | None = None) -> str:
    parts = [f'<div class="chapnum">{ch["number"]}</div>',
             f'<div class="chaptitle">{inline(ch["title"])}</div>',
             f'<div class="place">{inline(ch["place"])}</div>']
    parts.append(f'<div class="scenelabel">{inline(scene_label)}</div>' if scene_label
                 else '<div class="headgap"></div>')
    return "".join(parts)


def scene_html(paragraphs: list[str]) -> str:
    return "".join('<p class="break">***</p>' if p == "***" else f"<p>{inline(p)}</p>"
                   for p in paragraphs) + '<p class="break">***</p>'


def chapter_html(ch: dict) -> str:
    return ('<section class="chapter prose">' + heading_html(ch)
            + "".join(scene_html(s) for s in ch["scenes"]) + "</section>")


def appendix_html(details: dict | None) -> str:
    if not details or not details["sections"]:
        return ""
    out = ['<section class="appendix"><h1>Added Details not in Scene Packet</h1>',
           "<p>Every detail in this scene that its scene packet does not supply, in the order it "
           "appears. Items marked <em>decided</em> have since been approved and recorded in the "
           "planning documents. Everything else is open to change in the next draft.</p>"]
    for sec in details["sections"]:
        if sec["heading"]:
            out.append(f"<h3>{inline(sec['heading'])}</h3>")
        out.append("<ul>")
        for item in sec["items"]:
            m = re.search(r"\s*\((decided[^)]*)\)\s*$", item)
            if m:
                item = item[: m.start()]
                out.append(f'<li>{inline(item)} <span class="decided">({html.escape(m.group(1))})</span></li>')
            else:
                out.append(f"<li>{inline(item)}</li>")
        out.append("</ul>")
    out.append("</section>")
    return "".join(out)


def page(title: str, inner: str) -> str:
    return (f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(title)}</title>"
            f"<style>{CSS}</style></head><body>{inner}</body></html>")


def render(chrome: str, html_text: str, out_pdf: Path, workdir: Path) -> None:
    src = workdir / (out_pdf.stem + ".html")
    src.write_text(html_text, encoding="utf-8")
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
           "--print-to-pdf-no-header", f"--print-to-pdf={out_pdf}", src.as_uri()]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0 or not out_pdf.exists():
        sys.exit(f"Chrome failed to render {out_pdf.name}:\n{result.stderr[-800:]}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--book-draft", type=int, default=1,
                        help="Which full draft of the book this is (1 = First Draft).")
    args = parser.parse_args()

    chrome = next((c for c in CHROME_CANDIDATES if c and Path(c).exists()), None)
    if not chrome:
        sys.exit("Google Chrome or Chromium is required to render PDFs.")

    chapters = []
    for path in CHAPTERS_DIR.glob("chapter-*.md"):
        m = CHAPTER_RE.match(path.name)
        if m:
            chapters.append((int(m.group(1)), int(m.group(2) or 1), path))
    chapters.sort()
    if not chapters:
        sys.exit("No chapter drafts found in manuscript/chapters.")

    meta = json.loads((ROOT / "manuscript" / "metadata.json").read_text(encoding="utf-8"))
    ordinal = ORDINALS.get(args.book_draft, f"Draft {args.book_draft}")
    base = ROOT / "manuscript" / (f"{ordinal} Draft" if args.book_draft in ORDINALS else ordinal)
    book = args.book_draft
    written: list[Path] = []

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        parsed = []
        for number, _draft, path in chapters:
            ch = parse_chapter(path)
            ch["number"] = ch["number"] or number
            parsed.append(ch)
            details = parse_details(ch["number"])
            titles = scene_titles(ch["number"])
            for i, paragraphs in enumerate(ch["scenes"], start=1):
                scene_draft = details.get(i, {}).get("draft", book)
                label = f"Scene {i}" + (f" · {titles[i-1]}" if i <= len(titles) else "")
                body = ('<section class="chapter prose">' + heading_html(ch, label)
                        + scene_html(paragraphs) + "</section>" + appendix_html(details.get(i)))
                out = base / "Scenes" / f"CH{ch['number']}_S{i}_Draft{scene_draft}.pdf"
                render(chrome, page(out.stem, body), out, work)
                written.append(out)
            out = base / "Chapters" / f"Chapter{ch['number']}_Draft{book}.pdf"
            render(chrome, page(out.stem, chapter_html(ch)), out, work)
            written.append(out)

        title_page = ('<div class="titlepage">'
                      f'<div class="t">{inline(meta.get("title") or "Untitled")}</div>'
                      f'<div class="s">{inline(meta.get("series") or "")}: Vol. {meta.get("book_number", 1)}</div>'
                      f'<div class="b">By {inline(meta.get("author_byline") or meta.get("author") or "")}</div>'
                      "</div>")
        out = base / "Full Draft" / f"Draft{book}_Whole_Manuscript_So_Far.pdf"
        render(chrome, page(out.stem, title_page + "".join(chapter_html(c) for c in parsed)), out, work)
        written.append(out)

    for path in written:
        print(f"  {path.relative_to(ROOT)}")
    print(f"Built {len(written)} PDFs.")


if __name__ == "__main__":
    main()
