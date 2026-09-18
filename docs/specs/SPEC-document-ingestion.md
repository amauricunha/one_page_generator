# Spec: document-ingestion

> **Module ID**: `document-ingestion`  
> **Camada Clean Architecture**: Camada 3 (Adapters) & Camada 2 (Use Cases)  
> **Status**: Pronto para Implementação  
> **Versão**: 1.0.0  
> **Depende de**: `domain-core`  

---

## 1. Objective

Construir o pipeline híbrido de ingestão e extração de documentos PDF industriais e de fomento (FINEP / FAPESP).
O pipeline deve extrair textos, tabelas orçamentárias e metadados de PDFs heterogêneos, tratando deterministamente arquivos corrompidos, tabelas CMap ausentes e páginas digitalizadas através do cálculo do **Índice de Sanidade do Texto ($TSI$)** e fallback automático para OCR neural.

### Principais Atores e Casos Atendidos:
- **Usuário Proponente**: Faz o upload de editais e planos de trabalho volumosos (10 a 100 páginas) sem se preocupar com a codificação do arquivo.
- **Módulo Consumidor**: `cognitive-engine` e `orchestrator-api`.

---

## 2. Tech Stack & Commands

- **Linguagem**: Python 3.11+
- **Bibliotecas**: PyMuPDF (`fitz` 1.24+), `pdfplumber`, `docTR` (com PyTorch), `Pydantic v2`
- **Isolamento de Hardware**: Execução forçada em **CPU** (`device="cpu"`) em ambiente Dev para garantir a integridade da VRAM da GPU Ada 1000.

### Executable Commands:
```bash
# Executar testes unitários e de integração de extração
pytest backend/tests/integration/extractors -v -k "test_pdf_extraction"

# Executar benchmark de extração e cálculo de TSI
python backend/src/adapters/extractors/benchmark_ingestion.py --sample-pdf docs/samples/cybertech_sample.pdf
```

---

## 3. Project Structure

```
backend/src/
├── application/
│   ├── ports/
│   │   └── document_extractor.py     # Interface abstrata IDocumentExtractor
│   └── use_cases/
│       └── ingest_document_use_case.py # Orquestrador de leitura e fallback
└── adapters/
    └── extractors/
        ├── __init__.py
        ├── pymupdf_extractor.py       # Extração nativa de alta velocidade
        ├── pdfplumber_extractor.py    # Extração de coordenadas e tabelas
        ├── neural_ocr_extractor.py    # Fallback docTR / Marker (CPU/GPU)
        └── hybrid_extractor.py        # Adapter unificado com cálculo de TSI
```

---

## 4. Code Style & Implementação Canônica

Uso de Inversão de Dependências (DIP) e avaliação estrita de $TSI$:

```python
from abc import ABC, abstractmethod
from typing import NamedTuple
import unicodedata

class ExtractionResult(NamedTuple):
    text: str
    tsi_score: float
    is_fallback_used: bool
    tables: list[dict]

class IDocumentExtractor(ABC):
    @abstractmethod
    def extract(self, pdf_bytes: bytes) -> ExtractionResult:
        pass

class TextSanityEvaluator:
    @staticmethod
    def calculate_tsi(raw_text: str) -> float:
        if not raw_text or len(raw_text.strip()) == 0:
            return 0.0
        total_chars = len(raw_text)
        # Identifica caracteres válidos imprimíveis excluindo U+FFFD (replacement character)
        valid_chars = sum(
            1 for ch in raw_text 
            if ch != '\ufffd' and (unicodedata.category(ch)[0] in ('L', 'N', 'P', 'Z') or ch in '\n\r\t')
        )
        return round(valid_chars / total_chars, 4)

class HybridPdfExtractor(IDocumentExtractor):
    TSI_THRESHOLD: float = 0.85

    def __init__(self, fast_extractor: IDocumentExtractor, ocr_extractor: IDocumentExtractor):
        self._fast = fast_extractor
        self._ocr = ocr_extractor

    def extract(self, pdf_bytes: bytes) -> ExtractionResult:
        fast_result = self._fast.extract(pdf_bytes)
        if fast_result.tsi_score >= self.TSI_THRESHOLD:
            return fast_result
            
        # Fallback para OCR caso o texto esteja corrompido ou seja imagem escaneada
        ocr_result = self._ocr.extract(pdf_bytes)
        return ExtractionResult(
            text=ocr_result.text,
            tsi_score=ocr_result.tsi_score,
            is_fallback_used=True,
            tables=ocr_result.tables
        )
```

---

## 5. Testing Strategy

- **Testes com Fixtures Reais**:
  1. PDF digital nativo (esperado: processamento via PyMuPDF em $< 500\text{ms}$ com $TSI > 0.95$).
  2. PDF digitalizado / escaneado (esperado: ativação do fallback docTR com recuperação textual).
  3. PDF com CMap corrompido contendo sequências `\ufffd` (esperado: detecção $TSI < 0.85$ e acionamento de fallback).
- **Testes de Isolamento de Hardware**:
  - Validar que em ambiente Dev a engine de OCR não inicializa tensores na GPU CUDA (`torch.cuda.is_available()` não aloca VRAM).

---

## 6. Boundaries

- **Always**: Medir o $TSI$ antes de considerar o documento legível para a IA.
- **Always**: Rodar OCR na CPU em ambiente Dev.
- **Ask First**: Alterar o threshold de $0.85$ do $TSI$.
- **Never**: Lançar exceções não tratadas por erro de parsing do PDF (retornar `Result.failure`).
- **Never**: Executar OCR síncrono bloqueando a thread principal da API (usar async/worker).

---

## 7. Success Criteria

- [ ] Taxa de recuperação de dados $>95\%$ em PDFs de planos de trabalho da FINEP.
- [ ] Tempo de resposta para PDFs nativos $< 1.5$ segundo para arquivos de até 50 páginas.
- [ ] Chaveamento automático para OCR testado e validado em 100% dos arquivos com fontes Type3 ou sem CMap.
- [ ] 0 ocorrências de CUDA OOM na GPU Ada 1000 durante a execução contínua de extração.
