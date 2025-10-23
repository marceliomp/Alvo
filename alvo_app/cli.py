"""Command line interface for the Alvo financial scenario simulator."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .calculator import (
    Scenario,
    ScenarioMetrics,
    Sale,
    format_currency,
    render_broker_table,
    render_differences_table,
    render_metrics_table,
)


def load_scenario(path: Path) -> Scenario:
    data = json.loads(path.read_text(encoding="utf-8"))
    sales = [Sale.from_dict(item) for item in data.get("sales", [])]
    fixed_costs = {str(k): float(v) for k, v in data.get("fixed_costs", {}).items()}
    return Scenario(
        name=data.get("name", path.stem),
        sales=sales,
        fixed_costs=fixed_costs,
        other_income=float(data.get("other_income", 0.0)),
        other_expenses=float(data.get("other_expenses", 0.0)),
        depreciation=float(data.get("depreciation", 0.0)),
        amortization=float(data.get("amortization", 0.0)),
    )


def apply_overrides(scenario: Scenario, overrides: Iterable[str]) -> None:
    for override in overrides:
        if "=" not in override:
            raise ValueError(f"Override '{override}' must be in the format chave=valor")
        key, raw_value = override.split("=", 1)
        value = float(raw_value)
        if key.startswith("fixed."):
            scenario.apply_fixed_cost_override(key.split(".", 1)[1], value)
        elif key.startswith("sale."):
            parts = key.split(".")
            if len(parts) != 3:
                raise ValueError(
                    "Use o formato sale.ID.campo=valor. Exemplo: sale.V001.sale_value=1000000"
                )
            _, identifier, field = parts
            try:
                scenario.apply_sale_override(identifier, field, value)
            except KeyError as exc:
                raise ValueError(str(exc)) from exc
        elif key in {"other_income", "other_expenses", "depreciation", "amortization"}:
            setattr(scenario, key, value)
        else:
            raise ValueError(
                "Use o prefixo 'fixed.' para custos fixos ou 'sale.' para vendas, por exemplo "
                "fixed.aluguel=12000 ou sale.V001.commission_rate=0.05. "
                "Para ajustar outros itens utilize other_income=1000, other_expenses=500 etc."
            )


def apply_scaling(scenario: Scenario, args: argparse.Namespace) -> None:
    if args.scale_revenue is not None or args.scale_variable_costs is not None or args.scale_fixed_costs is not None:
        scenario.apply_global_scaling(
            revenue_multiplier=args.scale_revenue,
            variable_cost_multiplier=args.scale_variable_costs,
            fixed_cost_multiplier=args.scale_fixed_costs,
        )
    for broker_scale in args.scale_broker or []:
        broker, field, raw_multiplier = parse_three_part_entry(
            broker_scale,
            "Use o formato 'NomeDoCorretor.campo=valor'. Campos suportados: sale_value, revenue, variable_costs",
        )
        multiplier = float(raw_multiplier)
        if field in {"revenue", "sale_value"}:
            scenario.apply_broker_scaling(broker, revenue_multiplier=multiplier)
        elif field == "variable_costs":
            scenario.apply_broker_scaling(broker, variable_cost_multiplier=multiplier)
        else:
            raise ValueError(
                "Campo inválido para escala de corretor: utilize sale_value (ou revenue) ou variable_costs"
            )


def parse_three_part_entry(raw: str, error_message: str) -> List[str]:
    if "=" not in raw:
        raise ValueError(error_message)
    lhs, rhs = raw.split("=", 1)
    parts = lhs.split(".")
    if len(parts) != 2:
        raise ValueError(error_message)
    return [parts[0], parts[1], rhs]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simulador de margem de contribuição e EBITDA")
    parser.add_argument("scenario", type=Path, help="Arquivo JSON com a definição do cenário")
    parser.add_argument(
        "--scale-revenue",
        type=float,
        help="Multiplicador para o valor de venda (e consequentemente a comissão) de todas as vendas",
    )
    parser.add_argument(
        "--scale-variable-costs",
        type=float,
        help="Multiplicador para os custos variáveis de todas as vendas",
    )
    parser.add_argument(
        "--scale-fixed-costs",
        type=float,
        help="Multiplicador para os custos fixos",
    )
    parser.add_argument(
        "--scale-broker",
        action="append",
        help="Ajuste específico por corretor (ex: 'Maria.sale_value=1.1' ou 'Joao.variable_costs=0.9')",
    )
    parser.add_argument(
        "--override",
        action="append",
        help="Sobrescreve valores específicos. Use 'fixed.nome=valor' ou 'sale.ID.campo=valor'",
    )
    parser.add_argument(
        "--save",
        type=Path,
        help="Salva o cenário ajustado em um novo arquivo JSON",
    )
    return parser


def display_results(base_metrics: ScenarioMetrics, updated_metrics: ScenarioMetrics, scenario: Scenario) -> None:
    print("=== Indicadores do Cenário ===")
    print(render_metrics_table(updated_metrics))
    print()
    if base_metrics != updated_metrics:
        print("=== Comparativo vs. Base ===")
        print(render_differences_table(updated_metrics.difference(base_metrics)))
        print()
    print("=== Contribuição por Corretor ===")
    print(render_broker_table(scenario.broker_contribution()))
    print()
    print("Custos Fixos:")
    for name, value in sorted(scenario.fixed_costs.items()):
        print(f"  - {name}: {format_currency(value)}")
    if scenario.other_income or scenario.other_expenses:
        print()
        print("Outros Itens:")
        if scenario.other_income:
            print(f"  + Outras Receitas: {format_currency(scenario.other_income)}")
        if scenario.other_expenses:
            print(f"  - Outras Despesas: {format_currency(scenario.other_expenses)}")
    if scenario.depreciation or scenario.amortization:
        print()
        print("Depreciação & Amortização:")
        if scenario.depreciation:
            print(f"  - Depreciação: {format_currency(scenario.depreciation)}")
        if scenario.amortization:
            print(f"  - Amortização: {format_currency(scenario.amortization)}")


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    scenario_path: Path = args.scenario
    scenario = load_scenario(scenario_path)
    base_metrics = scenario.summary()

    adjusted = scenario.clone()
    apply_scaling(adjusted, args)
    if args.override:
        apply_overrides(adjusted, args.override)
    updated_metrics = adjusted.summary()

    display_results(base_metrics, updated_metrics, adjusted)

    if args.save:
        save_data: Dict[str, object] = {
            "name": adjusted.name,
            "sales": [
                {
                    "id": sale.id,
                    "broker": sale.broker,
                    "sale_value": sale.sale_value,
                    "commission_rate": sale.commission_rate,
                    **({"revenue": sale.revenue} if sale._manual_revenue is not None else {}),
                    "variable_costs": sale.variable_costs,
                    "notes": sale.notes,
                }
                for sale in adjusted.sales
            ],
            "fixed_costs": adjusted.fixed_costs,
            "other_income": adjusted.other_income,
            "other_expenses": adjusted.other_expenses,
            "depreciation": adjusted.depreciation,
            "amortization": adjusted.amortization,
        }
        args.save.write_text(json.dumps(save_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print()
        print(f"Cenário salvo em {args.save}")


if __name__ == "__main__":
    main()
