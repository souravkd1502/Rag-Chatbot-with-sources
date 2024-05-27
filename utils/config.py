"""
This module sets up the configuration for different language models based on environment variables.
It supports Claude, OpenAI, and Mistral models, and initializes HuggingFace embeddings.

The module performs the following steps:
1. Reads the model type and other necessary configuration from environment variables.
2. Sets up logging to provide informational and error messages.
3. Initializes the appropriate language model based on the specified type.
4. Configures HuggingFace embeddings.

Usage:
    Simply set the relevant environment variables (MODEL_TYPE, MODEL_NAME, API_KEYS, etc.),
    and import this module to use the configured language models and embeddings.
    
TODO:

FIXME:
"""

# Import dependencies
import os
from langchain_community.embeddings import HuggingFaceEmbeddings

# Set up logger
from .logger import create_logger

_logger = create_logger(__name__)


class Config:
    """
    Configuration class for setting up different language models based on the environment variables.

    Attributes:
        model_type (str): The type of model to use (Claude, OpenAI, or Mistral).
        llm (object): The initialized language model based on the specified model type.
        hf (HuggingFaceEmbeddings): HuggingFace embeddings model configuration.
    """

    # Get the model type from environment variables
    model_type = os.getenv("MODEL_TYPE")
    _logger.info(f"Model type specified: {model_type}")

    if model_type.lower() == "claude":
        # Configuration for Claude model
        model_name = os.getenv("MODEL_NAME")
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        _logger.info("Setting up Claude model configuration...")

        # Check if required variables are specified
        if any(
            value == "" or value is None for value in [model_name, anthropic_api_key]
        ):
            _logger.error("model_name and anthropic_api_key must be specified")
            raise ValueError("model_name and anthropic_api_key must be specified")

        try:
            from langchain_anthropic import ChatAnthropic

            _logger.info("Successfully imported ChatAnthropic module")
        except ImportError:
            _logger.exception("Could not import module langchain_anthropic")
            raise ImportError(
                "Could not import module. Please install langchain_anthropic with `pip install langchain_anthropic`"
            )

        # Initialize Claude model
        llm = ChatAnthropic(
            model_name=model_name,
            api_key=anthropic_api_key,
            temperature=0.2,
        )
        _logger.info("Claude model initialized successfully")

    elif model_type.lower() == "openai":
        # Configuration for OpenAI model
        model_name = os.getenv("MODEL_NAME")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        _logger.info("Setting up OpenAI model configuration...")

        # Check if required variables are specified
        if any(value == "" or value is None for value in [model_name, openai_api_key]):
            _logger.error("model_name and openai_api_key must be specified")
            raise ValueError("model_name and openai_api_key must be specified")

        try:
            from langchain_openai import ChatOpenAI

            _logger.info("Successfully imported ChatOpenAI module")
        except ImportError:
            _logger.exception("Could not import module langchain_openai")
            raise ImportError(
                "Could not import module. Please install langchain_openai with `pip install langchain_openai`"
            )

        # Initialize OpenAI model
        llm = ChatOpenAI(
            model=model_name,
            api_key=openai_api_key,
        )
        _logger.info("OpenAI model initialized successfully")

    elif model_type.lower() == "mistral":
        # Configuration for Mistral model
        model_path = os.getenv("MODEL_PATH")
        _logger.info("Setting up Mistral model configuration...")

        # Check if required variable is specified
        if any(value == "" or value is None for value in [model_path]):
            _logger.error("model_path must be specified")
            raise ValueError("model_path must be specified")

        try:
            from langchain_community.llms import CTransformers

            _logger.info("Successfully imported CTransformers module")
        except ImportError:
            _logger.exception("Cannot import module CTransformers")
            raise ImportError(
                "Cannot import module. Please install ctransformers with `pip install ctransformers` and `pip install langchain`"
            )

        # Initialize Mistral model
        llm = CTransformers(
            model=model_path,
            model_type="llama",
            config={"max_new_tokens": 512, "temperature": 0.8, "context_length": 4000},
        )
        _logger.info("Mistral model initialized successfully")

    # HuggingFace embeddings model configuration
    embedding_model_name = "sentence-transformers/all-mpnet-base-v2"
    embedding_model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": False}
    _logger.info(
        f"Initializing HuggingFace embeddings with model: {embedding_model_name}"
    )

    hf = HuggingFaceEmbeddings(
        model_name=embedding_model_name,
        model_kwargs=embedding_model_kwargs,
        encode_kwargs=encode_kwargs,
    )
    _logger.info(
        f"HuggingFace embeddings model {embedding_model_name} initialized successfully"
    )
