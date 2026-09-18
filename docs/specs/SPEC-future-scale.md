# Spec: future-scale (Rust, PostgreSQL, Auth & User Preferences)

> **Module ID**: `future-scale`  
> **Camadas Clean Architecture**: Camadas 1 a 4 (Roadmap de Escala Enterprise)  
> **Status**: Especificação Futura Aprovada (V2)  
> **Versão**: 2.0.0  
> **Depende de**: `domain-core`, `capability-map`  

---

## 1. Objective

Especificar a arquitetura de escala corporativa do **One Page Generator**, migrando o backend crítico para **Rust (Axum)**, estabelecendo persistência relacional em **PostgreSQL** com migrations versionadas, arquivamento auditável de documentos, salvamento de projetos/rascunhos na conta do usuário, autenticação segura (E-mail/Senha + Google OAuth 2.0) com complemento de perfil opcional, e sistema de preferências com suporte nativo a **Modo Claro / Modo Escuro**.

---

## 2. Tech Stack & Executable Docker Commands

- **Backend de Alta Performance**: Rust 1.82+ com **Axum** (Framework Web assíncrono), `tokio`, `tower-http` e `sqlx` (queries assíncronas com type-checking em tempo de compilação).
- **Banco de Dados Relacional**: PostgreSQL 16 (em container Docker isolado).
- **Gerenciador de Migrations**: `sqlx-cli` com scripts SQL determinísticos e versionados.
- **Autenticação**: `argon2` para hashing de senhas, `jsonwebtoken` para tokens JWT stateless e biblioteca `oauth2` para Google OpenID Connect.
- **Armazenamento de Arquivos**: Volume Docker persistente (`archived_documents_data`) com hash SHA-256 para integridade.

### Executable Docker Commands:
```bash
# Executar migrations do banco de dados dentro do container
docker compose run --rm backend sqlx migrate run

# Reverter a última migration (teste de rollback)
docker compose run --rm backend sqlx migrate revert

# Executar testes unitários e de integração do backend Rust
docker compose run --rm backend cargo test --all -- --nocapture

# Verificar integridade e lint do código Rust
docker compose run --rm backend cargo clippy -- -D warnings
```

---

## 3. Project Structure (Rust Clean Architecture)

```
backend-rust/
├── Cargo.toml
├── migrations/
│   ├── 20261001000001_create_users_and_profiles.sql
│   ├── 20261001000002_create_user_preferences.sql
│   ├── 20261001000003_create_report_templates.sql
│   ├── 20261001000004_create_project_drafts.sql
│   └── 20261001000005_create_archived_documents.sql
├── src/
│   ├── domain/               # CAMADA 1: Entidades, Invariantes e Erros
│   │   ├── entities.rs       # User, ProjectDraft, ReportTemplate
│   │   └── value_objects.rs  # Email, PasswordHash, Sha256Hash
│   ├── application/          # CAMADA 2: Casos de Uso e Portas Abstratas
│   │   ├── ports/            # IUserRepository, IProjectRepository, IOAuthService
│   │   └── use_cases/        # AuthenticateUser, SaveDraft, ArchiveDocument
│   ├── adapters/             # CAMADA 3: Implementação de Repositórios e Serviços
│   │   ├── postgres/         # Repositórios SQLx
│   │   └── auth/             # GoogleOAuthAdapter, Argon2Hasher
│   └── infrastructure/       # CAMADA 4: Web Server e Framework
│       ├── main.rs           # Entrypoint Axum e inicialização de rotas
│       ├── routers/          # Rotas /api/v2/auth, /api/v2/projects, /api/v2/templates
│       └── middlewares/      # AuthGuard (JWT), ErrorHandler, Cors
└── Dockerfile
```

---

## 4. Modelagem Relacional e Boas Práticas de Migration

### 4.1. Esquema DDL do PostgreSQL (`migrations/`)

```sql
-- 1. Tabela de Usuários (E-mail/Senha e Social Login)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NULL, -- Nulo para contas criadas via Google
    auth_provider VARCHAR(50) NOT NULL DEFAULT 'local', -- 'local' ou 'google'
    google_id VARCHAR(255) NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Perfil do Usuário (Complemento Opcional)
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    full_name VARCHAR(150),
    institution VARCHAR(150), -- SENAI, FIESC, Indústria Parceira, etc.
    role VARCHAR(100),        -- Pesquisador, Gestor de Inovação, Consultor
    avatar_url TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Configurações e Preferências (Tema Claro/Escuro)
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    theme_mode VARCHAR(20) NOT NULL DEFAULT 'system', -- 'light', 'dark', 'system'
    default_institutional_theme VARCHAR(50) NOT NULL DEFAULT 'SENAI',
    auto_save_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. Biblioteca de Modelos e Templates Estáticos
CREATE TABLE report_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) NOT NULL UNIQUE, -- 'pdi_industrial', 'economia_circular', etc.
    name VARCHAR(100) NOT NULL,
    description TEXT,
    schema_json JSONB NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. Rascunhos de Projetos na Conta do Usuário
CREATE TABLE project_drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    template_id UUID REFERENCES report_templates(id),
    title VARCHAR(255) NOT NULL,
    project_acronym VARCHAR(50),
    content_json JSONB NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    is_archived BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_project_drafts_user_id ON project_drafts(user_id);

-- 6. Arquivamento Auditável de Documentos Submetidos
CREATE TABLE archived_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    project_id UUID REFERENCES project_drafts(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    storage_path TEXT NOT NULL,
    sha256_hash CHAR(64) NOT NULL,
    tsi_score NUMERIC(5, 4),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_archived_documents_sha256 ON archived_documents(sha256_hash);
```

---

## 5. Arquitetura de Autenticação e Gestão de Sessão

```
                     ┌───────────────────────────────────────────────┐
                     │            FRONTEND (SPA React)               │
                     └───────┬───────────────────────────────┬───────┘
                             │                               │
             (1) Login E-mail/Senha              (2) Login Google OAuth
                             │                               │
                             ▼                               ▼
       ┌───────────────────────────────┐       ┌───────────────────────────────┐
       │   POST /api/v2/auth/login     │       │   POST /api/v2/auth/google    │
       │   Verifica Hash Argon2id      │       │   Valida IdToken com Google   │
       └───────────────┬───────────────┘       └───────────────┬───────────────┘
                       │                                       │
                       └───────────────────┬───────────────────┘
                                           │
                                           ▼
                       ┌───────────────────────────────────────┐
                       │ Gera Par de Tokens (JWT Access 15min) │
                       │ Refresh Token HttpOnly Cookie (7 dias)│
                       └───────────────────┬───────────────────┘
                                           │
                                           ▼
                       ┌───────────────────────────────────────┐
                       │ Retorna Perfil + Preferências (Tema)  │
                       │ [Complemento de Perfil se pendente]   │
                       └───────────────────────────────────────┘
```

---

## 6. Sistema de Temas: Aplicação vs Documento A4

Para evitar ambiguidades na experiência do usuário, a plataforma separa estritamente dois escopos de tema:

1. **Tema da Interface da Aplicação (`theme_mode`)**:
   - Controla o layout da plataforma: sidebar, navbar, modais, painel de ferramentas e botões.
   - Opções: `light`, `dark`, ou `system` (respeita `prefers-color-scheme`).
   - Aplicado na tag `<html>` ou `<body>` via classe `.dark` ou `.light`.
2. **Tema Institucional do Documento A4 (`selectedTheme`)**:
   - Controla a identidade visual do infográfico: cabeçalhos, barras de orçamento e acentos das seções.
   - Opções: `SENAI`, `SESI`, `FIESC`, `IEL` e `Corporativo`.
   - **Regra Imutável**: O container A4 é **sempre renderizado sobre fundo branco** ($#FFFFFF$) para preservar a fidelidade visual da impressão física em papel.

---

## 7. Boundaries

- **Always**: Aplicar migrations através de transações atômicas com verificação de idempotência.
- **Always**: Calcular e validar o hash SHA-256 no momento do upload de qualquer documento para arquivamento.
- **Always**: Proteger o refresh token em cookies `HttpOnly`, `Secure` e `SameSite=Strict`.
- **Ask First**: Adicionar colunas obrigatórias (`NOT NULL` sem default) em tabelas com dados produtivos.
- **Never**: Armazenar senhas de usuários em texto plano (usar exclusivamente Argon2id).
- **Never**: Permitir acesso a rascunhos de outros usuários sem autorização expressa (Tenant Isolation).

---

## 8. Success Criteria

- [ ] Latência de requisição de leitura de rascunhos em Rust $< 15\text{ms}$.
- [ ] Todas as migrations executam `up` e `down` com sucesso em ambiente de CI.
- [ ] Integração com Google OAuth validada com mock OIDC nos testes automatizados.
- [ ] Alternância entre Modo Claro e Escuro da UI ocorre instantaneamente sem "flicker" de tela.
