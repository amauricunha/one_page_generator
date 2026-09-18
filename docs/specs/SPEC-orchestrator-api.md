# Spec: orchestrator-api

> **Module ID**: `orchestrator-api`  
> **Camada Clean Architecture**: Camada 3 (Controllers/Presenters) & Camada 4 (FastAPI Framework)  
> **Status**: Pronto para Implementação  
> **Versão**: 1.0.0  
> **Depende de**: `domain-core`, `document-ingestion`, `cognitive-engine`, `pdf-export`  

---

## 1. Objective

Expor a API REST / SSE da aplicação, orquestrando as requisições do frontend web com os casos de uso do backend.
Garante a injeção correta de dependências (DIP), tratamento global de exceções, validação de contratos de entrada e saída com Pydantic v2 e roteamento entre os ambientes de Dev (Ollama) e Produção (vLLM).

### Principais Atores e Casos Atendidos:
- **Frontend SPA (React)**: Consome endpoints assíncronos para upload, reescrita, condensação e download de PDF.
- **Auditoria e Logs**: Registra tempos de inferência e métricas operacionais sem expor dados confidenciais do usuário.

---

## 2. Tech Stack & Commands

- **Framework**: FastAPI 0.115+
- **Servidor ASGI**: Uvicorn com suporte a workers assíncronos
- **Validação**: Pydantic v2
- **Testes de API**: `pytest`, `pytest-asyncio`, `httpx`

### Executable Docker Commands:
```bash
# Iniciar a API em container de desenvolvimento (com live-reload)
docker compose -f docker-compose.dev.yml up -d backend

# Executar testes de integração de API dentro do container
docker compose -f docker-compose.dev.yml exec backend pytest tests/integration/api -v

# Verificar documentação OpenAPI (Swagger) exposta pelo container
curl http://localhost:8000/openapi.json
```

---

## 3. Project Structure

```
backend/src/infrastructure/
├── api/
│   ├── main.py                  # Ponto de entrada FastAPI e middlewares
│   ├── dependencies.py          # Container de Injeção de Dependências (DIP)
│   ├── routers/
│   │   ├── ingestion_router.py  # POST /api/ingest (Upload de PDFs)
│   │   ├── cognitive_router.py  # POST /api/rewrite, POST /api/condense, POST /api/translate
│   │   ├── report_router.py     # GET/POST /api/reports (Templates e drafts)
│   │   └── export_router.py     # POST /api/export/pdf (Download do PDF gerado)
│   └── middlewares/
│       ├── error_handler.py     # Mapeamento de erros de domínio para HTTP Status
│       └── cors_middleware.py   # Configuração de CORS para o frontend Vite
└── config/
    └── settings.py              # Variáveis de ambiente (DEV vs PROD, URLs do LLM)
```

---

## 4. Code Style & Controladores Desacoplados

Controladores atuam estritamente como despachantes de casos de uso (*Thin Controllers*):

```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from application.use_cases.condense_text_use_case import CondenseTextUseCase
from infrastructure.api.dependencies import get_condense_use_case

router = APIRouter(prefix="/api/cognitive", tags=["Cognitive"])

class CondenseRequest(BaseModel):
    text: str
    target_compression_ratio: float
    project_context: str

class CondenseResponse(BaseModel):
    condensed_text: str
    original_length: int
    final_length: int

@router.post("/condense", response_model=CondenseResponse, status_code=status.HTTP_200_OK)
async def condense_text_endpoint(
    payload: CondenseRequest,
    use_case: CondenseTextUseCase = Depends(get_condense_use_case)
):
    result = await use_case.execute(
        text=payload.text,
        compression_ratio=payload.target_compression_ratio,
        context=payload.project_context
    )
    if not result.is_success:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=result.error_message
        )
    
    return CondenseResponse(
        condensed_text=result.data,
        original_length=len(payload.text),
        final_length=len(result.data)
    )
```

---

## 5. Testing Strategy

- **Testes End-to-End de Rotas via `httpx.AsyncClient`**:
  1. `POST /api/ingest`: Envio de arquivo PDF multipart e validação da resposta com $TSI$ e dados estruturados.
  2. `POST /api/cognitive/condense`: Envio de texto longo com taxa $CR = 0.70$ e verificação da redução de caracteres.
  3. `POST /api/export/pdf`: Envio de JSON completo e validação de `content-type: application/pdf` com payload binário válido.
- **Middleware de Erro**: Validar que erros de domínio (`ValidationError`) resultam em HTTP 422 com payload padronizado, e erros de infraestrutura retornam HTTP 500 sem vazamento de stack traces internos.

---

## 6. Boundaries

- **Always**: Validar todos os payloads de entrada e saída com schemas Pydantic v2.
- **Always**: Injetar adaptadores concretos através de abstrações (`Depends(get_cognitive_engine)`).
- **Ask First**: Adicionar novos endpoints públicos que alterem o fluxo de submissão do relatório.
- **Never**: Colocar regras de negócio, cálculos matemáticos ou formatações complexas diretamente nos arquivos de rota.
- **Never**: Bloquear o loop assíncrono do FastAPI com operações síncronas pesadas de OCR (usar `run_in_threadpool`).

---

## 7. Success Criteria

- [ ] Todos os 4 roteadores (`ingestion`, `cognitive`, `report`, `export`) operando com documentação Swagger automática em `/docs`.
- [ ] Tempo de resposta do endpoint de ingestão $< 2.0\text{s}$ para arquivos digitais típicos.
- [ ] Cobertura de testes de integração da API superior a 90%.
- [ ] 0 falhas de injeção de dependência na alternância entre ambientes DEV e PROD.
