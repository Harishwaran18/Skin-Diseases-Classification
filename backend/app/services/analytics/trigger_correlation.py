"""Trigger correlation engine — honest associations, NO causal claims.

Wording is strictly templated ("possible association") and never asserts
that a trigger causes a condition.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.symptom import Symptom
from app.models.trigger import Trigger
from app.models.user import User
from app.schemas.trigger import (
    TriggerAnalysisResponse,
    TriggerAssociation,
)

DIMS = [
    "itching", "redness", "dryness", "pain", "swelling",
    "irritation", "burning", "scaling",
]


def _score(sym: Symptom) -> float:
    vals = [getattr(sym, d) for d in DIMS] + [min(sym.lesion_count, 5)]
    return sum(vals) / len(vals)


def analyze_triggers(
    db: Session, user: User, window_days: int = 30
) -> TriggerAnalysisResponse:
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=window_days)
    symptoms = list(
        db.scalars(
            select(Symptom)
            .where(Symptom.user_id == user.id, Symptom.recorded_at >= start)
            .order_by(Symptom.recorded_at.asc())
        )
    )
    triggers = list(
        db.scalars(
            select(Trigger)
            .where(Trigger.user_id == user.id, Trigger.recorded_at >= start)
        )
    )

    if not symptoms or not triggers:
        return TriggerAnalysisResponse(
            associations=[],
            note=(
                "Not enough symptom and trigger records in the selected "
                "window to compute associations. Keep logging both daily."
            ),
        )

    # Build daily symptom score series.
    day_scores: dict[str, list[float]] = {}
    for s in symptoms:
        day_scores.setdefault(s.recorded_at.date().isoformat(), []).append(
            _score(s)
        )
    day_avg = {d: sum(v) / len(v) for d, v in day_scores.items()}

    # Group triggers by (category, name) -> set of days present.
    trigger_days: dict[tuple[str, str], set[str]] = {}
    trigger_count: dict[tuple[str, str], int] = {}
    for t in triggers:
        key = (t.category, t.name)
        trigger_days.setdefault(key, set()).add(
            t.recorded_at.date().isoformat()
        )
        trigger_count[key] = trigger_count.get(key, 0) + 1

    all_days = sorted(day_avg.keys())
    present_scores = {key: [] for key in trigger_days}
    absent_scores = {key: [] for key in trigger_days}
    for key, days in trigger_days.items():
        for d in all_days:
            if d in days:
                present_scores[key].append(day_avg[d])
            else:
                absent_scores[key].append(day_avg[d])

    associations: list[TriggerAssociation] = []
    for key, days in trigger_days.items():
        pres = present_scores[key]
        abst = absent_scores[key]
        mean_pres = float(np.mean(pres)) if pres else 0.0
        mean_abst = float(np.mean(abst)) if abst else 0.0
        diff = mean_pres - mean_abst
        # correlation between trigger presence and symptom score
        x = [1 if d in days else 0 for d in all_days]
        y = [day_avg[d] for d in all_days]
        if len(set(x)) > 1 and len(set(y)) > 1:
            corr = float(np.corrcoef(x, y)[0, 1])
            if np.isnan(corr):
                corr = 0.0
        else:
            corr = 0.0
        # cautious templated wording
        if abs(diff) < 0.2:
            summary = (
                f"No clear association between {key[1]} and symptom scores "
                f"in the last {window_days} days."
            )
        else:
            direction = "higher" if diff > 0 else "lower"
            summary = (
                f"Possible association: on days with {key[1]} recorded, "
                f"average symptom scores were {direction} "
                f"({mean_pres:.1f} vs {mean_abst:.1f}). This is an "
                f"observation, not a causal link."
            )
        associations.append(
            TriggerAssociation(
                category=key[0],
                name=key[1],
                frequency=trigger_count[key],
                mean_score_when_present=round(mean_pres, 2),
                mean_score_when_absent=round(mean_abst, 2),
                difference=round(diff, 2),
                correlation=round(corr, 2),
                summary=summary,
            )
        )

    associations.sort(key=lambda a: abs(a.difference), reverse=True)
    return TriggerAnalysisResponse(
        associations=associations,
        note=(
            "These are statistical observations of co-occurrence, not "
            "medical diagnoses or proof of causation. Discuss persistent "
            "patterns with a qualified healthcare professional."
        ),
    )
