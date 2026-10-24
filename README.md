# FS Rural — painel de solicitações

Painel interno da **FS Consultoria Rural** para receber e acompanhar os pedidos de
atendimento enviados pelo formulário da landing page.

- `POST /api/solicitacoes/` recebe o formulário do site e valida os dados no servidor.
- A equipe entra com login (bloqueado por 15 minutos após 5 tentativas erradas).
- A lista de pedidos pode ser filtrada por status e cidade; cada pedido tem uma tela
  para registrar o atendimento (status, agricultor familiar, serviço e atendente).

Feito em Django 5.2 (LTS) com SQLite.

## Como rodar

Requer Python 3.12 ou mais novo.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser # cria o primeiro usuário da equipe
python manage.py runserver
```

Acesse <http://127.0.0.1:8000/> e entre com o usuário criado.

Para rodar os testes:

```bash
python manage.py test
```

## Formulário da landing page

O site envia um JSON com `name`, `email`, `city`, `uf`, `phone` (`(99) 99999-9999`)
e `message`. Pode ir como `text/plain` com `mode: "no-cors"`, que evita o preflight
de CORS. O campo `website` é o honeypot: se vier preenchido, o envio é recusado.

Respostas: `201` com o `id` criado, ou `400` com os erros de cada campo.

## Produção

Defina as variáveis `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0` e `DJANGO_ALLOWED_HOSTS`.
