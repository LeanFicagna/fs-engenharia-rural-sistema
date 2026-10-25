import io
import json
from datetime import datetime, timezone
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Solicitacao
from .planilha import importar_da_planilha

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


def resposta_da_planilha(solicitacoes):
    return io.BytesIO(json.dumps({"ok": True, "total": len(solicitacoes), "solicitacoes": solicitacoes}).encode())


LINHA_VALIDA = {
    "id": 2,
    "data": "Wed Oct 14 2026 11:29:26 GMT-0300 (Horário Padrão de Brasília)",
    "nome": "Pedro Lima",
    "email": "pedro@example.com",
    "cidade": "Placas",
    "uf": "PA",
    "telefone": "(93) 99123-4567",
    "mensagem": "Georreferenciamento do lote.",
}


@override_settings(PLANILHA_URL="https://planilha.example/exec", PLANILHA_TOKEN="token-de-teste")
class ImportacaoPlanilhaTests(TestCase):
    def test_importa_linhas_validas_uma_vez_so(self):
        linha_invalida = {**LINHA_VALIDA, "id": 3, "email": "outra@example.com", "telefone": "123"}

        with patch("solicitacoes.planilha.urlopen", side_effect=lambda *a, **k: resposta_da_planilha([LINHA_VALIDA, linha_invalida])) as urlopen:
            primeira = importar_da_planilha()
            segunda = importar_da_planilha()

        self.assertIn("token=token-de-teste", urlopen.call_args.args[0])
        self.assertEqual((primeira.criadas, len(primeira.invalidas)), (1, 1))
        self.assertEqual((segunda.criadas, segunda.ja_importadas), (0, 1))

        solicitacao = Solicitacao.objects.get()
        self.assertEqual(solicitacao.nome, "Pedro Lima")
        self.assertEqual(solicitacao.criada_em, datetime(2026, 10, 14, 14, 29, 26, tzinfo=timezone.utc))

    @override_settings(PLANILHA_TOKEN="")
    def test_botao_avisa_quando_token_nao_esta_configurado(self):
        self.client.force_login(User.objects.create_user("maria", password=SENHA))

        resposta = self.client.post(reverse("importar-planilha"), follow=True)

        self.assertContains(resposta, "Configure PLANILHA_URL e PLANILHA_TOKEN")
        self.assertFalse(Solicitacao.objects.exists())


class CadastroUsuarioTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_admin_cadastra_usuario_que_entra_e_ve_solicitacoes(self):
        admin = User.objects.create_superuser("admin", "admin@example.com", SENHA)
        self.client.force_login(admin)
        senha_nova = "Pronaf-Santarem-2026"

        resposta = self.client.post(
            reverse("cadastrar-usuario"),
            {"first_name": "Lucas", "email": "Lucas@Example.com", "password1": senha_nova, "password2": senha_nova},
        )

        self.assertRedirects(resposta, reverse("lista"))
        usuario = User.objects.get(username="lucas@example.com")
        self.assertEqual(usuario.first_name, "Lucas")
        self.assertFalse(usuario.is_superuser)
        # Senha guardada com hash, nunca em texto puro
        self.assertNotEqual(usuario.password, senha_nova)
        self.assertTrue(usuario.check_password(senha_nova))

        # O novo usuário entra com o e-mail e vê a lista de solicitações
        self.client.logout()
        resposta = self.client.post(reverse("login"), {"username": "lucas@example.com", "password": senha_nova})
        self.assertRedirects(resposta, reverse("lista"))
        self.assertContains(self.client.get(reverse("lista")), "Solicitações")

    def test_usuario_comum_nao_acessa_cadastro(self):
        self.client.force_login(User.objects.create_user("maria", password=SENHA))
        senha_nova = "Pronaf-Santarem-2026"

        self.assertEqual(self.client.get(reverse("cadastrar-usuario")).status_code, 403)
        resposta = self.client.post(
            reverse("cadastrar-usuario"),
            {"first_name": "Intruso", "email": "intruso@example.com", "password1": senha_nova, "password2": senha_nova},
        )

        self.assertEqual(resposta.status_code, 403)
        self.assertFalse(User.objects.filter(email="intruso@example.com").exists())
