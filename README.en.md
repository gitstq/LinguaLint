# LinguaLint 🔎✍️

[简体中文](README.md) · [繁體中文](README.zh-TW.md) · **English**

<p align="center">
  <b>Zero-dependency · Fully offline · Bilingual (EN/ZH) writing linter</b><br/>
  A text-linting engine (library + CLI) written purely with the Python standard
  library. It brings <b>grammar checks, typography rules, readability scoring,
  safe auto-fix and CI gating</b> to Markdown, docs, copy and commit messages.
</p>

<p align="center">
  <img alt="python" src="https://img.shields.io/badge/python-3.8%2B-blue">
  <img alt="dependencies" src="https://img.shields.io/badge/runtime%20dependencies-0-success">
  <img alt="tests" src="https://img.shields.io/badge/tests-64%20passed-success">
  <img alt="rules" src="https://img.shields.io/badge/rules-22-orange">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-green">
  <a href="https://github.com/gitstq/LinguaLint/releases/latest"><img alt="release" src="https://img.shields.io/badge/release-v1.0.0-blueviolet"></a>
</p>

---

## 🎉 Introduction

**LinguaLint** is a local-first, fully offline bilingual writing linter. It
treats natural language the way ESLint treats code: the document is sliced into
addressable character spans, **22 deterministic rules** detect spelling,
grammar, CJK/Latin typography and style issues, and every finding comes with a
**line/column location, an explanation and a safe fix suggestion**. Reports are
available as terminal text, JSON, Markdown or a single self-contained HTML
file.

### Pain points it solves 😣
- **You cannot paste internal documents into SaaS grammar tools** — cloud
  checkers leak sensitive text; LinguaLint never opens a network connection.
- **Chinese typography is checked by hand** — CJK/Latin spacing, half-width
  punctuation inside Chinese sentences, idiom typos and redundant phrases have
  had no automation-friendly tooling.
- **Writing quality never reaches CI** — typos and run-on sentences are found
  late in review because there is no machine-enforceable gate.
- **NLP stacks are heavy** — model downloads, native builds and fragile
  installs do not belong in minimal CI images.

### Differentiators 🌟
1. **Genuinely zero runtime dependencies** — Python standard library only; a
   `py3-none-any` wheel that runs anywhere Python runs.
2. **One engine, two languages** — automatic language detection; mixed
   documents run both rule families at once without interfering.
3. **Precision-first deterministic rules** — every rule ships with allow-lists
   and protected ranges (inline code, fenced blocks and URLs are never edited).
4. **Convergent safe auto-fix (`--fix`)** — overlapping fixes are ordered
   automatically and converge within rounds; repeated runs are idempotent.
5. **Engineering-ready** — a 100-point quality score and three CI gates
   (`--min-score`, `--max-issues`, `--fail-severity`) with documented exit codes.
6. **Extensible** — `.lingualint.json` toggles rules, overrides severities and
   adds project typo pairs / ignore words.

> **Inspiration**: [Automattic/harper](https://github.com/Automattic/harper), a
> trending Rust project and excellent **English-only**, offline grammar
> checker. Not a single line of its code is reused — only the local-first,
> privacy-first product philosophy. LinguaLint independently adds **Chinese
> language support, a dependency-free Python runtime, CI gates, auto-fix and
> multi-format reports**.

---

## ✨ Features

### 🧱 22 built-in rules in five categories
| Category | Rules | Coverage |
| --- | ---: | --- |
| 📐 Common (COM) | 8 | trailing whitespace, blank-line runs, double spaces, space before punctuation, zero-width/BOM chars, repeated punctuation, quote pairing, long lines |
| 🇬🇧 English (ENG) | 8 | repeated words, a/an agreement, sentence capitalization, comma spacing, confusables (its/it's, than/then…), high-frequency misspellings, passive voice, filler words |
| 🇨🇳 Chinese (ZH) | 6 | half-width punctuation in Chinese context, CJK–Latin spacing, doubled particles, 30+ idiom typos, semantic redundancy, long Chinese sentences |

### 🧠 Protected ranges
Inline code, fenced code blocks and `http(s)://` URLs are skipped automatically
so code and links are never "corrected" as prose.

### 📊 Readability & scoring
- English: **Flesch Reading Ease** and **Flesch–Kincaid Grade**;
- Chinese: average sentence length, long-sentence ratio and a four-band
  fluency label;
- **LinguaLint Score (0–100)**: error −10, warning −4, suggestion −1, info 0,
  floored at 0.

### 🔧 Four reports & auto-fix
- Colored terminal output (TTY auto-detection, `--no-color` to disable);
- JSON for machine consumption and editor integration;
- Markdown tables to paste into PRs;
- **Self-contained HTML** — one file, zero external assets, dark theme;
- `--fix` rewrites files in place; fixes converge and are idempotent.

### 🧩 Library + CLI
Batch-lint from the shell or embed the Python API in a writing pipeline, static
site build or editor backend.

---

## 🚀 Quick Start

### Requirements 🧰
- **Python 3.8 – 3.13**, no third-party runtime dependencies
- Works on Windows, macOS and Linux

### Installation ⬇️
Latest release: <https://github.com/gitstq/LinguaLint/releases/latest>

```bash
# Option 1: install the universal wheel (registers the `lingualint` command)
pip install lingualint-1.0.0-py3-none-any.whl

# Option 2: editable install from source (development)
git clone https://github.com/gitstq/LinguaLint.git
cd LinguaLint
pip install -e .

# Option 3: run without installation
python -m lingualint README.md
```

### 30-second tour ⚡
```bash
# Lint a single file
lingualint examples/sample_en.md

# Recursively lint a directory and emit an HTML report
lingualint docs/ -f html -o report.html

# Apply every safe fix in place
lingualint docs/ --fix

# Pipe text through stdin
echo "Its definately wrong ," | lingualint --lang en
```

Real terminal output:

```text
📄 examples/sample_en.md  [lang=en, score=81]
  3:27  WARN  COM004  Space before punctuation mark.
        → ','
  3:36  ERROR ENG006  “definately” looks misspelled; did you mean “definitely”?
        → 'definitely'
  3:62  WARN  ENG005  Possessive “its” followed by a verb/particle; did you mean “it’s”?
        → "It's going"
  4:6   HINT  ENG008  “very” is a weak intensifier; use a precise word instead.

Totals: 1 file(s), 1 error(s), 2 warning(s), 1 suggestion(s), 0 info
lingualint: gate FAILED (3 blocking issue(s), worst score 81)
```

A live HTML report sample: [docs/sample-report.html](docs/sample-report.html).

---

## 📖 Usage Guide

### CLI reference 🧾
| Flag | Description |
| --- | --- |
| `paths` | files or directories to lint (directories are walked recursively); defaults to stdin |
| `-f, --format` | `text` (default) / `json` / `markdown` / `html` |
| `-o, --output` | write the report to a file instead of stdout |
| `--lang` | force language: `auto` (default) / `en` / `zh` |
| `--config` | path to a config file (auto-discovers `.lingualint.json` by default) |
| `--fix` | apply safe auto-fixes in place |
| `--ext` | comma-separated extensions for directory scans (default `.md,.markdown,.txt,.rst,.text`) |
| `--exclude` | fnmatch exclusion pattern (repeatable) |
| `--min-score N` | fail the gate when the score drops below N |
| `--max-issues N` | tolerated number of blocking issues (default 0) |
| `--fail-severity` | severities counted by the gate: `error/warning/suggestion/info` (default warning) |
| `--no-color` | disable ANSI colors |
| `--list-rules` | list every rule and exit |
| `--version` | print the version |

### Exit codes 🚦
| Code | Meaning |
| ---: | --- |
| `0` | clean, gate passed |
| `1` | blocking issues found or score below threshold (CI red) |
| `2` | usage error / missing path / invalid config |

### Rule catalog 📚
| ID | Default | Auto-fix | Description |
| --- | --- | :---: | --- |
| COM001 | warning | ✅ | trailing whitespace |
| COM002 | suggestion | ✅ | consecutive blank lines |
| COM003 | warning | ✅ | multiple spaces between words |
| COM004 | warning | ✅ | space before punctuation |
| COM005 | error | ✅ | zero-width / BOM / bidi control characters |
| COM006 | suggestion | ✅ | repeated punctuation (`...` ellipsis allowed) |
| COM007 | warning | ❌ | unmatched quotation marks |
| COM008 | info | ❌ | line too long (200 chars by default) |
| ENG001 | error | ✅ | adjacent repeated word (grammatical that/had allowed) |
| ENG002 | warning | ✅ | a/an mismatch (hour/university pronunciation exceptions) |
| ENG003 | suggestion | ✅ | sentence starts lowercase (e.g./i.e. exceptions) |
| ENG004 | warning | ✅ | missing space after a comma |
| ENG005 | warning | ✅ | its/it's, than/then, lose/loose, affect/effect confusables |
| ENG006 | error | ✅ | 18 high-frequency misspellings + custom typo pairs |
| ENG007 | suggestion | ❌ | possible passive voice (adjectival -ed allow-listed) |
| ENG008 | suggestion | ❌ | weak/filler words: very, really, just… |
| ZH001 | warning | ✅ | half-width punctuation in Chinese context (numbers exempt) |
| ZH002 | suggestion | ✅ | missing space between CJK and Latin/digits |
| ZH003 | error | ✅ | doubled function particles (legit reduplication exempt) |
| ZH004 | error | ✅ | 30+ common Chinese idiom misspellings |
| ZH005 | suggestion | partial | semantic redundancy (e.g. “大约…左右”) |
| ZH006 | info | ❌ | over-long Chinese sentence (60 hanzi by default) |

### Configuration `.lingualint.json` ⚙️
Place it at the project root for auto-discovery, or pass `--config`:

```json
{
  "language": "auto",
  "zh_latin_spacing": true,
  "max_line_length": 200,
  "long_zh_sentence": 60,
  "rules": {
    "ENG008": false,
    "COM008": "suggestion"
  },
  "ignore_words": ["LinguaLint"],
  "typo_pairs": {
    "foobar": "foo bar"
  },
  "exclude": ["drafts", "*.draft.md"]
}
```

- `rules`: `false` disables a rule; a severity string overrides the default;
- `typo_pairs`: project-specific replacements (Latin words match on word
  boundaries, Chinese on substrings);
- `ignore_words`: spelling allow-list for brand names and internal jargon.

### Python API 🐍
```python
from lingualint import Linter, Config

config = Config.from_dict({"rules": {"ENG007": False}})
linter = Linter(config)

result = linter.lint_text("This is is a definately draft", language="en")
print(result.score, result.language)
for issue in result.issues:
    print(issue.line, issue.col, issue.rule_id, issue.message, issue.suggestion)

fixed, n, remaining = linter.fix_text("definately the the text")
print(fixed, n, remaining.score)
```

### Common workflows 🧪
1. **Pre-build docs gate** for a static blog: run `lingualint content/` before the build;
2. **Pull-request gate** via GitHub Actions (snippet below);
3. **Clean legacy docs in bulk** with `--fix`, then review the Git diff;
4. **Editor / pipeline backend** consuming `-f json`;
5. **Archival report** with `-f html -o report.html`, a single emailable file.

### GitHub Actions 🔁
```yaml
name: docs-lint
on: [push, pull_request]
jobs:
  lingualint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install lingualint
      - run: lingualint docs/ --min-score 80 -f markdown -o lint-report.md
```

---

## 💡 Design & Roadmap

### Why “stdlib + deterministic rules” instead of an LLM 🧠
- **Reproducible** — the same input always yields the same output; reviews and
  regression tests can rely on it.
- **Offline by default** — no model downloads, no API keys, no network calls.
- **Tiny footprint** — the wheel is under 30 KB with millisecond cold starts.
- **Precision over recall** — rules stay silent unless confidence is high,
  backed by allow-lists and protected ranges.

### Architecture 🏗️
```
text (str)
  └─ Document        line offsets + protected ranges (code/URLs)
       └─ Rule sets  COM (common) / ENG (English) / ZH (Chinese)
            └─ Issue char spans + severity + fix suggestion
                 └─ Linter     scheduling, scoring, multi-round fix
                      └─ reporter text / json / markdown / html
```

### Roadmap 🗺️
- **v1.1 (planned)**: more Chinese sentence-pattern heuristics, a pre-commit
  hook, SARIF output, Markdown front-matter/table exemptions;
- **v1.2 (planned)**: external rule packs, user-defined regex rules, CSV
  dictionary import;
- **v2.0 (future)**: Japanese/Korean rule families, LanguageTool dictionary
  compatibility, an optional lightweight statistical model as *suggestion-only*
  input (off by default — the zero-dependency promise stays).

### Contribution areas 🙋
New high-confidence rules (with false-positive tests), idiom dictionaries,
documentation translations and report themes are all welcome.

---

## 📦 Packaging & Deployment

LinguaLint is a **library / CLI project**: pure Python, cross-platform, with no
per-OS binaries required.

```bash
pip install build
python -m build
# dist/lingualint-1.0.0.tar.gz              # source distribution
# dist/lingualint-1.0.0-py3-none-any.whl   # universal wheel
```

- **Compatibility**: Python 3.8+ on Windows, macOS and Linux;
- **Tests**: `python -m unittest discover -s tests` (64 tests, all green);
- **Air-gapped install**: copy the wheel to the internal network and run
  `pip install <wheel>` — no internet access required;
- **Uninstall**: `pip uninstall LinguaLint`.

The v1.0.0 distributions and SHA-256 checksums are on the
[Releases page](https://github.com/gitstq/LinguaLint/releases/latest).

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide. Essentials:

1. 🌿 Branch from `main` (`feat/…`, `fix/…`);
2. ✅ A new rule needs both positive and false-positive-exemption tests;
3. 📝 Follow the **Angular commit convention**:
   `feat:` / `fix:` / `docs:` / `refactor:` / `test:`;
4. 🧪 Keep `python -m unittest discover -s tests` green;
5. 💬 Bug reports need a minimal reproducing text, Python version and output.

---

## 📄 License

Released under the **[MIT License](LICENSE)** for personal and commercial use.

Hat tip to [Automattic/harper](https://github.com/Automattic/harper) for product
inspiration; all code here is independently written.
