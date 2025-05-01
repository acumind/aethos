from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import ValidationInfo, field_validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "Aethos Platform"
    API_V1_STR: str = "/api/v1"

    # SECURITY
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # AZURE SERVICES
    AZURE_TENANT_ID: str
    AZURE_CLIENT_ID: str
    AZURE_CLIENT_SECRET: str
    AZURE_SUBSCRIPTION_ID: str
    AZURE_RESOURCE_GROUP: str

    GLOBAL_LLM_SERVICE: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME: str
    AZURE_OPENAI_CHAT_DEPLOYMENT_NAME: str
    AZURE_OPENAI_API_VERSION: str
    PROJECT_CONNECTION_STRING: str
    GITHUB_TOKEN: str
    AZURE_SEARCH_SERVICE_ENDPOINT: str
    AZURE_SUBSCRIPTION_ID: str
    AZURE_AI_PROJECT_NAME: str
    AZURE_OPENAI_RESOURCE_GROUP: str
    AZURE_OPENAI_SERVICE: str
    AZURE_AI_AGENT_SERVICE_ENDPOINT: str

    # AZURE AI SERVICES
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_AI_AGENT_SERVICE_ENDPOINT: str

    # AZURE STORAGE
    AZURE_STORAGE_CONNECTION_STRING: str
    AZURE_BLOB_CONTAINER_NAME: str = "agent-files"

    # AZURE SQL
    AZURE_SQL_SERVER: str
    AZURE_SQL_DATABASE: str
    AZURE_SQL_USERNAME: str
    AZURE_SQL_PASSWORD: str

    # DATABASE
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode='before')
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> str:
        if isinstance(v, str):
            return v

        server = info.data.get("AZURE_SQL_SERVER")
        db = info.data.get("AZURE_SQL_DATABASE")
        user = info.data.get("AZURE_SQL_USERNAME")
        password = info.data.get("AZURE_SQL_PASSWORD")

        if not all([server, db, user, password]):
            raise ValueError("Database connection information incomplete")

        return f"mssql+pyodbc://{user}:{password}@{server}/{db}?driver=ODBC+Driver+17+for+SQL+Server"

    @field_validator("CORS_ORIGINS", mode='before')
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
