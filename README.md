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

## Persistência em JSON

Para manter os dados entre execuções, utilize os utilitários `load_repository` e `save_repository`. Eles gravam todas as oportunidades, motivos de perda e os próximos identificadores em um único arquivo JSON.

```python
from pathlib import Path

from alvo_forecast import load_repository, save_repository

path = Path("data/forecast_data.json")
repo, next_opportunity_id, next_loss_reason_id = load_repository(path)
# ... interaja com o repositório ...
save_repository(
    repo,
    path,
    next_opportunity_id=next_opportunity_id,
    next_loss_reason_id=next_loss_reason_id,
)
```

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

3. Acesse o endereço indicado pelo Streamlit no navegador para registrar oportunidades, cadastrar motivos de perda, visualizar o dashboard analítico e exportar os dados em CSV. Todas as inclusões são persistidas automaticamente no arquivo `data/forecast_data.json`.

## Como Disponibilizar Online

Para um guia passo a passo detalhado (incluindo pré-requisitos, criação do repositório no GitHub e sugestões de provedores), consulte [docs/deploy.md](docs/deploy.md).

Você pode publicar a aplicação na nuvem de duas maneiras rápidas:

### 1. Streamlit Community Cloud

1. Faça fork deste repositório para a sua conta do GitHub.
2. Acesse [streamlit.io/cloud](https://streamlit.io/cloud) e conecte sua conta do GitHub.
3. Crie um novo app selecionando o repositório e o branch desejado.
4. Informe `app/streamlit_app.py` como arquivo principal e mantenha o comando padrão (`streamlit run`).
5. O ambiente utilizará automaticamente o arquivo `requirements.txt` para instalar as dependências (`-e .[app]`).
6. Após o deploy, compartilhe a URL gerada com o time de corretores.

Para preservar os dados entre reinicializações, configure um diretório persistente nas configurações avançadas do Streamlit Cloud ou integre com um serviço externo (ex.: Google Sheets, banco de dados).

### 2. Container Docker

1. Construa a imagem:

   ```bash
   docker build -t alvo-forecast .
   ```

2. Execute o container expondo a porta 8501 e montando um volume para manter os dados do arquivo `data/forecast_data.json`:

   ```bash
   docker run -p 8501:8501 \
     -v "$(pwd)/data:/app/data" \
     alvo-forecast
   ```

3. Acesse `http://localhost:8501` no navegador e compartilhe o endereço público (ou faça o deploy em um provedor como AWS, Azure, GCP, Railway, etc.).

> **Dica:** ao publicar em um provedor de containers, garanta que o diretório `/app/data` esteja em um volume persistente para que as informações cadastradas permaneçam disponíveis.

## Publicação no GitHub Pages

Como a aplicação Streamlit precisa de um servidor Python em execução, o GitHub Pages será usado como um site estático complementar com informações e um link para o deploy ativo (por exemplo, no Streamlit Cloud ou em um provedor de containers).

1. Crie um repositório na sua conta do GitHub e copie a URL (HTTPS ou SSH).
2. No seu ambiente local, clone este projeto ou adicione o remoto ao diretório atual:

   ```bash
   git remote add origin <url-do-seu-repositorio>
   git push -u origin main
   ```

3. No GitHub, acesse **Settings → Pages** e selecione como fonte o branch `main` com a pasta `/docs`.
4. Edite o arquivo `docs/index.md` e substitua o placeholder `https://<seu-app-streamlit>` pela URL real do deploy (por exemplo, o endereço gerado no Streamlit Cloud).
5. Aguarde alguns minutos até que o GitHub Pages publique o site. Compartilhe o link gerado com o time para que eles encontrem rapidamente o app e a documentação.

## Próximos Passos

- Integrar os modelos a um banco de dados relacional.
- Conectar os cálculos a um dashboard interativo (por exemplo, Power BI ou Streamlit).
- Criar validações adicionais para garantir o preenchimento obrigatório dos campos SPIN acima do ticket mínimo configurável.
