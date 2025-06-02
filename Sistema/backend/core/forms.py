# Sistema/backend/core/forms.py

from django import forms
from .models import ConfiguracaoInicial

class ConfiguracaoInicialForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoInicial
        fields = [
            'db_host', 'db_port', 'db_name', 'db_user', 'db_password',
            'backup_local_path', 'smtp_host', 'smtp_port', 'smtp_user',
            'smtp_password', 'whatsapp_api_url', 'whatsapp_api_token',
        ]
        widgets = {
            'db_password': forms.PasswordInput(render_value=True),
            'smtp_password': forms.PasswordInput(render_value=True),
        }
