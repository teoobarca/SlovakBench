"""Simple LangChain wrapper for LLM calls with cost tracking via OpenRouter."""
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


def create_llm(model_id: str, extra_body: dict | None = None, temperature: float = 1.0) -> ChatOpenAI:
    """Create LangChain ChatOpenAI configured for OpenRouter.
    
    Args:
        model_id: OpenRouter model identifier (e.g. "openai/gpt-5.2")
        extra_body: Extra options like {"reasoning": {"enabled": True}}
        temperature: Sampling temperature
    """
    body = {"usage": {"include": True}}
    
    if extra_body:
        # Auto-add exclude: True to reasoning if present
        if "reasoning" in extra_body:
            extra_body["reasoning"]["exclude"] = True
        body.update(extra_body)
    
    return ChatOpenAI(
        model=model_id,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=temperature,
        extra_body=body,
    )


def get_cost(response) -> float:
    """Extract cost in USD from LangChain response."""
    return response.response_metadata.get("token_usage", {}).get("cost", 0.0)


def print_cost(response, label: str = ""):
    """Print cost from LangChain response."""
    cost = get_cost(response)
    prefix = f"{label}: " if label else ""
    print(f"💰 {prefix}${cost:.6f}")
