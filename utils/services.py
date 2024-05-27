"""

TODO:

FIXME:
"""

# Import dependencies
import os
import uuid
import base64
import requests
import chromadb
from requests import Session
from langchain_chroma import Chroma
from chromadb.config import Settings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings

from typing import Optional

from .config import Config

# Set up logger
from .logger import create_logger

_logger = create_logger(__name__)

# Environment variables
user = os.getenv("WP_USER")
password = os.getenv("WP_PASSWORD")
credentials = user + ":" + password
token = base64.b64encode(credentials.encode())
headers = {"Authorization": "Basic " + token.decode("utf-8")}


def get_wordpress_api_json(
    request_session: Session, api_url: str, api_call_timeout: int
) -> dict:
    """
    Sends a GET request to a specified WordPress API endpoint and returns the JSON response.

    Args:
        request_session (Session): A configured `requests.Session` object used to send the request.
        api_url (str): The URL of the WordPress API endpoint to be called.
        api_call_timeout (int): The timeout duration for the API call in seconds.

    Raises:
        Exception: If the API response status code is not 200 (OK).
        Exception: If the API call times out.
        Exception: If any other `requests` exception occurs during the API call.

    Returns:
        dict: The JSON response from the WordPress API if the call is successful.
    """
    try:
        _logger.info(f"Sending request to {api_url} endpoint...")
        response = request_session.get(
            url=api_url, headers=headers, timeout=api_call_timeout
        )

        if response.status_code == 200:
            json_raw = response.json()
            _logger.info(f"API response: {response.status_code} {response.reason}")
            return json_raw

        else:
            _logger.error(
                f"API response: {response.status_code} {response.reason} - {response.text}"
            )
            raise Exception(
                f"API response: {response.status_code} {response.reason} - {response.text}"
            )

    except requests.exceptions.Timeout:
        _logger.error(f"API call request timed out after {api_call_timeout} seconds!")
        raise Exception(f"API call request timed out after {api_call_timeout} seconds!")

    except requests.exceptions.RequestException as e:
        _logger.exception(f"Error during API call to {api_url}: {e}")
        raise Exception(f"Error during API call to {api_url}: {e}") from e


def data_loader(text: str, collection_name: str) -> None:
    """
    Loads text data, splits it into chunks, and stores it in a Chroma collection.

    Args:
        text (str): The input text to be loaded and split.
        collection_name (str): The name of the Chroma collection to store the chunks.

    Raises:
        ValueError: If the text or collection name is empty.
        ChromaException: If there is an error interacting with Chroma.
    """
    if not text or not collection_name:
        raise ValueError("Text and collection name must be provided and cannot be empty.")
    
    try:
        # Load the document and split it into chunks
        _logger.info("Loading document.")
        loader = TextLoader(text)
        documents = loader.load()

        # Split the document into chunks
        _logger.info("Splitting document into chunks.")
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        docs = text_splitter.split_documents(documents)

        # Initialize Chroma client and reset the database
        _logger.info("Initializing Chroma client and resetting the database.")
        client = chromadb.HttpClient(settings=Settings(allow_reset=True))
        client.reset()

        # Get or create the collection in Chroma
        _logger.info(f"Getting or creating collection: {collection_name}.")
        collection = client.get_or_create_collection(collection_name)

        # Add documents to the collection
        _logger.info("Adding documents to the collection.")
        for doc in docs:
            collection.add(
                ids=[str(uuid.uuid1())], 
                metadatas=doc.metadata, 
                documents=doc.page_content
            )

    except Exception as e:
        _logger.error(f"An error occurred while interacting with Chroma: {e}")
        raise

def create_vector_db_from_chroma(collection_name: str, embeddings: Optional[HuggingFaceEmbeddings] = Config.hf) -> Chroma:
    """
    Creates a Chroma vector database from the specified collection name using the provided embeddings.

    Args:
        collection_name (str): The name of the Chroma collection to create the vector database from.
        embeddings (HuggingFaceEmbeddings, optional): The embedding function to use. Defaults to Config.hf.

    Returns:
        Chroma: The Chroma vector database instance.

    Raises:
        ValueError: If the collection name is empty.
        ChromaException: If there is an error interacting with Chroma.
    """
    if not collection_name:
        raise ValueError("Collection name must be provided and cannot be empty.")

    try:
        _logger.info(f"Creating Chroma vector database for collection: {collection_name}.")
        client = chromadb.HttpClient(settings=Settings(allow_reset=True))
        vector_db = Chroma(
            client=client,
            collection_name=collection_name,
            embedding_function=embeddings,
        )
        return vector_db

    except Exception as e:
        _logger.error(f"An error occurred while creating the Chroma vector database: {e}")
        raise
