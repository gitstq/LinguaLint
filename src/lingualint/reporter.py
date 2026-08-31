"""Output reporters: text / json / markdown / self-contained html."""
from __future__ import annotations

import html
import json
from typing import Dict, List, Tuple

from .engine import LintResult

ANSI = {
    "reset": "\033[0m", "bold": "\033[1m", "dim": "\033[2m",
    "error": "\033[31m", "warning": "\033[33m",
    "suggestion": "\033[36m", "info": "\033[90m",
    "green": "\033[32m", "magenta": "\033[35m",
}
SEV_LABEL = {"error": "ERROR", "warning": "WARN ", "suggestion": "HINT ",
             "info": "INFO "}


def aggregate(items: List[Tuple[str, LintResult]]) -> Dict[str, int]:
    total = {"files": len(items), "error": 0, "warning": 0,
             "suggestion": 0, "info": 0}
    for _, r in items:
        for k, v in r.counts().items():
            total[k] += v
    total["issues"] = sum(total[k] for k in ("error", "warning", "suggestion", "info"))
    return total


# --- text -----------------------------------------------------------------

def render_text(items: List[Tuple[str, LintResult]], use_color: bool = True) -> str:
    c = ANSI if use_color else {k: "" for k in ANSI}
    lines: List[str] = []
    for path, result in items:
        lines.append(f"{c['bold']}📄 {path}{c['reset']}  "
                     f"{c['dim']}[lang={result.language}, score={result.score}]{c['reset']}")
        if not result.issues:
            lines.append(f"  {c['green']}✓ no issues found{c['reset']}")
            continue
        for i in result.issues:
            color = c[i.severity]
            head = f"  {i.line}:{i.col:<4}{color}{SEV_LABEL[i.severity]}{c['reset']} {c['magenta']}{i.rule_id}{c['reset']}"
            msg = f"{i.message}"
            lines.append(f"{head}  {msg}")
            if i.suggestion is not None and i.suggestion != "":
                shown = i.suggestion.replace("\n", "\\n")
                lines.append(f"        {c['dim']}→ {shown!r}{c['reset']}")
            elif i.suggestion == "":
                lines.append(f"        {c['dim']}→ remove{c['reset']}")
        counts = result.counts()
        lines.append("  " + c["dim"] + "summary: " +
                     ", ".join(f"{k}={v}" for k, v in counts.items() if v) +
                     c["reset"])
        lines.append("")
    total = aggregate(items)
    lines.append(
        f"{c['bold']}Totals{c['reset']}: {total['files']} file(s), "
        f"{total['error']} error(s), {total['warning']} warning(s), "
        f"{total['suggestion']} suggestion(s), {total['info']} info")
    return "\n".join(lines)


# --- json -----------------------------------------------------------------

def render_json(items: List[Tuple[str, LintResult]]) -> str:
    payload = {
        "summary": aggregate(items),
        "results": [r.to_dict() for _, r in items],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


# --- markdown -------------------------------------------------------------

def render_markdown(items: List[Tuple[str, LintResult]]) -> str:
    out = ["# LinguaLint Report", ""]
    total = aggregate(items)
    out.append(f"> Files: **{total['files']}** · Errors: **{total['error']}** · "
               f"Warnings: **{total['warning']}** · Suggestions: **{total['suggestion']}** · "
               f"Info: **{total['info']}**")
    out.append("")
    for path, result in items:
        out.append(f"## `{path}`")
        out.append("")
        out.append(f"Language: `{result.language}` · Score: **{result.score}/100**")
        out.append("")
        if not result.issues:
            out.append("✓ No issues found.")
            out.append("")
            continue
        out.append("| Line | Severity | Rule | Message | Suggestion |")
        out.append("| ---: | --- | --- | --- | --- |")
        for i in result.issues:
            sug = "" if i.suggestion is None else f"`{i.suggestion}`"
            msg = i.message.replace("|", "\\|")
            out.append(f"| {i.line}:{i.col} | {i.severity} | `{i.rule_id}` | {msg} | {sug} |")
        out.append("")
    return "\n".join(out)


# --- html -----------------------------------------------------------------

_HTML_STYLE = """
:root{--bg:#0f1115;--card:#181b22;--fg:#e6e8ec;--muted:#9aa4b2;--line:#2a2f3a;
--error:#ff6b6b;--warning:#ffb454;--suggestion:#4fc3f7;--info:#8b95a3;--ok:#51cf66}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);
font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'PingFang SC','Microsoft YaHei',sans-serif;line-height:1.55;padding:32px}
h1{margin:0 0 8px}.muted{color:var(--muted)}
.cards{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}.card{background:var(--card);
border:1px solid var(--line);border-radius:12px;padding:14px 18px;min-width:120px}
.card .n{font-size:26px;font-weight:700}.card .k{color:var(--muted);font-size:12px}
.file{background:var(--card);border:1px solid var(--line);border-radius:12px;margin:16px 0;overflow:hidden}
.file h2{margin:0;padding:14px 18px;font-size:15px;border-bottom:1px solid var(--line);
display:flex;justify-content:space-between;align-items:center}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:8px 12px;
border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--muted);font-weight:600}
.sev{font-weight:700;font-size:11px;padding:2px 8px;border-radius:999px}
.error{color:var(--error)}.warning{color:var(--warning)}.suggestion{color:var(--suggestion)}.info{color:var(--info)}
code{background:#0b0d11;padding:1px 6px;border-radius:6px;font-size:12px}
.ok{color:var(--ok);padding:14px 18px}
"""


def render_html(items: List[Tuple[str, LintResult]]) -> str:
    total = aggregate(items)
    cards = [("Files", total["files"]), ("Errors", total["error"]),
             ("Warnings", total["warning"]), ("Suggestions", total["suggestion"]),
             ("Info", total["info"])]
    card_html = "".join(
        f'<div class="card"><div class="n">{v}</div><div class="k">{html.escape(k)}</div></div>'
        for k, v in cards)
    files_html = []
    for path, result in items:
        if result.issues:
            rows = []
            for i in result.issues:
                sug = "—" if i.suggestion is None else f"<code>{html.escape(i.suggestion)}</code>"
                rows.append(
                    "<tr>"
                    f"<td>{i.line}:{i.col}</td>"
                    f"<td class='sev {i.severity}'>{i.severity.upper()}</td>"
                    f"<td><code>{html.escape(i.rule_id)}</code></td>"
                    f"<td>{html.escape(i.message)}</td>"
                    f"<td>{sug}</td></tr>")
            body = ("<table><thead><tr><th>Pos</th><th>Severity</th><th>Rule</th>"
                    "<th>Message</th><th>Suggestion</th></tr></thead><tbody>"
                    + "".join(rows) + "</tbody></table>")
        else:
            body = "<div class='ok'>✓ No issues found.</div>"
        files_html.append(
            "<section class='file'>"
            f"<h2><span>{html.escape(path)}</span>"
            f"<span class='muted'>lang={html.escape(result.language)} · "
            f"score {result.score}/100</span></h2>{body}</section>")
    return (
        "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>LinguaLint Report</title>"
        f"<style>{_HTML_STYLE}</style></head><body>"
        "<h1>LinguaLint Report</h1>"
        "<div class='muted'>Offline bilingual writing linter — self-contained report</div>"
        f"<div class='cards'>{card_html}</div>"
        + "".join(files_html) +
        "</body></html>")


RENDERERS = {
    "text": render_text,
    "json": render_json,
    "markdown": render_markdown,
    "html": render_html,
}
