from django.db import models
from django.contrib.auth.models import AbstractUser

class Role(models.Model):
    """
    Perfil de acesso (Admin, Diretor, Subdiretor, Secretário).
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Extensão do modelo padrão de usuário do Django, adicionando campo 'role'.
    """
    role = models.ForeignKey(
        Role, 
        on_delete=models.PROTECT,
        related_name='users',
        verbose_name='Perfil'
    )
    phone = models.CharField(
        'Telefone',
        max_length=20,
        blank=True,
        help_text='Formato: +244 XXXXXXXXX'
    )
    profile_photo = models.ImageField(
        'Foto de Perfil',
        upload_to='users/photos/',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f'{self.username} ({self.get_full_name()})'
