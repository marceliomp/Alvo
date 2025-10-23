"""Core financial models and calculations for the Alvo Forecast app."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, MutableMapping, Optional


@dataclass
class Sale:
    """Represents a single sale made by a broker."""

    id: str
    broker: str
    sale_value: float
    commission_rate: float = 1.0
    variable_costs: Dict[str, float] = field(default_factory=dict)
    notes: Optional[str] = None
    _manual_revenue: Optional[float] = field(default=None, repr=False)

    @property
    def revenue(self) -> float:
        """Commission revenue earned by Alvo for the sale."""

        if self._manual_revenue is not None:
            return self._manual_revenue
        return self.sale_value * self.commission_rate

    @revenue.setter
    def revenue(self, value: float) -> None:
        self._manual_revenue = value

    def clear_manual_revenue(self) -> None:
        self._manual_revenue = None

    def scale_revenue(self, multiplier: float) -> None:
        if self._manual_revenue is not None:
            self._manual_revenue *= multiplier
        else:
            self.sale_value *= multiplier

    @property
    def total_variable_costs(self) -> float:
        """Return the sum of the variable costs for the sale."""

        return float(sum(self.variable_costs.values()))

    @property
    def contribution_margin(self) -> float:
        """Contribution margin of the sale."""

        return self.revenue - self.total_variable_costs

    @property
    def contribution_margin_ratio(self) -> float:
        """Contribution margin ratio of the sale (percentage expressed as decimal)."""

        if self.revenue == 0:
            return 0.0
        return self.contribution_margin / self.revenue

    @classmethod
    def from_dict(cls, payload: MutableMapping[str, object]) -> "Sale":
        """Create a :class:`Sale` instance from a JSON-friendly dictionary."""

        variable_costs_payload = payload.get("variable_costs", {})
        if isinstance(variable_costs_payload, MutableMapping):
            variable_costs = {str(k): float(v) for k, v in variable_costs_payload.items()}
        else:
            variable_costs = {"total": float(variable_costs_payload)}
        manual_revenue: Optional[float] = None
        if "sale_value" in payload:
            sale_value = float(payload["sale_value"])
        elif "revenue" in payload:
            sale_value = float(payload["revenue"])
            manual_revenue = float(payload["revenue"])
        else:
            raise KeyError("Sale entry must contain 'sale_value' or 'revenue'")
        commission_rate = float(payload.get("commission_rate", 1.0))
        sale = cls(
            id=str(payload["id"]),
            broker=str(payload["broker"]),
            sale_value=sale_value,
            commission_rate=commission_rate,
            variable_costs=variable_costs,
            notes=str(payload.get("notes")) if payload.get("notes") is not None else None,
        )
        if "revenue" in payload and "sale_value" in payload:
            sale.revenue = float(payload["revenue"])
        elif manual_revenue is not None and "sale_value" not in payload:
            sale.revenue = manual_revenue
        return sale


@dataclass
class Scenario:
    """Financial scenario definition."""

    name: str
    sales: List[Sale]
    fixed_costs: Dict[str, float] = field(default_factory=dict)
    other_income: float = 0.0
    other_expenses: float = 0.0
    depreciation: float = 0.0
    amortization: float = 0.0

    @property
    def total_revenue(self) -> float:
        return float(sum(sale.revenue for sale in self.sales))

    @property
    def total_variable_costs(self) -> float:
        return float(sum(sale.total_variable_costs for sale in self.sales))

    @property
    def contribution_margin(self) -> float:
        return self.total_revenue - self.total_variable_costs

    @property
    def fixed_cost_total(self) -> float:
        return float(sum(self.fixed_costs.values()))

    def broker_contribution(self) -> Dict[str, Dict[str, float]]:
        """Aggregate metrics by broker."""

        summary: Dict[str, Dict[str, float]] = {}
        for sale in self.sales:
            broker_stats = summary.setdefault(
                sale.broker,
                {"revenue": 0.0, "variable_costs": 0.0, "contribution_margin": 0.0},
            )
            broker_stats["revenue"] += sale.revenue
            broker_stats["variable_costs"] += sale.total_variable_costs
            broker_stats["contribution_margin"] += sale.contribution_margin
        for stats in summary.values():
            revenue = stats["revenue"]
            stats["margin_ratio"] = stats["contribution_margin"] / revenue if revenue else 0.0
        return summary

    def clone(self) -> "Scenario":
        """Return a deep copy of the scenario."""

        cloned_sales: List[Sale] = []
        for sale in self.sales:
            new_sale = Sale(
                id=sale.id,
                broker=sale.broker,
                sale_value=sale.sale_value,
                commission_rate=sale.commission_rate,
                variable_costs=dict(sale.variable_costs),
                notes=sale.notes,
            )
            if sale._manual_revenue is not None:
                new_sale.revenue = sale._manual_revenue
            cloned_sales.append(new_sale)
        return Scenario(
            name=self.name,
            sales=cloned_sales,
            fixed_costs=dict(self.fixed_costs),
            other_income=self.other_income,
            other_expenses=self.other_expenses,
            depreciation=self.depreciation,
            amortization=self.amortization,
        )

    def apply_global_scaling(
        self,
        *,
        revenue_multiplier: Optional[float] = None,
        variable_cost_multiplier: Optional[float] = None,
        fixed_cost_multiplier: Optional[float] = None,
    ) -> None:
        """Scale financial values globally."""

        if revenue_multiplier is not None:
            for sale in self.sales:
                sale.scale_revenue(revenue_multiplier)
        if variable_cost_multiplier is not None:
            for sale in self.sales:
                for key in list(sale.variable_costs):
                    sale.variable_costs[key] *= variable_cost_multiplier
        if fixed_cost_multiplier is not None:
            for key in list(self.fixed_costs):
                self.fixed_costs[key] *= fixed_cost_multiplier

    def apply_broker_scaling(
        self,
        broker: str,
        *,
        revenue_multiplier: Optional[float] = None,
        variable_cost_multiplier: Optional[float] = None,
    ) -> None:
        """Scale values for a specific broker."""

        for sale in self.sales:
            if sale.broker.lower() != broker.lower():
                continue
            if revenue_multiplier is not None:
                sale.scale_revenue(revenue_multiplier)
            if variable_cost_multiplier is not None:
                for key in list(sale.variable_costs):
                    sale.variable_costs[key] *= variable_cost_multiplier

    def apply_sale_override(self, sale_id: str, field: str, value: float) -> None:
        """Override a specific field of a sale."""

        for sale in self.sales:
            if sale.id == sale_id:
                if field == "revenue":
                    sale.revenue = value
                elif field == "sale_value":
                    sale.sale_value = value
                    sale.clear_manual_revenue()
                elif field == "commission_rate":
                    sale.commission_rate = value
                    sale.clear_manual_revenue()
                elif field.startswith("variable_costs."):
                    _, subfield = field.split(".", 1)
                    sale.variable_costs[subfield] = value
                elif field == "variable_costs":
                    total = sale.total_variable_costs
                    if total == 0:
                        keys = list(sale.variable_costs.keys()) or ["total"]
                        per_key = value / len(keys)
                        for key in keys:
                            sale.variable_costs[key] = per_key
                    else:
                        factor = value / total
                        for key in list(sale.variable_costs):
                            sale.variable_costs[key] *= factor
                else:
                    sale.variable_costs[field] = value
                break
        else:
            raise KeyError(f"Sale with id '{sale_id}' not found")

    def apply_fixed_cost_override(self, cost_name: str, value: float) -> None:
        self.fixed_costs[cost_name] = value

    def summary(self) -> "ScenarioMetrics":
        return ScenarioMetrics.from_scenario(self)


@dataclass
class ScenarioMetrics:
    """Calculated KPIs for a scenario."""

    total_revenue: float
    total_variable_costs: float
    contribution_margin: float
    contribution_margin_ratio: float
    fixed_cost_total: float
    ebitda: float
    operating_profit: float
    net_margin: float
    break_even_revenue: Optional[float]

    @classmethod
    def from_scenario(cls, scenario: Scenario) -> "ScenarioMetrics":
        contribution_margin = scenario.contribution_margin
        total_revenue = scenario.total_revenue
        total_variable_costs = scenario.total_variable_costs
        fixed_cost_total = scenario.fixed_cost_total
        ebitda = contribution_margin - fixed_cost_total + scenario.other_income - scenario.other_expenses
        operating_profit = ebitda - scenario.depreciation - scenario.amortization
        margin_ratio = contribution_margin / total_revenue if total_revenue else 0.0
        net_margin = operating_profit / total_revenue if total_revenue else 0.0
        break_even_revenue: Optional[float]
        if margin_ratio > 0:
            break_even_revenue = fixed_cost_total / margin_ratio
        else:
            break_even_revenue = None
        return cls(
            total_revenue=total_revenue,
            total_variable_costs=total_variable_costs,
            contribution_margin=contribution_margin,
            contribution_margin_ratio=margin_ratio,
            fixed_cost_total=fixed_cost_total,
            ebitda=ebitda,
            operating_profit=operating_profit,
            net_margin=net_margin,
            break_even_revenue=break_even_revenue,
        )

    def difference(self, other: "ScenarioMetrics") -> "ScenarioMetrics":
        """Return the difference with another metrics snapshot."""

        return ScenarioMetrics(
            total_revenue=self.total_revenue - other.total_revenue,
            total_variable_costs=self.total_variable_costs - other.total_variable_costs,
            contribution_margin=self.contribution_margin - other.contribution_margin,
            contribution_margin_ratio=self.contribution_margin_ratio - other.contribution_margin_ratio,
            fixed_cost_total=self.fixed_cost_total - other.fixed_cost_total,
            ebitda=self.ebitda - other.ebitda,
            operating_profit=self.operating_profit - other.operating_profit,
            net_margin=self.net_margin - other.net_margin,
            break_even_revenue=(
                (self.break_even_revenue or 0.0) - (other.break_even_revenue or 0.0)
                if self.break_even_revenue is not None and other.break_even_revenue is not None
                else None
            ),
        )


def format_currency(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_percentage(value: float) -> str:
    return f"{value * 100:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")


def render_metrics_table(metrics: ScenarioMetrics) -> str:
    """Return a formatted table with the main KPIs."""

    rows = [
        ("Receita Total", format_currency(metrics.total_revenue)),
        ("Custos Variáveis", format_currency(metrics.total_variable_costs)),
        ("Margem de Contribuição", format_currency(metrics.contribution_margin)),
        ("Margem de Contribuição %", format_percentage(metrics.contribution_margin_ratio)),
        ("Custos Fixos", format_currency(metrics.fixed_cost_total)),
        ("EBITDA", format_currency(metrics.ebitda)),
        ("Lucro Operacional", format_currency(metrics.operating_profit)),
        ("Margem Líquida", format_percentage(metrics.net_margin)),
    ]
    if metrics.break_even_revenue is not None:
        rows.append(("Faturamento de Break-even", format_currency(metrics.break_even_revenue)))
    width = max(len(label) for label, _ in rows) + 2
    lines = ["Indicador".ljust(width) + "Valor"]
    lines.append("-" * (width + 20))
    for label, value in rows:
        lines.append(label.ljust(width) + value)
    return "\n".join(lines)


def render_broker_table(broker_summary: Dict[str, Dict[str, float]]) -> str:
    """Format broker contribution table."""

    if not broker_summary:
        return "Nenhuma venda cadastrada."
    name_width = max(len(name) for name in broker_summary) + 2
    headers = (
        "Corretor".ljust(name_width)
        + "Receita".rjust(15)
        + "Custos Var.".rjust(15)
        + "Margem".rjust(15)
        + "Margem %".rjust(12)
    )
    separator = "-" * len(headers)
    lines = [headers, separator]
    for name, stats in sorted(broker_summary.items()):
        lines.append(
            name.ljust(name_width)
            + format_currency(stats["revenue"]).rjust(15)
            + format_currency(stats["variable_costs"]).rjust(15)
            + format_currency(stats["contribution_margin"]).rjust(15)
            + format_percentage(stats["margin_ratio"]).rjust(12)
        )
    return "\n".join(lines)


def render_differences_table(difference: ScenarioMetrics) -> str:
    """Render metrics deltas."""

    rows = [
        ("Δ Receita", difference.total_revenue),
        ("Δ Custos Variáveis", difference.total_variable_costs),
        ("Δ Margem", difference.contribution_margin),
        ("Δ Margem %", difference.contribution_margin_ratio, True),
        ("Δ Custos Fixos", difference.fixed_cost_total),
        ("Δ EBITDA", difference.ebitda),
        ("Δ Lucro", difference.operating_profit),
        ("Δ Margem Líquida", difference.net_margin, True),
    ]
    if difference.break_even_revenue is not None:
        rows.append(("Δ Break-even", difference.break_even_revenue))
    width = max(len(label) for label, *_ in rows) + 2
    lines = ["Indicador".ljust(width) + "Variação"]
    lines.append("-" * (width + 20))
    for entry in rows:
        label, value, *rest = entry
        is_percentage = bool(rest and rest[0])
        formatted = format_percentage(value) if is_percentage else format_currency(value)
        lines.append(label.ljust(width) + formatted)
    return "\n".join(lines)
