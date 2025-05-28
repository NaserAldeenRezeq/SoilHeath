import os
import sys
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    sys.path.append(MAIN_DIR)

    from src.logs import log_error, log_info, log_debug, log_warning
    from src.dbs import add_query_response
    from src.prompt import FarmAssistantPromptBuilder
    from src.schemes import ChatRoute
    from src.llm import HuggingFaceLLM, GoogleLLM
    from src.db_vector import StartQdrant
    from src.embedding import EmbeddingService
    from src.helpers import split_soil_elements

except ImportError as e:
    msg = f"Import Error in {__file__}: {e}"
    raise ImportError(msg) from e

chat_route = APIRouter()

def get_llm(request: Request) -> Union[HuggingFaceLLM, GoogleLLM]:
    """Retrieve the LLM instance from the app state."""
    llm = getattr(request.app.state, "llm", None)
    if llm is None:
        log_warning("LLM instance not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "LLM service is not initialized. "
                "Please configure the LLM via the /llmsSettings endpoint."
            ),
        )
    return llm

def get_qdrant_vector_db(request: Request) -> StartQdrant:
    """Retrieve the Qdrant vector database connection from the app state."""
    qdrant = getattr(request.app.state, "qdrant", None)
    if qdrant is None:
        log_warning("Qdrant vector database connection not found.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Vector database service is not available.",
        )
    return qdrant

def get_db_conn(request: Request):
    """Retrieve the relational database connection from the app state."""
    conn = getattr(request.app.state, "conn", None)
    if conn is None:
        log_warning("Relational database connection not found.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Relational database service is not available.",
        )
    return conn

def get_embedding_model(request: Request) -> EmbeddingService:
    """Retrieve the embedding model instance from the app state."""
    embedding = getattr(request.app.state, "embedded", None)
    if embedding is None:
        log_warning("Embedding model instance not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Embedding model service is not available.",
        )
    return embedding

def format_retrieved_context(retrieved_docs: list[dict]) -> str:
    """Format retrieved docs into a single context string for the prompt."""
    parts = [
        f"Context {i+1} (Score: {doc['score']:.2f}): {doc['text']}"
        for i, doc in enumerate(retrieved_docs)
    ]
    return "\n\n".join(parts)

@chat_route.post("/chat", response_class=JSONResponse)
async def chat(
    user_id: str,
    body: ChatRoute,
    llm: Union[HuggingFaceLLM, GoogleLLM] = Depends(get_llm),
    conn = Depends(get_db_conn),
    qdrant: StartQdrant = Depends(get_qdrant_vector_db),
    embedding: EmbeddingService = Depends(get_embedding_model),
) -> JSONResponse:
    """
    1. Parses soil & weather from user query.
    2. Embeds each soil parameter.
    3. Retrieves similar docs from Qdrant.
    4. Builds prompt & queries LLM if context exists.
    5. Stores full interaction in relational DB.
    """
    query = body.query.strip()
    if not query:
        log_warning("Empty query received")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty",
        )

    log_info(f"Received chat query for user {user_id}")

    try:
        soil, weather = split_soil_elements(query)
        log_debug(f"Parsed input for user_id={user_id}: Soil={soil}, Weather={weather}")

        recommendations = []

        for parameter, value in soil.items():
            individual_query = f"{parameter}: {value}"
            log_debug(f"Embedding and searching for {parameter}...")

            # Step 1: Embed and search
            embedding_vector = embedding.embed(text=individual_query)
            retrieved = qdrant.search_embeddings(
                collection_name="embeddings",
                query_embedding=embedding_vector,
                top_k=5,
                score_threshold=0.3
            )

            if retrieved:
                # Build prompt from retrieved context
                context = format_retrieved_context(retrieved)
                prompt = FarmAssistantPromptBuilder().build_prompt(
                    context=context,
                    user_message=individual_query,
                    weather=weather,
                )
                try:
                    advice = llm.response(prompt=prompt).strip()
                    status = "Processed"
                    log_debug(f"Advice for {parameter}: {advice[:80]}...")
                except RuntimeError as e:
                    log_error(f"LLM error for {parameter}: {e}")
                    advice = "Error generating advice."
                    status = "Error"
            else:
                log_warning(f"No relevant docs found for {parameter}")
                advice = "No context found for this parameter."
                status = "NoContext"

            recommendations.append({
                "parameter": parameter,
                "value": value,
                "status": status,
                "advice": advice,
            })

        # Persist the interaction
        try:
            add_query_response(
                conn=conn,
                query=query,
                response=str(recommendations),
                user_id=user_id,
            )
            log_info(f"Stored interaction for user {user_id}")
        except RuntimeError as e:
            log_error(f"DB storage error: {e}")

        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "status": "success",
                "user_id": user_id,
                "recommendations": recommendations,
                "cached": False,
            },
        )

    except Exception as e:
        log_error(f"Unexpected error in /chat: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request",
        ) from e
