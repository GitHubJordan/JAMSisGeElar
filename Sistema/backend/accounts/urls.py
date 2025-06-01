# Sistema/backend/accounts/urls.py

from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Login e logout padrão (poderão usar as views builtin ou customizadas)
    # Exemplo com as views padrão do Django:
    path('login/', 
         LoginView.as_view(template_name='accounts/login.html'), 
         name='login'),
    path('logout/', 
         LogoutView.as_view(next_page='accounts:login'), 
         name='logout'),

     # Redirecionamento pós-login
     path('redirect-dashboard/', views.redirect_dashboard, name='redirect-dashboard'),

     # CRUD de Usuários (RF-03 a RF-06)
     path('users/', views.UserListView.as_view(), name='user-list'),
     path('users/new/', views.UserCreateView.as_view(), name='user-create'),
     path('users/edit/<int:pk>/', views.UserUpdateView.as_view(), name='user-edit'),
     path('users/delete/<int:pk>/', views.UserDeleteView.as_view(), name='user-delete'),
]
