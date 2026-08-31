# Changelog

All notable changes to LinguaLint are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-08-31

### Added
- Offline bilingual (English / Simplified Chinese) writing lint engine,
  fully implemented on the Python standard library (zero runtime
  dependencies), Python 3.8+ compatible.
- 22 built-in rules across five categories:
  - Common typography (whitespace, invisible characters, repeated
    punctuation, quote pairing, line length).
  - English grammar/style (repeated words, a/an agreement, sentence
    capitalization, confusable words, high-confidence misspellings,
    passive-voice and filler-word hints).
  - Chinese typography/style (half-width punctuation in Chinese context,
    CJK–Latin spacing, doubled particles, idiom misspellings, redundant
    expressions, long-sentence detection).
- Readability metrics: Flesch Reading Ease / Flesch–Kincaid grade for
  English; average sentence length and long-sentence ratio for Chinese.
- Deterministic 100-point LinguaLint score.
- Safe auto-fix (`--fix`) with multi-round convergence.
- Four report formats: ANSI text, JSON, Markdown, self-contained HTML.
- CI gate flags: `--fail-severity`, `--max-issues`, `--min-score` with
  documented exit codes (0 pass / 1 gate failed / 2 usage error).
- File, recursive directory, glob-exclusion and stdin workflows.
- `.lingualint.json` configuration: rule toggles/severity overrides,
  project typo pairs, ignore words, typography thresholds.
- Public library API (`Linter`, `Config`, `LintResult`).
- 64 unit tests covering every rule, the engine, autofix, reporters and
  the CLI.
