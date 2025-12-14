"""
Encounter management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.schemas import (
    CreateEncounterRequest,
    CreateEncounterResponse,
    UpdateEncounterRequest,
    SignNoteRequest,
    SignNoteResponse,
    EncounterResponse
)
from app.models import User, Encounter, AuditLog, EncounterStatus as DBEncounterStatus
from app.middleware.auth import get_current_user


router = APIRouter(prefix="/encounters", tags=["Encounters"])


@router.post("/", response_model=CreateEncounterResponse, status_code=status.HTTP_201_CREATED)
async def create_encounter(
    request: CreateEncounterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new encounter

    - **encounter**: Patient encounter details
    - **transcript**: Optional transcript text
    - **record**: Optional chiropractic record data
    - **status**: Document status (default: DRAFT)
    """
    try:
        # Parse encounter date
        encounter_date = datetime.fromisoformat(request.encounter.date)

        # Create encounter
        encounter = Encounter(
            user_id=current_user.id,
            patient_name=request.encounter.patientName,
            patient_id=request.encounter.patientId,
            visit_type=request.encounter.visitType.value,
            encounter_date=encounter_date,
            transcript=request.transcript,
            record=request.record.model_dump() if request.record else None,
            status=DBEncounterStatus[request.status.value]
        )

        db.add(encounter)
        db.commit()
        db.refresh(encounter)

        # Create audit log
        audit_log = AuditLog(
            encounter_id=encounter.id,
            user_id=current_user.id,
            action="created"
        )
        db.add(audit_log)
        db.commit()

        return CreateEncounterResponse(
            success=True,
            encounter_id=encounter.id,
            created_at=encounter.created_at
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create encounter: {str(e)}"
        )


@router.get("/", response_model=List[EncounterResponse])
async def list_encounters(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """
    List all encounters for the current user

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    encounters = db.query(Encounter)\
        .filter(Encounter.user_id == current_user.id)\
        .order_by(Encounter.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

    return encounters


@router.get("/{encounter_id}", response_model=EncounterResponse)
async def get_encounter(
    encounter_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific encounter by ID
    """
    encounter = db.query(Encounter)\
        .filter(Encounter.id == encounter_id)\
        .first()

    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found"
        )

    # Check ownership
    if encounter.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this encounter"
        )

    # Create audit log for viewing
    audit_log = AuditLog(
        encounter_id=encounter.id,
        user_id=current_user.id,
        action="viewed"
    )
    db.add(audit_log)
    db.commit()

    return encounter


@router.put("/{encounter_id}", response_model=EncounterResponse)
async def update_encounter(
    encounter_id: UUID,
    request: UpdateEncounterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an encounter

    - **record**: Updated chiropractic record
    - **status**: Updated status
    - **transcript**: Updated transcript
    """
    encounter = db.query(Encounter)\
        .filter(Encounter.id == encounter_id)\
        .first()

    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found"
        )

    # Check ownership
    if encounter.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this encounter"
        )

    # Check if locked
    if encounter.status == DBEncounterStatus.SIGNED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a signed encounter"
        )

    try:
        # Track changes for audit
        changes = {}

        # Update fields
        if request.record is not None:
            encounter.record = request.record.model_dump()
            changes["record"] = "updated"

        if request.status is not None:
            encounter.status = DBEncounterStatus[request.status.value]
            changes["status"] = request.status.value

        if request.transcript is not None:
            encounter.transcript = request.transcript
            changes["transcript"] = "updated"

        db.commit()
        db.refresh(encounter)

        # Create audit log
        audit_log = AuditLog(
            encounter_id=encounter.id,
            user_id=current_user.id,
            action="updated",
            changes=changes
        )
        db.add(audit_log)
        db.commit()

        return encounter

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update encounter: {str(e)}"
        )


@router.post("/{encounter_id}/sign", response_model=SignNoteResponse)
async def sign_note(
    encounter_id: UUID,
    request: SignNoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sign a clinical note

    - **signedBy**: Name of the person signing
    - **signature**: Optional digital signature (base64)
    """
    encounter = db.query(Encounter)\
        .filter(Encounter.id == encounter_id)\
        .first()

    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found"
        )

    # Check ownership
    if encounter.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to sign this encounter"
        )

    # Check if already signed
    if encounter.status == DBEncounterStatus.SIGNED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Encounter is already signed"
        )

    try:
        # Update encounter
        encounter.status = DBEncounterStatus.SIGNED
        encounter.signed_by = request.signedBy
        encounter.signed_at = datetime.utcnow()

        db.commit()
        db.refresh(encounter)

        # Create audit log
        audit_log = AuditLog(
            encounter_id=encounter.id,
            user_id=current_user.id,
            action="signed",
            changes={"signedBy": request.signedBy}
        )
        db.add(audit_log)
        db.commit()

        return SignNoteResponse(
            success=True,
            signed_at=encounter.signed_at,
            status=encounter.status.value
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sign note: {str(e)}"
        )


@router.delete("/{encounter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_encounter(
    encounter_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an encounter (soft delete or hard delete based on requirements)
    """
    encounter = db.query(Encounter)\
        .filter(Encounter.id == encounter_id)\
        .first()

    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found"
        )

    # Check ownership
    if encounter.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this encounter"
        )

    # Don't allow deletion of signed notes
    if encounter.status == DBEncounterStatus.SIGNED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a signed encounter"
        )

    try:
        # Create audit log before deletion
        audit_log = AuditLog(
            encounter_id=encounter.id,
            user_id=current_user.id,
            action="deleted"
        )
        db.add(audit_log)

        # Delete encounter
        db.delete(encounter)
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete encounter: {str(e)}"
        )
