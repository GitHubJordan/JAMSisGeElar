from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm as DjangoUserChangeForm
from .models import User, Role

class UserCreateForm(UserCreationForm):
    """
    Formulário para criação de usuário (RF-03).
    Inclui campos: username, first_name, last_name, email, role, phone, profile_photo, password1, password2.
    """
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        label='Perfil',
        empty_label=None,
        help_text='Selecione o perfil de acesso.'
    )
    phone = forms.CharField(
        label='Telefone',
        required=False,
        help_text='Formato: +244 XXXXXXXXX'
    )
    profile_photo = forms.ImageField(
        label='Foto de Perfil',
        required=False
    )

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
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'exemplo@dominio.com'}),
        }


class UserEditForm(DjangoUserChangeForm):
    """
    Formulário para edição de usuário (RF-04).
    Não exibe senha nem ask for password.
    """
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        label='Perfil',
        empty_label=None,
        help_text='Selecione o perfil de acesso.'
    )
    phone = forms.CharField(
        label='Telefone',
        required=False,
        help_text='Formato: +244 XXXXXXXXX'
    )
    profile_photo = forms.ImageField(
        label='Foto de Perfil',
        required=False
    )

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
