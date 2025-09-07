# core/management/commands/backup_database.py
import os
import subprocess
from datetime import datetime
from django.core.management.base import BaseCommand
from core.models import ConfiguracaoInicial, BackupLog
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Gera backup do banco de dados PostgreSQL e grava em BackupLog.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--manual',
            action='store_true',
            help='Indica que o backup foi disparado manualmente (pelo usuário).',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            default=None,
            help='ID do usuário que executou o backup manual',
        )

    def handle(self, *args, **options):
        try:
            config = ConfiguracaoInicial.objects.get(pk=1)
        except ConfiguracaoInicial.DoesNotExist:
            self.stderr.write(self.style.ERROR('Nenhuma configuração inicial encontrada.'))
            return

        now = datetime.now()
        filename = now.strftime(config.backup_filename_pattern)
        backup_dir = config.backup_local_path
        
        # Validar e criar o diretório
        if not backup_dir:
            self.stderr.write(self.style.ERROR('Diretório de backup não configurado.'))
            return
            
        try:
            os.makedirs(backup_dir, exist_ok=True)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Erro ao criar diretório: {str(e)}'))
            return

        filepath = os.path.join(backup_dir, filename)

        # Determinar quem executou o backup
        executado_por = 'Sistema (agendado)'
        if options['manual']:
            try:
                user = User.objects.get(id=options['user_id'])
                executado_por = user.username
            except User.DoesNotExist:
                executado_por = 'Usuário desconhecido'

        # Comando pg_dump
        env = os.environ.copy()
        env['PGPASSWORD'] = config.db_password or ''
        cmd = [
            'pg_dump',
            '-h', config.db_host,
            '-p', str(config.db_port),
            '-U', config.db_user,
            '-d', config.db_name,
            '-F', 'c',
            '-f', filepath
        ]

        try:
            result = subprocess.run(
                cmd, 
                env=env, 
                check=True, 
                capture_output=True,
                text=True
            )
            
            # Backup bem sucedido
            BackupLog.objects.create(
                arquivo_nome=filename,
                status='SUCESSO',
                detalhes=result.stdout,
                executado_por=executado_por
            )
            self.stdout.write(self.style.SUCCESS(f'Backup realizado: {filepath}'))
            
        except subprocess.CalledProcessError as e:
            # Backup falhou
            BackupLog.objects.create(
                arquivo_nome=filename,
                status='FALHA',
                detalhes=e.stderr,
                executado_por=executado_por
            )
            self.stderr.write(self.style.ERROR(f'Falha no backup: {e.stderr}'))