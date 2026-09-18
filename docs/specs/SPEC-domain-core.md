# Spec: domain-core

> **Module ID**: `domain-core`  
> **Camada Clean Architecture**: Camada 1 (Domain Entities & Value Objects)  
> **Status**: Pronto para Implementação  
> **Versão**: 1.0.0  

---

## 1. Objective

Definir as entidades puras de negócio, value objects, invariantes de integridade e contratos abstratos de portas do sistema **One Page Generator**. 
Este módulo é o coração inviolável da aplicação: ele **não possui dependência de nenhum framework, banco de dados, biblioteca gráfica ou runtime externo**.

### Principais Atores e Casos Atendidos:
- **Engenheiro de Propostas / Pesquisador**: Manipula relatórios com garantia de integridade matemática nas rubricas de orçamento FINEP ($\sum \% = 100\%$) e integridade textual nas seções A4.
- **Módulos Consumidores**: `document-ingestion`, `cognitive-engine`, `layout-editor`, `pdf-export` e `orchestrator-api`.

---

## 2. Tech Stack & Commands

- **Linguagens**: TypeScript 5.5+ (Frontend / Types) e Python 3.11+ (Backend Core)
- **Bibliotecas Auxiliares**: Zod (validação TypeScript), Pydantic v2 (validação Python)

### Executable Commands:
```bash
# Validação e Testes Unitários de Domínio (Python)
pytest backend/tests/unit/domain -v --cov=backend/src/domain --cov-fail-under=95

# Validação e Testes Unitários de Domínio (TypeScript)
npm run test:domain --prefix frontend
```

---

## 3. Project Structure

```
backend/src/domain/
├── __init__.py
├── constants.py               # Dimensões ISO 216, limites de caracteres e thresholds
├── entities/
│   ├── __init__.py
│   ├── report.py              # Agregado OnePageReport
│   ├── section.py             # Entidade SectionContent
│   └── budget.py              # Entidade BudgetFinep
├── value_objects/
│   ├── __init__.py
│   ├── layout_metrics.py      # Value Object para ocupação A4 e taxa de compressão
│   ├── text_sanity.py         # Value Object para TSI
│   └── theme.py               # Enumeração de temas visuais institucionais
└── errors/
    ├── __init__.py
    └── domain_errors.py       # Exceções e classes base de erro de domínio
```

---

## 4. Code Style & Patterns

Adota-se o padrão **Result Pattern** e classes imutáveis com **Guard Clauses**:

```python
from dataclasses import dataclass
from typing import List, Optional
from domain.errors.domain_errors import ValidationError

@dataclass(frozen=True)
class LayoutMetrics:
    content_height_px: int
    max_height_px: int = 1123  # A4 a 96 DPI
    
    @property
    def usage_percentage(self) -> float:
        return round((self.content_height_px / self.max_height_px) * 100, 1)

    @property
    def is_overflowing(self) -> bool:
        return self.content_height_px > self.max_height_px

    @property
    def compression_ratio(self) -> float:
        if not self.is_overflowing:
            return 1.0
        return round(self.max_height_px / self.content_height_px, 2)


@dataclass(frozen=True)
class BudgetFinep:
    total_value: float
    categories: List[dict]

    def __post_init__(self):
        if self.total_value <= 0:
            raise ValidationError("O valor total do projeto deve ser positivo.")
        total_perc = sum(cat.get("percentage", 0.0) for cat in self.categories)
        if abs(total_perc - 100.0) > 0.5:
            raise ValidationError(f"A soma das porcentagens das categorias ({total_perc}%) deve totalizar 100%.")
```

---

## 5. Testing Strategy

- **Testes Unitários Puros**: 100% dos testes devem rodar em memória, sem I/O de rede ou disco.
- **Cobertura Mínima**: 95% das linhas e branches do módulo de domínio.
- **Cenários Críticos**:
  1. Criação de relatório com metadados obrigatórios ausentes.
  2. Validação matemática de desbalanceamento de orçamento FINEP.
  3. Cálculo de taxa de compressão em cenários de sub-ocupação ($<100\%$) e sobre-ocupação ($>100\%$).
  4. Validação do índice de sanidade ($TSI$) com caracteres UTF-8 e sequências mojibake.

---

## 6. Boundaries

- **Always**: Usar objetos imutáveis (`frozen=True` no Python, `readonly` no TypeScript).
- **Always**: Validar invariantes no momento da instanciação dos objetos.
- **Ask First**: Adicionar novos campos no esquema canônico do relatório `ReportData`.
- **Never**: Importar bibliotecas como FastAPI, React, PyMuPDF, Ollama ou Puppeteer dentro deste módulo.
- **Never**: Silenciar erros de validação de domínio.

---

## 7. Success Criteria

- [ ] Todas as entidades de negócio instanciam e validam suas propriedades em testes unitários.
- [ ] O cálculo de métricas de ocupação A4 é determinístico e atende à norma ISO 216.
- [ ] A taxa de condensação $CR$ retorna valores válidos ($0.0 < CR \le 1.0$).
- [ ] 0 dependências externas impuras no `pyproject.toml` / `package.json` para esta camada.
