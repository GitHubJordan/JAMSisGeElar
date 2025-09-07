from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Colaborador, ContaContabil, Salario, BemPatrimonio, LancamentoContabil
from .forms import ColaboradorForm, ContaContabilForm, SalarioForm, BemPatrimonioForm, LancamentoContabilForm
from accounts.decorators import role_required
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils import timezone
import os
from decimal import Decimal, ROUND_HALF_UP
from weasyprint import HTML
from django.conf import settings
from django.utils.decorators import method_decorator


@login_required
@role_required('Admin', 'Diretor')
def usuario_redirect_administrativo(request):
    """
    Ao acessar /administrativo/, redireciona para o dashboard do Diretor/Admin.
    """
    return redirect('dashboard:diretor-dashboard')

# ------------------------------
# CRUD de Colaborador
# ------------------------------

@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class ColaboradorListView(LoginRequiredMixin, ListView):
    model = Colaborador
    template_name = 'administrativo/colaborador_list.html'
    context_object_name = 'colaboradores'
    paginate_by = 20
    ordering = ['nome']


@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class ColaboradorCreateView(LoginRequiredMixin, CreateView):
    model = Colaborador
    form_class = ColaboradorForm
    template_name = 'administrativo/colaborador_form.html'
    success_url = reverse_lazy('administrativo:colaborador-list')


@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class ColaboradorUpdateView(LoginRequiredMixin, UpdateView):
    model = Colaborador
    form_class = ColaboradorForm
    template_name = 'administrativo/colaborador_form.html'
    success_url = reverse_lazy('administrativo:colaborador-list')

@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
def no_delete(request):
    model = Colaborador
    template_name = 'administrativo/colaborador_confirm_no_delete.html'
    success_url = reverse_lazy('administrativo:colaborador-nodelete')

@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class ColaboradorDeleteView(LoginRequiredMixin, DeleteView):
    model = Colaborador
    template_name = 'administrativo/colaborador_confirm_delete.html'
    success_url = reverse_lazy('administrativo:colaborador-list')

    def dispatch(self, request, *args, **kwargs):
        colaborador = self.get_object()
        # Impede excluir colaborador que tenha salários vinculados
        if Salario.objects.filter(colaborador=colaborador).exists():
            # raise PermissionDenied("Não é possível excluir colaborador com salários registrados.")
            no_delete_url = reverse_lazy('administrativo:colaborador-nodelete')
            return redirect(no_delete_url)
        return super().dispatch(request, *args, **kwargs)


# ------------------------------
# CRUD de Salário
# ------------------------------

@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class SalarioListView(LoginRequiredMixin, ListView):
    model = Salario
    template_name = 'administrativo/salario_list.html'
    context_object_name = 'salarios'
    paginate_by = 20
    ordering = ['-mes_referencia']

    def get_queryset(self):
        return super().get_queryset().select_related('colaborador')


@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class SalarioCreateView(LoginRequiredMixin, CreateView):
    model = Salario
    form_class = SalarioForm
    template_name = 'administrativo/salario_form.html'
    success_url = reverse_lazy('administrativo:salario-list')

    def form_valid(self, form):
        # Converter para Decimal com tratamento de None
        def safe_decimal(value):
            return Decimal(str(value)) if value is not None else Decimal('0')
        
        colaborador = form.cleaned_data['colaborador']
        horas_extras = safe_decimal(form.cleaned_data['horas_extras'])
        descontos = safe_decimal(form.cleaned_data['descontos'])
        bonificacoes = safe_decimal(form.cleaned_data['bonificacoes'])
        base = colaborador.salario_base or Decimal('0')

        carga_horaria = Decimal('8')
        dias_uteis = Decimal('22')  # Considerando 22 dias úteis no mês
        
        # Cálculos com Decimal
        valor_hora = base / (carga_horaria * dias_uteis)
        valor_horas_extras = horas_extras * valor_hora * Decimal('1.5')
        salario_bruto = base + valor_horas_extras + bonificacoes - descontos
        
        # inss = salario_bruto * Decimal('0.08')
        # irt = salario_bruto * Decimal('0.15')
        salario_liquido = salario_bruto # - inss - irt
        
        # Arredondamento monetário
        salario_bruto = salario_bruto.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        # inss = inss.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        # irt = irt.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        salario_liquido = salario_liquido.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Atribuir valores ao formulário
        form.instance.salario_bruto = salario_bruto
        form.instance.inss = 0 # inss
        form.instance.irt = 0 # irt
        form.instance.salario_liquido = salario_liquido
        form.instance.processado_por = self.request.user

        response = super().form_valid(form)

        # Gerar holerite em PDF (apenas para CreateView)
        salario = form.instance
        html_string = render_to_string('administrativo/holerite_pdf.html', {
            'colaborador': colaborador,
            'salario': salario,
            'data_processamento': timezone.now(),
            'instituicao': "Instituto Médio Técnico Cecília Domingos",
        })
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        filename = f'holerite_{colaborador.nome.replace(" ", "_")}_{timestamp}.pdf'
        output_dir = os.path.join(settings.MEDIA_ROOT, 'administrativo', 'holerites')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)
        HTML(string=html_string, base_url=self.request.build_absolute_uri('/')).write_pdf(output_path)

        # Salva o caminho no campo arquivo_holerite
        salario.arquivo_holerite = f'administrativo/holerites/{filename}'
        salario.save()

        messages.success(self.request, f'Holerite gerado: {filename}')
        return response


@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class SalarioUpdateView(LoginRequiredMixin, UpdateView):
    model = Salario
    form_class = SalarioForm
    template_name = 'administrativo/salario_form.html'
    success_url = reverse_lazy('administrativo:salario-list')

    def form_valid(self, form):
        # Converter para Decimal com tratamento de None
        def safe_decimal(value):
            return Decimal(str(value)) if value is not None else Decimal('0')
        
        colaborador = form.cleaned_data['colaborador']
        horas_extras = safe_decimal(form.cleaned_data['horas_extras'])
        descontos = safe_decimal(form.cleaned_data['descontos'])
        bonificacoes = safe_decimal(form.cleaned_data['bonificacoes'])
        base = colaborador.salario_base or Decimal('0')
        
        # Cálculos com Decimal
        valor_hora = base / Decimal('160')
        valor_horas_extras = horas_extras * valor_hora * Decimal('1.5')
        salario_bruto = base + valor_horas_extras + bonificacoes - descontos
        
        inss = salario_bruto * Decimal('0.08')
        irt = salario_bruto * Decimal('0.15')
        salario_liquido = salario_bruto - inss - irt
        
        # Arredondamento monetário
        salario_bruto = salario_bruto.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        inss = inss.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        irt = irt.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        salario_liquido = salario_liquido.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Atribuir valores ao formulário
        form.instance.salario_bruto = salario_bruto
        form.instance.inss = inss
        form.instance.irt = irt
        form.instance.salario_liquido = salario_liquido
        form.instance.processado_por = self.request.user
        form.instance.data_processamento = timezone.now()

        return super().form_valid(form)


@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class SalarioDeleteView(LoginRequiredMixin, DeleteView):
    model = Salario
    template_name = 'administrativo/salario_confirm_delete.html'
    success_url = reverse_lazy('administrativo:salario-list')


# ------------------------------
# CRUD de BemPatrimonio
# ------------------------------

@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class BemPatrimonioListView(LoginRequiredMixin, ListView):
    model = BemPatrimonio
    template_name = 'administrativo/patrimonio_list.html'
    context_object_name = 'patrimonios'
    paginate_by = 20
    ordering = ['-data_aquisicao']

    def get_queryset(self):
        return super().get_queryset()


@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class BemPatrimonioCreateView(LoginRequiredMixin, CreateView):
    model = BemPatrimonio
    form_class = BemPatrimonioForm
    template_name = 'administrativo/patrimonio_form.html'
    success_url = reverse_lazy('administrativo:patrimonio-list')

    def form_valid(self, form):
        try:
            # Tente salvar sem lógica adicional
            return super().form_valid(form)
        except RecursionError:
            # Fallback seguro
            self.object = form.save()
            return redirect(self.get_success_url())


@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class BemPatrimonioUpdateView(LoginRequiredMixin, UpdateView):
    model = BemPatrimonio
    form_class = BemPatrimonioForm
    template_name = 'administrativo/patrimonio_form.html'
    success_url = reverse_lazy('administrativo:patrimonio-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        return response


@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class BemPatrimonioDeleteView(LoginRequiredMixin, DeleteView):
    model = BemPatrimonio
    template_name = 'administrativo/patrimonio_confirm_delete.html'
    success_url = reverse_lazy('administrativo:patrimonio-list')

# ------------------------------
# CRUD de Plano de Contas
# ------------------------------

@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class PlanoContasListView(LoginRequiredMixin, ListView):
    model = ContaContabil
    template_name = 'administrativo/plano_contas_list.html'
    context_object_name = 'contas'
    paginate_by = 20
    ordering = ['codigo']

@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class PlanoContasCreateView(LoginRequiredMixin, CreateView):
    model = ContaContabil
    form_class = ContaContabilForm
    template_name = 'administrativo/plano_contas_form.html'
    success_url = reverse_lazy('administrativo:plano-contas-list')

@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class PlanoContasUpdateView(LoginRequiredMixin, UpdateView):
    model = ContaContabil
    form_class = ContaContabilForm
    template_name = 'administrativo/plano_contas_form.html'
    success_url = reverse_lazy('administrativo:plano-contas-list')

@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class PlanoContasDeleteView(LoginRequiredMixin, DeleteView):
    model = ContaContabil
    template_name = 'administrativo/plano_contas_confirm_delete.html'
    success_url = reverse_lazy('administrativo:plano-contas-list')

# ------------------------------
# CRUD de LancamentoContabil
# ------------------------------

@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class LancamentoContabilListView(LoginRequiredMixin, ListView):
    model = LancamentoContabil
    template_name = 'administrativo/lancamento_list.html'
    context_object_name = 'lancamentos'
    paginate_by = 20
    ordering = ['-data_lancamento']

    def get_queryset(self):
        return super().get_queryset()


@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class LancamentoContabilCreateView(LoginRequiredMixin, CreateView):
    model = LancamentoContabil
    form_class = LancamentoContabilForm
    template_name = 'administrativo/lancamento_form.html'
    success_url = reverse_lazy('administrativo:lancamento-list')

    def form_valid(self, form):
        form.instance.lancado_por = self.request.user
        return super().form_valid(form)


@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class LancamentoContabilUpdateView(LoginRequiredMixin, UpdateView):
    model = LancamentoContabil
    form_class = LancamentoContabilForm
    template_name = 'administrativo/lancamento_form.html'
    success_url = reverse_lazy('administrativo:lancamento-list')


@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class LancamentoContabilDeleteView(LoginRequiredMixin, DeleteView):
    model = LancamentoContabil
    template_name = 'administrativo/lancamento_confirm_delete.html'
    success_url = reverse_lazy('administrativo:lancamento-list')

# ------------------------------
# Relatório de Salários (RF-XX)
# ------------------------------

@login_required
@role_required('Admin','Diretor')
def salario_report(request):
    ano = request.GET.get('ano')  # ou exercício atual via context processor
    qs = Salario.objects.select_related('colaborador')
    if ano:
        qs = qs.filter(data_processamento__year=ano)
    if request.GET.get('format') == 'excel':
        import pandas as pd
        data = []
        for s in qs:
            data.append({
                'Colaborador': s.colaborador.nome,
                'Mês Referência': s.mes_referencia.strftime('%m/%Y'),
                'Salário Bruto': s.salario_bruto,
                'INSS': s.inss,
                'IRRF': s.irt,
                'Salário Líquido': s.salario_liquido,
            })
        from io import BytesIO
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
            pd.DataFrame(data).to_excel(writer, index=False, sheet_name='Salários')
        buf.seek(0)
        resp = HttpResponse(
            buf,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        resp['Content-Disposition'] = f'attachment; filename=salarios_{ano}.xlsx'
        return resp
    # PDF via WeasyPrint se formato pdf
    if request.GET.get('format') == 'pdf':
        html = render_to_string('administrativo/salario_report_pdf.html', {'salarios': qs, 'ano': ano})
        pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
        return HttpResponse(pdf, content_type='application/pdf')
    return render(request, 'administrativo/salario_report.html', {'salarios': qs, 'ano': ano})

