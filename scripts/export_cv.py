#!/usr/bin/env python3
"""Exports a CV written in Markdown to PDF with the CV template, plus one PNG
preview per page.

  python3 scripts/export_cv.py <job folder | cv.md> [--name FILE_NAME] [--no-preview]

For a job folder (or its artifacts/cv.md) the PDF goes to
artifacts/<cv_file_pattern>.pdf, previews to artifacts/cv-preview/, and
`cv_pdf` in metadata.yml points to the PDF. For any other Markdown file the
PDF is written next to it.

Needs the optional PDF tools: run scripts/setup-pdf.sh once per machine.

CV format: optional front matter with `name` and a `header` list of items
(`text`, optional `link`, optional `newLine: true`); `## ` starts a section;
a line with only `\\newpage` forces a page break. See templates/cv.md.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VENV_PYTHON = REPO_ROOT / ".venv" / "bin" / "python"

try:
    import yaml
    from markdown_it import MarkdownIt
    from mdit_py_plugins.deflist import deflist_plugin
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import sync_playwright
except ImportError:
    if __name__ != "__main__":
        raise
    # Use the virtual environment from scripts/setup-pdf.sh when it exists.
    if VENV_PYTHON.exists() and Path(sys.prefix).resolve() != (REPO_ROOT / ".venv").resolve():
        os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), *sys.argv])
    print("export_cv: the PDF tools are not installed. Run once: scripts/setup-pdf.sh", file=sys.stderr)
    sys.exit(1)

import base64  # noqa: E402
import re  # noqa: E402
import unicodedata  # noqa: E402

from lib.flat_yaml import parse_flat_yaml, parse_front_matter  # noqa: E402
from lib.paths import resolve_data_root  # noqa: E402

TEMPLATE_DIR = REPO_ROOT / "scripts" / "cv"

# The template's fixed settings (the "classic" style of the earlier CV builder).
STYLE = {
    "paper_width_mm": 210,  # A4
    "paper_height_mm": 297,
    "margin_top": 46,
    "margin_right": 44,
    "margin_bottom": 46,
    "margin_left": 44,
    "font_family": "Inter, Arial, sans-serif",
    "font_size": 12,
    "line_height": 1.45,
    "paragraph_spacing": 7,
    "theme_color": "#b7791f",
    "text_align": "justify",
}

ICONS = {
    "award": '<path d="m15.477 12.89 1.515 8.526a.5.5 0 0 1-.81.47l-3.58-2.687a1 1 0 0 0-1.197 0l-3.586 2.686a.5.5 0 0 1-.81-.47l1.514-8.526"/><circle cx="12" cy="8" r="6"/>',
    "briefcase": '<path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/><rect width="20" height="14" x="2" y="6" rx="2"/>',
    "graduation": '<path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>',
    "github": '<path d="M15 22v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 19 4.77 5.07 5.07 0 0 0 18.91 1S17.73.65 15 2.48a13.38 13.38 0 0 0-7 0C5.27.65 4.09 1 4.09 1A5.07 5.07 0 0 0 4 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 8 18.13V22"/><path d="M9 18c-4.51 2-5-2-7-2"/>',
    "languages": '<path d="m5 8 6 6"/><path d="m4 14 6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="m22 22-5-10-5 10"/><path d="M14 18h6"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
    "linkedin": '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-4 0v7h-4v-7a6 6 0 0 1 6-6z"/><rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/>',
    "mail": '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.12.9.33 1.77.63 2.61a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.47-1.2a2 2 0 0 1 2.11-.45c.84.3 1.71.51 2.61.63A2 2 0 0 1 22 16.92z"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.68 0C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
    "sparkles": '<path d="M9.94 14.5 8.5 22l-1.44-7.5L0 13l7.06-1.5L8.5 4l1.44 7.5L17 13z"/><path d="M19 3v4"/><path d="M21 5h-4"/><path d="M18 17v2"/><path d="M19 18h-2"/>',
    "user": '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
}


def svg_icon(name: str, class_name: str) -> str:
    return (
        f'<svg class="{class_name}" data-icon-name="{name}" width="1em" height="1em" '
        'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        f"{ICONS[name]}</svg>"
    )


def section_icon(title: str) -> str:
    t = title.lower()
    if "experience" in t:
        return "briefcase"
    if "education" in t:
        return "graduation"
    if "cert" in t:
        return "award"
    if "skill" in t or "competenc" in t:
        return "sparkles"
    if "summary" in t or "profile" in t:
        return "user"
    if "language" in t:
        return "languages"
    return "shield"


def contact_icon(item: dict) -> str:
    text = item["text"].lower()
    link = (item.get("link") or "").lower()
    if link.startswith("mailto:") or "@" in text:
        return "mail"
    if link.startswith("tel:") or re.search(r"\+?\(?\d[\d\s().-]{6,}", item["text"]):
        return "phone"
    if "github.com" in link or "github" in text:
        return "github"
    if "linkedin.com" in link or "linkedin" in text:
        return "linkedin"
    if "language" in text:
        return "languages"
    return "link"


def split_front_matter(markdown: str) -> tuple[dict, str]:
    m = re.match(r"^---[ \t]*\r?\n([\s\S]*?)\r?\n---[ \t]*(?:\r?\n|$)", markdown)
    if not m:
        return {}, markdown
    data = yaml.safe_load(m.group(1)) or {}
    return (data if isinstance(data, dict) else {}), markdown[m.end() :]


def header_items(data: dict) -> list[dict]:
    items = []
    for raw in data.get("header") or []:
        if isinstance(raw, dict) and isinstance(raw.get("text"), str):
            items.append(
                {
                    "text": raw["text"],
                    "link": raw["link"] if isinstance(raw.get("link"), str) else None,
                    "new_line": raw.get("newLine") is True,
                }
            )
    return items


def render_header(data: dict) -> str:
    name = f"<h1>{data['name']}</h1>" if isinstance(data.get("name"), str) else ""
    parts = []
    for index, item in enumerate(header_items(data)):
        text = re.sub(r"""<span\s+class=["']iconify["'][^>]*></span>\s*""", "", item["text"], flags=re.I)
        content = f'<a href="{item["link"]}" target="_blank" rel="noopener noreferrer">{text}</a>' if item["link"] else text
        line_break = '<span class="resume-header-break" aria-hidden="true"></span>' if item["new_line"] else ""
        kind = "resume-header-title" if index == 0 else "resume-header-contact"
        icon = "" if index == 0 else svg_icon(contact_icon(item), "resume-inline-icon")
        parts.append(f'{line_break}<span class="resume-header-item {kind}">{icon}{content}</span>')
    if not name and not parts:
        return ""
    return f'<header class="resume-header"><div class="resume-header-main">{name}<div class="resume-header-items">{"".join(parts)}</div></div></header>'


def markdown_renderer() -> MarkdownIt:
    md = MarkdownIt("js-default", {"html": True, "linkify": True, "typographer": False}).use(deflist_plugin)

    def heading_open(self, tokens, idx, options, env):
        html = self.renderToken(tokens, idx, options, env)
        nxt = tokens[idx + 1] if idx + 1 < len(tokens) else None
        if tokens[idx].tag == "h2" and nxt is not None and nxt.type == "inline":
            html += svg_icon(section_icon(nxt.content), "resume-section-icon")
        return html

    md.add_render_rule("heading_open", heading_open)
    return md


def wrap_sections(html: str) -> str:
    out = []
    for part in re.split(r"(?=<h2\b)", html, flags=re.I):
        out.append(f'<section class="resume-section">{part}</section>' if re.match(r"<h2\b", part, flags=re.I) else part)
    return "".join(out)


def render_cv_html(markdown: str) -> str:
    data, body = split_front_matter(markdown)
    body = re.sub(
        r"^[ \t]*\\newpage[ \t]*$",
        '<div class="resume-manual-page-break" data-page-break="true"></div>',
        body.lstrip(),
        flags=re.M,
    )
    return render_header(data) + wrap_sections(markdown_renderer().render(body))


def template_css() -> str:
    css = (TEMPLATE_DIR / "resume.css").read_text(encoding="utf-8")

    def inline_font(m: re.Match) -> str:
        data = base64.b64encode((TEMPLATE_DIR / m.group(1)).read_bytes()).decode("ascii")
        return f'url("data:font/woff2;base64,{data}")'

    css = re.sub(r'url\("(fonts/[^"]+\.woff2)"\)', inline_font, css)
    return css.replace("var(--paper-width)", f"{STYLE['paper_width_mm']}mm").replace(
        "var(--paper-height)", f"{STYLE['paper_height_mm']}mm"
    )


def document_html(cv_html: str) -> str:
    s = STYLE
    page_style = (
        f"--resume-font-family: {s['font_family']}; --resume-font-size: {s['font_size']}px; "
        f"--resume-line-height: {s['line_height']}; --resume-paragraph-spacing: {s['paragraph_spacing']}px; "
        f"--resume-theme-color: {s['theme_color']}; --resume-text-align: {s['text_align']}; "
        f"width: {s['paper_width_mm']}mm; min-height: {s['paper_height_mm']}mm; "
        f"padding: {s['margin_top']}px {s['margin_right']}px {s['margin_bottom']}px {s['margin_left']}px;"
    )
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8" />\n'
        f"<style>\n{template_css()}\n</style>\n</head>\n<body>\n"
        f'<div class="resume-measure-root resume-page" style="{page_style}">{cv_html}</div>\n'
        '<div class="resume-print-root"></div>\n</body>\n</html>\n'
    )


def mm_to_px(mm: float) -> float:
    return mm / 25.4 * 96


def export_pdf(markdown: str, pdf_path: Path, preview_dir: Path | None) -> dict:
    s = STYLE
    max_content_height = mm_to_px(s["paper_height_mm"]) - s["margin_top"] - s["margin_bottom"]
    html = document_html(render_cv_html(markdown))
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except PlaywrightError as error:
            raise RuntimeError(f"cannot start Chromium ({error}). Run once: scripts/setup-pdf.sh") from error
        try:
            page = browser.new_page(
                viewport={
                    "width": int(mm_to_px(s["paper_width_mm"])) + 48,
                    "height": int(mm_to_px(s["paper_height_mm"])) + 48,
                }
            )
            page.set_content(html, wait_until="load")
            # Measure only after the embedded font is ready, or line breaks move.
            page.evaluate(
                "() => Promise.all(['400 12px Inter', '700 12px Inter', '800 12px Inter', 'italic 400 12px Inter']"
                ".map((f) => document.fonts.load(f))).then(() => document.fonts.ready)"
            )
            page.add_script_tag(path=str(TEMPLATE_DIR / "paginate.js"))
            result = page.evaluate("(o) => window.CvPagination.render(o)", {"maxContentHeight": max_content_height})
            page.pdf(path=str(pdf_path), print_background=True, prefer_css_page_size=True)
            previews = []
            if preview_dir is not None:
                preview_dir.mkdir(parents=True, exist_ok=True)
                for old in preview_dir.glob("page-*.png"):
                    old.unlink()
                pages = page.locator(".resume-print-root .resume-page")
                for i in range(result["pageCount"]):
                    target = preview_dir / f"page-{i + 1:02d}.png"
                    pages.nth(i).screenshot(path=str(target))
                    previews.append(target)
        finally:
            browser.close()
    return {"pages": result["pageCount"], "overflow": result["overflowPages"], "previews": previews}


def ascii_words(text: str) -> str:
    """'Senior DevSecOps Engineer' -> 'SeniorDevSecOpsEngineer'; drops accents."""
    text = text.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return "".join(w[:1].upper() + w[1:] for w in re.split(r"[^A-Za-z0-9]+", text) if w)


def default_name(data_root: Path | None, meta: dict) -> str:
    pattern = "CV_<Company>_<Role>"
    if data_root is not None:
        profile = data_root / "profile" / "career-profile.md"
        if profile.exists():
            found = parse_front_matter(profile.read_text(encoding="utf-8")).get("cv_file_pattern")
            if isinstance(found, str) and "<" not in found.split("_")[0]:
                pattern = found
    name = pattern.replace("<Company>", ascii_words(str(meta.get("company") or "Company")))
    return name.replace("<Role>", ascii_words(str(meta.get("role") or "Role")))


def set_cv_pdf(meta_path: Path, value: str) -> None:
    text = meta_path.read_text(encoding="utf-8")
    line = f'cv_pdf: "{value}"'
    if re.search(r"^cv_pdf:", text, flags=re.M):
        text = re.sub(r"^cv_pdf:[^\r\n]*", line, text, count=1, flags=re.M)
    elif re.search(r"^cv_markdown:", text, flags=re.M):
        text = re.sub(r"^(cv_markdown:[^\r\n]*)", lambda m: f"{m.group(1)}\n{line}", text, count=1, flags=re.M)
    else:
        text = text + ("" if text.endswith("\n") else "\n") + line + "\n"
    meta_path.write_text(text, encoding="utf-8", newline="")


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print("Usage: python3 scripts/export_cv.py <job folder | cv.md> [--name FILE_NAME] [--no-preview]", file=sys.stderr)
        return 1
    name = argv[argv.index("--name") + 1] if "--name" in argv and argv.index("--name") + 1 < len(argv) else None
    if name in args:
        args.remove(name)
    target = Path(args[0]).resolve()
    cv_path = target / "artifacts" / "cv.md" if target.is_dir() else target
    if not cv_path.exists():
        print(f"export_cv: {cv_path} not found", file=sys.stderr)
        return 1

    job_dir = cv_path.parent.parent if cv_path.parent.name == "artifacts" else None
    meta_path = job_dir / "metadata.yml" if job_dir else None
    if meta_path and meta_path.exists():
        meta = parse_flat_yaml(meta_path.read_text(encoding="utf-8"))
        try:
            data_root = resolve_data_root()
        except RuntimeError:
            data_root = None
        if data_root and not cv_path.is_relative_to(data_root):
            data_root = job_dir.parents[2] if len(job_dir.parents) > 2 else None
        file_name = name or default_name(data_root, meta)
        preview_dir = cv_path.parent / "cv-preview"
    else:
        meta_path, data_root = None, None
        file_name = name or cv_path.stem
        preview_dir = cv_path.parent / f"{cv_path.stem}-preview"
    if "--no-preview" in argv:
        preview_dir = None
    pdf_path = cv_path.parent / f"{file_name.removesuffix('.pdf')}.pdf"

    result = export_pdf(cv_path.read_text(encoding="utf-8"), pdf_path, preview_dir)
    print(f"Wrote {pdf_path} ({result['pages']} page(s))")
    if result["previews"]:
        print(f"Previews: {result['previews'][0].parent}/page-NN.png")
    if result["overflow"]:
        pages = ", ".join(str(n) for n in result["overflow"])
        print(f"warning: content does not fit on page {pages}; shorten that part", file=sys.stderr)
    if meta_path and data_root:
        set_cv_pdf(meta_path, pdf_path.relative_to(data_root).as_posix())
        print(f"metadata.yml: cv_pdf = {pdf_path.relative_to(data_root).as_posix()}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except (RuntimeError, OSError, yaml.YAMLError) as error:
        print(f"export_cv: {error}", file=sys.stderr)
        sys.exit(1)
