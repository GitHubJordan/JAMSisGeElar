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

     # CRUD Pré‑Matrícula
    path('prematriculas/', views.PreMatriculaListView.as_view(),   name='prematricula-list'),
    path('prematriculas/new/', views.PreMatriculaCreateView.as_view(), name='prematricula-create'),
    path('prematriculas/<int:pk>/edit/', views.PreMatriculaUpdateView.as_view(), name='prematricula-edit'),
    path('prematriculas/<int:pk>/delete/', views.PreMatriculaDeleteView.as_view(), name='prematricula-delete'),

    # Rematrícula: lista pendentes + formulário
    path('rematricula/', views.prematricula_list,   name='rematricula-list'),
    path('rematricula/novo/', views.prematricula_create, name='rematricula-create'),
    path('rematricula/<int:pk>/edit/', views.prematricula_update, name='rematricula-edit'),
    path('rematricula/<int:pk>/delete/', views.prematricula_delete, name='rematricula-delete'),

    # CRUD Fatura
    path('faturas/', views.FaturaListView.as_view(), name='fatura-list'),
    path('faturas/new/', views.FaturaCreateView.as_view(), name='fatura-create'),
    path('faturas/edit/<int:pk>/', views.FaturaUpdateView.as_view(), name='fatura-edit'),
    path('faturas/delete/<int:pk>/', views.FaturaDeleteView.as_view(), name='fatura-delete'),
    path('faturas/report/', views.fatura_report, name='fatura-report'),

    # Listagem de Conta Corrente (somente leitura)
    path('contacorrente/', views.ContaCorrenteListView.as_view(), name='contacorrente-list'),
    path('contacorrente/report/', views.contacorrente_report, name='contacorrente-report'),

    # CRUD Servico
    path('servicos/', views.ServicoListView.as_view(),   name='servico-list'),
    path('servicos/new/', views.ServicoCreateView.as_view(), name='servico-create'),
    path('servicos/edit/<int:pk>/', views.ServicoUpdateView.as_view(), name='servico-edit'),
    path('servicos/delete/<int:pk>/', views.ServicoDeleteView.as_view(), name='servico-delete'),
]
