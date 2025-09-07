from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Atividade(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    descricao = models.CharField(max_length=200)
    modulo = models.CharField(max_length=50)  # Ex: 'Secretaria', 'Pedagógico'
    data = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-data']
        verbose_name = 'Atividade'
        verbose_name_plural = 'Atividades'
    
    def __str__(self):
        return f"{self.modulo} - {self.descricao}"