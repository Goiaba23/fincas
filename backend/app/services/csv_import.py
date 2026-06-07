import hashlib
import io
import re
from datetime import date, datetime
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import TransactionJournal, Transaction
from app.models.category import Category
from app.models.merchant import MerchantMapping

EXPECTED_COLUMNS = {"date", "description", "amount", "type"}
BANK_COLUMN_ALIASES = {
    "data": "date",
    "data_mov": "date",
    "data_lanc": "date",
    "data_transacao": "date",
    "lançamento": "date",
    "historico": "description",
    "descrição": "description",
    "descricao": "description",
    "histórico": "description",
    "movimento": "description",
    "titulo": "description",
    "título": "description",
    "valor": "amount",
    "valr": "amount",
    "value": "amount",
    "débito_crédito": "type",
    "dc": "type",
    "entrada_saida": "type",
    "tipo": "type",
    "sinal": "type",
}


def normalize_merchant(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\b(pg|pag|ref|recibo|nf|nota)\b", "", name)
    for prefix in ["pg ", "pag ", "compra ", "compra "]:
        if name.startswith(prefix):
            name = name[len(prefix):]
    return name.strip()


def compute_import_hash(row: dict) -> str:
    raw = f"{row.get('date', '')}|{row.get('amount', '')}|{row.get('description', '')}|{row.get('external_id', '')}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class CsvImportPipeline:

    def __init__(self, db: AsyncSession, workspace_id: str, account_id: str | None = None):
        self.db = db
        self.workspace_id = workspace_id
        self.account_id = account_id
        self.errors: list[str] = []
        self.preview_rows: list[dict] = []
        self.merchant_cache: dict[str, dict] = {}

    async def _load_merchant_cache(self):
        result = await self.db.execute(select(MerchantMapping).where(
            MerchantMapping.workspace_id == self.workspace_id
        ))
        for m in result.scalars().all():
            self.merchant_cache[m.normalized_name] = {
                "category_id": str(m.category_id) if m.category_id else None,
                "payee_id": str(m.payee_id) if m.payee_id else None,
                "is_income": m.is_income,
            }

    async def _auto_match_merchant(self, description: str) -> dict:
        normalized = normalize_merchant(description)
        if normalized in self.merchant_cache:
            return self.merchant_cache[normalized]
        # fuzzy: partial match
        for key, val in self.merchant_cache.items():
            if key in normalized or normalized in key:
                return val
        return {"category_id": None, "payee_id": None, "is_income": False}

    # ---- Pipeline Stages ----

    def stage1_validate(self, df: pd.DataFrame) -> pd.DataFrame:
        cols = set(c.lower().strip() for c in df.columns)
        mapped = set()
        for c in cols:
            if c in EXPECTED_COLUMNS:
                mapped.add(c)
            elif c in BANK_COLUMN_ALIASES:
                mapped.add(BANK_COLUMN_ALIASES[c])
        missing = EXPECTED_COLUMNS - mapped
        if missing:
            raise ValueError(
                f"Colunas obrigatórias ausentes: {missing}. "
                f"Colunas encontradas: {list(df.columns)}"
            )
        return df

    def stage2_normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.strip()
        return df

    def stage3_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        renamed = {}
        for c in df.columns:
            low = c.lower().strip()
            if low in BANK_COLUMN_ALIASES:
                renamed[c] = BANK_COLUMN_ALIASES[low]
            else:
                renamed[c] = low
        df = df.rename(columns=renamed)

        if "amount" in df.columns:
            df["amount"] = (
                df["amount"]
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
                .str.replace(r"[^\d.-]", "", regex=True)
            )
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

        if "type" in df.columns:
            df["type_lower"] = df["type"].str.lower().str.strip()
            df["is_negative"] = df["type_lower"].apply(
                lambda x: x in ("débito", "debito", "debit", "saída", "saida", "saque", "pagamento", "-", "d")
            )
        else:
            df["is_negative"] = df["amount"] < 0

        df["amount_abs"] = df["amount"].abs()
        return df

    async def stage4_enrich(self, df: pd.DataFrame) -> pd.DataFrame:
        await self._load_merchant_cache()
        enriched = []
        for _, row in df.iterrows():
            desc = str(row.get("description", ""))
            match = await self._auto_match_merchant(desc)
            enriched.append({
                "date": row["date"].date() if pd.notna(row["date"]) else date.today(),
                "description": desc,
                "amount": float(row["amount_abs"]),
                "type": "deposit" if row["is_negative"] is False else "withdrawal",
                "category_id": match["category_id"],
                "payee_id": match["payee_id"],
                "is_income": match["is_income"],
                "import_hash": "",
            })
        return pd.DataFrame(enriched)

    def stage5_business_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        rules_applied = []
        salary_keywords = ["salário", "salario", "pagamento sal", "holerite", "transferência sal"]
        for _, row in df.iterrows():
            desc = row["description"].lower()
            is_salary = any(k in desc for k in salary_keywords)
            if is_salary:
                row["is_income"] = True
                row["category_id"] = None  # will be set to salary category
            rules_applied.append(row)
        return pd.DataFrame(rules_applied)

    def stage6_preview(self, df: pd.DataFrame) -> list[dict]:
        preview = []
        for _, row in df.iterrows():
            h = compute_import_hash(row.to_dict())
            preview.append({
                "date": row["date"].isoformat() if hasattr(row["date"], "isoformat") else str(row["date"]),
                "description": row["description"],
                "amount": row["amount"],
                "type": row["type"],
                "category_id": row.get("category_id"),
                "payee_id": row.get("payee_id"),
                "is_income": row.get("is_income", False),
                "import_hash": h,
            })
        self.preview_rows = preview
        return preview

    async def stage7_commit(self, df: pd.DataFrame) -> dict:
        imported = 0
        skipped = 0
        failed = 0
        for _, row in df.iterrows():
            try:
                h = compute_import_hash(row.to_dict())
                # dedup check
                existing = await self.db.execute(
                    select(TransactionJournal).where(
                        TransactionJournal.import_hash == h,
                        TransactionJournal.workspace_id == self.workspace_id,
                    )
                )
                if existing.scalar_one_or_none():
                    skipped += 1
                    continue

                category_id = row.get("category_id")
                journal = TransactionJournal(
                    workspace_id=self.workspace_id,
                    transaction_type="deposit" if row.get("is_income") else "withdrawal",
                    description=row["description"],
                    date=row["date"],
                    amount=row["amount"],
                    currency_code="BRL",
                    category_id=category_id,
                    import_hash=h,
                )
                self.db.add(journal)
                await self.db.flush()

                if self.account_id:
                    tx = Transaction(
                        journal_id=journal.id,
                        account_id=self.account_id,
                        amount=-row["amount"] if row.get("is_income") else row["amount"],
                    )
                    self.db.add(tx)

                imported += 1
            except Exception:
                failed += 1

        await self.db.flush()
        return {"imported": imported, "skipped": skipped, "failed": failed}

    async def run_pipeline(self, raw: str, account_id: str | None = None) -> dict:
        df = pd.read_csv(io.StringIO(raw))
        df = self.stage1_validate(df)
        df = self.stage2_normalize(df)
        df = self.stage3_transform(df)
        df = await self.stage4_enrich(df)
        df = self.stage5_business_rules(df)
        preview = self.stage6_preview(df)
        return {"preview": preview, "total": len(preview)}

    async def confirm_import(self, raw: str) -> dict:
        df = pd.read_csv(io.StringIO(raw))
        df = self.stage1_validate(df)
        df = self.stage2_normalize(df)
        df = self.stage3_transform(df)
        df = await self.stage4_enrich(df)
        df = self.stage5_business_rules(df)
        result = await self.stage7_commit(df)
        return result
