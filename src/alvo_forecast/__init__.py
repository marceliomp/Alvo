"""Pacote principal do Alvo Forecast."""

from .models import Opportunity, LossReason, OpportunityStatus, SpinStage
from .repository import ForecastRepository
from .analytics import (
    forecast_vs_realized,
    loss_reason_summary,
    spin_stage_blockers,
    objections_report,
)
from .exporters import export_opportunities_to_csv
from .storage import load_repository, save_repository

__all__ = [
    "Opportunity",
    "LossReason",
    "OpportunityStatus",
    "SpinStage",
    "ForecastRepository",
    "forecast_vs_realized",
    "loss_reason_summary",
    "spin_stage_blockers",
    "objections_report",
    "export_opportunities_to_csv",
    "load_repository",
    "save_repository",
]
