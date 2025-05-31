from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('accounts/', include('accounts.urls', namespace='accounts')),
    # Futuras rotas:
    # path('secretaria/', include('secretaria.urls', namespace='secretaria')),
    # path('pedagogico/', include('pedagogico.urls', namespace='pedagogico')),
    # path('administrativo/', include('administrativo.urls', namespace='administrativo')),
    # path('config/', include('core.urls', namespace='core')),
]
