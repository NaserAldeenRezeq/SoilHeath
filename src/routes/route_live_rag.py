import os
import sys
import sqlite3 as sql3
from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from src.logs.logger import log_warning

# Setup import path and modules
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
    from dbs import fetch_all_rows
    from embedding import EmbeddingService
    from db_vector import StartQdrant
    from schemes import LiveRAG

except ImportError as e:
    log_error(f"[IMPORT ERROR] {__file__}: {e}")
    raise

live_rag_route = APIRouter()


def get_embedd(request: Request) -> EmbeddingService:
    emb = getattr(request.app.state, "embedded", None)
    if not emb:
        log_error("Embedding model missing in app state.")
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR, "Embedding service unavailable.")
    return emb


def get_qdrant_vector_db(request: Request) -> StartQdrant:
    qdrant = getattr(request.app.state, "qdrant", None)
    if not qdrant:
        log_warning("Qdrant not found in app state.")
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR, "Vector DB unavailable.")
    return qdrant


@live_rag_route.post("/live_rag", response_class=JSONResponse)
async def live_rag(
    request_data: LiveRAG,
    embedd: EmbeddingService = Depends(get_embedd),
    qdrant: StartQdrant = Depends(get_qdrant_vector_db),
):
    """Endpoint for Live RAG search using vector embeddings."""
    query = request_data.query.strip()
    top_k = request_data.top_k
    score_threshold = request_data.score_threshold

    if not query:
        log_error("Received empty query.")
        raise HTTPException(HTTP_400_BAD_REQUEST, "Query cannot be empty.")

    if top_k <= 0:
        log_error(f"Invalid top_k: {top_k}")
        raise HTTPException(HTTP_400_BAD_REQUEST, "top_k must be greater than zero.")

    try:
        # Step 1: Embed the query
        query_embedding = embedd.embed(text=query)
        log_debug(f"Query embedded successfully.")

        # Step 2: Retrieve similar documents
        retrieved_docs = qdrant.search_embeddings(
            collection_name="embeddings",
            query_embedding=query_embedding,
            top_k=top_k,
            score_threshold=score_threshold,
        )

        if not retrieved_docs:
            log_info(f"No match found for query: '{query}'")
            return JSONResponse(
                status_code=HTTP_404_NOT_FOUND,
                content={"message": "No results found for the query."}
            )

        return JSONResponse(
            status_code=HTTP_200_OK,
            content={"Retriever Results": retrieved_docs}
        )

    except Exception as err:
        log_error(f"Unexpected error: {err}")
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR, "An internal error occurred.")
