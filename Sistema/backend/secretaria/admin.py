from django.contrib import admin
from .models import Encarregado, Aluno, Fatura, Recibo, ContaCorrente

@admin.register(Encarregado)
class EncarregadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'grau_parentesco', 'is_active')
    list_filter = ('is_active', 'grau_parentesco')
    search_fields = ('nome', 'telefone', 'email')

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'nome', 'status', 'encarregado')
    list_filter = ('status', 'genero')
    search_fields = ('nome', 'matricula', 'documento')
    raw_id_fields = ('encarregado',)

@admin.register(Fatura)
class FaturaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'aluno', 'tipo', 'valor_atual', 'status', 'data_vencimento')
    list_filter = ('tipo', 'status')
    search_fields = ('numero', 'aluno__nome')
    raw_id_fields = ('aluno',)
    date_hierarchy = 'data_emissao'

@admin.register(Recibo)
class ReciboAdmin(admin.ModelAdmin):
    list_display = ('numero_recibo', 'fatura', 'data_pagamento', 'forma_pagamento', 'valor_pago')
    search_fields = ('numero_recibo', 'fatura__numero')
    raw_id_fields = ('fatura',)
    date_hierarchy = 'data_pagamento'

@admin.register(ContaCorrente)
class ContaCorrenteAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'total_debito', 'total_credito', 'saldo')
    search_fields = ('aluno__matricula', 'aluno__nome')
    raw_id_fields = ('aluno',)