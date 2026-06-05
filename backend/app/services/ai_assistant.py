from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai import AIConversation, AIMessage
from app.models.user import User
from app.providers.llm import LLMProvider
from app.providers.llm.factory import get_llm_provider, get_embedding_provider
from app.services.finance_tools import FINANCE_TOOLS, execute_tool
from app.services.rag import search_similar_transactions

SYSTEM_PROMPT = """Você é o Zé, assistente financeiro pessoal do Fincas. 

REGRAS:
- Responda SEMPRE em português brasileiro, de forma direta e amigável
- Use linguagem simples e evite jargão financeiro complexo
- Quando apropriado, sugira ações como criar metas, reduzir gastos, etc.
- Se o usuário pedir dados financeiros, use as ferramentas disponíveis
- Se não souber a resposta, seja honesto e sugira alternativas
- Seja proativo em identificar oportunidades de economia
- Nunca invente números — use apenas dados reais das ferramentas
- Mantenha respostas curtas e objetivas (máximo 4-5 frases salvo se o usuário pedir detalhes)

Se for a primeira interação, welcome o usuário e pergunte como pode ajudar."""


async def process_chat(
    db: AsyncSession,
    user: User,
    message: str,
    conversation_id: UUID | None = None,
    provider_name: str | None = None,
) -> dict:
    provider = get_llm_provider(provider_name)

    # Get or create conversation
    if conversation_id:
        result = await db.execute(
            select(AIConversation).where(
                AIConversation.id == conversation_id,
                AIConversation.user_id == user.id,
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            return {"error": "Conversation not found"}
    else:
        conversation = AIConversation(
            user_id=user.id,
            title=message[:100],
        )
        db.add(conversation)
        await db.flush()

    # Save user message
    user_msg = AIMessage(
        conversation_id=conversation.id,
        role="user",
        content=message,
    )
    db.add(user_msg)

    # Build message history (last 20 messages)
    history_result = await db.execute(
        select(AIMessage)
        .where(AIMessage.conversation_id == conversation.id)
        .order_by(AIMessage.created_at.desc())
        .limit(20)
    )
    history = list(reversed(history_result.scalars().all()))

    # Build context from RAG
    similar = await search_similar_transactions(db, message)
    rag_context = ""
    if similar:
        rag_context = "\nTransações recentes relevantes:\n" + "\n".join(
            f"- {t['description']}: R$ {t['amount']:.2f} ({t['category']})"
            for t in similar[:3]
        )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + rag_context},
    ]
    for msg in history:
        role = msg.role
        content = msg.content
        if role == "tool":
            messages.append({"role": "tool", "content": content, "tool_call_id": msg.tool_call_id or ""})
        else:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": message})

    # LLM call with tools
    response = await provider.chat(messages, tools=FINANCE_TOOLS)

    # Handle tool calls
    if response.get("tool_calls"):
        messages.append({
            "role": "assistant",
            "content": response.get("content"),
            "tool_calls": response["tool_calls"],
        })
        for tc in response["tool_calls"]:
            try:
                import json
                args = json.loads(tc["function"]["arguments"])
                tool_result = await execute_tool(tc["function"]["name"], args, db)
            except Exception as e:
                tool_result = f"Erro ao executar {tc['function']['name']}: {e}"

            messages.append({
                "role": "tool",
                "content": tool_result,
                "tool_call_id": tc["id"],
            })

            # Save tool call
            db.add(AIMessage(
                conversation_id=conversation.id,
                role="assistant",
                content="",
                tool_calls=[tc],
            ))
            db.add(AIMessage(
                conversation_id=conversation.id,
                role="tool",
                content=tool_result,
                tool_call_id=tc["id"],
            ))

        # Second LLM call with tool results
        response = await provider.chat(messages)

    content = response.get("content") or ""

    # Save assistant response
    assistant_msg = AIMessage(
        conversation_id=conversation.id,
        role="assistant",
        content=content,
    )
    db.add(assistant_msg)

    if not conversation.title or conversation.title == message[:100]:
        conversation.title = message[:100]

    return {
        "conversation_id": str(conversation.id),
        "message": content,
    }
