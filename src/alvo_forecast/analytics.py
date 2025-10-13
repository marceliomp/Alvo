"""Funções analíticas para o dashboard do Alvo Forecast."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List, Literal

from .models import Opportunity, SpinStage

GroupByOption = Literal["mes", "corretor", "empreendimento"]


@dataclass
class ForecastRealizedRow:
    """Linha agregada de previsão versus realizado."""

    group: str
    forecast_value: float
    realized_value: float


def _group_key(opportunity: Opportunity, group_by: GroupByOption) -> str:
    if group_by == "mes":
        month = opportunity.forecast_date.replace(day=1)
        return month.isoformat()
    if group_by == "corretor":
        return opportunity.broker
    if group_by == "empreendimento":
        return opportunity.development
    raise ValueError(f"Agrupamento não suportado: {group_by}")


def forecast_vs_realized(
    opportunities: Iterable[Opportunity],
    *,
    group_by: GroupByOption = "mes",
) -> List[ForecastRealizedRow]:
    """Agrega os valores previstos e realizados por agrupamento."""

    aggregated: Dict[str, ForecastRealizedRow] = {}
    for opportunity in opportunities:
        group = _group_key(opportunity, group_by)
        row = aggregated.setdefault(
            group,
            ForecastRealizedRow(group=group, forecast_value=0.0, realized_value=0.0),
        )
        row.forecast_value += opportunity.expected_value
        if opportunity.is_won() and opportunity.realized_value is not None:
            row.realized_value += opportunity.realized_value
    return sorted(aggregated.values(), key=lambda r: r.group)


def loss_reason_summary(opportunities: Iterable[Opportunity]) -> Counter[str]:
    """Retorna a contagem de motivos de perda."""

    summary: Counter[str] = Counter()
    for opportunity in opportunities:
        if opportunity.is_lost() and opportunity.loss_reason:
            summary[opportunity.loss_reason.description] += 1
    return summary


def spin_stage_blockers(opportunities: Iterable[Opportunity]) -> Counter[SpinStage]:
    """Contabiliza em qual etapa do SPIN as oportunidades perdidas travaram."""

    summary: Counter[SpinStage] = Counter()
    for opportunity in opportunities:
        if opportunity.is_lost() and opportunity.loss_spin_stage:
            summary[opportunity.loss_spin_stage] += 1
    return summary


def objections_report(opportunities: Iterable[Opportunity]) -> Dict[str, int]:
    """Gera um ranking das objeções mais recorrentes."""

    occurrences: Dict[str, int] = defaultdict(int)
    for opportunity in opportunities:
        for objection in opportunity.identified_objections:
            normalized = objection.strip().lower()
            if not normalized:
                continue
            occurrences[normalized] += 1
    return dict(sorted(occurrences.items(), key=lambda item: item[1], reverse=True))


__all__ = [
    "GroupByOption",
    "ForecastRealizedRow",
    "forecast_vs_realized",
    "loss_reason_summary",
    "spin_stage_blockers",
    "objections_report",
]
