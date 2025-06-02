# Sistema/backend/secretaria/views.py
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Encarregado, Aluno, Fatura, ContaCorrente
from .forms import EncarregadoForm, AlunoForm, FaturaForm

# Decorator para checar roles (pode usar o mesmo role_required do accounts)
from accounts.decorators import role_required

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


@method_decorator(role_required('Admin', 'Diretor', 'Secretaria'), name='dispatch')
class EncarregadoUpdateView(LoginRequiredMixin, UpdateView):
    model = Encarregado
    form_class = EncarregadoForm
    template_name = 'secretaria/encarregado_form.html'
    success_url = reverse_lazy('secretaria:encarregado-list')


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

    def form_valid(self, form):
        # Gera número de fatura automático: “YYYY/NNNN”
        from datetime import date
        ano = date.today().year
        ultimo = Fatura.objects.filter(numero__startswith=str(ano)).order_by('-numero').first()
        if ultimo:
            try:
                seq = int(ultimo.numero.split('/')[-1]) + 1
            except:
                seq = 1
        else:
            seq = 1
        form.instance.numero = f"{ano}/{seq:04d}"
        form.instance.valor_atual = form.cleaned_data['valor_original']
        return super().form_valid(form)


@method_decorator(role_required('Admin', 'Diretor', 'Secretaria'), name='dispatch')
class FaturaUpdateView(LoginRequiredMixin, UpdateView):
    model = Fatura
    form_class = FaturaForm
    template_name = 'secretaria/fatura_form.html'
    success_url = reverse_lazy('secretaria:fatura-list')

    def dispatch(self, request, *args, **kwargs):
        fatura = self.get_object()
        if fatura.status == 'PAGO':
            # Não permitir editar faturas já pagas
            raise PermissionDenied("Não é possível editar uma fatura já paga.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Se mudarmos valor_original, redefinimos valor_atual caso status ainda seja PENDENTE
        if form.instance.status in ['PENDENTE', 'VENCIDO']:
            form.instance.valor_atual = form.cleaned_data['valor_original']
        return super().form_valid(form)


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
        return ContaCorrente.objects.select_related('aluno').filter(aluno__status='ATIVO')
