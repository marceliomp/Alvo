"""Repositório em memória para oportunidades e motivos de perda."""
from __future__ import annotations

from dataclasses import replace
from typing import Dict, Iterable, List, Optional

from .models import LossReason, Opportunity, OpportunityStatus


class ForecastRepository:
    """Repositório simples para gerenciar o ciclo de vida dos dados."""

    def __init__(self) -> None:
        self._opportunities: Dict[int, Opportunity] = {}
        self._loss_reasons: Dict[int, LossReason] = {}

    # --- Motivos de perda -------------------------------------------------
    def add_loss_reason(self, reason: LossReason) -> None:
        self._loss_reasons[reason.id] = reason

    def get_loss_reason(self, reason_id: int) -> Optional[LossReason]:
        """Recupera um motivo de perda pelo identificador."""

        return self._loss_reasons.get(reason_id)

    def list_loss_reasons(self, active_only: bool = True) -> List[LossReason]:
        reasons = self._loss_reasons.values()
        if active_only:
            return [reason for reason in reasons if reason.active]
        return list(reasons)

    # --- Oportunidades ----------------------------------------------------
    def add_opportunity(self, opportunity: Opportunity) -> None:
        self._opportunities[opportunity.id] = opportunity

    def update_opportunity(self, opportunity_id: int, **changes) -> Opportunity:
        opportunity = self._opportunities[opportunity_id]
        updated = replace(opportunity, **changes)
        self._opportunities[opportunity_id] = updated
        return updated

    def get_opportunity(self, opportunity_id: int) -> Optional[Opportunity]:
        return self._opportunities.get(opportunity_id)

    def list_opportunities(
        self,
        *,
        status: Optional[OpportunityStatus] = None,
    ) -> List[Opportunity]:
        if status is None:
            return list(self._opportunities.values())
        return [opp for opp in self._opportunities.values() if opp.status == status]

    def opportunities_requiring_spin(self, threshold: float) -> List[Opportunity]:
        return [
            opp
            for opp in self._opportunities.values()
            if opp.require_spin(threshold)
        ]

    def iter_opportunities(self) -> Iterable[Opportunity]:
        return self._opportunities.values()


__all__ = ["ForecastRepository"]
