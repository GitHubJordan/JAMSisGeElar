# Sistema/backend/dashboard/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def admin_dashboard(request):
    """
    Dashboard principal para o Admin.
    Exibe estatísticas de todas as áreas.
    """
    # Exemplo de contexto (você pode buscar dados reais de cada app)
    from secretaria.models import Aluno, Fatura
    from administrativo.models import Colaborador
    alunos_total = Aluno.objects.count()
    faturas_pendentes = Fatura.objects.filter(status='PENDENTE').count()
    colaboradores_ativos = Colaborador.objects.filter(status='ATIVO').count()

    context = {
        'alunos_total': alunos_total,
        'faturas_pendentes': faturas_pendentes,
        'colaboradores_ativos': colaboradores_ativos,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def diretor_dashboard(request):
    """
    Dashboard voltado para o Diretor (foco em área administrativa).
    """
    from administrativo.models import Colaborador, Salario
    colaboradores_ativos = Colaborador.objects.filter(status='ATIVO').count()
    salarios_pendentes = Salario.objects.filter(salario_liquido__isnull=True).count()

    context = {
        'colaboradores_ativos': colaboradores_ativos,
        'salarios_pendentes': salarios_pendentes,
    }
    return render(request, 'dashboard/diretor_dashboard.html', context)

@login_required
def pedagogico_dashboard(request):
    """
    Dashboard para o Subdiretor Pedagógico: indicadores de Turmas e Notas.
    """
    from pedagogico.models import Turma, Nota
    turmas_total = Turma.objects.count()
    notas_pendentes = Nota.objects.filter(media_parcial__isnull=True).count()

    context = {
        'turmas_total': turmas_total,
        'notas_pendentes': notas_pendentes,
    }
    return render(request, 'dashboard/pedagogico_dashboard.html', context)

@login_required
def secretaria_dashboard(request):
    """
    Dashboard para o Secretário: indicadores de Alunos e Faturas.
    """
    from secretaria.models import Aluno, Fatura
    alunos_ativos = Aluno.objects.filter(status='ATIVO').count()
    faturas_vencidas = Fatura.objects.filter(status='VENCIDO').count()

    context = {
        'alunos_ativos': alunos_ativos,
        'faturas_vencidas': faturas_vencidas,
    }
    return render(request, 'dashboard/secretaria_dashboard.html', context)
