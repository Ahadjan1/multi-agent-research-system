import os

import groq
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.rate_limiters import InMemoryRateLimiter

load_dotenv()

# Ek model ka quota/limit khatam ho to agla try hota hai
MODELS = [
    m.strip()
    for m in os.getenv(
        "GROQ_MODELS",
        "openai/gpt-oss-120b,openai/gpt-oss-20b,qwen/qwen3.8-27b",
    ).split(",")
    if m.strip()
]

# 1 request har 4 second, taake tokens-per-minute limit na tute
_rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.25,
    check_every_n_seconds=0.1,
    max_bucket_size=1,
)

# In errors par agle model par jao
FALLBACK_CODES = {400, 413, 429, 500, 502, 503}


def get_llm(model: str, temperature: float = 0, max_tokens: int = 1500):
    return ChatGroq(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        rate_limiter=_rate_limiter,
        max_retries=2,
    )


def run_with_fallback(fn, max_tokens: int = 1500):
    """fn(llm) ko pehle model par chalao; fail ho to agle model par."""
    last_error = None
    for model in MODELS:
        try:
            return fn(get_llm(model, max_tokens=max_tokens))
        except groq.APIStatusError as e:
            if e.status_code in FALLBACK_CODES:
                print(f"[fallback] {model} failed with {e.status_code}, trying next model...")
                last_error = e
                continue
            raise
    raise RuntimeError(
        "All Groq models are rate-limited or unavailable right now. Please try again later."
    ) from last_error