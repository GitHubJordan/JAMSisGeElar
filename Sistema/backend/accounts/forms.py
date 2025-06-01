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
