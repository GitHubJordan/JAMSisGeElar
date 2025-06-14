# Sistema/backend/pedagogico/urls.py

from django.urls import path
from . import views

app_name = 'pedagogico'

urlpatterns = [
    # Redirecionamento raiz → dashboard pedagógico
    path('', views.usuario_redirect_pedagogico, name='root'),

    # CRUD Turma
    path('turmas/', views.TurmaListView.as_view(), name='turma-list'),
    path('turmas/new/', views.TurmaCreateView.as_view(), name='turma-create'),
    path('turmas/edit/<int:pk>/', views.TurmaUpdateView.as_view(), name='turma-edit'),
    path('turmas/delete/<int:pk>/', views.TurmaDeleteView.as_view(), name='turma-delete'),

    # CRUD Disciplina
    path('disciplinas/', views.DisciplinaListView.as_view(), name='disciplina-list'),
    path('disciplinas/new/', views.DisciplinaCreateView.as_view(), name='disciplina-create'),
    path('disciplinas/edit/<int:pk>/', views.DisciplinaUpdateView.as_view(), name='disciplina-edit'),
    path('disciplinas/delete/<int:pk>/', views.DisciplinaDeleteView.as_view(), name='disciplina-delete'),

    # CRUD TurmaDisciplina
    path('turmadisciplinas/', views.TurmaDisciplinaListView.as_view(), name='turmadisciplina-list'),
    path('turmadisciplinas/new/', views.TurmaDisciplinaCreateView.as_view(), name='turmadisciplina-create'),
    path('turmadisciplinas/edit/<int:pk>/', views.TurmaDisciplinaUpdateView.as_view(), name='turmadisciplina-edit'),
    path('turmadisciplinas/delete/<int:pk>/', views.TurmaDisciplinaDeleteView.as_view(), name='turmadisciplina-delete'),

    # CRUD Matricula
    path('matriculas/', views.MatriculaListView.as_view(), name='matricula-list'),
    path('matriculas/new/', views.MatriculaCreateView.as_view(), name='matricula-create'),
    path('matriculas/edit/<int:pk>/', views.MatriculaUpdateView.as_view(), name='matricula-edit'),
    path('matriculas/delete/<int:pk>/', views.MatriculaDeleteView.as_view(), name='matricula-delete'),

    # CRUD Nota
    path('notas/', views.NotaListView.as_view(), name='nota-list'),
    path('notas/new/', views.NotaCreateView.as_view(), name='nota-create'),
    path('notas/edit/<int:pk>/', views.NotaUpdateView.as_view(), name='nota-edit'),
    path('notas/delete/<int:pk>/', views.NotaDeleteView.as_view(), name='nota-delete'),

    # Boletim: listagem + formulário de geração
    path('boletins/', views.BoletimListView.as_view(), name='boletim-list'),
    path('boletins/gerar/', views.gerar_boletim, name='boletim-gerar'),

    # CRUD Ano Letivo
    path('anoletivo/', views.AnoLetivoListView.as_view(), name='anoletivo-list'),
    path('anoletivo/new/', views.AnoLetivoCreateView.as_view(), name='anoletivo-create'),
    path('anoletivo/edit/<int:pk>/', views.AnoLetivoUpdateView.as_view(), name='anoletivo-edit'),
    path('anoletivo/delete/<int:pk>/', views.AnoLetivoDeleteView.as_view(), name='anoletivo-delete'),

    # CRUD Calendário (opcional)
    path('calendario/', views.CalendarioListView.as_view(), name='calendario-list'),
    path('calendario/new/', views.CalendarioCreateView.as_view(), name='calendario-create'),
    path('calendario/edit/<int:pk>/', views.CalendarioUpdateView.as_view(), name='calendario-edit'),
    path('calendario/delete/<int:pk>/', views.CalendarioDeleteView.as_view(), name='calendario-delete'),

    # Relatório de Ano Letivo
    path('relatorio/', views.relatorio_ano_letivo, name='relatorio-ano'),
]
