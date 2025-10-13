"""Interface Streamlit para o Alvo Forecast."""
from __future__ import annotations

import io
from datetime import date

import pandas as pd
import streamlit as st

from alvo_forecast import (
    ForecastRepository,
    LossReason,
    Opportunity,
    OpportunityStatus,
    SpinStage,
    forecast_vs_realized,
    loss_reason_summary,
    objections_report,
    spin_stage_blockers,
)

STATUS_LABELS = {
    OpportunityStatus.NEGOTIATION: "Em negociação",
    OpportunityStatus.WON: "Ganha",
    OpportunityStatus.LOST: "Perdida",
}

SPIN_STAGE_LABELS = {
    SpinStage.SITUATION: "Situação",
    SpinStage.PROBLEM: "Problema",
    SpinStage.IMPLICATION: "Implicação",
    SpinStage.NEED_PAYOFF: "Necessidade",
}

DEFAULT_LOSS_REASONS = [
    "Preço acima do esperado",
    "Concorrência",
    "Sem orçamento disponível",
    "Mudança de prioridade do cliente",
]


def _init_session_state() -> None:
    if "repo" not in st.session_state:
        st.session_state.repo = ForecastRepository()
        st.session_state.next_opportunity_id = 1
        st.session_state.next_loss_reason_id = 1
        _seed_default_loss_reasons()


def _seed_default_loss_reasons() -> None:
    repo: ForecastRepository = st.session_state.repo
    if repo.list_loss_reasons(active_only=False):
        return
    for description in DEFAULT_LOSS_REASONS:
        reason = LossReason(
            id=st.session_state.next_loss_reason_id,
            description=description,
            active=True,
        )
        repo.add_loss_reason(reason)
        st.session_state.next_loss_reason_id += 1


def _create_opportunity_row(opportunity: Opportunity) -> dict:
    return {
        "ID": opportunity.id,
        "Criada em": opportunity.created_at,
        "Corretor": opportunity.broker,
        "Empreendimento": opportunity.development,
        "Valor previsto": opportunity.expected_value,
        "Data do forecast": opportunity.forecast_date,
        "Probabilidade": f"{opportunity.closing_probability:.0%}",
        "Status": STATUS_LABELS[opportunity.status],
        "Motivo da perda": (
            opportunity.loss_reason.description if opportunity.loss_reason else ""
        ),
        "Etapa SPIN": (
            SPIN_STAGE_LABELS[opportunity.loss_spin_stage]
            if opportunity.loss_spin_stage
            else ""
        ),
        "SPIN - Situação": opportunity.spin_situation or "",
        "SPIN - Problema": opportunity.spin_problem or "",
        "SPIN - Implicação": opportunity.spin_implication or "",
        "SPIN - Necessidade": opportunity.spin_need or "",
        "Objeções": ", ".join(opportunity.identified_objections),
        "Valor realizado": opportunity.realized_value,
        "Data de fechamento": opportunity.closing_date,
    }


def _render_loss_reason_form() -> None:
    repo: ForecastRepository = st.session_state.repo

    with st.sidebar.expander("Cadastrar novo motivo de perda"):
        with st.form("loss_reason_form", clear_on_submit=True):
            description = st.text_input("Descrição do motivo")
            active = st.checkbox("Motivo ativo", value=True)
            submitted = st.form_submit_button("Adicionar motivo")
            if submitted:
                normalized = description.strip()
                if not normalized:
                    st.error("Informe uma descrição válida.")
                else:
                    reason = LossReason(
                        id=st.session_state.next_loss_reason_id,
                        description=normalized,
                        active=active,
                    )
                    repo.add_loss_reason(reason)
                    st.session_state.next_loss_reason_id += 1
                    st.success("Motivo cadastrado com sucesso!")

    loss_reasons = repo.list_loss_reasons(active_only=False)
    if loss_reasons:
        loss_reason_table = pd.DataFrame(
            [
                {
                    "ID": reason.id,
                    "Descrição": reason.description,
                    "Ativo": "Sim" if reason.active else "Não",
                }
                for reason in loss_reasons
            ]
        )
        st.sidebar.dataframe(loss_reason_table, width="stretch")
    else:
        st.sidebar.info("Nenhum motivo de perda cadastrado.")


def _render_opportunity_form() -> None:
    repo: ForecastRepository = st.session_state.repo

    st.subheader("Cadastrar oportunidade")
    with st.form("opportunity_form", clear_on_submit=True):
        cols_top = st.columns(3)
        created_at = cols_top[0].date_input(
            "Data de criação", value=date.today(), format="DD/MM/YYYY"
        )
        forecast_date = cols_top[1].date_input(
            "Data do forecast", value=date.today(), format="DD/MM/YYYY"
        )
        expected_value = cols_top[2].number_input(
            "Valor previsto (R$)", min_value=0.0, step=1000.0
        )

        broker = st.text_input("Corretor responsável")
        development = st.text_input("Empreendimento")

        probability_percentage = st.slider(
            "Probabilidade de fechamento (%)",
            min_value=0,
            max_value=100,
            value=50,
            step=5,
        )

        status = st.selectbox(
            "Status",
            options=list(STATUS_LABELS.keys()),
            format_func=lambda status: STATUS_LABELS[status],
        )

        loss_reason_id = None
        loss_spin_stage = None
        if status == OpportunityStatus.LOST:
            loss_reasons = repo.list_loss_reasons()
            if loss_reasons:
                reason_choice = st.selectbox(
                    "Motivo da perda",
                    options=[(-1, "Selecione um motivo")] + [
                        (reason.id, reason.description) for reason in loss_reasons
                    ],
                    format_func=lambda item: item[1],
                )
                if reason_choice[0] != -1:
                    loss_reason_id = reason_choice[0]
            else:
                st.warning("Cadastre ao menos um motivo de perda na barra lateral.")

            loss_spin_stage = st.selectbox(
                "Etapa SPIN onde ocorreu a perda",
                options=list(SPIN_STAGE_LABELS.keys()),
                format_func=lambda stage: SPIN_STAGE_LABELS[stage],
            )

        spin_situation = st.text_area("SPIN - Situação")
        spin_problem = st.text_area("SPIN - Problema")
        spin_implication = st.text_area("SPIN - Implicação")
        spin_need = st.text_area("SPIN - Necessidade")

        objections_text = st.text_area(
            "Objeções identificadas (uma por linha)",
            help="Separe cada objeção com uma quebra de linha.",
        )

        realized_value = None
        closing_date = None
        if status == OpportunityStatus.WON:
            realized_value = st.number_input(
                "Valor realizado (R$)",
                min_value=0.0,
                step=1000.0,
            )
            inform_closing_date = st.checkbox("Informar data de fechamento")
            if inform_closing_date:
                closing_date = st.date_input(
                    "Data de fechamento",
                    value=date.today(),
                    format="DD/MM/YYYY",
                )

        submitted = st.form_submit_button("Salvar oportunidade")

        if submitted:
            normalized_broker = broker.strip()
            normalized_development = development.strip()
            if not normalized_broker or not normalized_development:
                st.error("Informe o corretor e o empreendimento.")
                return

            if status == OpportunityStatus.LOST and loss_reason_id is None:
                st.error("Selecione um motivo de perda para oportunidades perdidas.")
                return

            objections = [
                line.strip()
                for line in objections_text.splitlines()
                if line.strip()
            ]

            opportunity = Opportunity(
                id=st.session_state.next_opportunity_id,
                created_at=created_at,
                broker=normalized_broker,
                development=normalized_development,
                expected_value=float(expected_value),
                forecast_date=forecast_date,
                closing_probability=probability_percentage / 100,
                status=status,
                loss_reason=(
                    repo.get_loss_reason(loss_reason_id)
                    if loss_reason_id is not None
                    else None
                ),
                loss_spin_stage=loss_spin_stage,
                spin_situation=spin_situation or None,
                spin_problem=spin_problem or None,
                spin_implication=spin_implication or None,
                spin_need=spin_need or None,
                identified_objections=objections,
                realized_value=realized_value if status == OpportunityStatus.WON else None,
                closing_date=closing_date if status == OpportunityStatus.WON else None,
            )

            repo.add_opportunity(opportunity)
            st.session_state.next_opportunity_id += 1
            st.success("Oportunidade salva com sucesso!")


def _render_opportunities_table() -> None:
    repo: ForecastRepository = st.session_state.repo
    opportunities = repo.list_opportunities()
    if not opportunities:
        st.info("Nenhuma oportunidade cadastrada até o momento.")
        return

    table = pd.DataFrame([_create_opportunity_row(opp) for opp in opportunities])
    st.dataframe(table, width="stretch")

    csv_buffer = io.StringIO()
    table.to_csv(csv_buffer, index=False)
    st.download_button(
        "Exportar oportunidades para CSV",
        data=csv_buffer.getvalue().encode("utf-8"),
        file_name="oportunidades.csv",
        mime="text/csv",
    )


def _render_analytics() -> None:
    repo: ForecastRepository = st.session_state.repo
    opportunities = list(repo.iter_opportunities())
    if not opportunities:
        return

    st.subheader("Dashboard analítico")
    group_options = {
        "mes": "Mês",
        "corretor": "Corretor",
        "empreendimento": "Empreendimento",
    }
    group_key = st.selectbox(
        "Agrupar previsão vs. realizado por",
        options=list(group_options.keys()),
        format_func=lambda key: group_options[key],
    )
    forecast_rows = forecast_vs_realized(opportunities, group_by=group_key)
    if forecast_rows:
        forecast_df = pd.DataFrame(
            [
                {
                    "Agrupamento": row.group,
                    "Valor previsto": row.forecast_value,
                    "Valor realizado": row.realized_value,
                }
                for row in forecast_rows
            ]
        ).set_index("Agrupamento")
        st.bar_chart(forecast_df)
    else:
        st.info("Ainda não há dados suficientes para o gráfico de previsão vs. realizado.")

    cols = st.columns(3)

    loss_summary = loss_reason_summary(opportunities)
    if loss_summary:
        loss_df = pd.DataFrame(
            {"Motivo": list(loss_summary.keys()), "Ocorrências": list(loss_summary.values())}
        )
        cols[0].table(loss_df)
    else:
        cols[0].info("Nenhuma perda registrada.")

    spin_summary = spin_stage_blockers(opportunities)
    if spin_summary:
        spin_df = pd.DataFrame(
            {
                "Etapa": [SPIN_STAGE_LABELS[stage] for stage in spin_summary.keys()],
                "Ocorrências": list(spin_summary.values()),
            }
        )
        cols[1].table(spin_df)
    else:
        cols[1].info("Nenhum gargalo SPIN registrado.")

    objections_summary = objections_report(opportunities)
    if objections_summary:
        objections_df = pd.DataFrame(
            {
                "Objeção": list(objections_summary.keys()),
                "Ocorrências": list(objections_summary.values()),
            }
        )
        cols[2].table(objections_df)
    else:
        cols[2].info("Nenhuma objeção registrada.")


def main() -> None:
    st.set_page_config(page_title="Alvo Forecast", layout="wide")
    _init_session_state()

    st.title("Alvo Forecast")
    st.caption("Plataforma para registrar e analisar oportunidades com metodologia SPIN")

    _render_loss_reason_form()
    _render_opportunity_form()
    _render_opportunities_table()
    _render_analytics()


if __name__ == "__main__":
    main()

