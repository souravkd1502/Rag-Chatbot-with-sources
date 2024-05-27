"""
Module for managing memory sessions using Redis for storing and retrieving chat history.

This module provides the ManageMemory class, which is used to interact with Redis for storing and
retrieving chat history data. It supports initialization, retrieval of messages, and adding messages
to Redis.

Classes:
    ManageMemory: A class to manage memory sessions using Redis for storing and retrieving chat history.

TODO:

FIXME:
"""

# Import Dependencies
import json
from langchain.schema import messages_from_dict
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory

from typing import Dict

# Set up logger
from .logger import create_logger

_logger = create_logger(__name__)


class ManageMemory:
    """
    A class to manage memory sessions using Redis for storing and retrieving chat history.

    Attributes:
        redis_url (str): The URL of the Redis server.
        redis_timeout (int): The time-to-live for Redis entries.
    """

    def __init__(
        self,
        redis_url: str = "http://localhost:6379",
        ttl: int = 600,
    ) -> None:
        """
        Initialize the ManageMemory instance.

        Args:
            redis_url (str, optional): The URL of the Redis server. Defaults to "http://localhost:6379".
            ttl (int, optional): The time-to-live for Redis entries in seconds. Defaults to 600.
        """
        self.redis_url = redis_url
        self.redis_timeout = ttl
        _logger.info(
            f"ManageMemory initialized with redis_url: {redis_url}, ttl: {ttl}"
        )

    def get_message_from_redis(self, session_id: str) -> ConversationBufferWindowMemory:
        """
        Retrieve messages from Redis and return a ConversationBufferWindowMemory object.

        Args:
            session_id (str): The unique identifier for the session.

        Returns:
            ConversationBufferWindowMemory: The chat memory buffer containing the retrieved messages.

        Raises:
            Exception: If there is an error retrieving messages from Redis.
        """
        try:
            _logger.info(
                f"Connecting to Redis at {self.redis_url} with session_id: {session_id} and ttl: {self.redis_timeout}"
            )

            # Initialize RedisChatMessageHistory
            message_history = RedisChatMessageHistory(
                url=self.redis_url, ttl=self.redis_timeout, session_id=session_id
            )

            _logger.info("Retrieving message history from Redis")
            # Retrieve and deserialize messages
            retrieve_from_db = json.loads(json.dumps(message_history))
            retrieved_messages = messages_from_dict(retrieve_from_db)
            retrieved_chat_history = ChatMessageHistory(messages=retrieved_messages)

            _logger.info("Messages retrieved successfully from Redis")
            return ConversationBufferWindowMemory(
                chat_memory=retrieved_chat_history,
                memory_key="chat_history",
                input_key="input",
                k=4,
            )

        except Exception as e:
            _logger.exception(
                f"Error retrieving messages from Redis for session_id: {session_id}"
            )
            raise Exception("Error retrieving messages from Redis") from e

    def add_messages_to_redis(self, session_id: str, messages: Dict[str, str]) -> None:
        """
        Add messages to Redis for the specified session.

        Args:
            session_id (str): The unique identifier for the session.
            messages (Dict[str, str]): A dictionary containing 'user' and 'ai_assistant' messages.

        Raises:
            KeyError: If 'user' or 'ai_assistant' is not specified in the messages dictionary.
            Exception: If there is an error adding messages to Redis.
        """
        if "user" not in messages or "ai_assistant" not in messages:
            _logger.error(
                "Both 'user' and 'ai_assistant' must be specified in messages"
            )
            raise KeyError(
                "Both 'user' and 'ai_assistant' must be specified in messages"
            )

        try:
            _logger.info(f"Adding messages to Redis for session_id: {session_id}")

            # Initialize RedisChatMessageHistory
            message_history = RedisChatMessageHistory(
                url=self.redis_url, ttl=self.redis_timeout, session_id=session_id
            )

            # Add the message history
            message_history.add_user_message(messages["user"])
            message_history.add_ai_message(messages["ai_assistant"])
            _logger.info("Messages added successfully to Redis")

        except Exception as e:
            _logger.exception(
                f"Error adding messages to Redis for session_id: {session_id}"
            )
            raise Exception("Error adding messages to Redis") from e
