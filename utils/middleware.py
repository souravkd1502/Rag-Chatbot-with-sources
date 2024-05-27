"""
This module contains functions for middleware used in an API application.

* Functions:
    - basic_auth_middleware: Middleware function for basic authentication. 
        It checks if the provided HTTP basic authentication credentials are valid.
    - loggingMiddleware: Middleware for logging HTTP requests and responses.

These middleware functions are used to handle authentication and logging for incoming HTTP requests and outgoing HTTP 
responses in an API application.

TODO: Add middleware for BasicAuth (DONE)
TODO: Add middleware for Logging (Bugs)
TODO: Add middleware for CORS (DONE)
TODO: SetUp OAuth middleware configuration
TODO: Implement JWT middleware for User and role authentication (In Progress)

FIXME: Address any existing issues or bugs in the codebase.
FIXME: Fix logging middleware.
"""

# Import Dependencies
import os
import time
import json
from jose import JWTError, jwt
from starlette.responses import Response
from fastapi import HTTPException, Depends, Request
from fastapi.security import (
    HTTPBasic,
    HTTPBearer,
    HTTPBasicCredentials, 
    HTTPAuthorizationCredentials
)


# Setup Logger
from .logger import create_logger
_logger = create_logger(__name__)

# Initialize security model for BasicAuth
security_model = HTTPBasic()
security = HTTPBearer()


def basic_auth_middleware(credentials: HTTPBasicCredentials = Depends(security_model)):
    """
    Middleware function for basic authentication.

    This function checks if the provided HTTP basic authentication credentials are valid.
    It compares the provided username and password with the correct ones.
    
    Args:
        credentials (HTTPBasicCredentials, optional): The HTTP basic authentication credentials. Defaults to Depends(security_model).

    Raises:
        HTTPException: If the provided credentials are incorrect.
        HTTPException: If the provided credentials are missing or invalid.
    """
    # Define the correct username and password
    correct_username = "admin"
    correct_password = "password"
    
    # Check if the provided credentials match the correct ones
    if credentials.username == correct_username and credentials.password == correct_password:
        return True
    else:
        # Raise an HTTPException with status code 401 if the credentials are incorrect
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
def jwt_auth_middleware(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Middleware function for JWT authentication.

    This function checks if the provided JWT token is valid.
    It decodes the token and returns the payload if valid.
    
    Args:
        credentials (HTTPAuthorizationCredentials): The HTTP bearer token credentials.

    Returns:
        dict: The decoded token payload.

    Raises:
        HTTPException: If the token is missing or invalid.
    """
    token = credentials.credentials
    ALGORITHM = "HS256"
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    try:
        # Validate the token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Return the payload to be used in the route
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e
    
    
async def loggingMiddleware(request: Request, call_next: callable) -> Response:
    """Middleware for logging HTTP requests and responses.

    Args:
        request (Request): The incoming HTTP request.
        call_next (callable): The next middleware or endpoint function to call.

    Returns:
        Response: The HTTP response returned by the next middleware or endpoint function.
    """
    start_time = time.perf_counter()
    
    # Call the next middleware or endpoint function
    response: Response = await call_next(request)
    resp_body = [section async for section in response.__dict__["body_iterator"]]

    try:
        resp_body = json.loads(resp_body[0].decode())
    except:
        resp_body = str(resp_body)
    
    finish_time = time.perf_counter()
    execution_time = finish_time - start_time

    overall_status = "successful" if response.status_code < 400 else "failed"
    
    request_log = {
        "path": request.url.path,
        "method": request.method,
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "body": await request.body(),
        "cookies": request.cookies,
    }
    
    response_log = {
        "status": overall_status,
        "status_code": response.status_code,
        "time_taken": f"{execution_time:0.4f}s",
        "response_body": resp_body,
    }
    
    api_log = {
        "request_log": request_log,
        "response_log": response_log
    }
    
    # Log the API request and response
    _logger.info("API log: %s", api_log)
    
    return response
