"""ReviserAgent — 修订者 Agent：spot-fix 修订"""
from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, field_validator, Field

from ..llm import LLMProvider, LLMMessage, parse_llm_json, with_retry
from ..types.narrative import Character
from ..narrative import ChapterOutlineSchema

from .kb import KB_ANTI_AI, KB_REDLINES, track_kb_query
from .auditor import _MODE_INSTRUCTIONS, CHANGELOG_SEPARATOR

_KB_ANTI_AI = KB_ANTI_AI
_KB_REDLINES = KB_REDLINES

@dataclass
class ReviseResult:
    content: str
    change_log: list[str]




class ReviserAgent:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def revise(
        self,
        original_content: str,
        issues: list[AuditIssue],
        mode: ReviseMode = "spot-fix",
    ) -> ReviseResult:
        critical = [i for i in issues if i.severity == "critical"]
        warnings  = [i for i in issues if i.severity == "warning"]

        if not critical and mode == "spot-fix":
            return ReviseResult(
                content=original_content,
                change_log=["无 critical 问题，跳过修订"],
            )

        issue_lines = []
        for i in (critical + warnings):
            line = f"- [{i.severity.upper()}] {i.dimension}：{i.description}"
            if i.location:
                line += f"\n  原文位置：「{i.location}」"
            if i.suggestion:
                line += f"\n  修复建议：{i.suggestion}"
            issue_lines.append(line)

        prompt = f"""\
## 修订任务
模式：{mode}
规则：{_MODE_INSTRUCTIONS[mode]}
硬约束：不得引入新情节，不得修改角色名，不得改变情节走向。

## 重要：修改幅度约束（必须严格遵守）
- 只修改下方「需修订的问题」明确指出的句子或段落
- 未被指出问题的段落，一个字都不能改，保持原样输出
- 如果某个问题只需要改一个词或一句话，就只改那一个词或那一句话
- 不要"顺便优化"其他地方的文笔、措辞、描写
- 改动越少越好，能改一句的不改一段，能改一词的不改一句

## 铁律：禁止输出规划信息
- 禁止在正文中输出任何写作规划信息（写前蓝图/核心冲突/情感旅程/节拍序列/目标/冲突/结尾钩子/结算表/伏笔管理/角色状态变化等）
- 你的输出必须是纯小说正文，不能包含任何元信息、注释、标记
- 不能输出 "---" 分隔符后跟规划内容

## 需修订的问题
{chr(10).join(issue_lines)}

## 原文
{original_content}

---
直接输出修订后的完整正文（不要任何前言），然后输出：
{CHANGELOG_SEPARATOR}
["改动说明1", "改动说明2", ...]"""

        def _call() -> ReviseResult:
            resp = self.llm.complete([
                LLMMessage(
                    "system",
                    f"你是精准的小说修订者，模式：{mode}。"
                    f"{_MODE_INSTRUCTIONS[mode]}"
                    "核心原则：最小改动。只改问题涉及的句子，其余内容一字不动原样输出。"
                    "禁止\"顺便优化\"、禁止润色未被指出的段落。"
                    "禁止在输出中包含任何写作规划信息（蓝图/大纲/细纲/节拍/结算表/伏笔管理/角色状态等），你的输出必须是纯小说正文。"
                    "直接输出修订后正文，不要任何前言。",
                ),
                LLMMessage("user", prompt),
            ])
            parts = resp.content.split(CHANGELOG_SEPARATOR, 1)
            content = parts[0].strip()
            change_log: list[str] = []
            if len(parts) > 1:
                try:
                    change_log = json.loads(parts[1].strip())
                except Exception:
                    change_log = [parts[1].strip()[:200]]
            return ReviseResult(content=content, change_log=change_log)

        return with_retry(_call)


# ─────────────────────────────────────────────────────────────────────────────
# 5. 摘要 Agent（新增）
# 写完章节后自动生成章节摘要，注入 chapter_summaries.md
# ─────────────────────────────────────────────────────────────────────────────

