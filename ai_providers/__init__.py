"""AI Providers package."""
from ai_providers.base import BaseAIProvider
from ai_providers.offline_provider import OfflineAIProvider
from ai_providers.gemini_provider import GeminiAIProvider

def get_ai_provider(provider_name: str = "offline", api_key: str = "") -> BaseAIProvider:
    if provider_name.lower() == "gemini":
        return GeminiAIProvider(api_key=api_key)
    return OfflineAIProvider()

__all__ = [
    "BaseAIProvider",
    "OfflineAIProvider",
    "GeminiAIProvider",
    "get_ai_provider",
]
