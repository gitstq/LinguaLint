# LinguaLint 🔎✍️

**简体中文** · [繁體中文](README.zh-TW.md) · [English](README.en.md)

<p align="center">
  <b>零依赖 · 完全离线 · 中英双语的写作校对引擎</b><br/>
  一个 Python 标准库写成的文本 Lint 工具（库 + CLI），为 Markdown / 文档 / 文案 / 提交说明提供
  <b>语法纠错、排版规范、可读性评分、自动修复与 CI 门禁</b>。
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

## 🎉 项目介绍

**LinguaLint** 是一个运行在本地、完全离线的双语写作校对工具。它像 ESLint 检查代码一样检查自然语言：
把文档切成可定位的字符区间，用 **22 条确定性规则**找出拼写、语法、中英文排版与文风问题，给出
**行号列号、问题解释与一键修复建议**，并输出终端 / JSON / Markdown / 自包含 HTML 四种报告。

### 它解决什么痛点 😣
- **在线写作工具不敢贴内部文档**：Grammarly 等 SaaS 工具需要上传文本，存在数据外泄风险；
- **中文排版长期靠人肉**：中英混排空格、全角半角标点、成语错别字、语义赘余没有趁手的自动化工具；
- **文档质量无法进入工程流程**：评审时才发现错别字与超长句，缺少可在 CI 中执行的质量门禁；
- **工具链依赖沉重**：NLP 模型体积大、安装慢、跨平台易翻车，难以跑在最小化 CI 镜像里。

### 自研差异化亮点 🌟
1. **真正零运行时依赖**：仅使用 Python 标准库，`py3-none-any` 纯 Python Wheel，任意平台开箱即用；
2. **中英双语一套引擎**：自动识别文档语言，混排文档同时跑两套规则族，互不干扰；
3. **精度优先的确定性规则**：每条规则都有白名单与保护区间（行内代码、代码块、URL 不会被误判），拒绝大模型式幻觉；
4. **多轮收敛的安全自动修复**（`--fix`）：重叠修复自动排序、最多 5 轮收敛，结果幂等；
5. **工程化闭环**：100 分制质量分、`--min-score / --max-issues / --fail-severity` 三级 CI 门禁、明确退出码；
6. **可扩展**：`.lingualint.json` 支持开关规则、覆盖严重级、项目自定义错词表与忽略词。

> **灵感来源**：GitHub Trending（Rust 榜）项目 [Automattic/harper](https://github.com/Automattic/harper)
> ——一个优秀的**离线英文**语法检查器。LinguaLint 没有复制其一行代码，仅参考「本地优先、隐私优先」
> 的产品理念，并在**中文语境支持、零依赖 Python 运行时、CI 门禁、自动修复与多格式报告**方向做了独立自研与差异化补齐。

---

## ✨ 核心特性

### 🧱 22 条内置规则，五大类别
| 类别 | 规则数 | 覆盖内容 |
| --- | ---: | --- |
| 📐 通用排版 COM | 8 | 行尾空白、连续空行、多余空格、标点前空格、零宽/BOM 不可见字符、重复标点、引号配对、超长行 |
| 🇬🇧 英文 ENG | 8 | 重复单词、a/an 一致、句首大写、逗号空格、易混词（its/it's、than/then…）、高频拼写错误、被动语态、弱化填充词 |
| 🇨🇳 中文 ZH | 6 | 中文语境半角标点、中英/中数空格、功能助词重复、成语错别字（30+）、语义赘余、中文长句 |

### 🧠 智能保护区间
行内代码 `` `code` ``、围栏代码块、`http(s)://` 链接、自动链接**自动跳过**，不会把代码与 URL 当自然语言误改。

### 📊 可读性与评分
- 英文：**Flesch Reading Ease** 与 **Flesch–Kincaid Grade**；
- 中文：平均句长、长句占比与四档流畅度评价；
- **LinguaLint Score（满分 100）**：error −10、warning −4、suggestion −1、info 0，下限 0。

### 🔧 四种报告 + 自动修复
- 终端彩色报告（自动识别 TTY，`--no-color` 可关）；
- JSON（机器可读，便于二次集成）；
- Markdown（直接贴 PR / Issue）；
- **自包含 HTML**（单文件、无外链、暗色主题，可直接发邮件或归档）；
- `--fix` 原地安全修复，可多轮收敛，重复执行结果不变。

### 🧩 库 + CLI 双形态
既可命令行批处理，也可作为 Python 库嵌入写作流水线、静态站点构建与编辑器后端。

---

## 🚀 快速开始

### 环境要求 🧰
- **Python 3.8 – 3.13**（无任何第三方运行时依赖）
- Windows / macOS / Linux 全平台通用

### 安装 ⬇️
最新 Release 下载：<https://github.com/gitstq/LinguaLint/releases/latest>

```bash
# 方式一：PyPI 风格本地安装（推荐，自动注册 lingualint 命令）
pip install lingualint-1.0.0-py3-none-any.whl

# 方式二：源码可编辑安装（参与开发）
git clone https://github.com/gitstq/LinguaLint.git
cd LinguaLint
pip install -e .

# 方式三：免安装直接运行
python -m lingualint README.md
```

### 30 秒体验 ⚡
```bash
# 检查单个文件
lingualint examples/sample_zh.md

# 递归检查整个文档目录，输出 HTML 报告
lingualint docs/ -f html -o report.html

# 自动修复所有可安全修复的问题
lingualint docs/ --fix

# 管道输入
echo "Its definately wrong ," | lingualint --lang en
```

真实终端效果：

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

在线预览 HTML 报告样例：[docs/sample-report.html](docs/sample-report.html)。

---

## 📖 详细使用指南

### 命令行参数全表 🧾
| 参数 | 说明 |
| --- | --- |
| `paths` | 待检查的文件或目录（目录递归扫描）；留空则读取标准输入 |
| `-f, --format` | `text`（默认）/ `json` / `markdown` / `html` |
| `-o, --output` | 报告写入文件而非标准输出 |
| `--lang` | `auto`（默认）/ `en` / `zh`，强制文档语言 |
| `--config` | 指定配置文件路径（默认自动向上查找 `.lingualint.json`） |
| `--fix` | 原地应用安全自动修复 |
| `--ext` | 目录扫描的扩展名，逗号分隔（默认 `.md,.markdown,.txt,.rst,.text`） |
| `--exclude` | fnmatch 排除模式，可重复传入 |
| `--min-score N` | 最低质量分，低于 N 则门禁失败 |
| `--max-issues N` | 允许的阻断级问题数量（默认 0） |
| `--fail-severity` | 计入门禁的最低严重级：`error/warning/suggestion/info`（默认 warning） |
| `--no-color` | 关闭 ANSI 颜色 |
| `--list-rules` | 列出全部规则后退出 |
| `--version` | 输出版本号 |

### 退出码 🚦
| 退出码 | 含义 |
| ---: | --- |
| `0` | 检查通过，门禁达标 |
| `1` | 发现阻断级问题或评分低于阈值（CI 红灯） |
| `2` | 用法错误 / 路径不存在 / 配置非法 |

### 规则目录 📚
| ID | 默认级别 | 可自动修复 | 说明 |
| --- | --- | :---: | --- |
| COM001 | warning | ✅ | 行尾空白 |
| COM002 | suggestion | ✅ | 连续多个空行 |
| COM003 | warning | ✅ | 词间连续多空格 |
| COM004 | warning | ✅ | 标点前多余空格 |
| COM005 | error | ✅ | 零宽字符 / BOM / 双向控制符 |
| COM006 | suggestion | ✅ | 重复标点（`...` 省略号豁免） |
| COM007 | warning | ❌ | 引号不配对 |
| COM008 | info | ❌ | 单行超长（默认 200） |
| ENG001 | error | ✅ | 相邻重复单词（that/had 合法叠词豁免） |
| ENG002 | warning | ✅ | a / an 误用（含 hour、university 等发音例外） |
| ENG003 | suggestion | ✅ | 句首未大写（e.g. 等缩写豁免） |
| ENG004 | warning | ✅ | 逗号后缺空格 |
| ENG005 | warning | ✅ | its/it's、than/then、lose/loose、affect/effect 等易混词 |
| ENG006 | error | ✅ | 18 个高频拼写错误 + 自定义错词表 |
| ENG007 | suggestion | ❌ | 疑似被动语态（形容词化 -ed 豁免） |
| ENG008 | suggestion | ❌ | very / really / just 等弱化填充词 |
| ZH001 | warning | ✅ | 中文语境误用半角标点（数字小数、时间豁免） |
| ZH002 | suggestion | ✅ | 中英文 / 中数之间缺空格 |
| ZH003 | error | ✅ | 的/了/是/在 等功能助词重复（合法叠词豁免） |
| ZH004 | error | ✅ | 30+ 高频成语 / 常用词错别字 |
| ZH005 | suggestion | 部分 | 语义赘余（涉及到、免费赠送、大约…左右） |
| ZH006 | info | ❌ | 中文单句超长（默认 60 汉字） |

### 配置文件 `.lingualint.json` ⚙️
在项目根目录放置配置文件即被自动识别，也可用 `--config` 指定：

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
    "foobar": "foo bar",
    "按装": "安装"
  },
  "exclude": ["drafts", "*.draft.md"]
}
```

- `rules`：`false` 关闭规则；或传 `error/warning/suggestion/info` 覆盖默认严重级；
- `typo_pairs`：项目级错词表，英文词按词边界匹配，中文按子串匹配；
- `ignore_words`：拼写白名单（品牌名、内部术语）。

### Python API 调用 🐍
```python
from lingualint import Linter, Config

config = Config.from_dict({"rules": {"ENG007": False}})
linter = Linter(config)

result = linter.lint_text("这是一个迫不急待的demo", language="zh")
print(result.score, result.language)
for issue in result.issues:
    print(issue.line, issue.col, issue.rule_id, issue.message, issue.suggestion)

fixed, n, remaining = linter.fix_text("definately the the text")
print(fixed, n, remaining.score)
```

### 典型场景 🧪
1. **静态博客构建前检查**：在 `build` 脚本前加 `lingualint content/`；
2. **PR 文档门禁**：配合下方 GitHub Actions，文档不达标直接红灯；
3. **批量清洗历史文档**：`lingualint docs/ --fix` 后用 Git diff 审阅；
4. **编辑器/流水线后端**：通过 `-f json` 消费结构化结果；
5. **对外发布前归档**：`-f html -o report.html` 生成可邮件分发的单文件报告。

### 接入 GitHub Actions 🔁
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

## 💡 设计思路与迭代规划

### 为什么是「标准库 + 正则规则」而不是大模型 🧠
- **可复现**：同样输入永远得到同样输出，评审与回归测试可依赖；
- **零成本离线**：无模型下载、无 API Key、无网络请求，符合隐私合规；
- **极小 footprint**：Wheel 不足 30 KB，冷启动毫秒级；
- **精度优先**：宁可不报也不误报——每条规则都配豁免白名单与保护区间。

### 架构分层 🏗️
```
text (str)
  └─ Document        行偏移表 + 保护区间（代码/URL）
       └─ Rule 族    COM（通用）/ ENG（英文）/ ZH（中文）
            └─ Issue 字符级起止 + 严重级 + 修复建议
                 └─ Linter      规则编排、语言调度、评分、多轮 fix
                      └─ reporter text / json / markdown / html
```

### 迭代路线图 🗺️
- **v1.1（规划中）**：扩充中文病句模式（搭配不当、主语残缺启发式）、pre-commit hook、SARIF 输出、Markdown frontmatter / 表格豁免；
- **v1.2（规划中）**：规则包外置与用户自定义正则规则、CSV 词典导入；
- **v2.0（远期）**：日文/韩文排版规则族、LanguageTool 词典兼容、可选的轻量统计语言模型作为「建议级」补充（默认关闭，不破坏零依赖承诺）。

### 贡献方向 🙋
欢迎贡献：新的高置信规则（请附误报反例测试）、成语/错别字词典、文档翻译、报告主题。

---

## 📦 打包与部署指南

本项目属于**工具库 / CLI 类项目**，跨平台纯 Python 实现，无需平台二进制产物。

```bash
# 安装构建工具
pip install build

# 构建 sdist 与通用 wheel
python -m build
# 产物：
#   dist/lingualint-1.0.0.tar.gz                 # 源码包
#   dist/lingualint-1.0.0-py3-none-any.whl      # 全平台通用 wheel
```

- **兼容环境**：Python 3.8+ / Windows、macOS、Linux；
- **运行测试**：`python -m unittest discover -s tests`（当前 64 个用例全部通过）；
- **离线部署**：把 wheel 拷入内网环境 `pip install <wheel>` 即可，无需联网；
- **卸载**：`pip uninstall LinguaLint`。

v1.0.0 分发包与 SHA-256 校验和见 [Releases 页面](https://github.com/gitstq/LinguaLint/releases/latest)。

---

## 🤝 贡献指南

提交 Issue / PR 前请阅读完整的 [CONTRIBUTING.md](CONTRIBUTING.md)，要点如下：

1. 🌿 从 `main` 切特性分支，分支名建议 `feat/xxx`、`fix/xxx`；
2. ✅ 新规则必须附带**正向命中 + 误报豁免**两类单元测试；
3. 📝 提交信息遵循 **Angular Convention**：
   `feat: 新增功能` / `fix: 修复问题` / `docs: 文档更新` / `refactor: 代码重构` / `test: 测试补充`；
4. 🧪 提交前确保 `python -m unittest discover -s tests` 全绿；
5. 💬 问题反馈请附上最小复现文本、Python 版本与实际输出。

---

## 📄 开源协议

本项目基于 **[MIT License](LICENSE)** 开源，可自由用于个人与商业用途，保留版权声明即可。

灵感致谢：[Automattic/harper](https://github.com/Automattic/harper)（产品理念参考，代码完全独立自研）。
