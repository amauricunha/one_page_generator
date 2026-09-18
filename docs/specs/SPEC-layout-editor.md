# Spec: layout-editor

> **Module ID**: `layout-editor`  
> **Camada Clean Architecture**: Camada 3 (Presenters/UI Adapters) & Camada 4 (React UI)  
> **Status**: Pronto para Implementação  
> **Versão**: 1.0.0  
> **Depende de**: `domain-core`  

---

## 1. Objective

Construir a interface do usuário web reativa que renderiza o One Page Report em proporção estrita A4 (norma ISO 216), com monitoramento de overflow em tempo real, edição *in-place*, customização visual instantânea via paletas institucionais, upload de logotipos em Base64 e persistência local resiliente (*Private App Storage* com auto-save em IndexedDB).

### Principais Atores e Casos Atendidos:
- **Redator / Gestor de Inovação**: Edita títulos, parágrafos, gráficos orçamentários e recebe feedback visual imediato sobre o limite de espaço da página A4.
- **Módulos Integrados**: Conecta-se ao `cognitive-engine` para reescrita/condensação e fornece a estrutura DOM limpa para o `pdf-export`.

---

## 2. Tech Stack & Commands

- **Framework**: React 19 + TypeScript 5.5+
- **Build Tool**: Vite 6+
- **Estilização**: Vanilla CSS com CSS Custom Properties (Tokens) + CSS Grid para diagramação A4
- **Persistência**: `localForage` (IndexedDB Wrapper) com debounce de 2.0s
- **Detecção de Layout**: Web APIs nativas (`ResizeObserver`, `MutationObserver`)

### Executable Docker Commands:
```bash
# Iniciar o frontend em container de desenvolvimento (porta 3000 com live-reload)
docker compose -f docker-compose.dev.yml up -d frontend

# Executar testes unitários e de componentes dentro do container
docker compose -f docker-compose.dev.yml exec frontend npm run test

# Executar verificação estática de tipos e linting no container
docker compose -f docker-compose.dev.yml exec frontend npm run lint && docker compose -f docker-compose.dev.yml exec frontend npm run typecheck
```

---

## 3. Project Structure

```
frontend/src/
├── components/
│   ├── layout/
│   │   ├── A4Container.tsx            # Container com restrição 210x297mm
│   │   ├── Toolbar.tsx                # Barra de temas, upload, badges e ações
│   │   └── OverflowBadge.tsx          # Indicador visual de percentual de ocupação
│   ├── sections/
│   │   ├── InstitutionalHeader.tsx    # Logos Base64 e títulos
│   │   ├── MotivationChallenges.tsx   # Coluna dupla Motivação/Desafios
│   │   ├── KeyResultsCards.tsx        # Grid R1 a R4
│   │   ├── BudgetFinepBars.tsx        # Barras de percentual orçamentário
│   │   └── ImpactsAndContacts.tsx     # Matriz de impactos e contatos
│   └── common/
│       ├── RewriteButton.tsx          # Botão "✨ Reescrever" por seção
│       └── LogoUploader.tsx           # Input com conversão em data:URI Base64
├── hooks/
│   ├── useLayoutMetrics.ts            # Hook com ResizeObserver para A4
│   ├── useAutoSave.ts                 # Hook com debounce para IndexedDB
│   └── useReportState.ts              # Gerenciador de estado do relatório
└── styles/
    ├── tokens.css                     # Variáveis CSS dos temas SENAI/SESI/FIESC/IEL
    └── a4-grid.css                    # Dimensões exatas e regras de impressão
```

---

## 4. Code Style & Hook de Detecção de Overflow

Exemplo do hook reativo isolado utilizando `ResizeObserver`:

```typescript
import { useState, useEffect, RefObject } from 'react';

export interface LayoutMetrics {
  contentHeight: number;
  maxHeight: number;
  usagePercentage: number;
  isOverflowing: boolean;
  compressionRatio: number;
}

const A4_96DPI_HEIGHT_PX = 1123;

export function useLayoutMetrics(containerRef: RefObject<HTMLElement>): LayoutMetrics {
  const [metrics, setMetrics] = useState<LayoutMetrics>({
    contentHeight: 0,
    maxHeight: A4_96DPI_HEIGHT_PX,
    usagePercentage: 0,
    isOverflowing: false,
    compressionRatio: 1.0,
  });

  useEffect(() => {
    const element = containerRef.current;
    if (!element) return;

    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const height = Math.round(entry.contentRect.height);
        const isOverflow = height > A4_96DPI_HEIGHT_PX;
        const usage = Number(((height / A4_96DPI_HEIGHT_PX) * 100).toFixed(1));
        const cr = isOverflow ? Number((A4_96DPI_HEIGHT_PX / height).toFixed(2)) : 1.0;

        setMetrics({
          contentHeight: height,
          maxHeight: A4_96DPI_HEIGHT_PX,
          usagePercentage: usage,
          isOverflowing: isOverflow,
          compressionRatio: cr,
        });
      }
    });

    observer.observe(element);
    return () => observer.disconnect();
  }, [containerRef]);

  return metrics;
}
```

---

## 5. Testing Strategy

- **Testes de Renderização com Testing Library**:
  1. Renderização de todos os cards e seções com o payload do projeto CYBERTECH.
  2. Teste de troca de tema (`SENAI` $\rightarrow$ `SESI`) validando a alteração das variáveis `--primary-color` e `--secondary-color`.
  3. Conversão de imagem para Base64 no upload de logo com injeção direta no DOM.
- **Testes de Auto-Save**:
  - Validar que digitações rápidas disparam apenas 1 escrita no IndexedDB após o silêncio de 2.0s de debounce.
- **Testes de Overflow**:
  - Simular inserção de texto longo e verificar a aplicação da classe visual `.overflow-warning` (borda vermelha pulsante).

---

## 6. Boundaries

- **Always**: Proteger a proporção visual A4 ($1:\sqrt{2} \approx 1:1.414$).
- **Always**: Salvar imagens de logotipos em formato Base64 puro para renderização offline garantida.
- **Ask First**: Adicionar dependências pesadas de bibliotecas visuais ou componentes prontos de terceiros.
- **Never**: Acionar chamadas de IA automaticamente a cada tecla digitada.
- **Never**: Depender de requisições de rede assíncronas externas para renderizar fontes ou ícones do relatório.

---

## 7. Success Criteria

- [ ] A folha A4 em tela mede exatamente $794\text{px} \times 1123\text{px}$ a 96 DPI em proporção 1:1.
- [ ] O indicador de ocupação reage em tempo real com precisão de $\pm 2$ pixels.
- [ ] Nenhuma perda de dados ao recarregar a página (restauração automática do último rascunho em IndexedDB).
- [ ] Alternância entre os 5 temas institucionais instantânea ($< 50\text{ms}$).
