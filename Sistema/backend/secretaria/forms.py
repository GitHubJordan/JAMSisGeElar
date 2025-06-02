from django import forms
from .models import Encarregado, Aluno, Fatura
from django.core.exceptions import ValidationError
from datetime import datetime

class EncarregadoForm(forms.ModelForm):
    """
    Formulário para CRUD de Encarregado (RF-09 a RF-12).
    """
    class Meta:
        model = Encarregado
        fields = [
            'nome',
            'telefone',
            'email',
            'endereco',
            'grau_parentesco',
            'is_active',
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome completo do responsável'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(+244) 9XXXXXXXX'}),
            'email': forms.EmailInput(attrs={'placeholder': 'exemplo@dominio.com'}),
            'endereco': forms.Textarea(attrs={'rows': 2}),
        }


class AlunoForm(forms.ModelForm):
    """
    Formulário para CRUD de Aluno (RF-13 a RF-16).
    Inclui abas de Dados Pessoais, Dados do Encarregado, Documentos e Observações.
    """
    # Para upload de documentos extras, podemos usar campos opcionais
    comprovante_residencia = forms.FileField(
        label='Comprovante de Residência',
        required=False
    )
    historico_escolar = forms.FileField(
        label='Histórico Escolar',
        required=False
    )
    outros_documentos = forms.FileField(
        label='Outros Documentos',
        required=False
    )

    class Meta:
        model = Aluno
        fields = [
            'nome',
            'data_nascimento',
            'genero',
            'endereco',
            'documento',
            'foto',
            'encarregado',
            'observacoes',
        ]
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'genero': forms.Select(),
            'documento': forms.TextInput(attrs={'placeholder': 'RG/BI'}),
            'endereco': forms.Textarea(attrs={'rows': 2}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_documento(self):
        documento = self.cleaned_data.get('documento')
        if Aluno.objects.filter(documento=documento).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Já existe um aluno com este documento cadastrado.")
        return documento


class FaturaForm(forms.ModelForm):
    """
    Formulário para CRUD de Fatura (RF-17 a RF-21).
    """
    class Meta:
        model = Fatura
        fields = [
            'numero',
            'aluno',
            'tipo',
            'valor_original',
            'valor_atual',
            'data_emissao',
            'data_vencimento',
            'status',
            'observacoes',
        ]
        widgets = {
            'data_emissao': forms.DateInput(attrs={'type': 'date'}),
            'data_vencimento': forms.DateInput(attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
            'numero': forms.TextInput(attrs={'readonly': 'readonly'}),  # será gerado automaticamente
            'valor_atual': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def clean(self):
        cleaned = super().clean()
        data_emissao = cleaned.get('data_emissao')
        data_vencimento = cleaned.get('data_vencimento')
        if data_vencimento and data_emissao and data_vencimento < data_emissao:
            raise ValidationError("A data de vencimento não pode ser anterior à data de emissão.")
        return cleaned
