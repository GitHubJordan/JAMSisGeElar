# Sistema/backend/secretaria/views.py
from datetime import datetime, timedelta
from django.utils import timezone
from pyexpat.errors import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from pedagogico.models import PreRematricula
from .models import Encarregado, Aluno, Fatura, ContaCorrente, Servico, PreMatricula
from .forms import EncarregadoForm, AlunoForm, FaturaForm, PreRematriculaForm, ServicoForm, FaturaServicoFormset, PreMatriculaForm

import pandas as pd
from io import BytesIO
from django.core.paginator import Paginator
from django.db.models import Q

# Decorator para checar roles (pode usar o mesmo role_required do accounts)
from accounts.decorators import role_required

ENCARREGADO_FORM_FIELDS = [
    'nome', 'telefone', 'email', 'endereco',
    'grau_parentesco', 'is_active'
]

@login_required
@role_required('Admin', 'Diretor', 'Secretaria')
def usuario_redirect_secretaria(request):
    """
    Redireciona automaticamente para o dashboard de secretaria.
    """
    return redirect('dashboard:secretaria-dashboard')

# ------------------------------
# CRUD de Encarregado (RF-09 a RF-12)
# ------------------------------

@method_decorator(role_required('Admin', 'Diretor', 'Secretaria'), name='dispatch')
class EncarregadoListView(LoginRequiredMixin, ListView):
    model = Encarregado
    template_name = 'secretaria/encarregado_list.html'
    context_object_name = 'encarregados'
    paginate_by = 20
    ordering = ['nome']


@method_decorator(role_required('Admin', 'Diretor', 'Secretaria'), name='dispatch')
class EncarregadoCreateView(LoginRequiredMixin, CreateView):
    model = Encarregado
    form_class = EncarregadoForm
    template_name = 'secretaria/encarregado_form.html'
    success_url = reverse_lazy('secretaria:encarregado-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_fields'] = ENCARREGADO_FORM_FIELDS
        return context


@method_decorator(role_required('Admin', 'Diretor', 'Secretaria'), name='dispatch')
class EncarregadoUpdateView(LoginRequiredMixin, UpdateView):
    model = Encarregado
    form_class = EncarregadoForm
    template_name = 'secretaria/encarregado_form.html'
    success_url = reverse_lazy('secretaria:encarregado-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_fields'] = ENCARREGADO_FORM_FIELDS
        return context

@method_decorator(role_required('Admin', 'Diretor', 'Secretaria'), name='dispatch')
class EncarregadoDeleteView(LoginRequiredMixin, DeleteView):
    model = Encarregado
    template_name = 'secretaria/encarregado_confirm_delete.html'
    success_url = reverse_lazy('secretaria:encarregado-list')


# ------------------------------
# CRUD de Aluno (RF-13 a RF-16)
# ------------------------------

@method_decorator(role_required('Admin', 'Diretor', 'Secretaria'), name='dispatch')
class AlunoListView(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'secretaria/aluno_list.html'
    context_object_name = 'alunos'
    paginate_by = 20
    ordering = ['matricula']

@method_decorator(role_required('Admin', 'Diretor', 'Secretaria'), name='dispatch')
class AlunoCreateView(LoginRequiredMixin, CreateView):
    model = Aluno
    form_class = AlunoForm
    template_name = 'secretaria/aluno_form.html'
    success_url = reverse_lazy('secretaria:aluno-list')

    def get_context_data(self, **kwargs):
        """Adiciona as abas ao contexto para o template."""
        context = super().get_context_data(**kwargs)
        context['tabs'] = [
            ('dadospessoais', 'Dados Pessoais'),
            ('dadosencarregado', 'Encarregado'),
            ('documentos', 'Documentos'),
            ('observacoes', 'Observações'),
        ]
        return context

    def form_valid(self, form):
        # Gera matrícula automaticamente: AnoEmissão + ID sequencial (ex.: “20250001”)
        from datetime import date
        ano = date.today().year
        ultimo = Aluno.objects.filter(matricula__startswith=str(ano)).order_by('-matricula').first()
        if ultimo:
            seq = int(ultimo.matricula[-4:]) + 1
        else:
            seq = 1
        form.instance.matricula = f"{ano}{seq:04d}"

        # Ainda que foto e documentos sejam opcionais, salvamos a instância
        return super().form_valid(form)


@method_decorator(role_required('Admin', 'Diretor', 'Secretaria'), name='dispatch')
class AlunoUpdateView(LoginRequiredMixin, UpdateView):
    model = Aluno
    form_class = AlunoForm
    template_name = 'secretaria/aluno_form.html'
    success_url = reverse_lazy('secretaria:aluno-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tabs'] = [
            ('dadospessoais', 'Dados Pessoais'),
            ('dadosencarregado', 'Encarregado'),
            ('documentos', 'Documentos'),
            ('observacoes', 'Observações'),
        ]
        return context


@method_decorator(role_required('Admin', 'Diretor', 'Secretaria'), name='dispatch')
class AlunoDeleteView(LoginRequiredMixin, DeleteView):
    model = Aluno
    template_name = 'secretaria/aluno_confirm_delete.html'
    success_url = reverse_lazy('secretaria:aluno-list')


# ------------------------------
# CRUD de Fatura (RF-17 a RF-21)
# ------------------------------

@method_decorator(role_required('Admin', 'Diretor', 'Secretaria'), name='dispatch')
class FaturaListView(LoginRequiredMixin, ListView):
    model = Fatura
    template_name = 'secretaria/fatura_list.html'
    context_object_name = 'faturas'
    paginate_by = 20
    ordering = ['-data_emissao']

    def get_queryset(self):
        hoje = timezone.localdate()
        Fatura.objects.filter(
            data_vencimento__lt=hoje,
            status='PENDENTE'
        ).update(status='VENCIDO')

        qs = super().get_queryset().select_related('aluno')
        # Filtro opcional por status ou aluno (poderá ser adicionado via GET)
        status = self.request.GET.get('status')
        aluno = self.request.GET.get('aluno')
        if status:
            qs = qs.filter(status=status)
        if aluno:
            qs = qs.filter(aluno__nome__icontains=aluno)
        return qs
    
    
@method_decorator(role_required('Admin', 'Diretor', 'Secretaria'), name='dispatch')
class FaturaCreateView(LoginRequiredMixin, CreateView):
    model = Fatura
    form_class = FaturaForm
    template_name = 'secretaria/fatura_form.html'
    success_url = reverse_lazy('secretaria:fatura-list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['servico_formset'] = FaturaServicoFormset(
            self.request.POST or None,
            instance=self.object
        )
        ctx['servicos_ativos'] = Servico.objects.filter(ativo=True)
        return ctx

    def form_valid(self, form):
        # Geração automática de número
        from datetime import date
        ano = date.today().year
        ultimo = Fatura.objects.filter(numero__startswith=str(ano))\
                                .order_by('-numero').first()
        seq = (int(ultimo.numero.split('/')[-1]) + 1) \
              if (ultimo and ultimo.numero.split('/')[-1].isdigit()) else 1
        form.instance.numero = f"{ano}/{seq:04d}"

        # Salva fields comuns (aluno, tipo, datas, status, observações...)
        self.object = form.save(commit=False)

        # RAMO 1: TIPO FIXO (não 'OUTRO') → usa valor_original do form
        if form.instance.tipo != 'OUTRO':
            self.object.valor_atual = form.cleaned_data['valor_original']
            self.object.save()
            return redirect(self.get_success_url())

        # RAMO 2: TIPO 'OUTRO' → processa formset de serviços
        self.object.save()
        formset = FaturaServicoFormset(self.request.POST, instance=self.object)
        if formset.is_valid():
            total = sum(item.servico.preco * item.quantidade for item in formset.save(commit=False))
            form.instance.valor_original = total
            form.instance.valor_atual    = total
            self.object.save()
            formset.save_m2m()
            return redirect(self.get_success_url())
        return self.form_invalid(form)


@method_decorator(role_required('Admin', 'Diretor', 'Secretaria'), name='dispatch')
class FaturaUpdateView(LoginRequiredMixin, UpdateView):
    model = Fatura
    form_class = FaturaForm
    template_name = 'secretaria/fatura_form.html'
    success_url = reverse_lazy('secretaria:fatura-list')

    def dispatch(self, request, *args, **kwargs):
        f = self.get_object()
        if f.status == 'PAGO':
            raise PermissionDenied("Não é possível editar uma fatura já paga.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['servico_formset'] = FaturaServicoFormset(
            self.request.POST or None,
            instance=self.object
        )
        ctx['servicos_ativos'] = Servico.objects.filter(ativo=True)
        return ctx

    def form_valid(self, form):
        self.object = form.save(commit=False)

        # RAMO 1: tipo fixo
        if form.instance.tipo != 'OUTRO':
            # mantém valor_atual = valor_original
            self.object.valor_atual = form.cleaned_data['valor_original']
            self.object.save()
            return redirect(self.get_success_url())

        # RAMO 2: tipo 'OUTRO'
        self.object.save()
        formset = FaturaServicoFormset(self.request.POST, instance=self.object)
        if formset.is_valid():
            total = sum(item.servico.preco * item.quantidade for item in formset.save(commit=False))
            form.instance.valor_original = total
            form.instance.valor_atual    = total
            self.object.save()
            formset.save_m2m()
            return redirect(self.get_success_url())
        return self.form_invalid(form)


@method_decorator(role_required('Admin', 'Diretor', 'Secretaria'), name='dispatch')
class FaturaDeleteView(LoginRequiredMixin, DeleteView):
    model = Fatura
    template_name = 'secretaria/fatura_confirm_delete.html'
    success_url = reverse_lazy('secretaria:fatura-list')

    def dispatch(self, request, *args, **kwargs):
        fatura = self.get_object()
        if fatura.status != 'PENDENTE':
            # Só permite excluir se estiver PENDENTE
            raise PermissionDenied("Só é possível excluir faturas com status PENDENTE.")
        return super().dispatch(request, *args, **kwargs)


# ------------------------------
# Listagem de Conta Corrente (somente leitura)
# ------------------------------

@method_decorator(role_required('Admin', 'Diretor', 'Secretaria'), name='dispatch')
class ContaCorrenteListView(LoginRequiredMixin, ListView):
    model = ContaCorrente
    template_name = 'secretaria/contacorrente_list.html'
    context_object_name = 'contas'
    paginate_by = 20

    def get_queryset(self):
        # Mostra apenas contas de alunos ativos (opcional)
        return ContaCorrente.objects.select_related('aluno').filter(aluno__status='ATIVO',saldo__gt=0)


# ------------------------------
# CRUD de Servico
# ------------------------------

@method_decorator(role_required('Admin', 'Diretor', 'Secretaria'), name='dispatch')
class ServicoListView(LoginRequiredMixin, ListView):
    model = Servico
    template_name = 'secretaria/servico_list.html'
    context_object_name = 'servicos'
    paginate_by = 20

@method_decorator(role_required('Admin', 'Diretor', 'Secretaria'), name='dispatch')
class ServicoCreateView(LoginRequiredMixin, CreateView):
    model = Servico
    form_class = ServicoForm
    template_name = 'secretaria/servico_form.html'
    success_url = reverse_lazy('secretaria:servico-list')

@method_decorator(role_required('Admin', 'Diretor', 'Secretaria'), name='dispatch')
class ServicoUpdateView(LoginRequiredMixin, UpdateView):
    model = Servico
    form_class = ServicoForm
    template_name = 'secretaria/servico_form.html'
    success_url = reverse_lazy('secretaria:servico-list')

@method_decorator(role_required('Admin', 'Diretor', 'Secretaria'), name='dispatch')
class ServicoDeleteView(LoginRequiredMixin, DeleteView):
    model = Servico
    template_name = 'secretaria/servico_confirm_delete.html'
    success_url = reverse_lazy('secretaria:servico-list')


# ------------------------------
# CRUD de Pré‑Matrícula (RF-XX)
# ------------------------------
@method_decorator(role_required('Admin','Diretor','Secretaria'), name='dispatch')
class PreMatriculaListView(LoginRequiredMixin, ListView):
    model = PreMatricula
    template_name = 'secretaria/prematricula_list.html'
    context_object_name = 'prematriculas'
    paginate_by = 20
    ordering = ['-data_solic']

    def get_queryset(self):
        # opcional: só pendentes, ou tudo
        return super().get_queryset()

@method_decorator(role_required('Admin','Diretor','Secretaria'), name='dispatch')
class PreMatriculaCreateView(LoginRequiredMixin, CreateView):
    model = PreMatricula
    form_class = PreMatriculaForm
    template_name = 'secretaria/prematricula_form.html'
    success_url = reverse_lazy('secretaria:prematricula-list')

    def form_valid(self, form):
        # status já é PENDENTE por default
        return super().form_valid(form)

@method_decorator(role_required('Admin','Diretor','Secretaria'), name='dispatch')
class PreMatriculaUpdateView(LoginRequiredMixin, UpdateView):
    model = PreMatricula
    form_class = PreMatriculaForm
    template_name = 'secretaria/prematricula_form.html'
    success_url = reverse_lazy('secretaria:prematricula-list')

    def get_queryset(self):
        # só permitir editar enquanto estiver PENDENTE
        return super().get_queryset().filter(status='PENDENTE')


@method_decorator(role_required('Admin','Diretor','Secretaria'), name='dispatch')
class PreMatriculaDeleteView(LoginRequiredMixin, DeleteView):
    model = PreMatricula
    template_name = 'secretaria/prematricula_confirm_delete.html'
    success_url = reverse_lazy('secretaria:prematricula-list')

    def get_queryset(self):
        # só permitir excluir enquanto estiver PENDENTE
        return super().get_queryset().filter(status='PENDENTE')


# ------------------------------
# Confirmação de Pré‑Matrícula (RF-XX)
# ------------------------------
@login_required
@role_required('Admin','Diretor','Secretaria')
def prematricula_list(request):
    pendentes = PreRematricula.objects.filter(status='PENDENTE')
    return render(request, 'secretaria/rematricula_list.html', {
        'pendentes': pendentes
    })

@login_required
@role_required('Admin','Diretor','Secretaria')
def prematricula_create(request):
    if request.method == 'POST':
        form = PreRematriculaForm(request.POST)
        if form.is_valid():
            # Preenche curso_origem e ano_origem antes de salvar
            rem = form.save(commit=False)
            rem.curso_origem = rem.turma_origem.curso
            rem.ano_origem   = rem.turma_origem.ano_letivo
            rem.save()
            messages.success(request, "Pré‑rematrícula solicitada com sucesso.")
            return redirect('secretaria:rematricula-list')
    else:
        form = PreRematriculaForm()
    return render(request, 'secretaria/rematricula_form.html', {
        'form': form
    })

@login_required
@role_required('Admin','Diretor','Secretaria')
def prematricula_update(request, pk):
    rem = get_object_or_404(PreRematricula, pk=pk, status='PENDENTE')
    if request.method == 'POST':
        form = PreRematriculaForm(request.POST, instance=rem)
        if form.is_valid():
            rem = form.save(commit=False)
            rem.curso_origem = rem.turma_origem.curso
            rem.ano_origem   = rem.turma_origem.ano_letivo
            rem.save()
            messages.success(request, "Solicitação de rematrícula atualizada.")
            return redirect('secretaria:rematricula-list')
    else:
        form = PreRematriculaForm(instance=rem)
    return render(request, 'secretaria/rematricula_form.html', {
        'form': form
    })

@login_required
@role_required('Admin','Diretor','Secretaria')
def prematricula_delete(request, pk):
    rem = get_object_or_404(PreRematricula, pk=pk, status='PENDENTE')
    if request.method == 'POST':
        rem.delete()
        messages.success(request, "Solicitação de rematrícula removida.")
        return redirect('secretaria:rematricula-list')
    return render(request, 'secretaria/rematricula_confirm_delete.html', {
        'object': rem
    })

# ------------------------------
# Relatório de Faturas (RF-XX)
# ------------------------------

@login_required
@role_required('Admin','Diretor','Secretaria')
def fatura_report(request):
    # Validação de parâmetros
    try:
        mes = int(request.GET.get('mes')) if request.GET.get('mes') else None
        if mes and not (1 <= mes <= 12):
            mes = None
    except (TypeError, ValueError):
        mes = None
        
    try:
        ano = int(request.GET.get('ano')) if request.GET.get('ano') else None
    except (TypeError, ValueError):
        ano = None
        
    status = request.GET.get('status')
    aluno_filter = request.GET.get('aluno', '').strip()

    # Query com otimização
    qs = Fatura.objects.select_related('aluno', 'aluno__encarregado').order_by('-data_emissao')
    
    # Filtros
    if mes and ano:
        qs = qs.filter(data_emissao__month=mes, data_emissao__year=ano)
    elif ano:
        qs = qs.filter(data_emissao__year=ano)
        
    if status:
        qs = qs.filter(status=status)
    
    if aluno_filter:
        qs = qs.filter(
            Q(aluno__nome__icontains=aluno_filter)
            )

    # Exportação para Excel
    if request.GET.get('format') == 'excel':
        try:
            data = [{
                'Número': f.numero,
                'Aluno': f.aluno.get_full_name(),
                'Encarregado': f.aluno.encarregado.nome,
                'Emissão': f.data_emissao.strftime('%d/%m/%Y'),
                'Vencimento': f.data_vencimento.strftime('%d/%m/%Y'),
                'Valor Original': f.valor_original,
                'Valor Atual': f.valor_atual,
                'Status': f.get_status_display(),
                'Serviços': ", ".join([s.nome for s in f.servicos.all()])
            } for f in qs]
            
            df = pd.DataFrame(data)
            
            # Cria um buffer de memória
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Faturas')
            buffer.seek(0)
            
            # Cria a resposta
            response = HttpResponse(
                buffer,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            filename = f"faturas_{ano}_{mes}.xlsx" if mes and ano else f"faturas_{ano}.xlsx"
            response['Content-Disposition'] = f'attachment; filename={filename}'
            return response
        except Exception as e:
            # Em caso de erro, retorna uma mensagem de erro
            return HttpResponse(f"Ocorreu um erro ao gerar o Excel: {str(e)}", status=500)

    # Calcula o valor total para exibição
    total_valor = sum(f.valor_atual for f in qs) if qs else 0

    # Paginação para a exibição no template
    paginator = Paginator(qs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'secretaria/fatura_report.html', {
        'faturas': page_obj,
        'mes': mes, 
        'ano': ano, 
        'status': status,
        'aluno_filter': aluno_filter,
        'page_obj': page_obj,  # Para a paginação
        'status_choices': Fatura.STATUS_CHOICES,  # Para o dropdown de status
        'total_valor': total_valor,  # Valor total das faturas
    })

# ------------------------------
# Relatório de Conta Corrente (RF-XX)
# ------------------------------

@login_required
@role_required('Admin','Diretor','Secretaria')
def contacorrente_report(request):
    # Validação de parâmetros
    aluno_filter = request.GET.get('aluno', '').strip()
    status_filter = request.GET.get('status', 'ATIVO')  # Valor padrão
    
    # Query com otimização
    qs = ContaCorrente.objects.select_related('aluno').filter(saldo__gt=0).order_by('aluno__nome')

    
    # Filtros
    if aluno_filter:
        qs = qs.filter(
            Q(aluno__nome__icontains=aluno_filter) |
            Q(aluno__sobrenome__icontains=aluno_filter)
        )
    
    if status_filter:
        qs = qs.filter(aluno__status=status_filter)
    
    # Calcula o saldo total
    saldo_total = sum(conta.saldo for conta in qs) if qs else 0
    
    # Exportação para Excel
    if request.GET.get('format') == 'excel':
        try:
            data = [{
                'Aluno': conta.aluno.get_full_name(),
                'Status Aluno': conta.aluno.get_status_display(),
                'Saldo (AOA)': conta.saldo,
                'Última Atualização': conta.ultima_atualizacao.strftime('%d/%m/%Y %H:%M'),
                'Detalhes': conta.detalhes
            } for conta in qs]
            
            df = pd.DataFrame(data)
            
            # Cria um buffer de memória
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Contas Correntes')
            buffer.seek(0)
            
            # Cria a resposta
            response = HttpResponse(
                buffer,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            filename = f"contas_correntes.xlsx"
            response['Content-Disposition'] = f'attachment; filename={filename}'
            return response
        except Exception as e:
            return HttpResponse(f"Ocorreu um erro ao gerar o Excel: {str(e)}", status=500)

    # Paginação
    paginator = Paginator(qs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'secretaria/contacorrente_report.html', {
        'contas': page_obj,
        'aluno_filter': aluno_filter,
        'status_filter': status_filter,
        'status_choices': Aluno.STATUS_CHOICES,  # Supondo que Aluno tenha STATUS_CHOICES
        'page_obj': page_obj,
        'saldo_total': saldo_total,
    })
