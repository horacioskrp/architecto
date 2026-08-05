from functools import lru_cache

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from architecto.core.config import settings


@lru_cache
def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.llm.model,
        api_key=settings.llm.api_key.get_secret_value(),
        temperature=settings.llm.temperature,
        max_tokens=settings.llm.max_tokens,
        timeout=settings.llm.timeout,
    )


@lru_cache
def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.llm.embedding_model,
        api_key=settings.llm.api_key.get_secret_value(),
    )
