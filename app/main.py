from fastapi import FastAPI

from app.api.collection_routes import router as collection_router
from app.api.query_routes import router as query_router
from app.config import get_settings
from app.middleware.collection_namespace import CollectionNamespaceMiddleware

settings = get_settings()
app = FastAPI(title=settings.app_name)
app.add_middleware(CollectionNamespaceMiddleware)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "env": settings.app_env}


app.include_router(query_router)
app.include_router(collection_router)
