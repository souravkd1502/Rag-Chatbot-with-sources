"""

TODO:

FIXME:
"""

# Define App information
TITLE = "RAG-based Query Suggestion Chatbot"
DESCRIPTION = """A versatile, intelligent chatbot that utilizes a Retrieval-Augmented Generation (RAG) system enhanced
    with a Chain of Thought (CoT) strategy. This chatbot will be integrated into various WordPress blogs and sites, designed to
    handle and adapt to a wide range of topics, maintaining logical and contextually relevant interactions."""
__version__ = "1.0"
AUTHOR = "Sourav Das"
EMAIL = "sourav.bt.kt@gmail.com"

# import dependencies
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, Response, Request

from utils.middleware import (
    jwt_auth_middleware,
    basic_auth_middleware,
)

from utils.services import (
    get_wordpress_api_json,
    data_loader,
)

from utils.models import (
    UploadRequest,
    UploadResponse,
)

# Set up logging
from utils.logger import create_logger

_logger = create_logger(__name__)

# Set up FastAPI Application
app = FastAPI(
    title=TITLE,
    description=DESCRIPTION,
    version=__version__,
    contact={
        "author": AUTHOR,
        "email": EMAIL,
    },
    debug=True,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    _logger.info(f"Server NOW started! " f"Listening to [::]:8080")


@app.get("/ping")
def check_liveness() -> str:
    """
    Sanity check - this will let the caller know that the service is operational.

    Returns:
        str: The status of the server ('pong' for running)
    """
    return "pong!"


@app.get("/")
def read_root(verification=Depends(basic_auth_middleware)) -> str:
    """
    Root path welcome message.

    Returns:
        str: General Information about the Application APIs
    """
    if verification:
        return (
            f"{TITLE} v{__version__} 🚀 {DESCRIPTION} ✨ "
            f"author: {AUTHOR} email: {EMAIL} 📄  "
            "Check out /docs or /redoc for the API documentation!"
        )
    else:
        raise HTTPException(status_code=401, detail="User not authorized.")


@app.post("/chat")
def chatWithDocs(verification=Depends(basic_auth_middleware)) -> Response:
    """_summary_

    Args:
        verification (_type_, optional): _description_. Defaults to Depends(basic_auth_middleware).

    Raises:
        HTTPException: _description_

    Returns:
        Response: _description_
    """
    if not verification:
        raise HTTPException(status_code=401, detail="User not authorized.")


@app.post("/upload", response_model=UploadResponse, tags=["Upload"])
def upload_data(
    request: UploadRequest, verification=Depends(basic_auth_middleware)
) -> UploadResponse:
    """
    Endpoint to upload data from a WordPress API URL to ChromaDB.

    Args:
        request (UploadRequest): The request containing the WordPress API URL and collection details.
        verification: The result of the basic authentication middleware.

    Returns:
        UploadResponse: The response indicating the status of the upload operation.

    Raises:
        HTTPException: If the user is not authorized or if any error occurs during the process.
    """
    try:
        # Authentication
        if not verification:
            _logger.warning("User not authorized.")
            raise HTTPException(status_code=401, detail="User not authorized.")

        # Get request parameters
        wp_url = request.url
        create_collection = request.create_collection
        collection_name = (
            request.collection_name if request.collection_name else "Default_Collection"
        )

        # Get data from WordPress API
        _logger.info(f"Fetching data from WordPress API at {wp_url}.")
        wp_data = get_wordpress_api_json(
            request_session=requests.Session(),
            api_url=wp_url,
            api_call_timeout=600,
        )

        # Load WordPress data to ChromaDB
        _logger.info(f"Loading data to ChromaDB collection: {collection_name}.")
        data_loader(
            text=wp_data,
            collection_name=collection_name,
        )

        return UploadResponse(message="Data loaded successfully", status="success")

    except requests.RequestException as e:
        _logger.error(f"An error occurred while fetching data from WordPress API: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching data from WordPress API: {e}",
        )

    except Exception as e:
        _logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}"
        )
