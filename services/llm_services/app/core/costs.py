# services/llm_services/app/core/costs.py

# services/llm_services/app/core/costs.py

# OpenAI pricing — update anytime
MODEL_PRICES = {
    "gpt-4o": {
        "input_per_1k": 0.005,
        "output_per_1k": 0.015,
    },
    "gpt-4o-mini": {
        "input_per_1k": 0.0006,
        "output_per_1k": 0.0024,
    },
    # add more models as needed
}

def estimate_cost(model_name: str, total_tokens: int) -> float:
    """
    Estimate approximate cost in USD based on token usage.
    OpenAI counts input & output separately but
    total_tokens is fine for early metrics.
    """

    if model_name not in MODEL_PRICES:
        return 0.0

    # Cost per 1K tokens (approx)
    price_per_1k = MODEL_PRICES[model_name]["output_per_1k"]

    return (total_tokens / 1000) * price_per_1k



# MODEL_COSTS = {
#     # per 1K tokens
#     "gpt-4-turbo": {"input": 0.01, "output": 0.03},
#     "gpt-4o": {"input": 0.005, "output": 0.015},
#     "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
#     # fallback defaults
# }
