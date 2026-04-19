"""
/writing 写作+审计+修订（V6 修复版）

修复内容：
- continue_writing / action_write：正确构造 WritingPipeline
- three_layer_audit：正确调用 auditor.audit_chapter
- action_revise：路由路径修复（移除重复前缀）
- 所有端点：添加错误恢复 checkpoint 支持
"""
from __future__ import annotations

import json
import logging
import asyncio
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from ..deps import (
    sm, load_env, create_llm, run_sync, dc_to_dict,
    ContinueWritingReq, SegmentRewriteReq, ThreeLayerAuditReq,
)

router = APIRouter(prefix="/api/books", tags=["writing"])


def _strip_blueprint(text: str) -> str:
    """剥离修订后 LLM 可能混入的蓝图/元信息（与 writer.py 后处理一致）"""
    import re as _re
    content = text
    # 第1轮：删除 "写前蓝图" 等标题段落
    content = _re.sub(
        r'(?:^|\n)#{1,3}\s*(?:写前蓝图|写作蓝图|章节大纲|章节细纲)[\s\S]*?(?=\n#{1,3}\s|\n键盘|\n【|\n　|\n[A-Z\u4e00-\u9fff]{2,})',
        '', content, flags=_re.MULTILINE
    ).strip()
    # 第2轮：删除元叙述引用
    content = _re.sub(
        r'(?:^|\n)(?:但是)?(?:章节大纲|章节细纲|大纲|细纲|环节[一二三四五六七八九十]|细章)[^\n]{0,20}里写着[：:][\s\S]*?(?=\n\n|\Z)',
        '', content, flags=_re.MULTILINE
    ).strip()
    # 第3轮：删除细纲格式内容
    for _pat in [
        r'(?:^|\n)(?:细纲|详细大纲|场景拆分)[^\n]*',
        r'(?:^|\n)\s*(?:目标|冲突|节拍|埋伏笔|结尾钩子)\s*[：:].*',
        r'(?:^|\n)\s*\*\s*(?:目标|冲突|节拍|埋伏笔|结尾钩子)\s*[：:].*',
        r'(?:^|\n)编辑\s*$',
        r'(?:^|\n)收起/展开\s*$',
        r'(?:^|\n)###\s*写后结算表[\s\S]*?(?=\n---|\n#{1,3}|\Z)',
        r'(?:^|\n)###\s*核心任务完成状态[\s\S]*?(?=\n---|\n#{1,3}|\Z)',
        r'(?:^|\n)\*\*\s*(?:新开伏笔|闭合.*伏笔|角色状态变化|与蓝图偏差)\s*\*\*[\s\S]*?(?=\n\n|\Z)',
    ]:
        content = _re.sub(_pat, '', content, flags=_re.MULTILINE)
    # 第4轮：如果 "核心冲突" 和 "情感旅程" 同时出现在前500字，截掉
    if '核心冲突' in content[:500] and '情感旅程' in content[:500]:
        _lines = content.split('\n')
        _cut = 0
        for _i, _l in enumerate(_lines):
            _lstrip = _l.strip()
            if _lstrip.startswith('**核心冲突') or _lstrip.startswith('* **核心冲突'):
                _start = _i
                for _j in range(_i-1, max(_i-5, -1), -1):
                    if _lines[_j].strip().startswith('#') or not _lines[_j].strip():
                        _start = _j
                        break
                _end = _i
                for _j in range(_i+1, min(_i+30, len(_lines))):
                    if _lines[_j].strip() == '' and _j > _i + 3:
                        _end = _j + 1
                        break
                    if any(kw in _lines[_j] for kw in ['键盘声', '屏幕', '他', '她', '门', '走廊']):
                        _end = _j
                        break
                _cut = len('\n'.join(_lines[:_start]))
                break
        if _cut > 0:
            content = content[_cut:].lstrip('\n')
    return content.strip()


def _build_pipeline(s, llm=None):
    """构造 WritingPipeline 的公共逻辑（V6 修复）"""
    from core.pipeline import WritingPipeline, PipelineConfig
    from core.narrative import NarrativeEngine
    from core.agents import (
        ArchitectAgent, WriterAgent, AuditorAgent, ReviserAgent,
        SummaryAgent, PatrolAgent,
        DialogueExpert, EmotionCurveDesigner, CharacterGrowthExpert,
        FeedbackExpert, StyleConsistencyChecker, SceneArchitect,
        PsychologicalPortrayalExpert, MiroFishReader,
    )
    from core.validators import PostWriteValidator
    from core.quality_dashboard import QualityDashboard
    from core.dynamic_planner import DynamicPlanner
    from core.kb_incentive import KBIncentiveTracker
    from core.setup import SetupLoader
    from ..deps import PROJECT_ROOT

    if llm is None:
        llm = create_llm()

    # 加载书籍状态
    try:
        state = SetupLoader.restore(str(PROJECT_ROOT), s.book_id)
    except Exception:
        # fallback：手动读取配置
        try:
            cfg = s.read_config()
        except FileNotFoundError:
            raise HTTPException(404, f"书籍不存在：{s.book_id}")
        state = None

    # 确定主角
    all_chars = list(state.characters.values()) if state else []
    protagonist = None
    if state:
        pid = state.config.protagonist_id
        if pid in state.characters:
            protagonist = state.characters[pid]
        else:
            for c in all_chars:
                if getattr(c, "role", "") in ("protagonist", "主角"):
                    protagonist = c
                    break
            if not protagonist and all_chars:
                protagonist = all_chars[0]

    if not protagonist:
        raise HTTPException(400, "书籍缺少角色配置，请先运行 setup load")

    # 创建各组件
    auditor_llm = create_llm(temperature=0.0, model_env="AUDITOR_MODEL")
    engine = NarrativeEngine(llm)
    config = PipelineConfig.from_env()

    style_guide = ""
    genre = "玄幻"
    forbidden_words = []
    if state:
        style_guide = state.config.style_guide
        genre = state.config.genre
        forbidden_words = state.config.custom_forbidden_words

    pipeline = WritingPipeline(
        state_manager=s,
        architect=ArchitectAgent(llm),
        writer=WriterAgent(llm, style_guide=style_guide, genre=genre),
        auditor=AuditorAgent(auditor_llm),
        reviser=ReviserAgent(llm),
        narrative_engine=engine,
        summary_agent=SummaryAgent(llm),
        validator=PostWriteValidator(forbidden_words),
        protagonist=protagonist,
        all_characters=all_chars,
        patrol=PatrolAgent(llm),
        dashboard=QualityDashboard(),
        dynamic_planner=DynamicPlanner() if (s.book_dir / "dynamic_planner.json").exists() else None,
        kb_tracker=KBIncentiveTracker(),
        # V4 增强 Agent
        dialogue_expert=DialogueExpert(llm),
        emotion_curve_designer=EmotionCurveDesigner(llm),
        character_growth_expert=CharacterGrowthExpert(llm),
        feedback_expert=FeedbackExpert(llm),
        style_checker=StyleConsistencyChecker(llm),
        scene_architect=SceneArchitect(llm),
        psychological_expert=PsychologicalPortrayalExpert(llm),
        mirofish_reader=MiroFishReader(llm),
        config=config,
    )

    # WebSocket 进度回调（延迟导入避免循环依赖）
    try:
        import importlib
        _server = importlib.import_module("core.server")
        _ws = getattr(_server, "ws_manager", None)
        if _ws:
            pipeline.set_progress_callback(
                lambda data: asyncio.ensure_future(_ws.broadcast(s.book_id, data))
            )
    except Exception:
        pass

    return pipeline, all_chars


def _get_next_chapter(s) -> int:
    """获取下一章号"""
    try:
        ws = s.read_world_state()
        return (ws.current_chapter or 0) + 1
    except Exception:
        return 1


@router.post("/{book_id}/continue-writing")
async def continue_writing(book_id: str, req: ContinueWritingReq):
    """续写指定数量的章节（V6 修复版）"""
    load_env()
    s = sm(book_id)
    try:
        s.read_config()
    except FileNotFoundError:
        raise HTTPException(404, f"书籍不存在：{book_id}")

    from core.narrative import ChapterOutlineSchema
    from ..deps import PROJECT_ROOT

    # 加载章纲
    chapter_outlines_path = s.state_dir / "chapter_outlines.json"
    if not chapter_outlines_path.exists():
        raise HTTPException(400, "章纲不存在，请先生成大纲")

    raw = json.loads(chapter_outlines_path.read_text(encoding="utf-8"))
    from core.llm import _fix_df
    for r in raw:
        if r.get("dramatic_function"):
            r["dramatic_function"] = _fix_df(r["dramatic_function"])
        for bi, beat in enumerate(r.get("beats", [])):
            if not beat.get("id"):
                beat["id"] = f"beat_{r.get('chapter_number', bi)}_{bi+1}"
            if beat.get("dramatic_function"):
                beat["dramatic_function"] = _fix_df(beat["dramatic_function"])
    all_outlines = [ChapterOutlineSchema.model_validate(r) for r in raw]

    pipeline, _ = _build_pipeline(s)
    next_ch = _get_next_chapter(s)

    # V6: 加载上一次的 checkpoint（如有）
    checkpoint_path = s.book_dir / "pipeline_checkpoint.json"
    start_offset = 0
    if checkpoint_path.exists():
        try:
            ckpt = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            if ckpt.get("status") == "interrupted":
                start_offset = ckpt.get("completed_count", 0)
                logging.info(f"[V6] 从 checkpoint 恢复：已完成 {start_offset} 章")
        except Exception:
            pass

    results = []
    for i in range(start_offset, req.count):
        ch_num = next_ch + i
        if ch_num > len(all_outlines):
            results.append({"chapter": ch_num, "status": "all_done"})
            break

        # V6: 写 checkpoint
        try:
            checkpoint_path.write_text(json.dumps({
                "status": "running",
                "total": req.count,
                "completed_count": i,
                "current_chapter": ch_num,
            }, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

        co = all_outlines[ch_num - 1]
        try:
            result = await run_sync(pipeline.run, co, False)
            results.append({
                "chapter": ch_num,
                "title": co.title,
                "ok": True,
                "audit_passed": result.audit_report.passed,
                "revision_rounds": result.revision_rounds,
                "word_count": result.word_count,
                "causal_links": result.causal_links,
                "total_rework": result.total_rework_count,
            })
        except Exception as e:
            logging.error(f"续写第 {ch_num} 章失败: {e}", exc_info=True)
            results.append({"chapter": ch_num, "error": str(e)})
            # V6: 中断时保存 checkpoint
            try:
                checkpoint_path.write_text(json.dumps({
                    "status": "interrupted",
                    "total": req.count,
                    "completed_count": i,
                    "failed_chapter": ch_num,
                    "error": str(e),
                }, ensure_ascii=False), encoding="utf-8")
            except Exception:
                pass
            break  # 中断后停止，保留 checkpoint 供恢复

    # V6: 完成后清除 checkpoint
    if len(results) == req.count or all(r.get("ok") or r.get("status") == "all_done" for r in results):
        try:
            if checkpoint_path.exists():
                checkpoint_path.write_text(json.dumps({"status": "completed"}, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    return {"ok": True, "results": results}


@router.post("/{book_id}/three-layer-audit")
async def three_layer_audit(book_id: str, req: ThreeLayerAuditReq):
    """三层审计（V6 修复版）"""
    load_env()
    s = sm(book_id)
    from core.agents import AuditorAgent, ArchitectBlueprint, PreWriteChecklist, PostWriteSettlement

    llm = create_llm(temperature=0.0, model_env="AUDITOR_MODEL")
    auditor = AuditorAgent(llm)

    content = s.read_final(req.chapter) or s.read_draft(req.chapter)
    if not content:
        raise HTTPException(404, f"第 {req.chapter} 章不存在")

    # 构造 blueprint（从章纲读取，或使用空默认值）
    from core.narrative import ChapterOutlineSchema
    from core.types.state import TruthFileKey

    blueprint = ArchitectBlueprint(
        core_conflict="",
        hooks_to_advance=[],
        hooks_to_plant=[],
        emotional_journey={},
        chapter_end_hook="",
        pace_notes="",
        pov_character_id="",
        pre_write_checklist=PreWriteChecklist([], [], [], [], ""),
    )

    # 尝试从章纲获取更完整的信息
    outline_path = s.state_dir / "chapter_outlines.json"
    if outline_path.exists():
        try:
            outlines = json.loads(outline_path.read_text(encoding="utf-8"))
            for co in outlines:
                if co.get("chapter_number") == req.chapter:
                    blueprint = ArchitectBlueprint(
                        core_conflict=co.get("summary", ""),
                        hooks_to_advance=co.get("hooks_to_advance", []),
                        hooks_to_plant=co.get("hooks_to_plant", []),
                        emotional_journey=co.get("emotional_arc", {}),
                        chapter_end_hook=co.get("chapter_end_hook", ""),
                        pace_notes=co.get("pace_notes", ""),
                        pov_character_id=co.get("pov_character_id", ""),
                        pre_write_checklist=PreWriteChecklist([], [], [], [], ""),
                    )
                    break
        except Exception:
            pass

    truth_ctx = s.read_truth_bundle([
        TruthFileKey.CURRENT_STATE,
        TruthFileKey.CHARACTER_MATRIX,
        TruthFileKey.PENDING_HOOKS,
    ])

    settlement = PostWriteSettlement([], [], [], [], [])

    try:
        report = await run_sync(
            auditor.audit_chapter,
            content, req.chapter, blueprint, truth_ctx, settlement,
            cross_thread_context="",
        )
        r = dc_to_dict(report)

        # Reshape AuditReport → 3-layer format for frontend
        LAYER_MAP = {
            "文笔去AI化": "language", "对话质量": "language", "风格一致": "language", "场景构建": "language", "心理刻画": "language",
            "逻辑自洽": "structure", "设定一致": "structure", "结构合理": "structure",
            "人物OOC": "drama",
        }
        layers = {"language": {"passed": True, "issues": []}, "structure": {"passed": True, "issues": []}, "drama": {"passed": True, "issues": []}}
        for iss in r.get("issues", []):
            dim = iss.get("dimension", "")
            lk = LAYER_MAP.get(dim, "language")
            layers[lk]["issues"].append(iss)
        for k in layers:
            if any(i.get("severity") == "critical" for i in layers[k]["issues"]):
                layers[k]["passed"] = False

        resp = {
            "ok": True,
            "chapter": r.get("chapter_number", req.chapter),
            "passed": r.get("passed", True),
            "summary": r.get("overall_note", ""),
            "layers": layers,
            "dimension_scores": r.get("dimension_scores", {}),
            "weighted_total": r.get("weighted_total", 0),
            "redline_violations": r.get("redline_violations", []),
        }

        # Save audit result to disk
        audit_dir = s.state_dir / "audits"
        audit_dir.mkdir(parents=True, exist_ok=True)
        (audit_dir / f"audit_ch{req.chapter:04d}.json").write_text(json.dumps(resp, ensure_ascii=False, indent=2), encoding="utf-8")

        return resp
    except Exception as e:
        raise HTTPException(500, f"审计失败：{e}")


@router.post("/{book_id}/revise")
async def action_revise(book_id: str, chapter: int = Query(...), mode: str = Query("spot-fix")):
    """手动触发修订（V6 修复版：修正路由路径）"""
    load_env()
    s = sm(book_id)
    from core.agents import ReviserAgent, AuditorAgent, ArchitectBlueprint, PreWriteChecklist, PostWriteSettlement
    from core.types.state import TruthFileKey

    content = s.read_final(chapter) or s.read_draft(chapter)
    if not content:
        raise HTTPException(404, f"第 {chapter} 章不存在")

    llm = create_llm()
    reviser = ReviserAgent(llm)

    # 先审计获取 issues
    auditor_llm = create_llm(temperature=0.0, model_env="AUDITOR_MODEL")
    auditor = AuditorAgent(auditor_llm)
    blueprint = ArchitectBlueprint(
        core_conflict="", hooks_to_advance=[], hooks_to_plant=[],
        emotional_journey={}, chapter_end_hook="", pace_notes="",
        pov_character_id="",
        pre_write_checklist=PreWriteChecklist([], [], [], [], ""),
    )
    truth_ctx = s.read_truth_bundle([TruthFileKey.CURRENT_STATE, TruthFileKey.PENDING_HOOKS])
    settlement = PostWriteSettlement([], [], [], [], [])

    try:
        report = await run_sync(auditor.audit_chapter, content, chapter, blueprint, truth_ctx, settlement,
                                 cross_thread_context="")
        result = await run_sync(reviser.revise, content, report.issues, mode)
        # 字数控制 + 蓝图剥离
        try:
            cfg = s.read_config()
            target_words = cfg.get("target_words_per_chapter", 2000)
        except Exception:
            target_words = 2000
        max_chars = int(target_words * 1.2)
        revised = _strip_blueprint(result.content)
        if len(revised) > max_chars:
            cut_pos = revised.rfind("\n\n", int(target_words * 0.8), max_chars + 200)
            if cut_pos > int(target_words * 0.8):
                revised = revised[:cut_pos]
            else:
                cut_pos = revised.rfind("。", int(target_words * 0.8), max_chars + 100)
                if cut_pos > int(target_words * 0.8):
                    revised = revised[:cut_pos+1]
                else:
                    revised = revised[:max_chars]
        s.save_draft(chapter, revised)
        final_path = s.chapter_dir / f"ch{chapter:04d}_final.md"
        if final_path.exists():
            final_path.unlink()
        return {"ok": True, "changes": result.change_log, "issues_count": len(report.issues)}
    except Exception as e:
        raise HTTPException(500, f"修订失败：{e}")


@router.post("/{book_id}/auto-revise-loop")
async def auto_revise_loop(book_id: str, chapter: int = Query(...), max_rounds: int = Query(5)):
    """循环自动修订：审计→修订→再审计，直到通过或达到上限"""
    load_env()
    s = sm(book_id)
    from core.agents import ReviserAgent, AuditorAgent, ArchitectBlueprint, PreWriteChecklist, PostWriteSettlement
    from core.types.state import TruthFileKey

    auditor_llm = create_llm(temperature=0.0, model_env="AUDITOR_MODEL")
    auditor = AuditorAgent(auditor_llm)
    reviser_llm = create_llm()
    reviser = ReviserAgent(reviser_llm)

    # ── 从章纲构建 blueprint（与 three-layer-audit 一致，避免审计员拿不到参照标准）──
    blueprint = ArchitectBlueprint(
        core_conflict="", hooks_to_advance=[], hooks_to_plant=[],
        emotional_journey={}, chapter_end_hook="", pace_notes="",
        pov_character_id="",
        pre_write_checklist=PreWriteChecklist([], [], [], [], ""),
    )
    _outline_path = s.state_dir / "chapter_outlines.json"
    if _outline_path.exists():
        try:
            _outlines = json.loads(_outline_path.read_text(encoding="utf-8"))
            for _co in _outlines:
                if int(_co.get("chapter_number", 0)) == int(chapter):
                    blueprint = ArchitectBlueprint(
                        core_conflict=_co.get("summary", ""),
                        hooks_to_advance=_co.get("hooks_to_advance", []),
                        hooks_to_plant=_co.get("hooks_to_plant", []),
                        emotional_journey=_co.get("emotional_arc", {}),
                        chapter_end_hook=_co.get("chapter_end_hook", ""),
                        pace_notes=_co.get("pace_notes", ""),
                        pov_character_id=_co.get("pov_character_id", ""),
                        pre_write_checklist=PreWriteChecklist([], [], [], [], ""),
                    )
                    break
        except Exception:
            pass
    truth_ctx = s.read_truth_bundle([TruthFileKey.CURRENT_STATE, TruthFileKey.CHARACTER_MATRIX, TruthFileKey.PENDING_HOOKS])
    settlement = PostWriteSettlement([], [], [], [], [])

    # 读取当前内容（优先 draft，因为修订操作目标是 draft）
    content = s.read_draft(chapter) or s.read_final(chapter)
    if not content:
        raise HTTPException(404, f"第 {chapter} 章不存在")

    # 修订前备份（不删 final，只备份 draft）
    import shutil as _shutil
    draft_path = s.chapter_dir / f"ch{chapter:04d}_draft.md"
    if draft_path.exists():
        _backup = s.chapter_dir / f"ch{chapter:04d}_draft.bak.md"
        _shutil.copy2(draft_path, _backup)
        logging.info(f"[V7.22] Backed up draft to {_backup.name}")

    rounds_log = []
    for round_num in range(1, max_rounds + 1):
        try:
            report = await run_sync(auditor.audit_chapter, content, chapter, blueprint, truth_ctx, settlement,
                                     cross_thread_context="")
        except Exception as e:
            rounds_log.append({"round": round_num, "error": f"审计失败: {e}"})
            break

        passed = report.passed
        issue_count = len(report.issues)

        # 记录每轮 issues 详情（用于前端展示）
        issues_detail = []
        for i in report.issues:
            issues_detail.append({
                "severity": i.severity, "dimension": i.dimension,
                "description": i.description, "location": i.location or "",
                "suggestion": i.suggestion or "",
            })
        rounds_log.append({
            "round": round_num, "passed": passed,
            "issues_count": issue_count, "weighted_total": report.weighted_total,
            "issues": issues_detail,
        })

        # 持久化审计结果（每轮都保存，确保前端刷新后能看到最新，使用与 three-layer-audit 相同的格式）
        audit_dir = s.state_dir / "audits"
        audit_dir.mkdir(exist_ok=True)
        _report_dict = dc_to_dict(report)
        # Reshape to 3-layer format (same as three-layer-audit)
        _LAYER_MAP = {
            "文笔去AI化": "language", "对话质量": "language", "风格一致": "language", "场景构建": "language", "心理刻画": "language",
            "逻辑自洽": "structure", "设定一致": "structure", "结构合理": "structure",
            "人物OOC": "drama",
        }
        _layers = {"language": {"passed": True, "issues": []}, "structure": {"passed": True, "issues": []}, "drama": {"passed": True, "issues": []}}
        for _iss in _report_dict.get("issues", []):
            _dim = _iss.get("dimension", "")
            _lk = _LAYER_MAP.get(_dim, "language")
            _layers[_lk]["issues"].append(_iss)
        for _k in _layers:
            if any(_i.get("severity") == "critical" for _i in _layers[_k]["issues"]):
                _layers[_k]["passed"] = False
        _resp = {
            "ok": True, "chapter": chapter, "passed": passed,
            "summary": f"Round {round_num}: {issue_count} issues, score={report.weighted_total}",
            "layers": _layers,
            "dimension_scores": _report_dict.get("dimension_scores", {}),
            "weighted_total": _report_dict.get("weighted_total", 0),
            "redline_violations": _report_dict.get("redline_violations", []),
        }
        (audit_dir / f"audit_ch{chapter:04d}.json").write_text(
            json.dumps(_resp, ensure_ascii=False, indent=2), encoding="utf-8")
        logging.info(f"[V7.22] Round {round_num}: {issue_count} issues, passed={passed}, score={report.weighted_total}")

        # 日志输出每个 issue（调试可见性）
        for i in report.issues:
            logging.info(f"[V7.22]   [{i.severity}] {i.dimension}: {i.description[:100]}")

        if passed:
            logging.info(f"[V7.22] Audit passed at round {round_num}")
            break

        # Revision
        critical = [i for i in report.issues if i.severity == "critical"]
        if not critical:
            from core.agents.auditor import AuditIssue as _AI
            forced_issues = [_AI(dimension=i.dimension, severity="critical",
                                 description=i.description, location=i.location,
                                 suggestion=i.suggestion, excerpt=i.excerpt) for i in report.issues]
        else:
            forced_issues = report.issues

        try:
            result = await run_sync(reviser.revise, content, forced_issues, mode="spot-fix")
            # 日志输出 change_log
            for _cl in result.change_log:
                logging.info(f"[V7.22]   Change: {_cl}")
            # 字数控制 + 蓝图剥离
            try:
                cfg = s.read_config()
                target_words = cfg.get("target_words_per_chapter", 2000)
            except Exception:
                target_words = 2000
            max_chars = int(target_words * 1.2)
            revised = _strip_blueprint(result.content)
            if len(revised) > max_chars:
                cut_pos = revised.rfind("\n\n", int(target_words * 0.8), max_chars + 200)
                if cut_pos > int(target_words * 0.8):
                    revised = revised[:cut_pos]
                else:
                    cut_pos = revised.rfind("。", int(target_words * 0.8), max_chars + 100)
                    if cut_pos > int(target_words * 0.8):
                        revised = revised[:cut_pos+1]
                    else:
                        revised = revised[:max_chars]
            s.save_draft(chapter, revised)
            content = revised  # 下一轮用修订后的内容
            # 不删除 final — 修订只更新 draft，final 由用户手动确认
            rounds_log[-1]["changes"] = result.change_log
        except Exception as e:
            rounds_log[-1]["error"] = f"修订失败: {e}"
            logging.error(f"[V7.22] Round {round_num} revision failed: {e}")
            break

    final_content = s.read_draft(chapter) or s.read_final(chapter)
    return {"ok": True, "rounds": rounds_log, "total_rounds": len(rounds_log),
            "final_passed": rounds_log[-1].get("passed", False) if rounds_log else False}


@router.get("/{book_id}/audit-results/{chapter}")
def get_audit_result(book_id: str, chapter: int):
    s = sm(book_id)
    path = s.state_dir / "audits" / f"audit_ch{chapter:04d}.json"
    if not path.exists():
        raise HTTPException(404, f"第 {chapter} 章审计结果不存在")
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("/{book_id}/audit-results")
def list_audit_results(book_id: str):
    s = sm(book_id)
    audit_dir = s.state_dir / "audits"
    if not audit_dir.exists():
        return []
    results = []
    for f in sorted(audit_dir.glob("audit_ch*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            results.append(data)
        except Exception:
            pass
    return results


@router.post("/{book_id}/ai-rewrite-segment")
async def ai_rewrite_segment(book_id: str, req: SegmentRewriteReq):
    """AI 重写指定段落（支持审计修复和手动选段两种模式）"""
    load_env()
    s = sm(book_id)
    content = s.read_final(req.chapter) or s.read_draft(req.chapter)
    if not content:
        raise HTTPException(404, f"第 {req.chapter} 章不存在")

    from core.agents import ReviserAgent
    llm = create_llm()
    reviser = ReviserAgent(llm)

    try:
        instruction = req.instruction or req.reason or "提升质量"
        original = req.original_text or ""

        if original and len(original) > 20 and original in content:
            # Targeted fix: rewrite the specific excerpt (only when it's real, not frontend fallback)
            from core.agents.auditor import AuditIssue
            fake_issues = [AuditIssue(dimension="综合", severity="critical",
                                     description=instruction, suggestion=instruction)]
            result = await run_sync(reviser.revise, original, fake_issues, mode="spot-fix")
            pos = content.find(original)
            new_content = content[:pos] + _strip_blueprint(result.content) + content[pos + len(original):]
        else:
            # Audit "AI 修复此问题": pass instruction as critical issue for guided revision
            from core.agents.auditor import AuditIssue
            fake_issues = [AuditIssue(dimension="综合", severity="critical",
                                     description=instruction, suggestion=instruction)]
            result = await run_sync(reviser.revise, content, fake_issues, mode="spot-fix")
            new_content = _strip_blueprint(result.content)

        # 后处理：字数控制，不超过目标120%
        try:
            cfg = s.read_config()
            target_words = cfg.get("target_words_per_chapter", 2000)
        except Exception:
            target_words = 2000
        max_chars = int(target_words * 1.2)
        if len(new_content) > max_chars:
            cut_pos = new_content.rfind("\n\n", int(target_words * 0.8), max_chars + 200)
            if cut_pos > int(target_words * 0.8):
                new_content = new_content[:cut_pos]
            else:
                cut_pos = new_content.rfind("。", int(target_words * 0.8), max_chars + 100)
                if cut_pos > int(target_words * 0.8):
                    new_content = new_content[:cut_pos+1]
                else:
                    new_content = new_content[:max_chars]

        # Only save to draft — user must manually re-promote to final via "确认最终稿"
        s.save_draft(req.chapter, new_content)
        # Remove stale final so frontend falls back to showing the revised draft
        final_path = s.chapter_dir / f"ch{req.chapter:04d}_final.md"
        if final_path.exists():
            final_path.unlink()
        return {"ok": True, "rewritten": new_content, "changes": result.change_log}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"重写失败：{e}")


@router.put("/{book_id}/chapters/{chapter}/content")
def update_chapter_content(book_id: str, chapter: int, req: dict):
    content = req.get("content", "")
    kind = req.get("kind", "draft")
    if not content:
        raise HTTPException(400, "内容不能为空")
    s = sm(book_id)
    s.save_draft(chapter, content)
    if kind == "final":
        s.save_final(chapter, content)
    return {"ok": True, "chars": len(content)}


@router.post("/{book_id}/write")
async def action_write(book_id: str, count: int = Query(1)):
    """触发写作（V6 修复版：正确构造 pipeline）"""
    load_env()
    s = sm(book_id)
    try:
        s.read_config()
    except FileNotFoundError:
        raise HTTPException(404, f"书籍不存在：{book_id}")

    from core.narrative import ChapterOutlineSchema
    from core.llm import _fix_df

    # 加载章纲
    chapter_outlines_path = s.state_dir / "chapter_outlines.json"
    if not chapter_outlines_path.exists():
        raise HTTPException(400, "章纲不存在，请先生成大纲")

    raw = json.loads(chapter_outlines_path.read_text(encoding="utf-8"))
    for r in raw:
        if r.get("dramatic_function"):
            r["dramatic_function"] = _fix_df(r["dramatic_function"])
        for bi, beat in enumerate(r.get("beats", [])):
            if not beat.get("id"):
                beat["id"] = f"beat_{r.get('chapter_number', bi)}_{bi+1}"
            if beat.get("dramatic_function"):
                beat["dramatic_function"] = _fix_df(beat["dramatic_function"])
    all_outlines = [ChapterOutlineSchema.model_validate(r) for r in raw]

    pipeline, _ = _build_pipeline(s)
    next_ch = _get_next_chapter(s)

    def _write_sync():
        results = []
        checkpoint_path = s.book_dir / "pipeline_checkpoint.json"
        for i in range(count):
            ch_num = next_ch + i
            if ch_num > len(all_outlines):
                results.append({"chapter": ch_num, "status": "all_done"})
                break
            # V7: 写 checkpoint
            try:
                checkpoint_path.write_text(json.dumps({
                    "status": "running", "total": count,
                    "completed_count": i, "current_chapter": ch_num,
                }, ensure_ascii=False), encoding="utf-8")
            except Exception:
                pass
            co = all_outlines[ch_num - 1]
            try:
                result = pipeline.run(co, False)
                results.append({
                    "chapter": ch_num, "ok": True,
                    "audit_passed": result.audit_report.passed,
                    "word_count": result.word_count,
                })
            except Exception as e:
                results.append({"chapter": ch_num, "error": str(e)})
                # V7: 中断时保存 checkpoint
                try:
                    checkpoint_path.write_text(json.dumps({
                        "status": "interrupted", "total": count,
                        "completed_count": i, "failed_chapter": ch_num,
                        "error": str(e),
                    }, ensure_ascii=False), encoding="utf-8")
                except Exception:
                    pass
                break
        # 完成后清除 checkpoint
        else:
            try:
                if checkpoint_path.exists():
                    checkpoint_path.write_text(json.dumps({"status": "completed"}, ensure_ascii=False), encoding="utf-8")
            except Exception:
                pass
        return results

    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, _write_sync)
    return {"ok": True, "results": results}


@router.post("/{book_id}/audit")
async def action_audit(book_id: str, chapter: int = Query(...)):
    """触发审计（V6 修复版）"""
    load_env()
    s = sm(book_id)
    from core.agents import AuditorAgent, ArchitectBlueprint, PreWriteChecklist, PostWriteSettlement
    from core.types.state import TruthFileKey

    content = s.read_final(chapter) or s.read_draft(chapter)
    if not content:
        raise HTTPException(404, f"第 {chapter} 章不存在")

    llm = create_llm(temperature=0.0, model_env="AUDITOR_MODEL")
    auditor = AuditorAgent(llm)
    blueprint = ArchitectBlueprint(
        core_conflict="", hooks_to_advance=[], hooks_to_plant=[],
        emotional_journey={}, chapter_end_hook="", pace_notes="",
        pov_character_id="",
        pre_write_checklist=PreWriteChecklist([], [], [], [], ""),
    )
    truth_ctx = s.read_truth_bundle([
        TruthFileKey.CURRENT_STATE, TruthFileKey.PENDING_HOOKS,
    ])
    settlement = PostWriteSettlement([], [], [], [], [])

    def _audit_sync():
        return auditor.audit_chapter(content, chapter, blueprint, truth_ctx, settlement,
                                      cross_thread_context="")

    try:
        loop = asyncio.get_event_loop()
        report = await loop.run_in_executor(None, _audit_sync)
        return {
            "ok": True,
            "chapter": chapter,
            "passed": report.passed,
            "issues": len(report.issues),
            "weighted_total": report.weighted_total,
            "critical_count": report.critical_count,
            "warning_count": report.warning_count,
            "dimension_scores": report.dimension_scores,
        }
    except Exception as e:
        raise HTTPException(500, f"审计失败：{e}")


# ── V6: 错误恢复端点 ─────────────────────────────────────────────────────────

@router.get("/{book_id}/checkpoint")
def get_checkpoint(book_id: str):
    """获取当前 checkpoint 状态（V6 新增）"""
    s = sm(book_id)
    checkpoint_path = s.book_dir / "pipeline_checkpoint.json"
    if not checkpoint_path.exists():
        return {"status": "none"}
    try:
        return json.loads(checkpoint_path.read_text(encoding="utf-8"))
    except Exception:
        return {"status": "corrupt"}


@router.post("/{book_id}/resume")
async def resume_from_checkpoint(book_id: str):
    """从 checkpoint 恢复写作（V6 新增）"""
    load_env()
    s = sm(book_id)
    checkpoint_path = s.book_dir / "pipeline_checkpoint.json"
    if not checkpoint_path.exists():
        raise HTTPException(400, "没有可恢复的 checkpoint")

    try:
        ckpt = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    except Exception:
        raise HTTPException(400, "checkpoint 文件损坏")

    if ckpt.get("status") != "interrupted":
        raise HTTPException(400, f"checkpoint 状态不是 interrupted（当前：{ckpt.get('status')}）")

    total = ckpt.get("total", 1)
    completed = ckpt.get("completed_count", 0)

    # 继续写作剩余章节
    remaining = total - completed
    req = ContinueWritingReq(count=remaining)
    return await continue_writing(book_id, req)


# ── V7: 旧路径兼容（独立注册，避免 router prefix 双重嵌套）─────────────────────

def register_legacy_routes(app):
    """注册旧版兼容路由（在 server/__init__.py 中调用）"""

    @app.post("/api/action/write")
    async def legacy_action_write(book_id: str = Query(...), count: int = Query(1)):
        """旧路径兼容：/api/action/write → /{book_id}/write"""
        logging.warning("[deprecated] /api/action/write 已弃用，请改用 /api/books/{book_id}/write")
        return await action_write(book_id, count)

    @app.post("/api/action/audit")
    async def legacy_action_audit(book_id: str = Query(...), chapter: int = Query(...)):
        """旧路径兼容：/api/action/audit → /{book_id}/audit"""
        logging.warning("[deprecated] /api/action/audit 已弃用，请改用 /api/books/{book_id}/audit")
        return await action_audit(book_id, chapter)

    @app.post("/api/action/revise")
    async def legacy_action_revise(
        book_id: str = Query(...),
        chapter: int = Query(...),
        mode: str = Query("spot-fix"),
    ):
        """旧路径兼容：/api/action/revise → /{book_id}/revise"""
        logging.warning("[deprecated] /api/action/revise 已弃用，请改用 /api/books/{book_id}/revise")
        return await action_revise(book_id, chapter, mode)

    @app.post("/api/action/auto-revise-loop")
    async def legacy_auto_revise_loop(
        book_id: str = Query(...),
        chapter: int = Query(...),
        max_rounds: int = Query(5),
    ):
        return await auto_revise_loop(book_id, chapter, max_rounds)
