import json
from pathlib import Path

import pytest

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

    assert round(metrics.total_revenue, 2) == 119500.0
    assert round(metrics.total_variable_costs, 2) == 67100.0
    assert round(metrics.contribution_margin, 2) == 52400.0
    assert round(metrics.fixed_cost_total, 2) == 63000.0
    assert round(metrics.ebitda, 2) == -8600.0
    assert round(metrics.operating_profit, 2) == -14600.0
    assert round(metrics.contribution_margin_ratio, 4) == round(52400.0 / 119500.0, 4)
    assert round(metrics.net_margin, 4) == round(-14600.0 / 119500.0, 4)
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


def test_commission_rate_inferred_from_revenue():
    payload = {
        "id": "X001",
        "broker": "Teste",
        "sale_value": 500000.0,
        "revenue": 25000.0,
        "variable_costs": {"comissao_corretor": 12000.0},
    }
    sale = Sale.from_dict(payload)
    assert sale.revenue == 25000.0
    assert sale.commission_rate == 0.05

    sale.clear_manual_revenue()
    assert sale.revenue == sale.sale_value * sale.commission_rate


def test_missing_commission_rate_without_revenue_raises():
    payload = {
        "id": "X002",
        "broker": "Teste",
        "sale_value": 200000.0,
        "variable_costs": {},
    }
    with pytest.raises(KeyError) as exc:
        Sale.from_dict(payload)
    assert "commission_rate" in str(exc.value)
