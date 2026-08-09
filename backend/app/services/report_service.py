"""Doctor-friendly PDF report generator (ReportLab)."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image as RLImage,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.safety import DISCLAIMER
from app.core.config import settings
from app.models.ai_prediction import AIPrediction
from app.models.report import Report
from app.models.skin_image import SkinImage
from app.models.symptom import Symptom
from app.models.treatment import Treatment, TreatmentLog
from app.models.trigger import Trigger
from app.models.user import User, UserProfile
from app.services.analytics.trend import trend_summary
from app.services.analytics.trigger_correlation import analyze_triggers
from app.services.image_service import image_path
from app.services.treatment_service import _adherence
from app.utils.errors import NotFoundError
from app.utils.ids import random_filename

DIMS = [
    "itching", "redness", "dryness", "pain", "swelling",
    "irritation", "burning", "scaling",
]


def _score(sym: Symptom) -> float:
    vals = [getattr(sym, d) for d in DIMS] + [min(sym.lesion_count, 5)]
    return sum(vals) / len(vals)


def _reports_dir() -> Path:
    d = Path(settings.upload_dir) / "reports"
    d.mkdir(parents=True, exist_ok=True)
    return d


def generate_report(
    db: Session,
    user: User,
    date_from: datetime | None,
    date_to: datetime | None,
    include_images: bool,
) -> Report:
    now = datetime.now(timezone.utc)
    if not date_from:
        date_from = now - timedelta(days=30)
    if not date_to:
        date_to = now

    profile = user.profile or UserProfile(user_id=user.id)
    symptoms = list(db.scalars(
        select(Symptom).where(
            Symptom.user_id == user.id,
            Symptom.recorded_at >= date_from,
            Symptom.recorded_at <= date_to,
        ).order_by(Symptom.recorded_at.asc())
    ))
    triggers = list(db.scalars(
        select(Trigger).where(
            Trigger.user_id == user.id,
            Trigger.recorded_at >= date_from,
            Trigger.recorded_at <= date_to,
        )
    ))
    treatments = list(db.scalars(
        select(Treatment).where(Treatment.user_id == user.id)
    ))
    images = list(db.scalars(
        select(SkinImage).where(
            SkinImage.user_id == user.id,
            SkinImage.created_at >= date_from,
            SkinImage.created_at <= date_to,
        ).order_by(SkinImage.created_at.asc())
    ))
    preds = list(db.scalars(
        select(AIPrediction).where(
            AIPrediction.user_id == user.id,
            AIPrediction.created_at >= date_from,
            AIPrediction.created_at <= date_to,
        ).order_by(AIPrediction.created_at.asc())
    ))
    trend = trend_summary(db, user, window_days=(date_to - date_from).days or 30)
    trigger_analysis = analyze_triggers(db, user, window_days=(date_to - date_from).days or 30)

    avg = mean_max = None
    if symptoms:
        scores = [_score(s) for s in symptoms]
        avg = round(sum(scores) / len(scores), 2)
        mean_max = round(max(scores), 2)

    filename = random_filename("pdf")
    path = _reports_dir() / filename

    _build_pdf(
        path,
        user=user,
        profile=profile,
        date_from=date_from,
        date_to=date_to,
        symptoms=symptoms,
        triggers=triggers,
        treatments=treatments,
        db=db,
        images=images,
        preds=preds,
        include_images=include_images,
        avg=avg,
        mean_max=mean_max,
        trend=trend,
        trigger_analysis=trigger_analysis,
    )

    report = Report(
        user_id=user.id,
        stored_filename=filename,
        date_from=date_from,
        date_to=date_to,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def list_reports(db: Session, user: User) -> list[Report]:
    return list(db.scalars(
        select(Report).where(Report.user_id == user.id).order_by(Report.created_at.desc())
    ))


def get_report(db: Session, user: User, report_id: str) -> tuple[Report, Path]:
    r = db.scalar(select(Report).where(
        Report.id == report_id, Report.user_id == user.id
    ))
    if not r:
        raise NotFoundError("Report not found")
    path = _reports_dir() / r.stored_filename
    return r, path


def _build_pdf(
    path: Path,
    *,
    user: User,
    profile: UserProfile,
    date_from: datetime,
    date_to: datetime,
    symptoms: list[Symptom],
    triggers: list[Trigger],
    treatments: list[Treatment],
    db: Session,
    images: list[SkinImage],
    preds: list[AIPrediction],
    include_images: bool,
    avg: float | None,
    mean_max: float | None,
    trend: dict,
    trigger_analysis,
) -> None:
    styles = getSampleStyleSheet()
    story = []

    title = Paragraph("SkinCare AI — Patient Monitoring Report", styles["Title"])
    story.append(title)
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        f"<b>Generated:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        styles["Normal"],
    ))
    story.append(Paragraph(
        f"<b>Reporting period:</b> {date_from.strftime('%Y-%m-%d')} — {date_to.strftime('%Y-%m-%d')}",
        styles["Normal"],
    ))
    story.append(Spacer(1, 0.3 * cm))

    # Patient info
    story.append(Paragraph("Patient Information", styles["Heading2"]))
    patient_rows = [
        ["Name", user.full_name],
        ["Age", str(profile.age) if profile.age is not None else "—"],
        ["Gender", profile.gender or "—"],
        ["Known condition", profile.known_condition or "—"],
        ["Allergies", (profile.allergies or "—")[:200]],
        ["Current treatments", (profile.current_treatments or "—")[:200]],
        ["Notes", (profile.notes or "—")[:200]],
    ]
    t = Table(patient_rows, colWidths=[4 * cm, 12 * cm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4 * cm))

    # Symptom summary
    story.append(Paragraph("Symptom Summary", styles["Heading2"]))
    if symptoms:
        story.append(Paragraph(
            f"Average overall score: <b>{avg}</b> / 5 &nbsp; Maximum: <b>{mean_max}</b> / 5 "
            f"&nbsp; Entries: {len(symptoms)} &nbsp; Trend: <b>{trend.get('direction','—')}</b>",
            styles["Normal"],
        ))
        # per-dimension averages
        dim_avgs = []
        for d in DIMS + ["lesion_count"]:
            vals = [getattr(s, d) for s in symptoms]
            dim_avgs.append([d.replace("_", " ").title(), round(sum(vals) / len(vals), 2)])
        dt = Table([["Dimension", "Avg"]] + dim_avgs, colWidths=[6 * cm, 4 * cm])
        dt.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ]))
        story.append(dt)
    else:
        story.append(Paragraph("No symptom entries in this period.", styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))

    # Triggers + associations
    story.append(Paragraph("Triggers & Associations", styles["Heading2"]))
    if triggers:
        story.append(Paragraph(
            f"{len(triggers)} trigger entries recorded.", styles["Normal"]
        ))
        for a in trigger_analysis.associations[:8]:
            story.append(Paragraph(f"• {a.summary}", styles["Normal"]))
        story.append(Paragraph(f"<i>{trigger_analysis.note}</i>", styles["Normal"]))
    else:
        story.append(Paragraph("No trigger entries in this period.", styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))

    # Treatments + adherence
    story.append(Paragraph("Treatments & Adherence", styles["Heading2"]))
    if treatments:
        rows = [["Treatment", "Schedule", "Adherence %", "Active"]]
        for tr in treatments:
            rows.append([
                tr.name, tr.schedule,
                f"{_adherence(tr, db)}%", "Yes" if tr.active else "No",
            ])
        tt = Table(rows, colWidths=[5 * cm, 5 * cm, 3 * cm, 2 * cm])
        tt.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ]))
        story.append(tt)
        story.append(Paragraph(
            "<i>The system only tracks adherence and reminds. It does not prescribe.</i>",
            styles["Normal"],
        ))
    else:
        story.append(Paragraph("No treatments recorded.", styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))

    # AI predictions
    story.append(Paragraph("AI Screening Results", styles["Heading2"]))
    if preds:
        for p in preds:
            cat = p.category or "unreliable (below threshold)"
            demo = " (DEMO/prototype model)" if p.is_demo else ""
            story.append(Paragraph(
                f"• {p.created_at.strftime('%Y-%m-%d')} — Category: <b>{cat}</b>, "
                f"confidence {p.confidence}{demo}",
                styles["Normal"],
            ))
        story.append(Paragraph(f"<i>{DISCLAIMER}</i>", styles["Normal"]))
    else:
        story.append(Paragraph("No AI predictions in this period.", styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))

    # Selected images
    if include_images and images:
        story.append(Paragraph("Selected Images (with timestamps)", styles["Heading2"]))
        for im in images[:6]:
            story.append(Paragraph(
                f"• {im.created_at.strftime('%Y-%m-%d')} — "
                f"{im.body_location or 'unspecified location'} — "
                f"quality {im.quality_score}",
                styles["Normal"],
            ))
            try:
                ip = image_path(user.id, im.stored_filename)
                if ip.exists():
                    rl = RLImage(str(ip), width=6 * cm, height=6 * cm)
                    story.append(rl)
                    story.append(Spacer(1, 0.2 * cm))
            except Exception:  # noqa: BLE001
                pass
        story.append(Paragraph(
            "<i>Images are shown for reference only. Visual differences do not "
            "constitute a medical comparison.</i>",
            styles["Normal"],
        ))
    story.append(Spacer(1, 0.5 * cm))

    # Disclaimer footer
    story.append(Paragraph("Disclaimer", styles["Heading2"]))
    story.append(Paragraph(DISCLAIMER, styles["Normal"]))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "This report was generated by SkinCare AI, a screening/monitoring/education "
        "tool, and is intended to support — not replace — a consultation with a "
        "qualified healthcare professional.",
        styles["Normal"],
    ))

    doc = SimpleDocTemplate(str(path), pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    doc.build(story)
