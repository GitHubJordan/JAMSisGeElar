from datetime import datetime
from django.core.management.base import BaseCommand
from secretaria.models import Fatura
from core.utils import send_email, send_whatsapp

class Command(BaseCommand):
    help = 'Envia notificações para Faturas vencidas'

    def handle(self, *args, **options):
        pendentes = Fatura.objects.filter(status__in=['PENDENTE','VENCIDO'], data_vencimento__lt=datetime.date.today())
        agrup = {}
        for f in pendentes:
            encarregado = f.aluno.encarregado
            agrup.setdefault(encarregado, []).append(f)
        for enc, faturas in agrup.items():
            subject = f"Cobrança de {len(faturas)} fatura(s) pendente(s)"
            body = "\n".join([f"- {f.numero}: AOA{f.valor_atual}" for f in faturas])
            sent_email = send_email(enc.email, subject, body)
            sent_whats = send_whatsapp(enc.telefone, body)
            self.stdout.write(self.style.SUCCESS(
                f"Enviado para {enc.nome}: email={sent_email} whatsapp={sent_whats}"
            ))
