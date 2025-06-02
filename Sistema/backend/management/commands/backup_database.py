# Sistema/backend/core/management/commands/backup_database.py

from django.core.management.base import BaseCommand
from core.models import ConfiguracaoInicial, BackupLog
import subprocess
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Gera backup do banco de dados PostgreSQL e grava em BackupLog.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--manual',
            action='store_true',
            help='Indica que o backup foi disparado manualmente (pelo usuário).',
        )

    def handle(self, *args, **options):
        # Obtém configuração (assume único registro pk=1)
        try:
            config = ConfiguracaoInicial.objects.get(pk=1)
        except ConfiguracaoInicial.DoesNotExist:
            self.stderr.write(self.style.ERROR('Nenhuma configuração inicial encontrada.'))
            return

        now = datetime.now()
        filename = now.strftime(config.backup_filename_pattern)
        backup_dir = config.backup_dir
        # Certifique-se de que o diretório exista
        os.makedirs(backup_dir, exist_ok=True)
        filepath = os.path.join(backup_dir, filename)

        # Comando pg_dump
        env = os.environ.copy()
        env['PGPASSWORD'] = config.db_password or ''
        cmd = [
            'pg_dump',
            '-h', config.db_host,
            '-p', config.db_port,
            '-U', config.db_user,
            '-d', config.db_name,
            '-F', 'c',  # formato customizado (compactado)
            '-f', filepath
        ]

        log = BackupLog(filepath=filepath, success=False)
        try:
            subprocess.run(cmd, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            log.success = True
            log.save()
            self.stdout.write(self.style.SUCCESS(f'Backup realizado: {filepath}'))
        except subprocess.CalledProcessError as e:
            log.error_message = e.stderr.decode()
            log.save()
            self.stderr.write(self.style.ERROR(f'Falha no backup: {log.error_message}'))

        return
