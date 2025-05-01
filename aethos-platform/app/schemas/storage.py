from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Base schema for Document with common attributes."""
    name: str
    description: Optional[str] = None
    file_type: str
    file_size: int
    blob_path: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DocumentCreate(DocumentBase):
    """Schema for creating a new Document."""
    task_id: Optional[int] = None
    owner_id: int


class DocumentUpdate(BaseModel):
    """Schema for updating an existing Document."""
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Document(DocumentBase):
    """Schema representing a Document."""
    id: int
    url: Optional[str] = None
    task_id: Optional[int] = None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class DocumentList(BaseModel):
    """Schema for a paginated list of Documents."""
    total: int
    items: List[Document]
