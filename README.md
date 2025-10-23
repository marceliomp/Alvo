# Alvo Forecast

Aplicativo de console para analisar a margem de contribuição, EBITDA e lucro das vendas imobiliárias. O objetivo é permitir simulações rápidas de cenários alterando valores de imóveis, percentuais de comissão por produto, custos variáveis por corretor e componentes de custos fixos.

## Como executar

### Interface web (playground visual)

1. Instale dependências opcionais (nenhuma é obrigatória) e inicie um servidor HTTP simples apontando para a pasta `web`:

   ```bash
   python -m http.server --directory web 8000
   ```

2. Acesse <http://localhost:8000> para abrir o **Alvo Forecast Playground**. A tela carrega o cenário de exemplo e permite:

   - editar cada venda (valor do imóvel, percentual de comissão, receita manual, custos variáveis e corretor);
   - aplicar multiplicadores globais para testar cenários;
   - ajustar custos fixos, outras receitas/despesas, depreciação e amortização;
   - importar um cenário em JSON ou exportar o cenário ajustado.

3. Para hospedar de forma estática (ex.: Vercel, GitHub Pages ou Netlify), publique somente o arquivo `web/index.html`. Ele já inclui estilos, scripts e o cenário padrão embutido, funcionando inclusive ao abrir o arquivo diretamente no navegador.

### Aplicativo de linha de comando

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

  - Aumentar o valor de todos os imóveis (e a comissão resultante) em 8% e reduzir custos variáveis em 5%:

     ```bash
     python -m alvo_app data/exemplo_cenario.json --scale-revenue 1.08 --scale-variable-costs 0.95
     ```

  - Ajustar somente o valor das vendas da corretora Maria (+12%) e reduzir custos fixos de tecnologia para R$ 6.500:

     ```bash
     python -m alvo_app data/exemplo_cenario.json \
    --scale-broker "Maria.sale_value=1.12" \
       --override "fixed.tecnologia=6500"
     ```

   - Alterar as demais linhas do DRE, como outras receitas e depreciação:

     ```bash
     python -m alvo_app data/exemplo_cenario.json --override "other_income=12000" --override "depreciation=5000"
     ```

 - Substituir o percentual de comissão da venda `V001` por 6% e redistribuir automaticamente os custos variáveis totais:

    ```bash
    python -m alvo_app data/exemplo_cenario.json --override "sale.V001.commission_rate=0.06" --override "sale.V001.variable_costs=15000"
    ```

5. **Salvar o cenário ajustado:**

   ```bash
   python -m alvo_app data/exemplo_cenario.json --scale-revenue 1.05 --save simulacao.json
   ```

## Formato do arquivo de cenário

Cada venda deve informar o valor do imóvel (`sale_value`) e o percentual de comissão recebido pela Alvo (`commission_rate`). A receita líquida considerada nos cálculos é `sale_value * commission_rate`. Se preferir trabalhar diretamente com a receita já calculada, também é possível acrescentar o campo `revenue`. Nesse caso, se `commission_rate` não for informado, o aplicativo deduz automaticamente o percentual a partir da razão `revenue / sale_value` — isso garante que ajustes posteriores no valor do imóvel continuem coerentes. Caso a venda informe apenas `sale_value`, o campo `commission_rate` passa a ser obrigatório.

Exemplo resumido:

```json
{
  "id": "V001",
  "broker": "Maria",
  "sale_value": 1000000.0,
  "commission_rate": 0.05,
  "variable_costs": {
    "comissao_corretor": 20000.0,
    "marketing": 5000.0
  }
}
```

## Testes

Execute os testes automatizados com o `pytest`:

```bash
pytest
```
