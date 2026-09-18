# 📄 One Page Generator: Co-Pilot para Relatórios Industriais

[![Clean Architecture](https://img.shields.io/badge/Architecture-Clean%20Architecture-blue.svg)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
[![Clean Code](https://img.shields.io/badge/Code-Clean%20Code-green.svg)](#-princípios-de-engenharia-e-clean-code)
[![Standard](https://img.shields.io/badge/Format-ISO%20216%20A4%20Strict-orange.svg)](#-engine-de-layout-a4-e-detecção-de-overflow)
[![Local-First AI](https://img.shields.io/badge/AI-100%25%20On--Premise%20Private-purple.svg)](#-motor-cognitivo-e-topologia-de-hardware)
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

## 🏛️ Arquitetura do Sistema (Clean Architecture)

O projeto adota os princípios de **Clean Architecture** (Robert C. Martin) e o padrão **Ports & Adapters (Hexagonal)**, garantindo independência de frameworks, testabilidade total e inversão de dependências (DIP):

```
                      +-------------------------------------------------------------+
                      |                 4. FRAMEWORKS & DRIVERS                     |
                      |   FastAPI | React 19 / Vite | Ollama | vLLM | Puppeteer     |
                      +------------------------------+------------------------------+
                                                     |
                                                     v
                      +-------------------------------------------------------------+
                      |                  3. INTERFACE ADAPTERS                      |
                      |   REST Controllers | OllamaAdapter | VllmAdapter            |
                      |   HybridPdfExtractor | PuppeteerPdfAdapter | Repositories   |
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

### Regras Fundamentais:
- **Regra de Dependência Inward**: Nenhuma camada interna conhece detalhes das camadas externas.
- **Portas Abstratas (`Ports`)**: Casos de uso interagem com interfaces (`IDocumentExtractor`, `ICognitiveEngine`, `IPdfRenderer`, `IReportRepository`).
- **Adaptadores Intercambiáveis**: Trocar de Ollama para vLLM, ou de PyMuPDF para outro parser, não altera uma única linha de regras de negócio.

---

## 🧠 Motor Cognitivo e Topologia de Hardware

A inferência opera em arquitetura **100% on-premise** para garantir conformidade com sigilo industrial e privacidade de dados (LGPD):

| Especificação | Ambiente Dev (Local / Edge) | Ambiente Prod (Servidor Corporativo) |
|---|---|---|
| **GPU Suportada** | 1x NVIDIA RTX Ada 1000 (6GB VRAM) | 1x NVIDIA RTX 3090 (24GB VRAM) |
| **Engine de Inferência** | Ollama / llama.cpp Server | vLLM OpenAI-Compatible Server |
| **Modelo Recomendado** | `Qwen2.5-7B-Instruct` (GGUF Q4_K_M) | `Llama-3.1-Nemotron-70B-Instruct-AWQ` |
| **Janela de Contexto** | 4.096 tokens | 16.384 tokens |
| **Orçamento de VRAM** | 4.2GB (Pesos) + 0.8GB (KV) + 0.6GB (Sys) = **5.6GB** | 18.5GB (Pesos) + 3.0GB (KV) + 1.5GB (Sys) = **23.0GB** |
| **Estratégia de OCR** | OCR pesado delegado à CPU (evita CUDA OOM) | vLLM dedicado em GPU; workers de OCR isolados |

---

## 📐 Pipeline de Ingestão e Engine de Layout A4

### 1. Ingestão Híbrida com Índice de Sanidade ($TSI$)
Propostas com tabelas CMap corrompidas ou páginas escaneadas são tratadas automaticamente:
1. **PyMuPDF / pdfplumber**: Extração vetorial ultrarrápida.
2. **Cálculo de $TSI$**: Razão entre caracteres UTF-8 legíveis e o total extraído. Se $TSI < 0.85$, dispara fallback automático.
3. **docTR / Marker**: OCR neural estruturado com recuperação de bounding boxes e tabelas orçamentárias.

### 2. Layout A4 Anti-Overflow em Tempo Real
- **Grid ISO 216**: Resolução base $794\text{px} \times 1123\text{px}$ (96 DPI) e $2480\text{px} \times 3508\text{px}$ (300 DPI para impressão).
- **Detecção de Overflow**: `ResizeObserver` monitora a altura do conteúdo contra a altura máxima ($1123\text{px}$).
- **Taxa de Compressão ($CR$)**: Caso $h_{content} > h_{A4}$, o sistema calcula $CR = h_{A4} / h_{content}$ e permite acionar a condensação inteligente com um clique.
- **Temas Institucionais**: Alternância instantânea via CSS Custom Properties (`SENAI`, `SESI`, `FIESC`, `IEL` e `Corporativo`).

---

## 🛠️ Skills de Agente Instaladas no Projeto

As seguintes skills especializadas foram instaladas no repositório (`.agents/skills/`) via [skills.sh](https://www.skills.sh/) para apoiar o ciclo de desenvolvimento:

*   [`clean-code`](file:///.agents/skills/clean-code/SKILL.md): Princípios SOLID, refatoração de code smells, limites de complexidade ciclomática e padrão Result Type.
*   [`clean-architecture`](file:///.agents/skills/clean-architecture/SKILL.md): Decomposição em 4 camadas concêntricas, Inversão de Dependências (DIP) e filtro anti-over-engineering.
*   [`pdf-processing`](file:///.agents/skills/pdf-processing/SKILL.md): Padrões de manipulação, extração tabular e renderização vetorial de PDFs.
*   [`senior-architect`](file:///.agents/skills/senior-architect/SKILL.md): Governança de ADRs, decisões arquiteturais e análise de trade-offs.
*   [`ui-design-system`](file:///.agents/skills/ui-design-system/SKILL.md): Tokens de interface, padrões de componentes reativos e design responsivo.

---

## 📂 Estrutura do Repositório

```
one_page_generator/
├── .agents/
│   └── skills/                 # Skills do agente no padrão de projeto
├── backend/                    # Core Python (FastAPI, PyMuPDF, OCR)
│   ├── src/
│   │   ├── domain/             # Entidades de negócio puras
│   │   ├── application/        # Casos de uso e portas de entrada/saída
│   │   ├── adapters/           # Adaptadores de LLM, PDF e Repositório
│   │   └── infrastructure/     # Rotas HTTP, dependências e servidor
│   └── tests/
├── frontend/                   # Interface Web (React 19 + TypeScript)
│   ├── src/
│   │   ├── components/         # Container A4, Toolbar, Seções
│   │   ├── hooks/              # useLayoutMetrics, useAutoSave
│   │   └── styles/             # Paletas SENAI/SESI/FIESC/IEL
│   └── tests/
├── spec/                       # Documentação Técnica e Especificações
│   ├── research.md             # Análise de viabilidade e referências
│   └── masterplan.md           # Masterplan Arquitetural Completo
├── LICENSE
└── README.md
```

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Node.js 20+ e npm
- Python 3.11+
- Instância do **Ollama** (para dev) ou **vLLM** (para produção) com o modelo configurado

### 1. Inicialização do Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
pip install -r requirements.txt
uvicorn src.infrastructure.api.main:app --reload --port 8000
```

### 2. Inicialização do Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Configuração do Motor LLM Local (Ambiente Dev)
```bash
# Baixar o modelo recomendado para GPU 6GB
ollama pull qwen2.5:7b-instruct-q4_K_M

# Verificar disponibilidade da API OpenAI-compatible
curl http://localhost:11434/v1/models
```

---

## 📚 Documentação e Especificações Técnicas (SDD)

* 🗺️ [Capability Map & Ordem de Construção](file:///c:/workspace/one_page_generator/docs/specs/capability-map.md)
* 📋 [Masterplan Arquitetural Completo](file:///c:/workspace/one_page_generator/docs/masterplan.md)
* 🔬 [Pesquisa Tecnológica e Levantamento Original](file:///c:/workspace/one_page_generator/docs/research.md)

### Especificações Formais por Módulo:
1. [`SPEC-domain-core.md`](file:///c:/workspace/one_page_generator/docs/specs/SPEC-domain-core.md): Entidades, Value Objects e Invariantes
2. [`SPEC-document-ingestion.md`](file:///c:/workspace/one_page_generator/docs/specs/SPEC-document-ingestion.md): Pipeline Híbrido, TSI e Fallback OCR
3. [`SPEC-cognitive-engine.md`](file:///c:/workspace/one_page_generator/docs/specs/SPEC-cognitive-engine.md): Orquestração LLM, Reescrita e Condensação
4. [`SPEC-layout-editor.md`](file:///c:/workspace/one_page_generator/docs/specs/SPEC-layout-editor.md): Container A4, ResizeObserver e Auto-Save
5. [`SPEC-pdf-export.md`](file:///c:/workspace/one_page_generator/docs/specs/SPEC-pdf-export.md): Puppeteer Headless e CSS Paged Media
6. [`SPEC-orchestrator-api.md`](file:///c:/workspace/one_page_generator/docs/specs/SPEC-orchestrator-api.md): Rotas FastAPI e Injeção de Dependências

---

## 📄 Licença

Distribuído sob a licença MIT. Consulte `LICENSE` para obter mais informações.