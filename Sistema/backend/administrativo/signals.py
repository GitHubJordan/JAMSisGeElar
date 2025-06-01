from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import BemPatrimonio
from datetime import date

@receiver(pre_save, sender=BemPatrimonio)
def atualizar_depreciacao_pre_save(sender, instance, **kwargs):
    """
    Antes de salvar BemPatrimonio, atualiza depreciação com base na data de referência atual.
    """
    # Se o objeto estiver sendo criado (instance.pk is None), ou atualizado, pode chamar calcular_depreciacao
    # Precisamos salvar primeiro para garantir que data_aquisicao e vida_util_anos existam.
    # Então, calculamos usando a data de hoje:
    instance.calcular_depreciacao(data_referencia=date.today())
