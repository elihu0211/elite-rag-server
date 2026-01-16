from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.graphql.router import graphql_router
from src.config import settings
from src.infrastructure.persistence.database import Base, engine, async_session_factory
from src.infrastructure.persistence.seeding import DataSeederManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create data directory and tables
    Path("data").mkdir(exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # ABP 對比：ABP 在 OnApplicationInitializationAsync 中執行種子資料
    # 執行資料種子
    logger.info("Running data seeders...")
    async with async_session_factory() as session:
        try:
            seeder = DataSeederManager()
            await seeder.seed_async(session)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Data seeding failed: {e}")
            raise

    yield
    # Shutdown
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(graphql_router, prefix="/graphql")

    return app


app = create_app()
