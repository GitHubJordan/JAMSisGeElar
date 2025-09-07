from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm as DjangoUserChangeForm
from .models import User, Role

class UserCreateForm(UserCreationForm):
    """
    Formulário para criação de usuário (RF-03).
    Inclui campos: username, first_name, last_name, email, role, phone, profile_photo, password1, password2.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remover textos de ajuda desnecessários
        self.fields['username'].help_text = None
        self.fields['phone'].help_text = None
        self.fields['role'].help_text = None
        self.fields['is_active'].help_text = "Indica se este usuário deve ser tratado como ativo."
        
        # Adicionar placeholders
        self.fields['username'].widget.attrs['placeholder'] = 'Nome de usuário único'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Primeiro nome'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Último nome'
        self.fields['email'].widget.attrs['placeholder'] = 'exemplo@dominio.com'
        self.fields['phone'].widget.attrs['placeholder'] = '+244 900 000 000'
        self.fields['password1'].widget.attrs['placeholder'] = 'Senha segura'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirme a senha'
        
        # Simplificar mensagens de senha
        self.fields['password1'].help_text = "Mínimo 8 caracteres, não totalmente numérica"
        self.fields['password2'].help_text = None

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        if role and role.name == 'Admin':
            # Verifica se já existe um usuário ativo com role 'Admin'
            from .models import User
            existing_admin = User.objects.filter(role__name='Admin', is_active=True).exists()
            # Se existe e não estamos editando um Admin (pois em criação, não temos self.instance.pk)
            if existing_admin:
                raise forms.ValidationError(
                    "Já existe um usuário Admin ativo. Não é permitido ter mais de um Admin."
                )
        return cleaned_data

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
            'phone',
            'profile_photo',
            'password1',
            'password2',
            'is_active',
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'exemplo@dominio.com'}),
        }


class UserEditForm(DjangoUserChangeForm):
    """
    Formulário para edição de usuário (RF-04).
    Não exibe senha nem ask for password.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remover textos de ajuda
        self.fields['phone'].help_text = None
        self.fields['role'].help_text = None
        self.fields['is_active'].help_text = "Indica se este usuário deve ser tratado como ativo. Desmarque esta opção em vez de excluir contas."
        
        # Adicionar placeholders
        self.fields['first_name'].widget.attrs['placeholder'] = 'Primeiro nome'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Último nome'
        self.fields['email'].widget.attrs['placeholder'] = 'exemplo@dominio.com'
        self.fields['phone'].widget.attrs['placeholder'] = '+244 900 000 000'

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        if role and role.name == 'Admin':
            from .models import User
            # Se estivermos editando, self.instance é o usuário sendo editado
            # Verifica se existe outro Admin ativo diferente dele
            qs = User.objects.filter(role__name='Admin', is_active=True).exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Já existe outro usuário Admin ativo. Só um Admin é permitido.")
        return cleaned_data

    class Meta:
        model = User
        fields = [
            'username',       # Só leitura no template, não editável
            'first_name',
            'last_name',
            'email',
            'role',
            'phone',
            'profile_photo',
            'is_active',
        ]
        widgets = {
            'username': forms.TextInput(attrs={'readonly': 'readonly'}),
        }
