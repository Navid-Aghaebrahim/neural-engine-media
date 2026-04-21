#!/usr/bin/env python3
"""Instagram strategy + QA helpers for Neural-Engine.

Goals:
- Reduce repetition by rotating content angles/hooks/CTAs
- Keep copy educational *and* commercially useful
- Enforce text-length guardrails for image legibility
- Avoid unreadable contrast combinations by using deterministic overlays
- Provide reusable slide/single-post generation plans and captions
"""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

W = H = 1024
SAFE_MARGIN = 80
CONTENT_MAX_W = W - SAFE_MARGIN * 2

MAX_HEADLINE_WORDS = 8
MAX_SUB_WORDS = 14
MAX_CTA_WORDS = 8
MAX_BULLETS = 3
MAX_BULLET_WORDS = 8
MAX_CAPTION_LINE_WORDS = 18

RECENT_PATH = Path("tmp/ig_recent_history.json")

POST_TYPES = [
    "myth-vs-fact",
    "3-step-framework",
    "mistake-to-avoid",
    "before-vs-after",
    "feature-to-benefit",
    "faq",
    "social-proof",
    "contrarian-tip",
]

HOOK_PATTERNS = [
    "Stop doing this before you enter",
    "Most traders skip this step",
    "The smarter workflow is simpler",
    "What good risk prep looks like",
    "The signal is not the decision",
    "Use AI here — not here",
    "A better pre-trade checklist",
    "Why reactive trading feels expensive",
]

CTA_PATTERNS = [
    "See the workflow",
    "Join the waitlist",
    "Watch smarter, not harder",
    "Build a calmer process",
    "Trade with more structure",
]

THEME_BANK = {
    "workflow": {
        "lessons": [
            "A checklist beats emotional entries.",
            "Context matters more than a raw signal.",
            "Pre-defining invalidation improves discipline.",
            "Reviewing process beats obsessing over P&L.",
        ],
        "benefits": [
            "Neural-Engine adds structure inside TradingView.",
            "The product supports faster chart review without taking control away.",
            "The workflow stays local and trader-led.",
        ],
        "caption_angles": [
            "pre-trade routine",
            "chart review discipline",
            "decision hygiene",
        ],
    },
    "risk": {
        "lessons": [
            "A signal without risk rules is just temptation.",
            "If invalidation is unclear, the trade is unclear.",
            "Position sizing should follow risk, not excitement.",
        ],
        "benefits": [
            "Neural-Engine helps surface setups while the trader keeps the decision.",
            "Clearer pattern visibility can make risk reviews more consistent.",
        ],
        "caption_angles": [
            "risk before reward",
            "position sizing discipline",
            "invalidation clarity",
        ],
    },
    "privacy": {
        "lessons": [
            "Local-first tools reduce workflow friction and privacy concerns.",
            "Traders want assistance without exporting their entire process.",
            "Confidence improves when the system is transparent.",
        ],
        "benefits": [
            "Neural-Engine runs on your Mac and stays inside your workflow.",
            "The product keeps the trader in control instead of hiding behind automation.",
        ],
        "caption_angles": [
            "local-first workflow",
            "privacy and control",
            "transparent assistance",
        ],
    },
    "features": {
        "lessons": [
            "A useful feature should shorten analysis, not distract from it.",
            "The best overlays make the next decision clearer.",
            "Speed matters only when clarity stays high.",
        ],
        "benefits": [
            "Neural-Engine highlights setups in a format traders already understand.",
            "The app is meant to improve scan speed without replacing judgment.",
        ],
        "caption_angles": [
            "overlay clarity",
            "feature to workflow",
            "speed with judgment",
        ],
    },
}


@dataclass
class SlidePlan:
    headline: str
    sub: str


@dataclass
class SinglePlan:
    headline: str
    sub: str
    cta: str


@dataclass
class StrategyPlan:
    post_type: str
    theme: str
    hook: str
    lesson: str
    benefit: str
    cta: str
    angle: str


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _word_count(text: str) -> int:
    return len([w for w in re.split(r"\s+", text.strip()) if w])


def _trim_words(text: str, max_words: int) -> str:
    words = [w for w in re.split(r"\s+", text.strip()) if w]
    if len(words) <= max_words:
        return text.strip()
    return " ".join(words[:max_words]).rstrip(" ,;:-")


def _load_recent() -> list[dict]:
    if not RECENT_PATH.exists():
        return []
    try:
        return json.loads(RECENT_PATH.read_text())
    except Exception:
        return []


def save_recent(plan: StrategyPlan, slides: Iterable[SlidePlan] | None = None, single: SinglePlan | None = None, caption: str | None = None) -> None:
    RECENT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = _load_recent()[-19:]
    rows.append(
        {
            "post_type": plan.post_type,
            "theme": plan.theme,
            "hook": plan.hook,
            "lesson": plan.lesson,
            "benefit": plan.benefit,
            "cta": plan.cta,
            "angle": plan.angle,
            "slides": [s.__dict__ for s in slides] if slides else None,
            "single": single.__dict__ if single else None,
            "caption": caption,
        }
    )
    RECENT_PATH.write_text(json.dumps(rows, indent=2))


def choose_strategy(theme: str, seed: int | None = None) -> StrategyPlan:
    rnd = random.Random(seed)
    recent = _load_recent()
    used_types = {row.get("post_type") for row in recent[-6:]}
    used_hooks = {_normalize(row.get("hook", "")) for row in recent[-8:]}
    used_angles = {_normalize(row.get("angle", "")) for row in recent[-8:]}

    available_types = [p for p in POST_TYPES if p not in used_types] or POST_TYPES
    available_hooks = [h for h in HOOK_PATTERNS if _normalize(h) not in used_hooks] or HOOK_PATTERNS

    bank = THEME_BANK.get(theme, THEME_BANK["workflow"])
    lesson = rnd.choice(bank["lessons"])
    benefit = rnd.choice(bank["benefits"])
    angle_options = [a for a in bank["caption_angles"] if _normalize(a) not in used_angles] or bank["caption_angles"]

    return StrategyPlan(
        post_type=rnd.choice(available_types),
        theme=theme,
        hook=rnd.choice(available_hooks),
        lesson=lesson,
        benefit=benefit,
        cta=rnd.choice(CTA_PATTERNS),
        angle=rnd.choice(angle_options),
    )


def build_carousel_plan(theme: str, seed: int | None = None) -> tuple[StrategyPlan, list[SlidePlan]]:
    plan = choose_strategy(theme, seed=seed)

    slides = [
        SlidePlan(
            headline=_trim_words(plan.hook, MAX_HEADLINE_WORDS),
            sub=_trim_words("One clear takeaway for better trade decisions.", MAX_SUB_WORDS),
        ),
        SlidePlan(
            headline=_trim_words("Step 1: Read context first", MAX_HEADLINE_WORDS),
            sub=_trim_words("Trend, level, session, then signal.", MAX_SUB_WORDS),
        ),
        SlidePlan(
            headline=_trim_words("Step 2: Define risk before entry", MAX_HEADLINE_WORDS),
            sub=_trim_words("Invalidation first. Size second. Entry last.", MAX_SUB_WORDS),
        ),
        SlidePlan(
            headline=_trim_words("Where Neural-Engine helps", MAX_HEADLINE_WORDS),
            sub=_trim_words(plan.benefit, MAX_SUB_WORDS),
        ),
    ]
    return plan, slides


def build_single_plan(theme: str, seed: int | None = None) -> tuple[StrategyPlan, SinglePlan]:
    plan = choose_strategy(theme, seed=seed)
    single = SinglePlan(
        headline=_trim_words(plan.hook, MAX_HEADLINE_WORDS),
        sub=_trim_words(f"{plan.lesson} {plan.benefit}", MAX_SUB_WORDS),
        cta=_trim_words(plan.cta, MAX_CTA_WORDS),
    )
    return plan, single


def build_caption(plan: StrategyPlan, kind: str = "carousel") -> str:
    openers = {
        "carousel": [
            f"{plan.hook}.",
            f"{plan.angle.title()} is where a lot of traders get sloppy.",
        ],
        "single": [
            f"{plan.hook}.",
            f"Better trading workflows start with calmer decisions.",
        ],
    }
    intro = random.choice(openers.get(kind, openers["single"]))
    lines = [
        intro,
        "",
        f"What this post is really about: {plan.lesson}",
        f"Why it matters: {plan.benefit}",
        "",
        "A simple rule:",
        "• read context first",
        "• define risk before entry",
        "• let the tool support the decision, not replace it",
        "",
        f"If you want a more structured workflow, {plan.cta.lower()}.",
        "",
        "#trading #tradingview #fintech #investingtools #ai #stockmarket #riskmanagement",
    ]
    return "\n".join(lines)


def validate_slide_copy(headline: str, sub: str) -> list[str]:
    issues: list[str] = []
    if _word_count(headline) > MAX_HEADLINE_WORDS:
        issues.append(f"headline too long ({_word_count(headline)} words)")
    if _word_count(sub) > MAX_SUB_WORDS:
        issues.append(f"sub too long ({_word_count(sub)} words)")
    if len(headline) > 55:
        issues.append("headline too long in characters")
    if len(sub) > 95:
        issues.append("sub too long in characters")
    return issues


def validate_single_copy(headline: str, sub: str, cta: str) -> list[str]:
    issues = validate_slide_copy(headline, sub)
    if _word_count(cta) > MAX_CTA_WORDS:
        issues.append(f"cta too long ({_word_count(cta)} words)")
    if len(cta) > 42:
        issues.append("cta too long in characters")
    return issues


def ensure_distinct_copy(items: Iterable[str]) -> list[str]:
    normalized = [_normalize(i) for i in items if i.strip()]
    issues: list[str] = []
    if len(set(normalized)) != len(normalized):
        issues.append("duplicate copy detected")
    return issues
