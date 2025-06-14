# Sistema/backend/pedagogico/forms.py

from django import forms
from .models import Turma, Disciplina, TurmaDisciplina, Matricula, Nota, AnoLetivo, Calendario

class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = ['nome', 'nivel', 'turno', 'professor_responsavel', 'ano_letivo']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex.: 10º Ano A'}),
            'professor_responsavel': forms.TextInput(attrs={'placeholder': 'Nome do professor'}),
            'ano_letivo': forms.Select(),
        }


class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ['nome', 'carga_horaria', 'professor_responsavel']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex.: Matemática'}),
            'carga_horaria': forms.NumberInput(attrs={'min': 0}),
            'professor_responsavel': forms.TextInput(attrs={'placeholder': 'Nome do professor'}),
        }


class TurmaDisciplinaForm(forms.ModelForm):
    class Meta:
        model = TurmaDisciplina
        fields = ['turma', 'disciplina']
        widgets = {
            'turma': forms.Select(),
            'disciplina': forms.Select(),
        }

    def clean(self):
        cleaned = super().clean()
        turma = cleaned.get('turma')
        disciplina = cleaned.get('disciplina')
        # O unique_together já previne duplicata, mas podemos validar legibilidade:
        if TurmaDisciplina.objects.filter(turma=turma, disciplina=disciplina).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Esta Disciplina já está associada a esta Turma.")
        return cleaned


class MatriculaForm(forms.ModelForm):
    class Meta:
        model = Matricula
        fields = ['aluno', 'turma', 'data_matricula', 'status', 'ano_letivo']
        widgets = {
            'aluno': forms.Select(),
            'turma': forms.Select(),
            'data_matricula': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(),
            'ano_letivo': forms.Select(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ativo = AnoLetivo.objects.filter(ativo=True).first()
        self.fields['ano_letivo'].queryset = AnoLetivo.objects.filter(pk=ativo.pk) if ativo else AnoLetivo.objects.none()
        self.fields['ano_letivo'].initial = ativo

    def clean(self):
        cleaned = super().clean()
        aluno = cleaned.get('aluno')
        turma = cleaned.get('turma')
        # Evita matrícula duplicada:
        if Matricula.objects.filter(aluno=aluno, turma=turma).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este aluno já está matriculado nesta turma.")
        return cleaned


class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['aluno', 'turma', 'disciplina', 'nota1', 'nota2', 'nota3', 'ano_letivo']
        widgets = {
            'aluno': forms.Select(),
            'turma': forms.Select(),
            'disciplina': forms.Select(),
            'nota1': forms.NumberInput(attrs={'step': '0.01', 'min': 0, 'max': 20}),
            'nota2': forms.NumberInput(attrs={'step': '0.01', 'min': 0, 'max': 20}),
            'nota3': forms.NumberInput(attrs={'step': '0.01', 'min': 0, 'max': 20}),
            'ano_letivo': forms.Select(attrs={'readonly':'readonly'}),
        }

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        ativo = AnoLetivo.objects.filter(ativo=True).first()
        self.fields['ano_letivo'].queryset = AnoLetivo.objects.filter(pk=ativo.pk) if ativo else AnoLetivo.objects.none()
        self.fields['ano_letivo'].initial = ativo

    def clean(self):
        cleaned = super().clean()
        aluno = cleaned.get('aluno')
        turma = cleaned.get('turma')
        disciplina = cleaned.get('disciplina')
        # Verifica unicidade de Nota para tupla (aluno, turma, disciplina)
        if Nota.objects.filter(aluno=aluno, turma=turma, disciplina=disciplina).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Já existe uma nota cadastrada para este Aluno/Turma/Disciplina.")
        return cleaned


class AnoLetivoForm(forms.ModelForm):
    class Meta:
        model = AnoLetivo
        fields = ['nome', 'data_inicio', 'data_fim', 'ativo']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned = super().clean()
        # As validações de datas e ano ativo já estão em clean() do model
        return cleaned


class CalendarioForm(forms.ModelForm):
    class Meta:
        model = Calendario
        fields = ['ano_letivo', 'titulo', 'data', 'descricao']
        widgets = {
            'ano_letivo': forms.Select(),
            'data': forms.DateInput(attrs={'type': 'date'}),
            'descricao': forms.Textarea(attrs={'rows': 2}),
        }

    def clean(self):
        cleaned = super().clean()
        return cleaned
