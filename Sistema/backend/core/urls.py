# Sistema/backend/core/urls.py

from django.urls import path
from . import views
from .views import exercicio_list

app_name = 'core'

urlpatterns = [
    # Configuração inicial (apenas edição)
    path('configuracao/', views.ConfiguracaoInicialUpdateView.as_view(), name='configuracao'),

    # Histórico de backups e botão "Backup Agora"
    path('backup/', views.backup_list, name='backup-list'),

    # Logs de erro
    path('logs/error/', views.ErrorLogListView.as_view(), name='errorlog-list'),

    # Logs de notificação
    path('logs/notification/', views.NotificationLogListView.as_view(), name='notificationlog-list'),

    # Logs de acesso (Admin)
    path('logs/access/', views.AccessLogListView.as_view(), name='accesslog-list'),

    # Exercício (switch)
    path('exercicio/', exercicio_list, name='exercicio-list'),
]
