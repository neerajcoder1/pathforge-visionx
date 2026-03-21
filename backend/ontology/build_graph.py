"""Build the ESCO graph pickle at data/esco_graph.pkl from skills_courses_full.json."""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

import networkx as nx


def _normalize_key(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _demand_to_criticality(demand: str) -> float:
    mapping = {
        "very high": 1.25,
        "high": 1.10,
        "medium": 1.00,
        "low": 0.85,
        "very low": 0.70,
    }
    return mapping.get(_normalize_key(demand), 1.00)


def build_graph_from_json(force: bool = True) -> Path:
    """Build graph using the real skills/course payload and overwrite pickle by default."""
    root = Path(__file__).resolve().parents[2]
    source_path = root / "skills_courses_full.json"
    if not source_path.exists():
        raise FileNotFoundError(f"Dataset not found: {source_path}")

    target_dir = root / "data"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / "esco_graph.pkl"
    if target_path.exists() and not force:
        return target_path

    with source_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    skills = payload.get("skills", []) if isinstance(payload, dict) else []
    courses = payload.get("courses", []) if isinstance(payload, dict) else []

    graph = nx.DiGraph()

    alias_table: dict[str, str] = {}
    for skill in skills:
        if not isinstance(skill, dict):
            continue

        skill_id = str(skill.get("id", "")).strip()
        if not skill_id:
            continue

        skill_name = str(skill.get("name", skill_id)).strip() or skill_id
        graph.add_node(
            skill_id,
            label=skill_name,
            name=skill_name,
            domain=str(skill.get("domain", "")).strip(),
            subcategory=str(skill.get("subcategory", "")).strip(),
            level=str(skill.get("level", "")).strip(),
            skill_type=str(skill.get("type", "")).strip(),
            demand=str(skill.get("demand", "")).strip(),
            criticality=_demand_to_criticality(str(skill.get("demand", ""))),
        )

        alias_table[_normalize_key(skill_name)] = skill_id
        alias_table[_normalize_key(skill_id)] = skill_id

    for skill in skills:
        if not isinstance(skill, dict):
            continue
        src = str(skill.get("id", "")).strip()
        if not src or src not in graph:
            continue

        related = skill.get("related_skills", [])
        if not isinstance(related, list):
            continue
        for dst in related:
            dst_id = str(dst).strip()
            if not dst_id or dst_id not in graph or dst_id == src:
                continue
            graph.add_edge(src, dst_id, relation="SIMILAR_TO", similarity_weight=0.8)

    catalog_courses: list[dict[str, Any]] = []
    mandatory_modules: set[str] = set()
    for course in courses:
        if not isinstance(course, dict):
            continue

        course_id = str(course.get("id", "")).strip()
        if not course_id:
            continue

        title = str(course.get("title", course_id)).strip() or course_id
        hours = _to_float(course.get("duration_hours", 0.0), default=0.0)

        raw_teaches = course.get("skills_covered", [])
        if isinstance(raw_teaches, list):
            teaches = [str(s).strip() for s in raw_teaches if str(s).strip()]
        else:
            teaches = []
        teaches = [s for s in teaches if s in graph]

        if not teaches:
            continue

        is_mandatory = bool(course.get("is_mandatory", False))
        requires_raw = course.get("requires", [])
        requires = [str(s).strip() for s in requires_raw if str(s).strip()] if isinstance(requires_raw, list) else []

        course_obj = {
            "course_id": course_id,
            "title": title,
            "hours": float(hours),
            "teaches": teaches,
            "is_mandatory": is_mandatory,
            "requires": requires,
        }
        catalog_courses.append(course_obj)
        if is_mandatory:
            mandatory_modules.add(course_id)

    graph.graph["alias_table"] = alias_table
    graph.graph["catalog_courses"] = catalog_courses
    graph.graph["mandatory_modules"] = mandatory_modules

    with target_path.open("wb") as f:
        pickle.dump(graph, f)

    return target_path


def ensure_graph_pickle() -> Path:
    """Keep compatibility with existing imports while ensuring a graph exists."""
    return build_graph_from_json(force=False)


if __name__ == "__main__":
    out = build_graph_from_json(force=True)
    with out.open("rb") as f:
        graph = pickle.load(f)
    print(f"ESCO graph rebuilt at: {out}")
    print(f"nodes={len(graph.nodes())} edges={len(graph.edges())} catalog_courses={len(graph.graph.get('catalog_courses', []))}")
