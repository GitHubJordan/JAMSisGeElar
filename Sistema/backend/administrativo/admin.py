from django.contrib import admin
from .models import Colaborador, Salario, BemPatrimonio, LancamentoContabil

@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cargo', 'departamento', 'status')
    list_filter = ('departamento', 'status')
    search_fields = ('nome', 'documento')

@admin.register(Salario)
class SalarioAdmin(admin.ModelAdmin):
    list_display = ('colaborador', 'mes_referencia', 'salario_liquido')
    list_filter = ('mes_referencia',)
    search_fields = ('colaborador__nome',)
    raw_id_fields = ('colaborador', 'processado_por')
    date_hierarchy = 'mes_referencia'

@admin.register(BemPatrimonio)
class BemPatrimonioAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'categoria', 'valor_contabil_liquido')
    list_filter = ('categoria',)
    search_fields = ('descricao', 'localizacao')

@admin.register(LancamentoContabil)
class LancamentoContabilAdmin(admin.ModelAdmin):
    list_display = ('data_lancamento', 'conta_debito', 'conta_credito', 'valor')
    search_fields = ('descricao', 'conta_debito', 'conta_credito')
    date_hierarchy = 'data_lancamento'
    raw_id_fields = ('lancado_por',)