"""
Database Models for ORION Architekt-AT
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import bcrypt

Base = declarative_base()


class User(Base):
    """User model"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="user")  # user, architect, engineer, admin
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    projects = relationship("Project", back_populates="owner")
    comments = relationship("Comment", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")

    def verify_password(self, password: str) -> bool:
        """Verify password"""
        return bcrypt.checkpw(password.encode("utf-8"), self.hashed_password.encode("utf-8"))

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password"""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


class Project(Base):
    """Project model"""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    bundesland = Column(String(50), nullable=False)
    building_type = Column(String(50), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Project data
    bgf_m2 = Column(Float)
    geschosse = Column(Integer)
    wohnungen = Column(Integer)
    budget_euro = Column(Float)
    energieziel = Column(String(10))

    # Relationships
    owner = relationship("User", back_populates="projects")
    members = relationship("ProjectMember", back_populates="project")
    comments = relationship("Comment", back_populates="project")
    calculations = relationship("Calculation", back_populates="project")
    bim_files = relationship("BIMFile", back_populates="project")


class ProjectMember(Base):
    """Project team members"""

    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), nullable=False)  # architect, engineer, client, viewer
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    project = relationship("Project", back_populates="members")


class Comment(Base):
    """Comments on projects"""

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(String(50), unique=True, index=True, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    element_id = Column(String(100))  # IFC element ID
    text = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"))  # For replies
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="comments")
    user = relationship("User", back_populates="comments")
    replies = relationship("Comment", remote_side=[parent_id])


class Calculation(Base):
    """Stored calculations"""

    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    calculation_type = Column(String(50), nullable=False)  # uwert, stellplaetze, etc.
    input_data = Column(JSON, nullable=False)
    result_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    project = relationship("Project", back_populates="calculations")


class BIMFile(Base):
    """BIM/IFC files"""

    __tablename__ = "bim_files"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer)
    ifc_version = Column(String(20))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(Integer, ForeignKey("users.id"))

    # Analysis results
    analysis_data = Column(JSON)
    compliance_data = Column(JSON)

    # Relationships
    project = relationship("Project", back_populates="bim_files")


class APIKey(Base):
    """API keys for authentication"""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100))
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=1000)  # Requests per hour
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    last_used_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="api_keys")


class ActivityLog(Base):
    """Activity log for audit trail"""

    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    action_type = Column(String(50), nullable=False)
    description = Column(Text)
    details = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
