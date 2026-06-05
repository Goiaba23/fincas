"""
Seed development database with minimal structure (user + categories only).
Usage: cd backend && python seed_dev.py
"""

import asyncio
import os
import uuid
import sys

sys.path.insert(0, ".")

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./fincas_dev.db")

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base
from app.models import *  # noqa: F401, F403
from app.core.security import hash_password as get_password_hash

from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.models.category import CategoryGroup, Category
from app.models.currency import Currency

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        user = User(
            id=uuid.uuid4(),
            email="admin@fincas.app",
            display_name="Admin",
            password_hash=get_password_hash("123456"),
            is_active=True,
        )
        session.add(user)
        await session.flush()

        ws = Workspace(id=uuid.uuid4(), name="Meu Espaço", created_by=user.id)
        session.add(ws)
        await session.flush()

        member = WorkspaceMember(workspace_id=ws.id, user_id=user.id, role="owner")
        session.add(member)
        await session.flush()

        groups_data = [
            ("Moradia", False, "#0D47A1"),
            ("Alimentação", False, "#FF5A36"),
            ("Transporte", False, "#22C55E"),
            ("Lazer", False, "#8B5CF6"),
            ("Saúde", False, "#EC4899"),
            ("Educação", False, "#F59E0B"),
            ("Assinaturas", False, "#06B6D4"),
            ("Compras", False, "#64748B"),
            ("Receitas", True, "#22C55E"),
        ]
        groups = {}
        for name, is_income, color in groups_data:
            g = CategoryGroup(id=uuid.uuid4(), workspace_id=ws.id, name=name, is_income=is_income, color=color)
            session.add(g)
            await session.flush()
            groups[name] = g

        cats_data = [
            ("Aluguel", "Moradia"), ("Condomínio", "Moradia"), ("Água/Luz/Gás", "Moradia"),
            ("Supermercado", "Alimentação"), ("Restaurante", "Alimentação"), ("Delivery", "Alimentação"),
            ("Gasolina", "Transporte"), ("Uber", "Transporte"),
            ("Cinema", "Lazer"), ("Streaming", "Lazer"),
            ("Plano de Saúde", "Saúde"), ("Farmácia", "Saúde"),
            ("Curso", "Educação"),
            ("Internet", "Assinaturas"), ("Celular", "Assinaturas"),
            ("Roupas", "Compras"),
            ("Salário", "Receitas"), ("Freelance", "Receitas"),
        ]
        for name, group_name in cats_data:
            c = Category(id=uuid.uuid4(), group_id=groups[group_name].id, name=name, color=groups[group_name].color)
            session.add(c)

        for code, name, symbol, decimals in [
            ("BRL", "Brazilian Real", "R$", 2),
            ("USD", "US Dollar", "$", 2),
            ("EUR", "Euro", "€", 2),
        ]:
            session.add(Currency(code=code, name=name, symbol=symbol, decimal_places=decimals))

        await session.commit()
        print("OK - Estrutura criada!")
        print(f"   Email: admin@fincas.app")
        print(f"   Senha: 123456")
        print("   (sem transações — adicione manualmente pelo sistema)")


if __name__ == "__main__":
    asyncio.run(seed())
