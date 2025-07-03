import asyncio
import sys
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta
import aiohttp
{%- if cookiecutter.auth_type == "OAuth2" %}
from urllib.parse import urlencode
{%- endif %}
{%- if cookiecutter.auth_type == "Basic Auth" %}
import base64
{%- endif %}

# Fix import path for direct execution
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.config import config


class {{cookiecutter.project_slug|title|replace("-", "")}}Auth:
    """
    pass
    Authentication handler for {{cookiecutter.api_service_type}} API
    
    Supports {{cookiecutter.auth_type}} authentication pattern.
    """
    
    def __init__(self):
{%- if cookiecutter.auth_type == "Bearer Token" or cookiecutter.auth_type == "OAuth2" %}
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
{%- endif %}
{%- if cookiecutter.auth_type == "OAuth2" %}
        self.refresh_token: Optional[str] = None
{%- endif %}
        self._lock = asyncio.Lock()
    
    async def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        async with self._lock:
{%- if cookiecutter.auth_type == "API Key" %}
            return await self._get_api_key_headers()
{%- elif cookiecutter.auth_type == "Bearer Token" %}
            return await self._get_bearer_token_headers()
{%- elif cookiecutter.auth_type == "OAuth2" %}
            return await self._get_oauth2_headers()
{%- elif cookiecutter.auth_type == "Basic Auth" %}
            return await self._get_basic_auth_headers()
{%- else %}
            return {"Authorization": "Custom Auth"}
{%- endif %}

{%- if cookiecutter.auth_type == "API Key" %}
    async def _get_api_key_headers(self) -> Dict[str, str]:
        """Generate API Key authentication headers"""
        if not config.api.api_key:
            raise ValueError("API key not configured. Please set API_KEY environment variable.")
        
        return {
            config.api.api_key_header: config.api.api_key,
            "Content-Type": "application/json",
            "User-Agent": f"{{cookiecutter.project_name}}/{{cookiecutter.project_version}}"
        }
{%- endif %}

{%- if cookiecutter.auth_type == "Bearer Token" %}
    async def _get_bearer_token_headers(self) -> Dict[str, str]:
        """Generate Bearer Token authentication headers"""
        if not self._is_token_valid():
            await self._refresh_bearer_token()
        
        if not self.access_token:
            raise ValueError("Bearer token not available. Please check your configuration.")
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "User-Agent": f"{{cookiecutter.project_name}}/{{cookiecutter.project_version}}"
        }
    
    def _is_token_valid(self) -> bool:
        """Check if current token is valid and not expiring soon"""
        if not self.access_token or not self.token_expires_at:
            return False
        
        buffer_time = timedelta(minutes=5)
        return datetime.now() < (self.token_expires_at - buffer_time)
    
    async def _refresh_bearer_token(self) -> None:
        """Refresh the bearer token"""
        if config.api.bearer_token:
            self.access_token = config.api.bearer_token
            self.token_expires_at = datetime.now() + timedelta(days=365)
        else:
            raise ValueError("Bearer token not configured. Please set BEARER_TOKEN environment variable.")
{%- endif %}

{%- if cookiecutter.auth_type == "Basic Auth" %}
    async def _get_basic_auth_headers(self) -> Dict[str, str]:
        """Generate Basic Authentication headers"""
        if not config.api.username or not config.api.password:
            raise ValueError("Username and password not configured. Please set USERNAME and PASSWORD environment variables.")
        
        credentials = f"{config.api.username}:{config.api.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        return {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
            "User-Agent": f"{{cookiecutter.project_name}}/{{cookiecutter.project_version}}"
        }
{%- endif %}

{%- if cookiecutter.auth_type == "OAuth2" %}
    async def _get_oauth2_headers(self) -> Dict[str, str]:
        """Generate OAuth2 authentication headers"""
        if not self._is_token_valid():
            await self._refresh_oauth2_token()
        
        if not self.access_token:
            raise ValueError("OAuth2 access token not available. Please complete OAuth2 flow.")
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "User-Agent": f"{{cookiecutter.project_name}}/{{cookiecutter.project_version}}"
        }
    
    def _is_token_valid(self) -> bool:
        """Check if current OAuth2 token is valid and not expiring soon"""
        if not self.access_token or not self.token_expires_at:
            return False
        
        buffer_time = timedelta(minutes=5)
        return datetime.now() < (self.token_expires_at - buffer_time)
    
    async def _refresh_oauth2_token(self) -> None:
        """Refresh OAuth2 access token using refresh token"""
        if not self.refresh_token:
            raise ValueError("No refresh token available. Please re-authenticate.")
        
        token_url = f"{config.api.base_url}/oauth/token"
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": config.api.client_id,
            "client_secret": config.api.client_secret
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(token_url, data=data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        
                        self.access_token = token_data["access_token"]
                        expires_in = token_data.get("expires_in", 3600)
                        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                        
                        if "refresh_token" in token_data:
                            self.refresh_token = token_data["refresh_token"]
                        
                        print(f"✅ OAuth2 token refreshed successfully")
                        
                    else:
                        error_text = await response.text()
                        raise Exception(f"OAuth2 token refresh failed: {response.status} - {error_text}")
                        
            except aiohttp.ClientError as e:
                raise Exception(f"Network error during OAuth2 token refresh: {str(e)}")
{%- endif %}
    
    async def validate_auth(self) -> bool:
        """Validate current authentication status"""
        try:
            headers = await self.get_auth_headers()
            
            # Simple connectivity test
            test_url = f"{config.api.base_url}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(test_url, headers=headers, timeout=10) as response:
                    return response.status < 400
                    
        except Exception as e:
            print(f"❌ Authentication validation failed: {e}")
            return False
    
    def get_auth_info(self) -> Dict[str, any]:
        """Get non-sensitive authentication information for debugging"""
        info = {
            "auth_type": "{{cookiecutter.auth_type}}",
            "api_base_url": config.api.base_url,
        }
        
{%- if cookiecutter.auth_type == "API Key" %}
        info.update({
            "api_key_configured": bool(config.api.api_key),
            "api_key_header": config.api.api_key_header
        })
{%- elif cookiecutter.auth_type == "Bearer Token" %}
        info.update({
            "token_configured": bool(self.access_token),
            "token_valid": self._is_token_valid(),
            "expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None
        })
{%- elif cookiecutter.auth_type == "OAuth2" %}
        info.update({
            "access_token_configured": bool(self.access_token),
            "refresh_token_configured": bool(self.refresh_token),
            "token_valid": self._is_token_valid(),
            "expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
            "client_id": config.api.client_id[:8] + "..." if config.api.client_id else None
        })
{%- elif cookiecutter.auth_type == "Basic Auth" %}
        info.update({
            "username_configured": bool(config.api.username),
            "password_configured": bool(config.api.password)
        })
{%- endif %}
        
        return info


# Global authentication instance
auth = {{cookiecutter.project_slug|title|replace("-", "")}}Auth()


async def test_authentication():
    """Test authentication setup and connectivity"""
    print(f"🔐 Testing {{cookiecutter.auth_type}} authentication...")
    print(f"📊 Auth info: {auth.get_auth_info()}")
    
    try:
        headers = await auth.get_auth_headers()
        print(f"✅ Authentication headers generated successfully")
        
        is_valid = await auth.validate_auth()
        if is_valid:
            print(f"✅ Authentication validation passed")
        else:
            print(f"⚠️ Authentication validation failed - check your credentials")
            
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_authentication())