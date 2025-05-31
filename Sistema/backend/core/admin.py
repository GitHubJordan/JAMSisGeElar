from django.contrib import admin
from .models import ConfiguracaoInicial, BackupLog, ErrorLog, NotificationLog

@admin.register(ConfiguracaoInicial)
class ConfiguracaoInicialAdmin(admin.ModelAdmin):
    list_display = ('db_engine', 'db_host', 'db_port')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(BackupLog)
class BackupLogAdmin(admin.ModelAdmin):
    list_display = ('arquivo_nome', 'status', 'data_execucao')
    list_filter = ('status',)
    search_fields = ('arquivo_nome', 'executado_por')
    date_hierarchy = 'data_execucao'
    readonly_fields = ('detalhes',)

@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'url', 'data_ocorrencia')
    search_fields = ('usuario', 'url')
    date_hierarchy = 'data_ocorrencia'
    readonly_fields = ('mensagem_erro', 'traceback')

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('destinatario', 'meio', 'status_envio', 'data_envio')
    list_filter = ('meio', 'status_envio')
    search_fields = ('destinatario', 'fatura_id')
    date_hierarchy = 'data_envio'