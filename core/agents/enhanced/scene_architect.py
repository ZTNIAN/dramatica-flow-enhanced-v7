"""SceneArchitect — 场景空间感/五感层次/氛围/转场质量审核"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from ...llm import LLMProvider, LLMMessage, parse_llm_json, with_retry

from ..kb import KB_SCENE_ARCHITECT, track_kb_query

_KB_SCENE_ARCHITECT = KB_SCENE_ARCHITECT


@dataclass
class SceneDimension:
    """单个场景维度检查结果"""
    dimension: str
    score: int
    level: str  # 优秀/良好/合格/不足
    details: str
    suggestion: str = ""


@dataclass
class SceneAuditResult:
    """场景审核结果"""
    dimensions: list[SceneDimension]
    overall_score: int
    passed: bool
    summary: str


class _SceneDimensionSchema(BaseModel):
    dimension: str
    score: int = 80
    level: str = "良好"
    details: str = ""
    suggestion: str = ""


class _SceneAuditSchema(BaseModel):
    dimensions: list[_SceneDimensionSchema] = Field(default_factory=list)
    overall_score: int = 80
    passed: bool = True
    summary: str = ""


class SceneArchitect:
    """场景建筑师：审核场景的空间感、五感层次、氛围营造、转场质量"""

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def audit_scene(
        self,
        chapter_content: str,
        chapter_number: int,
    ) -> SceneAuditResult:
        track_kb_query("scene_architect", "agent-specific/scene-architect-guide.md")
        kb_section = ""
        if _KB_SCENE_ARCHITECT:
            kb_section = f"\n## 场景建筑方法论\n{_KB_SCENE_ARCHITECT[:2000]}\n"

        content_excerpt = chapter_content[:3000]

        prompt = f"""你是场景建筑师，请审核第{chapter_number}章的场景质量。

## 章节内容
{content_excerpt}
{kb_section}
## 五维审核要求
1. 空间感构建（场景是否有清晰的空间布局、景深层次）
2. 五感层次（视觉/听觉/嗅觉/触觉/味觉的调动是否丰富）
3. 氛围营造（场景是否有情绪氛围，读者能否感受到）
4. 转场质量（场景切换是否自然流畅）
5. 场景与情节融合（场景描写是否服务于情节推进）

## 评分等级
- 优秀(90-100)：场景生动立体，读者身临其境
- 良好(75-89)：场景清晰，但五感层次可更丰富
- 合格(60-74)：场景基本清晰，但缺乏沉浸感
- 不足(0-59)：场景模糊，影响阅读体验

## 输出格式（JSON）
{{"dimensions": [
    {{"dimension": "空间感构建", "score": 85, "level": "良好", "details": "具体表现", "suggestion": "建议"}}
], "overall_score": 82, "passed": true, "summary": "整体评价（50字）"}}

评分标准：overall_score >= 80 为通过
只输出 JSON。"""

        def _call() -> SceneAuditResult:
            resp = self.llm.complete([
                LLMMessage("system", "你是场景建筑师，专注于场景空间感和五感层次审核。只输出合法 JSON。"),
                LLMMessage("user", prompt),
            ])
            parsed = parse_llm_json(resp.content, _SceneAuditSchema, "audit_scene")
            dimensions = [
                SceneDimension(
                    dimension=d.dimension,
                    score=d.score,
                    level=d.level,
                    details=d.details,
                    suggestion=d.suggestion,
                )
                for d in parsed.dimensions
            ]
            return SceneAuditResult(
                dimensions=dimensions,
                overall_score=parsed.overall_score,
                passed=parsed.overall_score >= 80,
                summary=parsed.summary,
            )

        return with_retry(_call)
