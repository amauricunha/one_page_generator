# Spec: pdf-export

> **Module ID**: `pdf-export`  
> **Camada Clean Architecture**: Camada 3 (Adapters) & Camada 4 (Puppeteer Driver)  
> **Status**: Pronto para Implementação  
> **Versão**: 1.0.0  
> **Depende de**: `domain-core`, `layout-editor`  

---

## 1. Objective

Garantir a renderização vetorial e exportação do One Page Report em arquivo PDF no padrão estrito A4 ($210\text{mm} \times 297\text{mm}$), com fidelidade visual idêntica ao infográfico exibido na interface web, **com garantia absoluta de página única (zero quebras de página involuntárias ou cortes de rodapé)**.

### Principais Atores e Casos Atendidos:
- **Usuário Executivo / Proponente**: Faz o download do PDF oficial para submissão direta no portal FINEP ou impressão física.
- **Módulo Consumidor**: `orchestrator-api` e `layout-editor`.

---

## 2. Tech Stack & Commands

- **Runtime**: Node.js 20+ ou Python com `playwright` / `puppeteer`
- **Engine**: Headless Chromium
- **Padrão de Impressão**: CSS Paged Media W3C (`@page`)
- **Fontes**: Embutimento local WOFF2 via Base64 para garantir independência do sistema operacional do host

### Executable Docker Commands:
```bash
# Executar testes de fidelidade de renderização PDF dentro do container backend
docker compose -f docker-compose.dev.yml exec backend pytest tests/integration/pdf -v -k "test_single_page_pdf"

# Gerar PDF de teste dentro do container a partir do snapshot CYBERTECH
docker compose -f docker-compose.dev.yml exec backend python src/adapters/pdf/export_cli.py --input docs/samples/cybertech_report.json --output storage/test_output.pdf
```

---

## 3. Project Structure

```
backend/src/adapters/pdf/
├── __init__.py
├── font_assets/              # Fontes WOFF2 convertidas em Base64
│   ├── inter_regular_base64.txt
│   └── inter_bold_base64.txt
├── template/
│   ├── printable_a4.html     # Template HTML hermético com CSS inline
│   └── paged_media.css       # Regras @page { size: A4; margin: 0; }
├── puppeteer_pdf_renderer.py # Adapter concreto de renderização
└── pdf_page_validator.py     # Verificador que valida se o PDF possui exatamente 1 página
```

---

## 4. Code Style & Implementação Canônica

Uso de CSS Paged Media e verificação automática de contagem de páginas:

```python
from abc import ABC, abstractmethod
import pypdf
from domain.errors.domain_errors import RenderError

class IPdfRenderer(ABC):
    @abstractmethod
    async def render(self, html_content: str) -> bytes:
        pass

class PuppeteerPdfRenderer(IPdfRenderer):
    async def render(self, html_content: str) -> bytes:
        # Lança Chromium headless isolado
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(args=["--no-sandbox", "--disable-gpu"])
            page = await browser.new_page()
            
            await page.set_content(html_content, wait_until="networkidle")
            
            # Gera PDF estrito em A4 sem margens externas do navegador
            pdf_bytes = await page.pdf(
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
                margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"}
            )
            await browser.close()

            # Validação Hard-Gate: O PDF gerado tem que ter exatamente 1 página
            self._assert_single_page(pdf_bytes)
            return pdf_bytes

    def _assert_single_page(self, pdf_bytes: bytes) -> None:
        import io
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        page_count = len(reader.pages)
        if page_count != 1:
            raise RenderError(
                f"Falha de fidelidade: o relatório transbordou e gerou {page_count} páginas. "
                f"O One Page Report deve conter estritamente 1 página."
            )
```

---

## 5. Testing Strategy

- **Testes de Contagem Estrita de Página (Hard Gate)**:
  - Todo teste de exportação deve verificar `assert len(reader.pages) == 1`.
- **Testes de Dimensão Geométrica**:
  - Verificar se a largura e altura da página são exatamente $595.28\text{pt} \times 841.89\text{pt}$ (medidas padrão do A4 no PDF).
- **Testes de Embutimento de Imagens**:
  - Validar que os logotipos injetados como `data:image/png;base64` aparecem no arquivo final sem artefatos ou dependência de rede.

---

## 6. Boundaries

- **Always**: Utilizar `prefer_css_page_size=True` e `print_background=True`.
- **Always**: Validar programaticamente que a contagem de páginas do PDF é rigorosamente igual a 1.
- **Ask First**: Permitir que o documento seja exportado em mais de uma página (violação da proposta One Page Report).
- **Never**: Usar fontes externas via CDN (e.g. `fonts.googleapis.com`) no template headless (risco de timeout e quebra de layout offline).

---

## 7. Success Criteria

- [ ] 100% dos relatórios gerados possuem exatamente 1 página A4.
- [ ] Tempo de renderização do PDF inferior a 2.5 segundos.
- [ ] Renderização vetorial cristalina de gráficos e fontes em qualquer leitor de PDF padrão (Adobe Acrobat, Chrome, Preview).
