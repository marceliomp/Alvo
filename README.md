# Alvo Forecast

Aplicativo de console para analisar a margem de contribuição, EBITDA e lucro das vendas imobiliárias. O objetivo é permitir simulações rápidas de cenários alterando volumes de vendas, custos variáveis por corretor e componentes de custos fixos.

## Como executar

1. **Criar um ambiente virtual (opcional, mas recomendado):**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows PowerShell
   ```

2. **Instalar dependências de desenvolvimento:**

   O projeto utiliza apenas a biblioteca padrão do Python. Para executar os testes automatizados, instale o `pytest`.

   ```bash
   pip install pytest
   ```

3. **Executar um cenário base:**

   ```bash
   python -m alvo_app data/exemplo_cenario.json
   ```

   O comando imprime um resumo dos indicadores principais e o detalhamento por corretor.

4. **Brincar com cenários:**

   - Aumentar toda a receita em 8% e reduzir custos variáveis em 5%:

     ```bash
     python -m alvo_app data/exemplo_cenario.json --scale-revenue 1.08 --scale-variable-costs 0.95
     ```

   - Ajustar somente a performance da corretora Maria (+12% de receita) e reduzir custos fixos de tecnologia para R$ 6.500:

     ```bash
     python -m alvo_app data/exemplo_cenario.json \
       --scale-broker "Maria.revenue=1.12" \
       --override "fixed.tecnologia=6500"
     ```

   - Alterar as demais linhas do DRE, como outras receitas e depreciação:

     ```bash
     python -m alvo_app data/exemplo_cenario.json --override "other_income=12000" --override "depreciation=5000"
     ```

   - Substituir a receita da venda `V001` por um valor específico e redistribuir automaticamente os custos variáveis totais:

     ```bash
     python -m alvo_app data/exemplo_cenario.json --override "sale.V001.revenue=180000" --override "sale.V001.variable_costs=15000"
     ```

5. **Salvar o cenário ajustado:**

   ```bash
   python -m alvo_app data/exemplo_cenario.json --scale-revenue 1.05 --save simulacao.json
   ```

## Testes

Execute os testes automatizados com o `pytest`:

```bash
pytest
```
