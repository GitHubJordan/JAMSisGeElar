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
]
