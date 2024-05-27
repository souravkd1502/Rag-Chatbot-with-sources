"""

"""

# Import Dependencies
from pydantic import BaseModel
from typing import Optional


class UploadRequest(BaseModel):
    """
    Model to represent the upload request data.

    Args:
        BaseModel (pydantic.BaseModel): Pydantic BaseModel to handle data validation and serialization.

    Attributes:
        url (str): URL to the WordPress site or file that will be uploaded.
        create_collection (bool): Whether to create a new collection for Chroma DB.
        collection_name (Optional[str]): Name of the collection. If not provided, defaults to 'Default_Collection'.
    """

    url: str  # URL to WordPress site/file that will be uploaded
    create_collection: bool  # Whether to create a new collection for Chroma DB
    collection_name: Optional[str] = None  # Name of the collection


class UploadResponse(BaseModel):
    """
    Model to represent the response of the upload request.

    Args:
        BaseModel (pydantic.BaseModel): Pydantic BaseModel to handle data validation and serialization.

    Attributes:
        message (str): Description of the upload request.
        status (str): Status of the upload request.
    """

    message: str  # Description of the upload request
    status: str  # Status of the upload request
