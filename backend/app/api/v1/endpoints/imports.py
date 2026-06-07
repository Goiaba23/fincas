from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.merchant import MerchantMapping, CsvImportLog
from app.models.category import Category
from app.services.csv_import import CsvImportPipeline

router = APIRouter(prefix="/imports", tags=["imports"])


class PreviewResponse(BaseModel):
    preview: list[dict]
    total: int


class ConfirmResponse(BaseModel):
    imported: int
    skipped: int
    failed: int


class MerchantCreate(BaseModel):
    merchant_name: str
    category_id: str | None = None
    payee_id: str | None = None
    is_income: bool = False
    is_recurring: bool = False


@router.post("/csv/preview")
async def preview_csv_import(
    file: UploadFile = File(...),
    account_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(400, "Apenas arquivos CSV são aceitos")
    raw = (await file.read()).decode("utf-8-sig")
    if not raw.strip():
        raise HTTPException(400, "Arquivo vazio")

    try:
        pipeline = CsvImportPipeline(db, str(user.id), account_id)
        result = await pipeline.run_pipeline(raw)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/csv/confirm")
async def confirm_csv_import(
    file: UploadFile = File(...),
    account_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(400, "Apenas arquivos CSV são aceitos")
    raw = (await file.read()).decode("utf-8-sig")

    try:
        pipeline = CsvImportPipeline(db, str(user.id), account_id)
        result = await pipeline.confirm_import(raw)
        log = CsvImportLog(
            workspace_id=user.id,
            account_id=account_id,
            filename=file.filename,
            status="completed",
            total_rows=result["imported"] + result["skipped"] + result["failed"],
            imported_rows=result["imported"],
            skipped_rows=result["skipped"],
            error_rows=result["failed"],
        )
        db.add(log)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/merchants")
async def list_merchants(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MerchantMapping).where(MerchantMapping.workspace_id == user.id)
        .order_by(MerchantMapping.merchant_name)
    )
    merchants = result.scalars().all()
    return [
        {
            "id": str(m.id),
            "merchant_name": m.merchant_name,
            "category_id": str(m.category_id) if m.category_id else None,
            "payee_id": str(m.payee_id) if m.payee_id else None,
            "is_income": m.is_income,
            "is_recurring": m.is_recurring,
        }
        for m in merchants
    ]


@router.post("/merchants")
async def create_merchant(
    req: MerchantCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.services.csv_import import normalize_merchant
    merchant = MerchantMapping(
        workspace_id=user.id,
        merchant_name=req.merchant_name,
        normalized_name=normalize_merchant(req.merchant_name),
        category_id=req.category_id,
        payee_id=req.payee_id,
        is_income=req.is_income,
        is_recurring=req.is_recurring,
    )
    db.add(merchant)
    return {"id": str(merchant.id), "merchant_name": merchant.merchant_name}


@router.get("/history")
async def list_import_history(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CsvImportLog).where(CsvImportLog.workspace_id == user.id)
        .order_by(CsvImportLog.created_at.desc())
        .limit(20)
    )
    logs = result.scalars().all()
    return [
        {
            "id": str(l.id),
            "filename": l.filename,
            "status": l.status,
            "total_rows": l.total_rows,
            "imported_rows": l.imported_rows,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]
