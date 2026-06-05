from app.core.config import get_settings
from app.providers.llm import LLMProvider
from app.providers.llm.openai_provider import OpenAIProvider
from app.providers.llm.anthropic_provider import AnthropicProvider
from app.providers.llm.ollama_provider import OllamaProvider


_providers: dict[str, LLMProvider] = {}


def get_llm_provider(name: str | None = None) -> LLMProvider:
    if not name:
        name = "default"

    if name in _providers:
        return _providers[name]

    settings = get_settings()
    provider_type = settings.ai_default_provider

    if provider_type == "openai":
        provider = OpenAIProvider(
            api_key=settings.openai_api_key or "",
            model=settings.ai_default_model or "gpt-4o",
        )
    elif provider_type == "anthropic":
        provider = AnthropicProvider(
            api_key=settings.anthropic_api_key or "",
            model=settings.ai_default_model or "claude-sonnet-4-20250514",
        )
    else:
        provider = OllamaProvider(
            model=settings.ai_default_model or "qwen3.5:latest",
        )

    _providers[name] = provider
    return provider


def get_embedding_provider() -> LLMProvider:
    settings = get_settings()
    if settings.openai_api_key:
        return OpenAIProvider(api_key=settings.openai_api_key, model="gpt-4o-mini")
    return OllamaProvider(model="qwen2.5:0.5b", embedding_model="nomic-embed-text")
