from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Role

@receiver(post_migrate)
def create_initial_roles(sender, **kwargs):
    if sender.name == 'accounts':
        if not Role.objects.exists():
            Role.objects.create(name="Admin", description="Administrador do sistema")
            Role.objects.create(name="Diretor", description="Acesso total ao sistema")
            Role.objects.create(name="Secretaria", description="Acesso à secretaria")
            Role.objects.create(name="Pedagogico", description="Acesso ao pedagógico")