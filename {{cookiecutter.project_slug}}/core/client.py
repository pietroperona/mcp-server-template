"""
HTTP Client for {{cookiecutter.project_name}}
Generic {{cookiecutter.api_service_type}} API client with rate limiting and error handling
Auto-generated from mcp-server-template
"""
import asyncio
import time
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import aiohttp
import httpx
{% if cookiecutter.include_rate_limiting == "yes" -%}
from asyncio import Semaphore
{% endif -%}

from .config import config
from .auth import auth


{% if cookiecutter.include_rate_limiting == "yes" -%}
class RateLimiter:
    """
    Rate limiter for API requests
    
    Implements token bucket algorithm to respect API rate limits.
    """
    
    def __init__(self, max_requests: int, time_window: int):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests allowed in time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.semaphore = Semaphore(max_requests)
        self.requests = []
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Wait for rate limit slot to be available"""
        async with self._lock:
            now = time.time()
            
            # Remove old requests outside the time window
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < self.time_window]
            
            # If we're at the limit, wait
            if len(self.requests) >= self.max_requests:
                sleep_time = self.time_window - (now - self.requests[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    return await self.acquire()
            
            # Record this request
            self.requests.append(now)
{% endif -%}


class {{cookiecutter.project_slug|title|replace("-", "")}}Client:
    """
    HTTP client for {{cookiecutter.api_service_type}} API integration
    
    Features:
    - Automatic authentication header injection
    - Rate limiting (configurable)
    - Retry logic with exponential backoff
    - Request/response logging
    - Error handling and custom exceptions
    - Support for both aiohttp and httpx
    
    Example:
        >>> client = {{cookiecutter.project_slug|title|replace("-", "")}}Client()
        >>> data = await client.get("/users/123")
        >>> result = await client.post("/users", {"name": "John"})
    """
    
    def __init__(self):
        self.base_url = config.api.full_api_url
        self.timeout = config.api.timeout
{% if cookiecutter.include_rate_limiting == "yes" -%}
        self.rate_limiter = RateLimiter(
            config.api.rate_limit_requests,
            config.api.rate_limit_window
        )
{% endif -%}
        self._session: Optional[aiohttp.ClientSession] = None
        self._httpx_client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup sessions"""
        await self.close()
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    async def _get_httpx_client(self) -> httpx.AsyncClient:
        """Get or create httpx client"""
        if self._httpx_client is None:
            self._httpx_client = httpx.AsyncClient(timeout=self.timeout)
        return self._httpx_client
    
    async def close(self):
        """Close all HTTP sessions"""
        if self._session and not self._session.closed:
            await self._session.close()
        if self._httpx_client:
            await self._httpx_client.aclose()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        data: Optional[Union[Dict, str, bytes]] = None,
        headers: Optional[Dict] = None,
        use_httpx: bool = False,
        **kwargs
    ) -> Dict[Any, Any]:
        """
        Make HTTP request with authentication, rate limiting, and retry logic
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (e.g., "/users" or "/users/123")
            params: URL parameters
            json_data: JSON payload for request body
            data: Raw data for request body
            headers: Additional headers
            use_httpx: Use httpx instead of aiohttp
            **kwargs: Additional arguments passed to the HTTP client
        
        Returns:
            Dict: JSON response from API
            
        Raises:
            APIError: If API returns error response
            RateLimitError: If rate limit exceeded
            TimeoutError: If request times out
            ConnectionError: If connection fails
        """
{% if cookiecutter.include_rate_limiting == "yes" -%}
        # Wait for rate limit slot
        await self.rate_limiter.acquire()
{% endif -%}
        
        # Prepare URL
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Get authentication headers
        auth_headers = await auth.get_auth_headers()
        
        # Merge headers
        final_headers = {**auth_headers}
        if headers:
            final_headers.update(headers)
        
        # Log request
        if config.mcp.debug:
            print(f"🌐 {method} {url}")
            if params:
                print(f"📝 Params: {params}")
            if json_data:
                print(f"📝 JSON: {json.dumps(json_data, indent=2)}")
        
        # Retry logic
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries + 1):
            try:
                if use_httpx:
                    response_data = await self._make_httpx_request(
                        method, url, params, json_data, data, final_headers, **kwargs
                    )
                else:
                    response_data = await self._make_aiohttp_request(
                        method, url, params, json_data, data, final_headers, **kwargs
                    )
                
                # Log successful response
                if config.mcp.debug:
                    print(f"✅ Response received ({len(str(response_data))} chars)")
                
                return response_data
                
            except (aiohttp.ClientError, httpx.RequestError, asyncio.TimeoutError) as e:
                if attempt == max_retries:
                    raise ConnectionError(f"Request failed after {max_retries + 1} attempts: {e}")
                
                # Exponential backoff
                delay = base_delay * (2 ** attempt)
                print(f"⚠️ Request failed (attempt {attempt + 1}/{max_retries + 1}), retrying in {delay}s: {e}")
                await asyncio.sleep(delay)
    
    async def _make_aiohttp_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict],
        json_data: Optional[Dict],
        data: Optional[Union[Dict, str, bytes]],
        headers: Dict[str, str],
        **kwargs
    ) -> Dict[Any, Any]:
        """Make request using aiohttp"""
        session = await self._get_session()
        
        async with session.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            data=data,
            headers=headers,
            **kwargs
        ) as response:
            
            # Handle different response types
            content_type = response.headers.get("Content-Type", "")
            
            if response.status >= 400:
                error_text = await response.text()
                raise APIError(
                    f"API error {response.status}: {error_text}",
                    status_code=response.status,
                    response_text=error_text
                )
            
            if "application/json" in content_type:
                return await response.json()
            else:
                text_content = await response.text()
                return {"content": text_content, "content_type": content_type}
    
    async def _make_httpx_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict],
        json_data: Optional[Dict],
        data: Optional[Union[Dict, str, bytes]],
        headers: Dict[str, str],
        **kwargs
    ) -> Dict[Any, Any]:
        """Make request using httpx"""
        client = await self._get_httpx_client()
        
        response = await client.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            data=data,
            headers=headers,
            **kwargs
        )
        
        if response.status_code >= 400:
            raise APIError(
                f"API error {response.status_code}: {response.text}",
                status_code=response.status_code,
                response_text=response.text
            )
        
        try:
            return response.json()
        except ValueError:
            return {"content": response.text, "content_type": response.headers.get("content-type")}
    
    # ===================================
    # �� CONVENIENCE METHODS
    # ===================================
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> Dict[Any, Any]:
        """
        Make GET request
        
        Args:
            endpoint: API endpoint
            params: URL parameters
            headers: Additional headers
        
        Returns:
            Dict: JSON response
        """
        return await self._make_request("GET", endpoint, params=params, headers=headers, **kwargs)
    
    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict] = None,
        data: Optional[Union[Dict, str, bytes]] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> Dict[Any, Any]:
        """
        Make POST request
        
        Args:
            endpoint: API endpoint
            json_data: JSON payload
            data: Raw data payload
            params: URL parameters
            headers: Additional headers
        
        Returns:
            Dict: JSON response
        """
        return await self._make_request(
            "POST", endpoint, params=params, json_data=json_data, data=data, headers=headers, **kwargs
        )
    
    async def put(
        self,
        endpoint: str,
        json_data: Optional[Dict] = None,
        data: Optional[Union[Dict, str, bytes]] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> Dict[Any, Any]:
        """Make PUT request"""
        return await self._make_request(
            "PUT", endpoint, params=params, json_data=json_data, data=data, headers=headers, **kwargs
        )
    
    async def patch(
        self,
        endpoint: str,
        json_data: Optional[Dict] = None,
        data: Optional[Union[Dict, str, bytes]] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> Dict[Any, Any]:
        """Make PATCH request"""
        return await self._make_request(
            "PATCH", endpoint, params=params, json_data=json_data, data=data, headers=headers, **kwargs
        )
    
    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> Dict[Any, Any]:
        """Make DELETE request"""
        return await self._make_request("DELETE", endpoint, params=params, headers=headers, **kwargs)
    
    # ===================================
    # 🔍 UTILITY METHODS
    # ===================================
    
    async def health_check(self) -> bool:
        """
        Check if API is accessible and responding
        
        Returns:
            bool: True if API is healthy
        """
        try:
            # Try a simple endpoint - adjust based on your API
            endpoints_to_try = [
                "/health",
                "/status", 
                "/ping",
                "/",
                "/api/health",
                "/v1/health"
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    response = await self.get(endpoint)
                    print(f"✅ Health check passed: {endpoint}")
                    return True
                except APIError as e:
                    if e.status_code == 404:
                        continue  # Try next endpoint
                    return False
                except Exception:
                    continue  # Try next endpoint
            
            print("⚠️ No health endpoint found, but authentication is working")
            return True
            
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    async def get_api_info(self) -> Dict[str, Any]:
        """
        Get API information and capabilities
        
        Returns:
            Dict: API information
        """
        info = {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "auth_type": "{{cookiecutter.auth_type}}",
{% if cookiecutter.include_rate_limiting == "yes" -%}
            "rate_limiting": {
                "enabled": True,
                "max_requests": config.api.rate_limit_requests,
                "time_window": config.api.rate_limit_window
            },
{% else -%}
            "rate_limiting": {"enabled": False},
{% endif -%}
            "client_info": {
                "user_agent": f"{{cookiecutter.project_name}}/{{cookiecutter.project_version}}",
                "session_active": self._session is not None and not self._session.closed,
                "httpx_client_active": self._httpx_client is not None
            }
        }
        
        return info


# ===================================
# 🚨 CUSTOM EXCEPTIONS
# ===================================

class APIError(Exception):
    """Raised when API returns an error response"""
    
    def __init__(self, message: str, status_code: int = None, response_text: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class RateLimitError(Exception):
    """Raised when rate limit is exceeded"""
    pass


class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass


# ===================================
# 🌍 GLOBAL CLIENT INSTANCE
# ===================================
client = {{cookiecutter.project_slug|title|replace("-", "")}}Client()


# ===================================
# 🧪 CLIENT TESTING
# ===================================
async def test_client():
    """
    Test client functionality and API connectivity
    
    This function can be called during development to verify
    that the HTTP client is working correctly.
    """
    print(f"🌐 Testing {{cookiecutter.api_service_type}} client...")
    print(f"📊 Client info: {await client.get_api_info()}")
    
    try:
        # Test authentication
        auth_headers = await auth.get_auth_headers()
        print(f"✅ Authentication headers generated")
        
        # Test basic connectivity
        is_healthy = await client.health_check()
        if is_healthy:
            print(f"✅ API connectivity verified")
        else:
            print(f"⚠️ API health check failed - check your configuration")
        
        return True
        
    except Exception as e:
        print(f"❌ Client test failed: {e}")
        return False
    finally:
        await client.close()


if __name__ == "__main__":
    # Allow running client module directly for testing
    import asyncio
    asyncio.run(test_client())
