"""Modelos de domínio para o Alvo Forecast."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional


class OpportunityStatus(str, Enum):
    """Status possíveis de uma oportunidade."""

    NEGOTIATION = "em_negociacao"
    WON = "ganha"
    LOST = "perdida"


class SpinStage(str, Enum):
    """Etapas do método SPIN."""

    SITUATION = "situacao"
    PROBLEM = "problema"
    IMPLICATION = "implicacao"
    NEED_PAYOFF = "necessidade"


@dataclass(slots=True)
class LossReason:
    """Motivo de perda."""

    id: int
    description: str
    active: bool = True


@dataclass(slots=True)
class Opportunity:
    """Representa uma oportunidade cadastrada."""

    id: int
    created_at: date
    broker: str
    development: str
    expected_value: float
    forecast_date: date
    closing_probability: float
    status: OpportunityStatus
    loss_reason: Optional[LossReason] = None
    loss_spin_stage: Optional[SpinStage] = None
    spin_situation: Optional[str] = None
    spin_problem: Optional[str] = None
    spin_implication: Optional[str] = None
    spin_need: Optional[str] = None
    identified_objections: List[str] = field(default_factory=list)
    realized_value: Optional[float] = None
    closing_date: Optional[date] = None

    def require_spin(self, threshold: float) -> bool:
        """Indica se os campos SPIN são obrigatórios de acordo com o valor."""

        return self.expected_value >= threshold

    def is_lost(self) -> bool:
        """Indica se a oportunidade foi perdida."""

        return self.status == OpportunityStatus.LOST

    def is_won(self) -> bool:
        """Indica se a oportunidade foi ganha."""

        return self.status == OpportunityStatus.WON


__all__ = [
    "LossReason",
    "Opportunity",
    "OpportunityStatus",
    "SpinStage",
]
