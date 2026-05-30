# =============================================================================
# backend/storage/storage_manager.py
# File Storage Abstraction Layer (Local Filesystem / AWS S3)
# =============================================================================

import os
import uuid
from abc import ABC, abstractmethod

class BaseStorage(ABC):
    """Abstract interface defining required storage operations"""
    
    @abstractmethod
    def save(self, file, ext: str) -> str:
        """Save a file and return the absolute path or S3 URL"""
        pass
        
    @abstractmethod
    def delete(self, identifier: str) -> bool:
        """Delete a file using its local path or S3 URL"""
        pass


class LocalStorage(BaseStorage):
    """Saves files to a local uploads directory"""
    
    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder
        os.makedirs(self.upload_folder, exist_ok=True)
        
    def save(self, file, ext: str) -> str:
        unique_name = f"{uuid.uuid4()}.{ext}"
        dest_path = os.path.join(self.upload_folder, unique_name)
        
        # Save file stream to local disk
        file.save(dest_path)
        return dest_path
        
    def delete(self, identifier: str) -> bool:
        if os.path.exists(identifier):
            try:
                os.remove(identifier)
                return True
            except OSError:
                return False
        return False


class S3Storage(BaseStorage):
    """Saves files to AWS S3 storage bucket using boto3"""
    
    def __init__(self, bucket_name: str, region: str, access_key: str, secret_key: str):
        self.bucket_name = bucket_name
        self.region = region
        
        try:
            import boto3
            # Initialize boto3 S3 client
            self.s3_client = boto3.client(
                "s3",
                region_name=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key
            )
        except ImportError:
            raise ImportError(
                "AWS S3 storage selected but 'boto3' library is not installed. "
                "Please run: pip install boto3"
            )
            
    def save(self, file, ext: str) -> str:
        unique_name = f"{uuid.uuid4()}.{ext}"
        
        try:
            # Upload file stream to S3
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                unique_name,
                ExtraArgs={"ContentType": f"application/{ext}"}
            )
            
            # Construct the S3 URL (using standard AWS URL schema)
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{unique_name}"
            return s3_url
            
        except Exception as e:
            raise IOError(f"Failed to upload file to AWS S3: {str(e)}")
            
    def delete(self, identifier: str) -> bool:
        try:
            # Extract key from S3 URL
            # Example: https://my-bucket.s3.us-east-1.amazonaws.com/unique-id.pdf -> unique-id.pdf
            key = identifier.split("/")[-1]
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False


def get_storage_provider(app) -> BaseStorage:
    """
    Factory function resolving storage provider from environment configurations.
    Falls back cleanly to LocalStorage if credentials are not provided.
    """
    config = app.config
    provider_type = config.get("STORAGE_PROVIDER", "local").lower()
    
    if provider_type == "s3" and config.get("S3_BUCKET"):
        try:
            return S3Storage(
                bucket_name=config.get("S3_BUCKET"),
                region=config.get("AWS_REGION", "us-east-1"),
                access_key=config.get("AWS_ACCESS_KEY_ID"),
                secret_key=config.get("AWS_SECRET_ACCESS_KEY")
            )
        except Exception as e:
            app.logger.error(f"S3 Storage initialization failed: {str(e)}. Falling back to LocalStorage.")
            
    # Fallback to local storage
    return LocalStorage(upload_folder=config.get("UPLOAD_FOLDER", "uploads"))
