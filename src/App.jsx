import React, { useMemo, useRef, useState } from 'react';

const defaultSales = [
  {
    id: 1,
    name: 'Apartamento Bela Vista',
    broker: 'Mariana',
    revenue: 850000,
    variableCost: 120000,
    commissionRate: 2.5
  },
  {
    id: 2,
    name: 'Cobertura Horizonte',
    broker: 'João',
    revenue: 1250000,
    variableCost: 180000,
    commissionRate: 3.2
  },
  {
    id: 3,
    name: 'Casa Jardim Europa',
    broker: 'Mariana',
    revenue: 980000,
    variableCost: 150000,
    commissionRate: 2.8
  }
];

const initialScenario = {
  revenueDelta: 0,
  variableCostDelta: 0,
  commissionDelta: 0,
  fixedCostDelta: 0
};

const formatCurrency = (value) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(value || 0);

const clampNumber = (value, min, max) => Math.min(Math.max(Number(value) || 0, min), max);

const ContributionCard = ({ title, primary, secondary }) => (
  <div
    style={{
      background: 'rgba(15, 23, 42, 0.85)',
      borderRadius: '16px',
      padding: '24px',
      color: '#f8fafc',
      boxShadow: '0 18px 45px rgba(15, 118, 110, 0.35)',
      display: 'flex',
      flexDirection: 'column',
      gap: '8px'
    }}
  >
    <span style={{ fontSize: '0.9rem', opacity: 0.8 }}>{title}</span>
    <strong style={{ fontSize: '1.8rem', fontWeight: 700 }}>{primary}</strong>
    {secondary && <span style={{ fontSize: '0.95rem', opacity: 0.85 }}>{secondary}</span>}
  </div>
);

const ScenarioSlider = ({ label, value, min = -50, max = 50, step = 1, onChange }) => (
  <label
    style={{
      display: 'grid',
      gap: '4px',
      color: '#0f172a',
      background: 'rgba(248, 250, 252, 0.95)',
      padding: '16px',
      borderRadius: '12px',
      boxShadow: '0 10px 35px rgba(15, 23, 42, 0.12)'
    }}
  >
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <span style={{ fontWeight: 600 }}>{label}</span>
      <span
        style={{
          fontVariantNumeric: 'tabular-nums',
          background: 'rgba(15, 118, 110, 0.12)',
          color: '#0f766e',
          padding: '4px 8px',
          borderRadius: '999px',
          fontWeight: 600
        }}
      >
        {value.toFixed(1)}%
      </span>
    </div>
    <input
      type="range"
      min={min}
      max={max}
      step={step}
      value={value}
      onChange={(event) => onChange(Number(event.target.value))}
      style={{ accentColor: '#0f766e' }}
    />
  </label>
);

function App() {
  const [sales, setSales] = useState(defaultSales);
  const [fixedCosts, setFixedCosts] = useState(245000);
  const [scenario, setScenario] = useState(initialScenario);
  const nextId = useRef(defaultSales.length + 1);
  const [newSale, setNewSale] = useState({
    name: '',
    broker: '',
    revenue: '',
    variableCost: '',
    commissionRate: ''
  });

  const baseSales = useMemo(
    () =>
      sales.map((sale) => {
        const revenue = Number(sale.revenue) || 0;
        const variableCost = Number(sale.variableCost) || 0;
        const commissionRate = Number(sale.commissionRate) || 0;
        const commissionValue = (revenue * commissionRate) / 100;
        const contribution = revenue - variableCost - commissionValue;
        const marginPercentage = revenue === 0 ? 0 : (contribution / revenue) * 100;

        return {
          ...sale,
          revenue,
          variableCost,
          commissionRate,
          commissionValue,
          contribution,
          marginPercentage
        };
      }),
    [sales]
  );

  const scenarioSales = useMemo(() => {
    const revenueFactor = 1 + scenario.revenueDelta / 100;
    const variableCostFactor = 1 + scenario.variableCostDelta / 100;
    const commissionFactor = 1 + scenario.commissionDelta / 100;

    return baseSales.map((sale) => {
      const revenue = sale.revenue * revenueFactor;
      const variableCost = sale.variableCost * variableCostFactor;
      const commissionRate = sale.commissionRate * commissionFactor;
      const commissionValue = (revenue * commissionRate) / 100;
      const contribution = revenue - variableCost - commissionValue;
      const marginPercentage = revenue === 0 ? 0 : (contribution / revenue) * 100;

      return {
        ...sale,
        revenue,
        variableCost,
        commissionRate,
        commissionValue,
        contribution,
        marginPercentage
      };
    });
  }, [baseSales, scenario]);

  const totals = useMemo(() => {
    const sum = baseSales.reduce(
      (acc, sale) => {
        acc.revenue += sale.revenue;
        acc.variableCost += sale.variableCost;
        acc.commissionValue += sale.commissionValue;
        acc.contribution += sale.contribution;
        return acc;
      },
      { revenue: 0, variableCost: 0, commissionValue: 0, contribution: 0 }
    );

    const ebitda = sum.contribution - fixedCosts;
    const marginPercentage = sum.revenue === 0 ? 0 : (sum.contribution / sum.revenue) * 100;

    return { ...sum, fixedCosts, ebitda, marginPercentage };
  }, [baseSales, fixedCosts]);

  const scenarioTotals = useMemo(() => {
    const sum = scenarioSales.reduce(
      (acc, sale) => {
        acc.revenue += sale.revenue;
        acc.variableCost += sale.variableCost;
        acc.commissionValue += sale.commissionValue;
        acc.contribution += sale.contribution;
        return acc;
      },
      { revenue: 0, variableCost: 0, commissionValue: 0, contribution: 0 }
    );

    const adjustedFixedCosts = fixedCosts * (1 + scenario.fixedCostDelta / 100);
    const ebitda = sum.contribution - adjustedFixedCosts;
    const marginPercentage = sum.revenue === 0 ? 0 : (sum.contribution / sum.revenue) * 100;

    return { ...sum, fixedCosts: adjustedFixedCosts, ebitda, marginPercentage };
  }, [scenarioSales, fixedCosts, scenario.fixedCostDelta]);

  const brokerSummary = useMemo(() => {
    const summary = new Map();

    baseSales.forEach((sale) => {
      if (!summary.has(sale.broker)) {
        summary.set(sale.broker, {
          broker: sale.broker,
          revenue: 0,
          contribution: 0,
          commissionValue: 0
        });
      }

      const brokerData = summary.get(sale.broker);
      brokerData.revenue += sale.revenue;
      brokerData.contribution += sale.contribution;
      brokerData.commissionValue += sale.commissionValue;
    });

    return Array.from(summary.values()).map((broker) => ({
      ...broker,
      marginPercentage: broker.revenue === 0 ? 0 : (broker.contribution / broker.revenue) * 100
    }));
  }, [baseSales]);

  const handleSaleChange = (id, field, value) => {
    setSales((current) =>
      current.map((sale) => (sale.id === id ? { ...sale, [field]: field === 'broker' || field === 'name' ? value : value } : sale))
    );
  };

  const handleRemoveSale = (id) => {
    setSales((current) => current.filter((sale) => sale.id !== id));
  };

  const handleAddSale = (event) => {
    event.preventDefault();
    if (!newSale.name || !newSale.broker) {
      return;
    }

    const sale = {
      id: nextId.current++,
      name: newSale.name,
      broker: newSale.broker,
      revenue: Number(newSale.revenue) || 0,
      variableCost: Number(newSale.variableCost) || 0,
      commissionRate: Number(newSale.commissionRate) || 0
    };

    setSales((current) => [...current, sale]);
    setNewSale({ name: '', broker: '', revenue: '', variableCost: '', commissionRate: '' });
  };

  const handleFixedCostsChange = (value) => {
    setFixedCosts(clampNumber(value, 0, 100000000));
  };

  const resetScenario = () => setScenario(initialScenario);

  return (
    <div
      style={{
        padding: '48px 24px 72px',
        maxWidth: '1280px',
        margin: '0 auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '32px'
      }}
    >
      <header style={{ color: '#e2e8f0' }}>
        <h1 style={{ margin: 0, fontSize: '2.5rem', fontWeight: 700 }}>Alvo Forecast</h1>
        <p style={{ maxWidth: '680px', lineHeight: 1.6, fontSize: '1rem', opacity: 0.9 }}>
          Consolide vendas, acompanhe a margem de contribuição e projete cenários de EBITDA em segundos. Ajuste custos variáveis,
          comissões, receita e despesas fixas para visualizar o impacto direto no resultado do negócio.
        </p>
      </header>

      <section
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '20px'
        }}
      >
        <ContributionCard
          title="Margem de contribuição"
          primary={formatCurrency(totals.contribution)}
          secondary={`${totals.marginPercentage.toFixed(1)}% da receita`}
        />
        <ContributionCard
          title="EBITDA"
          primary={formatCurrency(totals.ebitda)}
          secondary={`Custos fixos: ${formatCurrency(totals.fixedCosts)}`}
        />
        <ContributionCard
          title="Receita bruta"
          primary={formatCurrency(totals.revenue)}
          secondary={`Custos variáveis: ${formatCurrency(totals.variableCost)}`}
        />
      </section>

      <section
        style={{
          display: 'grid',
          gap: '20px',
          background: 'rgba(248, 250, 252, 0.98)',
          borderRadius: '20px',
          padding: '28px 28px 36px',
          boxShadow: '0 32px 45px rgba(15, 23, 42, 0.25)'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <h2 style={{ margin: 0, color: '#0f172a' }}>Vendas cadastradas</h2>
          <label style={{ display: 'flex', alignItems: 'center', gap: '12px', color: '#0f172a' }}>
            <span style={{ fontWeight: 600 }}>Custos fixos mensais</span>
            <input
              type="number"
              value={fixedCosts}
              min={0}
              step={1000}
              onChange={(event) => handleFixedCostsChange(event.target.value)}
              style={{
                borderRadius: '8px',
                border: '1px solid #cbd5f5',
                padding: '8px 12px',
                width: '180px',
                fontSize: '0.95rem'
              }}
            />
          </label>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '760px' }}>
            <thead>
              <tr style={{ textAlign: 'left', background: '#0f172a', color: '#f8fafc' }}>
                <th style={{ padding: '12px 16px', borderTopLeftRadius: '12px' }}>Negócio</th>
                <th style={{ padding: '12px 16px' }}>Corretor</th>
                <th style={{ padding: '12px 16px' }}>Receita</th>
                <th style={{ padding: '12px 16px' }}>Custos variáveis</th>
                <th style={{ padding: '12px 16px' }}>Comissão (%)</th>
                <th style={{ padding: '12px 16px' }}>Margem contrib.</th>
                <th style={{ padding: '12px 16px' }}>Ações</th>
              </tr>
            </thead>
            <tbody>
              {baseSales.map((sale) => (
                <tr key={sale.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                  <td style={{ padding: '12px 16px' }}>
                    <input
                      value={sale.name}
                      onChange={(event) => handleSaleChange(sale.id, 'name', event.target.value)}
                      style={inputStyle}
                    />
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <input
                      value={sale.broker}
                      onChange={(event) => handleSaleChange(sale.id, 'broker', event.target.value)}
                      style={inputStyle}
                    />
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <input
                      type="number"
                      min={0}
                      step={1000}
                      value={sale.revenue}
                      onChange={(event) => handleSaleChange(sale.id, 'revenue', Number(event.target.value))}
                      style={inputStyle}
                    />
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <input
                      type="number"
                      min={0}
                      step={1000}
                      value={sale.variableCost}
                      onChange={(event) => handleSaleChange(sale.id, 'variableCost', Number(event.target.value))}
                      style={inputStyle}
                    />
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <input
                      type="number"
                      min={0}
                      step={0.1}
                      value={sale.commissionRate}
                      onChange={(event) => handleSaleChange(sale.id, 'commissionRate', Number(event.target.value))}
                      style={inputStyle}
                    />
                  </td>
                  <td style={{ padding: '12px 16px', fontWeight: 600, color: '#0f766e' }}>
                    {formatCurrency(sale.contribution)} ({sale.marginPercentage.toFixed(1)}%)
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <button
                      type="button"
                      onClick={() => handleRemoveSale(sale.id)}
                      style={removeButtonStyle}
                    >
                      Remover
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <form
          onSubmit={handleAddSale}
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '16px',
            background: 'rgba(241, 245, 249, 0.9)',
            borderRadius: '12px',
            padding: '16px'
          }}
        >
          <input
            required
            placeholder="Nome da venda"
            value={newSale.name}
            onChange={(event) => setNewSale((state) => ({ ...state, name: event.target.value }))}
            style={inputStyle}
          />
          <input
            required
            placeholder="Corretor"
            value={newSale.broker}
            onChange={(event) => setNewSale((state) => ({ ...state, broker: event.target.value }))}
            style={inputStyle}
          />
          <input
            type="number"
            min={0}
            step={1000}
            placeholder="Receita"
            value={newSale.revenue}
            onChange={(event) => setNewSale((state) => ({ ...state, revenue: event.target.value }))}
            style={inputStyle}
          />
          <input
            type="number"
            min={0}
            step={1000}
            placeholder="Custos variáveis"
            value={newSale.variableCost}
            onChange={(event) => setNewSale((state) => ({ ...state, variableCost: event.target.value }))}
            style={inputStyle}
          />
          <input
            type="number"
            min={0}
            step={0.1}
            placeholder="Comissão (%)"
            value={newSale.commissionRate}
            onChange={(event) => setNewSale((state) => ({ ...state, commissionRate: event.target.value }))}
            style={inputStyle}
          />
          <button
            type="submit"
            style={{
              background: '#0f766e',
              border: 'none',
              color: '#f8fafc',
              fontWeight: 600,
              borderRadius: '10px',
              padding: '12px 16px',
              cursor: 'pointer',
              transition: 'filter 0.2s ease'
            }}
            onMouseOver={(event) => (event.currentTarget.style.filter = 'brightness(1.1)')}
            onMouseOut={(event) => (event.currentTarget.style.filter = 'none')}
          >
            Adicionar venda
          </button>
        </form>
      </section>

      <section
        style={{
          display: 'grid',
          gap: '20px',
          gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))'
        }}
      >
        <div
          style={{
            background: 'rgba(248, 250, 252, 0.96)',
            borderRadius: '20px',
            padding: '24px',
            boxShadow: '0 24px 45px rgba(15, 23, 42, 0.25)',
            display: 'grid',
            gap: '16px'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={{ margin: 0, color: '#0f172a' }}>Cenários</h2>
            <button
              type="button"
              onClick={resetScenario}
              style={{
                border: '1px solid rgba(15, 118, 110, 0.35)',
                background: 'transparent',
                color: '#0f766e',
                borderRadius: '8px',
                padding: '6px 12px',
                cursor: 'pointer'
              }}
            >
              Resetar
            </button>
          </div>
          <ScenarioSlider
            label="Receita"
            value={scenario.revenueDelta}
            onChange={(value) => setScenario((state) => ({ ...state, revenueDelta: value }))}
          />
          <ScenarioSlider
            label="Custos variáveis"
            value={scenario.variableCostDelta}
            onChange={(value) => setScenario((state) => ({ ...state, variableCostDelta: value }))}
          />
          <ScenarioSlider
            label="Comissões"
            value={scenario.commissionDelta}
            onChange={(value) => setScenario((state) => ({ ...state, commissionDelta: value }))}
          />
          <ScenarioSlider
            label="Custos fixos"
            value={scenario.fixedCostDelta}
            onChange={(value) => setScenario((state) => ({ ...state, fixedCostDelta: value }))}
          />
        </div>

        <div
          style={{
            background: 'rgba(248, 250, 252, 0.96)',
            borderRadius: '20px',
            padding: '24px',
            boxShadow: '0 24px 45px rgba(15, 23, 42, 0.25)',
            display: 'grid',
            gap: '12px'
          }}
        >
          <h2 style={{ margin: 0, color: '#0f172a' }}>Resultado do cenário</h2>
          <p style={{ margin: 0, color: '#475569' }}>
            Ajustes aplicados sobre os valores atuais. Combine variações de receita, custos e comissões para testar estratégias.
          </p>
          <div style={{ display: 'grid', gap: '12px', marginTop: '12px' }}>
            <div style={scenarioRowStyle}>
              <span>Receita</span>
              <strong>{formatCurrency(scenarioTotals.revenue)}</strong>
            </div>
            <div style={scenarioRowStyle}>
              <span>Custos variáveis</span>
              <strong>{formatCurrency(scenarioTotals.variableCost)}</strong>
            </div>
            <div style={scenarioRowStyle}>
              <span>Comissões</span>
              <strong>{formatCurrency(scenarioTotals.commissionValue)}</strong>
            </div>
            <div style={scenarioRowStyle}>
              <span>Margem de contribuição</span>
              <strong>
                {formatCurrency(scenarioTotals.contribution)} ({scenarioTotals.marginPercentage.toFixed(1)}%)
              </strong>
            </div>
            <div style={scenarioRowStyle}>
              <span>Custos fixos</span>
              <strong>{formatCurrency(scenarioTotals.fixedCosts)}</strong>
            </div>
            <div style={{ ...scenarioRowStyle, borderTop: '1px solid rgba(148, 163, 184, 0.4)', paddingTop: '16px' }}>
              <span>EBITDA projetado</span>
              <strong style={{ color: scenarioTotals.ebitda >= 0 ? '#0f766e' : '#dc2626' }}>
                {formatCurrency(scenarioTotals.ebitda)}
              </strong>
            </div>
          </div>
        </div>

        <div
          style={{
            background: 'rgba(248, 250, 252, 0.96)',
            borderRadius: '20px',
            padding: '24px',
            boxShadow: '0 24px 45px rgba(15, 23, 42, 0.25)',
            display: 'grid',
            gap: '12px'
          }}
        >
          <h2 style={{ margin: 0, color: '#0f172a' }}>Desempenho por corretor</h2>
          <div style={{ display: 'grid', gap: '12px' }}>
            {brokerSummary.map((broker) => (
              <div key={broker.broker} style={brokerRowStyle}>
                <div>
                  <strong style={{ color: '#0f172a' }}>{broker.broker}</strong>
                  <p style={{ margin: '4px 0 0', color: '#475569', fontSize: '0.9rem' }}>
                    Receita: {formatCurrency(broker.revenue)} • Comissão: {formatCurrency(broker.commissionValue)}
                  </p>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span style={{ display: 'block', fontWeight: 600, color: '#0f766e' }}>
                    {formatCurrency(broker.contribution)}
                  </span>
                  <small style={{ color: '#475569' }}>{broker.marginPercentage.toFixed(1)}% margem</small>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

const inputStyle = {
  width: '100%',
  borderRadius: '8px',
  border: '1px solid rgba(148, 163, 184, 0.6)',
  padding: '10px 12px',
  fontSize: '0.95rem',
  background: 'rgba(255, 255, 255, 0.92)'
};

const removeButtonStyle = {
  background: 'rgba(220, 38, 38, 0.12)',
  color: '#dc2626',
  border: '1px solid rgba(220, 38, 38, 0.35)',
  borderRadius: '8px',
  padding: '8px 12px',
  cursor: 'pointer'
};

const scenarioRowStyle = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: '8px 0',
  color: '#0f172a'
};

const brokerRowStyle = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: '14px 16px',
  borderRadius: '14px',
  background: 'rgba(241, 245, 249, 0.85)',
  border: '1px solid rgba(148, 163, 184, 0.3)'
};

export default App;
