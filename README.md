# FS Rural — painel de solicitações

[![CI](https://github.com/LeanFicagna/fs-engenharia-rural-sistema/actions/workflows/ci.yml/badge.svg)](https://github.com/LeanFicagna/fs-engenharia-rural-sistema/actions/workflows/ci.yml)

Painel interno da **FS Consultoria Rural** para receber e acompanhar os pedidos de
atendimento enviados pelo formulário da landing page.

- `POST /api/solicitacoes/` recebe o formulário do site e valida os dados no servidor.
- A equipe entra com login (bloqueado por 15 minutos após 5 tentativas erradas).
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
python manage.py createsuperuser # cria o primeiro usuário da equipe
python manage.py runserver
```

Acesse <http://127.0.0.1:8000/> e entre com o usuário criado.

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

## Produção

Defina as variáveis `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS`,
`PLANILHA_URL` e `PLANILHA_TOKEN` (no `.env` ou no ambiente do servidor).
