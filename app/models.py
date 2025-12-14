"""
SQLAlchemy ORM Models
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    """User roles"""
    PROVIDER = "provider"
    ADMIN = "admin"
    STAFF = "staff"


class EncounterStatus(str, enum.Enum):
    """Encounter status"""
    DRAFT = "DRAFT"
    SIGNED = "SIGNED"
    EXPORTED = "EXPORTED"


class User(Base):
    """User/Provider model"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.PROVIDER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    encounters = relationship("Encounter", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Encounter(Base):
    """Patient encounter model"""
    __tablename__ = "encounters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Patient information
    patient_name = Column(String(255), nullable=False)
    patient_id = Column(String(100), nullable=False, index=True)
    visit_type = Column(String(100), nullable=False)
    encounter_date = Column(DateTime, nullable=False)

    # Transcript
    transcript = Column(Text, nullable=True)

    # Chiropractic record (stored as JSONB for flexibility)
    record = Column(JSONB, nullable=True)

    # Document status
    status = Column(SQLEnum(EncounterStatus), default=EncounterStatus.DRAFT, nullable=False)
    signed_by = Column(String(255), nullable=True)
    signed_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="encounters")
    audit_logs = relationship("AuditLog", back_populates="encounter")


class AuditLog(Base):
    """Audit log for compliance tracking"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("encounters.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    action = Column(String(100), nullable=False)  # created, updated, signed, viewed, exported
    changes = Column(JSONB, nullable=True)  # Store what changed
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6
    user_agent = Column(String(500), nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
    encounter = relationship("Encounter", back_populates="audit_logs")
