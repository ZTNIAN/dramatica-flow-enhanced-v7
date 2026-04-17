# Dramatica-Flow Enhanced V7 — 项目交接文档

最后更新：2026-04-17
版本：V7（V6 基础上 Web UI 对齐 CLI + Token面板 + Checkpoint恢复 + KB热加载UI + 角色成长按钮 + 情绪曲线可视化）

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

一句话：V6 是"修复端点+自适应审查真正智能+MiroFish闭环+随时知道花了多少钱+改知识库不用重启"，V7 是"Web UI全面对齐CLI，所有V6后端功能前端都有对应UI"。

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
| **V7（当前）** | [v7](https://github.com/ZTNIAN/dramatica-flow-enhanced-v7) | **Web UI 全面对齐 CLI + 5项前端增强** |

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

### .env 文件内容

```
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=你的key    # 去 https://platform.deepseek.com 申请
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
DEFAULT_WORDS_PER_CHAPTER=2000
DEFAULT_TEMPERATURE=0.7
AUDITOR_TEMPERATURE=0.0
BOOKS_DIR=./books
```

### V4-V6 可选配置（不设则用默认值）

```
# 管线参数
PIPELINE_MAX_REVISE_ROUNDS=3
PIPELINE_MIROFISH_INTERVAL=5
PIPELINE_REVIEW_SCORE_FLOOR=75
PIPELINE_STYLE_SCORE_FLOOR=80
PIPELINE_AUDIT_PASS_TOTAL=95
PIPELINE_DORMANCY_THRESHOLD=5

# 安全配置
CORS_ALLOW_ORIGINS=http://localhost:8766,http://127.0.0.1:8766

# 多LLM配置
CLAUDE_API_KEY=你的key
OPENAI_API_KEY=你的key
LLM_FALLBACK_CHAIN=deepseek,claude,openai

# 审查模式: all/light/minimal/adaptive
PIPELINE_REVIEW_MODE=adaptive

# WebSocket
WS_ENABLED=true

# 自适应审查触发阈值
PIPELINE_REVIEW_FORCE_SCORE=70
PIPELINE_REVIEW_FORCE_WINDOW=3

# Token追踪（自动启用，无需配置）
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

V6 的后端功能已经完整，但 Web UI 缺少对应界面。V7 只改了一个文件：

**改动文件：`dramatica_flow_web_ui.html`**（225KB → 242KB）

| 优先级 | 功能 | API端点 | Web UI实现 |
|--------|------|---------|-----------|
| P1 | Token消耗面板 | `GET /api/books/{id}/token-usage` | 新增"💰 Token消耗"Tab，表格+柱状图展示每章每Agent消耗和美元费用 |
| P1 | Checkpoint恢复 | `POST /api/books/{id}/resume` + `GET /api/books/{id}/checkpoint` | 写作页面顶部黄色提示条，显示"检测到中断，恢复写作"按钮 |
| P1 | KB热加载 | `POST /api/books/reload-kb` + `GET /api/books/kb-status` | 设置页面新增"重新加载知识库"+"检查KB状态"按钮，显示文件更新状态 |
| P1 | 角色成长规划 | `POST /api/books/{id}/character-growth` | 世界观构建页面新增"👤 角色成长规划"按钮，调用CharacterGrowthExpert |
| P1 | 情绪曲线可视化 | `POST /api/books/{id}/emotion-curve` | 新增"💪 情绪曲线"Tab，Canvas绘制整书情绪曲线图+彩色柱状图+图例 |

### 详细功能说明

#### 1. Token消耗面板

- 位置：审计页面新增 "💰 Token消耗" Tab
- 功能：调用 `GET /api/books/{id}/token-usage`
- 展示：每章每Agent的token消耗表格 + 柱状图（按章节聚合） + 美元费用估算
- 包含总计行和按章节分组

#### 2. Checkpoint恢复

- 位置：写作页面顶部
- 触发：加载书籍时自动调用 `GET /api/books/{id}/checkpoint`
- 显示：黄色提示条 "检测到中断的写作任务（第X章），是否恢复？"
- 按钮："▶ 恢复写作" → 调用 `POST /api/books/{id}/resume`
- 恢复成功后自动刷新章节列表

#### 3. KB热加载

- 位置：设置页面
- 按钮1："🔄 重新加载知识库" → 调用 `POST /api/books/reload-kb`
- 按钮2："📊 检查KB状态" → 调用 `GET /api/books/kb-status`
- 显示：知识库文件列表，每个文件显示路径、最后修改时间、是否已更新状态

#### 4. 角色成长规划按钮

- 位置：世界观构建页面（与"AI 生成世界观"并列）
- 按钮："👤 角色成长规划"
- 功能：调用 `POST /api/books/{id}/character-growth`（CharacterGrowthExpert Agent）
- 展示：每个角色的8维档案（背景/动机/恐惧/缺陷/弧线/关系/象征/转折点）+ 成长弧线规划

#### 5. 情绪曲线可视化

- 位置：审计页面新增 "💪 情绪曲线" Tab
- 功能：调用 `POST /api/books/{id}/emotion-curve` 设计曲线
- 展示：
  - **Canvas曲线图**：高DPI渲染，带网格线和Y轴标签，每种情绪类型不同颜色
  - **彩色柱状图**：每章一个柱子，高度=强度，颜色=情绪类型
  - **图例**：13种情绪类型（压抑/紧张/恐惧/爽/感动/幽默/温暖/愤怒/悲伤/满足/激动/期待/惊讶）
  - **设计说明**：展示EmotionCurveDesigner的规划文字

---

## Web UI 与 CLI 功能对照

| 功能 | CLI | Web UI (V7) |
|------|-----|-------------|
| 创建书籍 | `df worldbuild` | ✅ 点击按钮 |
| 市场分析 | `df market` | ✅ 市场分析按钮 |
| 世界观构建 | `df worldbuild` | ✅ AI生成世界观按钮 |
| 角色成长规划 | 管线自动触发 | ✅ 角色成长规划按钮 (V7新增) |
| 情绪曲线设计 | 管线自动触发 | ✅ 情绪曲线Tab (V7新增) |
| 大纲规划 | `df outline` | ✅ 自动生成 |
| 写作 | `df write` | ✅ 写下一章按钮 |
| 审计 | `df audit` | ✅ 审计Tab |
| 修订 | `df revise` | ✅ 自动触发 |
| Token追踪 | API端点 | ✅ Token消耗Tab (V7新增) |
| Checkpoint恢复 | API端点 | ✅ 中断提示+恢复按钮 (V7新增) |
| KB热加载 | API端点 | ✅ 设置页按钮 (V7新增) |
| Agent画像 | API端点 | ✅ Agent画像Tab |
| 质量仪表盘 | API端点 | ✅ 质量仪表盘Tab |
| 导出 | `df export` | ✅ 导出按钮 |

**结论：V7 的 Web UI 已与 CLI 功能完全对齐。**

---

## 文件结构

```
dramatica-flow-enhanced-v7/
├── cli/main.py                    # CLI入口
├── core/
│   ├── agents/                    # Agent模块（21个文件）
│   │   ├── __init__.py            # re-export入口
│   │   ├── kb.py                  # 公共知识库模块（V6：热加载）
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
│   ├── pipeline.py                # 写作管线（V6：自适应审查+MiroFish闭环）
│   ├── llm/__init__.py            # LLM抽象层（V6：TrackedProvider）
│   ├── token_tracker.py           # Token追踪（V6新增）
│   ├── narrative/__init__.py      # 叙事引擎
│   ├── state/__init__.py          # 状态管理
│   ├── types/                     # 数据类型
│   ├── validators/__init__.py     # 写后验证器
│   ├── server/                    # Web服务（13个文件）
│   │   ├── __init__.py            # app实例+中间件+CORS+WebSocket
│   │   ├── deps.py                # 公共依赖+请求模型
│   │   └── routers/               # 路由模块
│   │       ├── books.py / setup.py / chapters.py
│   │       ├── outline.py / writing.py / ai_actions.py
│   │       ├── threads.py / analysis.py / enhanced.py
│   │       ├── settings.py / export.py
│   ├── quality_dashboard.py       # 质量仪表盘
│   ├── dynamic_planner.py         # 动态规划器
│   ├── kb_incentive.py            # KB查询激励
│   └── knowledge_base/            # 知识库（30+文件）
│       ├── rules/ references/ agent-specific/
│       ├── examples/ fanqie-data/ indexes/
├── templates/                     # JSON配置模板
├── tests/                         # 测试
├── docs/                          # 文档
├── dramatica_flow_web_ui.html     # Web UI（V7：全面对齐CLI）
├── dramatica_flow_timeline.html   # 时间轴可视化
├── pyproject.toml                 # 项目配置
├── .env.example                   # 环境变量模板
├── PROJECT_HANDOFF.md             # 本文件
└── USER_MANUAL.md                 # 操作手册
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

| 优先级 | Agent | 职责 |
|--------|-------|------|
| P1 | CharacterGrowthExpert | 角色8维档案 + 成长弧线规划 |
| P1 | DialogueExpert | 对话审查 + 语言指纹六维度 |
| P1 | EmotionCurveDesigner | 整书情绪曲线 + 每章情绪类型 |
| P1 | FeedbackExpert | 读者反馈分类路由 + 闭环追踪 |
| P2 | HookDesigner | 7种章末钩子方法论（注入Architect） |
| P2 | OpeningEndingDesigner | 黄金三章 + 全书结尾（注入Architect） |
| P2 | StyleConsistencyChecker | 五维一致性检查 |
| P3 | SceneArchitect | 场景四维审核 |
| P3 | PsychologicalPortrayalExpert | 心理四维审核 |
| P3 | MiroFishReader | 1000名读者模拟 |

---

## 写作管线流程

```
[市场分析]（可选）
  题材 → MarketAnalyzer → 风格指南 + 读者偏好
  ↓
[世界构建]（必做）
  一句话设定 → WorldBuilder → 世界观JSON
  ↓
[角色成长规划]
  角色列表 → CharacterGrowthExpert → 8维档案 + 成长弧线
  ↓
[情绪曲线设计]
  章节数 → EmotionCurveDesigner → 整书情绪曲线
  ↓
[大纲规划]（必做）
  世界观 → OutlinePlanner → 三幕结构 + 章纲
  ↓
[单章循环]（每章重复）
  ├── Checkpoint保存（V6：错误恢复）
  ├── 加载MiroFish反馈（V6：闭环）
  ├── 建筑师：规划蓝图（含读者反馈上下文）
  ├── 写手：生成正文 + 结算表
  ├── Token统计记录（V6：费用追踪）
  ├── 对话专家审查 → 问题汇入修订循环
  ├── 验证器：零LLM硬规则扫描
  ├── 巡查者：快速扫描
  ├── 场景审核 → 问题汇入修订循环
  ├── 心理审核 → 问题汇入修订循环
  ├── 审计员：9维度加权评分
  │   └── 合并所有审查问题 → 不通过 → 修订（最多3轮）
  ├── 自适应审查判断（V6：低分/连续返工触发全量）
  ├── 风格一致性检查 → 不通过则polish修正
  ├── 保存最终稿
  ├── 因果链提取 → 摘要生成 → 状态更新
  ├── 质量仪表盘记录
  ├── 动态规划器更新
  ├── KB查询统计保存
  ├── Agent能力画像记录
  ├── Token统计保存（V6）
  ├── Checkpoint更新为完成（V6）
  └── MiroFish测试（每5章）
  ↓
[导出]
  df export → Markdown / TXT
```

---

## API端点一览

| 端点 | 方法 | 说明 | Web UI对应 |
|------|------|------|-----------|
| `/api/books/{id}/token-usage` | GET | Token使用量和费用估算 | Token消耗Tab |
| `/api/books/reload-kb` | POST | 热加载知识库文件 | 设置页按钮 |
| `/api/books/kb-status` | GET | 检查知识库文件更新状态 | 设置页KB状态 |
| `/api/books/{id}/checkpoint` | GET | 查看当前checkpoint状态 | 写作页中断提示 |
| `/api/books/{id}/resume` | POST | 从checkpoint恢复写作 | 恢复写作按钮 |
| `/api/books/{id}/write` | POST | 写作端点 | 写下一章按钮 |
| `/api/books/{id}/revise` | POST | 修订端点 | 自动触发 |
| `/api/books/{id}/audit` | POST | 审计端点 | 审计按钮 |
| `/api/books/{id}/character-growth` | POST | 角色成长规划 | 角色成长按钮 |
| `/api/books/{id}/emotion-curve` | POST | 情绪曲线设计 | 情绪曲线Tab |
| `/api/books/{id}/agent-performance` | GET | Agent能力画像 | Agent画像Tab |

---

## 环境变量

通过 .env 文件或环境变量设置，不设则用默认值：

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| PIPELINE_MAX_REVISE_ROUNDS | 3 | 最大修订轮数 |
| PIPELINE_MIROFISH_INTERVAL | 5 | MiroFish每N章触发 |
| PIPELINE_MIROFISH_SAMPLE_CHARS | 3000 | MiroFish每章采样字数 |
| PIPELINE_RECENT_SUMMARIES_N | 3 | 前情摘要取最近N章 |
| PIPELINE_DORMANCY_THRESHOLD | 5 | 支线掉线预警章数 |
| PIPELINE_REVIEW_SCORE_FLOOR | 75 | 审查Agent问题汇入阈值 |
| PIPELINE_STYLE_SCORE_FLOOR | 80 | 风格一致性修正阈值 |
| PIPELINE_AUDIT_TENSION_FLOOR | 90 | 审计分低于此值调整张力曲线 |
| PIPELINE_AUDIT_DIMENSION_FLOOR | 85 | 单项维度最低分 |
| PIPELINE_AUDIT_PASS_TOTAL | 95 | 审计通过加权总分 |
| PIPELINE_REVIEW_MODE | adaptive | 审查模式：all/light/minimal/adaptive |
| PIPELINE_REVIEW_FORCE_SCORE | 70 | V6：低于此分触发全量审查 |
| PIPELINE_REVIEW_FORCE_WINDOW | 3 | V6：检查最近N章的分数 |
| CORS_ALLOW_ORIGINS | localhost | CORS白名单（逗号分隔） |
| LLM_FALLBACK_CHAIN | deepseek | 降级链：deepseek,claude,openai |
| WS_ENABLED | true | WebSocket进度推送 |

---

## 迭代备忘

### 服务器注意事项

```bash
# ❌ 不要用 base64 -w0 传大文件到shell变量
# ✅ 用 Python urllib 直接调用 GitHub Contents API

# ❌ git push 经常卡死或报 GnuTLS recv error (-110)
# ✅ 用 GitHub Contents API 逐文件上传

# ❌ sed -i 处理中文会乱码
# ✅ 用 Python pathlib 的 read_text/replace/write_text
```

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
    print(f" ✅ {filepath} → {commit}")
    time.sleep(1.5)  # 防止速率限制

# 使用示例
with open("dramatica_flow_web_ui.html", "r") as f:
    upload("dramatica_flow_web_ui.html", f.read(), "更新Web UI")
```

### Token 获取方法

- 打开 [https://github.com/settings/tokens](https://github.com/settings/tokens)
- 点「Generate new token (classic)」
- Note 填 "dramatica-flow-v7-迭代"
- 勾选 repo 权限（第一个勾）
- 点「Generate token」
- 复制 ghp_xxxxx 发给 AI

⚠️ **AI 推完代码后必须立刻 revoke 这个 token！** 因为 token 会出现在聊天记录里，不安全。

### 每次迭代流程

1. 把本文件 `PROJECT_HANDOFF.md` 发给 AI。它就能读懂整个项目。
2. 如果有新的参考资料（比如运行日志、审计报告、MiroFish测试报告、Token消耗报告），也一起发。
3. AI 读交接文档 → 理解项目
4. AI 在服务器上修改代码
5. AI 用 GitHub API 逐文件推送
6. AI 更新交接文档
7. AI 告诉你推完了
8. **Revoke token**（推完后立刻做！）
9. 本地拉取最新代码：

```bash
cd dramatica-flow-enhanced-v7
git fetch origin
git reset --hard origin/main
```

---

## V7 未来方向

| 优先级 | 方向 | 说明 |
|--------|------|------|
| P0 | 端到端测试 | 部署后实际跑一遍完整流程，验证所有端点 |
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
| LLM | DeepSeek API（默认）/ Ollama（本地免费）/ Claude / GPT-4 |
| 前端 | 单文件 HTML（暗色主题） |
| 校验 | Pydantic v2 |

---

本文档由AI自动生成。下次迭代时，把本文件发给AI即可快速理解整个项目。
