# Sistema/backend/pedagogico/signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Nota

@receiver(pre_save, sender=Nota)
def calcular_notas_pre_save(sender, instance, **kwargs):
    """
    Antes de salvar (criar ou atualizar) uma Nota, calcula media_parcial, media_final e situacao.
    """
    # Calcula media parcial (simples de N1, N2, N3)
    instance.media_parcial = (instance.nota1 + instance.nota2 + instance.nota3) / 3

    # Para este MVP, usamos peso=1,1,1 → média simples; ajustável se desejado.
    soma_pesos = 3
    instance.media_final = (instance.nota1 + instance.nota2 + instance.nota3) / soma_pesos
    instance.situacao = 'APROVADO' if instance.media_final >= 60 else 'REPROVADO'
