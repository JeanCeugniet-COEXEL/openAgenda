import os
import time
from fastapi import Security, HTTPException, Depends, Request
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_429_TOO_MANY_REQUESTS
from dotenv import load_dotenv
from typing import Dict, List, Tuple

# Load environment variables
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "X-API-Key"

# Create API key header dependency
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Rate limiting settings
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))  # Number of requests
RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # Period in seconds

# Store for rate limiting (in-memory for simplicity)
# In production, consider using Redis or another distributed cache
rate_limit_store: Dict[str, List[float]] = {}

async def get_api_key(api_key_header: str = Security(api_key_header)):
    """
    Validate API key from request header
    """
    if not API_KEY:
        # If API_KEY is not set in environment, disable authentication (for development)
        return True
    
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Invalid API Key"
        )

async def rate_limit(request: Request, api_key: str = Depends(get_api_key)):
    """
    Rate limiting middleware
    """
    if not RATE_LIMIT_ENABLED:
        return api_key
    
    # Use client IP as identifier if no API key
    identifier = api_key if isinstance(api_key, str) else request.client.host
    
    # Get current time
    current_time = time.time()
    
    # Initialize or get request timestamps for this identifier
    if identifier not in rate_limit_store:
        rate_limit_store[identifier] = []
    
    # Remove timestamps outside the current period
    rate_limit_store[identifier] = [
        timestamp for timestamp in rate_limit_store[identifier]
        if current_time - timestamp < RATE_LIMIT_PERIOD
    ]
    
    # Check if rate limit exceeded
    if len(rate_limit_store[identifier]) >= RATE_LIMIT_REQUESTS:
        # Calculate time until next request is allowed
        oldest_timestamp = min(rate_limit_store[identifier])
        retry_after = int(RATE_LIMIT_PERIOD - (current_time - oldest_timestamp))
        
        raise HTTPException(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)}
        )
    
    # Add current request timestamp
    rate_limit_store[identifier].append(current_time)
    
    return api_key 