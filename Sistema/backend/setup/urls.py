# Sistema/backend/setup/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from dashboard.views import home_view

urlpatterns = [
    # Página inicial do sistema
    path('', home_view, name='home'),
    
    # Admin Django
    path('admin/', admin.site.urls),

    # URLs de autenticação e CRUD de usuário
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # URLs de cada módulo do sistema
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('secretaria/', include('secretaria.urls', namespace='secretaria')),
    path('pedagogico/', include('pedagogico.urls', namespace='pedagogico')),
    path('administrativo/', include('administrativo.urls', namespace='administrativo')),
    path('config/', include('core.urls', namespace='core')),
]

# Servir arquivos de mídia (fotos e PDFs) em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
