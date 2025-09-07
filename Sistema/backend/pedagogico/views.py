# Sistema/backend/pedagogico/views.py
from io import BytesIO
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from core.mixins import AnoContextMixin
from .models import PreRematricula, Turma, Disciplina, TurmaDisciplina, Matricula, Nota, Boletim, AnoLetivo, Calendario, Curso
from .forms import PreRematriculaForm, TurmaForm, DisciplinaForm, TurmaDisciplinaForm, MatriculaForm, NotaForm, AnoLetivoForm, CalendarioForm, CursoForm
from accounts.decorators import role_required

from secretaria.models import PreMatricula

from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse

from django.contrib import messages
from django.utils import timezone


@login_required
@role_required('Admin', 'Diretor', 'Pedagogico')
def usuario_redirect_pedagogico(request):
    return redirect('dashboard:pedagogico-dashboard')

# --------------------------------
# CRUD de Turma (RF-??)
# --------------------------------

@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class TurmaListView(LoginRequiredMixin, AnoContextMixin, ListView):
    model = Turma
    template_name = 'pedagogico/turma/turma_list.html'
    context_object_name = 'turmas'
    paginate_by = 20
    ordering = ['nome']

    def get_queryset(self):
        # Pega ano ativo (ativo=True)
        ano = AnoLetivo.objects.filter(ativo=True).first()
        qs = super().get_queryset()
        if ano:
            return qs.filter(ano_letivo=ano)
        return qs.none()


@method_decorator(role_required('Admin','Diretor','Pedagogico'), name='dispatch')
class TurmaCreateView(LoginRequiredMixin, CreateView):
    model = Turma
    form_class = TurmaForm
    template_name = 'pedagogico/turma/turma_form.html'
    success_url = reverse_lazy('pedagogico:turma-list')

    def form_valid(self, form):
        ativo = AnoLetivo.objects.filter(ativo=True).first()
        if not ativo:
            form.add_error(None, "Não há nenhum ano letivo ativo definido.")
            return super().form_invalid(form)
        form.instance.ano_letivo = ativo
        return super().form_valid(form)


@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class TurmaUpdateView(LoginRequiredMixin, UpdateView):
    model = Turma
    form_class = TurmaForm
    template_name = 'pedagogico/turma/turma_form.html'
    success_url = reverse_lazy('pedagogico:turma-list')


@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class TurmaDeleteView(LoginRequiredMixin, DeleteView):
    model = Turma
    template_name = 'pedagogico/turma/turma_confirm_delete.html'
    success_url = reverse_lazy('pedagogico:turma-list')


# --------------------------------
# CRUD de Disciplina
# --------------------------------

@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class DisciplinaListView(LoginRequiredMixin, ListView):
    model = Disciplina
    template_name = 'pedagogico/disciplina/disciplina_list.html'
    context_object_name = 'disciplinas'
    paginate_by = 20
    ordering = ['nome']


@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class DisciplinaCreateView(LoginRequiredMixin, CreateView):
    model = Disciplina
    form_class = DisciplinaForm
    template_name = 'pedagogico/disciplina/disciplina_form.html'
    success_url = reverse_lazy('pedagogico:disciplina-list')


@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class DisciplinaUpdateView(LoginRequiredMixin, UpdateView):
    model = Disciplina
    form_class = DisciplinaForm
    template_name = 'pedagogico/disciplina/disciplina_form.html'
    success_url = reverse_lazy('pedagogico:disciplina-list')


@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class DisciplinaDeleteView(LoginRequiredMixin, DeleteView):
    model = Disciplina
    template_name = 'pedagogico/disciplina/disciplina_confirm_delete.html'
    success_url = reverse_lazy('pedagogico:disciplina-list')


# --------------------------------
# CRUD de TurmaDisciplina (Associação N:N)
# --------------------------------

@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class TurmaDisciplinaListView(LoginRequiredMixin, AnoContextMixin, ListView):
    model = TurmaDisciplina
    template_name = 'pedagogico/turmadisciplina/turmadisciplina_list.html'
    context_object_name = 'associacoes'
    paginate_by = 20
    ordering = ['turma__nome', 'disciplina__nome']

    # def get_queryset(self):
    #    return super().get_queryset().select_related('turma', 'disciplina')
    
    def get_queryset(self):
        # Pega ano ativo (ativo=True)
        ano = AnoLetivo.objects.filter(ativo=True).first()
        qs = super().get_queryset()
        if ano:
            return qs.filter(ano_letivo=ano)
        return qs.none()


@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class TurmaDisciplinaCreateView(LoginRequiredMixin, CreateView):
    model = TurmaDisciplina
    form_class = TurmaDisciplinaForm
    template_name = 'pedagogico/turmadisciplina/turmadisciplina_form.html'
    success_url = reverse_lazy('pedagogico:turmadisciplina-list')

    def form_valid(self, form):
        ativo = AnoLetivo.objects.filter(ativo=True).first()
        if not ativo:
            form.add_error(None, "Não há nenhum ano letivo ativo definido.")
            return super().form_invalid(form)
        # força o FK antes do save()
        form.instance.ano_letivo = ativo
        return super().form_valid(form)


@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class TurmaDisciplinaUpdateView(LoginRequiredMixin, UpdateView):
    model = TurmaDisciplina
    form_class = TurmaDisciplinaForm
    template_name = 'pedagogico/turmadisciplina/turmadisciplina_form.html'
    success_url = reverse_lazy('pedagogico:turmadisciplina-list')


@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class TurmaDisciplinaDeleteView(LoginRequiredMixin, DeleteView):
    model = TurmaDisciplina
    template_name = 'pedagogico/turmadisciplina/turmadisciplina_confirm_delete.html'
    success_url = reverse_lazy('pedagogico:turmadisciplina-list')


# --------------------------------
# CRUD de Matrícula
# --------------------------------

@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class MatriculaListView(LoginRequiredMixin, AnoContextMixin, ListView):
    model = Matricula
    template_name = 'pedagogico/matricula/matricula_list.html'
    context_object_name = 'matriculas'
    paginate_by = 20
    ordering = ['-data_matricula']

    # def get_queryset(self):
    #    return super().get_queryset().select_related('aluno', 'turma')

    def get_queryset(self):
        ano = AnoLetivo.objects.filter(ativo=True).first()
        qs = super().get_queryset()
        return qs.filter(ano_letivo=ano)

@method_decorator(role_required('Admin','Diretor','Pedagogico'), name='dispatch')
class MatriculaCreateView(LoginRequiredMixin, CreateView):
    model = Matricula
    form_class = MatriculaForm
    template_name = 'pedagogico/matricula/matricula_form.html'
    success_url = reverse_lazy('pedagogico:matricula-list')

    def form_valid(self, form):
        ativo = AnoLetivo.objects.filter(ativo=True).first()
        if not ativo:
            form.add_error(None, "Não há nenhum ano letivo ativo definido.")
            return super().form_invalid(form)
        form.instance.ano_letivo = ativo
        # curso atribuído automaticamente da turma
        form.instance.curso = form.instance.turma.curso
        return super().form_valid(form)


@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class MatriculaUpdateView(LoginRequiredMixin, UpdateView):
    model = Matricula
    form_class = MatriculaForm
    template_name = 'pedagogico/matricula/matricula_form.html'
    success_url = reverse_lazy('pedagogico:matricula-list')

    def form_valid(self, form):
        ativo = AnoLetivo.objects.filter(ativo=True).first()
        form.instance.ano_letivo = ativo
        return super().form_valid(form)

@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class MatriculaDeleteView(LoginRequiredMixin, DeleteView):
    model = Matricula
    template_name = 'pedagogico/matricula/matricula_confirm_delete.html'
    success_url = reverse_lazy('pedagogico:matricula-list')


# --------------------------------
# CRUD de Nota
# --------------------------------

@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class NotaListView(LoginRequiredMixin, AnoContextMixin, ListView):
    model = Nota
    template_name = 'pedagogico/nota/nota_list.html'
    context_object_name = 'notas'
    paginate_by = 20
    ordering = ['aluno__nome']

    # def get_queryset(self):
    #    return super().get_queryset().select_related('aluno', 'turma', 'disciplina')

    def get_queryset(self):
        ano = AnoLetivo.objects.filter(ativo=True).first()
        qs = super().get_queryset()
        return qs.filter(ano_letivo=ano)

@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class NotaCreateView(LoginRequiredMixin, CreateView):
    model = Nota
    form_class = NotaForm
    template_name = 'pedagogico/nota/nota_form.html'
    success_url = reverse_lazy('pedagogico:nota-list')

    def form_valid(self, form):
        ativo = AnoLetivo.objects.filter(ativo=True).first()
        if not ativo:
            form.add_error(None, "Não há nenhum ano letivo ativo definido.")
            return super().form_invalid(form)
        # força o FK antes do save()
        form.instance.ano_letivo = ativo
        return super().form_valid(form)


@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class NotaUpdateView(LoginRequiredMixin, UpdateView):
    model = Nota
    form_class = NotaForm
    template_name = 'pedagogico/nota/nota_form.html'
    success_url = reverse_lazy('pedagogico:nota-list')

    def form_valid(self, form):
        # força o FK do ano letivo ativo, tal como na criação
        ativo = AnoLetivo.objects.filter(ativo=True).first()
        if not ativo:
            form.add_error(None, "Não há nenhum ano letivo ativo definido.")
            return super().form_invalid(form)
        form.instance.ano_letivo = ativo
        return super().form_valid(form)


@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class NotaDeleteView(LoginRequiredMixin, DeleteView):
    model = Nota
    template_name = 'pedagogico/nota/nota_confirm_delete.html'
    success_url = reverse_lazy('pedagogico:nota-list')


# --------------------------------
# List e geração de Boletins
# --------------------------------

@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class BoletimListView(LoginRequiredMixin, AnoContextMixin, ListView):
    model = Boletim
    template_name = 'pedagogico/boletim/boletim_list.html'
    context_object_name = 'boletins'
    paginate_by = 20
    ordering = ['-data_geracao']

    def get_queryset(self):
        return super().get_queryset().select_related('turma', 'gerado_por')


@login_required
@role_required('Admin', 'Diretor', 'Pedagogico')
def gerar_boletim(request):
    """
    View para gerar Boletim PDF para uma Turma e Trimestre específicos.
    Usa WeasyPrint para renderizar o template HTML como PDF.
    """
    from django.template.loader import render_to_string
    from django.utils import timezone
    import os
    from weasyprint import HTML
    from .models import Boletim, Turma, Nota
    from django.contrib import messages

    if request.method == 'POST':
        turma_id = request.POST.get('turma')
        trimestre = int(request.POST.get('trimestre'))
        turma = get_object_or_404(Turma, pk=turma_id)

        # Coleta todas as Notas dessa Turma para o trimestre (não temos a lógica de trimestre na Nota, 
        # mas supomos que se trimestre=1, pegamos notas criadas antes de certa data; aqui simplificamos pegando todas)
        notas = Nota.objects.filter(turma=turma)

        # Renderiza um HTML simples (você deve criar o template `boletim_pdf.html`)
        html_string = render_to_string('pedagogico/boletim_pdf.html', {
            'turma': turma,
            'trimestre': trimestre,
            'notas': notas,
            'data_geracao': timezone.now(),
            'instituicao': "Instituto Médio Técnico Cecília Domingos",
        })

        # Define nome do arquivo: “boletim_{turma}_{trimestre}_{YYYYMMDDHHMMSS}.pdf”
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        filename = f'boletim_{turma.nome}_{trimestre}_{timestamp}.pdf'.replace(' ', '_')

        # Define caminho temporário para salvar PDF dentro de MEDIA_ROOT/pedagogico/boletins/
        from django.conf import settings
        output_dir = os.path.join(settings.MEDIA_ROOT, 'pedagogico', 'boletins')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)

        # Gera PDF
        HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(output_path)

        # Cria registro Boletim:
        boletim = Boletim.objects.create(
            turma=turma,
            trimestre=trimestre,
            arquivo_pdf=f'pedagogico/boletins/{filename}',
            gerado_por=request.user
        )

        messages.success(request, f'Boletim gerado: {filename}')
        return redirect('pedagogico:boletim-list')

    # Se GET, exibimos o formulário de seleção de Turma e Trimestre
    turmas = Turma.objects.all().order_by('nome')
    return render(request, 'pedagogico/boletim/boletim_list.html', {
        'turmas': turmas
    })

# ------------------------------
# CRUD de Ano Letivo
# ------------------------------

@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class AnoLetivoListView(ListView):
    model = AnoLetivo
    template_name = 'pedagogico/anolectivo/anoletivo_list.html'
    context_object_name = 'anos'
    paginate_by = 20
    ordering = ['-data_inicio']


@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class AnoLetivoCreateView(CreateView):
    model = AnoLetivo
    form_class = AnoLetivoForm
    template_name = 'pedagogico/anolectivo/anoletivo_form.html'
    success_url = reverse_lazy('pedagogico:anoletivo-list')


@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class AnoLetivoUpdateView(UpdateView):
    model = AnoLetivo
    form_class = AnoLetivoForm
    template_name = 'pedagogico/anolectivo/anoletivo_form.html'
    success_url = reverse_lazy('pedagogico:anoletivo-list')


@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class AnoLetivoDeleteView(DeleteView):
    model = AnoLetivo
    template_name = 'pedagogico/anolectivo/anoletivo_confirm_delete.html'
    success_url = reverse_lazy('pedagogico:anoletivo-list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        # Impede excluir se for o ano ativo
        if obj.ativo:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("Não é permitido excluir o ano letivo ativo.")
        return super().dispatch(request, *args, **kwargs)


# ------------------------------
# CRUD de Calendário
# ------------------------------

@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class CalendarioListView(ListView):
    model = Calendario
    template_name = 'pedagogico/calendario/calendario_list.html'
    context_object_name = 'eventos'
    paginate_by = 20
    ordering = ['data']

    def get_queryset(self):
        return super().get_queryset().select_related('ano_letivo')


@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class CalendarioCreateView(CreateView):
    model = Calendario
    form_class = CalendarioForm
    template_name = 'pedagogico/calendario/calendario_form.html'
    success_url = reverse_lazy('pedagogico:calendario-list')


@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class CalendarioUpdateView(UpdateView):
    model = Calendario
    form_class = CalendarioForm
    template_name = 'pedagogico/calendario/calendario_form.html'
    success_url = reverse_lazy('pedagogico:calendario-list')


@method_decorator(role_required('Admin', 'Diretor', 'Pedagogico'), name='dispatch')
class CalendarioDeleteView(DeleteView):
    model = Calendario
    template_name = 'pedagogico/calendario/calendario_confirm_delete.html'
    success_url = reverse_lazy('pedagogico:calendario-list')

#---------------------------------
# View para exibir o calendário em formato mensal
#---------------------------------

@login_required
@role_required('Admin', 'Diretor', 'Pedagogico')
def calendario_mensal(request):
    """
    View para exibir o calendário em formato mensal.
    """
    from django.utils import timezone
    from .models import Calendario

    ano_atual = timezone.now().year
    meses = Calendario.objects.filter(data__year=ano_atual).order_by('data')

    return render(request, 'pedagogico/calendario/calendario_mensal.html', {
        'meses': meses,
        'ano_atual': ano_atual,
    })

# --------------------------------
# CRUE de Relatório Academinico
# --------------------------------
@login_required
@role_required('Admin','Diretor','Pedagogico')
def relatorio_ano_letivo(request):
    ano = AnoLetivo.objects.filter(ativo=True).first()
    matriculas = Matricula.objects.filter(ano_letivo=ano).select_related('aluno','turma')
    notas = Nota.objects.filter(ano_letivo=ano).select_related('aluno','disciplina','turma')

    if request.GET.get('format') == 'pdf':
        html = render_to_string('pedagogico/relatorio_pdf.html',{
            'ano': ano,'matriculas': matriculas,'notas': notas
        })
        pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
        return HttpResponse(pdf, content_type='application/pdf')
    
    if request.GET.get('format') == 'excel':
        import pandas as pd
        # Build rows de matrículas e notas
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
            pd.DataFrame([...]).to_excel(writer, sheet_name='Matrículas', index=False)
            pd.DataFrame([...]).to_excel(writer, sheet_name='Notas', index=False)


    return render(request,'pedagogico/relatorio.html',{
        'ano':ano,'matriculas':matriculas,'notas':notas
    })


# --------------------------------
# CRUD de Curso
# --------------------------------
@method_decorator(role_required('Admin','Diretor','Pedagogico'), name='dispatch')
class CursoListView(LoginRequiredMixin, ListView):
    model = Curso
    template_name = 'pedagogico/curso/curso_list.html'
    context_object_name = 'cursos'
    paginate_by = 20

@method_decorator(role_required('Admin','Diretor','Pedagogico'), name='dispatch')
class CursoCreateView(LoginRequiredMixin, CreateView):
    model = Curso
    form_class = CursoForm
    template_name = 'pedagogico/curso/curso_form.html'
    success_url = reverse_lazy('pedagogico:curso-list')

@method_decorator(role_required('Admin','Diretor','Pedagogico'), name='dispatch')
class CursoUpdateView(LoginRequiredMixin, UpdateView):
    model = Curso
    form_class = CursoForm
    template_name = 'pedagogico/curso/curso_form.html'
    success_url = reverse_lazy('pedagogico:curso-list')

@method_decorator(role_required('Admin','Diretor','Pedagogico'), name='dispatch')
class CursoDeleteView(LoginRequiredMixin, DeleteView):
    model = Curso
    template_name = 'pedagogico/curso/curso_confirm_delete.html'
    success_url = reverse_lazy('pedagogico:curso-list')

# --------------------------------
# CRUD de Pré-Matrícula
# --------------------------------
@method_decorator(role_required('Admin','Diretor','Pedagogico'), name='dispatch')
class PreMatriculaPendentesListView(LoginRequiredMixin, AnoContextMixin, ListView):
    model = PreMatricula
    template_name = 'pedagogico/prematricula/prematricula_pendentes_list.html'
    context_object_name = 'pendentes'
    paginate_by = 20
    ordering = ['-data_solic']

    def get_queryset(self):
        ano = AnoLetivo.objects.filter(ativo=True).first()
        qs  = PreMatricula.objects.filter(status='PENDENTE')
        if ano:
            # converte o campo nome ("2025" ou "2025-2026") num inteiro de ano
            try:
                ano_int = int(ano.nome.split('-')[0])
            except ValueError:
                ano_int = timezone.now().year
            # filtra pela parte “ano” do DateTimeField
            return qs.filter(data_solic__year=ano_int).order_by('-data_solic')
        return qs.order_by('-data_solic')

@login_required
@role_required('Admin','Diretor','Pedagogico')
def confirmar_prematricula(request, pk):
    prem = get_object_or_404(PreMatricula, pk=pk, status='PENDENTE')
    ano = AnoLetivo.objects.filter(ativo=True).first()
    if not ano:
        messages.error(request, "Não há ano letivo ativo.")
        return redirect('pedagogico:prematricula-pendentes')

    turmas = Turma.objects.filter(ano_letivo=ano)

    if request.method == 'POST':
        acao = request.POST.get('acao')
        turma_id = request.POST.get('turma')

        if acao == 'aprovar':
            # 1) Seleção de turma obrigatória
            if not turma_id:
                messages.error(request, "Por favor, selecione uma turma.")
                return redirect(request.path)

            turma = get_object_or_404(Turma, pk=turma_id, ano_letivo=ano)

            # 2) Verifica se o aluno já tem matrícula neste ano
            existe = Matricula.objects.filter(
                aluno=prem.aluno,
                ano_letivo=ano
            )
            if existe.exists():
                messages.error(request,
                    "Este aluno já possui matrícula no ano letivo atual.")
                return redirect(request.path)

            # 3) Garante que turma.curso == prem.curso
            if turma.curso != prem.curso:
                messages.error(request,
                    "A turma escolhida não pertence ao curso solicitado na pré‑matrícula.")
                return redirect(request.path)

            # Tudo OK → cria matrícula
            Matricula.objects.create(
                aluno=prem.aluno,
                turma=turma,
                curso=turma.curso,
                ano_letivo=ano,
                data_matricula=timezone.now().date()
            )
            prem.status = 'APROVADA'
            prem.save()
            messages.success(request, "Pré‑matrícula aprovada.")
            return redirect('pedagogico:prematricula-pendentes')

        elif acao == 'recusar':
            prem.status = 'RECUSADA'
            prem.save()
            messages.warning(request, "Pré‑matrícula recusada.")
            return redirect('pedagogico:prematricula-pendentes')

    return render(request, 'pedagogico/prematricula/confirmar_prematricula.html', {
        'prematricula': prem,
        'turmas': turmas,
    })

# --------------------------------
# CRUD de Confirmação de Matrícula
# --------------------------------
@login_required
@role_required('Admin','Diretor','Pedagogico')
def rematricula_solicitar(request):
    """
    Secretaria pré‑solicita rematrícula de alunos ativos.
    """
    if request.method == 'POST':
        form = PreRematriculaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Solicitação de rematrícula criada.")
            return redirect('pedagogico:rematricula-pendentes')
    else:
        form = PreRematriculaForm()
    return render(request, 'pedagogico/rematricula/rematricula_form.html', {'form': form})

@method_decorator(role_required('Admin','Diretor','Pedagogico'), name='dispatch')
class PreRematriculaListView(LoginRequiredMixin, ListView):
    model = PreRematricula
    template_name = 'pedagogico/rematricula/rematricula_pendentes_list.html'
    context_object_name = 'pendentes'
    queryset = PreRematricula.objects.filter(status='PENDENTE')

@login_required
@role_required('Admin','Diretor','Pedagogico')
def rematricula_confirmar(request, pk):
    """
    Pedagógico aprova/recusa e efetiva nova matrícula.
    """
    prem = get_object_or_404(PreRematricula, pk=pk, status='PENDENTE')
    ano_novo = AnoLetivo.objects.filter(ativo=True).first()

    if not ano_novo:
        messages.error(request, "Não há ano letivo ativo definido.")
        return redirect('pedagogico:rematricula-pendentes')

    # Mostra apenas turmas do curso de origem e do ano letivo ativo
    turmas = Turma.objects.filter(curso=prem.curso_origem, ano_letivo=ano_novo)


    if request.method == 'POST':
        acao    = request.POST.get('acao')
        turma_id = request.POST.get('turma')
        if acao == 'aprovar' and turma_id:
            turma = get_object_or_404(Turma, pk=turma_id, ano_letivo=ano_novo)

            # ⚠️ Verifica se já existe matrícula deste aluno neste ano letivo
            if Matricula.objects.filter(aluno=prem.aluno, ano_letivo=ano_novo).exists():
                messages.error(request, "Este aluno já possui matrícula no ano letivo atual.")
                return redirect(request.path)

            # Garante que a turma corresponde ao curso de origem
            if turma.curso != prem.curso_origem:
                messages.error(request, "A turma selecionada não corresponde ao curso de origem do aluno.")
                return redirect(request.path)

            # Tudo certo → cria nova matrícula
            Matricula.objects.create(
                aluno=prem.aluno,
                turma=turma,
                curso=turma.curso,
                ano_letivo=ano_novo,
                data_matricula=timezone.now().date()
            )
            prem.status = 'APROVADA'
            prem.save()
            messages.success(request, "Rematrícula aprovada e efetivada.")
            return redirect('pedagogico:rematricula-pendentes')

        elif acao == 'recusar':
            prem.status = 'RECUSADA'
            prem.save()
            messages.warning(request, "Rematrícula recusada.")
            return redirect('pedagogico:rematricula-pendentes')
        else:
            messages.error(request, "Escolha uma ação e turma válidas.")

    return render(request, 'pedagogico/rematricula/rematricula_confirmar.html', {
        'prematricula': prem,
        'turmas': turmas
    })