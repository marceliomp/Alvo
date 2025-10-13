# Alvo Forecast

## Descrição do Projeto

O Alvo Forecast é uma ferramenta de forecast de vendas imobiliárias que utiliza a metodologia SPIN Selling para otimizar as vendas. O projeto inclui uma análise de perdas e um dashboard interativo para corretores e gestores, permitindo uma visualização clara e eficaz dos dados de vendas.

## Identidade Visual

A identidade visual do projeto será composta pelas seguintes cores:
- Branco
- Preto
- Azul Petróleo
- Verde Petróleo

A logomarca e a paleta de cores foram cuidadosamente escolhidas para refletir a seriedade e a modernidade da ferramenta.

## Estrutura de Dados

O módulo `alvo_forecast` fornece dataclasses para representar oportunidades e motivos de perda:

```python
from dataclasses import dataclass
from datetime import date

from alvo_forecast import Opportunity, LossReason, OpportunityStatus, SpinStage

opportunity = Opportunity(
    id=1,
    created_at=date(2024, 1, 12),
    broker="Alice",
    development="Residencial Horizonte",
    expected_value=900_000.0,
    forecast_date=date(2024, 2, 15),
    closing_probability=0.7,  # valores entre 0 e 1
    status=OpportunityStatus.NEGOTIATION,
    spin_situation="Situação atual do cliente",
    spin_problem="Problema identificado",
    spin_implication="Consequências do problema",
    spin_need="Necessidade de solução",
    identified_objections=["Prazo de entrega"],
)
```

Para oportunidades acima do ticket definido, utilize o método `require_spin` para validar o preenchimento dos campos SPIN.

## Repositório em Memória

O `ForecastRepository` oferece operações básicas para registrar e atualizar oportunidades e motivos de perda em memória. Ele também permite identificar facilmente quais oportunidades exigem o preenchimento completo do questionário SPIN.

## Camada Analítica

O módulo inclui funções para gerar as principais visões do dashboard descrito na especificação inicial:

- `forecast_vs_realized`: agrega valores previstos e realizados por mês, corretor ou empreendimento.
- `loss_reason_summary`: gera ranking dos motivos de perda.
- `spin_stage_blockers`: identifica em qual etapa do SPIN as vendas estão travando.
- `objections_report`: contabiliza objeções recorrentes levantadas pelos clientes.

## Exportação

Use `export_opportunities_to_csv` para exportar todas as oportunidades para um arquivo CSV compatível com ferramentas como Excel ou Google Sheets.

```python
from pathlib import Path

from alvo_forecast import export_opportunities_to_csv, ForecastRepository

repo = ForecastRepository()
# ... registrar oportunidades ...
export_opportunities_to_csv(repo.list_opportunities(), Path("oportunidades.csv"))
```

## Exemplo de Uso

Um script de exemplo está disponível em `examples/demo.py`. Execute-o para visualizar a saída consolidada e gerar um CSV com as oportunidades fictícias:

```bash
PYTHONPATH=src python examples/demo.py
```

O script imprime as métricas de dashboard no terminal e salva um arquivo `/tmp/oportunidades.csv`.

## Aplicação Web Interativa

Foi adicionada uma interface em Streamlit para permitir o preenchimento das oportunidades e o acompanhamento das métricas em tempo real.

1. Instale as dependências do projeto:

   ```bash
   pip install -e .[app]
   ```

2. Execute a aplicação:

   ```bash
   streamlit run app/streamlit_app.py
   ```

3. Acesse o endereço indicado pelo Streamlit no navegador para registrar oportunidades, cadastrar motivos de perda, visualizar o dashboard analítico e exportar os dados em CSV.

## Próximos Passos

- Integrar os modelos a um banco de dados relacional.
- Conectar os cálculos a um dashboard interativo (por exemplo, Power BI ou Streamlit).
- Criar validações adicionais para garantir o preenchimento obrigatório dos campos SPIN acima do ticket mínimo configurável.
