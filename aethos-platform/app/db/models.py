import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)

    # Relationships
    agents = relationship("Agent", back_populates="owner",
                          cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="owner",
                         cascade="all, delete-orphan")


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    description = Column(Text)
    agent_type = Column(String(50))
    capabilities = Column(JSON)
    config = Column(JSON)
    azure_agent_id = Column(String(255), unique=True)
    autogen_agent_id = Column(String(255), unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    owner = relationship("User", back_populates="agents")
    tasks = relationship("Task", back_populates="agent",
                         cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    description = Column(Text)
    input_data = Column(JSON)
    output_data = Column(JSON)
    status = Column(String(50), default="pending")
    azure_task_id = Column(String(255), unique=True)
    autogen_task_id = Column(String(255), unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    agent = relationship("Agent", back_populates="tasks")
    owner = relationship("User", back_populates="tasks")
    documents = relationship(
        "Document", back_populates="task", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text, nullable=True)
    file_type = Column(String(50))
    file_size = Column(Integer)
    blob_path = Column(String(255))
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    task = relationship("Task", back_populates="documents")
