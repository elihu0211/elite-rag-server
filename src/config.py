"""
應用程式配置

ABP 對比：
- ABP: appsettings.json + IConfiguration + IOptions<T>
- ABP 使用 services.Configure<TOptions>() 註冊配置
- Python: pydantic-settings 從 .env 讀取，功能類似但更簡潔
"""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    應用程式設定

    ABP 對比：
    - ABP: public class AppSettings 搭配 IOptions<AppSettings>
    - 敏感配置應從環境變數讀取，不應有預設值
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "Elite RAG Server"
    debug: bool = False

    # Database (PostgreSQL + pgvector)
    # PostgreSQL 命名慣例：小寫 + 底線
    database_url: str = Field(
        default="postgresql+asyncpg://localhost:5432/graph_server",
        description="資料庫連線字串，必須在 .env 中設定完整的認證資訊",
    )

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"]

    # JWT - 敏感配置必須從環境變數讀取
    jwt_secret_key: str = Field(
        default=...,  # 必填，無預設值
        description="JWT 簽名密鑰，必須在 .env 中設定",
    )
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24  # 24 hours

    # ========== 向量搜尋設定 ==========
    # ABP 對比：ABP 可能會建立獨立的 VectorSearchOptions 類別
    # 並透過 services.Configure<VectorSearchOptions>() 註冊

    # 嵌入模型設定
    embedding_provider: str = "local"  # "local" (sentence-transformers) 或 "openai"
    embedding_model: str = "all-MiniLM-L6-v2"  # 384 維，本地運行
    embedding_dimension: int = 384
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"

    # 文本分割設定
    chunk_size: int = 500
    chunk_overlap: int = 50

    # 搜尋設定
    default_search_limit: int = 10
    similarity_threshold: float = 0.7

    # ========== 種子資料設定 ==========
    # ABP 對比：ABP 在 appsettings.json 中設定 IdentityDataSeedOptions
    # 這些設定用於初始化系統管理員帳號

    seed_admin_email: str = Field(
        default="admin@example.com",
        description="預設管理員 Email",
    )
    seed_admin_password: str = Field(
        default="Admin@123456",
        description="預設管理員密碼（建議在生產環境修改）",
    )
    seed_admin_name: str = Field(
        default="System Administrator",
        description="預設管理員名稱",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
