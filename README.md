# 📄 One Page Generator: Co-Pilot para Relatórios Industriais

[![Clean Architecture](https://img.shields.io/badge/Architecture-Clean%20Architecture-blue.svg)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
[![Clean Code](https://img.shields.io/badge/Code-Clean%20Code-green.svg)](#-skills-de-agente-instaladas-no-projeto)
[![Docker](https://img.shields.io/badge/Architecture-100%25%20Dockerized-2496ED.svg?logo=docker&logoColor=white)](#-arquitetura-100-dockerizada-zero-bare-metal)
[![Standard](https://img.shields.io/badge/Format-ISO%20216%20A4%20Strict-orange.svg)](#-engine-de-layout-a4-e-detecção-de-overflow)
[![Local-First AI](https://img.shields.io/badge/AI-100%25%20On--Premise%20Private-purple.svg)](#-motor-cognitivo-e-topologia-de-hardware)
[![Rust Axum](https://img.shields.io/badge/Backend%20V2-Rust%20Axum-DEA584.svg?logo=rust&logoColor=white)](#-roadmap-de-escala-futura-v2)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%2016-336791.svg?logo=postgresql&logoColor=white)](#-roadmap-de-escala-futura-v2)
[![License](https://img.shields.io/badge/License-MIT-gray.svg)](LICENSE)

> Plataforma inteligente para ingestão de propostas complexas de PD&I (FINEP, FAPESP, Embrapii), avaliação de completude, edição visual em página única A4 e exportação vetorial em PDF de alta fidelidade sem quebra de layout.

---

## 🎯 Visão Geral do Sistema

A submissão de propostas em órgãos de fomento à inovação industrial (como **FINEP**, **FAPESP**, **SENAI**, **SESI**, **FIESC** e **IEL**) envolve planos de trabalho volumosos de dezenas de páginas. Executivos e avaliadores demandam frequentemente um **One Page Report** sintético, denso e visualmente padronizado.

O **One Page Generator** atua como um co-pilot de engenharia e redação técnica que:
1. **Ingere e Extrai Documentos Heterogêneos**: Processa PDFs complexos, digitalizados ou com fontes corrompidas via pipeline híbrido com índice de sanidade ($TSI$).
2. **Avalia Lacunas (Gap Assessment)**: Diagnostica seções ausentes e formula perguntas direcionadas para completar a proposta.
3. **Oferece Edição WYSIWYG A4 Estrita**: Renderiza a proposta no formato A4 ($210\text{mm} \times 297\text{mm}$) com monitoramento contínuo de overflow via `ResizeObserver`.
4. **Condensa e Reescreve com IA Local**: Permite regeneração localizada de blocos e condensação sintática preservando termos técnicos e números orçamentários.
5. **Exporta em PDF Vetorial Impecável**: Gera o PDF de página única exata via Headless Chromium (Puppeteer) com regras estritas de CSS Paged Media.

---

## 🐳 Arquitetura 100% Dockerizada (Zero Bare-Metal)

> ⚠️ **DIRETRIZ INVIOLÁVEL DE ENGENHARIA**: Todos os serviços da aplicação operam **estritamente em containers Docker**. É terminantemente proibida a execução direta (*bare-metal*) de Ollama, vLLM, Python, Node ou PostgreSQL no sistema operacional do host. A aceleração por GPU opera via **NVIDIA Container Toolkit**.

### Topologia de Containers:

| Serviço / Container | Imagem Base | Porta Exposta | Responsabilidade |
|---|---|---|---|
| `onepage_frontend_dev` | Node 20 / Alpine | `3000:3000` | Interface SPA React 19 com Hot-Reload montado em volume |
| `onepage_backend_dev` | Python 3.11-slim | `8000:8000` | API FastAPI, PyMuPDF e docTR (CPU isolada para evitar OOM) |
| `onepage_ollama_dev` | `ollama/ollama:latest` | `11434:11434` | Runtime de inferência local com GPU Passthrough (RTX Ada 1000 - 6GB) |
| `onepage_postgres_dev` | `postgres:16-alpine` | `5432:5432` | Banco relacional com volume persistente para modelos, usuários e rascunhos |
| `onepage_llm_prod` | `vllm/vllm-openai` | `8001:8000` | Servidor corporativo de produção para Nemotron-70B em RTX 3090 (24GB) |

---

## 🏛️ Arquitetura do Sistema (Clean Architecture)

O projeto adota os princípios de **Clean Architecture** (Robert C. Martin) e o padrão **Ports & Adapters (Hexagonal)**, garantindo independência de frameworks, testabilidade total e inversão de dependências (DIP):

```
                      +-------------------------------------------------------------+
                      |                 4. FRAMEWORKS & DRIVERS                     |
                      |   FastAPI / Axum | React 19 / Vite | Ollama | vLLM | Postgres|
                      +------------------------------+------------------------------+
                                                     |
                                                     v
                      +-------------------------------------------------------------+
                      |                  3. INTERFACE ADAPTERS                      |
                      |   REST Controllers | OllamaAdapter | VllmAdapter            |
                      |   HybridPdfExtractor | PuppeteerPdfAdapter | SqlxRepository |
                      +------------------------------+------------------------------+
                                                     |
                                                     v
                      +-------------------------------------------------------------+
                      |                 2. APPLICATION USE CASES                    |
                      |   IngestDocumentUseCase | AssessReportGapsUseCase           |
                      |   CondenseSectionUseCase | ExportPdfUseCase | Ports (APIs)  |
                      +------------------------------+------------------------------+
                                                     |
                                                     v
                      +-------------------------------------------------------------+
                      |                     1. DOMAIN ENTITIES                      |
                      |   OnePageReport | SectionContent | BudgetFinep              |
                      |   LayoutMetrics | ComplianceRule | Value Objects            |
                      +-------------------------------------------------------------+
```

---

## 🚀 Roadmap de Escala Futura (V2)

A evolução para a escala corporativa está formalmente especificada em [`docs/specs/SPEC-future-scale.md`](file:///c:/workspace/one_page_generator/docs/specs/SPEC-future-scale.md) e compreende:

1. **Backend de Alta Performance em Rust (Axum)**:
   - Migração do orquestrador para **Rust (Axum + Tokio + Tower)** para ultra performance, segurança estrita de memória e latência de leitura $< 15\text{ms}$.
2. **Persistência Relacional em PostgreSQL com Migrations**:
   - Controle de esquema determinístico com **`sqlx-cli`** com migrations versionadas e idempotentes (`up`/`down`).
   - Tabelas estruturadas: `users`, `user_profiles`, `user_preferences`, `report_templates`, `project_drafts` e `archived_documents`.
3. **Arquivamento Auditável de Documentos**:
   - Armazenamento com cálculo obrigatório de hash **SHA-256** para auditoria e garantia de conformidade técnica com órgãos financiadores.
4. **Salvamento de Projetos e Rascunhos em Nuvem**:
   - Persistência atrelada à conta do usuário com controle de versionamento e suporte a recuperação offline.
5. **Autenticação Segura & Gestão de Contas**:
   - Login tradicional com **E-mail / Senha** (hash seguro via `Argon2id`).
   - Social Login com **Google OAuth 2.0 / OpenID Connect**.
   - Fluxo de **complemento de perfil opcional** pós-login (unidade SENAI, instituição parceira, cargo).
   - Sessões protegidas com Refresh Tokens em cookies `HttpOnly` com CSRF protection.
6. **Configuração de Usuário: Modo Claro e Modo Escuro (UI)**:
   - **Tema da Aplicação**: Alternância entre Modo Claro (`light`) e Escuro (`dark`) nas preferências do usuário para menus, modais e barra de ferramentas.
   - **Tema do Documento A4**: Preservação inviolável da folha física A4 sobre **fundo branco ($#FFFFFF$)**, garantindo que o dark mode da interface nunca afete as cores oficiais da impressão.

---

## 🛠️ Skills de Agente Instaladas no Projeto

As seguintes skills especializadas estão instaladas no repositório (`.agents/skills/`) via [skills.sh](https://www.skills.sh/) para apoiar o ciclo completo de desenvolvimento e governança:

*   [`spec-driven-development`](file:///.agents/skills/spec-driven-development/SKILL.md): Fluxo metodológico em 4 fases com gates de aceitação (*Specify $\rightarrow$ Plan $\rightarrow$ Tasks $\rightarrow$ Implement*).
*   [`clean-code`](file:///.agents/skills/clean-code/SKILL.md): Princípios SOLID, refatoração de code smells, limites de complexidade e padrão *Result Type*.
*   [`clean-architecture`](file:///.agents/skills/clean-architecture/SKILL.md): Decomposição em 4 camadas concêntricas e Inversão de Dependências (DIP).
*   [`axum-web-framework`](file:///.agents/skills/axum-web-framework/SKILL.md): Boas práticas para desenvolvimento do backend de escala em Rust com Axum.
*   [`database-schema-design`](file:///.agents/skills/database-schema-design/SKILL.md): Modelagem de banco de dados relacional, estratégias de indexação e migrations.
*   [`oauth-implementation`](file:///.agents/skills/oauth-implementation/SKILL.md): Fluxos de autorização OAuth 2.0, OpenID Connect e integração Google.
*   [`security-review`](file:///.agents/skills/security-review/SKILL.md): Auditoria de vulnerabilidades, hash de senhas e gestão de segredos.
*   [`pdf-processing`](file:///.agents/skills/pdf-processing/SKILL.md): Padrões de manipulação, extração tabular e renderização de PDFs.
*   [`senior-architect`](file:///.agents/skills/senior-architect/SKILL.md): Governança de ADRs e decisões arquiteturais.
*   [`ui-design-system`](file:///.agents/skills/ui-design-system/SKILL.md): Design tokens, temas claro/escuro e componentes reativos.

---

## 📂 Estrutura do Repositório

```
one_page_generator/
├── .agents/
│   └── skills/                 # Skills do agente no formato de projeto (skills.sh)
├── backend/                    # Core Python (FastAPI / docTR / PyMuPDF)
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   ├── src/
│   └── tests/
├── frontend/                   # Interface Web (React 19 + TypeScript)
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   ├── src/
│   └── tests/
├── docs/                       # Documentação Técnica e Especificações
│   ├── research.md             # Análise de viabilidade original
│   ├── masterplan.md           # Masterplan Arquitetural Completo
│   └── specs/                  # Especificações Formais SDD
│       ├── capability-map.md
│       ├── SPEC-domain-core.md
│       ├── SPEC-document-ingestion.md
│       ├── SPEC-cognitive-engine.md
│       ├── SPEC-layout-editor.md
│       ├── SPEC-pdf-export.md
│       ├── SPEC-orchestrator-api.md
│       └── SPEC-future-scale.md
├── docker-compose.yml          # Orquestração de Containers em Produção
├── docker-compose.dev.yml      # Orquestração de Containers em Desenvolvimento
├── LICENSE
└── README.md
```

---

## 🚀 Como Executar o Projeto (Docker-First)

### Pré-requisitos
- **Docker** 24+ e **Docker Compose** v2+
- **NVIDIA Container Toolkit** (para aceleração por GPU no Ollama/vLLM)

### 1. Inicializar Todos os Serviços em Modo de Desenvolvimento
```bash
# Sobe Frontend, Backend, PostgreSQL e Ollama em containers isolados
docker compose -f docker-compose.dev.yml up -d
```

### 2. Configurar o Modelo de IA no Container Ollama
```bash
# Baixar o modelo Qwen2.5-7B diretamente dentro do container
docker compose -f docker-compose.dev.yml exec ollama ollama pull qwen2.5:7b-instruct-q4_K_M
```

### 3. Acessar a Aplicação
- **Interface Web**: [http://localhost:3000](http://localhost:3000)
- **API Swagger / OpenAPI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Ollama API Local**: [http://localhost:11434](http://localhost:11434)

### 4. Executar a Suíte de Testes dentro dos Containers
```bash
# Testes do Backend
docker compose -f docker-compose.dev.yml exec backend pytest

# Testes do Frontend
docker compose -f docker-compose.dev.yml exec frontend npm run test
```

---

## 📚 Documentação e Especificações Técnicas (SDD)

* 🗺️ [Capability Map & Ordem de Construção](file:///c:/workspace/one_page_generator/docs/specs/capability-map.md)
* 📋 [Masterplan Arquitetural Completo](file:///c:/workspace/one_page_generator/docs/masterplan.md)
* 🔬 [Pesquisa Tecnológica e Levantamento Original](file:///c:/workspace/one_page_generator/docs/research.md)
* ⚡ [Especificação de Escala Futura (Rust, Postgres, Auth, Temas)](file:///c:/workspace/one_page_generator/docs/specs/SPEC-future-scale.md)

---

## 📄 Licença

Distribuído sob a licença MIT. Consulte `LICENSE` para obter mais informações.