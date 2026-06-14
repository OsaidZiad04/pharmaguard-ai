from fastapi import APIRouter

from app.schemas.rag import RagQueryRequest, RagQueryResponse
from app.services.rag_service import query_local_knowledge_base

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/query", response_model=RagQueryResponse)
def query_rag(payload: RagQueryRequest) -> RagQueryResponse:
    return query_local_knowledge_base(
        query=payload.query,
        top_k=payload.top_k,
    )
