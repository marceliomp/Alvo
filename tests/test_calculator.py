import json
from pathlib import Path

from alvo_app.calculator import Sale, Scenario


def load_example() -> Scenario:
    data = json.loads(Path("data/exemplo_cenario.json").read_text(encoding="utf-8"))
    sales = [Sale.from_dict(item) for item in data["sales"]]
    return Scenario(
        name=data["name"],
        sales=sales,
        fixed_costs=data["fixed_costs"],
        other_income=data["other_income"],
        other_expenses=data["other_expenses"],
        depreciation=data["depreciation"],
        amortization=data["amortization"],
    )


def test_metrics_calculation():
    scenario = load_example()
    metrics = scenario.summary()

    assert round(metrics.total_revenue, 2) == 119750.0
    assert round(metrics.total_variable_costs, 2) == 70860.0
    assert round(metrics.contribution_margin, 2) == 48890.0
    assert round(metrics.fixed_cost_total, 2) == 44000.0
    assert round(metrics.ebitda, 2) == 6890.0
    assert round(metrics.operating_profit, 2) == 890.0
    assert round(metrics.contribution_margin_ratio, 4) == round(48890.0 / 119750.0, 4)
    assert round(metrics.net_margin, 4) == round(890.0 / 119750.0, 4)
    assert metrics.break_even_revenue is not None


def test_difference():
    scenario = load_example()
    metrics = scenario.summary()
    adjusted = scenario.clone()
    adjusted.apply_global_scaling(revenue_multiplier=1.1)
    updated = adjusted.summary()

    diff = updated.difference(metrics)
    assert diff.total_revenue == updated.total_revenue - metrics.total_revenue
    assert diff.ebitda == updated.ebitda - metrics.ebitda


def test_commission_is_driven_by_property_value():
    scenario = load_example()
    sale = scenario.sales[0]

    assert sale.revenue == sale.property_value * sale.commission_rate

    sale.revenue = 60000.0
    assert sale.revenue == 60000.0
