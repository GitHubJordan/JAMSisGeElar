from django.db import models
from django.contrib.auth import get_user_model
from pedagogico.models import AnoLetivo
from django.conf import settings

User = get_user_model()


class Exercicio(models.Model):
    ano = models.ForeignKey(AnoLetivo, on_delete=models.PROTECT)
    iniciado_em = models.DateTimeField(auto_now_add=True)
    encerrado_em = models.DateTimeField(null=True, blank=True)
    backup_path = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['-iniciado_em']

    def __str__(self):
        status = 'Aberto' if not self.encerrado_em else 'Encerrado'
        return f"{self.ano.nome} ({status})"


class ConfiguracaoInicial(models.Model):
    """
    Armazena configurações de conexão de banco e serviços (e-mail, WhatsApp).
    Normalmente haverá apenas uma instância ativa.
    """
    DB_ENGINE_CHOICES = [
        ('postgresql', 'PostgreSQL'),
        ('sqlite3', 'SQLite'),
    ]

    db_engine = models.CharField('Engine do Banco', max_length=15, choices=DB_ENGINE_CHOICES)
    db_name = models.CharField('Nome do Banco', max_length=100)
    db_user = models.CharField('Usuário do Banco', max_length=50, blank=True)
    db_password = models.CharField('Senha do Banco', max_length=100, blank=True)
    db_host = models.CharField('Host', max_length=100, default='localhost')
    db_port = models.PositiveIntegerField('Porta', default=5432)
    backup_local_path = models.CharField('Diretório de Backup', max_length=250)
    backup_filename_pattern = models.CharField(
        'Padrão do Nome do Backup',
        max_length=100,
        default='backup_%Y%m%d_%H%M%S.sql',
        help_text="Padrão para o nome do arquivo de backup. Use strftime para datas. Exemplo: 'backup_%%Y%%m%%d_%%H%%M%%S.sql'"
    )
    smtp_host = models.CharField('SMTP Host', max_length=100, blank=True)
    smtp_port = models.PositiveIntegerField('SMTP Port', blank=True, null=True)
    smtp_user = models.CharField('SMTP Usuário', max_length=100, blank=True)
    smtp_password = models.CharField('SMTP Senha', max_length=100, blank=True)
    whatsapp_api_url = models.CharField('WhatsApp API URL', max_length=200, blank=True)
    whatsapp_api_token = models.CharField('WhatsApp API Token', max_length=200, blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Configuração Inicial'
        verbose_name_plural = 'Configurações Iniciais'

    def __str__(self):
        return f'Configuração #{self.id} – {self.db_engine}://{self.db_host}'


class BackupLog(models.Model):
    """
    Histórico de backups executados (manuais ou agendados).
    """
    arquivo_nome = models.CharField('Nome do Arquivo', max_length=200)
    status = models.CharField('Status', max_length=10, choices=[('SUCESSO', 'SUCESSO'), ('FALHA', 'FALHA')])
    detalhes = models.TextField('Detalhes (stdout/stderr)', blank=True)
    executado_por = models.CharField('Executado por', max_length=50)
    data_execucao = models.DateTimeField('Data de Execução', auto_now_add=True)

    class Meta:
        verbose_name = 'Backup Log'
        verbose_name_plural = 'Logs de Backup'
        ordering = ['-data_execucao']

    def __str__(self):
        return f'{self.arquivo_nome} – {self.status}'


class ErrorLog(models.Model):
    """
    Armazena exceções ou erros críticos do sistema (via middleware).
    """
    usuario = models.CharField('Usuário', max_length=150, default='Anonymous')
    url = models.CharField('URL', max_length=200)
    mensagem_erro = models.TextField('Mensagem de Erro')
    traceback = models.TextField('Traceback', blank=True)
    data_ocorrencia = models.DateTimeField('Data de Ocorrência', auto_now_add=True)

    class Meta:
        verbose_name = 'Error Log'
        verbose_name_plural = 'Logs de Erro'
        ordering = ['-data_ocorrencia']

    def __str__(self):
        return f'{self.data_ocorrencia:%d/%m/%Y %H:%M:%S} – {self.usuario}'


class NotificationLog(models.Model):
    """
    Registra notificações (e-mail/WhatsApp) enviadas pelo sistema (ex.: faturas vencidas).
    """
    MEIO_CHOICES = [
        ('EMAIL', 'E-mail'),
        ('WHATSAPP', 'WhatsApp'),
    ]
    fatura_id = models.IntegerField('Fatura ID', blank=True, null=True)
    destinatario = models.CharField('Destinatário', max_length=150)
    meio = models.CharField('Meio', max_length=10, choices=MEIO_CHOICES)
    status_envio = models.CharField('Status', max_length=15, choices=[('SUCESSO', 'SUCESSO'), ('FALHA', 'FALHA')])
    mensagem = models.TextField('Mensagem Enviada')
    detalhes = models.TextField('Detalhes (resposta API)', blank=True)
    data_envio = models.DateTimeField('Data de Envio', auto_now_add=True)

    class Meta:
        verbose_name = 'Notification Log'
        verbose_name_plural = 'Logs de Notificações'
        ordering = ['-data_envio']

    def __str__(self):
        return f'{self.data_envio:%d/%m/%Y %H:%M} → {self.destinatario} ({self.meio})'
    

class AccessLog(models.Model):
    ACTIONS = [
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
    ]
    user      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action    = models.CharField(max_length=6, choices=ACTIONS)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Log de Acesso'
        verbose_name_plural = 'Logs de Acesso'

    def __str__(self):
        return f"{self.user.username} – {self.get_action_display()} em {self.timestamp:%d/%m/%Y %H:%M}"
