from datetime import timedelta
import os
from fastapi import Depends, FastAPI, Request, Form, Response, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_404_NOT_FOUND
from contextlib import asynccontextmanager

from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))

from src.login.user import get_current_user
from src.logs import log_info, log_error
from src.routes import (
    hello_routes, upload_route, to_chunks_route,
    chunks_embedding_route, chat_route,
    llm_settings_route, live_rag_route,
    logers_router, monitor_router
)
from src.dbs import get_sqlite_engine, init_chunks_table, init_query_response_table
from src.db_vector import StartQdrant
from src.embedding import EmbeddingService
from src.schemes import LoginRequest
from src.login import (authenticate_user,
                       create_access_token,
                       init_default_user)
templates = Jinja2Templates(directory=f"{MAIN_DIR}/src/web")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        log_info("[STARTUP] Initializing application components...")

        # Initialize services
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
    description="AI Assistant for Soil Helath",
    version="1.0.0",
    lifespan=lifespan
)

# Routers with authentication required
app.include_router(hello_routes, prefix="/api", tags=["Hello World"], dependencies=[Depends(get_current_user)])
app.include_router(upload_route, prefix="/api", tags=["Document Upload"], dependencies=[Depends(get_current_user)])
app.include_router(to_chunks_route, prefix="/api", tags=["Document Processing"], dependencies=[Depends(get_current_user)])
app.include_router(chunks_embedding_route, prefix="/api", tags=["Embedding Generation"], dependencies=[Depends(get_current_user)])
app.include_router(chat_route, prefix="/api", tags=["Chatbot Interaction"], dependencies=[Depends(get_current_user)])
app.include_router(llm_settings_route, prefix="/api", tags=["LLM Configuration"], dependencies=[Depends(get_current_user)])
app.include_router(live_rag_route, prefix="/api", tags=["Live RAG"], dependencies=[Depends(get_current_user)])
app.include_router(logers_router, prefix="/api", tags=["Loges System"])
app.include_router(monitor_router, prefix="/api", tags=["Resouces Monitro"])


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("/html/login.html", {"request": request})

@app.get("/pages/{page_name}", response_class=HTMLResponse)
async def get_page(request: Request, page_name: str):
    allowed_pages = {
        "index": "index.html",
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

# Ensure default user exists
init_default_user()

@app.post("/api/login")
async def login(
    username: str = Form(...),
    password: str = Form(...)
):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user["username"]})
    
    response = JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "bearer"
        }
    )
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=1800,
        path="/"
    )
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )