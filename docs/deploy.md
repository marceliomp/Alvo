# Guia de Deploy do Alvo Forecast

Este passo a passo mostra como publicar o projeto na internet usando GitHub, Streamlit Community Cloud e opções alternativas em provedores de contêiner.

## 1. Preparar o Repositório no GitHub

1. [Crie um fork](https://docs.github.com/pt/get-started/quickstart/fork-a-repo) deste repositório ou faça o upload do código para um repositório novo na sua conta.
2. No seu computador, clone o repositório com:
   ```bash
   git clone https://github.com/<seu-usuario>/<seu-repositorio>.git
   cd <seu-repositorio>
   ```
3. Garanta que os arquivos do projeto estejam na branch `main` (ou outra que você prefira publicar) e envie-os para o GitHub:
   ```bash
   git add .
   git commit -m "Publica Alvo Forecast"
   git push origin main
   ```

> **Dica:** o arquivo `docs/index.md` possui um link placeholder `https://<seu-app-streamlit>`. Atualize-o depois que o deploy estiver ativo.

## 2. Deploy com Streamlit Community Cloud (recomendado)

1. Acesse [https://streamlit.io/cloud](https://streamlit.io/cloud) e clique em **Get Started**.
2. Conecte a sua conta do GitHub ao Streamlit Community Cloud.
3. Clique em **New app** e selecione o repositório `<seu-usuario>/<seu-repositorio>` e a branch `main`.
4. Informe `app/streamlit_app.py` no campo **Main file path**.
5. O campo **Packages** pode ficar vazio porque o serviço lerá automaticamente o `requirements.txt` do projeto (que já aponta para `-e .[app]`).
6. Clique em **Deploy** e aguarde a criação do ambiente. A URL final aparecerá no painel do Streamlit.
7. Copie a URL pública gerada e atualize o arquivo `docs/index.md` com esse endereço para facilitar o acesso dos corretores.

### Persistência de dados no Streamlit Cloud

Por padrão, o Streamlit Community Cloud não garante persistência de arquivos entre reinicializações. Para manter os dados do arquivo `data/forecast_data.json` você pode:

- **Configurar um diretório persistente:** em **App settings → Advanced settings → Enable “Allow app to read and write files from a directory.”** Defina um caminho como `/mount/data` e ajuste `DATA_PATH` via variável de ambiente.
- **Usar um serviço externo:** adapte o código para salvar os dados em planilhas Google, Amazon S3, Supabase ou outro banco de dados acessível pela internet.

## 3. Opcional: Deploy em Provedores de Contêiner

Se você preferir controlar a infraestrutura ou já tiver conta em plataformas como Render, Railway, Fly.io, AWS, Azure ou GCP, utilize o `Dockerfile` incluso.

1. Gere a imagem localmente para testar:
   ```bash
   docker build -t alvo-forecast .
   docker run -p 8501:8501 -v "$(pwd)/data:/app/data" alvo-forecast
   ```
   O app ficará disponível em `http://localhost:8501`.
2. Nos provedores que aceitam deploy via Dockerfile, basta apontar o repositório e informar a porta `8501` como porta exposta.
3. Configure uma variável de ambiente chamada `STREAMLIT_SERVER_PORT=8501` caso o provedor exija a declaração explícita.
4. Monte um volume persistente (por exemplo, `/app/data`) para garantir que `data/forecast_data.json` seja preservado.

## 4. Publicar a Página Informativa no GitHub Pages

1. No GitHub, vá em **Settings → Pages** e selecione a branch `main` com a pasta `/docs`.
2. Aguarde a publicação do site e utilize o endereço `https://<seu-usuario>.github.io/<seu-repositorio>/` como página institucional.
3. Dentro de `docs/index.md`, substitua o placeholder pelo link real do deploy (ex.: URL do Streamlit Cloud ou do provedor de contêiner).

## 5. Checklist Final

- [ ] Repositório sincronizado com o GitHub.
- [ ] Deploy ativo (Streamlit Cloud ou contêiner).
- [ ] Link do deploy atualizado em `docs/index.md`.
- [ ] GitHub Pages habilitado para compartilhar instruções com os corretores.

Com esses passos, o time terá acesso ao aplicativo e às instruções de uso em poucos minutos.
