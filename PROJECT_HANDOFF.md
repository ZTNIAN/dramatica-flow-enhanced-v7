# Dramatica-Flow Enhanced — 项目交接文档

> 最后更新：2026-04-19（V7.18 2000字精写改造：从源头优化章节结构，修复2个BUG+1项架构改进）
> 版本：V7.18（V7.15 + 细纲解析修复 + 上下文恢复 + 截断优化 + 2000字精写改造）
> 本文档面向所有人，尤其是零基础用户。读完就能理解整个项目、怎么用、怎么继续迭代。

## ⚠️ 核心设计哲学（必读）

**从源头优化，而不是后处理截断。** 用户不在乎token消耗（DeepSeek便宜），要的是工具质量和作品质量。

- 番茄小说每章目标 **2000字左右**
- 如果截断怎么调都控制不好字数，说明**源头的章节结构设计有问题**——不是输出端砍，而是输入端控
- 章纲控制场景数和节拍数 → 细纲按场景展开 → 正文自然收敛到目标字数
- 不要一直改截断逻辑，回到 prompt 层面控制 LLM 的输出范围。治本 > 治标

---

## ⚠️ WSL 更新协议（必读）

> **绝对不要 `git pull` 或 `git reset --hard`，会导致本地修改丢失（.env、已有书籍数据、本地配置等）。**

**正确方式：只更新改动的文件，用 urllib 从 GitHub 下载覆盖：**

```bash
cd ~/dramatica-flow-enhanced-v7
python3 -c "
import urllib.request
for f in [
    # ← 在这里填本次改动的文件列表，例如：
    # 'core/server/routers/writing.py',
    # 'dramatica_flow_web_ui.html',
]:
    url = f'https://raw.githubusercontent.com/ZTNIAN/dramatica-flow-enhanced-v7/main/{f}'
    data = urllib.request.urlopen(url, timeout=30).read()
    with open(f, 'wb') as fh:
        fh.write(data)
    print(f'{f}: {len(data)} bytes')
"
# 重启 uvicorn
```

**每次更新时，我会列出具体改了哪几个文件，你照着填就行。**

**为什么不能 git pull：**
- `.env` 含 API Key，会被覆盖
- `books/` 目录含已创建的书籍和写作数据，会被覆盖
- `.venv/` 虚拟环境会冲突
- `__pycache__/` 编译缓存会导致合并冲突
- 之前试过 `git stash + git reset --hard`，结果丢了大量本地状态

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
| **V7.3** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v7 | 云服务器镜像调试修复9个BUG |
| **V7.4** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v7 | 正文生成+细纲+字数控制修复7个BUG |
| **V7.5** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v7 | 正文端到端+细纲加载修复5个BUG |
| **V7.6** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v7 | 审计+修订管线完整可用，修复12个BUG |
| **V7.7** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v7 | 修订质量+循环修订增强，修复4个BUG+3项改进 |
| **V7.8** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v7 | 正文生成质量修复：蓝图剥离+场景覆盖+字数分配，修复3个BUG |
| **V7.9（当前）** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v7 | 场景覆盖彻底修复：逐场景LLM调用，修复3个BUG+回退2个无效改动 |
| **V7.10** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v7 | 场景间去重+叙事手法注入+结尾钩子注入，修复3个BUG |
| **V7.11** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v7 | 全链路数据流修复：setup→state同步+世界观注入+场景字数控制+去重保护+强制节拍，修复6个BUG+4轮迭代 |
| **V7.12** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v7 | 场景级截断+结尾钩子修复：移除钩子注入+逐场景max_tokens+节拍进度标记，修复3个BUG |
| **V7.13** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v7 | 场景解析fallback+钩子后处理：从字符串提取场景+共享钩子拼接路径，修复2个BUG |
| **V7.14** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v7 | 截断生效+全局截断修复+debug日志：场景截断生效+全局按***截断+3场景5节拍全覆盖，修复2个BUG |
| **V7.15** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v7 | 细纲JSON解析修复：上下文2000/1500/1500→600/400/400 + JSON补全括号 + max_tokens=4096，修复1个BUG |
| **V7.16** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v7 | 细纲解析增强：max_tokens=8192 + 章纲int()类型统一 + 上下文恢复到V7.15前 + JSON增强解析+日志，修复2个BUG |
| **V7.17** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v7 | 截断优化：容忍度1.2→1.5 + 搜索范围扩大 + 按段落/句号边界截断，修复1个BUG |
| **V7.18（当前）** | https://github.com/ZTNIAN/dramatica-flow-enhanced-v7 | 2000字精写改造：从源头优化——章纲2场景×3节拍 + 细纲2场景×2-3节拍 + 截断1.3x + writer字数铁律，1项架构改进 |

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
✅ AI 修复（只写 draft，删除 final，字数控制，前端正确刷新）
✅ 自动修订（只写 draft，字数控制，需手动确认最终稿）
✅ 循环自动修订（最多5轮，最小改动约束，批量修复所有issues）
✅ 正文后处理剥离蓝图/细纲元信息（4轮正则过滤）
✅ 审计红线检测正文中的规划元信息（第6条红线 + 特别检查项）
⏳ 正文完整覆盖细纲全部场景（4个场景全部写成小说正文，待验证）
⏳ 场景字数按细纲分配（待验证）
⏳ 管线模式（写下一章 → 巡查 → 审计 → 修订循环，端到端测试中）
⏳ 情绪曲线（已修复前端res.data问题，待端到端测试）

---

## 六、待修复问题（后续迭代）

| 优先级 | 问题 | 说明 |
|--------|------|------|
| P1 | 正文场景覆盖完整性 | 细纲4个场景必须全部写成完整小说正文，不能跳过或压缩成大纲摘要 |
| P1 | 场景字数按细纲分配 | 每个场景的字数应接近细纲标注的目标值（word_budget） |
| P1 | 审计对正文质量的把控 | 审计应能发现场景缺失、内容不完整等结构性问题 |
| P1 | f-string转义漏网排查 | ai_actions.py之外的其他router文件可能存在同类问题（enhanced.py/outline.py等） |
| P2 | 前端其他功能对齐 | Token消耗面板、Checkpoint恢复、KB热加载等V6/V7新功能的Web UI验证 |
| P2 | 大纲续写返回new_total_chapters | 后端未返回该字段，前端toast显示不完整 |
| P2 | 细纲字数权重范围调优 | 当前weight 1-10差异过大，可考虑缩小到1-5或限制比例 |

---



## 十七、V7.7 修复（云服务器镜像调试 2026-04-18）

### 背景

V7.6 跑通了审计→修订→循环修订管线，但用户实测发现两个严重问题：1）AI修复后前端显示内容不变（实际改了但读不到）；2）AI修复后字数失控（目标2000字输出4337字）。另外用户反馈"逐个AI修复问题越修越多"，揭示了修订策略的根本问题。本轮修复4个BUG + 3项改进。

### BUG 修复

| BUG | 文件 | 现象 | 原因 | 修复 |
|-----|------|------|------|------|
| 57 | `core/server/routers/writing.py` | AI修复成功但前端显示不变 | `ai-rewrite-segment` 只 `save_draft()`，但 GET /chapters 优先读 `read_final()`，旧 final 未被清除 | 修订后删除旧 final 文件，前端 fallback 到显示修订后的 draft |
| 58 | `core/server/routers/writing.py` | AI修复后字数4337字（目标2000） | Reviser 无字数约束，LLM 自由发挥 | 修订后增加字数后处理：超过 target×1.2 按段落/句号截断（3个修订入口统一处理） |
| 59 | `core/server/routers/writing.py` | 循环自动修订 ImportError | `from core.agents.auditor import AuditSeverity` 但 `AuditSeverity` 从未定义 | 删除未使用的 import |
| 60 | `core/server/routers/writing.py` | 自动修订/循环修订自动升 final | `revise` 和 `auto-revise-loop` 都 `save_draft()` + `save_final()`，用户失去手动确认机会 | 改为只 save_draft()，删除旧 final，需用户手动"确认最终稿" |

### 改进

| 改进 | 文件 | 说明 |
|------|------|------|
| Reviser 最小改动约束 | `core/agents/reviser.py` | prompt 新增5条硬约束：只改问题句、未被指出的一字不动、不"顺便优化"；system message 同步强化 |
| 循环修订 3→5 轮 | `writing.py` + `web_ui` | `max_rounds` 默认 3→5，给更多修复机会 |
| UI 引导提示 | `dramatica_flow_web_ui.html` | 多问题时显示"建议用循环修订"提示；单个修复按钮加 hover 说明 |

### 修订策略改进说明

**问题根因**：逐个点击"AI修复此问题"时，每次都是全文重写。修复第1个问题后文本变了，第2个问题的 excerpt 定位失效，而且 LLM 每次重写都可能"顺便"改其他地方，引入新问题。

**V7.7 改进后的两种修订方式：**

1. **「✨ AI 修复此问题」**（单问题精准修复）
   - 适合：只有1-2个小问题
   - 逻辑：看到全部问题 → AI一次性全部修复 → 最小改动约束限制幅度
   - 约束：只改问题涉及的句子，其余一字不动

2. **「🔄 循环自动修订」**（多问题批量修复）⭐推荐
   - 适合：问题较多（3个以上）
   - 逻辑：审计 → 全部issues一次性传给AI → 修订 → 再审计 → 最多5轮
   - 每轮都读最新内容重新审计，不会定位失效

**工作流建议：**
```
写完一章 → 确认最终稿 → 审计
  → 通过 ✅ → 继续下一章
  → 不通过 → 点「🔄 循环自动修订」（别逐个点AI修复）
    → 审计通过 ✅ → 检查内容 → 确认最终稿
    → 还有问题 → 再跑一轮
```

### 已验证可工作

✅ AI 修复此问题（只写 draft，删 final，前端正确显示修订内容）
✅ 自动修订（只写 draft，需手动确认最终稿）
✅ 循环自动修订（5轮，最小改动约束，字数控制）
✅ 字数控制（修订后不超过 target×1.2）

### 踩坑记录（新增）

#### 坑46：read_final 优先级导致修订"隐形"
GET /chapters 返回 `read_final() or read_draft()`，final 优先。如果修订只写 draft 不删 final，前端永远显示旧 final。**规则**：修订类端点必须同时处理 final 文件（删除或更新），不能只写 draft 就完事。

#### 坑47：LLM 修订会"顺便优化"导致越修越多
Reviser 的 spot-fix prompt 只说"只修改有问题的句子/段落"，但 LLM 经常"顺便"优化其他段落。**解决方案**：在 prompt 中用多条硬约束强调最小改动，在 system message 中明确禁止"顺便优化"。

#### 坑48：逐个修复 vs 批量修复的根本差异
逐个修复每次全文重写，N个问题需要N次重写，每次都有引入新问题的风险。批量修复一次重写解决所有问题，只引入一次风险。**规则**：多个问题永远用批量修复（循环修订），单个问题才用逐个修复。

#### 坑49：不存在的 import 是运行时炸弹
`AuditSeverity` 在 auditor.py 中从未定义（只在 `from __future__ import annotations` 下作为类型注解字符串存在），但 auto-revise-loop 直接 `from core.agents.auditor import AuditSeverity`。这个 import 在该代码路径首次执行前不会暴露。**规则**：新增 import 后立即验证目标模块确实导出了该符号。

## 十八、V7.8 修复（云服务器镜像调试 2026-04-18）

### 背景

V7.7 审计→修订管线可用，但用户实测正文生成存在3个严重问题：1）LLM 把写前蓝图/细纲内容原样写进正文；2）细纲有4个场景，正文只写了2个就停了；3）审计只报2个 warning，没有发现蓝图混入和场景缺失。本轮修复3个BUG + 2项改进。

### BUG 修复

| BUG | 文件 | 现象 | 原因 | 修复 |
|-----|------|------|------|------|
| 61 | `core/agents/writer.py` | 正文中出现"写前蓝图"段落（核心冲突/情感旅程/结尾钩子等元信息） | prompt 给了蓝图信息但没有告诉 LLM 不要在输出中复述；LLM 把 prompt 结构当模板 | prompt 末尾加铁律（禁止输出规划信息）+ 后处理4轮正则剥离（写前蓝图标题/元叙述引用/细纲格式/核心冲突段落） |
| 62 | `core/server/routers/ai_actions.py` | 正文只写了细纲4个场景中的前2个，后2个场景缺失或极度压缩 | scene_summaries 只提取了 beats 描述，没有场景名和 word_budget 字数标注；LLM 不知道每个场景该写多少字，把 token 全花在前两个场景 | scene_summaries 构造时加入场景名 + （目标XX字）标注，LLM 看到每个场景的字数目标 |
| 63 | `core/agents/auditor.py` | 审计没有发现正文中混入了蓝图元信息，只报了2个 minor warning | 17条红线没有"正文中出现写作规划元信息"这条；审计 prompt 没有要求专项检查蓝图混入 | 红线新增第6条 + 审计 prompt 加"特别检查项"段落，要求优先扫描蓝图格式 |

### 改进

| 改进 | 文件 | 说明 |
|------|------|------|
| world_context 精简 | `ai_actions.py` | world.json 和 characters.json 的注入量从 2000→1200 字，减少 prompt 开销，留给输出更多 token |
| prompt 指令精简 | `writer.py` | anti-dump 铁律从5行缩到1行，系统提示红线精简，避免 prompt 膨胀挤占输出空间 |

### 已验证可工作

✅ 正文不再出现"写前蓝图"等元信息（后处理自动剥离）
✅ 审计能检测到蓝图混入（红线第6条触发 critical）
⏳ 4个场景全部写完（待用户端到端验证）
⏳ 场景字数按细纲分配（待验证）

### 待验证

- 场景覆盖完整性：4个场景是否都以完整小说正文呈现，不是大纲摘要
- 字数分配精度：每个场景的字数是否接近细纲标注的目标值
- prompt 精简效果：指令精简后，LLM 是否还会输出蓝图（需要多次测试确认后处理是否够用）

### 踩坑记录（新增）

#### 坑50：LLM 会复制 prompt 结构作为输出
当 prompt 包含大量结构化信息（### 标题 + 要点列表）时，LLM 倾向于按相同结构"填充"输出，甚至原样复制 prompt 内容。**规则**：prompt 中的参考信息尽量用叙述段落而非结构化列表；对 LLM 输出必须加后处理过滤。

#### 坑51：token 不够不是因为 max_tokens 小，而是 prompt 胖
之前能跑通的 max_tokens=3000 在 prompt 膨胀后就不够了。单纯加 max_tokens 治标不治本，还会增加成本。**规则**：优先精简 prompt，而不是加大 max_tokens。每个 KB 注入（before_after 4000字 + writer-skills 4000字 + show-dont-tell 3000字）都在吃输出空间，需要定期审视是否全都需要。

#### 坑52：scene_summaries 丢失场景边界信息
将细纲的4个场景的 beats 拍平成一个列表后，LLM 失去了场景边界感知。它不知道哪些 beats 属于哪个场景，也不知道每个场景该写多长。**规则**：传给 writer 的场景摘要必须保留场景名、场景边界、和每个场景的目标字数。


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
    │   └── 合并所有审查问题 → 不通过 → 修订（最多5轮）
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
| `PIPELINE_MAX_REVISE_ROUNDS` | 5 | 最大修订轮数 |
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

## 十八、V7.9 修复（云服务器镜像调试 2026-04-18）

### 背景

V7.8 实现了蓝图剥离+场景字数分配，但用户实测发现正文仍然只覆盖了细纲4个场景中的前2个（场景3和4缺失或极度压缩）。核心矛盾：**LLM 不遵守 prompt 中的字数约束，场景1（目标462字）每次写到1000+字，吃掉后面场景的输出空间**。经过4轮迭代尝试，最终确定"逐场景LLM调用"为唯一可靠方案。

### 问题分析过程

| 轮次 | 尝试方案 | 结果 | 原因分析 |
|------|---------|------|---------|
| 1 | max_tokens 1.5x→2.5x + 场景字数分配表 + 铁律④ | ❌ 无改善 | token 不是瓶颈（实际只用了3000/5000），LLM 自己"收工" |
| 2 | 铁律⑤进度标记 `[场景N/M 完]` + 后处理验证 | ❌ 更差（场景3完全消失） | 增加 prompt 复杂度反而让 LLM 更混乱 |
| 3 | 分2次调用（场景1-2 + 场景3-4） | ❌ 未生效 | WSL 环境未更新代码 + 即使生效，每半次仍然膨胀前半场景 |
| 4 | **逐场景调用（1场景=1次LLM调用）** | ✅ 代码已实现 | 每次只给 LLM 一个场景，物理上不可能跳过或膨胀其他场景 |

### 关键发现

> **LLM 不遵守字数约束是行为特性，不是 prompt 问题。** 无论怎么加提示、加标记、加铁律，LLM 看到强冲突场景（如"老陈被带走"）就会自然膨胀。解决办法不是靠 LLM 自觉，而是靠**架构设计**——每次只给一个场景。

### BUG 修复

| BUG | 文件 | 现象 | 原因 | 修复 |
|-----|------|------|------|------|
| 64 | `core/server/routers/ai_actions.py` | max_tokens 3000 不够4个场景+结算表 | 2000字×1.5=3000 token，但实际需要4000-4500 token | 乘数 1.5→2.5（3000→5000 token） |
| 65 | `core/agents/writer.py` | LLM 不知道每个场景该写多少字 | scene_summaries 只有 beats 描述，没有显式字数预算 | 自动解析细纲 word_budget，生成场景字数分配表注入 prompt |
| 66 | `core/server/routers/ai_actions.py` | 4个场景塞不进一次 LLM 输出 | LLM 把80%输出花在前2个场景，后2个被挤掉 | 改为逐场景调用：每个场景单独一次 LLM 请求，最后拼接 |

### 回退的无效改动

| 改动 | 版本 | 回退原因 |
|------|------|---------|
| 铁律⑤（进度标记） | V7.10 | 增加 prompt 复杂度，LLM 反而更混乱 |
| 后处理第5轮（标记验证+剥离） | V7.10 | 配合铁律⑤，一起回退 |

### 保留的改动

| 改动 | 文件 | 说明 |
|------|------|------|
| max_tokens 2.5x | `ai_actions.py` | `target_words * 2.5`，上限8192 |
| 场景字数分配表 | `writer.py` | 自动解析 `_scene_budgets` 生成 prompt 中的分配表 |
| 铁律④（字数控制） | `writer.py` | "每个场景字数严格控制在预算内，精练推进" |
| **逐场景调用** | `ai_actions.py` | 核心改动：`_scenes_list` 解析→`for`循环逐个调用→拼接 |
| `import re` | `writer.py` | 顶层导入 re 模块（用于场景名正则解析） |

### 逐场景调用逻辑

```python
# 从详细大纲 JSON 解析出场景列表
_scenes_list = [(header, beats, budget_int), ...]

if len(_scenes_list) <= 2:
    # 单次调用（兼容章纲模式）
    result = writer.write_chapter(scene_summaries, ...)
else:
    # 逐场景调用
    for _idx, (_header, _beats, _budget) in enumerate(_scenes_list):
        _scene_summary = f"{_header}\n{_beats}"  # 只传这一个场景
        _scene_target = _budget  # 用细纲的 word_budget
        _prior_ctx = 已写内容[-800:]  # 前面的场景作为上下文
        result = writer.write_chapter(_scene_summary, ...)
        _all_parts.append(result.content)
    content = "\n\n".join(_all_parts)  # 拼接所有场景
```

### 当前状态

⏳ **逐场景调用已部署到 GitHub，WSL 端正在从头端到端测试**
- 书籍数据因 re-clone 丢失，需要重新走全流程
- `.env` 和 `.venv` 需重建
- 待验证：4个场景是否全部以完整小说正文呈现

### WSL 更新方式

由于 git pull 在 WSL 下有 TLS 问题，推荐用 curl 单文件覆盖：

```bash
cd ~/dramatica-flow-enhanced-v7
curl -sL "https://raw.githubusercontent.com/ZTNIAN/dramatica-flow-enhanced-v7/main/core/server/routers/ai_actions.py" -o core/server/routers/ai_actions.py
curl -sL "https://raw.githubusercontent.com/ZTNIAN/dramatica-flow-enhanced-v7/main/core/agents/writer.py" -o core/agents/writer.py
# 重启 uvicorn
```

### 踩坑记录（新增）

#### 坑53：max_tokens 不够 ≠ token 被截断
max_tokens=3000 时输出约2500字就停了，看起来像是 token 耗尽。但把 max_tokens 提到5000后，输出仍然是2500字——LLM 是自己"收工"了，不是被截断。**规则**：不要用 max_tokens 来控制输出长度，它只是上限，不是目标。LLM 会在它认为"写完了"的时候自然停止。

#### 坑54：LLM 不遵守字数约束是常态中的常态
prompt 写"场景1目标462字"，LLM 写1000字。加了铁律、加了进度标记、加了字数分配表，都没用。**根本解决方案**：每次只给 LLM 一个场景，物理上限制它能写的内容范围。prompt 层面的约束只能做"提示"，不能做"控制"。

#### 坑55：WSL 下 git pull 有 TLS 问题，curl 下载也可能有坑
git pull 经常卡住（GnuTLS recv error -110）。curl 下载文件看起来成功（显示下载字节数），但文件可能没写入磁盘，或者写入后 `grep`/`cat`/`wc` 等命令看不到输出（WSL 终端 stdout 异常）。**解决方案**：用 Python `urllib` 下载并验证，或直接 `rm -rf` 重新 clone。

#### 坑56：re-clone 会丢失 books/ 目录和 .env
`books/` 和 `.env` 在项目目录内但不在 git 中。`rm -rf` + re-clone 会丢失所有书籍数据和配置。**规则**：re-clone 前先备份 `books/` 和 `.env` 到项目外。或者把 `BOOKS_DIR` 配置到项目外的绝对路径。

#### 坑57：终端 stdout 可能"静默失败"
WSL 某些情况下 `echo "hello"` 都没有输出，但命令实际执行成功了（文件写入了、curl 下载了）。遇到这种情况不要相信终端输出，用 `ls -la` 或 Python 脚本验证文件是否存在。

---

*本文档由AI自动生成。下次迭代时，把本文件发给AI即可快速理解整个项目。*

## 十九、V7.10 修复（云服务器镜像调试 2026-04-18）

### 背景

V7.9 实现了逐场景LLM调用，解决了"4个场景只写2个"的问题。但用户实测发现正文质量仍有3个严重问题：1）场景间出现大段重复内容（前场景尾部被后场景重新写了一遍）；2）细纲中标注的"双线并行"叙事手法在正文中完全丢失，场景3（数据碎片觉醒线）没有写出；3）细纲的"结尾钩子"没有注入正文收尾。本轮修复3个BUG。

### BUG 修复

| BUG | 文件 | 现象 | 原因 | 修复 |
|-----|------|------|------|------|
| 67 | `core/server/routers/ai_actions.py` | 场景间大段重复（如"维护部的灯光是惨白的..."出现两次） | `_prior_ctx` 取前场景尾部800字作为上下文，writer 看到后在新场景开头重写了一遍 | ① `_prior_ctx` 改为600字并加"不要重复"提示 ② 拼接时检测并移除重叠段落（滑动窗口比对） |
| 68 | `core/server/routers/ai_actions.py` | 细纲中标注的叙事手法（如"双线并行"）在正文中丢失 | 逐场景调用时只传了 beats 描述，没有提取 narrative_technique/foreshadowing/ending_hook 等场景级字段 | 场景解析时提取这些字段，注入 `_scene_summary` 的【本场景要求】段落 |
| 69 | `core/server/routers/ai_actions.py` | 细纲"结尾钩子"没有写入正文末尾 | `chapter_end_hook` 只在 blueprint 中传给单次调用模式，逐场景模式没有传 | 最后一个场景的 `_scene_summary` 追加【本章结尾钩子要求】段落 |

### 关键发现

> **逐场景调用的上下文传递需要更精细。** V7.9 只解决了"每个场景都有LLM调用"的架构问题，但没有解决"每个场景的 prompt 是否完整"的问题。场景级的叙事手法、伏笔、结尾钩子等元信息在解析时被丢弃了，writer 只看到了 beats 描述，丢失了所有叙事技法指令。

### 已验证可工作

⏳ 场景间去重（待用户端到端验证）
⏳ 叙事手法注入（待用户端到端验证）
⏳ 章末钩子注入（待用户端到端验证）

### WSL 更新方式

```bash
cd ~/dramatica-flow-enhanced-v7
python3 -c "
import urllib.request
url = 'https://raw.githubusercontent.com/ZTNIAN/dramatica-flow-enhanced-v7/main/core/server/routers/ai_actions.py'
data = urllib.request.urlopen(url, timeout=30).read()
with open('core/server/routers/ai_actions.py', 'wb') as f:
    f.write(data)
print(f'OK: {len(data)} bytes written')
"
# 重启 uvicorn
```

### 踩坑记录（新增）

#### 坑58：逐场景调用 ≠ 逐场景传完整上下文
V7.9 的逐场景调用只解决了"物理上每个场景都有独立LLM调用"的问题，但每次调用的 prompt 质量取决于传入的 `_scene_summary`。如果只传 beats 而丢弃叙事手法、伏笔、结尾钩子等元信息，writer 就不知道"怎么写"，只知道"写什么"。**规则**：逐场景调用时，场景级元信息（叙事手法、伏笔、结尾钩子）必须完整传递给 writer。

#### 坑59：_prior_ctx 取太多反而导致重复
取前场景尾部 800 字作为上下文，writer 看到后倾向于在新场景开头"衔接"，结果把尾部内容重写了一遍。**规则**：① 上下文截短到 600 字 ② 加明确提示"直接接续，不要重复" ③ 拼接时做去重检测。

#### 坑60：结尾钩子必须注入最后一个场景
`chapter_end_hook` 在单次调用模式下通过 blueprint 传入，但逐场景模式下 blueprint 对所有场景都一样，没有区分"最后一个场景需要收尾"。**规则**：逐场景模式下，结尾钩子只注入最后一个场景的 prompt，并明确要求"在本场景末尾自然地埋下这个钩子"。

---



## 二十一、V7.12-V7.15 修复（云服务器镜像调试 2026-04-19）

### 背景

V7.11 全链路数据流修复后，环节四正文生成存在3个严重问题：1）逐场景字数截断不生效，场景1+2严重超 budget；2）场景3节拍不全，总是跳过"办公室融化+归档码+惊醒"等核心节拍；3）结尾钩子没有写入正文。经过5轮迭代（V7.12→V7.13→V7.14→V7.14b→V7.15），最终实现3场景5节拍全覆盖 + 钩子后处理拼接。

### 问题诊断过程

| 轮次 | 问题 | 尝试方案 | 结果 | 根因 |
|------|------|----------|------|------|
| V7.12 | 场景3节拍不全+钩子缺失 | 移除钩子注入+逐场景max_tokens+节拍进度标记 | ⚠️ 节拍改善但截断+钩子仍不生效 | `logger` 未定义 NameError → 代码未执行 |
| V7.12c | 正文生成500 | 修复 `logger` → `logging` | ✅ 生成成功 | import logging 但无 logger 变量 |
| V7.13 | 截断不生效+钩子缺失 | 场景解析fallback+共享钩子后处理路径 | ✅ 钩子出现 | 钩子后处理移到共享路径生效 |
| V7.14 | 截断代码执行但看不到效果 | 添加debug日志 | ✅ 发现截断生效但全局截断失败 | 截断代码本就生效，只是没日志 |
| V7.14b | 全局截断找不到 

 切割点 | 改为按 \*\*\* 分隔符截断 | ✅ 全局截断生效 | 场景间用 \*\*\* 分隔，不是 

 |

### BUG 修复

| BUG | 文件 | 现象 | 原因 | 修复 |
|-----|------|------|------|------|
| 76 | `ai_actions.py` | 生成500: name 'logger' is not defined | `import logging` 但代码中用 `logger.info()`，logger 从未定义 | `logger.info` → `logging.info` |
| 77 | `ai_actions.py` | 结尾钩子不写入正文 | 钩子后处理代码只在逐场景分支内，单次调用路径不执行 | 移到两个分支的共享后处理路径 |
| 78 | `ai_actions.py` | 钩子字段名不兼容 | 只检查 `chapter_end_hook`，LLM可能输出 `结尾钩子` 或 `ending_hook` | 三字段名 fallback |
| 79 | `ai_actions.py` | 详细大纲JSON不存在时走单次调用 | `_scenes_list` 为空 → `len <= 2` → 单次调用 → 无截断 | 字符串提取fallback：从 scene_summaries 按 `###` 分割提取场景 |
| 80 | `ai_actions.py` | 全局截断找不到切割点 | 截断搜索 `

` 但场景间用 `***` 分隔；搜索范围 `0.8x~1.2x` 太窄 | 改为按 `***` 截断 + 扩大搜索范围到 `0.6x~全文` |

### 关键发现

> **debug 日志是最重要的调试工具。** V7.12 的截断代码本就正确，但因为没有日志，无法确认是否执行。加了 `[V7.14]` 日志后一轮就定位了问题。**规则**：新增逻辑必须伴随日志，特别是条件分支和截断/过滤类操作。

> **全局截断的切割点必须和实际分隔符一致。** 代码用 `

` 搜索段落分隔，但逐场景模式用 `

` 拼接、场景内容内也有 `

`，导致切割点不准。按 `***` 截断更可靠，因为 `***` 是场景间的唯一标识。

> **钩子后处理必须在共享路径。** 如果只在逐场景分支内做钩子拼接，单次调用模式就完全没有钩子。后处理应该在 if/else 之后、save_draft 之前执行。

> **场景预算对节拍完整性至关重要。** 场景3有5个节拍（公寓→坠落→坟场→融化→惊醒），700字预算太紧。LLM 把 token 花在前3个节拍的细节上，后2个就被挤掉了。需要根据节拍数动态调整预算，或给最后一个场景更多 max_tokens。

### 已验证可工作

✅ 逐场景截断生效（日志确认：1416→778, 1180→933, 1492→938）
✅ 全局截断生效（按 \*\*\* 分隔符截断）
✅ 结尾钩子后处理拼接（"项目：回响溯源" + 监控图标）
✅ 场景1全部5节拍 ✅ 场景2全部5节拍 ✅ 场景3全部5节拍
✅ 3次独立 LLM 调用（日志确认3次 DeepSeek API 200 OK）
⏳ 全局字数精确控制（微超17%，非阻断性）

### 踩坑记录（新增）

#### 坑65：没有日志 = 没有调试能力 ⭐V7.14新增
V7.12 的截断代码其实一直在执行，但因为没有任何日志输出，看起来像"没生效"。加了 `logging.info` 后立即看到 `Scene1 TRUNCATED: 1416 -> 778`。**规则**：任何条件分支、截断/过滤/转换操作，必须有日志记录关键变量值（输入大小、输出大小、阈值）。

#### 坑66：全局截断的切割点搜索范围太窄 ⭐V7.14新增
`rfind("

", int(target*0.8), max_chars+200)` 的搜索范围是 `1600~2400`，但如果场景分隔在位置 1700 或 2500，就找不到。**规则**：切割点搜索范围应该覆盖整个内容，从 `target*0.5` 到 `len(content)`。

#### 坑67：场景分隔符不统一导致截断失败 ⭐V7.14新增
逐场景模式用 `

` 拼接各场景，但场景内容本身也包含 `

`（段落分隔）。全局截断按 `

` 搜索会切在场景中间而不是场景边界。`***` 是更可靠的分隔符，因为场景内容中不会出现 `***`。**规则**：拼接时用唯一分隔符（如 `***`），截断时按同一分隔符切割。

#### 坑68：后处理逻辑必须在共享路径 ⭐V7.13新增
钩子后处理最初写在 `else:`（逐场景）分支内。当 `_scenes_list` 为空走单次调用路径时，后处理完全跳过。**规则**：任何两种路径都需要的后处理（截断、钩子、格式清理），必须在 if/else 之后统一执行。

#### 坑69：Python heredoc 中的 
 转义是噩梦 ⭐V7.13新增
在 Python heredoc (`cat > fix.py << 'EOF'`) 中写包含 `
` 的代码时，bash 和 Python 的转义规则冲突。`"\n"` 在 heredoc 中可能变成字面量 `
`（2字符）而不是换行（1字符）。**规则**：涉及 `
` 的 patch 用独立 Python 文件（`cat > fix.py` 然后 `python3 fix.py`），不要用 inline heredoc。

#### 坑70：LLM 会在视觉复杂的节拍上花费过多 token ⭐V7.14新增
场景3有"坟场实验室+数据星河"这种视觉冲击强的节拍，LLM 倾向于详细描写，挤占了后续节拍的空间。相比之下，"惊醒+冷汗"这种简单节拍反而容易被跳过。**规则**：视觉复杂的节拍在细纲中应标注为低 weight，把 token 预算留给结构性节拍（惊醒、决心、钩子）。

#### 坑71：细纲生成是坑40的完美复现 ⭐V7.15新增
细纲 prompt 包含故事大纲(2000)+章纲(1500)+世界观(3000)，合计约6500字符。DeepSeek 在处理这么长的上下文后输出 JSON，经常有语法错误。这和坑40（正文生成上下文过长）是同一类问题。**规则**：任何包含 JSON 返回格式的 prompt，上下文总长度应控制在 2000 字符以内。

#### 坑72：JSON 截断需要括号补全 ⭐V7.15新增
LLM 输出的 JSON 经常在中间被截断（`max_tokens` 不够或模型自行"收工"），导致最后一个 `}` 或 `]` 缺失。简单的 `json.loads` 会直接失败。**方案**：检测 `{`/`[` 和 `}`/`]` 的数量差异，自动补全缺失的闭合括号。注意：这只修复括号不匹配，不能修复字段值截断。

### WSL 更新方式

```bash
cd ~/dramatica-flow-enhanced-v7
python3 -c "
import urllib.request
url = 'https://raw.githubusercontent.com/ZTNIAN/dramatica-flow-enhanced-v7/main/core/server/routers/ai_actions.py'
data = urllib.request.urlopen(url, timeout=30).read()
with open('core/server/routers/ai_actions.py', 'wb') as f:
    f.write(data)
print(f'OK: {len(data)} bytes')
"
# 重启 uvicorn
```

---

*本文档由AI自动生成和维护。下次迭代时，把本文件发给AI即可快速理解整个项目。*

*本文档由AI自动维护。下次迭代时，把本文件发给AI即可快速理解整个项目。*

## 二十、V7.11 修复（云服务器镜像调试 2026-04-18）

### 背景

V7.10 逐场景调用+去重+钩子注入后，用户实测发现**全链路数据流断开**：环节二（世界观）生成的角色/地点，在环节三（大纲）和环节四（正文）中全部丢失，LLM 凭空捏造新角色。根本原因是 Web UI 流程的数据路径设计缺陷——环节二写 `setup/` 目录，但所有下游读 `state/` 目录，且环节三的 prompt 完全没有注入世界观。本轮共修复 6 个 BUG，经历 4 轮迭代。

### BUG 修复

| BUG | 文件 | 现象 | 原因 | 修复 |
|-----|------|------|------|------|
| 70 | `ai_actions.py` → `ai_generate_outline` | 环节三大纲角色和环节二完全不同 | prompt 只传 genre/title/target_chapters，**完全没有读取任何世界观数据** | 读取 setup/ 下 characters.json + world.json + events.json，截断注入 prompt，要求"必须使用以下角色/地点/事件" |
| 71 | `ai_actions.py` → `ai_generate_setup` | 环节二写 setup/ 但环节四读 state/，路径不匹配 | `ai_generate_setup` 写 `books/{id}/setup/`，但 `chapter_content` 读 `books/{id}/state/`，CLI 通过 `SetupLoader.load_all()` 桥接但 Web UI 从未调用 | 环节二末尾自动 `shutil.copy2` 三个文件到 state/ 目录 |
| 72 | `ai_actions.py` → `ai_generate_chapter_outlines` | 章纲也不含角色/世界观信息 | 章纲 prompt 只读 outline.json + target_words，不读角色/世界观 | 同步注入 setup/ 下 characters.json + world.json |
| 73 | `ai_actions.py` → `ai_generate_detailed_outline` + `chapter_content` | 详细大纲和正文读 state/characters.json 但文件不存在 | 同 BUG71，setup→state 路径未同步 | 所有读取点加 setup/ fallback：先查 state/，不存在则 fallback 到 setup/ |
| 74 | `enhanced.py` → `api_emotion_curve` | 情绪曲线刷新后丢失 | 生成后只返回 JSON 不写文件 | 写入 state/emotion_curve.json + 新增 GET 端点 |
| 75 | `ai_actions.py` → `chapter_content` | 场景3被去重逻辑误杀，整个场景只剩几个字 | 去重代码：取前场景尾部300字，在当前场景中找到匹配就截断，不检查截断后长度 | 加安全保护：去重后不足原文30%则跳过；跳过空场景不 append |

### 4轮迭代详情

| 轮次 | 问题 | 修复 | 结果 |
|------|------|------|------|
| V7.11a | 全链路数据断开（BUG70-74） | setup→state同步+世界观注入+fallback | ✅ 大纲/章纲/细纲角色一致 |
| V7.11b | 场景3被去重误杀（BUG75） | 去重安全保护30%阈值+跳过空场景 | ✅ 场景3终于出现 |
| V7.11c | 场景3写一半就断（token截断） | max_tokens 2.5x→3.5x + prior_ctx 600→400 | ⚠️ 场景3完整了但跳过了梦境节拍 |
| V7.11d | 场景1+2超字数+场景3跳节拍 | 场景级字数截断(budget×1.2) + 强制按节拍顺序写 | ⏳ 待用户验证 |

### 关键发现

> **Web UI 和 CLI 的数据路径是断裂的。** CLI 流程通过 `SetupLoader.load_all()` 将 setup/ 数据加载为 `setup_state.json` 写入 state/，所有下游通过 `read_truth_bundle` 读取。但 Web UI 流程从未调用 `SetupLoader`，直接写 setup/ 就完事了，下游全在读 state/。**根本修复**：环节二写 setup/ 时自动同步到 state/，所有读取加双重 fallback。

> **逐场景调用的 prompt 中，结尾钩子会干扰 LLM 的叙事顺序。** LLM 看到"在本场景末尾埋下这个钩子"就急于到达钩子点，跳过中间的节拍内容。**规则**：结尾钩子的注入方式需要更精细，或改为后处理拼接。

> **LLM 不遵守字数约束是行为特性，不是 prompt 问题。** 场景1目标600字，LLM 写了1100字。prompt 里加"不能超过720字"没用。**解决方案**：后处理截断（按句号边界）。

### 已验证可工作

✅ 环节二→三：大纲角色与环节二一致
✅ 环节二→三.五：章纲角色与环节二一致
✅ 环节二→四：正文能读到环节二的角色信息（不是默认"主角"）
✅ 情绪曲线持久化 + GET 端点
✅ 场景3出现（不再被去重误杀）
⏳ 场景1+2字数控制在 budget×1.2 以内
⏳ 场景3写完全部5个节拍（入睡→梦境→惊醒→决心）
⏳ 结尾钩子位置正确（惊醒之后）

### WSL 更新方式

```bash
cd ~/dramatica-flow-enhanced-v7
curl -sL "https://raw.githubusercontent.com/ZTNIAN/dramatica-flow-enhanced-v7/main/core/server/routers/ai_actions.py" -o core/server/routers/ai_actions.py
curl -sL "https://raw.githubusercontent.com/ZTNIAN/dramatica-flow-enhanced-v7/main/core/server/routers/enhanced.py" -o core/server/routers/enhanced.py
# 重启 uvicorn
```

### 踩坑记录（新增）

#### 坑61：Web UI 数据路径和 CLI 不一致 ⭐V7.11新增
Web UI 的 `ai_generate_setup` 写 `setup/` 目录，CLI 的 `SetupLoader.load_all()` 读 `setup/` 写 `state/`。Web UI 流程跳过了 `SetupLoader`，导致所有下游读不到世界观数据。**规则**：Web UI 的生成端点必须和 CLI 的数据流保持一致，不能各写各的目录。

#### 坑62：LLM 看到结尾钩子会跳过中间内容 ⭐V7.11新增
在场景 prompt 末尾注入"请在本场景末尾埋下结尾钩子"，LLM 会急于到达钩子点，跳过中间的节拍内容。**规则**：钩子注入应更自然（如融入节拍描述中），而不是作为额外指令放在末尾。

#### 坑63：去重逻辑必须有安全保护 ⭐V7.11新增
滑动窗口去重如果只检查"是否包含尾部片段"而不检查截断后长度，可能把整个场景吃掉。**规则**：去重后如果剩余内容不足原文30%，放弃去重。同时跳过空内容场景。

#### 坑64：场景级字数必须后处理控制 ⭐V7.11新增
LLM 不遵守 prompt 中的字数约束。场景1目标600字实际写了1100字。**解决方案**：每个场景 LLM 返回后立即截断到 budget×1.2，按句号边界切割。不能依赖 LLM 自觉。

### 当前端到端测试状态

**已完成：**
- ✅ 环节一：创建书籍
- ✅ 环节二：AI生成世界观（角色/地点/事件）→ 角色成长档案
- ✅ 环节三：故事大纲生成（角色一致）
- ✅ 环节三.五：章纲生成（角色一致）
- ✅ 环节四：详细大纲/细纲生成（世界上下文正确注入）
- ✅ 环节四：正文生成（能读到角色信息，场景3出现）
- ✅ 逐场景截断生效（场景1: 865→816, 场景2: 974→939, 场景3: 1185→936）
- ✅ 结尾钩子后处理拼接成功（"项目：回响溯源" + 监控图标闪烁）
- ✅ 场景3全部5节拍覆盖（入睡→坟场梦境→办公室融化+归档码→惊醒+冷汗→决心）

**当前进度：**
- ⚠️ 全局字数微超（2802 vs 目标2400，超17%，非阻断性）
- ⚠️ 场景截断后仍超 budget（截到句号边界，不是精确到字）
- 场景3的钩子拼接略生硬（从"沉默"直接跳到"打开加密文档"）

**下一步测试：**
1. 环节五：审计 → 修订 → 确认最终稿
2. 继续写第2章，测试管线连续性
3. 全局字数精确控制（可选优化）

## 二十二、V7.16-V7.18 修复（云服务器镜像调试 2026-04-19）

V7.15 之后实测发现：1）第2章细纲生成 500；2）正文截断切在句子中间；3）正文总字数严重超标（目标2000，实际3400+）。经过3轮迭代（V7.16→V7.17→V7.18），最终通过**从源头优化章节结构**解决了根本问题。

### BUG 清单

BUG | 文件 | 现象 | 原因 | 修复
---|------|------|------|---
81 | ai_actions.py | 第2章细纲 500（第1章正常） | `co.get("chapter_number") == req.chapter` 类型不匹配：章纲里是字符串 "2"，req.chapter 是整数 2 | 3处章纲匹配统一为 `int(co.get("chapter_number", 0)) == int(req.chapter)`
82 | ai_actions.py | V7.15 上下文截断过狠导致细纲质量下降 | 故事大纲600/章纲400/世界观400，LLM看不到足够信息 | 恢复到2000/1500/1500
83 | ai_actions.py + writer.py | 截断切在句子中间 | 截断只按字符位置切，不找句号/段落边界 | 先找 `\n\n` → `\n` → `。`，在完整句子处切
84 | ai_actions.py + writer.py | 正文总字数超标72%（2000→3434） | 4场景×5节拍=20节拍的架构就是为4000字设计的，硬塞2000字框里必然超 | **从源头改：章纲2场景×3节拍，细纲2场景×2-3节拍**

### V7.16：细纲解析增强

改动 | 之前 | 之后
---|------|------
max_tokens | 4096 | 8192
章纲匹配 | `== req.chapter` | `int() == int()`（3处）
故事大纲上下文 | 600字 | 2000字
章纲上下文 | 400字 | 1500字
世界观上下文 | 400字/文件 | 1500字/文件
JSON解析 | 基础括号补全 | 控制字符清洗+引号配对修复+修复失败打印原始内容

日志标签：`[V7.16]`

### V7.17：截断逻辑优化

改动 | 之前 | 之后
---|------|------
场景截断容忍度 | budget×1.2 | budget×1.5
全局截断容忍度 | target×1.2 | target×1.5
截断搜索范围 | 0.8×target ~ max | 0.5×target ~ 全文
截断边界优先级 | 只找 `。` | `\n\n` → `\n` → `。`

日志标签：`[V7.17]`→`[V7.18]`

### V7.18：2000字精写改造 ⭐核心架构改动

**用户初衷：番茄小说每章2000字左右，要保证文章质量（token不是问题）。**

**设计哲学：从源头优化，而不是后处理截断。** 如果截断怎么改都控制不好字数，说明源头的章节结构设计有问题——不是输出端砍，而是输入端控。

改动 | 之前 | 之后
---|------|------
章纲 prompt | 无约束，LLM自由3-5场景 | **强制2场景×3节拍（共6节拍）**
细纲 prompt | "2-4个场景" | **"2场景，每场景2-3节拍（共4-6节拍）"**
正文 max_tokens | 3.5x (7000) | 2.5x (5000)
逐场景 max_tokens | 2.5x | 2.0x
截断容忍度 | 1.5x (50%) | **1.3x (30%)**
writer prompt 字数约束 | "不超过1.2x" | **"不超过1.3x。宁可少写不要超。超字数=废稿"**

#### 为什么从源头改有效

之前的链条：
```
章纲4场景×5节拍=20节拍 → 细纲展开 → LLM每节拍写100-200字 → 正文3400字 → 截断砍内容 → 句子被腰斩
```

改造后：
```
章纲2场景×3节拍=6节拍 → 细纲精练 → LLM每节拍写250-350字 → 正文2000字 → 截断几乎不触发
```

番茄/起点2000字一章的写法是"一场戏+一个转折/钩子"，不是把5000字的内容压缩成2000字。2个场景、每个3个节拍，足够写出：
- 场景1：建立情境 + 推进冲突 + 制造紧张
- 场景2：高潮/转折 + 收束 + 章末钩子

#### 关键教训

> **当后处理截断怎么调都解决不了问题时，说明问题在源头。** 不要一直改截断逻辑，应该回到章节结构设计，从prompt层面控制LLM的输出范围。这是"治本"vs"治标"的区别。

### 部署方式

WSL 更新命令：
```bash
cd ~/dramatica-flow-enhanced-v7
python3 -c "
import urllib.request
for f in ['core/server/routers/ai_actions.py', 'core/agents/writer.py']:
    url = f'https://raw.githubusercontent.com/ZTNIAN/dramatica-flow-enhanced-v7/main/{f}'
    data = urllib.request.urlopen(url, timeout=30).read()
    with open(f, 'wb') as fh:
        fh.write(data)
    print(f'{f}: {len(data)} bytes')
"
# 重启 uvicorn
```

### 当前状态

- ✅ 细纲生成（200 OK，2场景×2-3节拍）
- ✅ 正文生成（200 OK，逐场景调用）
- ✅ 截断不在句子中间切割
- ⏳ 2000字精度控制（待V7.18实测验证）
- ⏳ 审计（待测试）
- ⏳ 修订循环（待测试）

**下一步测试：**
1. 重新生成章纲（V7.18格式：2场景×3节拍）
2. 生成第1章细纲 + 正文，验证2000字精度
3. 审计 → 修订 → 确认最终稿
4. 管线连续性测试

## 二十三、V7.19 修复（云服务器镜像调试 2026-04-19）

### 背景

云服务器首次部署，从环节三章纲生成开始逐环节测试。共发现 5 个问题，经历 6 轮迭代修复。

### BUG 清单

| BUG | 文件 | 现象 | 原因 | 修复 |
|-----|------|------|------|------|
| 85 | `ai_actions.py` | 章纲生成 500：`JSONDecodeError: Expecting value: line 26 column 41` | LLM 响应 12285 字符被截断，JSON 字符串值中间断开（缺闭合引号 `"`）。现有括号补全只补 `}`/`]`，不补未闭合的字符串引号 | 增强 JSON 补全：先扫描是否在字符串内被截断（逐字符追踪 `in_str` 状态），是则先补 `"` 再补 `}`/`]` |
| 86 | `ai_actions.py` | 章纲 max_tokens=4096 不够 | 2 章 × 6 节拍的 JSON 约 12000 字符，4096 token ≈ 6000-8000 字符，不够 | max_tokens 4096→8192 |
| 87 | `ai_actions.py` | 细纲生成 3 场景而非 2 场景 | LLM 无视 prompt 中"2 个场景"约束，看到章纲 6 个 beats 自然拆成 3 场景 | 后处理：scenes>2 时，将场景 3+ 的 beats/characters/goal/conflict 合并到场景 2 |
| 88 | `ai_actions.py` | 正文 `***` 分隔符错位 + 节拍 1.6（噩梦）反复缺失 | 1) LLM 在场景 1 内部输出 `***`（虽然 prompt 禁止），导致截断位置错位；2) 场景 1 字数超标挤压场景 2；3) 最后一个节拍总是被牺牲 | 后处理强制删除 `***` + 截断容忍度 1.1→1.2 + prompt 强调"最后一个节拍必须完整展开" |
| 89 | `ai_actions.py` | 正文字数超标 + 节拍 1.6 缺失 | per-scene max_tokens=target×2.0 太宽松；prompt 没有逐节拍字数分配，LLM 自然前重后轻 | max_tokens 2.0→1.5 + prompt 新增逐节拍字数分配表（最后一个节拍占 40%） |

### V7.19 改动总表

| 改动 | 之前 | 之后 | 目的 |
|------|------|------|------|
| JSON 补全 | 只补 `}`/`]` | 先补未闭合 `"` 再补 `}`/`]` | 修复截断在字符串中间的 JSON |
| 章纲 max_tokens | 4096 | 8192 | 给长 JSON 足够空间 |
| 细纲场景数校验 | 无 | scenes>2 时合并到 2 个场景 | 强制 V7.18 格式 |
| prompt 分隔符禁令 | 无 | "绝对不要输出 *** 或任何分隔符" | 防止 LLM 自行插分隔符 |
| `***` 后处理删除 | 无 | `_part.replace("***", "")` | 兜底：即使 LLM 输出了也删掉 |
| 场景截断容忍度 | 1.1x | 1.2x | 给场景 2 更多空间保留最后一个节拍 |
| prompt 末尾节拍保护 | 无 | "最后一个节拍必须完整展开，绝不能压缩或省略" | 防止 LLM 跳过最后节拍 |
| per-scene max_tokens | target×2.0 | target×1.5 | 从源头限制 LLM 输出量 |
| 逐节拍字数分配 | 无 | 最后节拍=40%，其余均分 60% | 确保每个节拍有独立的字数预算 |

### 关键教训

#### 坑73：JSON 截断在字符串中间需要引号补全 ⭐V7.19新增
括号补全逻辑只处理了 `}`/`]` 的缺失，但 LLM 截断更常发生在字符串值中间（`"description": "正在写的内容...`），此时缺少的是闭合引号 `"`。**规则**：JSON 补全必须先检查是否在字符串内（逐字符追踪 `in_str` 状态），先补 `"` 再补 `}`/`]`。

#### 坑74：prompt 约束对"数量"类限制几乎无效 ⭐V7.19新增
无论 prompt 怎么写"2 个场景"、"不要输出 ***"，LLM 都可能无视。**规则**：数量类约束（场景数、分隔符）必须后处理兜底，不能只靠 prompt。

#### 坑75：最后一个节拍永远是牺牲品 ⭐V7.19新增
LLM 天然前重后轻：看到强冲突的前几个节拍会详写，最后一个节拍（即使是噩梦这种重要内容）被挤掉。**解决方案**：逐节拍字数分配表 + 最后节拍占 40% + prompt 明确保护。

#### 坑76：`***` 分隔符的陷阱 ⭐V7.19新增
`***` 被用作场景间分隔符（截断时按 `***` 搜索），但 LLM 会在正文中自然输出 `***`（如场景内部的视觉分隔），导致截断位置错位。**解决方案**：禁止 LLM 输出 `***`（prompt + 后处理双重删除）。

### 当前状态

- ✅ 章纲生成（200 OK，2 场景 × 3 节拍，JSON 补全增强）
- ✅ 细纲生成（200 OK，强制 2 场景，逐节拍字数分配）
- ✅ 正文生成（200 OK，6 节拍全覆盖待验证）
- ⏳ 节拍 1.6（噩梦）完整生成（方案 C 执行中，等待结果）
- ⏳ 2000 字精度控制
- ⏳ 审计 → 修订循环

### WSL 更新方式

```bash
cd ~/dramatica-flow-enhanced-v7
python3 -c "
import urllib.request
url = 'https://raw.githubusercontent.com/ZTNIAN/dramatica-flow-enhanced-v7/main/core/server/routers/ai_actions.py'
data = urllib.request.urlopen(url, timeout=30).read()
with open('core/server/routers/ai_actions.py', 'wb') as f:
    f.write(data)
print(f'OK: {len(data)} bytes')
"
# 重启 uvicorn
```

## 二十三、V7.20-V7.22 修复（云服务器镜像调试 2026-04-19）

### 背景

环节四正文生成进入稳定阶段后，开始测试环节五（审计→修订）。发现修订阶段存在 4 个严重问题。

### V7.20：正文字数控制优化

**改动**：
- per-scene max_tokens: 1.5x → 1.3x（源头限制输出量）
- 场景截断容忍度: 1.2x → 1.0x（场景不超标）
- 全局截断容忍度: 1.1x → 1.05x
- prompt 字数铁律：「宁可少写100字，绝不能超！超字数=废稿。场景内换地点不加字数！」

**结果**：第1章从 V7.19 的 2652 字降到 2499 字，6节拍全覆盖，节拍1.6（噩梦）不再丢失。

**Release**: https://github.com/ZTNIAN/dramatica-flow-enhanced-v7/releases/tag/v7.20-stable

### V7.21：修订阶段蓝图剥离

| BUG | 文件 | 现象 | 原因 | 修复 |
|-----|------|------|------|------|
| 90 | writing.py | 修订后正文出现「写前蓝图」「写后结算表」 | writer.py 有4轮后处理剥离，但 reviser.py 和 writing.py 完全没有 | writing.py 新增 `_strip_blueprint()` 函数，4个修订出口统一调用 |
| 91 | reviser.py | 修订时 LLM 把规划信息当正文输出 | prompt 和 system message 没有禁止输出规划信息 | prompt 新增「铁律：禁止输出规划信息」+ system message 新增同等约束 |

### V7.22：审计→修订流程修复

| BUG | 文件 | 现象 | 原因 | 修复 |
|-----|------|------|------|------|
| 92 | writing.py | 修订后用户 promote 的 final 被删除 | `final_path.unlink()` 主动删除 final | 删除该行，修订只更新 draft |
| 93 | writing.py | 切换环节后审计结果为空（404） | auto-revise-loop 内部审计没持久化到文件 | 每轮审计后保存 audit_chXXXX.json |
| 94 | writing.py | 终端看不到审计问题和修订内容 | 无日志输出 issues 和 change_log | 每轮输出 issues 列表 + change_log，日志标签 `[V7.22]` |

### 根本问题：Reviser 全文重写导致越改越偏

**现象**：auto-revise-loop 多轮修订后，正文从「调谐中心+异常注释」完全变成了「教堂+老K+坟场」，等于重写了一整章。

**根因**：ReviserAgent 每次调用时传入全文 + 所有 issues，LLM 被要求「修订」但实际在「重写」。多轮重写累积漂移，每轮都在上一轮的基础上再改一遍，内容越来越偏离原文。

**修复方向（待实现）**：
1. 逐 issue 定位替换：用 excerpt 在原文中定位问题段落，只替换该段落
2. 相似度校验：修订后对比原文相似度，低于 70% 则拒绝并回滚
3. 单轮最大改动限制：一轮修订最多改 3 个 issue，超过则分轮处理
4. prompt 改为 diff 模式：要求 LLM 输出 `---旧内容 +++新内容` 格式，后端做 patch

**影响范围**：`core/agents/reviser.py` 的 `revise()` 方法 + `core/server/routers/writing.py` 的 auto-revise-loop

**临时规避**：当前版本只跑 1 轮修订（max_rounds=1），手动检查后再决定是否跑第 2 轮。

## 二十四、前端审计/修订流程修复（云服务器镜像调试 2026-04-20）

### 背景

环节五（审计→修订）在 V7.22 后端修复基础上，实测发现前端 3 个交互问题 + 后端 1 个格式问题。

### BUG 清单

| BUG | 文件 | 现象 | 原因 | 修复 |
|-----|------|------|------|------|
| 95 | `dramatica_flow_web_ui.html` | 正文编辑→点击「保存正文」→前端无变化，草稿没有变成最终稿 | `saveEditedContent(kind)` 传的是加载时的 kind（draft），永远只保存草稿，没有"升级为最终稿"的入口 | 拆分为两个按钮：「保存草稿」(kind=draft) + 「保存为最终稿」(kind=final) |
| 96 | `dramatica_flow_web_ui.html` | 点击「循环自动修订」→ 只弹一个 toast，不知道每轮改了什么、有什么问题 | `doAutoReviseLoop()` 只用 `toast()` 展示摘要，后端返回的 rounds/issues/changes 全部丢弃 | 在审计结果面板中渲染逐轮报告：每轮通过状态 + issues 列表 + changes 列表 |
| 97 | `dramatica_flow_web_ui.html` | 审计环节→切到其他环节→再切回审计→审计结果为空 | `switchAuditTab('audit')` 没有触发 `loadSavedAudit()`，审计结果只在 `loadStep6()` 初始化时加载一次 | 在 `switchAuditTab` 中增加 `if (tab === 'audit') loadSavedAudit()` |
| 98 | `writing.py` | auto-revise-loop 保存的审计结果，前端 `loadSavedAudit()` 加载后 `renderAuditResult()` 渲染失败（静默吞错） | `auto-revise-loop` 保存格式是 `{report: _report_dict}`，而 `renderAuditResult()` 需要 `{layers: {...}}`，格式不匹配 | `auto-revise-loop` 持久化时使用与 `three-layer-audit` 相同的 3-layer 格式 |
| 99 | `writing.py` | auto-revise-loop 5轮修订全部失败，审计只报"缺写前蓝图/写后结算表/真相文件"，修订无实际改动 | `auto-revise-loop` 传给审计员的 blueprint 全为空（core_conflict=""、hooks_to_plant=[]、emotional_journey={}），审计员没有参照标准，只能抱怨"缺元数据"。Reviser 试图添加元信息 → `_strip_blueprint()` 删掉 → 死循环 | 从 `chapter_outlines.json` 读取章纲，构建真实 blueprint（与 `three-layer-audit` 逻辑一致）。同时 truth_bundle 增加 CHARACTER_MATRIX |

### V7.23 改动总表

| 改动 | 文件 | 之前 | 之后 |
|------|------|------|------|
| 正文编辑按钮 | `dramatica_flow_web_ui.html` | 单按钮「保存正文」传 `kind=${res.kind}` | 双按钮：「保存草稿」(draft) + 「保存为最终稿」(final) |
| 循环修订结果展示 | `dramatica_flow_web_ui.html` | 只弹 toast 摘要 | 审计面板渲染逐轮报告（issues + changes） |
| 审计标签重载 | `dramatica_flow_web_ui.html` | 切回审计标签无操作 | 触发 `loadSavedAudit()` |
| 审计结果格式 | `writing.py` | `{ok, chapter, passed, summary, report}` | `{ok, chapter, passed, summary, layers, dimension_scores, ...}`（3-layer 格式） |
| auto-revise-loop blueprint | `writing.py` | 硬编码空 blueprint | 从 `chapter_outlines.json` 读取章纲构建 blueprint（与 three-layer-audit 一致） |
| auto-revise-loop truth_ctx | `writing.py` | 只读 CURRENT_STATE + PENDING_HOOKS | 增加 CHARACTER_MATRIX（与 three-layer-audit 一致） |

### 用户工作流（修复后）

```
1. 生成草稿
2. 正文编辑 → 点「保存为最终稿」→ 初始草稿存为 final（快照）
3. 运行审计 → 看到审计结果
4. 循环自动修订 → 审计面板显示每轮变化
5. 切到其他环节再切回审计 → 审计结果还在
6. 对比 final（初始）vs draft（修订后）→ 看效果
```

### WSL 更新方式

本次改动 1 个文件：

```bash
cd ~/dramatica-flow-enhanced-v7
python3 -c "
import urllib.request
for f in ['core/server/routers/writing.py']:
    url = f'https://raw.githubusercontent.com/ZTNIAN/dramatica-flow-enhanced-v7/main/{f}'
    data = urllib.request.urlopen(url, timeout=30).read()
    with open(f, 'wb') as fh:
        fh.write(data)
    print(f'{f}: {len(data)} bytes')
"
# 重启 uvicorn
```

> ⚠️ 如果你的 `dramatica_flow_web_ui.html` 还是旧版（只有一个「保存正文」按钮），也需要更新：
> 把 `'dramatica_flow_web_ui.html'` 加到上面的 for f 列表里。

### 当前状态

- ✅ 正文编辑：双按钮（保存草稿 / 保存为最终稿）
- ✅ 循环自动修订：逐轮报告渲染在审计面板
- ✅ 审计结果持久化：切环节不丢失
- ✅ 审计结果格式统一：auto-revise-loop 与 three-layer-audit 格式一致
- ✅ auto-revise-loop blueprint：从章纲读取，与 three-layer-audit 一致
- ⏳ 待用户实测验证

---

## ⚠️ AI 操作规范（血的教训，不可再犯）

> **2026-04-20 记录。以下错误导致用户浪费 1 小时调试，数据丢失风险，反复返工。**

### 🚫 禁止行为清单

#### 🔴 红线 1：改代码前必须读完所有相关文件
- **错误**：改 `writing.py` 前没读 `auditor.py`、`reviser.py`、`writer.py`、`state/__init__.py`，不知道审计员的 prompt 结构、blueprint 参数含义、truth 文件读取逻辑
- **后果**：提出的修复方案只改了审计结果格式（无关紧要），没发现真正的问题（blueprint 为空导致审计员报"缺元数据"）
- **规则**：改任何代码前，必须先 `grep -rn` 追踪完整的调用链，读完链上每个文件

#### 🔴 红线 2：必须读完项目交接文档再动手
- **错误**：PROJECT_HANDOFF.md 1400+ 行，只扫了标题和 grep 了几个关键词，没读"坑"和"已知问题"章节
- **后果**：文档第 1418 行已经写了"Reviser 全文重写导致越改越偏"的根本问题，我完全没看到，导致修复方向错误
- **规则**：读 PROJECT_HANDOFF.md 的完整内容，特别关注：坑记录、已知问题、当前状态、失败案例

#### 🔴 红线 3：不经过用户确认不能改代码和推送
- **错误**：用户报了 3 个 bug，我直接改了代码、提交、推送，没有先分析原因和列出方案
- **后果**：用户拿到的是我没理解清楚就改的代码，反而引入新问题（auto-revise-loop 死循环暴露）
- **规则**：必须按四步走：①分析所有可能原因 → ②每种情况的修复方案+副作用 → ③推荐方案+理由 → ④等用户确认再动手

#### 🔴 红线 4：不能用 urllib/git pull 覆盖用户本地文件
- **错误**：给了 `git pull` 和 `git stash + git reset --hard` 命令，差点覆盖用户的 `.env`、`books/`、本地修改
- **后果**：用户本地的 `reviser.py`、`writer.py`、`ai_actions.py`、`writing.py` 都有未提交的修改，差点全丢
- **规则**：更新只用 urllib 下载**本次改动的具体文件**，绝不 `git pull` / `git reset --hard`。每次更新前问用户：你的本地有哪些未提交的修改？

#### 🔴 红线 5：对比差异前不能假设"我的改动没影响"
- **错误**：看到 `git diff` 只改了格式就下结论"不影响逻辑"，没考虑到用户本地版本和 GitHub 版本可能不同
- **后果**：用户第一次测试能过、第二次过不了，我一开始完全无法解释，浪费了大量时间
- **规则**：任何行为差异，先假设"可能是版本/状态差异"，检查 git stash、本地修改、文件内容差异

### ✅ 正确操作流程

```
1. 用户报 bug → 先读完所有相关代码（含调用链上的每个文件）
2. 读完 PROJECT_HANDOFF.md（全文，重点看坑和已知问题）
3. 列出所有可能原因（情况1、情况2...）
4. 每种情况的修复方案 + 副作用
5. 推荐方案 + 为什么
6. 等用户确认
7. 改代码 → 本地测试 → 推送 → 告诉用户 urllib 更新命令
8. 更新命令只包含本次改动的文件，绝不 git pull
```

### 📌 给用户的更新命令模板

每次更新时，AI 必须提供：
1. 改了哪几个文件（完整路径）
2. 每个文件改了什么（一句话描述）
3. urllib 更新命令（只下载这些文件）

```bash
cd ~/dramatica-flow-enhanced-v7
python3 -c "
import urllib.request
for f in [
    # AI 在这里列出本次改动的文件
]:
    url = f'https://raw.githubusercontent.com/ZTNIAN/dramatica-flow-enhanced-v7/main/{f}'
    data = urllib.request.urlopen(url, timeout=30).read()
    with open(f, 'wb') as fh:
        fh.write(data)
    print(f'{f}: {len(data)} bytes')
"
# 重启 uvicorn
```

---



---

## 二十三、端到端调试方法论（2026-04-20 现场排查记录）

> 本章记录本次对第1章端到端测试结果的完整排查流程，供后续 AI 对话快速定位问题。

### 排查步骤清单

当用户反馈「生成结果不对」时，按以下顺序排查：

**Step 1：确认是代码问题还是数据问题**

```
git status                              # 本地修改了哪些文件
git diff core/server/routers/ai_actions.py   # 关键文件的 diff
git log --oneline origin/main...HEAD    # 本地落后远程多少提交
```

- 如果 `git diff` 无变化 → 问题在数据或 LLM 随机性
- 如果 `git diff` 有变化 → 检查改动是否引入了回归

**Step 2：验证数据层（章纲 + 细纲）**

```
# 章纲节拍数
python3 -c "import json; data=json.loads(open('./books/{书名}/state/chapter_outlines.json').read()); ch=[c for c in data if c.get('chapter_number')==N][0]; print(f'节拍数: {len(ch.get("beats",[]))}')"

# 细纲场景/节拍结构 + weight/word_budget
python3 -c "import json; data=json.loads(open('./books/{书名}/state/detailed_outlines/chNNNN.json').read()); [print(f'场景{i+1}: weight={sc.get("weight","?")}, word_budget={sc.get("word_budget","?")}, beats={len(sc.get("beats",[]))}') for i,sc in enumerate(data.get('scenes',[]))]"
```

**Step 3：验证传给 writer 的 scene_summaries（正则匹配 + 字数分配）**

writer.py 中 `_scene_budgets` 用正则 `^###\s+(.+?)（目标(\d+)字）` 从 scene_summaries 提取场景名和字数预算。如果格式不匹配，会 fallback 到均分，导致字数分配错误。

```
# 检查正则能否匹配所有场景
python3 -c "
import re
for line in scene_summaries.split('
'):
    m = re.match(r'^###\s+(.+?)（目标(\d+)字）', line)
    if m:
        print(f'场景: {m.group(1)}, 预算: {m.group(2)}字')
"
```

**Step 4：验证实际输出的场景字数分布**

```
python3 -c "
from pathlib import Path
content = Path('./books/{书名}/chapters/chNNNN_final.md').read_text(encoding='utf-8')
# 手动定位场景分界点，分别计算每个场景的字数
"
```

**Step 5：对比原始 draft vs auto-revise 后的版本（如有 .bak）**

```
diff ./books/{书名}/chapters/chNNNN_draft.bak.md ./books/{书名}/chapters/chNNNN_draft.md
```

### 本次排查发现的问题总结

| # | 问题 | 根因 | 状态 |
|---|------|------|------|
| 1 | 节拍 1.6（噩梦）被压缩成元叙事 | auto-revise-loop 的 Reviser 重写整章，无场景字数约束 | 待修复 |
| 2 | 场景1/场景2 字数严重失衡（1957/266 vs 目标1000/1000） | 同上，Reviser 自由发挥导致 | 待修复 |
| 3 | Schema 校验失败导致循环提前终止 | `_AuditReportSchema.weighted_total: int` 太严格 | 待修复 |
| 4 | Blueprint 伏笔列表为空 | 章纲 JSON 缺少 `hooks_to_advance`/`hooks_to_plant` | Warning，低优先级 |
| 5 | 写后结算表为空 | `PostWriteSettlement([], [], [], [], [])` 硬编码空值 | Warning，低优先级 |

### 关键教训

1. **不能 `git pull`**：会覆盖 .env、books/、.venv/。用 urllib 逐文件下载。
2. **先查数据再查代码**：多数问题根因在 chapter_outlines.json / detailed_outline 的结构，而非代码逻辑。
3. **auto-revise-loop 的 Reviser 是全文修订**：它会重写整章，可能破坏场景比例。需要场景级约束。
4. **v7.20-stable tag == 当前 main 的 HEAD**：GitHub 上 main 和 v7.20-stable 是同一 commit，本地有未提交修改 + 落后远程 35 个提交。
5. **`git diff` 比 `git pull` 更安全**：先看差异，再决定要不要拉。


---

## 二十四、V7.23 锚定式修订（2026-04-20）

### 问题背景

auto-revise-loop 的 Reviser 会重写整章，导致：
- 场景比例失衡（场景1膨胀到1957字、场景2压缩到266字，目标各1000字）
- 节拍被压缩（节拍1.6 噩梦只剩3行元叙事）

### 根因

Reviser 拿到「这些问题需要修」+「全文」，但不知道：
1. 每个场景的字数预算是多少
2. 场景边界在哪里
3. 哪些部分是好的、不该动

### 解决方案：锚定式修订

```
1. 保存 .bak
2. 按 ### 场景标题 拆分草稿为独立场景
3. 从 detailed_outline 读取每个场景的 word_budget
4. 根据 issues 的 location/description 定位到受影响的场景
5. 只修订受影响的场景，传入该场景的字数预算
6. 没问题的场景原样保留，一个字不动
7. 重新拼装 + 全局字数截断
```

### 新增函数（writing.py）

- `_parse_scenes_by_header(content)` — 按 `###` 标题拆分草稿
- `_identify_affected_scenes(issues, scenes)` — 根据 issues 定位受影响场景
- `_revise_scenes(content, issues, scenes, scene_budgets, reviser, s, chapter)` — 场景级修订

### 改动文件

| 文件 | 改动 |
|------|------|
| `core/server/routers/writing.py` | auto-revise-loop 改为场景级修订；新增3个辅助函数 |

### WSL 更新

```bash
cd ~/dramatica-flow-enhanced-v7
python3 -c "
import urllib.request
f = 'core/server/routers/writing.py'
url = f'https://raw.githubusercontent.com/ZTNIAN/dramatica-flow-enhanced-v7/main/{f}'
data = urllib.request.urlopen(url, timeout=30).read()
with open(f, 'wb') as fh:
    fh.write(data)
print(f'{f}: {len(data)} bytes')
"
# 重启 uvicorn
```

## 二十五、V7.23b 修复（云服务器镜像调试 2026-04-20）

### 背景

V7.23 锚定式修订部署后，实测发现两个核心问题：1）场景解析在 auto-revise-loop 的大多数轮次中失败（5轮中只有 Round 3 成功解析）；2）auto-revise-loop 5轮修订导致质量死亡螺旋（score 从 93 跌到 88，重新出现 critical）。

### 根因分析

#### 问题 1：场景解析间歇性失败

**数据流**：
```
ai_actions.py 生成 → "\n\n\n".join(parts) → draft 含 \n\n\n 分隔符
    ↓
writing.py auto-revise-loop Round 1:
    _parse_scenes() → 按 \n{3,} 拆分 → ✅ 可以解析
    → 但 fallback 到全文修订（因为初始读取的 content 来自 promote 的 final，可能无分隔符）
    → Reviser 全文重写 → 输出不含 \n\n\n 分隔符
    ↓
Round 2: _parse_scenes() → 按 \n{3,} 拆分 → ❌ 无分隔符，解析失败
    → 再次全文修订 → 输出仍无分隔符
    ↓
Round 3: 某种情况下分隔符恢复 → ✅ 解析成功 → 场景级修订
    → 场景级修订用 "\n\n\n".join() → 输出含 \n\n\n 分隔符
    ↓
Round 4: _parse_scenes() → ✅ 解析成功 → 但审计后 Reviser 全文重写又破坏分隔符
    ↓
Round 5: ❌ 解析失败
```

**根因**：Reviser 全文修订时不理解 `\n\n\n` 分隔符，重写后自然丢失。

#### 问题 2：修订质量死亡螺旋

**现象**：auto-revise-loop 每轮修订后 score 波动（86→94→93→88→93），Round 4 重新出现 critical。

**根因**：PROJECT_HANDOFF.md 第 V7.22 章已记录——"ReviserAgent 每次调用时传入全文 + 所有 issues，LLM 被要求「修订」但实际在「重写」。多轮重写累积漂移，每轮都在上一轮的基础上再改一遍，内容越来越偏离原文。"

**具体机制**：
1. Round 1: 原始草稿 → Reviser 全文重写 → 引入新表述
2. Round 2: 在 Round 1 的基础上再次重写 → 漂移加剧
3. Round N: 内容已偏离原始草稿很远 → 审计员发现新问题（与原始蓝图不一致）→ 分数下降

### BUG 修复

| BUG | 文件 | 现象 | 原因 | 修复 |
|-----|------|------|------|------|
| 100 | `writing.py` | auto-revise-loop 全文修订破坏 `\n\n\n` 分隔符 | Reviser 全文重写后无场景分隔符，下一轮解析失败 | fallback 从全文修订改为预算约束修订：注入字数约束 + 修订后截断 |
| 101 | `writing.py` | 5轮修订导致质量死亡螺旋 | 轮次越多，内容漂移越大，审计越差 | max_rounds 默认 5→2 |

### 改动总表

| 改动 | 文件 | 之前 | 之后 |
|------|------|------|------|
| fallback 修订策略 | `writing.py` | 全文修订（无字数约束） | 预算约束修订：注入 `total_budget` 字数约束 + 修订后截断 |
| max_rounds 默认值 | `writing.py` | 5 | 2 |
| legacy 路由 max_rounds | `writing.py` | 5 | 2 |

### 预算约束修订逻辑

当 `_parse_scenes` 失败时（`len(scenes) <= 1`），不再做无约束全文修订，改为：

1. 计算 `total_budget = sum(scene_budgets)`（所有场景字数预算之和）
2. 在第一个 issue 的 `suggestion` 字段末尾注入字数约束：
   ```
   [系统指令] 修订后全文不得超过 {total_budget} 字。原文共 {len(content)} 字。只修改问题涉及的句子，其余一字不动。宁可少改也不要膨胀字数。
   ```
3. 调用 Reviser 修订
4. 修订后如果超过 budget，按句号边界截断

### 备份版本

- **v7.23b-pre-anchor-fix**: https://github.com/ZTNIAN/dramatica-flow-enhanced-v7/releases/tag/v7.23b-pre-anchor-fix
  - 包含 V7.23 锚定式修订 + V7.23b 场景拼接修复（`\n\n\n` join）
  - 不包含本章的预算约束修订和 max_rounds 修改
  - 回滚方式见 release 页面

### 关键教训

#### 坑77：fallback 修订策略必须有字数约束 ⭐V7.23b新增
当场景解析失败降级为全文修订时，如果没有任何字数约束，LLM 会自由发挥导致输出膨胀。更严重的是，膨胀后的内容在下一轮可能触发新的审计问题（内容与蓝图不一致）。**规则**：任何修订路径（场景级或全文级）都必须传入字数约束。

#### 坑78：auto-revise-loop 轮次越多质量越差 ⭐V7.23b新增
LLM 修订的本质是"重写"而非"修补"。每轮重写都在上一轮的基础上累积漂移。5轮重写后，内容可能已面目全非。**规则**：auto-revise-loop 最多 2 轮。第 1 轮修主要问题，第 2 轮收尾。超过 2 轮应手动检查。

#### 坑79：场景分隔符是脆弱的全局状态 ⭐V7.23b新增
`\n\n\n` 分隔符只在 ai_actions.py 的生成阶段被写入。经过 Reviser、editor、promote 等任意一个环节后，分隔符都可能被破坏。**规则**：不应该依赖内容中的分隔符作为可靠的场景标识。更可靠的方式是在修订前用代码（而非 LLM）做场景拆分和重组。

### WSL 更新

本次改动 1 个文件：

```bash
cd ~/dramatica-flow-enhanced-v7
python3 -c "
import urllib.request
for f in ['core/server/routers/writing.py']:
    url = f'https://raw.githubusercontent.com/ZTNIAN/dramatica-flow-enhanced-v7/main/{f}'
    data = urllib.request.urlopen(url, timeout=30).read()
    with open(f, 'wb') as fh:
        fh.write(data)
    print(f'{f}: {len(data)} bytes')
"
# 重启 uvicorn
```

### 当前状态

- ✅ 场景拼接修复：`\n\n\n` join 匹配 `_parse_scenes` 的 `\n{3,}` 拆分
- ✅ 预算约束修订：fallback 路径注入字数约束 + 截断
- ✅ max_rounds: 5→2
- ⏳ 待用户实测验证
