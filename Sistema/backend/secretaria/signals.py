# Sistema/backend/secretaria/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Fatura, Recibo, ContaCorrente

@receiver(post_save, sender=Fatura)
def atualizar_contacorrente_na_fatura(sender, instance, created, **kwargs):
    """
    Quando uma Fatura é criada ou atualizada, recalcula o saldo da ContaCorrente.
    """
    conta = None
    try:
        conta = instance.aluno.conta_corrente
    except ContaCorrente.DoesNotExist:
        # Se ContaCorrente não existir, cria
        conta = ContaCorrente.objects.create(aluno=instance.aluno)
    conta.recalcular_saldo()

@receiver(post_delete, sender=Fatura)
def remocao_fatura_contacorrente(sender, instance, **kwargs):
    """
    Quando uma fatura é excluída, recalcula o saldo.
    """
    try:
        conta = instance.aluno.conta_corrente
        conta.recalcular_saldo()
    except ContaCorrente.DoesNotExist:
        pass

@receiver(post_save, sender=Recibo)
def atualizar_contacorrente_no_recibo(sender, instance, created, **kwargs):
    """
    Quando um Recibo é criado ou atualizado, recalcula o saldo da ContaCorrente.
    """
    conta = None
    try:
        conta = instance.fatura.aluno.conta_corrente
    except ContaCorrente.DoesNotExist:
        conta = ContaCorrente.objects.create(aluno=instance.fatura.aluno)
    conta.recalcular_saldo()

@receiver(post_delete, sender=Recibo)
def remocao_recibo_contacorrente(sender, instance, **kwargs):
    """
    Quando um Recibo é excluído, recalcula o saldo.
    """
    try:
        conta = instance.fatura.aluno.conta_corrente
        conta.recalcular_saldo()
    except ContaCorrente.DoesNotExist:
        pass
