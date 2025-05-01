from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repositories.task_repository import TaskRepository
from app.schemas.storage import Document, DocumentCreate, DocumentList
from app.core.security import get_current_user
from app.schemas.auth import User
from app.services.azure_blob_service import AzureBlobService
from app.db.models import Document as DocumentModel

router = APIRouter()
blob_service = AzureBlobService()


@router.post("/upload", response_model=Document, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    task_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a file to Azure Blob Storage and store metadata in the database.
    """
    # Validate task if provided
    if task_id:
        task_repo = TaskRepository(db)
        task = task_repo.get(id=task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.owner_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Not enough permissions")

    try:
        # Determine folder structure based on task
        folder_path = f"users/{current_user.id}"
        if task_id:
            folder_path = f"{folder_path}/tasks/{task_id}"

        # Upload file to Azure Blob Storage
        blob_info = await blob_service.upload_file(file, folder_path)

        # Create document record in database
        document = DocumentModel(
            name=file.filename,
            description=description,
            file_type=file.content_type,
            file_size=blob_info["file_size"],
            blob_path=blob_info["blob_path"],
            metadata={"original_filename": file.filename,
                      "content_type": file.content_type},
            task_id=task_id,
            owner_id=current_user.id
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        # Return document with URL
        return Document(
            id=document.id,
            name=document.name,
            description=document.description,
            file_type=document.file_type,
            file_size=document.file_size,
            blob_path=document.blob_path,
            url=blob_info["url"],
            metadata=document.metadata,
            task_id=document.task_id,
            owner_id=document.owner_id,
            created_at=document.created_at,
            updated_at=document.updated_at
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )


@router.get("/files", response_model=DocumentList)
async def list_files(
    task_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List files stored in the system, optionally filtered by task.
    """
    # Build query
    query = db.query(DocumentModel).filter(
        DocumentModel.owner_id == current_user.id)

    if task_id:
        # Validate task belongs to user
        task_repo = TaskRepository(db)
        task = task_repo.get(id=task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.owner_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Not enough permissions")

        query = query.filter(DocumentModel.task_id == task_id)

    # Get total count
    total = query.count()

    # Get documents with pagination
    documents = query.order_by(DocumentModel.created_at.desc()).offset(
        skip).limit(limit).all()

    # Generate signed URLs for each document
    document_list = []
    for doc in documents:
        try:
            # Generate a SAS URL using the blob service
            sas_token = blob_service._generate_sas_token(doc.blob_path)
            # Construct the full URL
            blob_client = blob_service.blob_service_client.get_blob_client(
                container=blob_service.container_name,
                blob=doc.blob_path
            )
            url = f"{blob_client.url}?{sas_token}"

            document_list.append(
                Document(
                    id=doc.id,
                    name=doc.name,
                    description=doc.description,
                    file_type=doc.file_type,
                    file_size=doc.file_size,
                    blob_path=doc.blob_path,
                    url=url,
                    metadata=doc.metadata,
                    task_id=doc.task_id,
                    owner_id=doc.owner_id,
                    created_at=doc.created_at,
                    updated_at=doc.updated_at
                )
            )
        except Exception as e:
            # If URL generation fails, still include the document but without URL
            document_list.append(
                Document(
                    id=doc.id,
                    name=doc.name,
                    description=doc.description,
                    file_type=doc.file_type,
                    file_size=doc.file_size,
                    blob_path=doc.blob_path,
                    url=None,
                    metadata=doc.metadata,
                    task_id=doc.task_id,
                    owner_id=doc.owner_id,
                    created_at=doc.created_at,
                    updated_at=doc.updated_at
                )
            )

    return DocumentList(
        total=total,
        items=document_list
    )


@router.get("/files/{document_id}", response_model=Document)
async def get_file(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific file by ID.
    """
    # Get document from database
    document = db.query(DocumentModel).filter(
        DocumentModel.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        # Generate a SAS URL using the blob service
        sas_token = blob_service._generate_sas_token(document.blob_path)
        # Construct the full URL
        blob_client = blob_service.blob_service_client.get_blob_client(
            container=blob_service.container_name,
            blob=document.blob_path
        )
        url = f"{blob_client.url}?{sas_token}"

        return Document(
            id=document.id,
            name=document.name,
            description=document.description,
            file_type=document.file_type,
            file_size=document.file_size,
            blob_path=document.blob_path,
            url=url,
            metadata=document.metadata,
            task_id=document.task_id,
            owner_id=document.owner_id,
            created_at=document.created_at,
            updated_at=document.updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate access URL: {str(e)}"
        )


@router.delete("/files/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a file.
    """
    # Get document from database
    document = db.query(DocumentModel).filter(
        DocumentModel.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        # Delete from blob storage
        blob_service.delete_file(document.blob_path)

        # Delete from database
        db.delete(document)
        db.commit()

        return None
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )
