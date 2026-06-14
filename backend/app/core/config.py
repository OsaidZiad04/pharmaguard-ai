import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    app_name: str
    environment: str
    allowed_origins: list[str]


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name="PharmaGuard AI",
        environment=os.getenv("PHARMAGUARD_ENV", "development"),
        allowed_origins=_csv(
            os.getenv(
                "PHARMAGUARD_ALLOWED_ORIGINS",
                "http://localhost:3000,http://127.0.0.1:3000",
            )
        ),
    )
