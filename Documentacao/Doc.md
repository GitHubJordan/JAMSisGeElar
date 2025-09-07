# Documentação do Desenvolvimento do Sistema JAMSisGeElar

## Sumário

1. [Introdução](#introdução)
2. [Organização Geral da Documentação](#organização-geral-da-documentação)
3. [Visão Geral do Projeto](#visão-geral-do-projeto)
4. [Plano de Desenvolvimento Detalhado](#plano-de-desenvolvimento-detalhado)

   * [Dia 1–7: Planejamento e Setup Inicial](#dia-1-7-planejamento-e-setup-inicial)
   * [Dia 8–10: Wireframes e Prototipação](#dia-8-10-wireframes-e-prototipação)
   * [Dia 11–14: Módulo Core](#dia-11-14-módulo-core)
   * [Dia 15–16: Integração e Ajustes](#dia-15-16-integração-e-ajustes)
   * [Dia 17–18: Revisão de Progresso](#dia-17-18-revisão-de-progresso)
   * [Dia 19–20: Finalização do Core](#dia-19-20-finalização-do-core)
   * [Dia 21: Ano Letivo e Calendário](#dia-21-ano-letivo-e-calendário)
   * [Dia 22: Filtragem por Ano Letivo & Relatório Acadêmico](#dia-22-filtragem-por-ano-letivo--relatório-acadêmico)
   * [Dia 23: Exercícios & Notificações Agendadas](#dia-23-exercícios--notificações-agendadas)
   * [Dia 24: Contexto Global & Refatoração de Views](#dia-24-contexto-global--refatoração-de-views)
   * [Dia 25: Serviços & Tabela de Preços na Secretaria](#dia-25-serviços--tabela-de-preços-na-secretaria)
   * [Dia 26: Cursos & Fluxo de Pré‑Matrícula](#dia-26-cursos--fluxo-de-pré‑matrícula)
   * [Dia 27: Controle de Sessão & Logs de Acesso](#dia-27-controle-de-sessão--logs-de-acesso)
   * [Dia 28: Relatórios & Exportações](#dia-28-relatórios--exportações)
5. [Próximos Passos](#próximos-passos)
6. [Apêndices](#apêndices)

---

## Introdução

Este documento descreve de forma sistemática todo o processo de desenvolvimento do sistema de gestão escolar **JAMSisGeElar**, seguindo o planejamento em cascata de **Dia 1** até **Dia 28**. O objetivo é servir como guia para novos desenvolvedores e stakeholders acompanharem o histórico de decisões, implementações e entregas.

## Organização Geral da Documentação

* **Seções Principais**: correspondem às fases (Dias) do cronograma.
* **Sumário em Markdown**: navegação rápida por tópicos.
* **Detalhamento de Cada Fase**: objetivos, artefatos gerados, migrações, comandos, views, templates e testes.

## Visão Geral do Projeto

* **Nome**: JAMSisGeElar v1.0.0
* **Objetivo**: sistema de gestão escolar para Instituto Médio Técnico Cecília Domingos, com módulos de Core, Pedagógico, Secretaria e Administrativo.
* **Stack**: Django, PostgreSQL, WeasyPrint, pandas/openpyxl, NSSM.
* **Metodologia**: Cascata, com entregas diárias (Dia 1–30).

## Plano de Desenvolvimento Detalhado

### Dia 1–7: Planejamento e Setup Inicial

**Objetivos**:

* Definição de requisitos funcionais e não funcionais.
* Modelagem inicial (ER diagram).
* Configuração do ambiente de desenvolvimento (venv, settings, banco).

**Artefatos**:

* Documento de requisitos.
* Diagrama ER e wireframes de alta fidelidade.

### Dia 8–10: Wireframes e Prototipação

**Objetivos**:

* Criação de protótipos de telas (login, dashboard, sidebar, topbar).
* Feedback e ajustes nos fluxos de navegação.

**Artefatos**:

* Figma/Sketch wireframes.
* Documento de mudanças após validação.

### Dia 11–14: Módulo Core

**Objetivos**:

* Implementar `ConfiguracaoInicial`, backup manual/automático e logs.
* Middleware de captura de erros.

**Artefatos**:

* `core/models.py`: `ConfiguracaoInicial`, `BackupLog`, `ErrorLog`, `NotificationLog`.
* Formulários e views MVC.
* Comando `backup_database`.
* Templates: configuração, backup, errorlog, notificationlog.

### Dia 15–16: Integração e Ajustes

**Objetivos**:

* Empacotar Django como serviço Windows via NSSM.
* Ajustes na UI conforme feedback.

**Artefatos**:

* Configuração NSSM.
* Atualização de rotas e templates.

### Dia 17–18: Revisão de Progresso

**Objetivos**:

* Revisar roadmap, priorizar ajustes.

**Artefatos**:

* Documento de backlog atualizado.

### Dia 19–20: Finalização do Core

**Objetivos**:

* Concluir funcionalidades de backup, logs de notificação, integração SMTP/WhatsApp.

**Artefatos**:

* `core/utils.py`: `send_email`, `send_whatsapp`.
* Ajustes finais em views e templates.

### Dia 21: Ano Letivo e Calendário

**Objetivos**:

* Criar `AnoLetivo` e `Calendario` com validações de data e unicidade.

**Artefatos**:

* `pedagogico/models.py`, forms, views, URLs e templates correspondentes.

### Dia 22: Filtragem por Ano Letivo & Relatório Acadêmico

**Objetivos**:

* Associar `ano_letivo` em Turma, Matrícula, Nota e criar mixin de contexto.
* Relatório acadêmico com PDF.

**Artefatos**:

* `core/mixins.py`: `AnoContextMixin`.
* Ajustes nas views e templates de pedagogico.

### Dia 23: Exercícios & Notificações Agendadas

**Objetivos**:

* Implementar `Exercicio` e comando `exercicio_switch`.
* Comando `notify_overdue_invoices` e agendamento via NSSM.

**Artefatos**:

* `core/models.py`, `management/commands`.
* `secretaria/management/commands/notify_overdue_invoices.py`.

### Dia 24: Contexto Global & Refatoração de Views

**Objetivos**:

* Context Processor `exercicio_atual`.
* Middleware `AnoLetivoMiddleware`.
* Mixin `AnoContextMixin` para views.

**Artefatos**:

* Ajustes em `settings.py`, `core/context_processors.py`, `core/middleware.py`, `core/mixins.py`.

### Dia 25: Serviços & Tabela de Preços na Secretaria

**Objetivos**:

* Modelo `Servico` e CRUD (Admin/Diretor).
* Integração com faturas via `FaturaServico`.

**Artefatos**:

* `secretaria/models.py`, forms, views, templates, inline formset.

### Dia 26: Cursos & Fluxo de Pré‑Matrícula

**Objetivos**:

* CRUD de `Curso`.
* FK em Turma/Matricula.
* Modelo `PreMatricula` e fluxo colaborativo.

**Artefatos**:

* `pedagogico/models.py`, `secretaria/models.py`, views e templates.

### Dia 27: Controle de Sessão & Logs de Acesso

**Objetivos**:

* Middleware `InactivityLogoutMiddleware`.
* Modelo `AccessLog` e signals de login/logout.

**Artefatos**:

* `core/middleware.py`, `core/models.py`, `core/signals.py`, views/templates de logs.

### Dia 28: Relatórios & Exportações

**Objetivos**:

* Relatórios de Faturas (Excel), Salários (Excel/PDF) e Relatório Acadêmico (Excel/PDF).

**Artefatos**:

* Views e templates em `secretaria`, `administrativo`, `pedagogico`; uso de pandas e WeasyPrint.

## Próximos Passos (Dias 29–30)

1. **Testes Automatizados** (unitários e mocks).
2. **Testes Funcionais** (Playwright/Selenium).
3. **UX/UI Final** (responsividade, animações, breadcrumbs).
4. **Deploy** (documentação NSSM, firewall, variáveis).
5. **Documentação Final** (README, manual do usuário, wiki).

## Apêndices

* **Glossário de Termos**
* **Referências Técnicas** (Django docs, pandas, WeasyPrint, NSSM)
* **Links Úteis** (repositório, tickets, wiki interna)
