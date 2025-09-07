from django.shortcuts import get_object_or_404
from core.models import Exercicio
from pedagogico.models import AnoLetivo

class AnoContextMixin:
    def get_ano(self):
        ano_id = self.request.session.get('ano_selecionado')
        if ano_id:
            return get_object_or_404(AnoLetivo, pk=ano_id)
        ex = Exercicio.objects.filter(encerrado_em__isnull=True).select_related('ano').first()
        return ex.ano if ex else None

    def get_queryset(self):
        ano = self.get_ano()
        qs = super().get_queryset()
        return qs.filter(ano_letivo=ano) if ano else qs.none()

    def form_valid(self, form):
        ano = self.get_ano()
        if ano and hasattr(form.instance, 'ano_letivo'):
            form.instance.ano_letivo = ano
        return super().form_valid(form)
