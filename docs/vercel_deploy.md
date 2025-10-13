# Publicação no Vercel

Este guia resume como publicar o forecast imobiliário no [Vercel](https://vercel.com/) usando o Dockerfile já existente no projeto. O fluxo é totalmente integrado ao GitHub e não exige ajustes no código da aplicação.

## 1. Preparar o repositório

1. Faça o fork do repositório no GitHub (ou envie o código para um repositório próprio).
2. Verifique se o arquivo `vercel.json` está na raiz do projeto. Ele instrui o Vercel a usar o `Dockerfile` para construir e executar a aplicação Streamlit.
3. Confirme se todos os arquivos necessários estão versionados, especialmente `requirements.txt`, `Dockerfile` e a pasta `app/`.

## 2. Criar o projeto no Vercel

1. Acesse o painel do Vercel e clique em **Add New… → Project**.
2. Conecte a sua conta GitHub (caso ainda não esteja conectada) e selecione o repositório do projeto.
3. Em **Framework Preset**, escolha **Other**.
4. Em **Build & Development Settings**, não defina nenhum comando personalizado. O Vercel detectará o `vercel.json` e usará o Dockerfile automaticamente.
5. Clique em **Deploy** para iniciar a primeira implantação.

> ⚠️ O Vercel cria uma instância efêmera a partir do container. Dados gravados na pasta `data/` serão perdidos quando o container reiniciar. Para manter persistência, configure um storage externo (por exemplo, bucket S3, Supabase ou banco gerenciado) e adapte o app para usá-lo.

## 3. Ajustes pós-deploy

1. Após a publicação, copie o domínio gerado (ex.: `https://seu-projeto.vercel.app`).
2. Se quiser usar um domínio próprio, configure-o em **Settings → Domains** e ajuste o DNS conforme instruções do Vercel.
3. Para atualizar o site basta fazer push das alterações na branch monitorada (por padrão, `main`). O Vercel reconstruirá automaticamente a imagem Docker.

## 4. Variáveis de ambiente e segredos

Se você adicionar integrações externas (por exemplo, um banco de dados gerenciado), defina as variáveis em **Settings → Environment Variables**. Reimplante o projeto após salvar.

## 5. Monitoramento

O painel do Vercel exibe histórico de deployments, logs do container e consumo de recursos. Utilize esses dados para acompanhar o uso pelos corretores e detectar eventuais erros na aplicação Streamlit.

---

### Checklist rápido

- [ ] Repositório no GitHub conectado ao Vercel
- [ ] `vercel.json` na raiz apontando para o `Dockerfile`
- [ ] Primeiro deploy concluído e domínio copiado
- [ ] Configuração de domínio customizado (opcional)
- [ ] Estratégia de persistência definida para evitar perda de dados
