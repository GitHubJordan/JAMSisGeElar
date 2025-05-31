from django.contrib import admin
from .models import Turma, Disciplina, TurmaDisciplina, Matricula, Nota, Boletim

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nivel', 'turno', 'professor_responsavel')
    list_filter = ('nivel', 'turno')
    search_fields = ('nome', 'professor_responsavel')

@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'carga_horaria')
    search_fields = ('nome',)

@admin.register(TurmaDisciplina)
class TurmaDisciplinaAdmin(admin.ModelAdmin):
    list_display = ('turma', 'disciplina')
    list_filter = ('turma__nivel', 'turma__turno')
    search_fields = ('turma__nome', 'disciplina__nome')

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'turma', 'data_matricula', 'status')
    list_filter = ('status', 'turma__nivel')
    search_fields = ('aluno__nome', 'turma__nome')
    raw_id_fields = ('aluno', 'turma')
    date_hierarchy = 'data_matricula'

@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'disciplina', 'turma', 'media_final', 'situacao')
    list_filter = ('situacao', 'turma__nivel')
    search_fields = ('aluno__nome', 'disciplina__nome')
    raw_id_fields = ('aluno', 'disciplina', 'turma')

@admin.register(Boletim)
class BoletimAdmin(admin.ModelAdmin):
    list_display = ('turma', 'trimestre', 'data_geracao')
    list_filter = ('trimestre', 'turma__nivel')
    search_fields = ('turma__nome',)
    raw_id_fields = ('turma', 'gerado_por')
    date_hierarchy = 'data_geracao'