# Sistema/backend/dashboard/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required

from administrativo.models import Colaborador, Salario, BemPatrimonio, LancamentoContabil
from pedagogico.models import AnoLetivo, Turma, Matricula, Nota, PreRematricula, Calendario, Disciplina
from secretaria.models import Aluno, Fatura, PreMatricula
from django.db.models import Sum, Count, Q, Avg
from datetime import datetime, timedelta
from django.utils import timezone
import json
from django.contrib.auth.decorators import user_passes_test

from .models import Atividade  # Modelo hipotético para log de atividades


def macaco(valor):
    try:
        valor = float(valor)
    except (TypeError, ValueError):
        return str(valor)
    if abs(valor) >= 1_000_000_000:
        return f"{valor/1_000_000_000:.2f}B"
    elif abs(valor) >= 1_000_000:
        return f"{valor/1_000_000:.2f}M"
    else:
        return f"{valor:.2f}"


def home_view(request):
    context = {
        'welcome_message': "Transformando Educação com Tecnologia",
        'current_time': timezone.now(),
        'features': [
            {"icon": "fas fa-rocket", "title": "Gestão Inteligente", "desc": "Controle completo em tempo real"},
            {"icon": "fas fa-brain", "title": "Pedagogia Avançada", "desc": "Ferramentas de aprendizagem adaptativa"},
            {"icon": "fas fa-chart-network", "title": "Análise Preditiva", "desc": "Insights para tomada de decisão"}
        ]
    }
    return render(request, 'dashboard/home.html', context)


@login_required
@role_required('Admin', 'Diretor')
def admin_dashboard(request):
    # Total de alunos
    alunos_total = Aluno.objects.count()
    
    # Crescimento de alunos no mês atual vs anterior
    hoje = timezone.now()
    inicio_mes_atual = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    alunos_mes_atual = Aluno.objects.filter(created_at__gte=inicio_mes_atual).count()
    
    fim_mes_anterior = inicio_mes_atual - timedelta(days=1)
    inicio_mes_anterior = fim_mes_anterior.replace(day=1)
    alunos_mes_anterior = Aluno.objects.filter(
        created_at__gte=inicio_mes_anterior,
        created_at__lte=fim_mes_anterior
    ).count()
    
    if alunos_mes_anterior > 0:
        crescimento_alunos = ((alunos_mes_atual - alunos_mes_anterior) / alunos_mes_anterior) * 100
    else:
        crescimento_alunos = 100 if alunos_mes_atual > 0 else 0
    
    # Saúde financeira (taxa de pagamentos)
    faturas_pagas = Fatura.objects.filter(status='PAGO').count()
    faturas_total = Fatura.objects.count()
    taxa_pagamentos = (faturas_pagas / faturas_total * 100) if faturas_total > 0 else 100
    
    # Faturas vencidas
    faturas_vencidas = Fatura.objects.filter(status='VENCIDO').count()
    
    # Colaboradores
    colaboradores_ativos = Colaborador.objects.filter(status='ATIVO').count()
    novos_colaboradores = Colaborador.objects.filter(
        data_admissao__gte=inicio_mes_atual
    ).count()
    
    # Salários pendentes (mês atual)
    mes_referencia_atual = hoje.strftime('%Y-%m')
    salarios_pendentes = Colaborador.objects.filter(
        status='ATIVO'
    ).exclude(
        salarios__mes_referencia=mes_referencia_atual
    ).count()
    
    # Receita mensal
    receita_mensal = Fatura.objects.filter(
        status='PAGO',
        updated_at__gte=inicio_mes_atual
    ).aggregate(total=Sum('valor_atual'))['total'] or 0
    
    # Crescimento de receita vs mês anterior
    receita_mes_anterior = Fatura.objects.filter(
        status='PAGO',
        updated_at__gte=inicio_mes_anterior,
        updated_at__lte=fim_mes_anterior
    ).aggregate(total=Sum('valor_atual'))['total'] or 0
    
    if receita_mes_anterior > 0:
        crescimento_receita = ((receita_mensal - receita_mes_anterior) / receita_mes_anterior) * 100
    else:
        crescimento_receita = 100 if receita_mensal > 0 else 0
    
    # Notas pendentes
    notas_pendentes = Nota.objects.filter(
        Q(nota1=0) | Q(nota2=0) | Q(nota3=0)
    ).count()
    
    # Pré-matrículas pendentes
    pre_matriculas_pendentes = PreMatricula.objects.filter(
        status='PENDENTE'
    ).count()
    
    # Dados para gráfico de matrículas (últimos 6 meses)
    matriculas_labels = []
    matriculas_data = []
    for i in range(5, -1, -1):
        mes_ref = hoje - timedelta(days=30*i)
        mes_nome = mes_ref.strftime('%b/%Y')
        matriculas_labels.append(mes_nome)
        
        inicio_mes_ref = mes_ref.replace(day=1)
        if i == 0:
            fim_mes_ref = hoje
        else:
            fim_mes_ref = (inicio_mes_ref + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        total = Aluno.objects.filter(
            created_at__gte=inicio_mes_ref,
            created_at__lte=fim_mes_ref
        ).count()
        matriculas_data.append(total)
    
    # Dados para gráfico financeiro
    despesas_mensal = Salario.objects.filter(
        mes_referencia=mes_referencia_atual
    ).aggregate(total=Sum('salario_liquido'))['total'] or 0
    
    financeiro_data = [
        float(receita_mensal),
        float(despesas_mensal),
        float(receita_mensal - despesas_mensal)
    ]
    
    # Alertas críticos
    alertas_vazios = not any([
        faturas_vencidas > 0,
        salarios_pendentes > 0,
        notas_pendentes > 0,
        pre_matriculas_pendentes > 0
    ])
    
    # Atividades recentes (últimas 10)
    atividades_recentes = Atividade.objects.order_by('-data')[:10]
    
    context = {
        'alunos_total': alunos_total,
        'crescimento_alunos': crescimento_alunos,
        'taxa_pagamentos': taxa_pagamentos,
        'faturas_vencidas': faturas_vencidas,
        'colaboradores_ativos': colaboradores_ativos,
        'novos_colaboradores': novos_colaboradores,
        'salarios_pendentes': salarios_pendentes,
        'receita_mensal': macaco(receita_mensal),
        'crescimento_receita': crescimento_receita,
        'notas_pendentes': notas_pendentes,
        'pre_matriculas_pendentes': pre_matriculas_pendentes,
        'alertas_vazios': alertas_vazios,
        'atividades_recentes': atividades_recentes,
        'matriculas_labels': json.dumps(matriculas_labels),
        'matriculas_data': json.dumps(matriculas_data),
        'financeiro_data': json.dumps(financeiro_data),
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
@role_required('Admin', 'Diretor')
def diretor_dashboard(request):
    # 1. Colaboradores ativos
    colaboradores_ativos = Colaborador.objects.filter(status='ATIVO').count()
    
    # 2. Novos colaboradores no mês atual
    hoje = timezone.now()
    inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    novos_colaboradores = Colaborador.objects.filter(
        status='ATIVO', 
        data_admissao__gte=inicio_mes
    ).count()
    
    # 3. Salários pendentes (para o mês atual)
    mes_referencia_atual = hoje.strftime('%Y-%m')
    salarios_pendentes = Colaborador.objects.filter(
        status='ATIVO'
    ).exclude(
        salarios__mes_referencia=mes_referencia_atual
    ).count()
    
    # 4. Salários atrasados (meses anteriores)
    mes_passado = (hoje.replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
    salarios_atrasados = Colaborador.objects.filter(
        status='ATIVO'
    ).exclude(
        salarios__mes_referencia=mes_passado
    ).count()
    
    # 5. Patrimônio total
    patrimonio_total = BemPatrimonio.objects.aggregate(
        total=Sum('valor_contabil_liquido')
    )['total'] or 0
    total_bens = BemPatrimonio.objects.count()
    
    # 6. Resultado financeiro mensal (simplificado)
    receitas = LancamentoContabil.objects.filter(
        data_lancamento__gte=inicio_mes,
        conta_credito__tipo="RECEITA"
    ).aggregate(Sum('valor'))['valor__sum'] or 0
    
    despesas = LancamentoContabil.objects.filter(
        data_lancamento__gte=inicio_mes,
        conta_debito__tipo="DESPESA"
    ).aggregate(Sum('valor'))['valor__sum'] or 0
    
    resultado_mensal = receitas - despesas
    
    # 7. Lista de salários pendentes com detalhes
    lista_salarios_pendentes = []
    for colab in Colaborador.objects.filter(status='ATIVO'):
        if not Salario.objects.filter(colaborador=colab, mes_referencia=mes_referencia_atual).exists():
            lista_salarios_pendentes.append({
                'colaborador': colab,
                'salario_liquido': colab.salario_base,
                'esta_atrasado': False
            })
        elif not Salario.objects.filter(colaborador=colab, mes_referencia=mes_passado).exists():
            lista_salarios_pendentes.append({
                'colaborador': colab,
                'salario_liquido': colab.salario_base,
                'esta_atrasado': True
            })
    
    # 8. Dados para gráfico de departamentos
    departamentos = Colaborador.objects.filter(status='ATIVO').values(
        'departamento'
    ).annotate(
        total=Count('id')
    ).order_by('-total')
    
    departamentos_data = {
        'labels': [d['departamento'] for d in departamentos],
        'values': [d['total'] for d in departamentos]
    }
    
    # 9. Dados para gráfico de folha de pagamento (últimos 6 meses)
    meses = []
    valores = []
    for i in range(5, -1, -1):
        mes_ref = (hoje - timedelta(days=30*i)).strftime('%Y-%m')
        meses.append((hoje - timedelta(days=30*i)).strftime('%b/%Y'))
        
        total = Salario.objects.filter(
            mes_referencia=mes_ref
        ).aggregate(
            total=Sum('salario_liquido')
        )['total'] or 0
        
        valores.append(float(total))
    
    folha_pagamento_data = {
        'labels': meses,
        'values': valores
    }
    
    # 10. Últimos lançamentos contábeis
    ultimos_lancamentos = LancamentoContabil.objects.order_by('-data_lancamento')[:5]
    
    context = {
        'colaboradores_ativos': colaboradores_ativos,
        'novos_colaboradores': novos_colaboradores,
        'salarios_pendentes': salarios_pendentes,
        'salarios_atrasados': salarios_atrasados,
        'patrimonio_total': macaco(patrimonio_total),
        'total_bens': total_bens,
        'resultado_mensal': macaco(resultado_mensal),
        'lista_salarios_pendentes': lista_salarios_pendentes,
        'departamentos_data': json.dumps(departamentos_data),
        'folha_pagamento_data': json.dumps(folha_pagamento_data),
        'ultimos_lancamentos': ultimos_lancamentos,
    }
    
    return render(request, 'dashboard/diretor_dashboard.html', context)

@login_required
@role_required('Admin', 'Diretor', 'Pedagogico')
def pedagogico_dashboard(request):
    # Ano letivo ativo
    ano_letivo = AnoLetivo.objects.filter(ativo=True).first()
    
    # 1. Total de turmas no ano letivo ativo
    turmas_total = Turma.objects.filter(ano_letivo=ano_letivo).count() if ano_letivo else 0
    
    # 2. Total de alunos matriculados ativos
    alunos_total = Matricula.objects.filter(
        status='ATIVO',
        ano_letivo=ano_letivo
    ).count() if ano_letivo else 0
    
    # 3. Notas pendentes (considerando notas com pelo menos uma nota em branco)
    notas_pendentes = Nota.objects.filter(
        Q(nota1=0) | Q(nota2=0) | Q(nota3=0),
        ano_letivo=ano_letivo
    ).count() if ano_letivo else 0
    
    # 4. Notas atrasadas (pendentes há mais de 15 dias)
    data_limite = timezone.now() - timedelta(days=15)
    notas_atrasadas = Nota.objects.filter(
        (Q(nota1=0) | Q(nota2=0) | Q(nota3=0)),
        updated_at__lt=data_limite,
        ano_letivo=ano_letivo
    ).count() if ano_letivo else 0
    
    # 5. Pré-matrículas pendentes
    pre_matriculas_pendentes = PreMatricula.objects.filter(
        status='PENDENTE'
    ).count()
    
    # 6. Rematrículas pendentes
    rematriculas_pendentes = PreRematricula.objects.filter(
        status='PENDENTE'
    ).count()
    
    # 7. Taxa de aprovação (considerando notas com todas as avaliações preenchidas)
    if ano_letivo:
        aprovados = Nota.objects.filter(
            ano_letivo=ano_letivo,
            situacao='APROVADO'
        ).count()
        total_avaliados = Nota.objects.filter(
            ano_letivo=ano_letivo,
            nota1__gt=0,
            nota2__gt=0,
            nota3__gt=0
        ).count()
        taxa_aprovacao = (aprovados / total_avaliados * 100) if total_avaliados > 0 else 0
    else:
        taxa_aprovacao = 0
    
    # 8. Lista de notas pendentes com detalhes
    lista_notas_pendentes = []
    if ano_letivo:
        pendentes = Nota.objects.filter(
            (Q(nota1=0) | Q(nota2=0) | Q(nota3=0)),
            ano_letivo=ano_letivo
        ).select_related('disciplina', 'turma')[:10]
        
        for nota in pendentes:
            lista_notas_pendentes.append({
                'disciplina': nota.disciplina.nome,
                'turma': nota.turma.nome,
                'professor': nota.turma.professor_responsavel,
                'atrasada': nota.updated_at < (timezone.now() - timedelta(days=15))
            })
    
    # 9. Dados para gráfico de distribuição de alunos por turma
    turmas_data = {'labels': [], 'values': []}
    if ano_letivo:
        turmas = Turma.objects.filter(ano_letivo=ano_letivo).annotate(
            total_alunos=Count('matriculas')
        ).order_by('nome')
        
        turmas_data = {
            'labels': [t.nome for t in turmas],
            'values': [t.total_alunos for t in turmas]
        }
    
    # 10. Dados para gráfico de desempenho por disciplina
    desempenho_data = {'labels': [], 'values': []}
    if ano_letivo:
        disciplinas = Disciplina.objects.annotate(
            media_geral=Avg('notas__media_parcial', filter=Q(notas__ano_letivo=ano_letivo))
        ).order_by('nome')[:10]
        
        # Correção: converter Decimal para float
        desempenho_data = {
            'labels': [d.nome for d in disciplinas],
            'values': [float(d.media_geral) if d.media_geral is not None else 0.0 for d in disciplinas]
        }
    
    # 11. Próximos eventos acadêmicos (30 dias)
    data_inicio = timezone.now().date()
    data_fim = data_inicio + timedelta(days=30)
    proximos_eventos = Calendario.objects.filter(
        data__range=[data_inicio, data_fim]
    ).order_by('data')[:5]
    
    context = {
        'turmas_total': turmas_total,
        'alunos_total': alunos_total,
        'notas_pendentes': notas_pendentes,
        'notas_atrasadas': notas_atrasadas,
        'pre_matriculas_pendentes': pre_matriculas_pendentes,
        'rematriculas_pendentes': rematriculas_pendentes,
        'taxa_aprovacao': taxa_aprovacao,
        'lista_notas_pendentes': lista_notas_pendentes,
        'turmas_data': json.dumps(turmas_data),
        'desempenho_data': json.dumps(desempenho_data),
        'proximos_eventos': proximos_eventos,
    }
    
    return render(request, 'dashboard/pedagogico_dashboard.html', context)

@login_required
@role_required('Admin', 'Diretor', 'Secretaria')
def secretaria_dashboard(request):
    # 1. Alunos ativos
    alunos_ativos = Aluno.objects.filter(status='ATIVO').count()
    
    # 2. Novos alunos este mês
    hoje = timezone.now()
    inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    novos_alunos = Aluno.objects.filter(
        status='ATIVO', 
        created_at__gte=inicio_mes
    ).count()
    
    # 3. Faturas vencidas
    faturas_vencidas = Fatura.objects.filter(
        status='VENCIDO',
    ).count()
    
    # 4. Valor total vencido
    valor_vencido = Fatura.objects.filter(
        status='VENCIDO'
    ).aggregate(total=Sum('valor_atual'))['total'] or 0
    
    # 5. Faturas pendentes (não pagas e não vencidas)
    faturas_pendentes = Fatura.objects.filter(
        status='PENDENTE'
    ).count()
    
    # 6. Valor total pendente
    valor_pendente = Fatura.objects.filter(
        status='PENDENTE'
    ).aggregate(total=Sum('valor_atual'))['total'] or 0
    
    # 7. Pré-matrículas pendentes
    pre_matriculas_pendentes = PreMatricula.objects.filter(
        status='PENDENTE'
    ).count()
    
    # 8. Rematrículas pendentes
    rematriculas_pendentes = PreMatricula.objects.filter(
        status='PENDENTE'
    ).count()
    
    # 9. Lista de faturas vencidas (com dias de atraso)
    faturas_vencidas_lista = []
    for fatura in Fatura.objects.filter(status='VENCIDO').select_related('aluno')[:5]:
        dias_vencidos = (timezone.now().date() - fatura.data_vencimento).days
        faturas_vencidas_lista.append({
            'aluno': fatura.aluno,
            'data_vencimento': fatura.data_vencimento,
            'valor_atual': fatura.valor_atual,
            'dias_vencidos': dias_vencidos
        })
    
    # 10. Lista de pré-matrículas pendentes
    pre_matriculas_lista = PreMatricula.objects.filter(
        status='PENDENTE'
    ).select_related('aluno', 'curso')[:5]
    
    # 11. Dados para gráfico de status dos alunos
    status_data = {
        'labels': ['Ativos', 'Inativos'],
        'values': [
            Aluno.objects.filter(status='ATIVO').count(),
            Aluno.objects.filter(status='INATIVO').count()
        ]
    }
    
    # 12. Dados para gráfico de recebimentos (últimos 6 meses)
    meses = []
    valores = []
    for i in range(5, -1, -1):
        data_ref = hoje - timedelta(days=30*i)
        mes_nome = data_ref.strftime('%b/%Y')
        meses.append(mes_nome)
        
        # Exemplo simplificado - ajustar conforme modelo de pagamentos
        total = Fatura.objects.filter(
            status='PAGO',
            updated_at__month=data_ref.month,
            updated_at__year=data_ref.year
        ).aggregate(total=Sum('valor_atual'))['total'] or 0
        
        valores.append(float(total))
    
    recebimentos_data = {
        'labels': meses,
        'values': valores
    }
    
    context = {
        'alunos_ativos': alunos_ativos,
        'novos_alunos': novos_alunos,
        'faturas_vencidas': faturas_vencidas,
        'valor_vencido': valor_vencido,
        'faturas_pendentes': faturas_pendentes,
        'valor_pendente': valor_pendente,
        'pre_matriculas_pendentes': pre_matriculas_pendentes,
        'rematriculas_pendentes': rematriculas_pendentes,
        'faturas_vencidas_lista': faturas_vencidas_lista,
        'pre_matriculas_lista': pre_matriculas_lista,
        'status_data': json.dumps(status_data),
        'recebimentos_data': json.dumps(recebimentos_data),
    }
    
    return render(request, 'dashboard/secretaria_dashboard.html', context)