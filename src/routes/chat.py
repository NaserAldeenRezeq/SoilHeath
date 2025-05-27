"""
docstring
"""

import os
import sys
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    sys.path.append(MAIN_DIR)

    from src.logs import log_error, log_info, log_debug, log_warning
    from src.dbs import add_query_response, fetch_all_rows
    from src.prompt import FarmAssistantPromptBuilder
    from src.schemes import ChatRoute
    from src.llm import HuggingFaceLLM, GoogleLLM
    from src.db_vector import StartQdrant
    from src.embedding import EmbeddingService
    from src.helpers import split_soil_elements

except ValueError as e:  # Replace with a specific exception type, e.g., ValueError
    msg = f"Import Error in: {__file__}, Error: {e}"
    raise ImportError(msg) from e

chat_route = APIRouter()

def get_llm(request: Request) -> Union[HuggingFaceLLM, GoogleLLM]:
    """Retrieve the LLM instance from the app state."""
    llm = request.app.state.llm
    if not llm:
        log_warning("LLM instance not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="""LLM service is not initialized. Please configure 
                      the LLM via the /llmsSettings endpoint."""
        )
    return llm

def get_qdrant_vector_db(request: Request) -> StartQdrant:
    """Retrieve the Qdrant vector database connection from the app state."""
    qdrant = request.app.state.qdrant
    if not qdrant:
        log_warning("Qdrant vector database connection not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Vector database service is not available."
        )
    return qdrant

def get_db_conn(request: Request):
    """Retrieve the relational database connection from the app state."""
    conn = request.app.state.conn
    if not conn:
        log_warning("Relational database connection not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Relational database service is not available."
        )
    return conn

def get_embedding_model(request: Request) -> EmbeddingService:
    """Retrieve the embedding model instance from the app state."""
    embedding = request.app.state.embedded  # Fixed typo: was request.pp.state.embedded
    if not embedding:
        log_warning("Embedding model instance not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Embedding model service is not available."
        )
    return embedding

def format_retrieved_context(retrieved_docs: list[dict]) -> str:
    """Format the retrieved documents into a context string for the prompt."""
    context_parts = []
    for i, doc in enumerate(retrieved_docs, 1):
        context_parts.append(f"Context {i} (Score: {doc['score']:.2f}): {doc['text']}")
    return "\n\n".join(context_parts)

@chat_route.post("/chat", response_class=JSONResponse)
async def chat(
    use_id: str,
    body: ChatRoute,
    top_k: int = 3,
    score_threshold: float = 0.7,
    llm: HuggingFaceLLM = Depends(get_llm),
    conn = Depends(get_db_conn),
    qdrant: StartQdrant = Depends(get_qdrant_vector_db),
    embedding: EmbeddingService = Depends(get_embedding_model)
) -> JSONResponse:
    """
    Chat endpoint that:
    1. Parses input elements
    2. Embeds user query
    3. Retrieves relevant context from vector DB
    4. Generates a response using the LLM
    5. Stores the interaction in the database
    
    Args:
        top_k: Number of relevant chunks to retrieve (default: 3)
        score_threshold: Minimum similarity score for retrieved chunks (default: 0.7)
    """
    query = body.query.strip()
    if not query:
        log_warning("Empty query received")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    log_error(query)
    try:
        soil, weather = split_soil_elements(query)

        log_error(f"Parsed elements: {soil}")

        log_debug(f"Parsed input for user_id={use_id}: SoilData={soil}, WeatherData={weather}")

        recommendations = []

        for parameter, value in soil.items():
            individual_query = f"{parameter}: {value}"
            log_debug(f"Processing {parameter} with value {value} for user {use_id}")

            query_embedding = embedding.embed(text=individual_query)

            retrieved_docs = qdrant.search_embeddings(
                collection_name="embeddings",
                query_embedding=query_embedding,
                top_k=top_k,
                score_threshold=score_threshold
            )
            status = "null"
            if not retrieved_docs:
                log_warning(f"No relevant documents found for {parameter}")

                context = format_retrieved_context(retrieved_docs)
                try:
                    prompt = FarmAssistantPromptBuilder().build_prompt(
                        context=context,
                        user_message=individual_query,
                        weather=weather
                    )
                    advice = llm.response(prompt=prompt).strip()
                    status = "Processed"
                    log_debug(f"Response for {parameter}: {advice[:100]}...")
                except RuntimeError as e:
                    log_error(f"Failed to generate response for {parameter}: {str(e)}")
                    advice = "Error generating advice."
                    status = "Error"

            recommendations.append({
                "parameter": parameter,
                "value": value,
                "status": status,
                "advice": advice
            })

        try:
            add_query_response(
                conn=conn,
                query=query,
                response=str(recommendations),
                user_id=use_id
            )
            log_info(f"Stored full interaction for user {use_id}")
        except RuntimeError as e:
            log_error(f"Failed to store interaction: {str(e)}")

        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "status": "success",
                "user_id": use_id,
                "recommendations": recommendations,
                "cached": False
            }
        )
    except Exception as e:
        log_error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        ) from e

