from django.db import models
from django.forms import ValidationError
from accounts.models import User
from secretaria.models import Aluno


class AnoLetivo(models.Model):
    """
    Representa um ano acadêmico (pode ser 2025/2026 ou apenas 2025).
    """
    nome = models.CharField(
        max_length=20,
        unique=True,
        help_text="Ex.: 2025, 2025-2026 ou 2025.1"
    )
    data_inicio = models.DateField(
        help_text="Data de início do ano letivo"
    )
    data_fim = models.DateField(
        help_text="Data de término do ano letivo"
    )
    ativo = models.BooleanField(
        default=False,
        help_text="Marcar apenas um ano como ativo"
    )

    class Meta:
        ordering = ['-data_inicio']
        verbose_name = "Ano Letivo"
        verbose_name_plural = "Anos Letivos"

    def __str__(self):
        return self.nome

    def clean(self):
        """
        Garante que:
        - data_inicio < data_fim
        - se ativo=True, desmarcar outros anos ativos
        """
        if self.data_inicio >= self.data_fim:
            raise ValidationError("A data de início deve ser anterior à data de fim.")
        # Verifica unicidade de ativo
        if self.ativo:
            qs = AnoLetivo.objects.filter(ativo=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError("Já existe outro Ano Letivo ativo. Desmarque-o antes de ativar este.")

    def save(self, *args, **kwargs):
        # Caso esteja sendo marcado como ativo, desmarcar os demais
        if self.ativo:
            AnoLetivo.objects.filter(ativo=True).exclude(pk=self.pk).update(ativo=False)
        super().save(*args, **kwargs)

# Opcional: modelo para eventos/feriados acadêmicos vinculados a um ano letivo
class Calendario(models.Model):
    """
    Eventos acadêmicos (feriados, início de período, encerramento, etc.) para cada Ano Letivo.
    """
    ano_letivo = models.ForeignKey(AnoLetivo, on_delete=models.CASCADE, related_name='eventos')
    titulo = models.CharField(max_length=100)
    data = models.DateField()
    descricao = models.TextField(blank=True)

    class Meta:
        ordering = ['data']
        unique_together = ('ano_letivo', 'data', 'titulo')
        verbose_name = "Evento no Calendário"
        verbose_name_plural = "Calendário de Eventos"

    def __str__(self):
        return f"{self.titulo} – {self.data:%d/%m/%Y}"

    def clean(self):
        # Garante que a data do evento esteja dentro do intervalo do ano letivo
        if not (self.ano_letivo.data_inicio <= self.data <= self.ano_letivo.data_fim):
            raise ValidationError("A data do evento deve estar entre o início e o fim do Ano Letivo.")

class Curso(models.Model):
    codigo    = models.CharField(max_length=10, unique=True)
    nome      = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    ativo     = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['codigo']
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'

    def __str__(self):
        return f"{self.codigo} – {self.nome}"

class Turma(models.Model):
    """
    Conjunto de alunos numa série/turno, com disciplinas nucleares.
    """
    NIVEIS_CHOICES = [
        ('10º Ano', '10º Ano'),
        ('11º Ano', '11º Ano'),
        ('12º Ano', '12º Ano'),
        ('13º Ano', '13º Ano'),
    ]
    TURNO_CHOICES = [
        ('MANHÃ', 'Manhã'),
        ('TARDE', 'Tarde'),
        ('NOITE', 'Noite'),
    ]

    nome = models.CharField('Nome da Turma', max_length=50, unique=True)
    nivel = models.CharField('Ano/Nível', max_length=20, choices=NIVEIS_CHOICES)
    turno = models.CharField('Turno', max_length=10, choices=TURNO_CHOICES)
    professor_responsavel = models.CharField(
        'Professor Responsável',
        max_length=150,
        blank=True,
        help_text='Nome ou FK para Colaborador (futuro)'
    )
    ano_letivo = models.ForeignKey(
        AnoLetivo,
        on_delete=models.PROTECT,
        null=False,        # permitir NULO
        blank=True,       # permitir formulário em branco, se usar admin/forms
        related_name="turmas",
    )
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT)

    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Disciplina(models.Model):
    """
    Cada disciplina lecionada no Instituto.
    """
    nome = models.CharField('Nome da Disciplina', max_length=100)
    carga_horaria = models.PositiveIntegerField('Carga Horária (horas/ano)')
    professor_responsavel = models.CharField(
        'Professor Responsável',
        max_length=150,
        blank=True,
        help_text='Nome ou FK para Colaborador (futuro)'
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Disciplina'
        verbose_name_plural = 'Disciplinas'
        unique_together = [['nome']]
        ordering = ['nome']

    def __str__(self):
        return self.nome


class TurmaDisciplina(models.Model):
    """
    Associação N:N entre Turma e Disciplina.
    """
    turma = models.ForeignKey(
        Turma,
        on_delete=models.CASCADE,
        related_name='turma_disciplinas'
    )
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE,
        related_name='disciplina_turmas'
    )
    professor_responsavel = models.CharField(
        'Professor Responsável',
        max_length=150,
        blank=True,
        help_text='Nome ou FK para Colaborador (futuro)',
    )
    ano_letivo = models.ForeignKey(
        AnoLetivo,
        on_delete=models.PROTECT,
        null=False,        # permitir NULO
        blank=True,       # permitir formulário em branco, se usar admin/forms
        related_name="turma_disciplinas",
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Turma-Disciplina'
        verbose_name_plural = 'Turmas-Disciplinas'
        unique_together = [['turma', 'disciplina']]

    def __str__(self):
        return f'{self.turma.nome} – {self.disciplina.nome}'


class Matricula(models.Model):
    """
    Vincula Aluno a uma Turma (ano/série) e registra a data de matrícula.
    """
    STATUS_CHOICES = [
        ('ATIVO', 'ATIVO'),
        ('TRANSFERIDO', 'TRANSFERIDO'),
        ('DESLIGADO', 'DESLIGADO'),
    ]

    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
        related_name='matriculas'
    )
    turma = models.ForeignKey(
        Turma,
        on_delete=models.CASCADE,
        related_name='matriculas'
    )
    ano_letivo = models.ForeignKey(
        AnoLetivo,
        on_delete=models.PROTECT,
        null=False,        # permitir NULO
        blank=True,       # permitir formulário em branco, se usar admin/forms
        related_name="matriculas",
    )
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT, null=True, blank=True)
    data_matricula = models.DateField('Data de Matrícula')
    status = models.CharField('Status', max_length=12, choices=STATUS_CHOICES, default='ATIVO')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        unique_together = [['aluno', 'turma']]
        constraints = [
            # proíbe dois registros com o mesmo aluno no mesmo ano_letivo
            models.UniqueConstraint(
                fields=['aluno', 'ano_letivo'],
                name='unique_matricula_aluno_ano'
            ),
        ]

    def __str__(self):
        return f'{self.aluno.matricula} → {self.turma.nome}'


class Nota(models.Model):
    """
    Armazena as notas (N1, N2, N3), média parcial e final de cada aluno em cada disciplina de uma turma.
    """
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
        related_name='notas'
    )
    turma = models.ForeignKey(
        Turma,
        on_delete=models.CASCADE,
        related_name='notas'
    )
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE,
        related_name='notas'
    )
    ano_letivo = models.ForeignKey(
        AnoLetivo,
        on_delete=models.PROTECT,
        null=False,        # permitir NULO
        blank=True,       # permitir formulário em branco, se usar admin/forms
        related_name="notas",
    )
    nota1 = models.DecimalField('N1', max_digits=5, decimal_places=2, default=0)
    nota2 = models.DecimalField('N2', max_digits=5, decimal_places=2, default=0)
    nota3 = models.DecimalField('N3', max_digits=5, decimal_places=2, default=0)
    media_parcial = models.DecimalField(
        'Média Parcial',
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )
    media_final = models.DecimalField(
        'Média Final',
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )
    SITUACAO_CHOICES = [
        ('APROVADO', 'APROVADO'),
        ('REPROVADO', 'REPROVADO'),
    ]
    situacao = models.CharField(
        'Situação',
        max_length=10,
        choices=SITUACAO_CHOICES,
        blank=True
    )
    observacao = models.TextField('Observação', blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        unique_together = [['aluno', 'turma', 'disciplina']]

    def __str__(self):
        return f'{self.aluno.matricula} | {self.disciplina.nome} | Turma: {self.turma.nome}'

    def calcular_media_parcial(self):
        """
        Média simples de N1, N2 e N3. Deve ser chamada sempre que as notas mudarem.
        """
        self.media_parcial = (self.nota1 + self.nota2 + self.nota3) / 3
        return self.media_parcial

    def calcular_media_final(self, peso1=1, peso2=1, peso3=1):
        """
        Possibilita cálculo com pesos, se necessário. Por default, média simples.
        """
        soma_pesos = peso1 + peso2 + peso3
        self.media_final = (
            (self.nota1 * peso1 + self.nota2 * peso2 + self.nota3 * peso3) / soma_pesos
        )
        # Determina situação conforme média_final ≥ 10
        self.situacao = 'APROVADO' if self.media_final >= 10 else 'REPROVADO'
        return self.media_final
    
    @property
    def situacao_atual(self):
        # só para exibição — não salva no banco
        media = (self.nota1 + self.nota2 + self.nota3) / 3
        return 'APROVADO' if media >= 10 else 'REPROVADO'
    
    def save(self, *args, **kwargs):
        # recalcula sempre que for salvo
        self.calcular_media_parcial()
        # chamar sem pesos para usar média simples e definir self.situacao
        self.calcular_media_final()
        super().save(*args, **kwargs)

class Boletim(models.Model):
    """
    Registro de geração de boletins trimestrais. Armazena apenas metadados e caminho do PDF.
    """
    turma = models.ForeignKey(
        Turma,
        on_delete=models.CASCADE,
        related_name='boletins'
    )
    trimestre = models.PositiveSmallIntegerField('Trimestre', choices=[(1, '1º'), (2, '2º'), (3, '3º')])
    arquivo_pdf = models.FileField(
        'Arquivo Boletim (PDF)',
        upload_to='pedagogico/boletins/',
        blank=True,
        null=True
    )
    gerado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='boletins_gerados',
        null=True,
        verbose_name='Gerado por'
    )
    data_geracao = models.DateTimeField('Data de Geração', auto_now_add=True)

    class Meta:
        verbose_name = 'Boletim'
        verbose_name_plural = 'Boletins'
        unique_together = [['turma', 'trimestre']]

    def __str__(self):
        return f'Boletim {self.trimestre}º – {self.turma.nome}'

class PreRematricula(models.Model):
    """
    Solicitação de Rematrícula de um aluno já matriculado para o próximo ano letivo.
    """
    STATUS_CHOICES = [
        ('PENDENTE','Pendente'),
        ('APROVADA','Aprovada'),
        ('RECUSADA','Recusada'),
    ]

    aluno          = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    turma_origem   = models.ForeignKey(Turma, on_delete=models.PROTECT, related_name='rematriculas_origem')
    curso_origem   = models.ForeignKey(Curso, on_delete=models.PROTECT)
    ano_origem     = models.ForeignKey(AnoLetivo, on_delete=models.PROTECT, related_name='+')
    data_solic     = models.DateTimeField(auto_now_add=True)
    status         = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDENTE')

    class Meta:
        verbose_name = 'Pré‑Rematrícula'
        verbose_name_plural = 'Pré‑Rematrículas'
        ordering = ['-data_solic']

    def __str__(self):
        return f"{self.aluno} ({self.turma_origem}) → {self.status}"
