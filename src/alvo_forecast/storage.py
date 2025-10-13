"""Persistência simples em JSON para o Alvo Forecast."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Dict, Optional, Tuple

from .models import LossReason, Opportunity, OpportunityStatus, SpinStage
from .repository import ForecastRepository


def _date_to_str(value: Optional[date]) -> Optional[str]:
    return value.isoformat() if value else None


def _date_from_str(value: Optional[str]) -> Optional[date]:
    return date.fromisoformat(value) if value else None


def _serialize_loss_reason(reason: LossReason) -> Dict[str, object]:
    return {
        "id": reason.id,
        "description": reason.description,
        "active": reason.active,
    }


def _serialize_opportunity(opportunity: Opportunity) -> Dict[str, object]:
    return {
        "id": opportunity.id,
        "created_at": _date_to_str(opportunity.created_at),
        "broker": opportunity.broker,
        "development": opportunity.development,
        "expected_value": opportunity.expected_value,
        "forecast_date": _date_to_str(opportunity.forecast_date),
        "closing_probability": opportunity.closing_probability,
        "status": opportunity.status.value,
        "loss_reason_id": opportunity.loss_reason.id if opportunity.loss_reason else None,
        "loss_spin_stage": (
            opportunity.loss_spin_stage.value if opportunity.loss_spin_stage else None
        ),
        "spin_situation": opportunity.spin_situation,
        "spin_problem": opportunity.spin_problem,
        "spin_implication": opportunity.spin_implication,
        "spin_need": opportunity.spin_need,
        "identified_objections": list(opportunity.identified_objections),
        "realized_value": opportunity.realized_value,
        "closing_date": _date_to_str(opportunity.closing_date),
    }


def _deserialize_loss_reason(payload: Dict[str, object]) -> LossReason:
    return LossReason(
        id=int(payload["id"]),
        description=str(payload["description"]),
        active=bool(payload.get("active", True)),
    )


def _deserialize_opportunity(
    payload: Dict[str, object],
    *,
    loss_reasons: Dict[int, LossReason],
) -> Opportunity:
    loss_reason_id = payload.get("loss_reason_id")
    loss_reason = loss_reasons.get(int(loss_reason_id)) if loss_reason_id is not None else None
    loss_spin_stage = payload.get("loss_spin_stage")
    return Opportunity(
        id=int(payload["id"]),
        created_at=_date_from_str(payload.get("created_at")) or date.today(),
        broker=str(payload["broker"]),
        development=str(payload["development"]),
        expected_value=float(payload.get("expected_value", 0.0)),
        forecast_date=_date_from_str(payload.get("forecast_date")) or date.today(),
        closing_probability=float(payload.get("closing_probability", 0.0)),
        status=OpportunityStatus(str(payload.get("status", OpportunityStatus.NEGOTIATION.value))),
        loss_reason=loss_reason,
        loss_spin_stage=SpinStage(loss_spin_stage) if loss_spin_stage else None,
        spin_situation=payload.get("spin_situation"),
        spin_problem=payload.get("spin_problem"),
        spin_implication=payload.get("spin_implication"),
        spin_need=payload.get("spin_need"),
        identified_objections=list(payload.get("identified_objections", [])),
        realized_value=(
            float(payload["realized_value"])
            if payload.get("realized_value") is not None
            else None
        ),
        closing_date=_date_from_str(payload.get("closing_date")),
    )


def save_repository(
    repo: ForecastRepository,
    path: Path,
    *,
    next_opportunity_id: int,
    next_loss_reason_id: int,
) -> None:
    """Salva o conteúdo do repositório em um arquivo JSON."""

    payload = {
        "loss_reasons": [
            _serialize_loss_reason(reason) for reason in repo.list_loss_reasons(active_only=False)
        ],
        "opportunities": [
            _serialize_opportunity(opportunity) for opportunity in repo.list_opportunities()
        ],
        "metadata": {
            "next_opportunity_id": next_opportunity_id,
            "next_loss_reason_id": next_loss_reason_id,
        },
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_repository(path: Path) -> Tuple[ForecastRepository, int, int]:
    """Carrega um repositório previamente salvo.

    Retorna o repositório reconstruído e os próximos IDs para oportunidades e motivos.
    """

    repo = ForecastRepository()
    next_opportunity_id = 1
    next_loss_reason_id = 1

    if not path.exists():
        return repo, next_opportunity_id, next_loss_reason_id

    payload = json.loads(path.read_text(encoding="utf-8"))
    reason_map: Dict[int, LossReason] = {}
    for item in payload.get("loss_reasons", []):
        reason = _deserialize_loss_reason(item)
        repo.add_loss_reason(reason)
        reason_map[reason.id] = reason

    for item in payload.get("opportunities", []):
        opportunity = _deserialize_opportunity(item, loss_reasons=reason_map)
        repo.add_opportunity(opportunity)

    metadata = payload.get("metadata", {})
    next_opportunity_id = int(metadata.get("next_opportunity_id", next_opportunity_id))
    next_loss_reason_id = int(metadata.get("next_loss_reason_id", next_loss_reason_id))

    return repo, next_opportunity_id, next_loss_reason_id


__all__ = ["load_repository", "save_repository"]
