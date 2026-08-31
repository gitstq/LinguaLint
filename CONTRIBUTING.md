# Contributing to LinguaLint / 贡献指南

[English](#english) · [简体中文](#简体中文)

感谢你愿意为 LinguaLint 做贡献！本项目坚持**零运行时依赖、精度优先、测试先行**三条底线。

---

## 简体中文

### 1. 开发环境
```bash
git clone https://github.com/gitstq/LinguaLint.git
cd LinguaLint
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .[dev]
```

### 2. 新增一条规则
1. 在 `src/lingualint/rules/english.py` 或 `chinese.py`（通用排版放 `common.py`）中新增规则类，
   继承对应基类，填写唯一的 `ENG/ZH/COMxxx` 编号、严重级、类别与 `title/description`；
2. 只使用 **Python 标准库**，禁止引入第三方运行时依赖；
3. 在 `tests/` 中至少补两类测试：
   - **正向命中**：问题文本必须被检出；
   - **误报豁免**：合法写法（代码区间、URL、白名单词、数字语境）不得被误报；
4. 在三份 README 的「规则目录」表格中同步登记；
5. 运行全量测试：`python -m unittest discover -s tests`，必须全绿。

### 3. 提交规范（Angular Convention）
```
feat: 新功能（如 feat(rules): 新增中文虚词赘余规则 ZH007）
fix: 缺陷修复
docs: 文档
test: 测试
refactor: 重构（不改变外部行为）
chore: 构建/工程配置
ci: 持续集成
```
- 一个提交只做一件事，保持历史可读；
- 不提交构建产物（`dist/`、`build/`、`*.egg-info/` 已在 `.gitignore`）。

### 4. Pull Request
- 从 `main` 切出 `feat/xxx`、`fix/xxx` 分支；
- PR 描述写清：解决的问题、规则设计理由（为什么误报率低）、测试覆盖情况；
- 涉及行为变化时同步更新 CHANGELOG 与三份 README。

### 5. Issue 反馈
请附上：最小复现文本、Python 版本、操作系统、实际输出与期望输出。

---

## English

### 1. Development setup
```bash
git clone https://github.com/gitstq/LinguaLint.git
cd LinguaLint
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .[dev]
```

### 2. Adding a rule
1. Add the rule class to `english.py`, `chinese.py` (or `common.py` for
   language-agnostic typography) with a unique `ENG/ZH/COMxxx` id, severity,
   category, `title` and `description`;
2. Use the **Python standard library only** — no third-party runtime deps;
3. Add at least two kinds of tests: a **positive hit** and a
   **false-positive exemption** (code spans, URLs, allow-listed words, numeric
   contexts);
4. Register the rule in the catalog tables of all three READMEs;
5. Run `python -m unittest discover -s tests` — everything must pass.

### 3. Commit convention (Angular)
`feat:` / `fix:` / `docs:` / `test:` / `refactor:` / `chore:` / `ci:`,
optionally scoped, e.g. `feat(rules): add ZH007 redundant collocation rule`.

### 4. Pull Requests
- Branch from `main` as `feat/…` or `fix/…`;
- Explain the problem, why false positives are unlikely, and test coverage;
- Update CHANGELOG and the three READMEs for behavior changes.

### 5. Issues
Include a minimal reproducing text, Python version, OS, actual and expected output.
