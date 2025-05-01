import logging
from datetime import datetime, timedelta
from typing import BinaryIO, List, Optional, Dict
import uuid

from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from fastapi import HTTPException, UploadFile

from app.core.config import settings

logger = logging.getLogger(__name__)


class AzureBlobService:
    """Service for handling Azure Blob Storage operations."""

    def __init__(self):
        try:
            self.connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
            self.container_name = settings.AZURE_BLOB_CONTAINER_NAME
            self.blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string)
            self._ensure_container_exists()
        except Exception as e:
            logger.error(f"Error initializing Azure Blob Service: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to initialize Azure Blob Storage")

    def _ensure_container_exists(self):
        """Ensure the blob container exists, creating it if necessary."""
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name)
            if not container_client.exists():
                container_client = self.blob_service_client.create_container(
                    self.container_name)
                logger.info(f"Created blob container: {self.container_name}")
            return container_client
        except Exception as e:
            logger.error(f"Error ensuring container exists: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to create or access blob container")

    async def upload_file(self, file: UploadFile, folder_path: str = "") -> Dict[str, str]:
        """
        Upload a file to Azure Blob Storage.

        Args:
            file: The file to upload
            folder_path: Optional folder path within the container

        Returns:
            Dict with file information including blob_path and URL
        """
        try:
            # Generate a unique name for the blob
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            sanitized_filename = file.filename.replace(" ", "_")
            blob_name = f"{folder_path}/{timestamp}_{unique_id}_{sanitized_filename}" if folder_path else f"{timestamp}_{unique_id}_{sanitized_filename}"
            blob_name = blob_name.lstrip('/')

            # Get a blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )

            # Upload the file content
            file_content = await file.read()
            blob_client.upload_blob(file_content, overwrite=True)

            # Get the URL
            sas_token = self._generate_sas_token(blob_name)
            url = f"{blob_client.url}?{sas_token}"

            return {
                "blob_path": blob_name,
                "url": url,
                "file_name": file.filename,
                "file_size": len(file_content),
                "content_type": file.content_type
            }

        except Exception as e:
            logger.error(
                f"Error uploading file to Azure Blob Storage: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to upload file to Azure Blob Storage")

    def download_file(self, blob_path: str) -> bytes:
        """
        Download a file from Azure Blob Storage.

        Args:
            blob_path: Path to the blob within the container

        Returns:
            The file content as bytes
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_path
            )

            # Download the blob
            blob_data = blob_client.download_blob()
            content = blob_data.readall()

            return content

        except Exception as e:
            logger.error(
                f"Error downloading file from Azure Blob Storage: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to download file from Azure Blob Storage")

    def delete_file(self, blob_path: str) -> bool:
        """
        Delete a file from Azure Blob Storage.

        Args:
            blob_path: Path to the blob within the container

        Returns:
            True if deletion was successful
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_path
            )

            # Delete the blob
            blob_client.delete_blob()

            return True

        except Exception as e:
            logger.error(
                f"Error deleting file from Azure Blob Storage: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to delete file from Azure Blob Storage")

    def list_files(self, folder_path: Optional[str] = None) -> List[Dict[str, str]]:
        """
        List files in a folder in Azure Blob Storage.

        Args:
            folder_path: Optional folder path within the container

        Returns:
            List of file information
        """
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name)

            # List blobs in the container or folder
            prefix = f"{folder_path}/" if folder_path else ""
            blobs = container_client.list_blobs(name_starts_with=prefix)

            result = []
            for blob in blobs:
                # Generate SAS token for accessing the blob
                sas_token = self._generate_sas_token(blob.name)
                blob_client = self.blob_service_client.get_blob_client(
                    container=self.container_name,
                    blob=blob.name
                )
                url = f"{blob_client.url}?{sas_token}"

                result.append({
                    "name": blob.name.split('/')[-1],
                    "blob_path": blob.name,
                    "size": blob.size,
                    "created_at": blob.creation_time.isoformat(),
                    "url": url,
                    "content_type": blob.content_settings.content_type
                })

            return result

        except Exception as e:
            logger.error(
                f"Error listing files in Azure Blob Storage: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to list files in Azure Blob Storage")

    def _generate_sas_token(self, blob_name: str, expiry_hours: int = 24) -> str:
        """
        Generate a SAS token for accessing a blob.

        Args:
            blob_name: Name of the blob
            expiry_hours: Token expiry time in hours

        Returns:
            SAS token string
        """
        # Parse connection string for account name and key
        # This is a simplified approach; in production, use Azure Key Vault or Managed Identity
        conn_parts = self.connection_string.split(';')
        account_name = next((part.split(
            '=')[1] for part in conn_parts if part.startswith('AccountName=')), None)
        account_key = next((part.split(
            '=')[1] for part in conn_parts if part.startswith('AccountKey=')), None)

        if not account_name or not account_key:
            raise ValueError("Invalid connection string")

        # Generate SAS token
        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=self.container_name,
            blob_name=blob_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
        )

        return sas_token
