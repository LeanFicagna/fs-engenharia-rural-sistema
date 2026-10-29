# FS Rural — painel de solicitações

[![CI](https://github.com/LeanFicagna/fs-engenharia-rural-sistema/actions/workflows/ci.yml/badge.svg)](https://github.com/LeanFicagna/fs-engenharia-rural-sistema/actions/workflows/ci.yml)

Painel interno da **FS Consultoria Rural** para receber e acompanhar os pedidos de
atendimento enviados pelo formulário da landing page.

- `POST /api/solicitacoes/` recebe o formulário do site e valida os dados no servidor.
- A equipe entra com login (bloqueado por 15 minutos após 5 tentativas erradas).
- O administrador cadastra novos usuários da equipe em **Cadastrar usuário**
  (nome, e-mail e senha); o novo usuário entra com o e-mail.
- Os pedidos que a landing registra na planilha do Google são importados pelo botão
  **Importar da planilha** (ou pelo comando `importar_planilha`).
- A lista de pedidos pode ser filtrada por status e cidade; cada pedido tem uma tela
  para registrar o atendimento (status, agricultor familiar, serviço e atendente).

Feito em Django 5.2 (LTS) com SQLite.

## Como rodar

Requer Python 3.12 ou mais novo.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # preencha o PLANILHA_TOKEN
python manage.py migrate
python manage.py createsuperuser # cria o administrador; os demais ele cadastra pelo painel
python manage.py runserver
```

Acesse <http://127.0.0.1:8000/painel/> e entre com o usuário criado. A raiz
<http://127.0.0.1:8000/> mostra a landing page.

Para rodar os testes:

```bash
python manage.py test
```

O GitHub Actions roda os mesmos testes a cada push na `main` e em pull requests.

## Formulário da landing page

O site envia um JSON com `name`, `email`, `city`, `uf`, `phone` (`(99) 99999-9999`)
e `message`. Pode ir como `text/plain` com `mode: "no-cors"`, que evita o preflight
de CORS. O campo `website` é o honeypot: se vier preenchido, o envio é recusado.

Respostas: `201` com o `id` criado, ou `400` com os erros de cada campo.

## Importar da planilha

A landing grava cada pedido numa planilha via Apps Script. O `doGet` do script devolve
as linhas em JSON quando recebe `?token=` correto. O painel lê `PLANILHA_URL` e
`PLANILHA_TOKEN` do arquivo `.env`, que **não vai para o Git** (o modelo está em
`.env.example`).

```bash
python manage.py importar_planilha
```

Cada linha é validada como no formulário e importada uma vez só (a chave é data do
envio + e-mail). Linhas inválidas são ignoradas e listadas no aviso.

Para usar outro arquivo de banco (por exemplo, um banco só com dados fictícios),
defina `DJANGO_DB_PATH` com o caminho do arquivo.

## Produção

Defina as variáveis `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS`,
`PLANILHA_URL` e `PLANILHA_TOKEN` (no `.env` ou no ambiente do servidor).

## Landing page

O código da landing page da FS Consultoria Rural está em `landing/`: HTML, CSS e JS
estáticos, sem build. O site publicado em <https://www.fsengenhariarural.com.br> continua
sendo servido pelo GitHub Pages a partir do repositório
[LeanFicagna/fs-engenharia_web-site](https://github.com/LeanFicagna/fs-engenharia_web-site)
(branch `develop`); esta pasta é uma cópia dele e pode ficar desatualizada.

O Django também serve essa pasta na raiz: `/` é a landing (via WhiteNoise, `WHITENOISE_ROOT`),
`/painel/` é o painel da equipe, `/api/solicitacoes/` recebe o formulário e `/admin/` é o admin.

O formulário da landing envia cada pedido ao Google Apps Script (`landing/apps-script/`),
que grava na planilha. O painel traz esses pedidos pelo botão **Importar da planilha**.
O token de leitura fica só nas propriedades do script e no `.env` do painel, nunca no código.
