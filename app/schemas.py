"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


# Enums
class VisitType(str, Enum):
    INITIAL_CONSULTATION = "Initial Consultation"
    FOLLOW_UP = "Follow-up"
    ANNUAL_PHYSICAL = "Annual Physical"
    ACUTE_CARE = "Acute Care"
    PROCEDURE = "Procedure"


class EncounterStatus(str, Enum):
    DRAFT = "DRAFT"
    SIGNED = "SIGNED"
    EXPORTED = "EXPORTED"


# Chiropractic Record Schema (matches frontend TypeScript interface)
class ChiropracticRecord(BaseModel):
    """Structured chiropractic clinical record"""
    model_config = ConfigDict(use_enum_values=True)

    # Patient Info
    occupation: str = ""
    workload: str = "Unknown"
    isNewPatient: bool = False

    # Chief Complaint
    mainProblem: str = ""
    location: str = ""
    onset: str = "Unknown"
    duration: str = ""
    painQuality: List[str] = []

    # Pain Analysis
    aggravatedBy: str = ""
    relievedBy: str = ""
    diurnalVariation: List[str] = []
    radiation: str = ""
    numbness: bool = False
    weakness: bool = False

    # History
    similarProblems: bool = False
    historyDetails: str = ""
    previousTrauma: str = ""

    # Medical History
    conditions: str = ""
    surgeries: str = ""
    medications: str = ""
    allergies: str = ""
    sickLeave: bool = False

    # Red Flags
    redFlags: List[str] = []
    redFlagsComments: str = ""

    # Lifestyle
    activity: str = ""
    sleepQuality: str = "Unknown"
    stressLevel: str = "Unknown"
    workStress: bool = False

    # Clinical Exam
    inspection: str = ""
    palpation: str = ""
    tenderness: str = ""
    jointRestrictions: str = ""
    rom: str = ""
    neuro: str = ""
    orthoPositive: str = ""
    orthoNegative: str = ""

    # Assessment
    diagnosis: str = ""
    differential: str = ""
    prognosis: str = ""

    # Treatment Plan
    plannedTreatment: List[str] = []
    frequency: str = ""
    goals: str = ""

    # Treatment Today
    treatedArea: str = ""
    techniques: str = ""
    response: str = ""

    # Advice
    exercises: str = ""
    advice: str = ""

    # Follow-up
    nextAppointment: str = ""


# Patient Encounter Schemas
class PatientEncounter(BaseModel):
    """Patient encounter details"""
    patientName: str
    patientId: str
    visitType: VisitType
    date: str  # ISO date string


# Request Schemas
class GenerateNoteRequest(BaseModel):
    """Request to generate clinical note from transcript"""
    transcript: str = Field(..., min_length=10)
    visitType: VisitType
    encounter: PatientEncounter


class CreateEncounterRequest(BaseModel):
    """Request to create/save encounter"""
    encounter: PatientEncounter
    transcript: Optional[str] = None
    record: Optional[ChiropracticRecord] = None
    status: EncounterStatus = EncounterStatus.DRAFT


class UpdateEncounterRequest(BaseModel):
    """Request to update encounter"""
    record: Optional[ChiropracticRecord] = None
    status: Optional[EncounterStatus] = None
    transcript: Optional[str] = None


class SignNoteRequest(BaseModel):
    """Request to sign a note"""
    signedBy: str
    signature: Optional[str] = None  # Optional base64 digital signature


# Response Schemas
class GenerateNoteResponse(BaseModel):
    """Response from generate note endpoint"""
    success: bool
    data: ChiropracticRecord


class EncounterResponse(BaseModel):
    """Encounter response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    patient_name: str
    patient_id: str
    visit_type: str
    encounter_date: datetime
    transcript: Optional[str]
    record: Optional[dict]
    status: str
    signed_by: Optional[str]
    signed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class CreateEncounterResponse(BaseModel):
    """Response from create encounter"""
    success: bool
    encounter_id: UUID
    created_at: datetime


class SignNoteResponse(BaseModel):
    """Response from sign note"""
    success: bool
    signed_at: datetime
    status: str


# User/Auth Schemas
class UserCreate(BaseModel):
    """User registration"""
    email: EmailStr
    name: str
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """User login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """JWT token payload data"""
    user_id: UUID
    email: str


# Error Response
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
