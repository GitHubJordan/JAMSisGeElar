# Sistema/backend/core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import UpdateView, ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import ConfiguracaoInicial, BackupLog, ErrorLog, NotificationLog
from .forms import ConfiguracaoInicialForm
from .management.commands.backup_database import Command as BackupCommand
from django.core.exceptions import PermissionDenied
from accounts.decorators import role_required
from django.utils.decorators import method_decorator

import subprocess
import os
from datetime import datetime
from django.conf import settings

# ------------------------------
# Configuração Inicial (edit only)
# ------------------------------

@method_decorator(role_required('Admin'), name='dispatch')
class ConfiguracaoInicialUpdateView(LoginRequiredMixin, UpdateView):
    model = ConfiguracaoInicial
    form_class = ConfiguracaoInicialForm
    template_name = 'core/configuracao_form.html'
    success_url = reverse_lazy('core:configuracao')

    def get_object(self, queryset=None):
        # Sempre retornamos o único objeto de ConfiguracaoInicial (pk=1), ou criamos se não existir
        obj, created = ConfiguracaoInicial.objects.get_or_create(pk=1)
        return obj

    def form_valid(self, form):
        response = super().form_valid(form)
        # Após salvar, tentamos conexão de teste com o banco
        obj = form.instance
        try:
            # Comando simplificado: psql -h host -p port -U user -d dbname -c "\q"
            env = os.environ.copy()
            env['PGPASSWORD'] = obj.db_password
            cmd = [
                'psql',
                '-h', obj.db_host,
                '-p', obj.db_port,
                '-U', obj.db_user,
                '-d', obj.db_name,
                '-c', '\\q'
            ]
            subprocess.run(cmd, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            messages.success(self.request, 'Conexão ao banco testada com sucesso.')
        except subprocess.CalledProcessError as e:
            messages.error(self.request, f'Falha ao conectar ao banco: {e.stderr.decode()}')
        return response


@login_required
@role_required('Admin')
def backup_list(request):
    """
    Exibe histórico de BackupLog e permite executar backup manual.
    """
    logs = BackupLog.objects.all().order_by('-data_execucao')
    if request.method == 'POST':
        # Executa backup manualmente via management command
        cmd = BackupCommand()
        # Chamamos handle() diretamente, passando a si mesmo como args
        result = cmd.handle(manual=True)
        return redirect('core:backup-list')
    return render(request, 'core/backup_list.html', {'logs': logs})


@method_decorator(role_required('Admin'), name='dispatch')
class ErrorLogListView(LoginRequiredMixin, ListView):
    model = ErrorLog
    template_name = 'core/errorlog_list.html'
    context_object_name = 'errors'
    paginate_by = 20
    ordering = ['-data_ocorrencia']  # Campo correto: 'data_ocorrencia'


@method_decorator(role_required('Admin'), name='dispatch')
class NotificationLogListView(LoginRequiredMixin, ListView):
    model = NotificationLog
    template_name = 'core/notificationlog_list.html'
    context_object_name = 'notifications'
    paginate_by = 20
    ordering = ['-data_envio']
