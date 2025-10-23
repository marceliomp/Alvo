# Alvo Forecast

Ferramenta interativa para simular o resultado operacional de uma operação imobiliária. Cadastre vendas, acompanhe a margem de contribuição por corretor e teste cenários variando receita, custos variáveis, comissões e despesas fixas.

## Pré-requisitos

- Node.js 18 ou superior
- npm 9 ou superior

## Como executar

```bash
npm install
npm run dev
```

O comando `npm run dev` inicia o Vite na porta `5173`. A aplicação será recarregada automaticamente ao salvar alterações.

## Build de produção

```bash
npm run build
npm run preview
```

O build gera os arquivos estáticos em `dist/`. O comando `npm run preview` permite validar a versão otimizada antes da publicação.

## Funcionalidades principais

- Consolidação das vendas com cálculo automático de margem de contribuição e EBITDA.
- Visão por corretor com receita, comissões e margem.
- Simulador de cenários para ajustar percentuais de receita, custos variáveis, comissões e custos fixos.
- Inclusão e remoção de vendas em tempo real.
