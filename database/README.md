# Modelo de Dados — Personal Finance App

## Visão Geral (20 tabelas principais)

```
                    ┌──────────────────────────────────────────────────┐
                    │                   WORKSPACES                    │
                    │  (multi-tenancy: personal, casal, família)      │
                    └──────────┬──────────────────┬───────────────────┘
                               │                  │
              ┌────────────────┤     ┌────────────┴──────────────┐
              ▼                │     ▼                           ▼
    ┌─────────────────┐        │  ┌────────────────────┐  ┌──────────────┐
    │   WORKSPACE     │        │  │     ACCOUNTS       │  │  CATEGORY    │
    │   MEMBERS       │        │  │ (checking, credit, │  │  GROUPS      │
    │ (owner/editor/  │        │  │  investment, etc)  │  │              │
    │  viewer)        │        │  └────────┬───────────┘  └──────┬───────┘
    └─────────────────┘        │           │                     │
                               │           ▼                     ▼
    ┌─────────────────┐        │  ┌─────────────────────────────────────┐
    │     USERS       │        │  │       TRANSACTION_JOURNALS          │
    │                 │────────┤  │  (grupo atômico: data, descrição,   │
    └─────────────────┘        │  │   valor, parcelamento, import_hash) │
                               │  └────────────────┬────────────────────┘
    ┌─────────────────┐        │                   │
    │     RULES       │        │                   ▼
    │  ENGINE         │        │  ┌─────────────────────────────────────┐
    │ (triggers +     │        │  │         TRANSACTIONS                │
    │  actions)       │        │  │  (dupla entrada: source/destino)    │
    └─────────────────┘        │  └────────────────┬────────────────────┘
                               │                   │
    ┌─────────────────┐        │         ┌─────────┴─────────┐
    │   PLUGGY /      │        │         ▼                   ▼
    │   BANK SYNC     │────────┤  ┌────────────┐    ┌──────────────┐
    │                 │        │  │ CATEGORIES │    │    PAYEES    │
    └─────────────────┘        │  └────────────┘    └──────────────┘
                               │
    ┌─────────────────┐        │  ┌─────────────────────────────────────┐
    │   BUDGETS +     │        │  │         TAGS                        │
    │   LIMITS        │        │  └─────────────────────────────────────┘
    │ (envelope)      │        │
    └─────────────────┘        │  ┌─────────────────────────────────────┐
                               │  │     SYNC_MESSAGES (CRDT)            │
    ┌─────────────────┐        │  │  (offline-first, conflitos          │
    │   AI AGENTS     │        │  │   resolvidos via timestamp)          │
    │ + RAG (pgvector)│        │  └─────────────────────────────────────┘
    └─────────────────┘        │
                               │  ┌─────────────────────────────────────┐
    ┌─────────────────┐        │  │     CREDIT_CARD_BILLS               │
    │   RECURRING     │        │  │  (faturas com fechamento, vencimento)│
    │   TRANSACTIONS  │        │  └─────────────────────────────────────┘
    └─────────────────┘        │
                               │  ┌─────────────────────────────────────┐
    ┌─────────────────┐        │  │     GOALS (piggy banks)             │
    │   ATTACHMENTS   │        │  └─────────────────────────────────────┘
    └─────────────────┘        │
```

## Decisões de Design

### 1. Multi-Tenancy com Workspaces (Securo)
Cada dado financeiro pertence a um `workspace`. Um usuário pode pertencer a múltiplos workspaces com papéis diferentes (owner = admin, editor = CRUD, viewer = read-only). Isso permite:
- Modo casal (2 pessoas, 1 workspace)
- Controle parental (pais editam, filhos veem)
- Freelancer (workspace pessoal + profissional)

### 2. Dupla Entrada (Firefly III)
Toda transação tem um `transaction_journal` (grupo) + 2 `transactions` (débito/crédito).
Exemplo: transferir R$100 da conta corrente pra poupança:
```
journal: {type: 'transfer', amount: 100, date: '2026-06-01'}
  transaction 1: {account: 'corrente', amount: -100}  (source)
  transaction 2: {account: 'poupança', amount: +100}  (dest)
```

### 3. Parcelamento Nativo (Securo)
Campos diretos no journal: `is_installment`, `installment_number`, `total_installments`, `installment_total_amount`. Isso resolve um dos maiores gaps do Firefly III (que trata parcelamento como transações separadas sem vínculo).

### 4. CRDT Sync (Actual Budget)
`sync_messages` armazena cada alteração como uma mensagem imutável com timestamp. O servidor é só um relay. Conflitos são resolvidos por last-writer-wins. Isso permite:
- Offline-first (funciona sem internet)
- Multi-dispositivo sem conflito
- Undo de qualquer ação

### 5. AI + RAG (Securo)
`knowledge_documents` usa `pgvector` para buscar contexto financeiro do usuário em linguagem natural. O usuário pode perguntar "quanto gastei em restaurante esse mês?" e o AI responde com os dados reais.

### 6. Engine de Regras (Firefly III)
`rules` + `rule_triggers` + `rule_actions` permite auto-categorização:
```
SE descrição contém "UBER" → categoriza como "Transporte"
SE valor > 500 E categoria = "Lazer" → adiciona tag "Gasto Alto"
```

### 7. Bank Sync Genérico (Pluggy)
`bank_connections` tem `provider` ENUM. Cada provider (Pluggy, TecnoSpeed, Belvo) implementa o mesmo contrato. Fácil trocar ou adicionar.

## Tamanho Estimado

| Tabela | Registros esperados (1 ano, 1 usuário) |
|--------|--------------------------------------|
| transaction_journals | ~1.000-3.000 |
| transactions | ~2.000-6.000 |
| accounts | 5-20 |
| categories | 20-50 |
| budgets | 1-5 |
| rules | 0-30 |
| sync_messages | ~50.000 (toda alteração é registrada) |
| bank_connections | 1-10 |
| credit_card_bills | 12-24 |
