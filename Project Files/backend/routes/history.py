"""
History route — paginated query history for authenticated users.
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.database import get_db, User, QueryHistory
from routes.auth import get_current_user_from_token

router = APIRouter(prefix="/api", tags=["History"])


# ── Response schema ───────────────────────────────────────────

class HistoryItem(BaseModel):
    id: int
    natural_query: str
    generated_sql: str
    model_used: str
    confidence_score: float | None
    confidence_explanation: str | None
    executed: bool
    error: str | None
    created_at: str | None

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# ── Routes ────────────────────────────────────────────────────

@router.get("/history", response_model=HistoryResponse)
def get_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_from_token),
):
    """
    Return paginated query history.
    If authenticated, returns only the user's queries.
    If unauthenticated, returns all queries without a user_id (demo queries).
    """
    query = db.query(QueryHistory)

    if user:
        query = query.filter(QueryHistory.user_id == user.id)
    else:
        query = query.filter(QueryHistory.user_id.is_(None))

    # Total count
    total = query.count()

    # Paginate
    items = (
        query.order_by(QueryHistory.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # Serialize
    history_items = []
    for item in items:
        history_items.append(HistoryItem(
            id=item.id,
            natural_query=item.natural_query,
            generated_sql=item.generated_sql,
            model_used=item.model_used,
            confidence_score=item.confidence_score,
            confidence_explanation=item.confidence_explanation,
            executed=item.executed or False,
            error=item.error,
            created_at=item.created_at.isoformat() if item.created_at else None,
        ))

    total_pages = max(1, (total + page_size - 1) // page_size)

    return HistoryResponse(
        items=history_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.delete("/history/{query_id}")
def delete_history_item(
    query_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_token),
):
    """Delete a specific history entry (must belong to the user)."""
    entry = db.query(QueryHistory).filter(QueryHistory.id == query_id).first()

    if not entry:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="History entry not found.")

    if user and entry.user_id != user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not authorized to delete this entry.")

    db.delete(entry)
    db.commit()

    return {"message": "History entry deleted.", "id": query_id}
