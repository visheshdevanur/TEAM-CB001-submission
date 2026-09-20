import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "MysuruDrishti"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/beforeafterai")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    MODEL_NAME: str = os.getenv("MODEL_NAME", "yolo11n-seg.pt")
    SAM2_MODEL_PATH: str = os.getenv("SAM2_MODEL_PATH", "sam2_hiera_tiny.pt")
    VLM_MODEL: str = os.getenv("VLM_MODEL", "Qwen2.5-VL-7B-Instruct")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    # Keep the live visual-review model configurable in hosting environments.
    # Gemini 2.5 Flash accepts image inputs and structured JSON output.
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


    AI_MODE: str = os.getenv("AI_MODE", "demo") # demo, cpu, gpu
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_MB: int = int(os.getenv("MAX_UPLOAD_MB", "25"))

    LOCATION_MATCH_RADIUS_METERS: float = float(os.getenv("LOCATION_MATCH_RADIUS_METERS", "20"))
    RESOLUTION_THRESHOLD: float = float(os.getenv("RESOLUTION_THRESHOLD", "80"))
    PARTIAL_RESOLUTION_THRESHOLD: float = float(os.getenv("PARTIAL_RESOLUTION_THRESHOLD", "30"))
    RELOCATION_THRESHOLD: float = float(os.getenv("RELOCATION_THRESHOLD", "50"))

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
