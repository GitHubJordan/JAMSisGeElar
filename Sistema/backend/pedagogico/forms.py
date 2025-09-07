# Sistema/backend/pedagogico/forms.py

from django import forms
from django.forms import HiddenInput
from django.core.exceptions import ValidationError
from .models import PreRematricula, Turma, Disciplina, TurmaDisciplina, Matricula, Nota, AnoLetivo, Calendario, Curso
from administrativo.models import Colaborador


class TurmaForm(forms.ModelForm):
    professor_responsavel = forms.ModelChoiceField(
        queryset=(
            Colaborador.objects.filter(cargo__iexact='Professor') |
            Colaborador.objects.filter(cargo__iexact='Professora')
        ),
        label='Professor Responsável',
        empty_label='(selecione um professor)'
    )

    class Meta:
        model = Turma
        fields = ['nome', 'nivel', 'turno', 'professor_responsavel', 'curso', 'ano_letivo']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex.: 10º Ano A'}),
            'ano_letivo': HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # só cursos ativos
        self.fields['curso'].queryset = Curso.objects.filter(ativo=True)
        self.fields['curso'].empty_label = '(selecione um curso)'
        # ano letivo ativo
        ativo = AnoLetivo.objects.filter(ativo=True).first()
        if ativo:
            self.fields['ano_letivo'].queryset = AnoLetivo.objects.filter(pk=ativo.pk)
            self.fields['ano_letivo'].initial = ativo
        else:
            self.fields['ano_letivo'].queryset = AnoLetivo.objects.none()


class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ['nome', 'carga_horaria']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex.: Matemática'}),
            'carga_horaria': forms.NumberInput(attrs={'min': 0}),
        }


class TurmaDisciplinaForm(forms.ModelForm):
    professor_responsavel = forms.ModelChoiceField(
        queryset=Colaborador.objects.filter(cargo__iexact='Professor') | Colaborador.objects.filter(cargo__iexact='Professora') | Colaborador.objects.filter(cargo__iexact='professor') | Colaborador.objects.filter(cargo__iexact='professora'),
        label='Professor Responsável',
        empty_label='(selecione um professor)'
    )

    class Meta:
        model = TurmaDisciplina
        fields = ['turma', 'disciplina', 'professor_responsavel', 'ano_letivo']
        widgets = {
            'turma': forms.Select(),
            'disciplina': forms.Select(),
            'ano_letivo': HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ativo = AnoLetivo.objects.filter(ativo=True).first()
        if ativo:
            self.fields['ano_letivo'].queryset = AnoLetivo.objects.filter(pk=ativo.pk)
            self.fields['ano_letivo'].initial = ativo
        else:
            self.fields['ano_letivo'].queryset = AnoLetivo.objects.none()

    def clean(self):
        cleaned = super().clean()
        turma = cleaned.get('turma')
        disciplina = cleaned.get('disciplina')
        if TurmaDisciplina.objects.filter(turma=turma, disciplina=disciplina).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Esta Disciplina já está associada a esta Turma.")
        return cleaned

class MatriculaForm(forms.ModelForm):
    turma = forms.ModelChoiceField(
        queryset=Turma.objects.none(),  # preenchido no __init__
        label='Turma',
        empty_label='(selecione uma turma)'
    )

    class Meta:
        model = Matricula
        fields = ['aluno', 'turma', 'data_matricula', 'status', 'ano_letivo']
        widgets = {
            'data_matricula': forms.DateInput(attrs={'type': 'date'}),
            'ano_letivo': HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ativo = AnoLetivo.objects.filter(ativo=True).first()
        if ativo:
            self.fields['ano_letivo'].queryset = AnoLetivo.objects.filter(pk=ativo.pk)
            self.fields['ano_letivo'].initial = ativo
            # turmas só do ano letivo ativo
            self.fields['turma'].queryset = Turma.objects.filter(ano_letivo=ativo)
        else:
            self.fields['ano_letivo'].queryset = AnoLetivo.objects.none()
            self.fields['turma'].queryset = Turma.objects.none()

    def clean(self):
        cleaned = super().clean()
        aluno = cleaned.get('aluno')
        turma = cleaned.get('turma')
        ano   = cleaned.get('ano_letivo')

        # 1) evita duplicata aluno+turma
        if aluno and turma:
            qs = Matricula.objects.filter(aluno=aluno, turma=turma)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Este aluno já está matriculado nesta turma.")

        # 2) evita aluno em 2 turmas no mesmo ano
        if aluno and ano:
            qs2 = Matricula.objects.filter(aluno=aluno, ano_letivo=ano)
            if self.instance.pk:
                qs2 = qs2.exclude(pk=self.instance.pk)
            if qs2.exists():
                raise ValidationError(
                    "Este aluno já possui matrícula em outra turma neste ano letivo."
                )

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
            'ano_letivo': HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ativo = AnoLetivo.objects.filter(ativo=True).first()
        if ativo:
            self.fields['ano_letivo'].queryset = AnoLetivo.objects.filter(pk=ativo.pk)
            self.fields['ano_letivo'].initial = ativo
        else:
            self.fields['ano_letivo'].queryset = AnoLetivo.objects.none()

    def clean(self):
        cleaned = super().clean()
        aluno      = cleaned.get('aluno')
        turma      = cleaned.get('turma')
        disciplina = cleaned.get('disciplina')

        # 1) Verifica unicidade como antes
        if aluno and turma and disciplina:
            qs = Nota.objects.filter(aluno=aluno, turma=turma, disciplina=disciplina)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Já existe uma nota cadastrada para este Aluno/Turma/Disciplina.")

        # 2) Nova validação: turma deve ter essa disciplina
        if turma and disciplina:
            if not TurmaDisciplina.objects.filter(turma=turma, disciplina=disciplina).exists():
                raise ValidationError(
                    "A disciplina “%s” não está associada à turma “%s”. "
                    "Verifique as associações antes de lançar notas."
                    % (disciplina.nome, turma.nome)
                )

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

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['codigo', 'nome', 'descricao', 'ativo']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows':2}),
        }
    

class PreRematriculaForm(forms.ModelForm):
    class Meta:
        model = PreRematricula
        fields = ['aluno', 'turma_origem', 'curso_origem', 'ano_origem']
        widgets = {
            'ano_origem': forms.HiddenInput(),
            'curso_origem': forms.HiddenInput(),
            'turma_origem': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ano corrente
        ano = AnoLetivo.objects.filter(ativo=True).first()
        if ano and self.instance.pk is None:
            self.fields['ano_origem'].initial   = ano
        # turma e curso podem ser populados na view
        self.fields['aluno'].queryset    = self.fields['aluno'].queryset.filter(status='ATIVO')
