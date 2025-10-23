const state = {
  base: null,
  current: null,
};

const saleTemplate = document.getElementById("sale-template");
const costTemplate = document.getElementById("cost-row-template");

const scenarioNameInput = document.getElementById("scenario-name");
const otherIncomeInput = document.getElementById("other-income");
const otherExpensesInput = document.getElementById("other-expenses");
const depreciationInput = document.getElementById("depreciation");
const amortizationInput = document.getElementById("amortization");

const scaleRevenueInput = document.getElementById("scale-revenue");
const scaleVariableCostsInput = document.getElementById("scale-variable-costs");
const scaleFixedCostsInput = document.getElementById("scale-fixed-costs");

function randomId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `sale-${Math.random().toString(36).slice(2, 10)}`;
}

function deepClone(value) {
  return JSON.parse(JSON.stringify(value));
}

function normalizeScenario(raw) {
  const normalized = {
    name: raw.name || "Cenário",
    other_income: Number(raw.other_income || 0),
    other_expenses: Number(raw.other_expenses || 0),
    depreciation: Number(raw.depreciation || 0),
    amortization: Number(raw.amortization || 0),
    fixed_costs: Object.entries(raw.fixed_costs || {}).map(([name, amount]) => ({
      name,
      value: Number(amount || 0),
    })),
    sales: (raw.sales || []).map((sale) => ({
      id: sale.id || randomId(),
      broker: sale.broker || "",
      sale_value: Number(sale.sale_value || 0),
      commission_rate: Number(sale.commission_rate || 0),
      manual_revenue:
        sale.revenue !== undefined && sale.revenue !== null
          ? Number(sale.revenue)
          : null,
      variable_costs: Object.entries(sale.variable_costs || {}).map(
        ([name, amount]) => ({
          name,
          value: Number(amount || 0),
        }),
      ),
      notes: sale.notes || "",
    })),
  };

  normalized.sales.sort((a, b) => a.id.localeCompare(b.id));
  return normalized;
}

function computeSaleRevenue(sale) {
  if (sale.manual_revenue !== null && sale.manual_revenue !== undefined) {
    return sale.manual_revenue;
  }
  return sale.sale_value * sale.commission_rate;
}

function computeSaleVariableCosts(sale) {
  return sale.variable_costs.reduce((total, item) => total + item.value, 0);
}

function computeScenarioMetrics(scenario) {
  const totalRevenue = scenario.sales.reduce(
    (total, sale) => total + computeSaleRevenue(sale),
    0,
  );
  const totalVariableCosts = scenario.sales.reduce(
    (total, sale) => total + computeSaleVariableCosts(sale),
    0,
  );
  const contributionMargin = totalRevenue - totalVariableCosts;
  const contributionMarginRatio = totalRevenue
    ? contributionMargin / totalRevenue
    : 0;
  const fixedCostTotal = scenario.fixed_costs.reduce(
    (total, cost) => total + cost.value,
    0,
  );
  const ebitda =
    contributionMargin -
    fixedCostTotal +
    scenario.other_income -
    scenario.other_expenses;
  const operatingProfit =
    ebitda - scenario.depreciation - scenario.amortization;
  const netMargin = totalRevenue ? operatingProfit / totalRevenue : 0;
  const breakEvenRevenue =
    contributionMarginRatio > 0
      ? fixedCostTotal / contributionMarginRatio
      : null;

  return {
    totalRevenue,
    totalVariableCosts,
    contributionMargin,
    contributionMarginRatio,
    fixedCostTotal,
    ebitda,
    operatingProfit,
    netMargin,
    breakEvenRevenue,
  };
}

function computeBrokerSummary(scenario) {
  const summary = new Map();
  for (const sale of scenario.sales) {
    const revenue = computeSaleRevenue(sale);
    const variable = computeSaleVariableCosts(sale);
    const margin = revenue - variable;
    const key = sale.broker || "Sem corretor";
    if (!summary.has(key)) {
      summary.set(key, {
        revenue: 0,
        variable: 0,
        margin: 0,
      });
    }
    const entry = summary.get(key);
    entry.revenue += revenue;
    entry.variable += variable;
    entry.margin += margin;
  }

  return Array.from(summary.entries())
    .map(([broker, values]) => ({
      broker,
      revenue: values.revenue,
      variable: values.variable,
      margin: values.margin,
      marginRatio: values.revenue ? values.margin / values.revenue : 0,
    }))
    .sort((a, b) => a.broker.localeCompare(b.broker));
}

function formatCurrency(value) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 2,
  }).format(value || 0);
}

function formatPercent(value) {
  return new Intl.NumberFormat("pt-BR", {
    style: "percent",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value || 0);
}

function renderSummary() {
  const metrics = computeScenarioMetrics(state.current);
  const rows = [
    ["Receita Total", formatCurrency(metrics.totalRevenue)],
    ["Custos Variáveis", formatCurrency(metrics.totalVariableCosts)],
    ["Margem de Contribuição", formatCurrency(metrics.contributionMargin)],
    ["Margem de Contribuição %", formatPercent(metrics.contributionMarginRatio)],
    ["Custos Fixos", formatCurrency(metrics.fixedCostTotal)],
    ["EBITDA", formatCurrency(metrics.ebitda)],
    ["Lucro Operacional", formatCurrency(metrics.operatingProfit)],
    ["Margem Líquida", formatPercent(metrics.netMargin)],
  ];

  if (metrics.breakEvenRevenue !== null) {
    rows.push(["Faturamento de Break-even", formatCurrency(metrics.breakEvenRevenue)]);
  }

  const tbody = document.getElementById("summary-body");
  tbody.innerHTML = rows
    .map(
      ([label, value]) =>
        `<tr><td>${label}</td><td class="kpi-value">${value}</td></tr>`,
    )
    .join("");
}

function renderFixedCosts() {
  const tbody = document.getElementById("fixed-costs-body");
  tbody.innerHTML = "";

  if (state.current.fixed_costs.length === 0) {
    const emptyRow = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 3;
    cell.textContent = "Nenhum custo cadastrado";
    cell.classList.add("muted");
    emptyRow.appendChild(cell);
    tbody.appendChild(emptyRow);
    return;
  }

  state.current.fixed_costs.forEach((cost, index) => {
    const row = document.createElement("tr");

    const nameCell = document.createElement("td");
    const nameInput = document.createElement("input");
    nameInput.type = "text";
    nameInput.value = cost.name;
      nameInput.addEventListener("change", (event) => {
        state.current.fixed_costs[index].name = event.target.value;
        renderBrokerTable();
      });
    nameCell.appendChild(nameInput);

    const valueCell = document.createElement("td");
    const valueInput = document.createElement("input");
    valueInput.type = "number";
    valueInput.step = "0.01";
    valueInput.value = cost.value;
    valueInput.addEventListener("change", (event) => {
      state.current.fixed_costs[index].value = Number(event.target.value || 0);
      renderSummary();
    });
    valueCell.appendChild(valueInput);

    const actionsCell = document.createElement("td");
    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.className = "remove-cost";
    removeButton.textContent = "Remover";
    removeButton.addEventListener("click", () => {
      state.current.fixed_costs.splice(index, 1);
      renderAll();
    });
    actionsCell.appendChild(removeButton);

    row.appendChild(nameCell);
    row.appendChild(valueCell);
    row.appendChild(actionsCell);
    tbody.appendChild(row);
  });
}

function renderBrokerTable() {
  const wrapper = document.getElementById("broker-table-wrapper");
  const summary = computeBrokerSummary(state.current);

  if (summary.length === 0) {
    wrapper.innerHTML = "<p class=\"muted\">Nenhuma venda cadastrada.</p>";
    return;
  }

  const rows = summary
    .map(
      (item) => `
        <tr>
          <td>${item.broker}</td>
          <td>${formatCurrency(item.revenue)}</td>
          <td>${formatCurrency(item.variable)}</td>
          <td>${formatCurrency(item.margin)}</td>
          <td>${formatPercent(item.marginRatio)}</td>
        </tr>
      `,
    )
    .join("");

  wrapper.innerHTML = `
    <table class="kpi-table">
      <thead>
        <tr>
          <th>Corretor</th>
          <th>Receita</th>
          <th>Custos Variáveis</th>
          <th>Margem</th>
          <th>Margem %</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderSales() {
  const container = document.getElementById("sales-container");
  container.innerHTML = "";

  state.current.sales.forEach((sale, index) => {
    const node = saleTemplate.content.firstElementChild.cloneNode(true);
    node.dataset.index = String(index);

    node.querySelector("h3").textContent = `${sale.id} · ${sale.broker || "Sem corretor"}`;

    const saleIdInput = node.querySelector('input[data-field="sale_id"]');
    saleIdInput.value = sale.id;
    saleIdInput.addEventListener("change", (event) => {
      const newId = event.target.value.trim();
      if (!newId) {
        event.target.value = sale.id;
        return;
      }
      if (
        state.current.sales.some(
          (existing, existingIndex) => existing.id === newId && existingIndex !== index,
        )
      ) {
        alert("Já existe uma venda com esse código. Utilize outro identificador.");
        event.target.value = sale.id;
        return;
      }
      sale.id = newId;
      node.querySelector("h3").textContent = `${sale.id} · ${sale.broker || "Sem corretor"}`;
    });

    const brokerInput = node.querySelector('input[data-field="broker"]');
    brokerInput.value = sale.broker;
    brokerInput.addEventListener("input", (event) => {
      sale.broker = event.target.value;
      node.querySelector("h3").textContent = `${sale.id} · ${sale.broker || "Sem corretor"}`;
      renderBrokerTable();
    });

    const saleValueInput = node.querySelector('input[data-field="sale_value"]');
    saleValueInput.value = sale.sale_value;
    saleValueInput.addEventListener("change", (event) => {
      sale.sale_value = Number(event.target.value || 0);
      if (sale.manual_revenue !== null && sale.manual_revenue !== undefined) {
        // mantém receita manual; nenhuma ação
      }
      renderAll();
    });

    const commissionInput = node.querySelector('input[data-field="commission_rate"]');
    commissionInput.value = sale.commission_rate * 100;
    commissionInput.addEventListener("change", (event) => {
      sale.commission_rate = Number(event.target.value || 0) / 100;
      if (sale.manual_revenue !== null && sale.manual_revenue !== undefined) {
        // alterar percentual limpa receita manual
        sale.manual_revenue = null;
        manualRevenueInput.value = "";
      }
      renderAll();
    });

    const manualRevenueInput = node.querySelector('input[data-field="manual_revenue"]');
    manualRevenueInput.value =
      sale.manual_revenue !== null && sale.manual_revenue !== undefined
        ? sale.manual_revenue
        : "";
    manualRevenueInput.addEventListener("change", (event) => {
      const value = event.target.value;
      sale.manual_revenue = value === "" ? null : Number(value || 0);
      renderAll();
    });

    const clearManualButton = node.querySelector(".clear-manual-revenue");
    clearManualButton.addEventListener("click", () => {
      sale.manual_revenue = null;
      manualRevenueInput.value = "";
      renderAll();
    });

    const removeSaleButton = node.querySelector(".remove-sale");
    removeSaleButton.addEventListener("click", () => {
      state.current.sales.splice(index, 1);
      renderAll();
    });

    const addVariableCostButton = node.querySelector(".add-variable-cost");
    addVariableCostButton.addEventListener("click", () => {
      sale.variable_costs.push({ name: "Novo custo", value: 0 });
      renderSales();
      renderSummary();
      renderBrokerTable();
    });

    const variableTableBody = node.querySelector("tbody");
    variableTableBody.innerHTML = "";
    sale.variable_costs.forEach((cost, costIndex) => {
      const costRow = costTemplate.content.firstElementChild.cloneNode(true);
      const nameInput = costRow.querySelector('input[data-field="cost-name"]');
      const valueInput = costRow.querySelector('input[data-field="cost-value"]');

      nameInput.value = cost.name;
      nameInput.addEventListener("change", (event) => {
        sale.variable_costs[costIndex].name = event.target.value;
      });

      valueInput.value = cost.value;
      valueInput.addEventListener("change", (event) => {
        sale.variable_costs[costIndex].value = Number(event.target.value || 0);
        renderSummary();
        renderBrokerTable();
      });

      const removeCostButton = costRow.querySelector(".remove-cost");
      removeCostButton.addEventListener("click", () => {
        sale.variable_costs.splice(costIndex, 1);
        renderSales();
        renderSummary();
        renderBrokerTable();
      });

      variableTableBody.appendChild(costRow);
    });

    const totalRevenue = computeSaleRevenue(sale);
    const totalVariable = computeSaleVariableCosts(sale);
    const contribution = totalRevenue - totalVariable;
    const marginRatio = totalRevenue ? contribution / totalRevenue : 0;
    const footer = node.querySelector(".sale-metrics");
    footer.innerHTML = `
      <strong>Receita:</strong> ${formatCurrency(totalRevenue)} ·
      <strong>Custos Var.:</strong> ${formatCurrency(totalVariable)} ·
      <strong>Margem:</strong> ${formatCurrency(contribution)} (${formatPercent(
        marginRatio,
      )})
    `;

    container.appendChild(node);
  });
}

function renderScenarioInputs() {
  scenarioNameInput.value = state.current.name;
  otherIncomeInput.value = state.current.other_income;
  otherExpensesInput.value = state.current.other_expenses;
  depreciationInput.value = state.current.depreciation;
  amortizationInput.value = state.current.amortization;
}

function renderAll() {
  renderScenarioInputs();
  renderSummary();
  renderFixedCosts();
  renderBrokerTable();
  renderSales();
}

function applyScaling() {
  const revenueMultiplier = parseFloat(scaleRevenueInput.value);
  const variableMultiplier = parseFloat(scaleVariableCostsInput.value);
  const fixedMultiplier = parseFloat(scaleFixedCostsInput.value);

  for (const sale of state.current.sales) {
    if (!Number.isNaN(revenueMultiplier)) {
      if (sale.manual_revenue !== null && sale.manual_revenue !== undefined) {
        sale.manual_revenue *= revenueMultiplier;
      } else {
        sale.sale_value *= revenueMultiplier;
      }
    }
    if (!Number.isNaN(variableMultiplier)) {
      sale.variable_costs.forEach((cost) => {
        cost.value *= variableMultiplier;
      });
    }
  }

  if (!Number.isNaN(fixedMultiplier)) {
    state.current.fixed_costs.forEach((cost) => {
      cost.value *= fixedMultiplier;
    });
  }

  scaleRevenueInput.value = "";
  scaleVariableCostsInput.value = "";
  scaleFixedCostsInput.value = "";
  renderAll();
}

function resetScenario() {
  state.current = deepClone(state.base);
  renderAll();
}

function uniqueName(baseName, used, fallbackPrefix) {
  const base = baseName && baseName.trim() ? baseName.trim() : fallbackPrefix;
  let candidate = base;
  let counter = 2;
  while (used.has(candidate)) {
    candidate = `${base} (${counter})`;
    counter += 1;
  }
  used.add(candidate);
  return candidate;
}

function scenarioToJson(scenario) {
  const fixedCostsUsed = new Set();
  const payload = {
    name: scenario.name,
    sales: scenario.sales.map((sale) => {
      const usedCosts = new Set();
      const variableCosts = Object.fromEntries(
        sale.variable_costs.map((cost, index) => [
          uniqueName(cost.name, usedCosts, `Custo ${index + 1}`),
          cost.value,
        ]),
      );
      const result = {
        id: sale.id,
        broker: sale.broker,
        sale_value: sale.sale_value,
        commission_rate: sale.commission_rate,
        variable_costs: variableCosts,
      };
      if (sale.notes) {
        result.notes = sale.notes;
      }
      if (sale.manual_revenue !== null && sale.manual_revenue !== undefined) {
        result.revenue = sale.manual_revenue;
      }
      return result;
    }),
    fixed_costs: Object.fromEntries(
      scenario.fixed_costs.map((cost, index) => [
        uniqueName(cost.name, fixedCostsUsed, `Custo Fixo ${index + 1}`),
        cost.value,
      ]),
    ),
    other_income: scenario.other_income,
    other_expenses: scenario.other_expenses,
    depreciation: scenario.depreciation,
    amortization: scenario.amortization,
  };

  return payload;
}

function downloadScenario() {
  const payload = scenarioToJson(state.current);
  const blob = new Blob([JSON.stringify(payload, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  const safeName = (state.current.name || "cenario").replace(/\s+/g, "-");
  link.download = `${safeName.toLowerCase()}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function generateSaleId() {
  let counter = state.current.sales.length + 1;
  while (true) {
    const candidate = `V${String(counter).padStart(3, "0")}`;
    if (!state.current.sales.some((sale) => sale.id === candidate)) {
      return candidate;
    }
    counter += 1;
  }
}

function addSale() {
  state.current.sales.push({
    id: generateSaleId(),
    broker: "",
    sale_value: 0,
    commission_rate: 0.05,
    manual_revenue: null,
    variable_costs: [],
    notes: "",
  });
  renderAll();
}

async function importScenario(file) {
  const text = await file.text();
  const json = JSON.parse(text);
  state.base = normalizeScenario(json);
  state.current = deepClone(state.base);
  renderAll();
}

function wireStaticEvents() {
  document
    .getElementById("apply-scaling")
    .addEventListener("click", applyScaling);
  document
    .getElementById("reset-scenario")
    .addEventListener("click", resetScenario);
  document
    .getElementById("download-scenario")
    .addEventListener("click", downloadScenario);
  document.getElementById("add-fixed-cost").addEventListener("click", () => {
    state.current.fixed_costs.push({ name: "Novo custo", value: 0 });
    renderFixedCosts();
    renderSummary();
  });
  document.getElementById("add-sale").addEventListener("click", addSale);
  scenarioNameInput.addEventListener("input", (event) => {
    state.current.name = event.target.value;
  });
  otherIncomeInput.addEventListener("change", (event) => {
    state.current.other_income = Number(event.target.value || 0);
    renderAll();
  });
  otherExpensesInput.addEventListener("change", (event) => {
    state.current.other_expenses = Number(event.target.value || 0);
    renderAll();
  });
  depreciationInput.addEventListener("change", (event) => {
    state.current.depreciation = Number(event.target.value || 0);
    renderAll();
  });
  amortizationInput.addEventListener("change", (event) => {
    state.current.amortization = Number(event.target.value || 0);
    renderAll();
  });

  document.getElementById("scenario-upload").addEventListener("change", (event) => {
    const [file] = event.target.files;
    if (file) {
      importScenario(file).catch((error) => {
        console.error("Erro ao carregar cenário", error);
        alert("Não foi possível carregar o arquivo. Verifique o formato JSON.");
      });
      event.target.value = "";
    }
  });
}

async function bootstrap() {
  wireStaticEvents();
  try {
    const candidates = ["exemplo_cenario.json", "../data/exemplo_cenario.json"];
    let json = null;
    for (const url of candidates) {
      try {
        const response = await fetch(url);
        if (response.ok) {
          json = await response.json();
          break;
        }
      } catch (error) {
        console.warn(`Falha ao carregar ${url}`, error);
      }
    }
    if (!json) {
      throw new Error("Não foi possível carregar nenhum cenário padrão");
    }
    state.base = normalizeScenario(json);
  } catch (error) {
    console.warn("Não foi possível carregar o cenário padrão. Usando fallback.", error);
    state.base = {
      name: "Cenário",
      sales: [],
      fixed_costs: [],
      other_income: 0,
      other_expenses: 0,
      depreciation: 0,
      amortization: 0,
    };
  }
  state.current = deepClone(state.base);
  renderAll();
}

bootstrap();
