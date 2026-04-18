"""
/ai-actions AI 生成/提取
"""
from __future__ import annotations

import json
import logging
import re

from fastapi import APIRouter, HTTPException

from ..deps import (
    sm, load_env, create_llm, run_sync, dc_to_dict, DF_MAP,
    AiGenerateSetupReq, ExtractFromNovelReq, AiGenerateOutlineReq,
    AiContinueOutlineReq, DetailedOutlineReq, ChapterContentReq,
    ExtractStoryStateReq,
)

router = APIRouter(prefix="/api/books", tags=["ai-actions"])


@router.post("/{book_id}/ai-generate/setup")
async def ai_generate_setup(book_id: str, req: AiGenerateSetupReq):
    """AI 自动生成世界观设定"""
    load_env()
    s = sm(book_id)
    llm = create_llm()
    from core.llm import LLMMessage
    prompt = f"""你是一位专业的小说世界观构建师。请为以下小说生成完整的角色、世界和事件设定。

题材：{req.genre}
书名：{req.book_title}
{f'核心想法：{req.idea}' if req.idea else ''}

请返回 JSON 格式，包含：
1. characters: 角色数组（每个包含 id, name, role, personality, backstory, goals, relationships）
2. locations: 地点数组（每个包含 id, name, description, significance）
3. events: 种子事件数组（每个包含 id, description, chapter_hint, impact）

风格：{req.style}
返回纯 JSON，不要 markdown 代码块。"""
    try:
        resp = await run_sync(llm.complete, [LLMMessage(role="user", content=prompt)])
        import json as _json, re as _re
        data = _json.loads(_re.sub(r"^\s*```(?:json)?\s*", "", resp.content.strip(), flags=_re.MULTILINE).replace("```", "").strip())
        setup_dir = s.book_dir / "setup"
        setup_dir.mkdir(parents=True, exist_ok=True)
        if "characters" in data:
            chars = {"characters": data["characters"]}
            (setup_dir / "characters.json").write_text(json.dumps(chars, ensure_ascii=False, indent=2), encoding="utf-8")
        if "locations" in data:
            world = {"locations": data["locations"], "power_system": data.get("power_system", "")}
            (setup_dir / "world.json").write_text(json.dumps(world, ensure_ascii=False, indent=2), encoding="utf-8")
        if "events" in data:
            evts = {"events": data["events"]}
            (setup_dir / "events.json").write_text(json.dumps(evts, ensure_ascii=False, indent=2), encoding="utf-8")
        # ── 同步复制到 state/ 目录，供下游环节读取 ──
        import shutil as _shutil
        state_dir = s.state_dir
        state_dir.mkdir(parents=True, exist_ok=True)
        for _fname in ("characters.json", "world.json", "events.json"):
            _src = setup_dir / _fname
            if _src.exists():
                _shutil.copy2(_src, state_dir / _fname)
        return {"ok": True, "data": data}
    except Exception as e:
        raise HTTPException(500, f"AI 生成设定失败：{e}")


@router.post("/{book_id}/extract-from-novel")
async def extract_from_novel(book_id: str, req: ExtractFromNovelReq):
    """从已有小说文本中提取角色和世界观设定"""
    load_env()
    s = sm(book_id)
    llm = create_llm()
    from core.llm import LLMMessage
    text_preview = req.text[:8000]
    prompt = f"""你是一位专业的小说分析师。请从以下小说文本中提取角色和世界观设定。

题材：{req.genre}

小说文本（节选）：
{text_preview}

请返回 JSON 格式：
1. characters: 提取的角色（每个包含 id, name, role, personality, relationships）
2. locations: 提取的地点
3. world_rules: 发现的世界规则/设定
4. plot_summary: 情节概述

返回纯 JSON。"""
    try:
        resp = await run_sync(llm.complete, [LLMMessage(role="user", content=prompt)])
        import json as _json, re as _re
        data = _json.loads(_re.sub(r"^\s*```(?:json)?\s*", "", resp.content.strip(), flags=_re.MULTILINE).replace("```", "").strip())
        return {"ok": True, "extracted": data}
    except Exception as e:
        raise HTTPException(500, f"提取失败：{e}")


@router.post("/{book_id}/extract-story-state")
async def extract_story_state(book_id: str, req: ExtractStoryStateReq):
    """从小说文本中提取完整故事状态（角色位置/情感/因果链等）"""
    load_env()
    s = sm(book_id)
    llm = create_llm()
    from core.llm import LLMMessage
    text_preview = req.text[:12000]
    prompt = f"""你是一位资深小说分析师。请从小说文本中提取完整的故事状态信息。

小说文本：
{text_preview}

请返回 JSON 格式：
1. characters: 角色详细信息（含当前位置、情感状态、关系变化）
2. plot_progression: 情节推进节点
3. causal_chain: 因果链（事件A导致事件B）
4. emotional_states: 角色情感变化轨迹
5. pending_hooks: 未回收的伏笔
6. world_state: 当前世界观状态

返回纯 JSON。"""
    try:
        resp = await run_sync(llm.complete, [LLMMessage(role="user", content=prompt)])
        import json as _json, re as _re
        data = _json.loads(_re.sub(r"^\s*```(?:json)?\s*", "", resp.content.strip(), flags=_re.MULTILINE).replace("```", "").strip())
        return {"ok": True, "state": data}
    except Exception as e:
        raise HTTPException(500, f"提取故事状态失败：{e}")


@router.post("/{book_id}/extract-story-state/batch")
async def extract_story_state_batch(book_id: str):
    """批量提取故事状态（从所有已写章节）"""
    load_env()
    s = sm(book_id)
    chapters = []
    for f in sorted(s.chapter_dir.glob("ch*_final.md")):
        content = f.read_text(encoding="utf-8")
        chapters.append(content)
    if not chapters:
        raise HTTPException(404, "没有已写章节")

    llm = create_llm()
    from core.llm import LLMMessage
    all_states = []
    for i, ch_content in enumerate(chapters):
        try:
            prompt = f"""从第{i+1}章文本中提取关键信息：
- 出场角色及其状态
- 关键事件和因果关系
- 情感变化
- 伏笔

文本：{ch_content[:5000]}
返回 JSON。"""
            resp = await run_sync(llm.complete, [LLMMessage(role="user", content=prompt)])
            import json as _json, re as _re
            state = _json.loads(_re.sub(r"^\s*```(?:json)?\s*", "", resp.content.strip(), flags=_re.MULTILINE).replace("```", "").strip())
            state["chapter"] = i + 1
            all_states.append(state)
        except Exception as e:
            logging.warning(f"提取第{i+1}章状态失败: {e}")
            continue
    return {"ok": True, "chapters_processed": len(all_states), "states": all_states}


@router.post("/{book_id}/ai-generate/outline")
async def ai_generate_outline(book_id: str, req: AiGenerateOutlineReq):
    """AI 生成故事大纲"""
    load_env()
    s = sm(book_id)
    try:
        cfg = s.read_config()
        genre = cfg.get("genre", "玄幻")
        title = cfg.get("title", "")
        target_ch = cfg.get("target_chapters", 90)
    except Exception:
        genre, title, target_ch = "玄幻", "", 90

    # ── 读取世界观设定（环节二生成的）──
    world_ctx = ""
    for _fname in ("characters.json", "world.json", "events.json"):
        _fp = s.state_dir / _fname
        if not _fp.exists():
            _fp = s.book_dir / "setup" / _fname  # fallback 到 setup/
        if _fp.exists():
            try:
                world_ctx += f"\n{_fname}：{_fp.read_text(encoding='utf-8')[:800]}"
            except Exception:
                pass

    llm = create_llm()
    from core.llm import LLMMessage
    idea_text = f"用户想法：{req.idea}\n" if req.idea else ""
    prompt = f"""你是一位专业的小说大纲规划师。请为以下小说生成完整的故事大纲。

题材：{genre}
书名：{title}
目标章数：{target_ch}
{idea_text}
{f'''世界观设定（必须严格使用以下角色、地点和事件，不能自己另编）：
{world_ctx}''' if world_ctx else ''}

请生成包含 6-10 个序列（sequence）的大纲，每个序列包含：
- id: 序列标识
- title: 序列标题
- dramatic_function: setup/inciting/turning/midpoint/crisis/climax/reveal/decision/consequence/transition
- summary: 序列概述
- narrative_goal: 叙事目标
- estimated_scenes: 预估场景数（整数）
- key_events: 关键事件列表

返回 JSON：{{"sequences": [...]}}"""
    try:
        resp = await run_sync(llm.complete, [LLMMessage(role="user", content=prompt)])
        import json as _json, re as _re
        data = _json.loads(_re.sub(r"^\s*```(?:json)?\s*", "", resp.content.strip(), flags=_re.MULTILINE).replace("```", "").strip())
        if "sequences" in data:
            from ..deps import normalize_outline
            data = normalize_outline(data, s)
        return {"ok": True, "outline": data}
    except Exception as e:
        raise HTTPException(500, f"AI 生成大纲失败：{e}")


@router.post("/{book_id}/ai-continue/outline")
async def ai_continue_outline(book_id: str, req: AiContinueOutlineReq):
    """AI 续写大纲（追加序列）"""
    load_env()
    s = sm(book_id)
    outline_path = s.state_dir / "outline.json"
    if not outline_path.exists():
        raise HTTPException(404, "大纲不存在，请先生成")
    existing = json.loads(outline_path.read_text(encoding="utf-8"))
    existing_seqs = existing.get("sequences", [])
    last_summary = existing_seqs[-1].get("summary", "") if existing_seqs else ""

    llm = create_llm()
    from core.llm import LLMMessage
    prompt = f"""续写故事大纲。已有 {len(existing_seqs)} 个序列，最后序列：{last_summary}
请追加 {req.extra_sequences} 个新序列。
{f'想法：{req.idea}' if req.idea else ''}
返回 JSON：{{"sequences": [...]}}"""
    try:
        resp = await run_sync(llm.complete, [LLMMessage(role="user", content=prompt)])
        import json as _json, re as _re
        new_seqs = _json.loads(_re.sub(r"^\s*```(?:json)?\s*", "", resp.content.strip(), flags=_re.MULTILINE).replace("```", "").strip())
        if "sequences" in new_seqs:
            existing["sequences"].extend(new_seqs["sequences"])
        else:
            existing["sequences"].extend(new_seqs if isinstance(new_seqs, list) else [])
        from ..deps import normalize_outline
        existing = normalize_outline(existing, s)
        return {"ok": True, "outline": existing, "added": req.extra_sequences}
    except Exception as e:
        raise HTTPException(500, f"续写大纲失败：{e}")


@router.post("/{book_id}/ai-generate/chapter-outlines")
async def ai_generate_chapter_outlines(book_id: str):
    """AI 根据大纲生成章纲"""
    load_env()
    s = sm(book_id)
    outline_path = s.state_dir / "outline.json"
    if not outline_path.exists():
        raise HTTPException(404, "大纲不存在")
    outline = json.loads(outline_path.read_text(encoding="utf-8"))

    # 读取每章字数配置
    try:
        cfg = s.read_config()
        target_words_ch = cfg.get("target_words_per_chapter", 2000)
    except Exception:
        target_words_ch = 2000

    # ── 读取世界观设定 ──
    world_ctx = ""
    for _fname in ("characters.json", "world.json"):
        _fp = s.state_dir / _fname
        if not _fp.exists():
            _fp = s.book_dir / "setup" / _fname
        if _fp.exists():
            try:
                world_ctx += f"\n{_fname}：{_fp.read_text(encoding='utf-8')[:800]}"
            except Exception:
                pass

    llm = create_llm()
    from core.llm import LLMMessage
    prompt = f"""根据以下故事大纲，生成详细的章纲。

大纲：{json.dumps(outline, ensure_ascii=False)[:4000]}
{f'''世界观设定（角色和地点必须使用以下已定义的，不能另编）：
{world_ctx}''' if world_ctx else ''}

每个章纲包含：
- chapter_number: 章号
- title: 章标题
- summary: 章节概述
- beats: 情节节拍数组（每个含 id, description, dramatic_function）
- emotional_arc: {{"start": "起始情绪", "end": "结束情绪"}}
- target_words: 目标字数（统一使用 {target_words_ch}）

返回 JSON 数组。"""
    try:
        resp = await run_sync(llm.complete, [LLMMessage(role="user", content=prompt)])
        import json as _json, re as _re
        data = _json.loads(_re.sub(r"^\s*```(?:json)?\s*", "", resp.content.strip(), flags=_re.MULTILINE).replace("```", "").strip())
        outlines = data if isinstance(data, list) else data.get("outlines", data.get("chapters", []))
        co_path = s.state_dir / "chapter_outlines.json"
        co_path.write_text(json.dumps(outlines, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, "outlines": outlines, "count": len(outlines)}
    except Exception as e:
        raise HTTPException(500, f"生成章纲失败：{e}")


@router.post("/{book_id}/ai-generate/detailed-outline")
async def ai_generate_detailed_outline(book_id: str, req: DetailedOutlineReq):
    """AI 生成某章的详细大纲"""
    load_env()
    s = sm(book_id)
    try:
        cfg = s.read_config()
        genre = cfg.get("genre", "玄幻")
        target_words = cfg.get("target_words_per_chapter", 2000)
    except Exception:
        genre = "玄幻"
        target_words = 2000
    llm = create_llm()
    from core.llm import LLMMessage
    # 读取故事大纲和本章章纲作为上下文
    outline_ctx = ""
    outline_path = s.state_dir / "outline.json"
    if outline_path.exists():
        try:
            outline_data = json.loads(outline_path.read_text(encoding="utf-8"))
            seqs = outline_data.get("sequences", [])
            outline_ctx = f"故事大纲序列：{json.dumps([{'id': sq.get('id',''), 'title': sq.get('title',''), 'summary': sq.get('summary','')} for sq in seqs[:10]], ensure_ascii=False)[:2000]}"
        except Exception:
            pass

    chapter_outline_ctx = ""
    co_path = s.state_dir / "chapter_outlines.json"
    if co_path.exists():
        try:
            all_cos = json.loads(co_path.read_text(encoding="utf-8"))
            for co in all_cos:
                if co.get("chapter_number") == req.chapter:
                    chapter_outline_ctx = f"本章章纲：{json.dumps(co, ensure_ascii=False)[:1500]}"
                    break
        except Exception:
            pass

    # 读取世界观
    world_ctx = ""
    for wf in ("world.json", "characters.json"):
        wp = s.state_dir / wf
        if not wp.exists():
            wp = s.book_dir / "setup" / wf  # fallback 到 setup/
        if wp.exists():
            try:
                world_ctx += f"\n{wf}：{wp.read_text(encoding='utf-8')[:1500]}"
            except Exception:
                pass

    llm = create_llm()
    from core.llm import LLMMessage
    prompt = f"""为第 {req.chapter} 章生成详细大纲（细纲）。

题材：{genre}
风格：{req.style}
每章目标字数：{target_words}字
{outline_ctx}
{chapter_outline_ctx}
{world_ctx}
{f'用户补充要点：{req.context}' if req.context else ''}

要求：
- 必须严格遵循章纲的情节方向，不能偏离故事主线
- 拆分为 2-4 个场景，每个场景包含地点、人物、冲突、情节节拍
- 规划伏笔植入点和章末钩子
- 情绪弧线要与章纲一致
- 每个场景用 weight（1-10）标注情节权重：过渡/铺垫=2-3，冲突推进=5-6，高潮/转折=8-10，收束=3-4。系统会按权重比例自动计算 word_budget

返回 JSON：{{"title": "...", "detailed_summary": "...", "scenes": [{{"scene_title": "...", "location": "...", "characters": ["..."], "goal": "...", "conflict": "...", "weight": 5, "beats": ["..."]}}], "hooks_to_plant": ["..."], "chapter_end_hook": "...", "emotional_arc": {{"start": "...", "end": "..."}}}}"""
    try:
        resp = await run_sync(llm.complete, [LLMMessage(role="user", content=prompt)])
        import json as _json, re as _re
        data = _json.loads(_re.sub(r"^\s*```(?:json)?\s*", "", resp.content.strip(), flags=_re.MULTILINE).replace("```", "").strip())
        data["chapter"] = req.chapter

        # ── 场景字数归一化：按 weight 比例分配 target_words ──
        scenes = data.get("scenes", [])
        if scenes:
            # 提取权重，默认 5
            weights = [max(1, min(10, sc.get("weight", 5))) for sc in scenes]
            total_weight = sum(weights)
            if total_weight == 0:
                total_weight = len(scenes)
                weights = [1] * len(scenes)

            # 按比例分配，至少 100 字/场景
            allocated = []
            remaining = target_words
            for i, w in enumerate(weights[:-1]):
                words = max(100, round(target_words * w / total_weight))
                allocated.append(words)
                remaining -= words
            allocated.append(max(100, remaining))  # 余数给最后一个

            # 写回 word_budget，删掉 weight
            for i, sc in enumerate(scenes):
                sc["word_budget"] = allocated[i]
                sc.pop("weight", None)

        out_dir = s.state_dir / "detailed_outlines"
        out_dir.mkdir(exist_ok=True)
        (out_dir / f"ch{req.chapter:04d}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, "outline": data}
    except Exception as e:
        raise HTTPException(500, f"生成详细大纲失败：{e}")


@router.get("/{book_id}/detailed-outline/{chapter}")
def get_detailed_outline(book_id: str, chapter: int):
    s = sm(book_id)
    path = s.state_dir / "detailed_outlines" / f"ch{chapter:04d}.json"
    if not path.exists():
        raise HTTPException(404, f"第 {chapter} 章详细大纲不存在")
    return json.loads(path.read_text(encoding="utf-8"))


@router.put("/{book_id}/detailed-outline/{chapter}")
def save_detailed_outline(book_id: str, chapter: int, data: dict):
    s = sm(book_id)
    out_dir = s.state_dir / "detailed_outlines"
    out_dir.mkdir(exist_ok=True)
    (out_dir / f"ch{chapter:04d}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True}


@router.post("/{book_id}/ai-generate/chapter-content")
async def ai_generate_chapter_content(book_id: str, req: ChapterContentReq):
    """AI 生成某章内容"""
    load_env()
    s = sm(book_id)
    try:
        cfg = s.read_config()
        genre = cfg.get("genre", "玄幻")
        target_words = cfg.get("target_words_per_chapter", 2000)
        style_guide = cfg.get("style_guide", "")
        forbidden = cfg.get("custom_forbidden_words", [])
    except Exception:
        genre, target_words, style_guide, forbidden = "玄幻", 2000, "", []

    # ── 1. 构造 scene_summaries（从章纲或详细大纲） ──
    scene_summaries = ""
    chapter_title = ""

    # 优先用详细大纲
    do_path = s.state_dir / "detailed_outlines" / f"ch{req.chapter:04d}.json"
    if do_path.exists():
        try:
            do = json.loads(do_path.read_text(encoding="utf-8"))
            chapter_title = do.get("title", "")
            scenes = do.get("scenes", [])
            parts = []
            for sc in scenes:
                stitle = sc.get("scene_title", sc.get("title", ""))
                budget = sc.get("word_budget", "")
                header = f"### {stitle}" if stitle else "### 场景"
                if budget:
                    header += f"（目标{budget}字）"
                parts.append(header)
                beats = sc.get("beats", [])
                for b in beats:
                    if isinstance(b, str):
                        parts.append(f"- {b}")
                    elif isinstance(b, dict):
                        parts.append(f"- {b.get('description', str(b))}")
            scene_summaries = "\n".join(parts) if parts else do.get("detailed_summary", "")
        except Exception:
            pass

    # 回退到章纲
    if not scene_summaries:
        co_path = s.state_dir / "chapter_outlines.json"
        if co_path.exists():
            try:
                all_cos = json.loads(co_path.read_text(encoding="utf-8"))
                for co in all_cos:
                    if co.get("chapter_number") == req.chapter:
                        chapter_title = co.get("title", "")
                        beats = co.get("beats", [])
                        parts = []
                        for b in beats:
                            if isinstance(b, dict):
                                parts.append(f"- {b.get('description', str(b))}")
                            else:
                                parts.append(f"- {str(b)}")
                        scene_summaries = "\n".join(parts) if parts else co.get("summary", "")
                        break
            except Exception:
                pass

    # 最终兜底
    if not scene_summaries:
        scene_summaries = f"第{req.chapter}章，请根据故事大纲推进剧情。"

    # ── 2. 构造 world_context（世界观+角色） ──
    world_ctx_parts = []
    for fname in ("world.json", "characters.json"):
        fp = s.state_dir / fname
        if not fp.exists():
            fp = s.book_dir / "setup" / fname  # fallback 到 setup/
        if fp.exists():
            try:
                world_ctx_parts.append(f"## {fname}\n{fp.read_text(encoding='utf-8')[:1200]}")
            except Exception:
                pass
    world_context = "\n\n".join(world_ctx_parts) if world_ctx_parts else "（世界观信息暂缺）"

    # ── 3. 构造 protagonist（从 characters.json 提取主角） ──
    from core.types.narrative import Character, CharacterNeed, CharacterWorldview, Obstacle
    protagonist = None
    char_path = s.state_dir / "characters.json"
    if not char_path.exists():
        char_path = s.book_dir / "setup" / "characters.json"  # fallback 到 setup/
    if char_path.exists():
        try:
            chars_data = json.loads(char_path.read_text(encoding="utf-8"))
            char_list = chars_data if isinstance(chars_data, list) else chars_data.get("characters", chars_data.get("main_characters", []))
            if char_list:
                c = char_list[0]
                # 尝试找到主角
                for ch in char_list:
                    if ch.get("role") in ("protagonist", "主角", "main") or ch.get("id") == cfg.get("protagonist_id", ""):
                        c = ch
                        break
                protagonist = Character(
                    id=c.get("id", "protagonist"),
                    name=c.get("name", "主角"),
                    need=CharacterNeed(
                        external=c.get("need", {}).get("external", c.get("external_goal", "生存")),
                        internal=c.get("need", {}).get("internal", c.get("internal_goal", "找到自我"))
                    ),
                    obstacles=[],
                    worldview=CharacterWorldview(
                        power=c.get("worldview", {}).get("power", "accepts"),
                        trust=c.get("worldview", {}).get("trust", "selective"),
                        coping=c.get("worldview", {}).get("coping", "fight")
                    ),
                    arc=c.get("arc", "positive"),
                    profile=c.get("profile", c.get("background", "")),
                    behavior_lock=c.get("behavior_lock", []),
                    role=c.get("role", "protagonist"),
                    current_goal=c.get("current_goal", ""),
                    hidden_agenda=c.get("hidden_agenda", "")
                )
        except Exception:
            pass
    if protagonist is None:
        protagonist = Character(
            id="protagonist", name="主角",
            need=CharacterNeed(external="生存", internal="找到自我"),
            obstacles=[], worldview=CharacterWorldview(power="accepts", trust="selective", coping="fight"),
            arc="positive", profile="", behavior_lock=[]
        )

    # ── 4. 构造 ArchitectBlueprint ──
    from core.agents.architect import ArchitectBlueprint, PreWriteChecklist
    # 从章纲提取信息
    hooks_to_plant = []
    chapter_end_hook = ""
    core_conflict = ""
    emotional_journey = {"start": "平静", "end": "紧张"}

    # 从详细大纲提取
    if do_path.exists():
        try:
            do = json.loads(do_path.read_text(encoding="utf-8"))
            hooks_to_plant = do.get("hooks_to_plant", [])
            chapter_end_hook = do.get("chapter_end_hook", "") or do.get("结尾钩子", "") or do.get("ending_hook", "")
            ea = do.get("emotional_arc", {})
            if ea:
                emotional_journey = {"start": ea.get("start", "平静"), "end": ea.get("end", "紧张")}
        except Exception:
            pass

    # 从章纲提取
    co_path2 = s.state_dir / "chapter_outlines.json"
    if co_path2.exists():
        try:
            all_cos2 = json.loads(co_path2.read_text(encoding="utf-8"))
            for co in all_cos2:
                if co.get("chapter_number") == req.chapter:
                    ea = co.get("emotional_arc", {})
                    if ea and not emotional_journey.get("start"):
                        emotional_journey = {"start": ea.get("start", "平静"), "end": ea.get("end", "紧张")}
                    break
        except Exception:
            pass

    blueprint = ArchitectBlueprint(
        core_conflict=core_conflict or "推进剧情",
        hooks_to_advance=[],
        hooks_to_plant=hooks_to_plant,
        emotional_journey=emotional_journey,
        chapter_end_hook=chapter_end_hook,
        pace_notes="",
        pre_write_checklist=PreWriteChecklist(
            active_characters=[protagonist.name],
            required_locations=[],
            resources_in_play=[],
            hooks_status=[],
            risk_scan=""
        )
    )

    # ── 5. 读取前文摘要 ──
    prior_summaries = req.previous_summary
    if not prior_summaries:
        summary_path = s.state_dir / "chapter_summaries.md"
        if summary_path.exists():
            prior_summaries = summary_path.read_text(encoding="utf-8")[-3000:]

    # ── 6. 读取伏笔/因果链/情感弧线 ──
    pending_hooks = ""
    hooks_path = s.state_dir / "hooks.json"
    if hooks_path.exists():
        try:
            hooks = json.loads(hooks_path.read_text(encoding="utf-8"))
            open_hooks = [h for h in hooks if not h.get("resolved")]
            pending_hooks = "\n".join(f"- {h.get('description','')}" for h in open_hooks[:10])
        except Exception:
            pass

    causal_chain = ""
    cc_path = s.state_dir / "causal_chain.json"
    if cc_path.exists():
        try:
            cc = json.loads(cc_path.read_text(encoding="utf-8"))
            causal_chain = json.dumps(cc[-5:], ensure_ascii=False) if isinstance(cc, list) else str(cc)
        except Exception:
            pass

    emotional_arcs = ""
    ea_path = s.state_dir / "emotional_arcs.json"
    if ea_path.exists():
        try:
            emotional_arcs = ea_path.read_text(encoding="utf-8")[-1000:]
        except Exception:
            pass

    # ── 7. 调用 WriterAgent（逐场景调用，确保每个场景都覆盖） ──
    from core.agents import WriterAgent
    chapter_max_tokens = min(8192, max(2048, int(target_words * 3.5)))
    llm = create_llm(max_tokens=chapter_max_tokens)
    writer = WriterAgent(llm, style_guide=style_guide, genre=genre)

    # ── 解析场景列表 ──
    _scenes_list = []  # [(header_str, beats_lines_str, budget_int), ...]
    _do_path = s.state_dir / "detailed_outlines" / f"ch{req.chapter:04d}.json"
    if _do_path.exists():
        try:
            _do = json.loads(_do_path.read_text(encoding="utf-8"))
            for _sc in _do.get("scenes", []):
                _stitle = _sc.get("scene_title", _sc.get("title", ""))
                _budget_str = _sc.get("word_budget", "")
                _budget_int = 0
                if _budget_str:
                    try: _budget_int = int(_budget_str)
                    except: pass
                _header = f"### {_stitle}" if _stitle else "### 场景"
                if _budget_str:
                    _header += f"（目标{_budget_str}字）"
                _beats_parts = []
                for _b in _sc.get("beats", []):
                    if isinstance(_b, str):
                        _beats_parts.append(f"- {_b}")
                    elif isinstance(_b, dict):
                        _beats_parts.append(f"- {_b.get('description', str(_b))}")
                # V7.10: 提取场景级额外信息（叙事手法/伏笔/结尾钩子）
                _extra_parts = []
                _narr = _sc.get("narrative_technique", _sc.get("叙事手法", ""))
                if _narr:
                    _extra_parts.append(f"叙事手法：{_narr}")
                _foil = _sc.get("foreshadowing", _sc.get("埋伏笔", ""))
                if _foil:
                    _extra_parts.append(f"埋伏笔：{_foil}")
                _hook = _sc.get("ending_hook", _sc.get("结尾钩子", ""))
                if _hook:
                    _extra_parts.append(f"结尾钩子：{_hook}")
                _scenes_list.append((_header, "\n".join(_beats_parts), _budget_int, "\n".join(_extra_parts)))
        except Exception:
            pass

    try:
        # 如果没有解析到分场景（<=2个），降级为单次调用
        if len(_scenes_list) <= 2:
            result = await run_sync(
                writer.write_chapter,
                scene_summaries, blueprint, protagonist, world_context,
                req.chapter, target_words,
                prior_summaries=prior_summaries, chapter_title=chapter_title,
                pending_hooks=pending_hooks, causal_chain=causal_chain,
                emotional_arcs=emotional_arcs,
            )
            content = result.content
            settlement = result.settlement
        else:
            # ── 逐场景调用：每个场景单独一次 LLM 调用 ──
            _all_parts = []
            _settlement = None
            _scene_count = len(_scenes_list)
            for _idx in range(_scene_count):
                _item = _scenes_list[_idx]
                _header, _beats, _budget = _item[0], _item[1], _item[2]
                _extra = _item[3] if len(_item) > 3 else ""
                _scene_summary = f"{_header}\n{_beats}"
                _scene_target = _budget if _budget > 0 else target_words // _scene_count
                # V7.12: 节拍进度标记 — 告诉 LLM 本场景有几个节拍、已完成/未完成
                _beat_lines = [l for l in _beats.strip().split("\n") if l.strip().startswith("-")]
                _total_beats = len(_beat_lines)
                # V7.11: 强制要求按节拍顺序写
                _scene_summary += f"\n\n【强制要求】本场景共{_total_beats}个节拍，必须逐一展开写成完整小说正文，不能跳过、合并或替换任何节拍。字数预算约{_scene_target}字，不能超{_scene_target*1.2:.0f}字。"
                # V7.10: 注入叙事手法等额外信息
                if _extra:
                    _scene_summary += f"\n\n【本场景要求】\n{_extra}"
                # V7.12: 不在场景 prompt 中注入结尾钩子，避免 LLM 急于到达钩子点而跳过节拍
                # 钩子由后处理拼接到最后一个场景末尾
                # 前面已写内容作为上下文（取最后400字，避免膨胀）
                # V7.12: 最后一个场景不传 prior_ctx，把 token 空间留给节拍内容
                _prior_ctx = ""
                if _idx < _scene_count - 1 and _all_parts:
                    _written_so_far = "\n\n".join(_all_parts)
                    _prior_ctx = f"### 本章已写内容（续写时直接接续，不要重复以上内容）\n{_written_so_far[-400:]}"
                elif _idx == 0:
                    _prior_ctx = prior_summaries
                # V7.12: 每个场景独立 max_tokens（而非全局 target×3.5）
                _scene_max_tokens = min(8192, max(2048, int(_scene_target * 2.5)))
                _scene_llm = create_llm(max_tokens=_scene_max_tokens)
                _scene_writer = WriterAgent(_scene_llm, style_guide=style_guide, genre=genre)

                _result = await run_sync(
                    _scene_writer.write_chapter,
                    _scene_summary,       # 只传这一个场景
                    blueprint, protagonist, world_context,
                    req.chapter, _scene_target,
                    prior_summaries=_prior_ctx,
                    chapter_title=chapter_title if _idx == 0 else "",  # 只有第一个场景带标题
                    pending_hooks=pending_hooks, causal_chain=causal_chain,
                    emotional_arcs=emotional_arcs,
                )
                _part = _result.content.strip()
                # ── 场景级字数截断：超过 budget×1.2 强制截断 ──
                if _scene_target > 0:
                    _max_scene_chars = int(_scene_target * 1.2)
                    _raw_len = len(_part)
                    if _raw_len > _max_scene_chars:
                        _cut = _part.rfind("。", int(_scene_target * 0.8), _max_scene_chars + 100)
                        if _cut > int(_scene_target * 0.8):
                            _part = _part[:_cut+1]
                        else:
                            _part = _part[:_max_scene_chars]
                        logger.info(f"[V7.12] Scene{_idx+1}: {_raw_len}chars -> {len(_part)}chars (target={_scene_target}, max={_max_scene_chars})")
                    else:
                        logger.info(f"[V7.12] Scene{_idx+1}: {_raw_len}chars (target={_scene_target}, max={_max_scene_chars}, NO TRUNCATE)")
                else:
                    logger.info(f"[V7.12] Scene{_idx+1}: _scene_target={_scene_target}, SKIPPING truncation")
                # 去掉非首个场景可能重复的章节标题
                if _idx > 0:
                    _title_pat = re.compile(r'^#\s*第\d+章[^\n]*\n*', re.MULTILINE)
                    _part = _title_pat.sub('', _part, count=1).strip()
                # V7.11: 场景间去重 - 移除与上一个场景尾部重叠的段落（带安全保护）
                if _all_parts and _part:
                    _prev = _all_parts[-1]
                    _orig_len = len(_part)
                    for _overlap in range(min(300, len(_prev)), 49, -10):
                        _tail = _prev[-_overlap:].strip()
                        if _tail and _tail in _part:
                            _cut = _part.index(_tail) + len(_tail)
                            _candidate = _part[_cut:].strip()
                            # 安全保护：去重后长度不足原文30%则跳过，避免误杀整个场景
                            if len(_candidate) >= _orig_len * 0.3:
                                _part = _candidate
                            break
                # 跳过空场景（不足50字视为无效）
                if _part and len(_part) > 50:
                    _all_parts.append(_part)
                _settlement = _result.settlement or _settlement

            content = "\n\n".join(_all_parts)
            settlement = _settlement
            logger.info(f"[V7.12] Per-scene done: {_scene_count} scenes, total {len(content)} chars, chapter_end_hook={chapter_end_hook[:50]!r}")

            # ── V7.12b: 结尾钩子后处理 — 检查钩子是否在最后一个场景中，不在则追加 ──
            if _all_parts and chapter_end_hook:
                _last_part = _all_parts[-1]
                # 检查结尾钩子关键词是否出现在最后一个场景中
                _hook_matched = False
                # 用多个关键词片段做宽松匹配
                for _kw_len in (30, 20, 15, 10):
                    _kw = chapter_end_hook[:_kw_len]
                    if _kw and _kw in _last_part:
                        _hook_matched = True
                        break
                logger.info(f"[V7.12] Hook check: matched={_hook_matched}, hook_start={chapter_end_hook[:30]!r}, last_scene_chars={len(_last_part)}")
                if not _hook_matched:
                    # 提取钩子的核心动作描述，拼接为自然段落
                    _hook_text = chapter_end_hook.strip()
                    # 去掉可能的引导语前缀
                    for _prefix in ("林默从坟场的噩梦惊醒后，", "林默从坟场的噩梦惊醒后,"):
                        if _hook_text.startswith(_prefix):
                            _hook_text = _hook_text[len(_prefix):]
                            break
                    _hook_para = f"\n\n{_hook_text[:300]}"
                    _all_parts[-1] = _last_part + _hook_para
                    content = "\n\n".join(_all_parts)
                    logger.info(f"[V7.12] Hook appended ({len(_hook_para)}chars)")
                # 检查最后一个场景的节拍完整性
                _last_beats = [l.strip("- ").strip() for l in _beats.strip().split("\n") if l.strip().startswith("-")]
                _missing = []
                for _b in _last_beats:
                    _kw = _b[:12] if len(_b) > 12 else _b
                    if _kw and _kw not in _last_part and _kw[:6] not in _last_part:
                        _missing.append(_b[:30])
                if _missing:
                    logger.warning(f"[V7.12] Last scene missing beats: {_missing}")

        # 后处理：超过目标120%则截断
        max_chars = int(target_words * 1.2)
        if len(content) > max_chars:
            cut_pos = content.rfind("\n\n", int(target_words * 0.8), max_chars + 200)
            if cut_pos > int(target_words * 0.8):
                content = content[:cut_pos]
            else:
                cut_pos = content.rfind("。", int(target_words * 0.8), max_chars + 100)
                if cut_pos > int(target_words * 0.8):
                    content = content[:cut_pos+1]
                else:
                    content = content[:max_chars]
        s.save_draft(req.chapter, content)
        return {"ok": True, "content": content, "chars": len(content),
                "settlement": dc_to_dict(settlement) if settlement else None}
    except Exception as e:
        raise HTTPException(500, f"生成章节内容失败：{e}")
