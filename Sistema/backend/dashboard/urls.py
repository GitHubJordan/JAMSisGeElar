from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('admin/', views.admin_dashboard, name='admin-dashboard'),
    path('diretor/', views.diretor_dashboard, name='diretor-dashboard'),
    path('pedagogico/', views.pedagogico_dashboard, name='pedagogico-dashboard'),
    path('secretaria/', views.secretaria_dashboard, name='secretaria-dashboard'),
]
