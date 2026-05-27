"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "EnergyOptimizationPlatform"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"

    # Database
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "energy_optimization"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    DATABASE_URL: str = "sqlite:///./energy_optimization.db"

    # AWS
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    # AWS IoT Core
    AWS_IOT_ENDPOINT: Optional[str] = None
    AWS_IOT_CERT_PATH: str = "./certs/certificate.pem.crt"
    AWS_IOT_KEY_PATH: str = "./certs/private.pem.key"
    AWS_IOT_ROOT_CA_PATH: str = "./certs/AmazonRootCA1.pem"

    # AWS SQS
    SQS_QUEUE_URL: Optional[str] = None
    SQS_DEAD_LETTER_QUEUE_URL: Optional[str] = None

    # MQTT
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None
    MQTT_TOPIC_PREFIX: str = "factory/sensors"

    # SCADA
    SCADA_HOST: str = "192.168.1.100"
    SCADA_PORT: int = 4840
    SCADA_USERNAME: str = "operator"
    SCADA_PASSWORD: str = "scada-password"
    SCADA_WRITEBACK_ENABLED: bool = False

    # AI Engine
    AI_ANOMALY_THRESHOLD: float = 0.85
    AI_MODEL_PATH: str = "./models"
    AI_RETRAIN_INTERVAL_HOURS: int = 24

    # Dashboard
    DASHBOARD_PORT: int = 8501
    DASHBOARD_REFRESH_INTERVAL: int = 5

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
