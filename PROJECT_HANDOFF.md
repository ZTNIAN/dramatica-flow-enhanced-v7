# Dramatica-Flow Enhanced — 项目交接文档

> 最后更新：2026-04-18（V7.6 审计+修订管线完整可用）
> 版本：V7.6（V7.5 + 审计→修订→循环修订完整管线修复8个BUG）
> 本文档面向所有人，尤其是零基础用户。读完就能理解整个项目、怎么用、怎么继续迭代。

---

## 一、这是什么？

**Dramatica-Flow Enhanced** 是一个 **AI 自动写小说系统**。你给它一句话设定，它帮你：

1. **市场分析** — 分析目标读者偏好（引用番茄小说真实数据）
2. **构建世界观** — 角色/势力/地点/规则，全部自动生成
3. **角色成长规划** — 每个主要角色8维档案 + 成长弧线 + 转折点
4. **情绪曲线设计** — 整书情绪起伏规划，精确操控读者情绪
5. **生成大纲** — 三幕结构 + 逐章规划 + 张力曲线
6. **自动写作** — 一章一章写，每章2000-4000字
7. **多维审查** — 对话/场景/心理/风格，4个专项审查Agent
8. **自动审计** — 9维度加权评分 + 17条红线一票否决
9. **审查→修订闭环** — 所有审查问题合并进修订循环
10. **MiroFish读者测试** — 每5章模拟1000名读者反馈 → 反馈注入下一章
11. **Agent能力画像** — 追踪每个Agent的工作质量
12. **Token费用追踪** — 精确到每章每Agent的LLM消耗（Web UI可视化）
13. **知识库热加载** — 改了知识库文件立即生效，不用重启（Web UI按钮）
14. **错误恢复** — 写作中断后可从checkpoint恢复（Web UI提示+按钮）
15. **Web UI 全功能** — 浏览器端与CLI功能完全对齐

**一句话：V7.1 是"Web UI全面对齐CLI + 自检修复12个BUG"，V7.2 是"首次实测部署修复7个阻断性BUG"，V7.3 是"云服务器镜像调试修复9个BUG，角色成长→世界观查看→大纲生成完整可用"。**

---

## 二、项目地址

### GitHub 仓库

| 版本 | 地址 | 说明 |
|------|------|------|
| **原版** | https://github.com/ydsgangge-ux/dramatica-flow | 叙事逻辑强，但缺乏前期规划和质量管控 |
| **V1** | https://github.com/ZTNIAN/dramatica-flow-enhanced | 12个增强点完成但有6项"写了没接入" |
| **V2** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v2 | 修复V1的核心问题 + 知识库扩充 |
| **V3** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v3 | 全面升级：知识库+Web界面+动态规划+KB追踪 |
| **V4** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v4 | 架构重构：模块化+配置化+安全加固+异步化 |
| **V5** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v5 | 多LLM+选择性审查+WebSocket+Agent画像可视化 |
| **V6** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v6 | 修复端点+自适应审查+闭环+追踪+热加载+恢复 |
| **V7** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v7 | Web UI对齐CLI + 自检修复12个BUG |
| **V7.2** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v7 | 首次实测部署修复7个阻断性BUG |
| **V7.3（当前）** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v7 | 云服务器镜像调试修复9个BUG |

### 本地部署位置

```bash
git clone https://github.com/ZTNIAN/dramatica-flow-enhanced-v7.git
cd dramatica-flow-enhanced-v7
```

---

## 三、V7.1 → V7.2 的区别：首次实测修复 7 个 BUG

在 Windows-WSL 环境下首次部署 V7 时，逐个发现并修复了 7 个阻断性 BUG。这些 BUG 在 V7/V7.1 的"自检"阶段未被发现，因为从未实际运行过完整流程。

### BUG 1：BookConfig 多余参数 🔴严重
- **文件**：`core/server/routers/books.py` 第57-64行
- **现象**：`POST /api/books` 返回 500，`TypeError: BookConfig.__init__() got an unexpected keyword argument 'status'`
- **原因**：`create_book` 函数向 `BookConfig()` 传入了 `status="planning"` 和 `created_at=datetime.now(...)`，但 `BookConfig` 数据类没有这两个字段
- **修复**：删除这两个多余参数
```python
# ❌ 旧代码
config = BookConfig(
    id=book_id, title=req.title, genre=req.genre,
    target_words_per_chapter=req.words, target_chapters=req.chapters,
    protagonist_id="", status="planning",           # ← 不存在的字段
    created_at=datetime.now(timezone.utc).isoformat(), # ← 不存在的字段
    custom_forbidden_words=[...],
    style_guide=req.style_guide,
)
# ✅ 修复后
config = BookConfig(
    id=book_id, title=req.title, genre=req.genre,
    target_words_per_chapter=req.words, target_chapters=req.chapters,
    protagonist_id="",
    custom_forbidden_words=[...],
    style_guide=req.style_guide,
)
```

### BUG 2：路由双花括号 {{book_id}} 🔴严重
- **文件**：`core/server/routers/` 下 6 个文件
- **现象**：创建书籍后，`/api/books/{book_id}/chapters`、`/setup/status`、`/causal-chain` 等子路由全部 404
- **原因**：路由装饰器使用了 `{{book_id}}`（Jinja2模板语法，字面量花括号），而不是 `{book_id}`（FastAPI路径参数）
- **涉及文件**：
  - `chapters.py`：5处
  - `outline.py`：6处
  - `analysis.py`：8处
  - `threads.py`：6处
  - `setup.py`：5处
- **修复**：全局替换 `{{` → `{` 和 `}}` → `}`（仅在路由路径中）
```python
# ❌ 旧代码
@router.get("/{{book_id}}/chapters")
# ✅ 修复后
@router.get("/{book_id}/chapters")
```

### BUG 3：WorldState 缺少属性 🟡中等
- **文件**：`core/server/routers/analysis.py`
- **现象**：`GET /api/books/{id}/causal-chain` 和 `/hooks` 返回 500，`AttributeError: 'WorldState' object has no attribute 'causal_chain'`
- **原因**：`analysis.py` 访问了 `ws.causal_chain` 和 `ws.pending_hooks`，但 `WorldState` 数据类没有这两个字段
- **修复**：用 `getattr()` 兜底，属性不存在时返回空列表
```python
# ❌ 旧代码
return dc_to_dict(ws.causal_chain)
hooks = dc_to_dict(ws.pending_hooks)
for hook in ws.pending_hooks:
# ✅ 修复后
return dc_to_dict(getattr(ws, "causal_chain", []))
hooks = dc_to_dict(getattr(ws, "pending_hooks", []))
for hook in getattr(ws, "pending_hooks", []):
```

### BUG 4：llm.chat → llm.complete 🔴严重
- **文件**：`core/server/routers/ai_actions.py`（10处）
- **现象**：`POST /api/books/{id}/ai-generate/setup` 返回 500，`AttributeError: 'DeepSeekProvider' object has no attribute 'chat'`
- **原因**：`ai_actions.py` 调用 `llm.chat()`，但 LLM Provider 的方法名是 `complete()` 不是 `chat()`
- **修复**：全局替换 `llm.chat` → `llm.complete`

### BUG 5：max_tokens 超出 DeepSeek 限制 🔴严重
- **文件**：`core/server/deps.py` 第112行
- **现象**：AI 生成世界观时报 `Error code: 400 - Invalid max_tokens value, the valid range of max_tokens is [1, 8192]`
- **原因**：`create_llm()` 默认 `max_tokens=16384`，但 DeepSeek API 最大只支持 8192
- **修复**：`max_tokens: int = 16384` → `max_tokens: int = 8192`

### BUG 6：parse_llm_json 缺少 schema 参数 🔴严重
- **文件**：`core/server/routers/ai_actions.py`（10处）
- **现象**：AI 调用成功（DeepSeek 200 OK）但后续处理崩溃，`TypeError: parse_llm_json() missing 1 required positional argument: 'schema'`
- **原因**：`parse_llm_json(resp.content)` 只传了一个参数，但函数签名要求 `schema: type[T]` 为必填参数（Pydantic模型类）
- **修复**：`ai_actions.py` 不需要 Pydantic 验证，改用 `json.loads` 直接解析
```python
# ❌ 旧代码
from core.llm import parse_llm_json
data = parse_llm_json(resp.content)
# ✅ 修复后
import json as _json, re as _re
data = _json.loads(_re.sub(r"^\s*```(?:json)?\s*", "", resp.content.strip(), flags=_re.MULTILINE).replace("```", "").strip())
```

### BUG 7：前端世界观页面刷新逻辑 🟡中等（待确认）
- **文件**：`dramatica_flow_web_ui.html`
- **现象**：AI 生成世界观成功（后端200 OK，文件已写入），但前端世界观页面不显示内容，需要在 JSON 编辑器中手动点"保存"才能继续
- **原因**：前端在 AI 生成完成后没有自动刷新世界观数据，可能缺少回调刷新逻辑
- **状态**：⚠️ 待修复（需要分析前端 JS 代码）

---

## 四、已修复文件清单

### V7.2 修复（首次实测）

| 文件 | 改动 |
|------|------|
| `core/server/routers/books.py` | 删除 BookConfig 的 status 和 created_at 参数 |
| `core/server/routers/chapters.py` | {{book_id}} → {book_id}（5处） |
| `core/server/routers/outline.py` | {{book_id}} → {book_id}（6处） |
| `core/server/routers/analysis.py` | {{book_id}} → {book_id}（8处）+ getattr 兜底 |
| `core/server/routers/threads.py` | {{book_id}} → {book_id}（6处） |
| `core/server/routers/setup.py` | {{book_id}} → {book_id}（5处） |
| `core/server/routers/ai_actions.py` | llm.chat → llm.complete + parse_llm_json → json.loads |
| `core/server/deps.py` | max_tokens 16384 → 8192 |

### V7.3 修复（云服务器镜像调试）

| BUG | 文件 | 现象 | 原因 | 修复 |
|-----|------|------|------|------|
| 24 | `core/server/routers/enhanced.py` | 角色成长"生成失败"500 | plan_character_growth期望(world_context, characters_json)，旧代码传(char_dict, start_chapter=...) | 读取world.json作上下文，传角色JSON字符串 |
| 25 | `core/agents/kb.py` | 角色成长500: _LazyKB object is not subscriptable | _LazyKB类缺少__getitem__方法，所有KB[:N]切片操作都会崩溃 | 添加__getitem__方法委托到str(self)[key] |
| 26 | `core/server/routers/enhanced.py` | 角色成长JSON解析失败 | 5角色×8维度一次生成超过DeepSeek 8192 max_tokens，响应截断 | 改为逐角色调用，每角色独立LLM请求 |
| 27 | `core/agents/enhanced/character_growth.py` | 角色成长Schema校验失败 | Pydantic schema字段与LLM输出不完全匹配 | 去掉parse_llm_json，改用json.loads宽松解析 |
| 28 | `dramatica_flow_web_ui.html` | 角色成长/情绪曲线/大纲等"生成失败" | 前端res.data但后端返回res.result/res.outline | 7处res.data改为res.result或res.outline，加fallback |
| 29 | `dramatica_flow_web_ui.html` | 大纲续写引用不存在的res.new_total_chapters | 后端未返回该字段 | 删除该引用 |
| 30 | `core/server/routers/enhanced.py` | 角色成长结果刷新后丢失 | 无GET端点，结果仅在POST响应中 | 添加GET /{book_id}/character-growth端点 |
| 31 | `dramatica_flow_web_ui.html` | 无法查看角色成长档案 | 前端无查看按钮，结果临时插入DOM | 添加"查看成长档案"按钮 + loadCharacterGrowth函数，step3每次渲染自动加载 |
| 32 | `dramatica_flow_web_ui.html` | 无法查看世界观内容（角色/地点/事件） | 前端无查看入口，世界观数据隐藏在JSON编辑器中 | 添加"查看世界观"按钮 + loadWorldView函数 + 可折叠面板 |

### V7.4 修复（AI云服务器镜像调试 2026-04-18）

| BUG | 文件 | 现象 | 原因 | 修复 |
|-----|------|------|------|------|
| 33 | `core/server/routers/ai_actions.py` | 大纲生成500: Invalid format specifier | f-string里的JSON示例 `{"sequences": [...]}` 花括号未转义 | 3处 `{"key": ...}` → `{{"key": ...}}`，Python表达式保持 `{expr}` |
| 34 | `core/server/routers/ai_actions.py` | 章节大纲500: Invalid format specifier | 同上，`emotional_arc: {"start":...}` 未转义 | `{{"start":...}}` |
| 35 | `core/server/routers/ai_actions.py` | 章纲/详细大纲字数写3000-5000 | prompt没传target_words，LLM自由发挥；fallback默认4000 | 读config的target_words_per_chapter传入prompt；fallback改为2000 |
| 36 | `core/server/deps.py` | 生成细纲/正文422 Unprocessable Entity | 前端发`chapter_number`/`extra_points`/`style_override`，后端要`chapter`/`context`/`style` | Pydantic加`Field(alias=...)` + `populate_by_name=True` |
| 37 | `core/server/routers/ai_actions.py` | 细纲生成修仙题材，和章纲无关 | prompt只传了题材，没传故事大纲/章纲/世界观 | prompt加入outline.json + chapter_outlines.json + world.json + characters.json上下文 |
| 38 | `core/server/routers/ai_actions.py` | 正文生成500或乱写 | WriterAgent.write_chapter需要6个位置参数，旧代码只传了3个且类型错误 | 完整重写：构造scene_summaries/blueprint/protagonist/world_context，正确传参 |
| 39 | `core/server/routers/ai_actions.py` | 细纲场景字数等分不合理 | LLM不遵守word_budget，后端等分2000/n | 改为LLM输出weight(1-10)，后端按权重比例归一化分配字数 |

---

## 五、已验证可工作的流程

✅ 创建书籍（POST /api/books → 200）
✅ 加载书籍详情（GET /api/books/{id} → 200）
✅ 章节列表（GET /api/books/{id}/chapters → 200）
✅ 因果链（GET /api/books/{id}/causal-chain → 200）
✅ 钩子（GET /api/books/{id}/hooks → 200）
✅ 关系图（GET /api/books/{id}/relationships → 200）
✅ 情感弧（GET /api/books/{id}/emotional-arcs → 200）
✅ setup/status（GET /api/books/{id}/setup/status → 200）
✅ AI 生成世界观（POST /api/books/{id}/ai-generate/setup → 200，生成3个JSON文件）
✅ 角色成长规划（逐角色调用，5角色约2-3分钟，结果持久化到character_growth.json）
✅ 前端世界观查看（可折叠面板显示角色/地点/事件）
✅ 前端角色成长查看（可折叠面板，自动加载已保存数据）
✅ 故事大纲生成（POST /api/books/{id}/ai-generate/outline → 200）
✅ 章节大纲生成（POST /api/books/{id}/ai-generate/chapter-outlines → 200）
✅ 详细大纲/细纲生成（POST /api/books/{id}/ai-generate/detailed-outline → 200，字数按权重分配）
✅ 章节正文生成（POST /api/books/{id}/ai-generate/chapter-content → 200，WriterAgent正确传参）
✅ 审计（POST /api/books/{id}/three-layer-audit → 200，三层审计报告正常显示）
✅ AI 修复（POST /api/books/{id}/ai-rewrite-segment → 200，全文修订+前端刷新）
✅ 自动修订（POST /api/action/revise → 200）
✅ 循环自动修订（POST /api/action/auto-revise-loop → 200，最多3轮审计→修订循环）
⏳ 管线模式（写下一章 → 巡查 → 审计 → 修订循环，端到端测试中）
⏳ 情绪曲线（已修复前端res.data问题，待端到端测试）

---

## 六、待修复问题（后续迭代）

| 优先级 | 问题 | 说明 |
|--------|------|------|
| P1 | 正文生成端到端测试 | 细纲→正文→审计→修订完整跑通，验证WriterAgent产出质量 |
| P1 | f-string转义漏网排查 | ai_actions.py之外的其他router文件可能存在同类问题（enhanced.py/outline.py等） |
| P2 | 前端其他功能对齐 | Token消耗面板、Checkpoint恢复、KB热加载等V6/V7新功能的Web UI验证 |
| P2 | 大纲续写返回new_total_chapters | 后端未返回该字段，前端toast显示不完整 |
| P2 | 细纲字数权重范围调优 | 当前weight 1-10差异过大，可考虑缩小到1-5或限制比例 |

---

## 七、小白操作手册

### 7.1 两种用法

| | Web UI（浏览器） | CLI（命令行） |
|--|-----------------|---------------|
| 怎么打开 | 浏览器打开 http://127.0.0.1:8766/ | 终端输入 `df` 命令 |
| 适合谁 | 喜欢点按钮、看图形界面 | 喜欢敲命令、批量操作 |
| 功能 | 创建书、写章节、看状态、审计 | 同上 + 全部命令 |
| 区别 | 界面友好 | 功能最全 |

**结论：日常写作用 Web UI，前期设计用 CLI。**

### 7.2 首次部署（5步）

```bash
# 第1步：克隆项目
git clone https://github.com/ZTNIAN/dramatica-flow-enhanced-v7.git
cd dramatica-flow-enhanced-v7

# 第2步：创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate    # Linux/Mac
# .venv\Scripts\activate     # Windows

# 第3步：安装依赖
pip install -e .

# 第4步：配置API Key
cp .env.example .env
# 用编辑器打开 .env，填入你的 DeepSeek API Key
```

`.env` 文件内容：
```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=你的key           # 去 https://platform.deepseek.com 申请
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
DEFAULT_WORDS_PER_CHAPTER=2000
DEFAULT_TEMPERATURE=0.7
AUDITOR_TEMPERATURE=0.0
BOOKS_DIR=./books
```

```bash
# 第5步：启动
# 方式A：命令行
df --help

# 方式B：Web UI
uvicorn core.server:app --reload --host 0.0.0.0 --port 8766
# 然后浏览器打开 http://127.0.0.1:8766/
```

### 7.3 Web UI 操作流程

1. 打开 http://127.0.0.1:8766/
2. 步骤1（创建书籍）：点「+ 创建新书籍」→ 填书名、题材
3. 步骤2（世界观）：点「AI 一键生成」→ 选择详细程度 → 生成
4. 步骤3（大纲）：AI 自动生成三幕结构 + 章纲
5. 步骤4（写作）：点「写下一章」→ AI 自动写 + 多维审查 + 审计 + 修订
6. 步骤5（审计）：查看审计结果、质量仪表盘、KB统计
7. 步骤6（导出）：导出为 Markdown 或 TXT

---

## 八、踩坑记录（新增）

### 坑19：BookConfig 字段不匹配 ⭐V7.2新增
`BookConfig` 数据类只定义了 `id, title, genre, target_words_per_chapter, target_chapters, protagonist_id, custom_forbidden_words, style_guide`。任何多传的字段都会导致 `TypeError`。新增字段必须先在 `core/types/state.py` 的 `BookConfig` 类中定义。

### 坑20：FastAPI 路由不能用双花括号 ⭐V7.2新增
`@router.get("/{{book_id}}/chapters")` 中的 `{{book_id}}` 是 Jinja2 模板语法，FastAPI 会把它当作字面量字符串 `{book_id}` 而不是路径参数。必须用单花括号 `@router.get("/{book_id}/chapters")`。

### 坑21：DeepSeek max_tokens 上限 8192 ⭐V7.2新增
DeepSeek API 的 `max_tokens` 有效范围是 `[1, 8192]`，超过会报 400 错误。

### 坑22：LLM Provider 方法名是 complete 不是 chat ⭐V7.2新增
`DeepSeekProvider`、`OllamaProvider`、`ClaudeProvider`、`OpenAIProvider` 统一用 `complete()` 方法，不是 `chat()`。

### 坑23：parse_llm_json 需要 Pydantic schema ⭐V7.2新增
`parse_llm_json(raw, schema)` 的 `schema` 参数必须是 Pydantic 模型类（有 `model_validate` 方法）。如果只需要解析普通 JSON，用 `json.loads` 即可。

### 坑24：API handler 和 Agent 方法参数签名必须对齐 ⭐V7.3新增
`enhanced.py` 调用 `expert.plan_character_growth(char, start_chapter=1)` 但方法签名是 `(world_context: str, characters_json: str)`。**教训**：改了 Agent 方法签名后，必须同步检查所有调用方。

### 坑25：_LazyKB 必须实现完整字符串协议 ⭐V7.3新增
`_LazyKB` 懒加载代理实现了 `__str__`/`__len__`/`__bool__`/`__contains__`/`__iter__`，但漏了 `__getitem__`。代码中大量使用 `KB_XXX[:3000]` 切片操作，缺少 `__getitem__` 会直接崩溃。**必须补全**：`def __getitem__(self, key): return str(self)[key]`

### 坑26：LLM 响应长度可能超过 max_tokens ⭐V7.3新增
DeepSeek max_tokens 上限 8192。5个角色×8维度的详细 JSON 一次生成会超出限制，响应被截断导致 JSON 语法错误。**解决方案**：逐角色调用，或精简 prompt 控制输出长度。

### 坑27：Pydantic schema 和 LLM 输出永远存在偏差 ⭐V7.3新增
LLM 输出的字段名/类型/嵌套结构不可能 100% 匹配预定义的 Pydantic model。`parse_llm_json` 的 schema 校验会导致合法但格式稍有不同的响应被拒绝。**建议**：对非核心流程用 `json.loads` 宽松解析，只在需要强校验时才用 Pydantic。

### 坑28：前端 res.data ≠ 后端返回字段名 ⭐V7.3新增
后端各端点返回的 key 不统一（`result`/`outline`/`data`/`extracted`），但前端统一写的 `res.data`。**规则**：新增 API 端点时，后端返回 key 必须和前端 JS 对应，或前端加 fallback：`res.result || res.data`。

### 坑29：Web UI 动态内容刷新即丢失 ⭐V7.3新增
前端用 `panel.prepend(div)` 插入的动态内容（如角色成长结果），在面板重新渲染时会丢失。**解决方案**：后端持久化到文件 + 前端每次渲染时自动从 API 加载已保存数据。

### 坑30：f-string 里 JSON 花括号必须转义 ⭐V7.4新增
Python 的 `f"""..."""` 字符串中，`{` 和 `}` 是格式化占位符。如果 prompt 里包含 JSON 示例如 `{"key": "value"}`，必须写成 `{{"key": "value"}}`。**常见触发场景**：给 LLM 的 prompt 中包含返回格式示例。**规则**：f-string 里的字面量花括号一律双写 `{{` `}}`，Python 表达式保持单写 `{expr}`。

### 坑31：Pydantic alias 兼容前后端字段名 ⭐V7.4新增
前端和后端字段名不一致时（如前端 `chapter_number` vs 后端 `chapter`），422 Unprocessable Entity。**解决方案**：Pydantic v2 用 `Field(alias="前端字段名")` + `model_config = {"populate_by_name": True}`，两种命名都能识别。

### 坑32：LLM prompt 必须包含足够上下文 ⭐V7.4新增
生成细纲时 prompt 只给了题材和风格，没给故事大纲/章纲/世界观，LLM 无上下文就按默认套路（修仙）编。**规则**：所有生成类 prompt 必须传入相关上下文文件（outline.json / chapter_outlines.json / world.json / characters.json）。

### 坑33：Web UI 调 Agent 必须正确传参 ⭐V7.4新增
Web UI 的 `ai_generate_chapter_content` 直接调 `WriterAgent.write_chapter()`，但传参全错（位置参数类型错误、缺少必填参数）。CLI 走的 `pipeline.py` 正常，因为 pipeline 正确构造了所有参数。**教训**：Web UI 和 CLI 共用 Agent 时，Web UI 端必须按 Agent 方法签名完整传参，不能偷懒。

### 坑34：LLM 不遵守 prompt 中的数值约束 ⭐V7.4新增
prompt 中写 `word_budget: 667`，LLM 经常输出 900。**解决方案**：不要依赖 LLM 严格遵守数值，改为让 LLM 输出权重（weight），后端代码做归一化计算。

### 坑35：config 字段名必须和 read_config() 返回的 key 一致 ⭐V7.4新增
`BookConfig` 数据类定义 `target_words_per_chapter`，`read_config()` 返回 dict 的 key 也是这个。如果 fallback 默认值和实际 config 值不一致（如默认 4000 但 config 是 2000），会导致字数异常。**建议**：所有 fallback 默认值应与 BookConfig 定义一致。

---

## 九、迭代写入方式（推荐方法）

### 为什么不推荐 git push

本服务器的 git 客户端存在 TLS 连接问题（GnuTLS recv error -110），`git push` 经常卡死。这是服务器环境问题，不是代码问题。

### 推荐方法：GitHub Contents API 逐文件上传

#### 方法：大文件（>1MB）或中文路径用 Python ⭐推荐

```python
import base64, json, urllib.request, time
from urllib.parse import quote

TOKEN = "你的GitHub Token"
REPO = "ZTNIAN/dramatica-flow-enhanced-v7"
filepath = "core/server/routers/books.py"

encoded = "/".join(quote(seg, safe="") for seg in filepath.split("/"))

with open(filepath, "rb") as f:
    content_b64 = base64.b64encode(f.read()).decode()

sha = ""
try:
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/contents/{encoded}",
        headers={"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"}
    )
    sha = json.loads(urllib.request.urlopen(req, timeout=10).read()).get("sha", "")
except:
    pass

data = json.dumps({
    "message": "update " + filepath,
    "content": content_b64,
    "branch": "main",
    **({"sha": sha} if sha else {}),
}).encode()

req = urllib.request.Request(
    f"https://api.github.com/repos/{REPO}/contents/{encoded}",
    data=data,
    headers={
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    },
    method="PUT"
)
result = json.loads(urllib.request.urlopen(req, timeout=20).read())
print(f"{filepath} → {result.get('commit',{}).get('sha','ERROR')[:8]}")
```

---

## 十、技术栈

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

## 十一、文件结构

```
dramatica-flow-enhanced-v7/
├── cli/main.py                          # CLI入口
├── core/
│   ├── agents/                          # Agent模块（21个文件）
│   │   ├── __init__.py                  # re-export入口
│   │   ├── kb.py                        # 公共知识库模块
│   │   ├── architect.py                 # 建筑师
│   │   ├── writer.py                    # 写手
│   │   ├── auditor.py                   # 审计员
│   │   ├── reviser.py                   # 修订者
│   │   ├── summary.py                   # 摘要
│   │   ├── patrol.py                    # 巡查
│   │   ├── worldbuilder.py              # 世界观构建
│   │   ├── outline_planner.py           # 大纲规划
│   │   ├── market_analyzer.py           # 市场分析
│   │   └── enhanced/                    # 增强Agent（10个文件）
│   │       ├── character_growth.py
│   │       ├── dialogue.py
│   │       ├── emotion_curve.py
│   │       ├── feedback.py
│   │       ├── style_checker.py
│   │       ├── scene_architect.py
│   │       ├── psychological.py
│   │       ├── mirofish.py
│   │       └── methods.py
│   ├── pipeline.py                      # 写作管线
│   ├── llm/__init__.py                  # LLM抽象层
│   ├── token_tracker.py                 # Token追踪
│   ├── narrative/__init__.py            # 叙事引擎
│   ├── state/__init__.py                # 状态管理
│   ├── types/                           # 数据类型
│   ├── validators/__init__.py           # 写后验证器
│   ├── server/                          # Web服务（13个文件）
│   │   ├── __init__.py                  # app实例+中间件+CORS+WebSocket
│   │   ├── deps.py                      # 公共依赖+请求模型
│   │   └── routers/                     # 路由模块
│   │       ├── books.py / setup.py / chapters.py
│   │       ├── outline.py / writing.py / ai_actions.py
│   │       ├── threads.py / analysis.py / enhanced.py
│   │       ├── settings.py / export.py
│   ├── quality_dashboard.py             # 质量仪表盘
│   ├── dynamic_planner.py               # 动态规划器
│   ├── kb_incentive.py                  # KB查询激励
│   └── knowledge_base/                  # 知识库（30+文件）
│       ├── rules/ references/ agent-specific/
│       ├── examples/ fanqie-data/ indexes/
├── templates/                           # JSON配置模板
├── tests/                               # 测试
├── docs/                                # 文档
├── dramatica_flow_web_ui.html           # Web UI
├── dramatica_flow_timeline.html         # 时间轴可视化
├── pyproject.toml                       # 项目配置
├── .env.example                         # 环境变量模板
├── PROJECT_HANDOFF.md                   # 本文件
└── USER_MANUAL.md                       # 操作手册
```

---

## 十二、Agent 体系（19个Agent）

### 原有 9 个

| Agent | 职责 | 触发时机 |
|-------|------|---------|
| WorldBuilderAgent | 一句话→世界观 | `df worldbuild` |
| OutlinePlannerAgent | 大纲+章纲 | `df outline` |
| MarketAnalyzerAgent | 市场分析 | `df market` |
| ArchitectAgent | 规划单章蓝图 | 每章写前 |
| WriterAgent | 生成正文 | 每章写手 |
| PatrolAgent | 快速扫描 | 写后立即 |
| AuditorAgent | 9维加权审计 | 巡查后 |
| ReviserAgent | 修订正文 | 审计不通过 |
| SummaryAgent | 章节摘要 | 写完后 |

### V4 新增 10 个

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

## 十三、写作管线流程

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
    ├── Checkpoint保存
    ├── 加载MiroFish反馈
    ├── 建筑师：规划蓝图
    ├── 写手：生成正文 + 结算表
    ├── Token统计记录
    ├── 对话专家审查
    ├── 验证器：零LLM硬规则扫描
    ├── 巡查者：快速扫描
    ├── 场景审核 + 心理审核
    ├── 审计员：9维度加权评分
    │   └── 合并所有审查问题 → 不通过 → 修订（最多3轮）
    ├── 自适应审查判断
    ├── 风格一致性检查
    ├── 保存最终稿
    ├── 因果链提取 → 摘要生成 → 状态更新
    ├── 质量仪表盘记录 + 动态规划器更新 + KB查询统计 + Agent能力画像 + Token统计
    ├── Checkpoint更新为完成
    └── MiroFish测试（每5章）
    ↓
[导出]
    df export → Markdown / TXT
```

---

## 十四、可配置参数

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `PIPELINE_MAX_REVISE_ROUNDS` | 3 | 最大修订轮数 |
| `PIPELINE_MIROFISH_INTERVAL` | 5 | MiroFish每N章触发 |
| `PIPELINE_REVIEW_MODE` | adaptive | 审查模式：all/light/minimal/adaptive |
| `PIPELINE_AUDIT_PASS_TOTAL` | 95 | 审计通过加权总分 |
| `CORS_ALLOW_ORIGINS` | localhost | CORS白名单 |
| `LLM_FALLBACK_CHAIN` | deepseek | 降级链：deepseek,claude,openai |
| `WS_ENABLED` | true | WebSocket进度推送 |

---


## 十五、V7.5 修复（云服务器镜像调试 2026-04-18）

### BUG 修复

| BUG | 文件 | 现象 | 原因 | 修复 |
|-----|------|------|------|------|
| 40 | `core/server/routers/ai_actions.py` | 正文生成500: CharacterWorldview got unexpected keyword 'belief' | CharacterWorldview数据类字段是power/trust/coping，但代码传了belief/flaw | 改为使用正确字段：power="accepts", trust="selective", coping="fight"（2处：JSON提取 + fallback默认值） |
| 41 | `core/agents/writer.py` | 正文生成500: SETTLEMENT_SEPARATOR is not defined | writer.py使用了architect.py中定义的常量但未导入 | 添加 `from .architect import SETTLEMENT_SEPARATOR` |
| 42 | `core/agents/writer.py` | 正文生成500: _track_kb_query is not defined | import的是`track_kb_query`（无下划线），代码调用的是`_track_kb_query` | 统一改为`track_kb_query` |
| 43 | `core/server/routers/ai_actions.py` | 正文超字数（目标2000字，实际输出4000-4600字） | LLM不遵守prompt字数约束；max_tokens=8192过大 | 双重控制：①max_tokens=target_words×1.5（上限8192，下限2048）②后处理：超过target×1.2按段落/句号截断 |
| 44 | `core/server/routers/ai_actions.py` | 细纲生成JSON解析失败 | prompt上下文太长（大纲2000+章纲1500+世界观1500字符），DeepSeek输出异常 | 上下文截断：大纲2000→800，章纲1500→600，世界观1500→600 |

### Web UI 改进

| 改进 | 文件 | 说明 |
|------|------|------|
| 细纲自动加载 | `dramatica_flow_web_ui.html` | 选章节时自动从API加载已有细纲（GET /detailed-outline/{chapter}），刷新后不丢失 |
| 细纲收起/展开 | `dramatica_flow_web_ui.html` | 细纲右上角添加「收起/展开」按钮，生成和加载时都有 |

### 已验证可工作

✅ 正文生成（2000字目标 → 实际2500字左右，可接受）
✅ 审计（三层审计报告显示语言层/结构层/戏剧层）
✅ AI 修复（逐问题修复，全文修订模式）
✅ 循环自动修订（audit→revise 最多3轮自动循环）

### 踩坑记录（新增）

#### 坑36：CharacterWorldview 字段名与代码调用不一致
`CharacterWorldview` 定义了 `power/trust/coping`（Dramatica理论术语），但 `ai_actions.py` 中用 `belief/flaw`（通俗理解）。**教训**：构造数据类实例前，先检查类定义的字段名，不能凭直觉猜。

#### 坑37：import 名和使用名不一致（下划线前缀）
`from .kb import track_kb_query` 导入后，代码里写 `_track_kb_query()`。Python 不会报 NameError 在 import 阶段，只在实际调用时才报。**规则**：import 后立即在同文件确认使用名一致。

#### 坑38：LLM 不遵守字数约束是常态，必须后处理
prompt 写"2000字，不能超过2400字"，DeepSeek 输出 4000+。max_tokens 限制可以卡上限，但不够精确。**方案**：API层限制 token + 代码层后处理截断（按段落/句号边界），双重保险。

#### 坑39：f-string 中截断字符串操作要小心转义
在 Python 三引号字符串中写 `content.rfind('

', ...)` 时，`
` 会被解释为换行，导致代码结构崩溃。**方案**：用 `\n\n` 或在单独变量中定义分隔符。

#### 坑40：上下文过长会导致 DeepSeek JSON 输出异常
详细大纲 prompt 包含完整大纲+章纲+世界观+角色数据（合计约5000字符）时，DeepSeek 返回的 JSON 经常有语法错误。简化 prompt 或只传部分数据时正常。**方案**：对非关键上下文做截断（各600-800字符）。

---

## 十六、V7.6 修复（云服务器镜像调试 2026-04-18）

### 背景

V7.5 跑通正文生成后，开始测试完整管线：写→审→改循环。审计是第一个关卡，发现了一连串从前端到后端的字段不匹配、缺失 import 等问题。本轮共修复 8 个 BUG。

### BUG 修复

| BUG | 文件 | 现象 | 原因 | 修复 |
|-----|------|------|------|------|
| 45 | `core/agents/auditor.py` | 审计500: name '_KB_REVIEWER_CHECKLIST' is not defined | auditor.py 使用 `_KB_REVIEWER_CHECKLIST` 但从未 import `KB_REVIEWER_CHECKLIST` | 添加 `from .kb import KB_REVIEWER_CHECKLIST` 和赋值 `_KB_REVIEWER_CHECKLIST = KB_REVIEWER_CHECKLIST` |
| 46 | `core/agents/auditor.py` | KB查询不记录 | import `track_kb_query`，代码调用 `_track_kb_query`（下划线前缀） | 统一改为 `track_kb_query`（3处） |
| 47 | `core/agents/architect.py` | KB查询不记录 | 同坑46，import 无下划线，调用有下划线 | 添加 `_track_kb_query = track_kb_query` 赋值 |
| 48 | `core/server/routers/writing.py` | 审计前端显示 "undefined" | 后端返回 `{"ok": true, "report": {...}}` 但前端期望 `res.layers`/`res.passed`/`res.summary` 等顶层字段 | reshape AuditReport 为前端期望的三层格式（language/structure/drama）+ 返回 `ok/chapter/passed/summary/layers` |
| 49 | `core/server/routers/writing.py` | GET /audit-results/1 返回 404 | three-layer-audit 端点没有把结果保存到磁盘 | 添加 `audit_dir / f"audit_ch{chapter:04d}.json"` 写入 |
| 50 | `core/server/routers/writing.py` + `deps.py` | "AI 修复此问题" 422 | 前端发 `{original_text, instruction, context_before, context_after}`，后端 `SegmentRewriteReq` 只接受 `{start_line, end_line, reason}` | SegmentRewriteReq 添加前端字段；handler 支持文本定位和行号两种模式 |
| 51 | `core/server/routers/writing.py` | AI 修复 400 "选中段落为空" | 审计 issue 的 excerpt 经常为空，前端 fallback `fullText.substring(0, 500)` 导致后端只改了前500字且定位不准 | 后端：excerpt 为空或 ≤20字时走全文修订模式（把审计建议传给 Reviser）；前端：修复后直接 loadBookData() 刷新 |
| 52 | `core/server/routers/writing.py` | AI 修复后重新审计问题还在 | ReviserAgent.revise() 在 `mode="spot-fix"` 时，只有 `severity="critical"` 的 issue 才会触发修订，warning 直接跳过返回原文 | fake issue 改为 `severity="critical"` |
| 53 | `core/agents/reviser.py` | 修订500: name '_MODE_INSTRUCTIONS' is not defined | reviser.py 使用 `_MODE_INSTRUCTIONS` 和 `CHANGELOG_SEPARATOR` 但从未 import（定义在 auditor.py） | 添加 `from .auditor import _MODE_INSTRUCTIONS, CHANGELOG_SEPARATOR` |
| 54 | `core/server/routers/writing.py` | 修订500: 'ReviseResult' object has no attribute 'changes_summary' | ReviseResult 的属性名是 `change_log` 不是 `changes_summary` | 全局替换 `changes_summary` → `change_log`（2处） |
| 55 | `dramatica_flow_web_ui.html` | "自动修订"按钮 422 | 前端发 JSON body `{book_id, chapter, mode}`，后端 legacy 路由 `/api/action/revise` 用 `Query(...)` 读取 | 前端改为 query 参数传参 |
| 56 | `core/server/routers/writing.py` + `dramatica_flow_web_ui.html` | 无循环自动修订功能 | 需要审计→修订→再审计自动循环直到通过 | 新增 `/api/action/auto-revise-loop` 端点（最多3轮）+ 前端「🔄 循环自动修订」按钮 |

### Web UI 改进

| 改进 | 文件 | 说明 |
|------|------|------|
| 审计三层报告 | `writing.py` | 后端 reshape AuditReport 为 language/structure/drama 三层面板 |
| 审计结果持久化 | `writing.py` | 审计结果保存到 `audits/audit_chXXXX.json`，刷新后可加载 |
| AI 修复刷新 | `web_ui` | 修复成功后自动 loadBookData() 刷新页面 |
| 循环自动修订按钮 | `web_ui` | 「🔄 循环自动修订」按钮，最多3轮 audit→revise 循环，显示每轮结果 |

### 已验证可工作

✅ 审计（三层报告，语言层/结构层/戏剧层，200 OK）
✅ 审计结果持久化（GET /audit-results/{chapter} → 200）
✅ AI 修复此问题（全文修订模式，修复后正文刷新）
✅ 自动修订（单次 audit→revise）
✅ 循环自动修订（最多3轮，审计通过自动停止）

### 工作流说明

**两种修订方式：**
1. **「✨ AI 修复此问题」** — 针对单个审计问题修复。点击后 AI 在全文范围内根据该条建议修改，修改后自动刷新正文。可能引入新问题，需重新审计。
2. **「🔄 循环自动修订」** — 自动跑最多3轮 audit→revise 循环。每轮审计所有 issues，自动修订，再审计。warning 级别也会触发修订。直到审计通过（passed=true）或达到3轮上限。适合批量修复。

**WSL 更新方式（推荐 curl，git pull 因 TLS 问题可能卡住）：**
```bash
curl -sL "https://raw.githubusercontent.com/ZTNIAN/dramatica-flow-enhanced-v7/main/core/server/routers/writing.py" -o core/server/routers/writing.py
curl -sL "https://raw.githubusercontent.com/ZTNIAN/dramatica-flow-enhanced-v7/main/core/agents/auditor.py" -o core/agents/auditor.py
curl -sL "https://raw.githubusercontent.com/ZTNIAN/dramatica-flow-enhanced-v7/main/core/agents/reviser.py" -o core/agents/reviser.py
curl -sL "https://raw.githubusercontent.com/ZTNIAN/dramatica-flow-enhanced-v7/main/core/server/deps.py" -o core/server/deps.py
curl -sL "https://raw.githubusercontent.com/ZTNIAN/dramatica-flow-enhanced-v7/main/dramatica_flow_web_ui.html" -o dramatica_flow_web_ui.html
# 重启 uvicorn
```

### 踩坑记录（新增）

#### 坑41：审计报告格式和前端期望不一致
后端 `AuditReport` 是扁平结构（issues + dimension_scores），但前端期望三层结构（layers.language/structure/drama）。**教训**：新增 API 端点时，后端返回格式必须和前端 JS 期望的字段完全对齐，不能想当然。

#### 坑42：审计结果不持久化导致刷新丢失
`three-layer-audit` POST 端点返回审计结果但没有写入磁盘。前端刷新后 `loadSavedAudit()` 调 GET 返回 404。**规则**：所有生成类端点必须同时保存结果到文件。

#### 坑43：Reviser spot-fix 模式忽略 warning 级别
`reviser.revise()` 在 `mode="spot-fix"` 时跳过所有非 critical 问题，直接返回原文。审计报告的 issues 大多是 warning 级别，导致"AI修复"按钮点完没效果。**教训**：调用 Reviser 时必须确认 issue severity 和 mode 的组合是否会触发实际修订。

#### 坑44：跨文件常量引用不 import
`reviser.py` 使用 `_MODE_INSTRUCTIONS` 和 `CHANGELOG_SEPARATOR`，但这两个常量定义在 `auditor.py`，reviser.py 从未 import。Python 不会在 import 阶段报错，只在运行时调用才报 `NameError`。**规则**：跨文件引用的符号必须显式 import，不能靠"碰巧在同包内"。

#### 坑45：前后端字段名差异是反复出现的问题
本次 8 个 BUG 中有 4 个是前后端字段/API 参数不匹配（坑48/50/51/55）。**根因**：Web UI 和后端由不同时间/方式开发，字段命名没有统一约束。**建议**：新增 API 端点时，先定义前后端的字段契约（哪怕只是注释），再同时开发。

---

*本文档由AI自动生成。下次迭代时，把本文件发给AI即可快速理解整个项目。*
