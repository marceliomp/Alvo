# Alvo Forecast

Aplicativo de console para analisar a margem de contribuição, EBITDA e lucro das vendas imobiliárias. O objetivo é permitir simulações rápidas de cenários alterando volumes de vendas, custos variáveis por corretor e componentes de custos fixos.

Cada venda representa a comercialização de um imóvel. Você informa o valor do imóvel e a porcentagem de comissão da Alvo e o sistema calcula automaticamente a receita (comissão bruta). A partir dessa comissão você pode definir os pagamentos aos corretores e demais custos variáveis.

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

   - Aumentar o valor de todos os imóveis em 8% (consequentemente a comissão) e reduzir custos variáveis em 5%:

     ```bash
     python -m alvo_app data/exemplo_cenario.json --scale-revenue 1.08 --scale-variable-costs 0.95
     ```

   - Ajustar somente a performance da corretora Maria (+12% no valor dos imóveis dela) e reduzir custos fixos de tecnologia para R$ 6.500:

     ```bash
     python -m alvo_app data/exemplo_cenario.json \
       --scale-broker "Maria.revenue=1.12" \
       --override "fixed.tecnologia=6500"
     ```

   - Alterar as demais linhas do DRE, como outras receitas e depreciação:

     ```bash
     python -m alvo_app data/exemplo_cenario.json --override "other_income=12000" --override "depreciation=5000"
     ```

   - Atualizar diretamente o valor do imóvel `V001` para R$ 1.200.000 e redefinir a comissão da Alvo para 6%:

     ```bash
     python -m alvo_app data/exemplo_cenario.json --override "sale.V001.property_value=1200000" --override "sale.V001.commission_rate=6"
     ```

   - Fixar manualmente a comissão recebida na venda `V002` em R$ 45.000 e redistribuir automaticamente os custos variáveis totais:

     ```bash
     python -m alvo_app data/exemplo_cenario.json --override "sale.V002.revenue=45000" --override "sale.V002.variable_costs=25000"
     ```

5. **Salvar o cenário ajustado:**

   ```bash
   python -m alvo_app data/exemplo_cenario.json --scale-revenue 1.05 --save simulacao.json
   ```

## Formato do arquivo de cenário

Cada entrada em `sales` deve conter:

- `id`: identificador único da venda.
- `broker`: nome do corretor responsável.
- `property_value`: valor de venda do imóvel.
- `commission_rate`: percentual da comissão da Alvo. Pode ser informado em decimal (`0.05`) ou em porcentagem base 100 (`5`).
- `variable_costs`: dicionário com os custos variáveis descontados da comissão (ex.: repasse ao corretor, marketing, impostos).
- `notes` (opcional): observações livres.

Opcionalmente você pode definir `commission_override` para fixar manualmente a comissão recebida. Se não informar esse campo, a comissão será calculada automaticamente como `property_value * commission_rate`.

## Testes

Execute os testes automatizados com o `pytest`:

```bash
pytest
```
