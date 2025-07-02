"""
HTTP Client for {{cookiecutter.project_name}}
Generic {{cookiecutter.api_service_type}} API client with rate limiting and error handling
Auto-generated from mcp-server-template
"""
import asyncio
import sys
from pathlib import Path
import time
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import aiohttp
{% if cookiecutter.include_rate_limiting == "yes" -%}
from asyncio import Semaphore
{% endif -%}

# Fix import path for direct execution
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.config import config
from core.auth import auth


{% if cookiecutter.include_rate_limiting == "yes" -%}
class RateLimiter:
    """Rate limiter for API requests using token bucket algorithm"""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
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
    
    async def close(self):
        """Close all HTTP sessions"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        data: Optional[Union[Dict, str, bytes]] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> Dict[Any, Any]:
        """Make HTTP request with authentication, rate limiting, and retry logic"""
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
                session = await self._get_session()
                
                async with session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    data=data,
                    headers=final_headers,
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
                        result = await response.json()
                    else:
                        text_content = await response.text()
                        result = {"content": text_content, "content_type": content_type}
                    
                    # Log successful response
                    if config.mcp.debug:
                        print(f"✅ Response received ({len(str(result))} chars)")
                    
                    return result
                
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == max_retries:
                    raise ConnectionError(f"Request failed after {max_retries + 1} attempts: {e}")
                
                # Exponential backoff
                delay = base_delay * (2 ** attempt)
                print(f"⚠️ Request failed (attempt {attempt + 1}/{max_retries + 1}), retrying in {delay}s: {e}")
                await asyncio.sleep(delay)
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> Dict[Any, Any]:
        """Make GET request"""
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
        """Make POST request"""
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
    
    async def health_check(self) -> bool:
        """Check if API is accessible and responding"""
        try:
            # Try common health check endpoints
            endpoints_to_try = [
                "/health",
                "/status", 
                "/ping",
                "/",
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
        """Get API information and capabilities"""
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
                "session_active": self._session is not None and not self._session.closed
            }
        }
        
        return info


# Custom Exceptions
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


# Global client instance
client = {{cookiecutter.project_slug|title|replace("-", "")}}Client()


async def test_client():
    """Test client functionality and API connectivity"""
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
    import asyncio
    asyncio.run(test_client())