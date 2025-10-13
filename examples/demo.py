"""Exemplo de uso do pacote Alvo Forecast."""
from __future__ import annotations

from datetime import date
from pathlib import Path

from alvo_forecast import (
    ForecastRepository,
    LossReason,
    Opportunity,
    OpportunityStatus,
    SpinStage,
    export_opportunities_to_csv,
    forecast_vs_realized,
    loss_reason_summary,
    objections_report,
    spin_stage_blockers,
)


def _seed_repository(repo: ForecastRepository) -> None:
    price_threshold = 800_000.0
    cheaper_competitor = LossReason(id=1, description="Concorrente com preço menor")
    credit_denied = LossReason(id=2, description="Cliente sem crédito aprovado")

    repo.add_loss_reason(cheaper_competitor)
    repo.add_loss_reason(credit_denied)

    repo.add_opportunity(
        Opportunity(
            id=1,
            created_at=date(2024, 1, 12),
            broker="Alice",
            development="Residencial Horizonte",
            expected_value=900_000.0,
            forecast_date=date(2024, 2, 15),
            closing_probability=0.7,
            status=OpportunityStatus.WON,
            spin_situation="Família buscando upgrade de imóvel",
            spin_problem="Imóvel atual pequeno para família em crescimento",
            spin_implication="Desconforto e falta de espaço para home office",
            spin_need="Busca de condomínio com lazer e espaço extra",
            identified_objections=["Valor do condomínio"],
            realized_value=880_000.0,
            closing_date=date(2024, 2, 20),
        )
    )

    repo.add_opportunity(
        Opportunity(
            id=2,
            created_at=date(2024, 1, 20),
            broker="Bruno",
            development="Parque das Águas",
            expected_value=650_000.0,
            forecast_date=date(2024, 3, 10),
            closing_probability=0.5,
            status=OpportunityStatus.LOST,
            loss_reason=cheaper_competitor,
            loss_spin_stage=SpinStage.PROBLEM,
            spin_situation="Cliente deseja investir em imóvel para renda",
            spin_problem="Retorno financeiro percebido como baixo",
            spin_implication="Investimento redirecionado para renda fixa",
            spin_need="Garantir renda mensal mínima de R$4.000",
            identified_objections=["Taxa de condomínio", "Localização"],
        )
    )

    repo.add_opportunity(
        Opportunity(
            id=3,
            created_at=date(2024, 2, 5),
            broker="Alice",
            development="Residencial Horizonte",
            expected_value=1_100_000.0,
            forecast_date=date(2024, 4, 1),
            closing_probability=0.4,
            status=OpportunityStatus.LOST,
            loss_reason=credit_denied,
            loss_spin_stage=SpinStage.IMPLICATION,
            spin_situation="Cliente precisa mudar rapidamente",
            spin_problem="Financiamento negado",
            spin_implication="Cliente perdeu prazo para mudança",
            spin_need="Aprovação de crédito emergencial",
            identified_objections=["Prazo de entrega"],
        )
    )

    for opp in repo.opportunities_requiring_spin(price_threshold):
        assert opp.spin_situation, "Campos SPIN devem estar preenchidos para tickets altos"


def main() -> None:
    repo = ForecastRepository()
    _seed_repository(repo)

    opportunities = repo.list_opportunities()
    print("Previsão vs Realizado por mês:")
    for row in forecast_vs_realized(opportunities, group_by="mes"):
        print(f"- {row.group}: previsto R${row.forecast_value:,.2f} | realizado R${row.realized_value:,.2f}")

    print("\nMotivos de perda:")
    for reason, count in loss_reason_summary(opportunities).most_common():
        print(f"- {reason}: {count}")

    print("\nEtapas SPIN com mais perdas:")
    for stage, count in spin_stage_blockers(opportunities).most_common():
        print(f"- {stage.value}: {count}")

    print("\nObjeções recorrentes:")
    for objection, count in objections_report(opportunities).items():
        print(f"- {objection}: {count}")

    export_path = Path("/tmp/oportunidades.csv")
    export_opportunities_to_csv(opportunities, export_path)
    print(f"\nExportação realizada em {export_path}")


if __name__ == "__main__":
    main()
