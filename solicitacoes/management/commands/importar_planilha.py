from django.core.management.base import BaseCommand, CommandError

from solicitacoes.planilha import ErroPlanilha, importar_da_planilha


class Command(BaseCommand):
    help = "Importa para o painel os pedidos registrados na planilha da landing page."

    def handle(self, *args, **options):
        try:
            resultado = importar_da_planilha()
        except ErroPlanilha as erro:
            raise CommandError(str(erro)) from erro

        self.stdout.write(
            self.style.SUCCESS(
                f"{resultado.criadas} importada(s), {resultado.ja_importadas} já estavam no painel."
            )
        )
        for aviso in resultado.invalidas:
            self.stdout.write(self.style.WARNING(f"Ignorada — {aviso}"))
