from datetime import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()

class Colaborador(models.Model):
    """
    Funcionários da instituição (professores, pessoal administrativo, etc.).
    """
    DEPARTAMENTO_CHOICES = [
        ('RH', 'Recursos Humanos'),
        ('TESOURARIA', 'Tesouraria'),
        ('PATRIMONIO', 'Patrimônio'),
        ('CONTABILIDADE', 'Contabilidade'),
        ('SUBDIRECAO PEDAGOGICA', 'Subdireção Pedagógica'),
        ('SUBDIRECAO ADMINISTRATIVA', 'Subdireção Administrativa'),
        ('DIRCAO GERAL', 'Direção Geral'),
        ('OUTRO', 'Outro'),
    ]
    STATUS_CHOICES = [
        ('ATIVO', 'ATIVO'),
        ('INATIVO', 'INATIVO'),
    ]

    nome = models.CharField('Nome Completo', max_length=150)
    documento = models.CharField('Documento (BI)', max_length=50, unique=True)
    cargo = models.CharField('Cargo', max_length=100)
    departamento = models.CharField('Departamento', max_length=32, choices=DEPARTAMENTO_CHOICES)
    data_admissao = models.DateField('Data de Admissão')
    salario_base = models.DecimalField('Salário Base', max_digits=12, decimal_places=2)
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)
    status = models.CharField('Status', max_length=10, choices=STATUS_CHOICES, default='ATIVO')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Colaborador'
        verbose_name_plural = 'Colaboradores'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} ({self.cargo})'


class Salario(models.Model):
    """
    Registro mensal de cálculo de salário de um colaborador.
    """
    colaborador = models.ForeignKey(
        Colaborador,
        on_delete=models.CASCADE,
        related_name='salarios'
    )
    mes_referencia = models.CharField(
        max_length=7,  # Formato: "YYYY-MM"
        validators=[
            RegexValidator(
                regex=r'^\d{4}-\d{2}$',
                message="Formato deve ser YYYY-MM (ex: 2025-04)"
            )
        ]
    )
    data_referencia = models.DateField(null=True, blank=True)  # Novo campo
    horas_extras = models.DecimalField('Horas Extras', max_digits=5, decimal_places=2, default=0)
    descontos = models.DecimalField('Descontos', max_digits=12, decimal_places=2, default=0)
    bonificacoes = models.DecimalField('Bonificações', max_digits=12, decimal_places=2, default=0)
    salario_bruto = models.DecimalField('Salário Bruto', max_digits=12, decimal_places=2, blank=True, null=True)
    inss = models.DecimalField('INSS', max_digits=12, decimal_places=2, blank=True, null=True)
    irt = models.DecimalField('IRT', max_digits=12, decimal_places=2, blank=True, null=True)
    salario_liquido = models.DecimalField('Salário Líquido', max_digits=12, decimal_places=2, blank=True, null=True)
    arquivo_holerite = models.FileField(
        'Holerite (PDF)',
        upload_to='administrativo/holerites/',
        blank=True,
        null=True
    )
    processado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='salarios_processados',
        null=True,
        verbose_name='Processado por'
    )
    data_processamento = models.DateTimeField('Data de Processamento', auto_now_add=True)

    def mes_formatado(self):
        meses = {
            "01": "Janeiro", "02": "Fevereiro", "03": "Março",
            "04": "Abril", "05": "Maio", "06": "Junho",
            "07": "Julho", "08": "Agosto", "09": "Setembro",
            "10": "Outubro", "11": "Novembro", "12": "Dezembro"
        }
        try:
            ano, mes = self.mes_referencia.split('-')
            return f"{meses[mes]} de {ano}"
        except:
            return self.mes_referencia

    def save(self, *args, **kwargs):
        # Preenche automaticamente data_referencia
        if self.mes_referencia:
            # Use o datetime importado corretamente
            self.data_referencia = datetime.strptime(self.mes_referencia + '-01', '%Y-%m-%d').date()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Salário'
        verbose_name_plural = 'Salários'
        unique_together = [['colaborador', 'mes_referencia']]

    def __str__(self):
        return f'{self.colaborador.nome} – {self.mes_referencia:%b/%Y}'


class BemPatrimonio(models.Model):
    """
    Bens patrimoniais da instituição, com cálculo de depreciação.
    """
    CATEGORIA_CHOICES = [
        ('MOVEIS', 'Móveis'),
        ('EQUIPAMENTOS', 'Equipamentos'),
        ('VEICULOS', 'Veículos'),
        ('IMÓVEIS', 'Imóveis'),
        ('OUTRO', 'Outro'),
    ]

    descricao = models.CharField('Descrição', max_length=200)
    categoria = models.CharField('Categoria', max_length=20, choices=CATEGORIA_CHOICES)
    valor_aquisicao = models.DecimalField('Valor de Aquisição', max_digits=12, decimal_places=2)
    data_aquisicao = models.DateField('Data de Aquisição')
    vida_util_anos = models.PositiveIntegerField('Vida Útil (anos)')
    localizacao = models.CharField('Localização', max_length=150, blank=True)
    depreciacao_acumulada = models.DecimalField(
        'Depreciação Acumulada',
        max_digits=12,
        decimal_places=2,
        default=0
    )
    valor_contabil_liquido = models.DecimalField(
        'Valor Contábil Líquido',
        max_digits=12,
        decimal_places=2,
        default=0
    )
    arquivo_documento = models.FileField(
        'Arquivo Nota Fiscal',
        upload_to='administrativo/patrimonio/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Bem de Patrimônio'
        verbose_name_plural = 'Bens de Patrimônio'
        ordering = ['-data_aquisicao']

    def __str__(self):
        return f'{self.descricao} ({self.categoria})'

    def save(self, *args, **kwargs):
        # Não chame self.save() aqui! Isso causaria recursão
        # Se precisar de pré-processamento, faça antes de chamar super()
        
        # Exemplo correto:
        if not self.pk:  # Se for um novo objeto
            self.calcular_depreciacao()
            
        super().save(*args, **kwargs)

    def calcular_depreciacao(self, data_referencia=None):
        """
        Recalcula depreciacao_acumulada e valor_contabil_liquido com base na data de referência.
        Se data_referencia for None, utiliza hoje.
        """
        from datetime import date

        if data_referencia is None:
            data_referencia = date.today()
        
        # Evitar divisão por zero
        if self.vida_util_anos == 0:
            self.depreciacao_acumulada = 0
            self.valor_contabil_liquido = self.valor_aquisicao
            return self.valor_contabil_liquido

        meses_total = self.vida_util_anos * 12
        meses_passados = (data_referencia.year - self.data_aquisicao.year) * 12 + (data_referencia.month - self.data_aquisicao.month)
        meses_passados = max(0, min(meses_passados, meses_total))
        
        # Verificação adicional para meses_total = 0
        if meses_total == 0:
            self.depreciacao_acumulada = 0
            self.valor_contabil_liquido = self.valor_aquisicao
            return self.valor_contabil_liquido

        depreciacao_mensal = self.valor_aquisicao / meses_total
        self.depreciacao_acumulada = depreciacao_mensal * meses_passados
        self.valor_contabil_liquido = self.valor_aquisicao - self.depreciacao_acumulada
        
        # Garantir não ficar negativo:
        if self.valor_contabil_liquido < 0:
            self.valor_contabil_liquido = 0
        
        return self.valor_contabil_liquido


class LancamentoContabil(models.Model):
    """
    Lançamento contábil (partidas dobradas).
    """
    data_lancamento = models.DateField('Data do Lançamento')
    conta_debito = models.CharField('Conta Débito', max_length=100)
    conta_credito = models.CharField('Conta Crédito', max_length=100)
    valor = models.DecimalField('Valor', max_digits=12, decimal_places=2)
    descricao = models.TextField('Descrição')
    lancado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='lancamentos_contabeis',
        null=True,
        verbose_name='Lançado por'
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Lançamento Contábil'
        verbose_name_plural = 'Lançamentos Contábeis'
        ordering = ['-data_lancamento']

    def __str__(self):
        return f'{self.data_lancamento:%d/%m/%Y} | {self.valor} AKZ'
