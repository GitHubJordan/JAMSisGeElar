from django.urls import path
from . import views

app_name = 'administrativo'

urlpatterns = [
    # Redireciona /administrativo/ → dashboard administrativo
    path('', views.usuario_redirect_administrativo, name='root'),

    # CRUD de Colaborador
    path('colaboradores/', views.ColaboradorListView.as_view(), name='colaborador-list'),
    path('colaboradores/new/', views.ColaboradorCreateView.as_view(), name='colaborador-create'),
    path('colaboradores/edit/<int:pk>/', views.ColaboradorUpdateView.as_view(), name='colaborador-edit'),
    path('colaboradores/delete/<int:pk>/', views.ColaboradorDeleteView.as_view(), name='colaborador-delete'),
    path('colaboradores/no-delete/', views.no_delete, name='colaborador-nodelete'),

    # CRUD de Salário
    path('salarios/', views.SalarioListView.as_view(), name='salario-list'),
    path('salarios/new/', views.SalarioCreateView.as_view(), name='salario-create'),
    path('salarios/edit/<int:pk>/', views.SalarioUpdateView.as_view(), name='salario-edit'),
    path('salarios/delete/<int:pk>/', views.SalarioDeleteView.as_view(), name='salario-delete'),
    path('salarios/report/', views.salario_report, name='salario-report'),

    # Geração de holerite por PDF (opcional, se quisermos rota separada)
    # path('salarios/<int:pk>/holerite/', views.gerar_holerite, name='salario-holerite'),

    # CRUD de BemPatrimonio
    path('patrimonios/', views.BemPatrimonioListView.as_view(), name='patrimonio-list'),
    path('patrimonios/new/', views.BemPatrimonioCreateView.as_view(), name='patrimonio-create'),
    path('patrimonios/edit/<int:pk>/', views.BemPatrimonioUpdateView.as_view(), name='patrimonio-edit'),
    path('patrimonios/delete/<int:pk>/', views.BemPatrimonioDeleteView.as_view(), name='patrimonio-delete'),

    # CRUD de Plano de Contas
    path('contas/', views.PlanoContasListView.as_view(), name='plano-contas-list'),
    path('contas/novo/', views.PlanoContasCreateView.as_view(), name='plano-contas-create'),
    path('contas/<int:pk>/editar/', views.PlanoContasUpdateView.as_view(), name='plano-contas-edit'),
    path('contas/<int:pk>/excluir/', views.PlanoContasDeleteView.as_view(), name='plano-contas-delete'),

    # CRUD de LancamentoContabil
    path('lancamentos/', views.LancamentoContabilListView.as_view(), name='lancamento-list'),
    path('lancamentos/new/', views.LancamentoContabilCreateView.as_view(), name='lancamento-create'),
    path('lancamentos/edit/<int:pk>/', views.LancamentoContabilUpdateView.as_view(), name='lancamento-edit'),
    path('lancamentos/delete/<int:pk>/', views.LancamentoContabilDeleteView.as_view(), name='lancamento-delete'),
]
