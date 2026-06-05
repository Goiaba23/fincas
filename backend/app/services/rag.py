from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai import KnowledgeDocument
from app.models.transaction import TransactionJournal
from app.models.category import Category
from app.providers.llm.factory import get_embedding_provider


async def embed_and_store_document(
    db: AsyncSession,
    workspace_id: str,
    title: str,
    content: str,
    content_type: str = "text",
    metadata: dict | None = None,
    user_id: str | None = None,
) -> KnowledgeDocument:
    provider = get_embedding_provider()
    embedding = await provider.embed([content])

    doc = KnowledgeDocument(
        workspace_id=workspace_id,
        title=title,
        content=content,
        content_type=content_type,
        embedding=embedding[0],
        metadata_=metadata or {},
        created_by=user_id,
    )
    db.add(doc)
    return doc


async def search_similar_transactions(
    db: AsyncSession,
    query: str,
    limit: int = 5,
) -> list[dict]:
    tsquery = " & ".join(query.split())
    result = await db.execute(
        select(
            TransactionJournal.id,
            TransactionJournal.description,
            TransactionJournal.amount,
            TransactionJournal.date,
            TransactionJournal.transaction_type,
            Category.name.label("category_name"),
        )
        .join(Category, TransactionJournal.category_id == Category.id, isouter=True)
        .where(
            text("to_tsvector('portuguese', coalesce(description, '')) @@ to_tsquery('portuguese', :q)")
            .bindparams(q=tsquery)
        )
        .order_by(TransactionJournal.created_at.desc())
        .limit(limit)
    )
    rows = result.all()
    return [
        {
            "id": str(r.id),
            "description": r.description,
            "amount": float(r.amount),
            "date": r.date.isoformat() if r.date else None,
            "type": r.transaction_type,
            "category": r.category_name,
        }
        for r in rows
    ]


async def search_knowledge_base(
    db: AsyncSession,
    workspace_id: str,
    query: str,
    limit: int = 3,
) -> list[dict]:
    provider = get_embedding_provider()
    embedding = await provider.embed([query])

    result = await db.execute(
        select(
            KnowledgeDocument.id,
            KnowledgeDocument.title,
            KnowledgeDocument.content,
            KnowledgeDocument.content_type,
            KnowledgeDocument.metadata_,
        )
        .where(KnowledgeDocument.workspace_id == workspace_id)
        .order_by(KnowledgeDocument.embedding.l2_distance(embedding[0]))
        .limit(limit)
    )
    rows = result.all()
    return [
        {
            "id": str(r.id),
            "title": r.title,
            "content": r.content[:500] if r.content else "",
            "content_type": r.content_type,
            "metadata": r.metadata_,
        }
        for r in rows
    ]
