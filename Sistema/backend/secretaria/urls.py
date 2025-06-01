# Sistema/backend/secretaria/urls.py

from django.urls import path
from . import views

app_name = 'secretaria'

urlpatterns = [
    # Dashboard de secretaria (caso alguém acesse /secretaria/ sem especificar)
    path('', views.usuario_redirect_secretaria, name='root'),

    # CRUD Encarregado
    path('encarregados/', views.EncarregadoListView.as_view(), name='encarregado-list'),
    path('encarregados/new/', views.EncarregadoCreateView.as_view(), name='encarregado-create'),
    path('encarregados/edit/<int:pk>/', views.EncarregadoUpdateView.as_view(), name='encarregado-edit'),
    path('encarregados/delete/<int:pk>/', views.EncarregadoDeleteView.as_view(), name='encarregado-delete'),

    # CRUD Aluno
    path('alunos/', views.AlunoListView.as_view(), name='aluno-list'),
    path('alunos/new/', views.AlunoCreateView.as_view(), name='aluno-create'),
    path('alunos/edit/<int:pk>/', views.AlunoUpdateView.as_view(), name='aluno-edit'),
    path('alunos/delete/<int:pk>/', views.AlunoDeleteView.as_view(), name='aluno-delete'),

    # CRUD Fatura
    path('faturas/', views.FaturaListView.as_view(), name='fatura-list'),
    path('faturas/new/', views.FaturaCreateView.as_view(), name='fatura-create'),
    path('faturas/edit/<int:pk>/', views.FaturaUpdateView.as_view(), name='fatura-edit'),
    path('faturas/delete/<int:pk>/', views.FaturaDeleteView.as_view(), name='fatura-delete'),

    # Listagem de Conta Corrente (somente leitura)
    path('contacorrente/', views.ContaCorrenteListView.as_view(), name='contacorrente-list'),
]
