"""
Generate route — executes the split-work pipeline (Planner + Coder).
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.database import get_db, User, QueryHistory
from services.groq_service import execute_pipeline, get_available_models
from services.confidence_service import calculate_confidence
from routes.auth import get_current_user_from_token

router = APIRouter(prefix="/api", tags=["Generate"])


# ── Request/Response schemas ──────────────────────────────────

class GenerateRequest(BaseModel):
    question: str
    conversation_history: list[dict] | None = None


class GenerateResponse(BaseModel):
    plan: str
    sql: str
    planner_model: str
    coder_model: str
    confidence: dict
    query_id: int | None = None


# ── Routes ────────────────────────────────────────────────────

@router.post("/generate", response_model=GenerateResponse)
async def generate(
    req: GenerateRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_from_token),
):
    """
    Execute the multi-agent pipeline where work is split:
    Llama plans the query, Qwen writes the code.
    """
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        # Run the split-work pipeline
        pipeline_result = await execute_pipeline(
            question=req.question,
            conversation_history=req.conversation_history,
        )

        # Calculate confidence score of the final SQL
        confidence = calculate_confidence(
            sql=pipeline_result["sql"],
            question=req.question,
        )

        model_desc = f"{pipeline_result['planner_model']} (Plan) + {pipeline_result['coder_model']} (SQL)"

        # Save to history
        history_entry = QueryHistory(
            user_id=user.id if user else None,
            natural_query=req.question,
            generated_sql=pipeline_result["sql"],
            model_used=model_desc,
            confidence_score=confidence["score"],
            confidence_explanation=confidence["explanation"],
            executed=False,
        )
        db.add(history_entry)
        db.commit()
        db.refresh(history_entry)

        return GenerateResponse(
            plan=pipeline_result["plan"],
            sql=pipeline_result["sql"],
            planner_model=pipeline_result["planner_model"],
            coder_model=pipeline_result["coder_model"],
            confidence=confidence,
            query_id=history_entry.id,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")


@router.get("/models")
def list_models():
    return {"models": get_available_models()}


@router.get("/schema")
def get_schema():
    from services.schema_service import get_schema_string, get_all_columns
    return {
        "schema_text": get_schema_string(),
        "tables": get_all_columns(),
    }
