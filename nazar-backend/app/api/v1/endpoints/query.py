from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/query", tags=["query"])
def handle_query(request: QueryRequest):
    # Dummy implementation for Voice Query Bar
    return {
        "text": f"Found results for: {request.query}",
        "bounds": [[28.5350, 77.3900], [28.5360, 77.3920]]
    }
