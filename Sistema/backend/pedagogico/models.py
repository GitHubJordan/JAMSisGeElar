from django.db import models
from accounts.models import User
from secretaria.models import Aluno

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
    data_matricula = models.DateField('Data de Matrícula')
    status = models.CharField('Status', max_length=12, choices=STATUS_CHOICES, default='ATIVO')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        unique_together = [['aluno', 'turma']]

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
        # Determina situação conforme média_final ≥ 60
        self.situacao = 'APROVADO' if self.media_final >= 60 else 'REPROVADO'
        return self.media_final


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
