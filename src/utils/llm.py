"""Simple LangChain wrapper for LLM calls with cost tracking via OpenRouter."""
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


def create_llm(model_name: str, temperature: float = 1.0) -> ChatOpenAI:
    """Create LangChain ChatOpenAI configured for OpenRouter with cost tracking."""
    return ChatOpenAI(
        model=model_name,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=temperature,
        extra_body={
            "usage": {"include": True},
            "reasoning": {"exclude": True},
        },
    )


def get_cost(response) -> float:
    """Extract cost in USD from LangChain response."""
    return response.response_metadata.get("token_usage", {}).get("cost", 0.0)


def print_cost(response, label: str = ""):
    """Print cost from LangChain response."""
    cost = get_cost(response)
    prefix = f"{label}: " if label else ""
    print(f"💰 {prefix}${cost:.6f}")
