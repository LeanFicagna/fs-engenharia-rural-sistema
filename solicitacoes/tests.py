import json

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from .models import Solicitacao

SENHA = "senha-de-teste-123"

ENVIO_VALIDO = {
    "name": "João Pereira",
    "email": "joao@example.com",
    "city": "Santarém",
    "uf": "PA",
    "phone": "(93) 99999-0000",
    "message": "Preciso regularizar o CAR da propriedade.",
}


class SolicitacoesTests(TestCase):
    def setUp(self):
        # O contador de tentativas de login fica no cache, que não é limpo entre testes
        cache.clear()
        self.atendente = User.objects.create_user("maria", password=SENHA)

    def enviar(self, dados):
        # Igual à landing page: JSON como text/plain
        return self.client.post(
            reverse("api-criar-solicitacao"),
            data=json.dumps(dados),
            content_type="text/plain;charset=utf-8",
        )

    def criar_solicitacao(self):
        return Solicitacao.objects.create(
            nome="Ana", email="ana@example.com", cidade="Belterra", uf="PA",
            telefone="(93) 98888-1111", mensagem="Quero crédito rural para custeio.",
        )

    def entrar(self, senha):
        return self.client.post(reverse("login"), {"username": "maria", "password": senha})

    def test_envio_valido_cria_solicitacao(self):
        resposta = self.enviar(ENVIO_VALIDO)

        self.assertEqual(resposta.status_code, 201)
        solicitacao = Solicitacao.objects.get(pk=resposta.json()["id"])
        self.assertEqual(solicitacao.nome, "João Pereira")
        self.assertEqual(solicitacao.cidade, "Santarém")
        self.assertEqual(solicitacao.status, Solicitacao.Status.NOVA)

    def test_envio_invalido_retorna_erros_e_nao_salva(self):
        dados = {**ENVIO_VALIDO, "email": "nao-e-email", "uf": "XX", "phone": "123", "name": ""}

        resposta = self.enviar(dados)

        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(set(resposta.json()["erros"]), {"name", "email", "uf", "phone"})
        self.assertFalse(Solicitacao.objects.exists())

    def test_painel_exige_login(self):
        solicitacao = self.criar_solicitacao()

        for url in [reverse("lista"), reverse("atendimento", args=[solicitacao.pk])]:
            resposta = self.client.get(url)
            self.assertRedirects(resposta, f"{reverse('login')}?next={url}")

    def test_login_da_equipe_entra_no_painel(self):
        resposta = self.entrar(SENHA)

        self.assertRedirects(resposta, reverse("lista"))
        self.assertEqual(self.client.get(reverse("lista")).status_code, 200)

    def test_login_bloqueia_apos_5_tentativas_erradas(self):
        for _ in range(5):
            self.entrar("senha-errada")

        # Mesmo com a senha certa, continua bloqueado
        resposta = self.entrar(SENHA)

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Muitas tentativas erradas")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_atualizacao_do_atendimento(self):
        solicitacao = self.criar_solicitacao()
        self.client.force_login(self.atendente)

        resposta = self.client.post(
            reverse("atendimento", args=[solicitacao.pk]),
            {
                "status": Solicitacao.Status.EM_ATENDIMENTO,
                "agricultor_familiar": "true",
                "servico": Solicitacao.Servico.CREDITO_RURAL,
                "atendente": self.atendente.pk,
                "observacoes": "Documentos do Pronaf pedidos por WhatsApp.",
            },
        )

        self.assertRedirects(resposta, reverse("lista"))
        solicitacao.refresh_from_db()
        self.assertEqual(solicitacao.status, Solicitacao.Status.EM_ATENDIMENTO)
        self.assertTrue(solicitacao.agricultor_familiar)
        self.assertEqual(solicitacao.servico, Solicitacao.Servico.CREDITO_RURAL)
        self.assertEqual(solicitacao.atendente, self.atendente)
