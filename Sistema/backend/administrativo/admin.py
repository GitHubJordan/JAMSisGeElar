from django.contrib import admin
from .models import Colaborador, ContaContabil, Salario, BemPatrimonio, LancamentoContabil

@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cargo', 'departamento', 'status')
    list_filter = ('departamento', 'status')
    search_fields = ('nome', 'documento')

@admin.register(Salario)
class SalarioAdmin(admin.ModelAdmin):
    list_display = ('colaborador', 'get_mes_formatado', 'salario_liquido')
    list_filter = ('mes_referencia',)
    search_fields = ('colaborador__nome',)
    raw_id_fields = ('colaborador', 'processado_por')
    date_hierarchy = 'data_referencia'  # Use o novo campo


    def get_mes_formatado(self, obj):
        return obj.mes_formatado()
    get_mes_formatado.short_description = 'Mês Referência'

@admin.register(BemPatrimonio)
class BemPatrimonioAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'categoria', 'valor_contabil_liquido')
    list_filter = ('categoria',)
    search_fields = ('descricao', 'localizacao')

@admin.register(ContaContabil)
class ContaContabilAdmin(admin.ModelAdmin):
    list_display = ('codigo','nome', 'tipo', 'posicao')
    search_fields = ('codigo','nome')
    ordering = ('codigo',)

@admin.register(LancamentoContabil)
class LancamentoContabilAdmin(admin.ModelAdmin):
    list_display = ('data_lancamento',
                    'get_conta_debito','get_conta_credito','valor')
    search_fields = ('descricao', 'conta_debito', 'conta_credito')
    date_hierarchy = 'data_lancamento'
    raw_id_fields = ('lancado_por',)

    def get_conta_debito(self, obj):
        return obj.conta_debito.codigo + ' – ' + obj.conta_debito.nome
    get_conta_debito.short_description = 'Conta Débito'

    def get_conta_credito(self, obj):
        return obj.conta_credito.codigo + ' – ' + obj.conta_credito.nome
    get_conta_credito.short_description = 'Conta Crédito'