# Spec: cognitive-engine

> **Module ID**: `cognitive-engine`  
> **Camada Clean Architecture**: Camada 3 (Adapters) & Camada 2 (Use Cases)  
> **Status**: Pronto para Implementação  
> **Versão**: 1.0.0  
> **Depende de**: `domain-core`  

---

## 1. Objective

Orquestrar a inteligência artificial generativa local (on-premise) para as 4 funções centrais do Co-Pilot:
1. **Gap Assessment (Avaliação de Lacunas)**: Comparar os dados brutos extraídos do PDF com os campos obrigatórios do One Page Report e gerar um diagnóstico de pendências.
2. **Reescrita Parcial por Seção ("✨ Reescrever")**: Refinar o texto de um bloco específico mantendo o contexto global do projeto e atendendo à instrução do usuário ("resuma", "expanda", "mais formal").
3. **Condensação Inteligente de Texto**: Comprimir o texto sob uma taxa alvo ($CR = h_{A4} / h_{content}$), eliminando prolixidade sem perder números, metas ou parceiros.
4. **Tradução Multilíngue (PT $\leftrightarrow$ EN / ES)**: Traduzir preservando integralmente marcas, siglas institucionais e termos tecnológicos homologados.

---

## 2. Tech Stack & Commands

- **Linguagem**: Python 3.11+
- **Bibliotecas**: `httpx` (Async HTTP client), `pydantic v2`, `jinja2` (templating de prompts estruturados)
- **Engines Suportadas (100% Containerizadas)**:
  - **Dev**: Container `ollama` (`http://ollama:11434/v1`) com `qwen2.5:7b-instruct-q4_K_M` e GPU passthrough
  - **Prod**: Container `vllm` (`http://llm_engine:8000/v1`) com `Llama-3.1-Nemotron-70B-Instruct-AWQ`

### Executable Docker Commands:
```bash
# Inicializar o container Ollama com GPU passthrough
docker compose -f docker-compose.dev.yml up -d ollama

# Baixar o modelo dentro do container Ollama
docker compose -f docker-compose.dev.yml exec ollama ollama pull qwen2.5:7b-instruct-q4_K_M

# Executar testes unitários com mocks de chamadas LLM no container backend
docker compose -f docker-compose.dev.yml exec backend pytest tests/unit/cognitive -v

# Validar prompts e testes de regressão de schema JSON
docker compose -f docker-compose.dev.yml exec backend pytest tests/integration/cognitive/test_llm_contracts.py -v
```

---

## 3. Project Structure

```
backend/src/
├── application/
│   ├── ports/
│   │   └── cognitive_engine.py       # Interface abstrata ICognitiveEngine
│   └── use_cases/
│       ├── assess_gaps_use_case.py   # Diagnóstico de campos ausentes
│       ├── rewrite_section_use_case.py # Reescrita contextual
│       ├── condense_text_use_case.py # Condensação baseada em CR
│       └── translate_report_use_case.py # Tradução com glossário blindado
└── adapters/
    └── cognitive/
        ├── __init__.py
        ├── prompts/
        │   ├── gap_assessment.jinja2
        │   ├── section_rewrite.jinja2
        │   ├── text_condensation.jinja2
        │   └── translation_glossary.jinja2
        ├── openai_compatible_adapter.py # Adapter unificado para Ollama e vLLM
        └── glossary_guard.py         # Validador pós-inferência de termos técnicos
```

---

## 4. Code Style & Glossário Blindado

Padrão de prompt com blindagem de termos e saída estritamente em JSON:

```python
from typing import Protocol, Optional
import httpx
from domain.entities.report import OnePageReport

PROTECTED_GLOSSARY = {
    "FINEP", "UNISENAI", "SENAI", "SESI", "FIESC", "IEL", "FAPESP",
    "Teamcenter", "Omniverse", "Typhoon HIL", "MultiCyber", "CYBERTECH",
    "DGX H200", "5G Private Network", "Digital Twin", "Gêmeo Digital"
}

class ICognitiveEngine(Protocol):
    async def assess_gaps(self, extracted_text: str) -> dict: ...
    async def rewrite_section(self, section_name: str, text: str, mode: str, context: str) -> str: ...
    async def condense_text(self, text: str, compression_ratio: float) -> str: ...
    async def translate_report(self, report: OnePageReport, target_language: str) -> OnePageReport: ...

class OpenAiCompatibleCognitiveAdapter:
    def __init__(self, base_url: str, model_name: str, client: httpx.AsyncClient):
        self._base_url = base_url
        self._model = model_name
        self._client = client

    async def condense_text(self, text: str, compression_ratio: float) -> str:
        prompt = (
            f"Você é um redator executivo industrial sênior. "
            f"Condense o texto a seguir para ocupar aproximadamente {int(compression_ratio * 100)}% "
            f"do seu tamanho original em caracteres. "
            f"REGRAS INVIOLÁVEIS:\n"
            f"1. Preserve TODOS os valores numéricos, datas e percentuais.\n"
            f"2. Mantenha os nomes de parceiros e tecnologias sem alteração.\n"
            f"3. Responda apenas com o texto final condensado, sem introduções.\n\n"
            f"Texto Original:\n{text}"
        )
        response = await self._client.post(
            f"{self._base_url}/chat/completions",
            json={
                "model": self._model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
            timeout=30.0
        )
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
```

---

## 5. Testing Strategy

- **Mocking Determinístico com `respx`**: Simular respostas da API OpenAI-compatible do Ollama/vLLM sem necessidade de GPU ativa nos testes unitários da esteira de CI.
- **Validação de Schema JSON**: Garantir que o payload de resposta preenche 100% dos campos de `ReportData`.
- **Glossary Assertion Test**: Validar que nenhum termo pertencente a `PROTECTED_GLOSSARY` foi traduzido ou corrompido durante traduções EN/ES.

---

## 6. Boundaries

- **Always**: Forçar temperatura baixa ($\le 0.3$) para tarefas de extração estruturada e condensação.
- **Always**: Validar o JSON de resposta com Pydantic antes de repassar à camada de apresentação.
- **Ask First**: Adicionar chamadas a APIs proprietárias na nuvem (OpenAI/Anthropic).
- **Never**: Enviar dados de projetos para fora da infraestrutura on-premise local (risco de quebra de sigilo industrial).
- **Never**: Realizar reescritas sem incluir o contexto do título e objetivo central do projeto.

---

## 7. Success Criteria

- [ ] Latência de reescrita localizada $< 1.5$s no ambiente vLLM de Produção.
- [ ] Taxa de preservação de termos do glossário de 100% nos testes de tradução.
- [ ] Schema JSON gerado pela IA 100% aderente ao contrato `ReportData`.
- [ ] Condensação de texto reduz a contagem de caracteres dentro da margem de tolerância ($\pm 5\%$).
