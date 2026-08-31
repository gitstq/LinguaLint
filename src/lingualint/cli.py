"""Command line interface."""
from __future__ import annotations

import argparse
import fnmatch
import os
import sys
from typing import List, Optional, Tuple

from . import __version__
from .config import Config
from .engine import LintResult, Linter
from .issues import SEVERITY_ORDER
from .reporter import RENDERERS, aggregate
from .rules import RULE_MAP


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="lingualint",
        description="LinguaLint — offline, zero-dependency bilingual (EN/ZH) "
                    "writing linter. Lints files, directories or stdin.")
    p.add_argument("paths", nargs="*", help="files or directories to lint (default: stdin)")
    p.add_argument("-f", "--format", choices=list(RENDERERS), default="text",
                   help="report format (default: text)")
    p.add_argument("-o", "--output", help="write report to a file instead of stdout")
    p.add_argument("--lang", choices=["auto", "en", "zh"], default=None,
                   help="force document language (default: auto detect)")
    p.add_argument("--config", help="path to .lingualint.json")
    p.add_argument("--fix", action="store_true",
                   help="apply safe auto-fixes (files are rewritten in place)")
    p.add_argument("--ext", default=None,
                   help="comma-separated extensions when scanning directories")
    p.add_argument("--exclude", action="append", default=[],
                   help="fnmatch pattern to exclude (repeatable)")
    p.add_argument("--min-score", type=int, default=None,
                   help="exit non-zero when the lint score drops below N")
    p.add_argument("--max-issues", type=int, default=None,
                   help="tolerated number of blocking issues (default 0)")
    p.add_argument("--fail-severity", choices=list(SEVERITY_ORDER), default=None,
                   help="issues at least this severe count toward the gate "
                        "(default: warning)")
    p.add_argument("--no-color", action="store_true", help="disable ANSI colors")
    p.add_argument("--list-rules", action="store_true", help="list all built-in rules and exit")
    p.add_argument("--version", action="version", version=f"lingualint {__version__}")
    return p


def list_rules() -> str:
    rows = []
    for rule_id, cls in sorted(RULE_MAP.items()):
        rows.append(f"{rule_id:<8} {cls.severity.upper():<10} "
                    f"{','.join(cls.languages):<7} {cls.title}")
    return "\n".join(rows)


def collect_files(paths: List[str], config: Config, cli_exclude: List[str]) -> List[str]:
    excludes = list(config.exclude) + cli_exclude
    exts = {e if e.startswith(".") else f".{e}" for e in config.extensions}
    found: List[str] = []
    for raw in paths:
        if os.path.isfile(raw):
            found.append(raw)
        elif os.path.isdir(raw):
            for root, dirs, files in os.walk(raw):
                dirs[:] = sorted(d for d in dirs if not _excluded(d, excludes) and not d.startswith("."))
                for name in sorted(files):
                    rel = os.path.relpath(os.path.join(root, name), raw)
                    if os.path.splitext(name)[1].lower() not in exts:
                        continue
                    if _excluded(rel, excludes) or _excluded(os.path.join(root, name), excludes):
                        continue
                    found.append(os.path.join(root, name))
        else:
            raise FileNotFoundError(f"path not found: {raw}")
    # De-duplicate while preserving order.
    seen, uniq = set(), []
    for f in found:
        ap = os.path.abspath(f)
        if ap not in seen:
            seen.add(ap)
            uniq.append(f)
    return uniq


def _excluded(name: str, patterns: List[str]) -> bool:
    return any(fnmatch.fnmatch(os.path.basename(name), p) or fnmatch.fnmatch(name, p)
               for p in patterns)


def _force_utf8_stdio() -> None:
    """Make stdout/stderr UTF-8 safe (Windows defaults to a locale charmap).

    Emoji and CJK characters must not crash when output is redirected.
    Streams without ``reconfigure`` (e.g. in-memory test streams) are skipped.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            pass


def run(argv: Optional[List[str]] = None) -> int:
    _force_utf8_stdio()
    args = build_parser().parse_args(argv)
    if args.list_rules:
        print(list_rules())
        return 0

    # Config loading: explicit --config > discovered .lingualint.json > defaults.
    try:
        if args.config:
            config = Config.from_file(args.config)
        else:
            discovered = Config.discover(".")
            config = Config.from_file(discovered) if discovered else Config()
        if args.lang:
            config.language = args.lang
        if args.ext:
            config.extensions = [e.strip() for e in args.ext.split(",") if e.strip()]
        if args.min_score is not None:
            config.min_score = args.min_score
        if args.max_issues is not None:
            config.max_issues = args.max_issues
        if args.fail_severity is not None:
            config.fail_severity = args.fail_severity
    except (ValueError, OSError) as exc:
        print(f"lingualint: config error: {exc}", file=sys.stderr)
        return 2

    linter = Linter(config)

    # --- stdin mode -------------------------------------------------------
    if not args.paths:
        if sys.stdin.isatty():
            print("lingualint: no input files and stdin is a terminal", file=sys.stderr)
            return 2
        text = sys.stdin.read()
        if args.fix:
            fixed, n, _ = linter.fix_text(text)
            sys.stdout.write(fixed)
            print(f"lingualint: applied {n} auto-fix(es)", file=sys.stderr)
            return 0
        result = linter.lint_text(text, path="<stdin>")
        items = [("<stdin>", result)]
        return _emit(args, config, items, linter)

    # --- file / directory mode -------------------------------------------
    try:
        files = collect_files(args.paths, config, args.exclude)
    except FileNotFoundError as exc:
        print(f"lingualint: {exc}", file=sys.stderr)
        return 2
    if not files:
        print("lingualint: no files matched", file=sys.stderr)
        return 2

    items: List[Tuple[str, LintResult]] = []
    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                text = fh.read()
        except UnicodeDecodeError:
            print(f"lingualint: skip binary/unreadable file: {path}", file=sys.stderr)
            continue
        if args.fix:
            fixed, n, remaining = linter.fix_text(text)
            if n:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(fixed)
                print(f"lingualint: {path}: applied {n} fix(es)", file=sys.stderr)
            items.append((path, remaining))
        else:
            items.append((path, linter.lint_text(text, path=path)))

    return _emit(args, config, items, linter)


def _emit(args, config: Config, items, linter: Linter) -> int:
    use_color = (args.format == "text" and sys.stdout.isatty() and not args.no_color)
    renderer = RENDERERS[args.format]
    if args.format == "text":
        report = renderer(items, use_color=use_color)
    else:
        report = renderer(items)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
            if not report.endswith("\n"):
                fh.write("\n")
    else:
        sys.stdout.write(report)
        if not report.endswith("\n"):
            sys.stdout.write("\n")

    # --- CI gate ----------------------------------------------------------
    threshold = SEVERITY_ORDER[config.fail_severity]
    blocking = sum(1 for _, r in items for i in r.issues
                   if SEVERITY_ORDER[i.severity] <= threshold)
    worst_score = min((r.score for _, r in items), default=100)
    failed = blocking > config.max_issues
    if config.min_score is not None and worst_score < config.min_score:
        failed = True
    if args.format == "text":
        if failed:
            print(f"lingualint: gate FAILED ({blocking} blocking issue(s), "
                  f"worst score {worst_score})", file=sys.stderr)
        else:
            print(f"lingualint: gate passed (worst score {worst_score})", file=sys.stderr)
    return 1 if failed else 0


def main() -> None:  # console-script entry point
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
