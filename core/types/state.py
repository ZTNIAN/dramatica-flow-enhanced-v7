"""
状态管理核心类型
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ── 真相文件键 ──────────────────────────────────────────────────────────────────

class TruthFileKey(str, Enum):
    CURRENT_STATE    = "current_state"
    CHARACTER_MATRIX = "character_matrix"
    PENDING_HOOKS    = "pending_hooks"
    CAUSAL_CHAIN     = "causal_chain"
    EMOTIONAL_ARCS   = "emotional_arcs"
    CHAPTER_SUMMARIES = "chapter_summaries"
    STORY_BIBLE      = "story_bible"
    THREAD_STATUS    = "thread_status"


TRUTH_FILE_NAMES: dict[TruthFileKey, str] = {
    TruthFileKey.CURRENT_STATE:    "current_state.md",
    TruthFileKey.CHARACTER_MATRIX: "character_matrix.md",
    TruthFileKey.PENDING_HOOKS:    "pending_hooks.md",
    TruthFileKey.CAUSAL_CHAIN:     "causal_chain.md",
    TruthFileKey.EMOTIONAL_ARCS:   "emotional_arcs.md",
    TruthFileKey.CHAPTER_SUMMARIES: "chapter_summaries.md",
    TruthFileKey.STORY_BIBLE:      "story_bible.md",
    TruthFileKey.THREAD_STATUS:    "thread_status.md",
}


# ── 关系类型 ──────────────────────────────────────────────────────────────────

class RelationshipType(str, Enum):
    ALLY    = "ally"
    ENEMY   = "enemy"
    NEUTRAL = "neutral"


# ── 伏笔状态 ──────────────────────────────────────────────────────────────────

class HookStatus(str, Enum):
    OPEN     = "open"
    RESOLVED = "resolved"
    DROPPED  = "dropped"


# ── 伏笔类型 ──────────────────────────────────────────────────────────────────

class HookType(str, Enum):
    FORESHADOW = "foreshadow"
    MYSTERY    = "mystery"
    PROMISE    = "promise"
    RED_HERRING = "red_herring"


# ── 情感快照 ──────────────────────────────────────────────────────────────────

@dataclass
class EmotionalSnapshot:
    character_id: str
    emotion: str
    intensity: int
    chapter: int
    trigger: str = ""


# ── 受影响的决策 ──────────────────────────────────────────────────────────────

@dataclass
class AffectedDecision:
    character_id: str
    decision: str


# ── 因果链 ──────────────────────────────────────────────────────────────────

@dataclass
class CausalLink:
    id: str
    chapter: int
    cause: str
    event: str
    consequence: str
    affected_decisions: list[AffectedDecision] = field(default_factory=list)


# ── 关系变更记录 ──────────────────────────────────────────────────────────────

@dataclass
class RelationshipDelta:
    chapter: int
    delta: int
    reason: str = ""


# ── 关系记录 ──────────────────────────────────────────────────────────────────

@dataclass
class RelationshipRecord:
    character_a: str
    character_b: str
    type: RelationshipType = RelationshipType.NEUTRAL
    score: int = 50
    history: list[RelationshipDelta] = field(default_factory=list)


# ── 已知信息记录 ──────────────────────────────────────────────────────────────

@dataclass
class KnownInfoRecord:
    character_id: str
    info_key: str
    content: str
    learned_in_chapter: int
    source: str = ""


# ── 伏笔 ──────────────────────────────────────────────────────────────────────

@dataclass
class Hook:
    id: str
    type: HookType
    description: str
    planted_in_chapter: int
    expected_resolution_range: tuple[int, int] = (0, 0)
    status: HookStatus = HookStatus.OPEN
    resolved_in_chapter: int | None = None


# ── 世界状态 ──────────────────────────────────────────────────────────────────

@dataclass
class WorldState:
    book_id: str
    current_chapter: int = 0
    character_positions: dict[str, str] = field(default_factory=dict)
    relationships: dict[str, RelationshipRecord] = field(default_factory=dict)
    known_info: list[KnownInfoRecord] = field(default_factory=list)
    emotional_snapshots: list[EmotionalSnapshot] = field(default_factory=list)
    timeline: list[dict[str, Any]] = field(default_factory=list)


# ── 状态快照 ──────────────────────────────────────────────────────────────────

@dataclass
class StateSnapshot:
    chapter: int
    summary: str
    character_states: dict[str, dict[str, Any]] = field(default_factory=dict)
    world_changes: list[str] = field(default_factory=list)


# ── 书籍配置 ──────────────────────────────────────────────────────────────────

@dataclass
class BookConfig:
    id: str
    title: str
    genre: str
    target_words_per_chapter: int = 2000
    target_chapters: int = 50
    protagonist_id: str = ""
    custom_forbidden_words: list[str] = field(default_factory=list)
    style_guide: str = ""


# ── 项目状态 ──────────────────────────────────────────────────────────────────

@dataclass
class ProjectState:
    config: BookConfig
    characters: dict[str, Any] = field(default_factory=dict)
    locations: dict[str, Any] = field(default_factory=dict)
    factions: dict[str, Any] = field(default_factory=dict)
    world_rules: list[Any] = field(default_factory=list)
    seed_events: list[Any] = field(default_factory=list)
    world_state: WorldState | None = None
