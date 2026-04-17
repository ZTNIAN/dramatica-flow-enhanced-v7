# Dramatica-Flow Enhanced V7 — 项目交接文档

最后更新：2026-04-17
版本：V7（V6 基础上 Web UI 对齐 CLI + 全面自检修复）

---

## 项目一句话

Dramatica-Flow Enhanced 是一个 AI 自动写小说系统。你给它一句话设定，它帮你：

- 市场分析 — 分析目标读者偏好（引用番茄小说真实数据）
- 构建世界观 — 角色/势力/地点/规则，全部自动生成
- 角色成长规划 — 每个主要角色8维档案 + 成长弧线 + 转折点
- 情绪曲线设计 — 整书情绪起伏规划，精确操控读者情绪
- 生成大纲 — 三幕结构 + 逐章规划 + 张力曲线
- 自动写作 — 一章一章写，每章2000-4000字
- 多维审查 — 对话/场景/心理/风格，4个专项审查Agent
- 自动审计 — 9维度加权评分 + 17条红线一票否决
- 审查→修订闭环 — 所有审查问题合并进修订循环
- MiroFish读者测试 — 每5章模拟1000名读者反馈 → 反馈注入下一章
- Agent能力画像 — 追踪每个Agent的工作质量
- Token费用追踪 — 精确到每章每Agent的LLM消耗（Web UI可视化）
- 知识库热加载 — 改了知识库文件立即生效，不用重启（Web UI按钮）
- 错误恢复 — 写作中断后可从checkpoint恢复（Web UI提示+按钮）
- **Web UI 全功能** — 浏览器端与CLI功能完全对齐

一句话：V6 是"修复端点+自适应审查+MiroFish闭环+Token追踪+KB热加载+Checkpoint恢复"，V7 是"Web UI全面对齐CLI + 自检修复12个BUG"。

---

## 版本历史

| 版本 | 地址 | 说明 |
|------|------|------|
| 原版 | [dramatica-flow](https://github.com/ydsgangge-ux/dramatica-flow) | 叙事逻辑强，但缺乏前期规划和质量管控 |
| V1 | [v1](https://github.com/ZTNIAN/dramatica-flow-enhanced) | 12个增强点完成但有6项"写了没接入" |
| V2 | [v2](https://github.com/ZTNIAN/dramatica-flow-enhanced-v2) | 修复V1的核心问题 + 知识库扩充 |
| V3 | [v3](https://github.com/ZTNIAN/dramatica-flow-enhanced-v3) | 全面升级：知识库+Web界面+动态规划+KB追踪 |
| V4 | [v4](https://github.com/ZTNIAN/dramatica-flow-enhanced-v4) | 架构重构：模块化+配置化+安全加固+异步化 |
| V5 | [v5](https://github.com/ZTNIAN/dramatica-flow-enhanced-v5) | 多LLM+选择性审查+WebSocket+Agent画像可视化 |
| V6 | [v6](https://github.com/ZTNIAN/dramatica-flow-enhanced-v6) | 修复端点+自适应审查+闭环+追踪+热加载+恢复 |
| **V7（当前）** | [v7](https://github.com/ZTNIAN/dramatica-flow-enhanced-v7) | **Web UI对齐CLI + 自检修复12个BUG** |

---

## 快速开始

```bash
git clone https://github.com/ZTNIAN/dramatica-flow-enhanced-v7.git
cd dramatica-flow-enhanced-v7

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -e .

# 配置API Key
cp .env.example .env
# 用编辑器打开 .env，填入你的 DeepSeek API Key
```

### 启动

```bash
# 方式A：命令行
df --help

# 方式B：Web UI（推荐）
uvicorn core.server:app --reload --host 0.0.0.0 --port 8766
# 然后浏览器打开 http://127.0.0.1:8766/
```

---

## V6 → V7 改动总结

### 第一轮：Web UI 功能对齐（5项新增）

改动文件：`dramatica_flow_web_ui.html`

| 功能 | API端点 | Web UI |
|------|---------|--------|
| Token消耗面板 | `GET /api/books/{id}/token-usage` | 新增"💰 Token消耗"Tab，表格+柱状图 |
| Checkpoint恢复 | `POST /api/books/{id}/resume` | 写作页顶部中断提示+恢复按钮 |
| KB热加载 | `POST /api/books/reload-kb` | 设置页重新加载按钮+状态显示 |
| 角色成长规划 | `POST /api/books/{id}/character-growth` | 世界观页"👤 角色成长规划"按钮 |
| 情绪曲线可视化 | `POST /api/books/{id}/emotion-curve` | 新增"💪 情绪曲线"Tab，Canvas曲线图 |

### 第二轮：自检修复（12个BUG）

| # | 严重度 | 问题 | 修复 |
|---|--------|------|------|
| 1 | 🔴 | "写下一章"调用 `/action/write` → 404 | 改为 `/books/{id}/write` |
| 2 | 🔴 | Token面板字段名与后端完全不匹配 | 重写前端对齐后端格式 |
| 3 | 🔴 | KB热加载toast显示 `undefined` | `res.files_loaded` → `res.changed_count` |
| 4 | 🔴 | "续写"发送 `extra_chapters`，API期望 `count` | 统一为 `count` |
| 5 | 🔴 | Legacy路由双重前缀 `/api/books/api/action/*` | 改为独立注册到app |
| 6 | 🟡 | `action_write()` 无checkpoint支持 | 增加checkpoint写入逻辑 |
| 7 | 🟡 | 角色成长只处理第一个角色 | 遍历所有角色 |
| 8 | 🟡 | 情绪曲线硬编码90章 | 从章纲推断章节数 |
| 9 | 🟡 | `_recent_low_score_trigger` 数据源问题 | 保留（低风险） |
| 10 | 🟡 | `action_write`与`continue_writing` checkpoint不一致 | 统一checkpoint逻辑 |
| 11 | 🟢 | `_build_pipeline` 每次创建全部Agent | 保留（影响小） |
| 12 | 🟢 | TrackedProvider无法穿透FallbackProvider检测模型 | 增加穿透逻辑 |

### 改动文件清单

| 文件 | 改动 |
|------|------|
| `dramatica_flow_web_ui.html` | 修复#1 #2 #3 #4 — 写下一章端点、Token面板格式、KB消息、续写字段名 |
| `core/server/routers/writing.py` | 修复#5 #6 #10 — legacy路由独立注册、action_write增加checkpoint |
| `core/server/routers/enhanced.py` | 修复#7 #8 — 角色成长遍历所有、情绪曲线从章纲推断 |
| `core/server/__init__.py` | 修复#5 — 调用register_legacy_routes |
| `core/llm/__init__.py` | 修复#12 — TrackedProvider模型检测穿透 |

---

## Web UI 与 CLI 功能对照

| 功能 | CLI | Web UI (V7) |
|------|-----|-------------|
| 创建书籍 | `df worldbuild` | ✅ |
| 市场分析 | `df market` | ✅ |
| 世界观构建 | `df worldbuild` | ✅ |
| 角色成长规划 | 管线自动 | ✅ (V7修复) |
| 情绪曲线设计 | 管线自动 | ✅ (V7修复) |
| 大纲规划 | `df outline` | ✅ |
| 写作 | `df write` | ✅ (V7修复) |
| 续写 | — | ✅ (V7修复) |
| 审计 | `df audit` | ✅ |
| 修订 | `df revise` | ✅ |
| Token追踪 | API | ✅ (V7修复) |
| Checkpoint恢复 | API | ✅ (V7修复) |
| KB热加载 | API | ✅ (V7修复) |
| Agent画像 | API | ✅ |
| 质量仪表盘 | API | ✅ |
| 导出 | `df export` | ✅ |

---

## 文件结构

```
dramatica-flow-enhanced-v7/
├── cli/main.py                    # CLI入口
├── core/
│   ├── agents/                    # Agent模块（21个文件）
│   │   ├── __init__.py            # re-export入口
│   │   ├── kb.py                  # 公共知识库模块（热加载）
│   │   ├── architect.py           # 建筑师
│   │   ├── writer.py              # 写手
│   │   ├── auditor.py             # 审计员
│   │   ├── reviser.py             # 修订者
│   │   ├── summary.py             # 摘要
│   │   ├── patrol.py              # 巡查
│   │   ├── worldbuilder.py        # 世界观构建
│   │   ├── outline_planner.py     # 大纲规划
│   │   ├── market_analyzer.py     # 市场分析
│   │   └── enhanced/              # 增强Agent（10个文件）
│   │       ├── character_growth.py
│   │       ├── dialogue.py
│   │       ├── emotion_curve.py
│   │       ├── feedback.py
│   │       ├── style_checker.py
│   │       ├── scene_architect.py
│   │       ├── psychological.py
│   │       ├── mirofish.py
│   │       └── methods.py
│   ├── pipeline.py                # 写作管线（自适应审查+MiroFish闭环）
│   ├── llm/__init__.py            # LLM抽象层（V7: 修复模型检测）
│   ├── token_tracker.py           # Token追踪
│   ├── narrative/__init__.py      # 叙事引擎
│   ├── state/__init__.py          # 状态管理
│   ├── types/                     # 数据类型
│   ├── validators/__init__.py     # 写后验证器
│   ├── server/                    # Web服务（13个文件）
│   │   ├── __init__.py            # app+CORS+WebSocket（V7: 注册legacy路由）
│   │   ├── deps.py                # 公共依赖+请求模型
│   │   └── routers/
│   │       ├── books.py / setup.py / chapters.py
│   │       ├── outline.py / writing.py / ai_actions.py
│   │       ├── threads.py / analysis.py / enhanced.py
│   │       ├── settings.py / export.py
│   ├── quality_dashboard.py
│   ├── dynamic_planner.py
│   ├── kb_incentive.py
│   └── knowledge_base/            # 知识库（30+文件）
├── dramatica_flow_web_ui.html     # Web UI（V7: 全面对齐CLI+修复）
├── dramatica_flow_timeline.html
├── pyproject.toml
├── .env.example
├── PROJECT_HANDOFF.md
└── USER_MANUAL.md
```

---

## 核心Agent一览

| Agent | 职责 | 触发时机 |
|-------|------|----------|
| WorldBuilderAgent | 一句话→世界观 | df worldbuild |
| OutlinePlannerAgent | 大纲+章纲 | df outline |
| MarketAnalyzerAgent | 市场分析 | df market |
| ArchitectAgent | 规划单章蓝图 | 每章写前 |
| WriterAgent | 生成正文 | 每章写手 |
| PatrolAgent | 快速扫描 | 写后立即 |
| AuditorAgent | 9维加权审计 | 巡查后 |
| ReviserAgent | 修订正文 | 审计不通过 |
| SummaryAgent | 章节摘要 | 写完后 |

### 增强Agent

| Agent | 职责 |
|-------|------|
| CharacterGrowthExpert | 角色8维档案 + 成长弧线规划 |
| DialogueExpert | 对话审查 + 语言指纹六维度 |
| EmotionCurveDesigner | 整书情绪曲线 + 每章情绪类型 |
| FeedbackExpert | 读者反馈分类路由 + 闭环追踪 |
| HookDesigner | 7种章末钩子方法论 |
| OpeningEndingDesigner | 黄金三章 + 全书结尾 |
| StyleConsistencyChecker | 五维一致性检查 |
| SceneArchitect | 场景四维审核 |
| PsychologicalPortrayalExpert | 心理四维审核 |
| MiroFishReader | 1000名读者模拟 |

---

## 写作管线流程

```
[市场分析] → [世界构建] → [角色成长规划] → [情绪曲线设计] → [大纲规划]
    ↓
[单章循环]（每章重复）
  ├── Checkpoint保存
  ├── 加载MiroFish反馈（V6闭环）
  ├── 建筑师规划蓝图
  ├── 写手生成正文
  ├── Token统计记录
  ├── 对话/场景/心理专家审查（选择性触发）
  ├── 写后验证（零LLM硬规则）
  ├── 巡查者快速扫描
  ├── 审计员9维度加权评分
  │   └── 合并审查问题 → 不通过 → 修订（最多3轮）
  ├── 自适应审查判断
  ├── 风格一致性检查
  ├── 保存最终稿
  ├── 因果链提取 → 摘要生成
  ├── 质量仪表盘 + 动态规划器 + KB统计 + Agent画像
  ├── Token统计保存
  ├── Checkpoint更新
  └── MiroFish测试（每5章）
    ↓
[导出] → Markdown / TXT
```

---

## API端点一览

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/books/{id}/write` | POST | 写作（V7: 增加checkpoint） |
| `/api/books/{id}/continue-writing` | POST | 批量续写 |
| `/api/books/{id}/audit` | POST | 审计 |
| `/api/books/{id}/revise` | POST | 修订 |
| `/api/books/{id}/token-usage` | GET | Token使用量 |
| `/api/books/{id}/checkpoint` | GET | Checkpoint状态 |
| `/api/books/{id}/resume` | POST | 从checkpoint恢复 |
| `/api/books/{id}/character-growth` | POST | 角色成长规划 |
| `/api/books/{id}/emotion-curve` | POST | 情绪曲线设计 |
| `/api/books/{id}/agent-performance` | GET | Agent能力画像 |
| `/api/books/reload-kb` | POST | 热加载知识库 |
| `/api/books/kb-status` | GET | KB文件状态 |
| `/api/action/write` | POST | 旧版兼容（V7修复） |
| `/api/action/audit` | POST | 旧版兼容（V7修复） |
| `/api/action/revise` | POST | 旧版兼容（V7修复） |

---

## 环境变量

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| PIPELINE_MAX_REVISE_ROUNDS | 3 | 最大修订轮数 |
| PIPELINE_MIROFISH_INTERVAL | 5 | MiroFish每N章触发 |
| PIPELINE_REVIEW_MODE | adaptive | 审查模式 |
| PIPELINE_REVIEW_FORCE_SCORE | 70 | 低于此分触发全量审查 |
| PIPELINE_AUDIT_PASS_TOTAL | 95 | 审计通过加权总分 |
| LLM_FALLBACK_CHAIN | deepseek | 降级链 |
| WS_ENABLED | true | WebSocket进度推送 |

---

## 迭代备忘

### GitHub API 上传脚本

```python
import base64, json, urllib.request, time
from urllib.parse import quote

TOKEN = "你的GitHub Token"
REPO = "ZTNIAN/dramatica-flow-enhanced-v7"

def upload(filepath, content, message):
    encoded = "/".join(quote(seg, safe="") for seg in filepath.split("/"))
    content_b64 = base64.b64encode(content.encode("utf-8")).decode()
    sha = ""
    try:
        url = f"https://api.github.com/repos/{REPO}/contents/{encoded}"
        req = urllib.request.Request(url, headers={
            "Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"
        })
        sha = json.loads(urllib.request.urlopen(req, timeout=10).read()).get("sha", "")
    except:
        pass
    data = json.dumps({
        "message": message, "content": content_b64, "branch": "main",
        **({"sha": sha} if sha else {}),
    }).encode()
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/contents/{encoded}",
        data=data, method="PUT",
        headers={
            "Authorization": f"token {TOKEN}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
    )
    result = json.loads(urllib.request.urlopen(req, timeout=20).read())
    commit = result.get("commit", {}).get("sha", "ERROR")[:8]
    print(f"  {filepath} -> {commit}")
    time.sleep(1.5)
```

### 注意事项

- ❌ `git push` 经常卡死（GnuTLS error -110）→ 用 GitHub Contents API
- ❌ `sed -i` 处理中文会乱码 → 用 Python pathlib
- ❌ `base64 -w0` 传大文件到 shell 变量 → 用 Python urllib
- ⚠️ AI 推完代码后必须立刻 revoke token

### 每次迭代流程

1. 把本文件 `PROJECT_HANDOFF.md` 发给 AI
2. AI 读交接文档 → 理解项目
3. AI 修改代码
4. AI 用 GitHub API 逐文件推送
5. AI 更新交接文档并推送
6. **Revoke token**（推完后立刻做！）
7. 本地拉取：`git fetch origin && git reset --hard origin/main`

---

## V7 未来方向

| 优先级 | 方向 | 说明 |
|--------|------|------|
| P0 | 端到端测试 | 部署后实际跑一遍完整流程 |
| P1 | 多书并行写作 | 支持同时写多本书，管线隔离 |
| P2 | 写作质量趋势图 | 基于Token追踪数据，画出每章质量+费用趋势 |
| P2 | 知识库版本管理 | KB修改历史追踪，支持回滚 |
| P2 | Agent提示词可视化 | 在Web UI中查看和编辑每个Agent的prompt |
| P3 | 导出格式增强 | 支持EPUB、PDF导出 |
| P3 | 协作写作 | 多人共享同一本书的写作任务 |

---

## 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.11+ |
| 后端 | FastAPI |
| CLI | Typer |
| 数据存储 | 文件系统（JSON + Markdown） |
| LLM | DeepSeek API（默认）/ Ollama / Claude / GPT-4 |
| 前端 | 单文件 HTML（暗色主题） |
| 校验 | Pydantic v2 |

---

本文档由AI自动生成。下次迭代时，把本文件发给AI即可快速理解整个项目。
