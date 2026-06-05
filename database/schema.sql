-- ==============================================================
-- SCHEMA: Personal Finance App
-- Inspirado em: Firefly III (dupla entrada), Securo (workspaces,
--   Pluggy, AI), Actual Budget (envelope budgeting, CRDT sync)
-- Database: PostgreSQL 16 + pgvector + pgcrypto
-- ==============================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pgvector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==============================================================
-- 1. AUTH & MULTI-TENANCY
-- ==============================================================

CREATE TYPE workspace_kind AS ENUM (
  'personal', 'couple', 'family', 'freelancer', 'small_business'
);

CREATE TYPE member_role AS ENUM (
  'owner', 'editor', 'viewer'
);

CREATE TABLE users (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email         VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  display_name  VARCHAR(100),
  avatar_url    TEXT,
  locale        VARCHAR(10) DEFAULT 'pt-BR',
  timezone      VARCHAR(50) DEFAULT 'America/Sao_Paulo',
  currency_code VARCHAR(3) DEFAULT 'BRL',
  is_2fa_enabled BOOLEAN DEFAULT FALSE,
  totp_secret   TEXT,
  is_active     BOOLEAN DEFAULT TRUE,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE workspaces (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name            VARCHAR(255) NOT NULL,
  kind            workspace_kind DEFAULT 'personal',
  icon            VARCHAR(50),
  color           VARCHAR(7),
  default_currency VARCHAR(3) DEFAULT 'BRL',
  locale          VARCHAR(10) DEFAULT 'pt-BR',
  is_archived     BOOLEAN DEFAULT FALSE,
  created_by      UUID NOT NULL REFERENCES users(id),
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE workspace_members (
  workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role            member_role NOT NULL DEFAULT 'editor',
  invited_by      UUID REFERENCES users(id),
  joined_at       TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (workspace_id, user_id)
);

CREATE TABLE user_preferences (
  user_id       UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  preferences   JSONB NOT NULL DEFAULT '{}',
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ==============================================================
-- 2. CURRENCIES & EXCHANGE RATES
-- ==============================================================

CREATE TABLE currencies (
  code          VARCHAR(3) PRIMARY KEY,
  name          VARCHAR(100) NOT NULL,
  symbol        VARCHAR(10) NOT NULL,
  decimal_places INT DEFAULT 2,
  is_active     BOOLEAN DEFAULT TRUE
);

CREATE TABLE exchange_rates (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  from_currency VARCHAR(3) NOT NULL REFERENCES currencies(code),
  to_currency   VARCHAR(3) NOT NULL REFERENCES currencies(code),
  rate          NUMERIC(18, 8) NOT NULL,
  date          DATE NOT NULL DEFAULT CURRENT_DATE,
  source        VARCHAR(50) DEFAULT 'bcb_ptax',
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (from_currency, to_currency, date)
);

-- ==============================================================
-- 3. ACCOUNTS (Firefly III + Securo model)
-- ==============================================================

CREATE TYPE account_type AS ENUM (
  'checking', 'savings', 'credit_card', 'investment',
  'loan', 'mortgage', 'cash', 'asset', 'liability',
  'receivable', 'payable'
);

CREATE TABLE accounts (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  account_type    account_type NOT NULL,
  name            VARCHAR(255) NOT NULL,
  description     TEXT,
  currency_code   VARCHAR(3) NOT NULL REFERENCES currencies(code),
  balance         NUMERIC(15, 2) DEFAULT 0,
  balance_date    DATE DEFAULT CURRENT_DATE,
  is_archived     BOOLEAN DEFAULT FALSE,
  is_off_budget   BOOLEAN DEFAULT FALSE,
  -- Credit card specific
  credit_limit      NUMERIC(15, 2),
  statement_close_day INT,
  statement_due_day   INT,
  card_brand        VARCHAR(50),
  card_last_digits  VARCHAR(4),
  -- Bank sync fields (Pluggy)
  external_id       VARCHAR(255),
  external_item_id  VARCHAR(255),
  connector_provider VARCHAR(50),
  last_sync_at      TIMESTAMPTZ,
  -- Metadata
  color             VARCHAR(7),
  icon              VARCHAR(50),
  sort_order        INT DEFAULT 0,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_accounts_workspace ON accounts(workspace_id);
CREATE INDEX idx_accounts_type ON accounts(account_type);

-- ==============================================================
-- 4. TRANSACTIONS (Double-entry: Firefly III model)
-- ==============================================================

CREATE TYPE transaction_type AS ENUM (
  'withdrawal', 'deposit', 'transfer', 'opening_balance', 'reconciliation'
);

-- A journal groups a double-entry transaction (one journal = atomic event)
CREATE TABLE transaction_journals (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id      UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  transaction_type  transaction_type NOT NULL,
  description       TEXT,
  date              DATE NOT NULL,
  effective_date    DATE,
  currency_code     VARCHAR(3) NOT NULL REFERENCES currencies(code),
  amount            NUMERIC(15, 2) NOT NULL,
  -- For foreign currency transactions
  foreign_amount      NUMERIC(15, 2),
  foreign_currency_id VARCHAR(3) REFERENCES currencies(code),
  exchange_rate       NUMERIC(18, 8),
  -- Who/where
  payee_id            UUID,
  notes               TEXT,
  -- Installment tracking (Securo model)
  is_installment          BOOLEAN DEFAULT FALSE,
  installment_number      INT,
  total_installments      INT,
  installment_total_amount NUMERIC(15, 2),
  -- Recurring reference
  recurring_id            UUID,
  -- Import tracking
  import_hash             VARCHAR(64),
  external_id             VARCHAR(255),
  -- CRDT sync fields (Actual Budget inspired)
  sync_version            INT DEFAULT 1,
  is_pending              BOOLEAN DEFAULT FALSE,
  created_by              UUID REFERENCES users(id),
  created_at              TIMESTAMPTZ DEFAULT NOW(),
  updated_at              TIMESTAMPTZ DEFAULT NOW()
);

-- Double-entry lines: each journal has 2+ lines
CREATE TABLE transactions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  journal_id      UUID NOT NULL REFERENCES transaction_journals(id) ON DELETE CASCADE,
  account_id      UUID NOT NULL REFERENCES accounts(id),
  amount          NUMERIC(15, 2) NOT NULL,
  -- Reconciled status
  is_reconciled   BOOLEAN DEFAULT FALSE,
  reconciled_at   TIMESTAMPTZ,
  -- Order within journal (1 = source, 2 = destination)
  sort_order      INT DEFAULT 0,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_journals_workspace ON transaction_journals(workspace_id);
CREATE INDEX idx_journals_date ON transaction_journals(date);
CREATE INDEX idx_journals_payee ON transaction_journals(payee_id);
CREATE INDEX idx_journals_external ON transaction_journals(external_id);
CREATE INDEX idx_journals_import_hash ON transaction_journals(import_hash);
CREATE INDEX idx_transactions_journal ON transactions(journal_id);
CREATE INDEX idx_transactions_account ON transactions(account_id);

-- ==============================================================
-- 5. CATEGORIES (Firefly III + Securo)
-- ==============================================================

CREATE TABLE category_groups (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id  UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  name          VARCHAR(255) NOT NULL,
  sort_order    INT DEFAULT 0,
  is_income     BOOLEAN DEFAULT FALSE,
  color         VARCHAR(7),
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE categories (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  group_id        UUID NOT NULL REFERENCES category_groups(id) ON DELETE CASCADE,
  name            VARCHAR(255) NOT NULL,
  description     TEXT,
  sort_order      INT DEFAULT 0,
  is_hidden       BOOLEAN DEFAULT FALSE,
  color           VARCHAR(7),
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE journal_category (
  journal_id    UUID NOT NULL REFERENCES transaction_journals(id) ON DELETE CASCADE,
  category_id   UUID NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
  PRIMARY KEY (journal_id, category_id)
);

-- ==============================================================
-- 6. PAYEES
-- ==============================================================

CREATE TABLE payees (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id  UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  name          VARCHAR(255) NOT NULL,
  normalized_name VARCHAR(255),
  category_id   UUID REFERENCES categories(id),
  is_merchant   BOOLEAN DEFAULT TRUE,
  logo_url      TEXT,
  external_id   VARCHAR(255),
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_payees_workspace ON payees(workspace_id);

-- ==============================================================
-- 7. TAGS
-- ==============================================================

CREATE TABLE tags (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id  UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  name          VARCHAR(255) NOT NULL,
  color         VARCHAR(7),
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (workspace_id, name)
);

CREATE TABLE journal_tag (
  journal_id    UUID NOT NULL REFERENCES transaction_journals(id) ON DELETE CASCADE,
  tag_id        UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (journal_id, tag_id)
);

-- ==============================================================
-- 8. BUDGETS (Firefly III + Envelope style from Actual)
-- ==============================================================

CREATE TYPE budget_type AS ENUM ('envelope', 'tracking');

CREATE TABLE budgets (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id  UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  name          VARCHAR(255) NOT NULL,
  budget_type   budget_type DEFAULT 'envelope',
  currency_code VARCHAR(3) NOT NULL REFERENCES currencies(code),
  is_active     BOOLEAN DEFAULT TRUE,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Budget limits: how much per category per period
CREATE TABLE budget_limits (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  budget_id       UUID NOT NULL REFERENCES budgets(id) ON DELETE CASCADE,
  category_id     UUID NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
  amount          NUMERIC(15, 2) NOT NULL,
  period          VARCHAR(20) NOT NULL DEFAULT 'monthly',
  start_date      DATE NOT NULL,
  end_date        DATE,
  is_carryover    BOOLEAN DEFAULT FALSE,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ==============================================================
-- 9. RULES ENGINE (Firefly III inspired)
-- ==============================================================

CREATE TABLE rule_groups (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id  UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  name          VARCHAR(255) NOT NULL,
  description   TEXT,
  sort_order    INT DEFAULT 0,
  is_active     BOOLEAN DEFAULT TRUE,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE rules (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  group_id        UUID NOT NULL REFERENCES rule_groups(id) ON DELETE CASCADE,
  name            VARCHAR(255) NOT NULL,
  description     TEXT,
  sort_order      INT DEFAULT 0,
  is_active       BOOLEAN DEFAULT TRUE,
  stop_processing BOOLEAN DEFAULT FALSE,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TYPE trigger_type AS ENUM (
  'description_contains', 'description_is', 'description_starts',
  'description_ends', 'description_matches',
  'amount_is', 'amount_less', 'amount_more',
  'date_is', 'date_before', 'date_after',
  'account_is', 'account_contains',
  'category_is', 'category_contains',
  'payee_is', 'payee_contains',
  'tags_match',
  'transaction_type_is',
  'has_notes', 'has_no_category',
  'expression_is'
);

CREATE TABLE rule_triggers (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rule_id       UUID NOT NULL REFERENCES rules(id) ON DELETE CASCADE,
  trigger_type  trigger_type NOT NULL,
  value         TEXT NOT NULL,
  is_negated    BOOLEAN DEFAULT FALSE,
  sort_order    INT DEFAULT 0
);

CREATE TYPE action_type AS ENUM (
  'set_category', 'clear_category',
  'set_budget', 'clear_budget',
  'add_tag', 'remove_tag', 'remove_all_tags',
  'set_description',
  'set_payee',
  'set_notes', 'clear_notes',
  'set_amount',
  'set_source_account', 'set_destination_account',
  'link_to_bill',
  'convert_withdrawal', 'convert_deposit', 'convert_transfer',
  'delete_transaction'
);

CREATE TABLE rule_actions (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rule_id       UUID NOT NULL REFERENCES rules(id) ON DELETE CASCADE,
  action_type   action_type NOT NULL,
  value         TEXT,
  sort_order    INT DEFAULT 0
);

-- ==============================================================
-- 10. RECURRING TRANSACTIONS & BILLS
-- ==============================================================

CREATE TABLE recurring_transactions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  description     TEXT NOT NULL,
  transaction_type transaction_type NOT NULL,
  amount          NUMERIC(15, 2) NOT NULL,
  source_account_id UUID REFERENCES accounts(id),
  dest_account_id   UUID REFERENCES accounts(id),
  category_id     UUID REFERENCES categories(id),
  payee_id        UUID REFERENCES payees(id),
  -- Recurrence rule (rrule format)
  rrule           TEXT NOT NULL,
  frequency       VARCHAR(20) NOT NULL,
  interval_count  INT DEFAULT 1,
  day_of_month    INT,
  month_of_year   INT,
  day_of_week     VARCHAR(20),
  -- Dates
  start_date      DATE NOT NULL,
  end_date        DATE,
  next_occurrence DATE,
  last_occurrence DATE,
  -- Auto-create
  auto_create     BOOLEAN DEFAULT TRUE,
  notes           TEXT,
  is_active       BOOLEAN DEFAULT TRUE,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE bills (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  name            VARCHAR(255) NOT NULL,
  description     TEXT,
  amount_min      NUMERIC(15, 2) NOT NULL,
  amount_max      NUMERIC(15, 2),
  date            DATE NOT NULL,
  repeat_freq     VARCHAR(20),
  payee_id        UUID REFERENCES payees(id),
  category_id     UUID REFERENCES categories(id),
  account_id      UUID REFERENCES accounts(id),
  is_active       BOOLEAN DEFAULT TRUE,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ==============================================================
-- 11. GOALS / SAVINGS (Firefly III Piggy Banks + Securo Goals)
-- ==============================================================

CREATE TABLE goals (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  name            VARCHAR(255) NOT NULL,
  description     TEXT,
  target_amount   NUMERIC(15, 2) NOT NULL,
  current_amount  NUMERIC(15, 2) DEFAULT 0,
  target_date     DATE,
  account_id      UUID REFERENCES accounts(id),
  category_id     UUID REFERENCES categories(id),
  -- The "piggy bank" logic from Firefly III
  is_piggy_bank   BOOLEAN DEFAULT FALSE,
  sort_order      INT DEFAULT 0,
  is_completed    BOOLEAN DEFAULT FALSE,
  completed_at    TIMESTAMPTZ,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ==============================================================
-- 12. GROUP SPENDING (Securo model)
-- ==============================================================

CREATE TABLE group_spending (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  journal_id      UUID NOT NULL REFERENCES transaction_journals(id) ON DELETE CASCADE,
  paid_by         UUID NOT NULL REFERENCES users(id),
  description     TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE group_splits (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  group_spending_id UUID NOT NULL REFERENCES group_spending(id) ON DELETE CASCADE,
  user_id         UUID NOT NULL REFERENCES users(id),
  amount          NUMERIC(15, 2) NOT NULL,
  is_settled      BOOLEAN DEFAULT FALSE,
  settled_at      TIMESTAMPTZ,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ==============================================================
-- 13. BANK SYNC (Pluggy / TecnoSpeed)
-- ==============================================================

CREATE TYPE sync_provider AS ENUM (
  'pluggy', 'tecno_speed', 'belvo', 'enable_banking', 'simplefin'
);

CREATE TYPE connection_status AS ENUM (
  'connected', 'disconnected', 'error', 'pending', 'expired'
);

CREATE TABLE bank_connections (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id      UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id           UUID NOT NULL REFERENCES users(id),
  provider          sync_provider NOT NULL,
  external_item_id  VARCHAR(255) NOT NULL,
  external_connector_id VARCHAR(255),
  -- Encrypted credentials
  credentials_encrypted TEXT,
  status            connection_status DEFAULT 'connected',
  last_sync_at      TIMESTAMPTZ,
  last_sync_error   TEXT,
  sync_frequency_min INT DEFAULT 240, -- 4 hours default
  is_active         BOOLEAN DEFAULT TRUE,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (provider, external_item_id)
);

-- Transaction from bank sync (deduplication)
CREATE TABLE import_logs (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  connection_id     UUID REFERENCES bank_connections(id),
  workspace_id      UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  status            VARCHAR(20) NOT NULL DEFAULT 'pending',
  transactions_found INT DEFAULT 0,
  transactions_imported INT DEFAULT 0,
  transactions_skipped  INT DEFAULT 0,
  error_message     TEXT,
  started_at        TIMESTAMPTZ,
  completed_at      TIMESTAMPTZ,
  created_at        TIMESTAMPTZ DEFAULT NOW()
);

-- Sync audit trail
CREATE TABLE sync_audit (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  connection_id   UUID REFERENCES bank_connections(id) ON DELETE CASCADE,
  event_type      VARCHAR(50) NOT NULL,
  status          VARCHAR(20) NOT NULL,
  message         TEXT,
  metadata        JSONB,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ==============================================================
-- 14. CREDIT CARDS (Securo model - fatura management)
-- ==============================================================

CREATE TYPE bill_status AS ENUM (
  'open', 'closed', 'paid', 'overdue', 'partial'
);

CREATE TABLE credit_card_bills (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id      UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  closing_date    DATE NOT NULL,
  due_date        DATE NOT NULL,
  total_amount    NUMERIC(15, 2) DEFAULT 0,
  minimum_payment NUMERIC(15, 2),
  paid_amount     NUMERIC(15, 2) DEFAULT 0,
  status          bill_status DEFAULT 'open',
  is_closed       BOOLEAN DEFAULT FALSE,
  paid_at         TIMESTAMPTZ,
  external_id     VARCHAR(255),
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bills_account ON credit_card_bills(account_id);
CREATE INDEX idx_bills_due_date ON credit_card_bills(due_date);

-- ==============================================================
-- 15. AI & ASSISTANT (Securo MCP + RAG model)
-- ==============================================================

CREATE TYPE ai_provider AS ENUM (
  'openai', 'anthropic', 'ollama', 'openai_compatible'
);

CREATE TABLE ai_connections (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  provider        ai_provider NOT NULL,
  display_name    VARCHAR(100),
  model           VARCHAR(100),
  config          JSONB NOT NULL DEFAULT '{}',
  is_default      BOOLEAN DEFAULT FALSE,
  is_active       BOOLEAN DEFAULT TRUE,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE ai_conversations (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  workspace_id    UUID REFERENCES workspaces(id),
  title           VARCHAR(255),
  provider_id     UUID REFERENCES ai_connections(id),
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE ai_messages (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL REFERENCES ai_conversations(id) ON DELETE CASCADE,
  role            VARCHAR(20) NOT NULL,
  content         TEXT NOT NULL,
  tool_calls      JSONB,
  token_count     INT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Knowledge base for RAG (pgvector)
CREATE TABLE knowledge_documents (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  title           VARCHAR(255),
  content         TEXT NOT NULL,
  content_type    VARCHAR(50) DEFAULT 'text',
  embedding       vector(1536),
  metadata        JSONB DEFAULT '{}',
  created_by      UUID REFERENCES users(id),
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_knowledge_embedding ON knowledge_documents
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- ==============================================================
-- 16. ATTACHMENTS (Polymorphic)
-- ==============================================================

CREATE TABLE attachments (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  attachable_id   UUID NOT NULL,
  attachable_type VARCHAR(50) NOT NULL,
  filename        VARCHAR(255) NOT NULL,
  original_name   VARCHAR(255) NOT NULL,
  mime_type       VARCHAR(100),
  size_bytes      INT,
  storage_path    TEXT NOT NULL,
  description     TEXT,
  created_by      UUID REFERENCES users(id),
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_attachments_polymorphic ON attachments(attachable_id, attachable_type);

-- ==============================================================
-- 17. NOTIFICATIONS
-- ==============================================================

CREATE TABLE notification_channels (
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  channel       VARCHAR(50) NOT NULL, -- 'email', 'push', 'whatsapp'
  is_enabled    BOOLEAN DEFAULT TRUE,
  config        JSONB DEFAULT '{}',
  PRIMARY KEY (user_id, channel)
);

CREATE TABLE notifications (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  workspace_id  UUID REFERENCES workspaces(id),
  type          VARCHAR(50) NOT NULL,
  title         VARCHAR(255) NOT NULL,
  body          TEXT,
  data          JSONB,
  is_read       BOOLEAN DEFAULT FALSE,
  read_at       TIMESTAMPTZ,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id, is_read, created_at DESC);

-- ==============================================================
-- 18. CRDT SYNC (Actual Budget inspired)
-- ==============================================================

CREATE TABLE sync_messages (
  id            BIGSERIAL PRIMARY KEY,
  workspace_id  UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id       UUID NOT NULL REFERENCES users(id),
  dataset       VARCHAR(100) NOT NULL,
  row_id        UUID NOT NULL,
  column_name   VARCHAR(100),
  value         JSONB,
  timestamp     BIGINT NOT NULL,
  vector_clock  TEXT,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sync_workspace ON sync_messages(workspace_id, timestamp);
CREATE INDEX idx_sync_row ON sync_messages(workspace_id, dataset, row_id);

-- Merkle tree for sync integrity
CREATE TABLE sync_merkle (
  workspace_id  UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  node_hash     VARCHAR(64) NOT NULL,
  depth         INT NOT NULL,
  left_hash     VARCHAR(64),
  right_hash    VARCHAR(64),
  PRIMARY KEY (workspace_id, node_hash)
);

-- ==============================================================
-- 19. SUBSCRIPTIONS / SAAS (Stripe/Asaas)
-- ==============================================================

CREATE TABLE subscriptions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  provider        VARCHAR(50) NOT NULL, -- 'stripe', 'asaas'
  provider_subscription_id VARCHAR(255),
  plan_code       VARCHAR(50) NOT NULL,
  status          VARCHAR(50) NOT NULL,
  current_period_start TIMESTAMPTZ,
  current_period_end   TIMESTAMPTZ,
  trial_started_at TIMESTAMPTZ,
  trial_end       TIMESTAMPTZ,
  cancel_at       TIMESTAMPTZ,
  canceled_at     TIMESTAMPTZ,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ==============================================================
-- 20. SYSTEM
-- ==============================================================

CREATE TABLE app_settings (
  key           VARCHAR(255) PRIMARY KEY,
  value         JSONB NOT NULL,
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ==============================================================
-- 21. FINCAS METHODS GLOBAIS
-- Kakeibo (Japão), Tsumitate (Japão), Regra 10 (Holanda),
-- Lagom (Suécia), Desafio Suíço (Suíça), Acordo a Dois (Holanda),
-- Limpeza Financeira (Suécia/Döstädning)
-- ==============================================================

CREATE TYPE fincas_method AS ENUM (
  'kakeibo', 'envelope_pix', 'tsumitate', 'regra_10',
  'lagom', 'desafio_suico', 'acordo_dois', 'limpeza_financeira'
);

-- Methods enabled per workspace
CREATE TABLE workspace_methods (
  workspace_id   UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  method         fincas_method NOT NULL,
  is_enabled     BOOLEAN DEFAULT TRUE,
  config         JSONB NOT NULL DEFAULT '{}',
  created_at     TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (workspace_id, method)
);

-- Kakeibo weekly check-ins (4 perguntas)
CREATE TABLE kakeibo_entries (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id   UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id        UUID NOT NULL REFERENCES users(id),
  week_start     DATE NOT NULL,
  total_income   NUMERIC(15,2),
  total_expenses NUMERIC(15,2),
  savings_amount NUMERIC(15,2),
  -- As 4 perguntas do Kakeibo
  q1_available   TEXT,    -- Quanto dinheiro você tem disponível?
  q2_save_goal   TEXT,    -- Quanto gostaria de poupar?
  q3_spending    TEXT,    -- Quanto está gastando?
  q4_improve     TEXT,    -- Como pode melhorar?
  reflection     TEXT,
  mood           VARCHAR(20), -- 'great', 'okay', 'struggling'
  created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Kakeibo 4-category spending (essenciais, desejos, cultura, imprevistos)
CREATE TABLE kakeibo_spending (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  entry_id       UUID NOT NULL REFERENCES kakeibo_entries(id) ON DELETE CASCADE,
  category       VARCHAR(20) NOT NULL CHECK (category IN ('essential', 'wants', 'culture', 'unexpected')),
  description    TEXT,
  amount         NUMERIC(15,2) NOT NULL,
  journal_id     UUID REFERENCES transaction_journals(id),
  created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Tsumitate / Micro-savings rules (Poupança automática)
CREATE TABLE micro_savings (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id      UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  name              VARCHAR(255) NOT NULL,
  savings_type      VARCHAR(20) NOT NULL CHECK (savings_type IN ('daily', 'weekly', 'per_transaction', 'roundup', 'percent_income')),
  amount            NUMERIC(15,2),
  percentage        NUMERIC(5,2),
  source_account_id UUID REFERENCES accounts(id),
  target_account_id UUID REFERENCES accounts(id),
  goal_id           UUID REFERENCES goals(id),
  is_active         BOOLEAN DEFAULT TRUE,
  run_count         INT DEFAULT 0,
  total_saved       NUMERIC(15,2) DEFAULT 0,
  last_run_at       TIMESTAMPTZ,
  config            JSONB DEFAULT '{}',
  created_at        TIMESTAMPTZ DEFAULT NOW()
);

-- Log de execução das micro-savings
CREATE TABLE micro_savings_log (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  micro_savings_id UUID NOT NULL REFERENCES micro_savings(id) ON DELETE CASCADE,
  amount          NUMERIC(15,2) NOT NULL,
  journal_id      UUID REFERENCES transaction_journals(id),
  executed_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Seed basic currencies
INSERT INTO currencies (code, name, symbol, decimal_places) VALUES
  ('BRL', 'Brazilian Real', 'R$', 2),
  ('USD', 'US Dollar', '$', 2),
  ('EUR', 'Euro', '€', 2),
  ('GBP', 'British Pound', '£', 2),
  ('ARS', 'Argentine Peso', '$', 2),
  ('PYG', 'Paraguayan Guarani', '₲', 0);
