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
        max_length=10,
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

    numero = models.CharField('Número da Fatura', max_length=20, unique=True)
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
        related_name='faturas',
        verbose_name='Aluno'
    )
    tipo = models.CharField('Tipo', max_length=15, choices=TIPO_CHOICES)
    valor_original = models.DecimalField('Valor Original', max_digits=12, decimal_places=2)
    valor_atual = models.DecimalField('Valor Atual', max_digits=12, decimal_places=2)
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
