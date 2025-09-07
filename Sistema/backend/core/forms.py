# Sistema/backend/core/forms.py

from django import forms
from .models import ConfiguracaoInicial

class ConfiguracaoInicialForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoInicial
        fields = [
            'db_host', 'db_port', 'db_name', 'db_user', 'db_password',
            'backup_local_path', 'backup_filename_pattern',
            'smtp_host', 'smtp_port', 'smtp_user',
            'smtp_password', 'whatsapp_api_url', 'whatsapp_api_token',
        ]
        widgets = {
            'db_password': forms.PasswordInput(render_value=True),
            'smtp_password': forms.PasswordInput(render_value=True),
            'backup_local_path': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'backup_path_input'
            }),
        }
        help_texts = {
            'backup_filename_pattern': 'Use padrões de data como %Y (ano), %m (mês), %d (dia), %H (hora), %M (minuto), %S (segundo)',
        }