from datetime import timedelta
import os
from fastapi import FastAPI, Request, Form, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_404_NOT_FOUND
from contextlib import asynccontextmanager

MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))

from logs import log_info, log_error
from src.routes import (
    hello_routes, upload_route, to_chunks_route,
    chunks_embedding_route, chat_route,
    llm_settings_route, live_rag_route,
    logers_router, monitor_router
)
from src.dbs import get_sqlite_engine, init_chunks_table, init_query_response_table
from src.db_vector import StartQdrant
from src.embedding import EmbeddingService

templates = Jinja2Templates(directory=f"{MAIN_DIR}/src/web")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        log_info("[STARTUP] Initializing application components...")

        app.state.qdrant = StartQdrant()
        app.state.embedded = EmbeddingService()
        app.state.qdrant.create_collection("embeddings")

        app.state.conn = get_sqlite_engine()
        init_chunks_table(conn=app.state.conn)
        init_query_response_table(conn=app.state.conn)

        app.state.llm = None
        log_info("[STARTUP] LLM initialized.")
        yield
    except Exception as e:
        log_error(f"[STARTUP ERROR] Failed to initialize: {e}")
        raise
    finally:
        log_info("[SHUTDOWN] Cleaning up application resources...")
        if hasattr(app.state, 'conn'):
            app.state.conn.close()
            log_info("[SHUTDOWN] SQLite connection closed.")
        if hasattr(app.state, 'llm'):
            del app.state.llm
            log_info("[SHUTDOWN] LLM resources released.")


app = FastAPI(
    title="Soil Heath",
    description="AI Assistant for Soil Health",
    version="1.0.0",
    lifespan=lifespan
)

# Routers without authentication
app.include_router(hello_routes, prefix="/api", tags=["Hello World"])
app.include_router(upload_route, prefix="/api", tags=["Document Upload"])
app.include_router(to_chunks_route, prefix="/api", tags=["Document Processing"])
app.include_router(chunks_embedding_route, prefix="/api", tags=["Embedding Generation"])
app.include_router(chat_route, prefix="/api", tags=["Chatbot Interaction"])
app.include_router(llm_settings_route, prefix="/api", tags=["LLM Configuration"])
app.include_router(live_rag_route, prefix="/api", tags=["Live RAG"])
app.include_router(logers_router, prefix="/api", tags=["Loges System"])
app.include_router(monitor_router, prefix="/api", tags=["Resouces Monitro"])


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/pages/{page_name}", response_class=HTMLResponse)
async def get_page(request: Request, page_name: str):
    allowed_pages = {
        "hello": "hello.html",
        "upload": "upload.html",
        "to_chunks": "to_chunks.html",
        "chunks_to_embedding": "chunks_to_embedding.html",
        "llms_config": "llms_config.html",
        "monitoring": "monitoring.html",
        "chat": "chat.html",
        "crawl": "crawl.html",
        "rag": "rag.html",
    }
    template_name = allowed_pages.get(page_name)
    if not template_name:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    if page_name == "index":
        return templates.TemplateResponse(f"/{template_name}", {"request": request})

    return templates.TemplateResponse(f"html/{template_name}", {"request": request})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )
