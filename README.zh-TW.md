# LinguaLint 🔎✍️

[简体中文](README.md) · **繁體中文** · [English](README.en.md)

<p align="center">
  <b>零相依 · 完全離線 · 中英雙語的寫作校對引擎</b><br/>
  一個僅用 Python 標準函式庫寫成的文本 Lint 工具（函式庫 + CLI），為 Markdown、說明書、
  文案與 commit 訊息提供 <b>語法糾錯、排版規範、可讀性評分、自動修復與 CI 關卡</b>。
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

## 🎉 專案介紹

**LinguaLint** 是一套在本機執行、完全離線的雙語寫作校對工具。它就像 ESLint 檢查程式碼一樣
檢查自然語言：把文章切成可定位的字元區間，以 **22 條確定性規則**找出拼字、語法、中英排版
與文風問題，每一條都附上**行列位置、問題說明與一鍵修復建議**，並可輸出終端機 / JSON /
Markdown / 單一自包含 HTML 四種報告。

### 解決什麼痛點 😣
- **線上工具不敢貼內部文件**：SaaS 文法檢查需要上傳文本，有資料外洩疑慮；LinguaLint 完全不連網；
- **中文排版長期靠人工**：中英混排空格、全半形標點、成語錯別字、語義贅詞缺乏自動化工具；
- **文件品質無法進入工程流程**：錯別字與超長句總在審稿時才被發現，缺少可在 CI 執行的品質關卡；
- **工具鏈依賴沉重**：NLP 模型體積大、安裝慢、跨平台容易失敗，難以塞進精簡 CI 映像檔。

### 自研差異化亮點 🌟
1. **真正零執行期相依**：僅使用 Python 標準函式庫，`py3-none-any` 通用 Wheel，跨平台隨裝即用；
2. **中英雙語一套引擎**：自動辨識語言，混排文件同時執行兩組規則族，彼此互不干擾；
3. **精度優先的確定性規則**：每條規則都具備白名單與保護區間（行內程式碼、程式碼區塊、URL 不會被誤判）；
4. **多輪收斂的安全自動修復**（`--fix`）：重疊修復自動排序、最多 5 輪收斂，重複執行結果一致；
5. **工程化閉環**：100 分制品質分數、`--min-score / --max-issues / --fail-severity` 三道 CI 關卡與明確結束碼；
6. **易於擴充**：`.lingualint.json` 可開關規則、覆寫嚴重度、新增專屬錯詞表與忽略詞。

> **靈感來源**：GitHub Trending（Rust 榜）專案 [Automattic/harper](https://github.com/Automattic/harper)
> ——一個優秀的**離線英文**文法檢查器。LinguaLint 未沿用其任何一行程式碼，僅參考「本機優先、
> 隱私優先」的產品理念，並在**中文語境支援、零相依 Python 執行環境、CI 關卡、自動修復與多格式報告**
> 等方向完成獨立自研與差異化補齊。

---

## ✨ 核心特性

### 🧱 22 條內建規則，五大類別
| 類別 | 規則數 | 涵蓋內容 |
| --- | ---: | --- |
| 📐 通用排版 COM | 8 | 行尾空白、連續空行、多餘空格、標點前空格、零寬/BOM 不可見字元、重複標點、引號成對、超長行 |
| 🇬🇧 英文 ENG | 8 | 重複單字、a/an 一致、句首大寫、逗號空格、易混詞（its/it's、than/then…）、高頻拼字錯誤、被動語態、弱化填充詞 |
| 🇨🇳 中文 ZH | 6 | 中文語境半形標點、中英/中數空格、功能助詞重複、成語錯別字（30+）、語義贅詞、中文長句 |

### 🧠 智慧保護區間
行內程式碼 `` `code` ``、圍欄程式碼區塊與 `http(s)://` 連結會**自動略過**，不會把程式碼與網址當作文章修改。

### 📊 可讀性與評分
- 英文：**Flesch Reading Ease** 與 **Flesch–Kincaid Grade**；
- 中文：平均句長、長句占比與四檔流暢度評價；
- **LinguaLint Score（滿分 100）**：error −10、warning −4、suggestion −1、info 0，最低 0 分。

### 🔧 四種報告 + 自動修復
- 終端機彩色報告（自動辨識 TTY，可以 `--no-color` 關閉）；
- JSON（機器可讀，方便二次整合）；
- Markdown（直接貼進 PR / Issue）；
- **自包含 HTML**（單一檔案、無外部資源、暗色主題，適合郵件寄送或歸檔）；
- `--fix` 原地安全修復，多輪收斂且具冪等性。

### 🧩 函式庫 + CLI 雙型態
既可於命令列批次處理，也能作為 Python 函式庫嵌入寫作流水線、靜態網站建置或編輯器後端。

---

## 🚀 快速開始

### 環境需求 🧰
- **Python 3.8 – 3.13**（無任何第三方執行期相依）
- Windows / macOS / Linux 全平台適用

### 安裝 ⬇️
最新 Release 下載：<https://github.com/gitstq/LinguaLint/releases/latest>

```bash
# 方式一：安裝通用 wheel（自動註冊 lingualint 指令）
pip install lingualint-1.0.0-py3-none-any.whl

# 方式二：原始碼可編輯安裝（參與開發）
git clone https://github.com/gitstq/LinguaLint.git
cd LinguaLint
pip install -e .

# 方式三：免安裝直接執行
python -m lingualint README.md
```

### 30 秒體驗 ⚡
```bash
# 檢查單一檔案
lingualint examples/sample_zh.md

# 遞迴檢查整個資料夾並輸出 HTML 報告
lingualint docs/ -f html -o report.html

# 自動修復所有可安全修復的問題
lingualint docs/ --fix

# 管線輸入
echo "Its definately wrong ," | lingualint --lang en
```

實際終端機輸出：

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

HTML 報告範例可直接開啟預覽：[docs/sample-report.html](docs/sample-report.html)。

---

## 📖 詳細使用指南

### 命令列參數一覽 🧾
| 參數 | 說明 |
| --- | --- |
| `paths` | 待檢查的檔案或資料夾（資料夾遞迴掃描）；留空則讀取標準輸入 |
| `-f, --format` | `text`（預設）/ `json` / `markdown` / `html` |
| `-o, --output` | 將報告寫入檔案而非標準輸出 |
| `--lang` | `auto`（預設）/ `en` / `zh`，強制指定文件語言 |
| `--config` | 指定設定檔路徑（預設自動向上尋找 `.lingualint.json`） |
| `--fix` | 原地套用安全自動修復 |
| `--ext` | 資料夾掃描的副檔名，逗號分隔（預設 `.md,.markdown,.txt,.rst,.text`） |
| `--exclude` | fnmatch 排除模式，可重複帶入 |
| `--min-score N` | 最低品質分，低於 N 則關卡失敗 |
| `--max-issues N` | 可容忍的阻斷級問題數量（預設 0） |
| `--fail-severity` | 計入關卡的最低嚴重度：`error/warning/suggestion/info`（預設 warning） |
| `--no-color` | 關閉 ANSI 顏色 |
| `--list-rules` | 列出全部規則後退出 |
| `--version` | 顯示版本號 |

### 結束碼 🚦
| 結束碼 | 意義 |
| ---: | --- |
| `0` | 檢查通過，關卡達標 |
| `1` | 發現阻斷級問題或分數低於門檻（CI 紅燈） |
| `2` | 用法錯誤 / 路徑不存在 / 設定不合法 |

### 規則目錄 📚
| ID | 預設層級 | 自動修復 | 說明 |
| --- | --- | :---: | --- |
| COM001 | warning | ✅ | 行尾空白 |
| COM002 | suggestion | ✅ | 連續多個空行 |
| COM003 | warning | ✅ | 字詞間連續多空格 |
| COM004 | warning | ✅ | 標點前多餘空格 |
| COM005 | error | ✅ | 零寬字元 / BOM / 雙向控制字元 |
| COM006 | suggestion | ✅ | 重複標點（`...` 省略號豁免） |
| COM007 | warning | ❌ | 引號不成對 |
| COM008 | info | ❌ | 單行過長（預設 200） |
| ENG001 | error | ✅ | 相鄰重複單字（that/had 合法重疊豁免） |
| ENG002 | warning | ✅ | a / an 誤用（含 hour、university 等發音例外） |
| ENG003 | suggestion | ✅ | 句首未大寫（e.g. 等縮寫豁免） |
| ENG004 | warning | ✅ | 逗號後缺空格 |
| ENG005 | warning | ✅ | its/it's、than/then、lose/loose、affect/effect 等易混詞 |
| ENG006 | error | ✅ | 18 個高頻拼字錯誤 + 自訂錯詞表 |
| ENG007 | suggestion | ❌ | 疑似被動語態（形容詞化 -ed 豁免） |
| ENG008 | suggestion | ❌ | very / really / just 等弱化填充詞 |
| ZH001 | warning | ✅ | 中文語境誤用半形標點（數字小數、時間豁免） |
| ZH002 | suggestion | ✅ | 中英文 / 中數之間缺空格 |
| ZH003 | error | ✅ | 的/了/是/在 等功能助詞重複（合法疊字豁免） |
| ZH004 | error | ✅ | 30+ 高頻成語 / 常用詞錯別字 |
| ZH005 | suggestion | 部分 | 語義贅詞（涉及到、免費贈送、大約…左右） |
| ZH006 | info | ❌ | 中文單句過長（預設 60 漢字） |

### 設定檔 `.lingualint.json` ⚙️
放在專案根目錄即自動辨識，也可以用 `--config` 指定：

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

- `rules`：`false` 關閉規則；傳入 `error/warning/suggestion/info` 可覆寫預設嚴重度；
- `typo_pairs`：專案級錯詞表，英文詞按字詞邊界匹配，中文按子字串匹配；
- `ignore_words`：拼字白名單（品牌名、內部術語）。

### Python API 呼叫 🐍
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

### 常見使用情境 🧪
1. **靜態網誌建置前檢查**：在建置腳本前加上 `lingualint content/`；
2. **PR 文件關卡**：搭配下方 GitHub Actions，文件未達標即亮紅燈；
3. **批次清理歷史文件**：`lingualint docs/ --fix` 後以 Git diff 審閱；
4. **編輯器 / 流水線後端**：透過 `-f json` 取用結構化結果；
5. **發布前歸檔**：`-f html -o report.html` 產出可郵件分發的單檔報告。

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

## 💡 設計思路與迭代規劃

### 為什麼選擇「標準函式庫 + 規則」而非大模型 🧠
- **可重現**：同樣輸入永遠得到同樣輸出，審稿與回歸測試都能信賴；
- **零成本離線**：不需下載模型、不需 API Key、不發任何網路請求；
- **體積極小**：Wheel 不到 30 KB，冷啟動為毫秒級；
- **精度優先**：寧可漏報也不誤報——每條規則都配備豁免白名單與保護區間。

### 架構分層 🏗️
```
text (str)
  └─ Document        行偏移表 + 保護區間（程式碼/URL）
       └─ Rule 族    COM（通用）/ ENG（英文）/ ZH（中文）
            └─ Issue 字元級起止 + 嚴重度 + 修復建議
                 └─ Linter      規則排程、語言調度、評分、多輪 fix
                      └─ reporter text / json / markdown / html
```

### 迭代路線圖 🗺️
- **v1.1（規劃中）**：擴充中文病句模式（搭配不當、主語殘缺啟發式）、pre-commit hook、SARIF 輸出、Markdown frontmatter / 表格豁免；
- **v1.2（規劃中）**：規則包外置、使用者自訂正則規則、CSV 詞典匯入；
- **v2.0（遠期）**：日文 / 韓文排版規則族、LanguageTool 詞典相容，以及預設關閉的輕量統計模型作為「建議級」補充（不打破零相依承諾）。

### 貢獻方向 🙋
歡迎貢獻新高信度規則（請附上誤報反例測試）、成語錯別字詞典、文件翻譯與報告主題。

---

## 📦 打包與部署指南

本專案屬於**工具函式庫 / CLI 類型**，以跨平台純 Python 實作，不需要平台專屬的二進位產物。

```bash
pip install build
python -m build
# 產物：
#   dist/lingualint-1.0.0.tar.gz              # 原始碼封包
#   dist/lingualint-1.0.0-py3-none-any.whl   # 全平台通用 wheel
```

- **相容環境**：Python 3.8+ / Windows、macOS、Linux；
- **執行測試**：`python -m unittest discover -s tests`（目前 64 個測試全數通過）；
- **離線部署**：把 wheel 帶入內網環境執行 `pip install <wheel>` 即可，完全不需聯網；
- **解除安裝**：`pip uninstall LinguaLint`。

v1.0.0 分發檔與 SHA-256 校驗碼請見 [Releases 頁面](https://github.com/gitstq/LinguaLint/releases/latest)。

---

## 🤝 貢獻指南

提交 Issue / Pull Request 前請先閱讀完整的 [CONTRIBUTING.md](CONTRIBUTING.md)，重點如下：

1. 🌿 從 `main` 切出特性分支，建議命名 `feat/xxx`、`fix/xxx`；
2. ✅ 新規則必須同時附上**正向命中**與**誤報豁免**兩類單元測試；
3. 📝 提交訊息遵循 **Angular 規範**：
   `feat: 新增功能` / `fix: 修復問題` / `docs: 文件更新` / `refactor: 重構` / `test: 測試補充`；
4. 🧪 提交前請確認 `python -m unittest discover -s tests` 全綠；
5. 💬 回報問題請附上最小重現文本、Python 版本與實際輸出。

---

## 📄 開源授權

本專案以 **[MIT License](LICENSE)** 授權開源，個人與商業用途皆可自由使用，請保留版權宣告。

靈感致謝：[Automattic/harper](https://github.com/Automattic/harper)（僅參考產品理念，程式碼完全獨立自研）。
