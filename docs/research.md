Masterplan Arquitetural e Tecnológico: Aplicação Co-Pilot para Geração e Gestão de One Page Reports Industriais
Visão Geral e Arquitetura do Sistema Co-Pilot
A captação de recursos de fomento à pesquisa, desenvolvimento e inovação (PD&I) junto a órgãos financiadores como FINEP e FAPESP exige a consolidação de projetos altamente complexos em propostas executivas coesas1. Em ecossistemas como SENAI, SESI, FIESC e IEL, os planos de trabalho detalhados frequentemente abrangem dezenas de páginas contendo justificativas, orçamentos discriminados, arranjos ciberfísicos, metas físicas e cronogramas de desembolso1. A conversão desse volume documental em um One Page Report sintético e visualmente denso é uma tarefa crítica para a aprovação institucional e a apresentação para executivos industriais1.
A aplicação Co-Pilot foi projetada como uma plataforma web inteligente focada na automação do ciclo de vida dos relatórios executivos3. A solução realiza a ingestão de múltiplos formatos de arquivo (PDFs, textos planos, Markdown, apresentações e estudos de viabilidade), executa a análise de completude por meio de inteligência artificial generativa, renderiza um relatório editável em página única A4 e permite a exportação em PDF de alta fidelidade sem quebras de layout1.



┌────────────────────────────────────────────────────────────────────────┐
│                        CAMADA DE INTERFACE (UI/UX)                     │
│   Toolbar Reativa, Editor A4, Seletor de Temas, Upload Base64, Badges  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    v
┌────────────────────────────────────────────────────────────────────────┐
│                     ENGINE DE LAYOUT E OVERFLOW                        │
│     ResizeObserver, Cálculo de Ocupação A4, Puppeteer PDF Engine       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    v
┌────────────────────────────────────────────────────────────────────────┐
│                   MOTOR COGNITIVO E RAG DE INGESTÃO                    │
│   Gap Assessment, Reescrita Parcial, Condensação, Tradução Técnica     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    v
┌────────────────────────────────────────────────────────────────────────┐
│                   INFRAESTRUTURA DE MODELOS DE IA                      │
│   Dev: Ollama / Qwen2.5 (6GB) | Prod: vLLM / Nemotron-70B AWQ (24GB)   │
└────────────────────────────────────────────────────────────────────────┘


A arquitetura do sistema divide-se em quatro camadas integradas:

Camada da Arquitetura
Responsabilidade Funcional
Componentes e Tecnologias
Camada de Ingestão e OCR
Leitura de fontes heterogêneas, extração de texto em PDFs com codificação corrompida, análise visual de layout e estruturação de dados1.
PyMuPDF, pdfplumber, Marker, docTR, Tesseract OCR4.
Motor Cognitivo (LLM)
Avaliação de lacunas (Gap Assessment), reescrita contextual de seções, tradução técnica mantendo acrônimos e condensação sintática3.
Ollama (Ambiente Dev), vLLM (Ambiente Produção), NVIDIA Nemotron-70B, Qwen2.56.
Interface de Usuário e Layout
Renderização em grid A4 estrito, monitoramento dinâmico de overflow, customização visual instantânea e edição in-place3.
React.js, TailwindCSS, CSS Grid/Flexbox, Web APIs (ResizeObserver, IndexedDB).
Engine de Exportação PDF
Renderização vetorial em página única no formato A4 infográfico/flyer sem distorção ou quebras involuntárias3.
Headless Chromium via Puppeteer, CSS Paged Media (@page), Paged.js8.

O fluxo operacional inicia-se quando o usuário carrega a documentação bruta do projeto no sistema1. O pipeline de ingestão processa os arquivos, normaliza o texto e aciona o Motor Cognitivo para avaliar a completude dos dados em relação ao modelo de One Page Report1. Caso sejam identificadas lacunas de informação, o sistema apresenta um diagnóstico com perguntas direcionadas para preencher os campos ausentes3. Após a validação dos dados, o relatório é montado dinamicamente em um container visual A4, onde o usuário pode customizar temas, ajustar logos, solicitar reescritas parciais via IA e exportar o documento impresso em página única3.
Pipeline de Ingestão e Processamento Avançado de Documentos PDF Complexos
A extração de informações a partir de documentos PDF no contexto de propostas FINEP apresenta desafios técnicos significativos1. É comum encontrar arquivos PDF gerados por sistemas legados contendo tabelas de mapeamento de caracteres (ToUnicode CMap) ausentes ou corrompidas, fontes customizadas do tipo Type3 sem correspondência ASCII/UTF-8 direta e páginas digitalizadas sem camada de texto vetorial5. Nesses cenários, a extração de texto convencional resulta em sequências vazias ou em caracteres ilegíveis (mojibake), inviabilizando o processamento direto por modelos de linguagem5.
Para resolver essas limitações de forma determinística, a aplicação emprega uma estratégia de extração híbrida em três estágios com fallback automático, garantindo a integridade dos dados independente do formato de origem4.
No primeiro estágio, o sistema submete o arquivo a parsers nativos de alta velocidade como PyMuPDF (fitz) e pdfplumber4. Durante a leitura, calcula-se o Índice de Sanidade do Texto (), expresso pela razão entre os caracteres UTF-8 legíveis e o total de caracteres extraídos:

Se o valor de  for inferior a 0.85, ou se o sistema detectar a ocorrência continuada do caractere de substituição Unicode U+FFFD, a extração nativa é abortada5. O documento é então automaticamente sinalizado como PDF codificado ou digitalizado e redirecionado para o segundo estágio do pipeline5.
O segundo estágio aplica visão computacional e OCR estruturado utilizando as engines Marker e docTR4. O Marker executa a análise de layout por meio de modelos baseados em redes neurais convolucionais e transformers, segmentando o documento em blocos funcionais (títulos, parágrafos, listas e tabelas orçamentárias) e reconstruindo a ordem de leitura correta em formato Markdown limpo5. Simultaneamente, o docTR fornece suporte a OCR profundo com detecção de caixas delimitadoras (bounding boxes), recuperando o texto de imagens escaneadas ou gráficos vetoriais sem camada de texto4. Esse processo preserva a geometria e a relação entre linhas e colunas de tabelas orçamentárias complexas, como as rubricas de capital e despesas correntes do projeto CYBERTECH1.
No terceiro estágio, a representação estruturada em Markdown é enviada ao Motor Cognitivo8. O modelo de linguagem realiza a extração semântica das entidades do projeto, mapeando o texto bruto para os campos formais do One Page Report1.

Engine de Extração
Mecanismo de Funcionamento
Acurácia de Layout
Escala de Velocidade
Cenário de Uso Principal
PyMuPDF (fitz)
Mineração direta de streams de texto vetorial no PDF5.
Baixa em layouts complexos

PDFs nativos digitais e documentos em texto corrido sem codificação customizada.
pdfplumber
Mapeamento detalhado de coordenadas visuais e bordas de tabelas4.
Média-Alta em quadros simples

Extração de quadros demonstrativos de orçamento e tabelas com linhas visíveis1.
Marker (Docker)
Análise de layout via Transformers + Reconstrução em Markdown5.
Altíssima em documentos heterogêneos

PDFs de planos de trabalho com múltiplas colunas, imagens e codificação corrompida1.
docTR
OCR vetorial profundo com redes convolucionais e detecção de Bounding Boxes4.
Altíssima para texto não estruturado

Documentos digitalizados, plantas baixas, infográficos e PDFs com falhas de CMap5.

Motor Cognitivo de IA e Topologia de Infraestrutura de Hardware
A execução do Motor Cognitivo é baseada em uma arquitetura on-premise privada, garantindo total conformidade com os requisitos de sigilo e propriedade intelectual exigidos em projetos de inovação industrial1. A infraestrutura foi dimensionada para suportar dois ambientes funcionais: um ambiente local de desenvolvimento e testes rodando em hardware restrito (6GB de VRAM) e um servidor corporativo de produção projetado para alta concorrência (24GB de VRAM)6.
No ambiente de desenvolvimento, a aplicação utiliza a placa NVIDIA RTX Ada 1000 com 6GB de VRAM9. Para viabilizar a execução de um LLM com capacidade de raciocínio estruturado dentro desse limite de memória, utiliza-se o modelo Qwen2.5-7B-Instruct quantizado no formato GGUF (Q4_K_M) ou o Nemotron-Mini-4B-Instruct, orquestrados via Ollama ou llama.cpp6. O orçamento de VRAM é rigidamente alocado: os pesos do modelo quantizado ocupam aproximadamente 4,2 GB, o cache KV para uma janela de contexto de 4.096 tokens consome 0,8 GB, e a margem de segurança do runtime aloca 0,6 GB, totalizando 5,6 GB de VRAM ocupados9.
No ambiente de produção, a infraestrutura conta com um servidor equipado com uma placa NVIDIA RTX 3090 de 24GB de VRAM, utilizando a engine de inferência vLLM6. O modelo adotado é o Llama-3.1-Nemotron-70B-Instruct-AWQ (quantização em 4 bits via AWQ)6. O vLLM otimiza o uso da memória gráfica por meio do algoritmo PagedAttention, permitindo o atendimento eficiente de requisições simultâneas6. A alocação da VRAM de 24 GB distribui-se em 18,5 GB para os pesos do modelo quantizado, 3,0 GB para o cache KV dinâmico (com suporte a até 16.384 tokens de contexto) e 1,5 GB para overhead dos kernels CUDA, atingindo aproveitamento otimizado com a flag --gpu-memory-utilization 0.956.

Métrica / Parâmetro
Ambiente de Desenvolvimento (Ada 1000)
Ambiente de Produção (RTX 3090)
Hardware de GPU
1x NVIDIA RTX Ada 1000 (6GB VRAM GDDR6)
1x NVIDIA RTX 3090 (24GB VRAM GDDR6X)6
Engine de Inferência
Ollama / llama.cpp Server6
vLLM Async OpenAI-Compatible API Server6
Modelo Selecionado
Qwen2.5-7B-Instruct / Nemotron-Mini-4B6
Llama-3.1-Nemotron-70B-Instruct-AWQ6
Formato de Quantização
GGUF Q4_K_M6
AWQ INT4 (Compressed Tensors)6
Janela de Contexto ()
4.096 tokens
16.384 tokens6
Throughput Médio


[cite: 6]
Alocação de VRAM
4,2 GB (Modelo) + 0,8 GB (KV) + 0,6 GB (Sys)
18,5 GB (Modelo) + 3,0 GB (KV) + 1,5 GB (Sys)6

O Motor Cognitivo desempenha quatro funções principais no sistema:
Avaliação de Lacunas (Gap Assessment): O LLM analisa os dados extraídos dos arquivos enviados e valida o preenchimento de cada campo do One Page Report1. Caso faltem dados essenciais (como prazos, parcelas do orçamento ou indicadores de impacto), a IA gera um relatório interativo de pendências, solicitando as informações complementares ao usuário1.
Reescrita Parcial por Seção ("✨ Reescrever"): Cada bloco do relatório conta com um botão de regeneração independente3. Ao ser acionado, o sistema envia para o LLM apenas o texto daquela seção específica acrescido do contexto global do projeto3. O usuário seleciona orientações como "Resuma mais", "Expanda" ou "Tom mais formal", garantindo o refinamento localizado sem alterar as seções editadas manualmente3.
Condensação Inteligente de Texto ("Ajustar ao tamanho"): Quando o conteúdo excede o limite físico da folha A4, a IA calcula o percentual de redução necessário e reescreve o texto de forma sintética, preservando dados quantitativos, nomes de parceiros e termos técnicos1.
Tradução Multilíngue Preservando Termos Técnicos (PT / EN / ES): O sistema permite a conversão instantânea de todo o relatório para inglês ou espanhol3. As diretrizes do prompt forçam o modelo a manter inalterados nomes próprios, marcas, acrônimos institucionais e especificações tecnológicas, tais como "FINEP", "UNISENAI", "Teamcenter", "Omniverse", "Typhoon HIL" e "MultiCyber"1.
Engine de Layout Interativo, Detecção de Overflow e Renderização de PDF A4 de Página Única
Para atender à exigência de geração de um relatório executivo em página única no formato infográfico/flyer, o sistema adota um modelo de grid A4 baseado estritamente na norma ISO 216 (210mm × 297mm)3. Em tela, o container do relatório é dimensionado proporcionalmente para corresponder a 794px × 1123px em resolução de 96 DPI, ou 2480px × 3508px em resolução de 300 DPI para renderização de alta fidelidade.
O layout organiza as seções do projeto CYBERTECH no modelo de One Page Report através da seguinte distribuição espacial3:



┌────────────────────────────────────────────────────────────────────────┐
│ HEADER INSTITUCIONAL: Logo Esquerda | Título do Projeto | Logo Direita │
├───────────────────────────────────┬────────────────────────────────────┤
│ MOTIVAÇÃO                         │ DESAFIOS                           │
│ Descrição do problema e alinhamento│ Lista de desafios operacionais e   │
│ com a política Nova Indústria Brasil.│ tecnológicos enfrentados.        │
├───────────────────────────────────┴────────────────────────────────────┤
│ RESULTADOS CHAVE (Cards R1, R2, R3 e R4)                               │
│ R1: 5G & PLM | R2: Plataforma Colaborativa | R3: Simulação | R4: HPC & IA│
├────────────────────────────────────────────────────────────────────────┤
│ OBJETIVO DO PROJETO (Banner de Destaque)                               │
│ Declaração central da missão do projeto e impacto pretendido.          │
├───────────────────────────────────┬────────────────────────────────────┤
│ OBJETIVOS ESPECÍFICOS             │ ARQUITETURA TECNOLÓGICA RESUMIDA   │
│ Lista numerada dos objetivos 1 a 8.│ Camadas: Interação, Engenharia,    │
│                                   │ Barramentos e Core Físico.         │
├───────────────────────────────────┼────────────────────────────────────┤
│ ORÇAMENTO FINEP                   │ PARCEIROS DE PD&I                  │
│ Barras e percentuais por categoria│ Lista e badges das empresas       │
│ econômica do projeto.             │ parceiras do ecossistema.          │
├───────────────────────────────────┼────────────────────────────────────┤
│ IMPACTOS POTENCIAIS               │ CONTATO INSTITUCIONAL              │
│ Matriz de Impactos: Econômico,    │ Coordenador, Líder Técnico e       │
│ Social e Ambiental (Circular).    │ Endereço da unidade executora.     │
└───────────────────────────────────┴────────────────────────────────────┘


A interface possui um sistema de detecção e ajuste de overflow em tempo real3. Através das APIs ResizeObserver e MutationObserver, o sistema monitora continuamente a altura do conteúdo interno do relatório () contra a altura fixa disponível no container A4 ()3.
O percentual de utilização do espaço exibido na barra de ferramentas é determinado por:

Sempre que , o indicador visual ativa um alerta em tempo real, aplicando uma borda vermelha pulsante ao redor da folha A4 e exibindo um badge de overflow na toolbar3.
Ao clicar no botão "Ajustar ao tamanho", o sistema calcula a taxa de condensação necessária ():

Essa taxa é enviada ao Motor Cognitivo como instrução de compressão textual, encurtando parágrafos e otimizando listas até que o conteúdo se enquadre exatamente nos limites da folha A43.
Para a exportação em PDF sem as desconfigurações provocadas pelos motores de impressão tradicionais dos navegadores (window.print()), a aplicação utiliza um pipeline baseado em Headless Chromium gerenciado por Puppeteer3. O documento HTML renderizado é enviado para o Puppeteer, que executa o cálculo de layout utilizando regras estritas de CSS Paged Media (@page { size: A4 portrait; margin: 0; }), congelando as proporções visuais e gerando um arquivo PDF vetorial de página única idêntico ao infográfico exibido na interface3.
Interface de Usuário, Toolbar de Customização e Gestão de Estado Persistente
A interface da aplicação foi estruturada para oferecer controle visual direto sobre o One Page Report3. A barra de ferramentas superior (toolbar) centraliza os controles operacionais de tema, upload de logotipos, monitoramento de espaço, tradução de idioma e exportação3.
O seletor de paleta de cores permite a troca dinâmica do tema do relatório em tempo real3. A alteração do tema atualiza instantaneamente as variáveis CSS globais (CSS Custom Properties) que regem a estilização do cabeçalho, bordas de seções, acentos de texto e barras de gráficos do orçamento3.
Nome da Paleta
Cor Primária (Header/Títulos)
Cor Secundária (Acentos/Highlights)
Cor das Barras de Orçamento
Azul e Vermelho SENAI
[cite: 3]
Azul Institucional (#005CA9)
Vermelho SENAI (#E30613)
#005CA9 / #E30613
Azul e Verde Sustentável SESI
[cite: 3]
Azul SESI (#005691)
Verde Sustentável (#00843D)
#00843D / #00843D
Cinza Corporativo
[cite: 3]
Grafite Escuro (#2C3E50)
Cinza Prata (#7F8C8D)
#34495E / #95A5A6
FIESC
[cite: 3]
Azul Marinho FIESC (#002B49)
Amarelo Ouro (#FFC72C)
#002B49 / #E5A823
IEL
[cite: 3]
Azul Petróleo (#00829B)
Laranja IEL (#E85E12)
#00829B / #E85E12

O cabeçalho do relatório dispõe de áreas de upload dedicado para logotipos institucionais3. Ao selecionar os arquivos de imagem (logo da instituição executora à esquerda e do órgão financiador à direita), o sistema converte os arquivos localmente em sequências de texto no formato data: URI (Base64)3. As imagens são injetadas diretamente nas tags <img> do documento, garantindo que sejam renderizadas inline no DOM e capturadas perfeitamente pelo engine de exportação PDF do Puppeteer sem depender de requisições de rede assíncronas3.
Para evitar a perda de edições manuais ou de relatórios gerados por chamadas de IA, o aplicativo inclui um sistema de salvamento automático e biblioteca local em Private App Storage3. O mecanismo opera através das seguintes regras:
Auto-Save Silencioso com Debounce: Todas as alterações feitas nos campos de texto, paletas ou logos disparam um temporizador de debounce de 2,0 segundos3. Após esse intervalo sem novas interações, o estado completo do relatório é persistido silenciosamente no armazenamento local do navegador (IndexedDB via localForage)3.
Restauração Automática de Rascunho: Ao abrir ou recarregar a aplicação, o sistema restaura automaticamente o último rascunho em edição, recuperando texto, imagens em Base64 e o tema selecionado3.
Biblioteca de Relatórios: A tela inicial apresenta uma galeria contendo todos os relatórios salvos anteriormente3. Cada item lista o nome do projeto, data da última edição, idioma e uma miniatura representando a paleta visual adotada, permitindo que o usuário carregue, duplique ou exclua projetos com um clique3.
Esquema de Dados JSON e Galeria de Templates Estáticos
O estado do One Page Report é governado por um esquema de dados JSON padronizado, assegurando compatibilidade entre as respostas da IA, os formulários editáveis da interface e o motor de exportação3.
O esquema ReportData é definido conforme a estrutura abaixo:



JSON
{
  "metadata": {
    "id": "cybertech-001",
    "projectTitle": "CENTRO DE REFERÊNCIA EM TRANSFORMAÇÃO DIGITAL PARA NEOINDUSTRIALIZAÇÃO",
    "projectAcronym": "CYBERTECH",
    "institutionName": "UniSENAI / SENAI Instituto de Inovação",
    "funderName": "FINEP",
    "selectedTheme": "SENAI",
    "language": "PT",
    "logoLeftDataUri": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "logoRightDataUri": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "lastModified": "2026-07-22T08:10:36Z"
  },
  "content": {
    "motivation": "A modernização da indústria brasileira é um imperativo para a manutenção da competitividade global...",
    "challenges": [
      "Integrar tecnologias complexas e heterogêneas em um ambiente digital robusto e acessível.",
      "Democratizar o acesso de PMEs a plataformas avançadas de simulação e Gêmeos Digitais.",
      "Validar algoritmos de IA de forma segura e eficiente antes da implementação em produção."
    ],
    "keyResults": [
      {
        "code": "R1",
        "title": "5G & Integração PLM",
        "description": "Implantação de rede 5G privada e baseline de dados no Teamcenter..."
      },
      {
        "code": "R2",
        "title": "Plataforma Colaborativa Multiusuário",
        "description": "Integração do Siemens Teamcenter e NVIDIA Omniverse para criar uma plataforma aberta..."
      }
    ],
    "projectObjective": "A missão do projeto é catalisar a transformação digital do setor industrial brasileiro...",
    "specificObjectives": [
      "Simulação e Modelagem: Metaverso industrial para testes virtuais seguros.",
      "Sistemas Ciberfísicos: Automação, coleta em tempo real e decisão autônoma."
    ],
    "technicalArchitecture": {
      "interactionLayer": "Metaverso Industrial, Workstations Virtuais, Fator Humano",
      "engineeringEngines": "Simulação Discreta, Simulação Física Avançada, Testes de Controle",
      "connectionBuses": "Teamcenter PLM (Backbone), Rede 5G & IIoT",
      "physicalCore": "NVIDIA DGX H200 (IA), Servidores Base"
    },
    "budgetFinep": {
      "totalValue": 14936520.66,
      "categories": [
        { "name": "Equip. Nacional", "percentage": 11.0, "value": 1640656.75 },
        { "name": "Equip. Importado", "percentage": 25.2, "value": 3765162.54 },
        { "name": "Pagamento Pessoal", "percentage": 27.5, "value": 4108032.00 },
        { "name": "Outros Serviços PJ", "percentage": 38.3, "value": 5422669.37 }
      ]
    },
    "potentialImpacts": {
      "economic": "Redução relevante de custos, aumento de produtividade, expansão dos ciclos de exportação.",
      "social": "Geração de empregos, melhoria da qualidade de vida, acesso democratizado de MPEs.",
      "environmental": "Redução de resíduos, água, energia elétrica e emissão de poluentes."
    },
    "partners": ["SCHULZ S.A.", "DOHLER S.A.", "NETZSCH DO BRASIL", "TUPY S.A.", "KRONA", "VALE S.A."],
    "contactInfo": {
      "coordinatorName": "Luis Gonzaga Trabasso",
      "coordinatorEmail": "luis.gonzaga@sc.senai.br",
      "technicalLeaderName": "Thiago Rosa Soares",
      "technicalLeaderEmail": "thiago.r.soares@edu.sc.senai.br",
      "address": "Rua Arno Waldemar Dohler, nº 957, Zona Industrial Norte, Joinville-SC"
    }
  }
}


Para garantir o uso imediato da ferramenta sem dependência inicial de chamadas à API de IA, a aplicação inclui uma galeria de templates estáticos armazenados localmente no código3. Cada template fornece seções pré-preenchidas com dados alinhados às chamadas públicas da FINEP1:

Template Estático
Foco do Projeto
Estrutura de Orçamento Padrão
Tipos de Impacto Relevantes
PD&I Industrial
[cite: 3]
Modernização de linhas de produção, Gêmeos Digitais, automação com IA e robótica avançada1.
Aumento em Equipamentos Importados e Licenciamento de Software1.
Redução de custos operacionais, aumento de produtividade e flexibilidade1.
Infraestrutura de Pesquisa
[cite: 3]
Estruturação de laboratórios multiusuários, data centers HPC e redes de testes (testbeds)1.
Concentração em Equipamentos de Capital e Adequação de Data Center1.
Acesso democratizado para ICTs e PMEs, fortalecimento da pesquisa aplicada1.
Capacitação Tecnológica
[cite: 3]
Programas de formação profissional, qualificação em Indústria 4.0 e extensão tecnológica1.
Predominância em Pagamento de Pessoal (Bolsas/Pesquisadores) e Treinamento1.
Formação de recursos humanos qualificados e geração de empregos técnicos1.
Economia Circular
[cite: 3]
Eficiência energética, descarbonização, redução de resíduos e análise de ciclo de vida (LCA)1.
Equilíbrio entre Serviços de Terceiros PJ e Consumo de Insumos1.
Diminuição do impacto ambiental, reuso de recursos e certificações verdes2.

Roteiro de Implantação e Estratégia de Qualidade
A implementação da plataforma está organizada em cinco etapas sequenciais de desenvolvimento e homologação:

Etapa
Duração
Atividades Principais
Entregáveis Técnicos
Etapa 1: Infraestrutura de IA
Semanas 1 e 2
Setup do ambiente Ollama na GPU Ada 1000 (Dev) e do servidor vLLM na RTX 3090 (Prod)6. Quantização e deploy dos modelos Qwen2.5 e Nemotron-70B6.
API de inferência local operacional com suporte a chamadas assíncronas6.
Etapa 2: Ingestão e OCR
Semanas 3 e 4
Desenvolvimento do extrator híbrido (PyMuPDF/pdfplumber + Marker/docTR)4. Implementação das rotas de estruturação JSON e avaliação de lacunas3.
Pipeline de parsing capaz de processar PDFs com codificação corrompida4.
Etapa 3: Interface e Layout
Semanas 5 e 6
Construção da folha A4 em CSS Grid com detectores de overflow em tempo real (ResizeObserver)3. Integração do seletor de temas e upload em Base643.
Editor WYSIWYG responsivo com cálculo exato de espaço A43.
Etapa 4: Assistência de IA
Semanas 7 e 8
Implementação dos botões "✨ Reescrever", ajuste automático de tamanho e tradução (PT/EN/ES)3. Ativação do auto-salvamento em IndexedDB3.
Motor cognitivo interativo com biblioteca de relatórios funcional3.
Etapa 5: Exportação e Testes
Semanas 9 e 10
Configuração do motor de exportação PDF via Puppeteer8. Testes de estresse com a proposta CYBERTECH e validação com usuários1.
Sistema homologado e pronto para implantação em ambiente produtivo.

Para assegurar o funcionamento adequado da solução em ambiente corporativo, a aplicação deve atender aos seguintes critérios de qualidade:
Precisão na Extração de PDFs: O pipeline híbrido deve atingir uma taxa de recuperação correta de dados superior a 95% em propostas formais da FINEP, mesmo em arquivos escaneados ou com tabelas complexas1.
Fidelidade da Exportação PDF: Os relatórios exportados devem possuir dimensões exatas de 210mm × 297mm, sem quebras de página indesejadas, cortes de texto ou distorções nas barras de orçamento e logotipos3.
Desempenho da Inferência: No servidor de produção (RTX 3090 com vLLM), o tempo de resposta para reescritas parciais deve ser inferior a 1,5 segundo, e a tradução completa do relatório não deve exceder 4,0 segundos6.
Integridade dos Dados: O sistema de salvamento automático via IndexedDB deve garantir zero perda de conteúdo durante navegações indevidas ou atualizações da página3.
Referências citadas
Plano De Trabalho Atualizado CYBERTECH.pdf
Resultados e impactos - CYBERTECH.pdf
One Page Report - Cybertech - PT.pdf
Deepdoctection: Open-Source Document AI Orchestration, https://idp-software.com/vendors/deepdoctection/
Is anyone actually adopting Microsoft's new Agent Framework yet?, https://www.reddit.com/r/dotnet/comments/1qo8byw/net_10_ai_is_anyone_actually_adopting_microsofts/
Nemotron 70B Local Setup: NVIDIA RLHF-Refined Llama (2026), https://localaimaster.com/blog/nemotron-70b-local-setup
note4yaoo/lib-ai-app-community-model-popular.md at main - GitHub, https://github.com/uptonking/note4yaoo/blob/main/lib-ai-app-community-model-popular.md
Open-Source PDF Software Directory | PDFog, https://www.pdfog.com/open-source
Aphrodite Engine | Guides - Clore.ai, https://docs.clore.ai/guides/language-models/aphrodite-engine
200+ Local AI Tutorials & Guides (Updated Jan 2026), https://localaimaster.com/blog
Can You Run This LLM? VRAM Calculator (Nvidia GPU and Apple, https://apxml.com/tools/vram-calculator
vllm_cookbook.ipynb - Nemotron-3-Ultra - GitHub, https://github.com/NVIDIA-NeMo/Nemotron/blob/main/usage-cookbook/Nemotron-3-Ultra/vllm_cookbook.ipynb
