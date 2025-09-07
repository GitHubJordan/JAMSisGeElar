from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class Encarregado(models.Model):
    """
    Pessoa responsável financeiramente pelo(s) aluno(s).
    """
    GRAU_PARENTESCO_CHOICES = [
        ('Pai', 'Pai'),
        ('Mãe', 'Mãe'),
        ('Tio', 'Tio'),
        ('Tia', 'Tia'),
        ('Avô', 'Avô'),
        ('Avó', 'Avó'),
        ('Outro', 'Outro'),
    ]

    nome = models.CharField('Nome', max_length=150)
    telefone = models.CharField('Telemóvel', max_length=20, unique=True)
    email = models.EmailField('E-mail', blank=True)
    endereco = models.CharField('Endereço', max_length=250)
    grau_parentesco = models.CharField(
        'Grau de Parentesco',
        max_length=20,
        choices=GRAU_PARENTESCO_CHOICES
    )
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Encarregado'
        verbose_name_plural = 'Encarregados'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} ({self.telefone})'


class Aluno(models.Model):
    """
    Dados do aluno matriculado.
    """
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]
    STATUS_CHOICES = [
        ('ATIVO', 'ATIVO'),
        ('INATIVO', 'INATIVO'),
        ('SUSPENSO', 'Suspenso'),
        ('TRANCADO', 'Trancado'),
        ('FORMADO', 'Formado'),
        ('TRANSFERIDO', 'Transferido'),
        ('DESISTENTE', 'Desistente'),
    ]

    nome = models.CharField('Nome', max_length=150)
    data_nascimento = models.DateField('Data de Nascimento')
    genero = models.CharField('Gênero', max_length=1, choices=GENERO_CHOICES)
    endereco = models.CharField('Endereço', max_length=250)
    documento = models.CharField('Documento (RG/BI)', max_length=50, unique=True)
    foto = models.ImageField(
        'Foto',
        upload_to='students/photos/',
        blank=True,
        null=True
    )
    observacoes = models.TextField('Observações', blank=True)
    encarregado = models.ForeignKey(
        Encarregado,
        on_delete=models.PROTECT,
        related_name='alunos',
        verbose_name='Encarregado'
    )
    matricula = models.CharField(
        'Matrícula',
        max_length=20,
        unique=True,
        help_text='Gerada automaticamente'
    )
    status = models.CharField(
        'Status',
        max_length=12,
        choices=STATUS_CHOICES,
        default='ATIVO'
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'
        ordering = ['matricula']

    def __str__(self):
        return f'{self.matricula} - {self.nome}'

class Servico(models.Model):
    codigo     = models.CharField(max_length=10, unique=True)
    descricao  = models.CharField(max_length=100)
    preco      = models.DecimalField(max_digits=10, decimal_places=2)
    ativo      = models.BooleanField(default=True)
    criado_em  = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['codigo']
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'

    def __str__(self):
        return f"{self.codigo} – {self.descricao} (AOA {self.preco})"

class FaturaServico(models.Model):
    fatura  = models.ForeignKey('Fatura', on_delete=models.CASCADE)
    servico = models.ForeignKey(Servico, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField(default=1)
    valor_unitario = models.DecimalField(
        'Valor Unitário',
        max_digits=10,
        decimal_places=2,
        default=0
    )

    class Meta:
        unique_together = ('fatura','servico')

    def subtotal(self):
        return self.servico.preco * self.quantidade

class Fatura(models.Model):
    """
    Cobranças emitidas para um aluno (mensalidades, matrículas, etc.).
    """
    TIPO_CHOICES = [
        ('MENSALIDADE', 'Mensalidade'),
        ('MATRICULA', 'Matrícula'),
        ('MATERIAL', 'Material Didático'),
        ('OUTRO', 'Outro'),
    ]
    STATUS_CHOICES = [
        ('PENDENTE', 'PENDENTE'),
        ('VENCIDO', 'VENCIDO'),
        ('PAGO', 'PAGO'),
    ]

    numero = models.CharField('Número da Fatura', max_length=20, unique=True, blank=True, null=True)
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
        related_name='faturas',
        verbose_name='Aluno'
    )
    tipo = models.CharField('Tipo', max_length=15, choices=TIPO_CHOICES)
    itens = models.ManyToManyField(Servico, through=FaturaServico)
    valor_original = models.DecimalField('Valor Original', max_digits=12, decimal_places=2)
    valor_atual = models.DecimalField('Valor Atual', max_digits=12, decimal_places=2, blank=True, null=True)
    data_emissao = models.DateField('Data de Emissão')
    data_vencimento = models.DateField('Data de Vencimento')
    status = models.CharField('Status', max_length=10, choices=STATUS_CHOICES, default='PENDENTE')
    observacoes = models.TextField('Observações', blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Fatura'
        verbose_name_plural = 'Faturas'
        ordering = ['-data_emissao']

    def __str__(self):
        return f'{self.numero} | {self.aluno.matricula} | {self.status}'


class Recibo(models.Model):
    """
    Recibo gerado quando a fatura é paga.
    """
    FORMA_PAGAMENTO_CHOICES = [
        ('DINHEIRO', 'Dinheiro'),
        ('TRANSFERÊNCIA', 'Transferência Bancária'),
        ('CHEQUE', 'Cheque'),
        ('OUTRO', 'Outro'),
    ]

    fatura = models.OneToOneField(
        Fatura,
        on_delete=models.CASCADE,
        related_name='recibo',
        verbose_name='Fatura'
    )
    numero_recibo = models.CharField('Número do Recibo', max_length=20, unique=True)
    data_pagamento = models.DateField('Data de Pagamento')
    forma_pagamento = models.CharField(
        'Forma de Pagamento',
        max_length=15,
        choices=FORMA_PAGAMENTO_CHOICES
    )
    valor_pago = models.DecimalField('Valor Pago', max_digits=12, decimal_places=2)
    observacoes = models.TextField('Observações', blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Recibo'
        verbose_name_plural = 'Recibos'
        ordering = ['-data_pagamento']

    def __str__(self):
        return f'{self.numero_recibo} | {self.fatura.numero}'

class PreMatricula(models.Model):
    aluno      = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    curso      = models.ForeignKey('pedagogico.Curso', on_delete=models.PROTECT)
    data_solic = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [('PENDENTE','Pendente'),('APROVADA','Aprovada'),('RECUSADA','Recusada')]
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDENTE')

    class Meta:
        ordering = ['-data_solic']
        verbose_name = 'Pré‑Matrícula'
        verbose_name_plural = 'Pré‑Matrículas'

    def __str__(self):
        return f"{self.aluno} → {self.curso} [{self.status}]"


class ContaCorrente(models.Model):
    """
    Consolida débitos e créditos de um aluno.
    """
    aluno = models.OneToOneField(
        Aluno,
        on_delete=models.CASCADE,
        related_name='conta_corrente',
        verbose_name='Aluno'
    )
    total_debito = models.DecimalField('Total de Débito', max_digits=12, decimal_places=2, default=0)
    total_credito = models.DecimalField('Total de Crédito', max_digits=12, decimal_places=2, default=0)
    saldo = models.DecimalField('Saldo', max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Conta Corrente'
        verbose_name_plural = 'Contas Correntes'

    def __str__(self):
        return f'{self.aluno.matricula} | Saldo: {self.saldo}'

    def recalcular_saldo(self):
        """
        Atualiza os campos total_debito, total_credito e saldo consultando faturas e recibos.
        Deve ser chamado sempre que Fatura ou Recibo mudar.
        """
        faturas = self.aluno.faturas.all()
        self.total_debito = sum([f.valor_atual for f in faturas if f.status in ['PENDENTE', 'VENCIDO']])
        recibos = [f.recibo.valor_pago for f in faturas if hasattr(f, 'recibo')]
        self.total_credito = sum(recibos)
        self.saldo = self.total_debito - self.total_credito
        self.save()

