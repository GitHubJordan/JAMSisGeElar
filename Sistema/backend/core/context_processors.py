# core/context_processors.py
from core.models import Exercicio

def exercicio_atual(request):
    ex = Exercicio.objects.select_related('ano').filter(encerrado_em__isnull=True).first()
    anos = [e.ano for e in Exercicio.objects.select_related('ano').order_by('-iniciado_em')]
    return {
        'exercicio_atual': ex,
        'ano_letivo_ativo': ex.ano if ex else None,
        'anos_disponiveis': anos,
    }
