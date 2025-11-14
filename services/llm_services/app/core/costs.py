# services/llm_services/app/core/costs.py
MODEL_COSTS = {
    # per 1K tokens
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
    # fallback defaults
}
