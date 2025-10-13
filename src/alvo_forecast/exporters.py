"""Funções utilitárias para exportação de dados."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from .models import Opportunity


def export_opportunities_to_csv(
    opportunities: Iterable[Opportunity],
    file_path: Path,
) -> None:
    """Exporta oportunidades para um arquivo CSV."""

    headers = [
        "id",
        "data_criacao",
        "corretor",
        "empreendimento",
        "valor_previsto",
        "data_forecast",
        "probabilidade_fechamento",
        "status",
        "motivo_perda",
        "etapa_spin_perda",
        "spin_situacao",
        "spin_problema",
        "spin_implicacao",
        "spin_necessidade",
        "objeções_identificadas",
        "valor_realizado",
        "data_fechamento",
    ]

    with file_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for opportunity in opportunities:
            writer.writerow(
                {
                    "id": opportunity.id,
                    "data_criacao": opportunity.created_at.isoformat(),
                    "corretor": opportunity.broker,
                    "empreendimento": opportunity.development,
                    "valor_previsto": f"{opportunity.expected_value:.2f}",
                    "data_forecast": opportunity.forecast_date.isoformat(),
                    "probabilidade_fechamento": f"{opportunity.closing_probability:.0%}",
                    "status": opportunity.status.value,
                    "motivo_perda": (
                        opportunity.loss_reason.description
                        if opportunity.loss_reason
                        else ""
                    ),
                    "etapa_spin_perda": (
                        opportunity.loss_spin_stage.value
                        if opportunity.loss_spin_stage
                        else ""
                    ),
                    "spin_situacao": opportunity.spin_situation or "",
                    "spin_problema": opportunity.spin_problem or "",
                    "spin_implicacao": opportunity.spin_implication or "",
                    "spin_necessidade": opportunity.spin_need or "",
                    "objeções_identificadas": "; ".join(opportunity.identified_objections),
                    "valor_realizado": (
                        f"{opportunity.realized_value:.2f}"
                        if opportunity.realized_value is not None
                        else ""
                    ),
                    "data_fechamento": (
                        opportunity.closing_date.isoformat()
                        if opportunity.closing_date is not None
                        else ""
                    ),
                }
            )


__all__ = ["export_opportunities_to_csv"]
