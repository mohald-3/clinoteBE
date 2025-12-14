"""
AI/Gemini integration routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import GenerateNoteRequest, GenerateNoteResponse
from app.services.gemini_service import generate_chiropractic_draft
from app.middleware.auth import get_current_user
from app.models import User


router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/generate-note", response_model=GenerateNoteResponse)
async def generate_note(
    request: GenerateNoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate structured clinical note from transcript using Gemini AI

    - **transcript**: Raw conversation transcript (min 10 characters)
    - **visitType**: Type of clinical visit
    - **encounter**: Patient encounter details

    Returns structured ChiropracticRecord
    """
    try:
        # Generate clinical note using Gemini
        record = await generate_chiropractic_draft(
            transcript=request.transcript,
            visit_type=request.visitType.value
        )

        return GenerateNoteResponse(success=True, data=record)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate note: {str(e)}"
        )
