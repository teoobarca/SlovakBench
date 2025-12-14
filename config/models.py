"""Model configuration - simple dict with model_id -> LLM instance."""
from src.utils.llm import create_llm

# =============================================================================
# MODEL DEFINITIONS
# Dict: model_id (with provider/) -> LLM instance
# =============================================================================

MODELS = {
    # OpenAI
    "openai/gpt-4o": create_llm("openai/gpt-4o"),
    "openai/gpt-4.1": create_llm("openai/gpt-4.1"),
    "openai/o3": create_llm("openai/o3", {"reasoning": {"enabled": True}}),
    # "openai/o3-pro": create_llm("openai/o3", {"reasoning": {"enabled": True}}),
    "openai/o4-mini": create_llm("openai/o4-mini", {"reasoning": {"enabled": True}}),
    "openai/gpt-5-nano": create_llm("openai/gpt-5-nano", {"reasoning": {"enabled": True}}),
    "openai/gpt-5-mini": create_llm("openai/gpt-5-mini", {"reasoning": {"enabled": True}}),
    "openai/gpt-5-default": create_llm("openai/gpt-5", {"reasoning": {"enabled": True}}),
    "openai/gpt-5-minimal": create_llm("openai/gpt-5", {"reasoning": {"enabled": True, "effort": "minimal"}}),
    "openai/gpt-5-high": create_llm("openai/gpt-5", {"reasoning": {"enabled": True, "effort": "high"}}),


    "openai/gpt-5.1-low": create_llm("openai/gpt-5.1", {"reasoning": {"enabled": True, "effort": "low"}}),
    "openai/gpt-5.1-default": create_llm("openai/gpt-5.1", {"reasoning": {"enabled": True}}),
    "openai/gpt-5.1-high": create_llm("openai/gpt-5.1", {"reasoning": {"enabled": True, "effort": "high"}}),

    "openai/gpt-5.2-none": create_llm("openai/gpt-5.2", {"reasoning": {"effort": "none"}}),
    "openai/gpt-5.2-low": create_llm("openai/gpt-5.2", {"reasoning": {"enabled": True, "effort": "low"}}),
    "openai/gpt-5.2-default": create_llm("openai/gpt-5.2", {"reasoning": {"enabled": True}}),
    "openai/gpt-5.2-high": create_llm("openai/gpt-5.2", {"reasoning": {"enabled": True, "effort": "high"}}),
    "openai/gpt-5.2-xhigh": create_llm("openai/gpt-5.2", {"reasoning": {"enabled": True, "effort": "xhigh"}}),

    # "openai/gpt-5.2-pro": create_llm("openai/gpt-5.2-pro", {"reasoning": {"enabled": True, "effort": "high"}}),

    "openai/gpt-oss-20b": create_llm("openai/gpt-oss-20b", {"reasoning": {"enabled": True}}),
    "openai/gpt-oss-120b": create_llm("openai/gpt-oss-120b", {"reasoning": {"enabled": True}}),

    # Anthropic
    "anthropic/claude-3.5-sonnet": create_llm("anthropic/claude-3.5-sonnet", {"reasoning": {"enabled": True}}),
    "anthropic/claude-3.5-haiku": create_llm("anthropic/claude-3.5-haiku", {"reasoning": {"enabled": True}}),
    "anthropic/claude-sonnet-4-non-thinking": create_llm("anthropic/claude-sonnet-4", {"reasoning": {"enabled": False}}),
    "anthropic/claude-sonnet-4": create_llm("anthropic/claude-sonnet-4", {"reasoning": {"enabled": True}}),
    "anthropic/claude-opus-4": create_llm("anthropic/claude-opus-4", {"reasoning": {"enabled": True}}),
    "anthropic/claude-haiku-4.5": create_llm("anthropic/claude-haiku-4.5"),
    "anthropic/claude-sonnet-4.5": create_llm("anthropic/claude-sonnet-4.5", {"reasoning": {"enabled": True}}),
    "anthropic/claude-opus-4.5": create_llm("anthropic/claude-opus-4.5"),
    "anthropic/claude-opus-4.5-thinking-high": create_llm("anthropic/claude-opus-4.5", {"reasoning": {"enabled": True, "effort": "high"}}),

    # Google Gemini
    "google/gemini-2.5-flash": create_llm("google/gemini-2.5-flash", {"reasoning": {"enabled": False}}),
    "google/gemini-2.5-flash-reasoning": create_llm("google/gemini-2.5-flash", {"reasoning": {"enabled": True}}),
    "google/gemini-2.5-flash-lite-preview-09-2025": create_llm("google/gemini-2.5-flash-lite-preview-09-2025", {"reasoning": {"enabled": False}}),
    "google/gemini-2.5-flash-lite-preview-09-2025-reasoning": create_llm("google/gemini-2.5-flash-lite-preview-09-2025", {"reasoning": {"enabled": True}}),
    "google/gemini-2.5-pro": create_llm("google/gemini-2.5-pro", {"reasoning": {"enabled": True}}),
    "google/gemini-3-pro-preview": create_llm("google/gemini-3-pro-preview", {"reasoning": {"enabled": True}}),

    # xAI Grok
    "x-ai/grok-3-mini": create_llm("x-ai/grok-3-mini", {"reasoning": {"enabled": True}}),
    "x-ai/grok-4": create_llm("x-ai/grok-4", {"reasoning": {"enabled": True}}),
    "x-ai/grok-4.1-fast": create_llm("x-ai/grok-4.1-fast", {"reasoning": {"enabled": True}}),

    # Moonshot Kimi
    "moonshotai/kimi-k2-0905": create_llm("moonshotai/kimi-k2-0905"),
    "moonshotai/kimi-k2-thinking": create_llm("moonshotai/kimi-k2-thinking", {"reasoning": {"enabled": True}}),

    # Qwen
    "qwen/qwen3-32b": create_llm("qwen/qwen3-32b", {"reasoning": {"enabled": True}}),
    "qwen/qwen3-235b-a22b-thinking-2507": create_llm("qwen/qwen3-235b-a22b-thinking-2507", {"reasoning": {"enabled": True}}),

    # Z-AI (GLM)
    "z-ai/glm-4.5": create_llm("z-ai/glm-4.5", {"reasoning": {"enabled": True}}),
    "z-ai/glm-4.5v": create_llm("z-ai/glm-4.5v", {"reasoning": {"enabled": True}}),
    "z-ai/glm-4.6": create_llm("z-ai/glm-4.6", {"reasoning": {"enabled": True}}),
    "z-ai/glm-4.6v": create_llm("z-ai/glm-4.6v", {"reasoning": {"enabled": True}}),

    # MiniMax
    "minimax/minimax-m2": create_llm("minimax/minimax-m2", {"reasoning": {"enabled": True}}),

    # Meta Llama
    # "meta-llama/llama-3.3-70b-instruct": create_llm("meta-llama/llama-3.3-70b-instruct", {"reasoning": {"enabled": True}}),
    "meta-llama/llama-4-scout": create_llm("meta-llama/llama-4-scout", {"reasoning": {"enabled": True}}),
    "meta-llama/llama-4-maverick": create_llm("meta-llama/llama-4-maverick", {"reasoning": {"enabled": True}}),

    # Mistral
    "mistralai/mistral-large-2512": create_llm("mistralai/mistral-large-2512", {"reasoning": {"enabled": True}}),
    "mistralai/devstral-medium": create_llm("mistralai/devstral-medium", {"reasoning": {"enabled": True}}),
    "mistralai/mistral-medium-3.1": create_llm("mistralai/mistral-medium-3.1", {"reasoning": {"enabled": True}}),

    # Cohere
    "cohere/command-a": create_llm("cohere/command-a", {"reasoning": {"enabled": True}}),

    # qwen
    "qwen/qwen3-max": create_llm("qwen/qwen3-max", {"reasoning": {"enabled": True}}),
    "qwen/qwen3-235b-a22b-thinking-2507": create_llm("qwen/qwen3-235b-a22b-thinking-2507", {"reasoning": {"enabled": True}}),
    "qwen/qwen3-next-80b-a3b-thinking": create_llm("qwen/qwen3-next-80b-a3b-thinking", {"reasoning": {"enabled": True}}),
    "qwen/qwen3-vl-235b-a22b-thinking": create_llm("qwen/qwen3-vl-235b-a22b-thinking", {"reasoning": {"enabled": True}}),

    # Deepseek
    "deepseek/deepseek-chat-v3.1": create_llm("deepseek/deepseek-chat-v3.1", {"reasoning": {"enabled": False}}),
    "deepseek/deepseek-chat-v3.1-thinking": create_llm("deepseek/deepseek-chat-v3.1", {"reasoning": {"enabled": True}}),
    "deepseek/deepseek-v3.2": create_llm("deepseek/deepseek-v3.2", {"reasoning": {"enabled": False}}),
    "deepseek/deepseek-v3.2-thinking-high": create_llm("deepseek/deepseek-v3.2", {"reasoning": {"enabled": True, "effort": "high"}}),
}



#legacy models

# MODELS = [
#     #openai
#     "openai/gpt-3.5-turbo",
#     "openai/gpt-4-turbo",
#     "openai/gpt-4o",
#     "openai/gpt-4o-mini",
#     "openai/gpt-4.1-nano",
#     "openai/gpt-4.1-mini",
#     "openai/gpt-4.1",
#     "openai/o4-mini-high",
#     "openai/o3",
#     "openai/gpt-5-nano",
#     "openai/gpt-5-mini",
#     "openai/gpt-5",
#     "openai/gpt-5.1",
#     "openai/gpt-5.1-chat",
#     "openai/gpt-5.2",
#     "openai/gpt-5.2-chat",


#     #anthropic
#     "anthropic/claude-3-haiku",
#     # "anthropic/claude-3-sonnet",
#     # "anthropic/claude-3-opus",
#     "anthropic/claude-3.5-sonnet",
#     "anthropic/claude-3.5-haiku",
#     # "anthropic/claude-3.5-opus",
#     # "anthropic/claude-3.5-haiku-20241022",
#     "anthropic/claude-3.7-sonnet:thinking",
#     "anthropic/claude-sonnet-4",
#     # "anthropic/claude-opus-4",
#     # "anthropic/claude-opus-4.1",
#     "anthropic/claude-haiku-4.5",
#     "anthropic/claude-sonnet-4.5",
#     "anthropic/claude-opus-4.5",


#     #google
#     "google/gemini-2.0-flash-001",
#     # "google/gemini-2.0-flash-exp:free",
#     "google/gemini-2.5-flash",
#     "google/gemini-2.5-flash-preview-09-2025",
#     "google/gemini-2.5-flash-lite",
#     "google/gemini-2.5-flash-lite-preview-09-2025",
#     "google/gemini-2.5-pro",
#     "google/gemini-3-pro-preview",

#     #mistral
#     "mistralai/devstral-2512",
#     "mistralai/ministral-14b-2512",
#     "mistralai/mistral-large-2512",
#     "mistralai/mistral-saba",
#     "mistralai/mistral-medium-3",
#     "mistralai/mistral-medium-3.1",
#     "mistral/ministral-8b",
#     "mistralai/mistral-small-3.2-24b-instruct",
#     "mistralai/devstral-small",
#     "mistralai/devstral-medium",
#     "mistralai/codestral-2508",
    

#     #moonshot
#     "moonshotai/kimi-k2-thinking",
#     "moonshotai/kimi-k2-0905",
#     "moonshotai/kimi-k2",

#     #minimax
#     # "minimax/minimax-01",
#     "minimax/minimax-m1",
#     "minimax/minimax-m2",
    

#     #qwen
#     "qwen/qwen3-vl-8b-thinking",
#     "qwen/qwen3-vl-8b-instruct",
#     "qwen/qwen3-vl-30b-a3b-thinking",
#     "qwen/qwen3-vl-30b-a3b-instruct",
#     "qwen/qwen3-vl-235b-a22b-thinking",
#     "qwen/qwen3-vl-235b-a22b-instruct",
#     "qwen/qwen3-max",
#     "qwen/qwen3-coder-plus",
#     "qwen/qwen3-coder-flash",
#     "qwen/qwen3-next-80b-a3b-thinking",
#     "qwen/qwen3-next-80b-a3b-instruct",
#     "qwen/qwen-plus-2025-07-28:thinking",
#     "qwen/qwen3-30b-a3b-thinking-2507",
#     "qwen/qwen3-coder-30b-a3b-instruct",
#     "qwen/qwen3-30b-a3b-instruct-2507",
#     "qwen/qwen3-235b-a22b-thinking-2507",
#     "qwen/qwen3-coder",
#     "qwen/qwen3-235b-a22b-2507",
#     "qwen/qwen3-30b-a3b",
#     "qwen/qwen3-8b",
#     "qwen/qwen3-32b",

#     #zai
#     "z-ai/glm-4-32b",
#     "z-ai/glm-4.5-air",
#     "z-ai/glm-4.5",
#     "z-ai/glm-4.5v",
#     "z-ai/glm-4.6",
#     "z-ai/glm-4.6v",

#     #meta
#     "meta-llama/llama-3-8b-instruct",
#     "meta-llama/llama-3-70b-instruct",
#     "meta-llama/llama-3.1-70b-instruct",
#     "meta-llama/llama-3.1-405b-instruct",
#     "meta-llama/llama-3.1-8b-instruct",
#     "meta-llama/llama-3.2-1b-instruct",
#     "meta-llama/llama-3.2-3b-instruct",
#     "meta-llama/llama-3.3-70b-instruct",
#     "meta-llama/llama-4-scout",
#     "meta-llama/llama-4-maverick",
#     "meta-llama/llama-guard-4-12b",


#     #xai
#     "x-ai/grok-3",
#     "x-ai/grok-3-mini",
#     "x-ai/grok-4",
#     "x-ai/grok-code-fast-1",
#     "x-ai/grok-4-fast",
#     "x-ai/grok-4.1-fast",

#     #cohere
#     "cohere/command-r-plus-08-2024",
#     "cohere/command-r-08-2024",
#     "cohere/command-r7b-12-2024",
#     "cohere/command-a",

#     #a21
#     "ai21/jamba-large-1.7",
#     "ai21/jamba-mini-1.7",

#     #microsoft
#     "microsoft/phi-3-mini-128k-instruct",
#     "microsoft/phi-3.5-mini-128k-instruct",
#     "microsoft/phi-4",
#     "microsoft/phi-4-multimodal-instruct",
#     "microsoft/phi-4-reasoning-plus",
# ]
