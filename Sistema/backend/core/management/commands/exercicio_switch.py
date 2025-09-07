from django.core.management.base import BaseCommand
from core.models import Exercicio
from pedagogico.models import AnoLetivo
from core.management.commands.backup_database import Command as BackupCmd
from datetime import datetime

class Command(BaseCommand):
    help = 'Encerra o exercício atual (faz backup) e inicia novo exercício para o AnoLetivo indicado.'

    def add_arguments(self, parser):
        parser.add_argument('ano_id', type=int, help='ID do AnoLetivo a iniciar')

    def handle(self, *args, **options):
        ano = AnoLetivo.objects.get(pk=options['ano_id'])
        # 1. Encerrar atual
        atual = Exercicio.objects.filter(encerrado_em__isnull=True).first()
        if atual:
            backup = BackupCmd()
            backup.handle(manual=True)
            atual.encerrado_em = datetime.now()
            atual.backup_path = getattr(backup, 'last_backup_path', '')
            atual.save()
            self.stdout.write(self.style.SUCCESS('Exercício anterior encerrado e backup feito.'))

        # 2. Iniciar novo
        Exercicio.objects.create(ano=ano)
        self.stdout.write(self.style.SUCCESS(f'Novo exercício iniciado: {ano.nome}'))
