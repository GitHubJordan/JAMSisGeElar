from django import forms
from .models import Colaborador, Salario, BemPatrimonio, LancamentoContabil
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class ColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = [
            'nome',
            'documento',
            'cargo',
            'departamento',
            'data_admissao',
            'salario_base',
            'telefone',
            'email',
            'status',
        ]
        widgets = {
            'data_admissao': forms.DateInput(attrs={'type': 'date'}),
            'salario_base': forms.NumberInput(attrs={'step': '0.01', 'min': 0}),
            'telefone': forms.TextInput(attrs={'placeholder': '(+244) 9XXXXXXXX'}),
            'email': forms.EmailInput(attrs={'placeholder': 'exemplo@dominio.com'}),
        }

    def clean_documento(self):
        documento = self.cleaned_data.get('documento')
        if Colaborador.objects.filter(documento=documento).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Já existe um colaborador com este documento.")
        return documento


class SalarioForm(forms.ModelForm):
    class Meta:
        model = Salario
        fields = [
            'colaborador',
            'mes_referencia',
            'horas_extras',
            'descontos',
            'bonificacoes',
        ]
        widgets = {
            'colaborador': forms.Select(),
            'mes_referencia': forms.DateInput(attrs={'type': 'month'}),  # mostra apenas mês/ano
            'horas_extras': forms.NumberInput(attrs={'step': '0.01', 'min': 0}),
            'descontos': forms.NumberInput(attrs={'step': '0.01', 'min': 0}),
            'bonificacoes': forms.NumberInput(attrs={'step': '0.01', 'min': 0}),
        }

    def clean(self):
        cleaned = super().clean()
        colaborador = cleaned.get('colaborador')
        mes = cleaned.get('mes_referencia')
        # Verifica se já existe registro para esse colaborador e mês
        if colaborador and mes:
            qs = Salario.objects.filter(colaborador=colaborador, mes_referencia=mes)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Já existe um salário processado para este colaborador neste mês.")
        return cleaned


class BemPatrimonioForm(forms.ModelForm):
    class Meta:
        model = BemPatrimonio
        fields = [
            'descricao',
            'categoria',
            'valor_aquisicao',
            'data_aquisicao',
            'vida_util_anos',
            'localizacao',
            'arquivo_documento',
        ]
        widgets = {
            'descricao': forms.TextInput(attrs={'placeholder': 'Ex.: Computador Dell'}),
            'data_aquisicao': forms.DateInput(attrs={'type': 'date'}),
            'valor_aquisicao': forms.NumberInput(attrs={'step': '0.01', 'min': 0}),
            'vida_util_anos': forms.NumberInput(attrs={'min': 1}),
            'localizacao': forms.TextInput(attrs={'placeholder': 'Ex.: Sala 101'}),
        }


class LancamentoContabilForm(forms.ModelForm):
    class Meta:
        model = LancamentoContabil
        fields = [
            'data_lancamento',
            'conta_debito',
            'conta_credito',
            'valor',
            'descricao',
        ]
        widgets = {
            'data_lancamento': forms.DateInput(attrs={'type': 'date'}),
            'conta_debito': forms.TextInput(attrs={'placeholder': 'Conta Débito'}),
            'conta_credito': forms.TextInput(attrs={'placeholder': 'Conta Crédito'}),
            'valor': forms.NumberInput(attrs={'step': '0.01', 'min': 0}),
            'descricao': forms.Textarea(attrs={'rows': 2}),
        }

    def clean(self):
        cleaned = super().clean()
        conta_debito = cleaned.get('conta_debito')
        conta_credito = cleaned.get('conta_credito')
        if conta_debito == conta_credito:
            raise ValidationError("Conta Débito e Conta Crédito não podem ser iguais.")
        return cleaned
