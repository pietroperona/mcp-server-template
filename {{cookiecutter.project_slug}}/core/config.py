"""
Configuration management for {{cookiecutter.project_name}}
Auto-generated from mcp-server-template
"""
import os
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class APIConfig(BaseSettings):
    """{{cookiecutter.api_service_type}} API configuration"""
    
    # API Connection Settings
    base_url: str = Field(env="API_BASE_URL", description="Base URL for the API")
    version: str = Field(default="v1", env="API_VERSION", description="API version")
    timeout: int = Field(default=30, env="API_TIMEOUT", description="Request timeout in seconds")
    
    # Authentication Configuration
{% if cookiecutter.auth_type == "API Key" -%}
    api_key: str = Field(env="API_KEY", description="API key for authentication")
    api_key_header: str = Field(default="X-API-Key", env="API_KEY_HEADER", description="Header name for API key")
{% elif cookiecutter.auth_type == "Bearer Token" -%}
    bearer_token: str = Field(env="BEARER_TOKEN", description="Bearer token for authentication")
{% elif cookiecutter.auth_type == "OAuth2" -%}
    client_id: str = Field(env="CLIENT_ID", description="OAuth2 client ID")
    client_secret: str = Field(env="CLIENT_SECRET", description="OAuth2 client secret")
    oauth_scope: str = Field(default="read,write", env="OAUTH_SCOPE", description="OAuth2 scope")
    redirect_uri: str = Field(default="http://localhost:8080/callback", env="OAUTH_REDIRECT_URI", description="OAuth2 redirect URI")
{% elif cookiecutter.auth_type == "Basic Auth" -%}
    username: str = Field(env="USERNAME", description="Username for basic authentication")
    password: str = Field(env="PASSWORD", description="Password for basic authentication")
{% endif -%}
    
{% if cookiecutter.include_rate_limiting == "yes" -%}
    # Rate Limiting Configuration
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS", description="Max requests per time window")
    rate_limit_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW", description="Rate limit time window in seconds")
{% endif -%}
    
    @property
    def full_api_url(self) -> str:
        """Get the complete API URL"""
        if self.version and self.version.lower() != "none":
            return f"{self.base_url.rstrip('/')}/{self.version}"
        return self.base_url.rstrip('/')
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # Ignore extra environment variables
        "validate_assignment": True
    }

class MCPConfig(BaseSettings):
    """MCP Server configuration"""
    
    server_name: str = Field(default="{{cookiecutter.project_slug}}", env="MCP_SERVER_NAME")
    server_version: str = Field(default="{{cookiecutter.project_version}}", env="MCP_SERVER_VERSION")
    host: str = Field(default="0.0.0.0", env="MCP_HOST")
    port: int = Field(default=8000, env="MCP_PORT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

{% if cookiecutter.include_caching == "yes" -%}
class CacheConfig(BaseSettings):
    """Caching configuration"""
    
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    cache_ttl: int = Field(default=300, env="CACHE_TTL")
    
    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }
{% endif -%}

class AppConfig:
    """Main application configuration container"""
    
    def __init__(self):
        self.api = APIConfig()
        self.mcp = MCPConfig()
{% if cookiecutter.include_caching == "yes" -%}
        self.cache = CacheConfig()
{% endif -%}
    
    def validate(self) -> bool:
        """Validate all configuration settings"""
        missing_settings = []
        
        # Check required API settings
{% if cookiecutter.auth_type == "API Key" -%}
        if not self.api.api_key:
            missing_settings.append("API_KEY")
{% elif cookiecutter.auth_type == "Bearer Token" -%}
        if not self.api.bearer_token:
            missing_settings.append("BEARER_TOKEN")
{% elif cookiecutter.auth_type == "OAuth2" -%}
        if not self.api.client_id:
            missing_settings.append("CLIENT_ID")
        if not self.api.client_secret:
            missing_settings.append("CLIENT_SECRET")
{% elif cookiecutter.auth_type == "Basic Auth" -%}
        if not self.api.username:
            missing_settings.append("USERNAME")
        if not self.api.password:
            missing_settings.append("PASSWORD")
{% endif -%}
        
        if not self.api.base_url:
            missing_settings.append("API_BASE_URL")
        
        if missing_settings:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_settings)}")
        
        return True
    
    def get_debug_info(self) -> dict:
        """Get non-sensitive configuration info for debugging"""
        return {
            "server_name": self.mcp.server_name,
            "server_version": self.mcp.server_version,
            "api_base_url": self.api.base_url,
            "environment": self.mcp.environment,
            "debug_mode": self.mcp.debug,
{% if cookiecutter.include_rate_limiting == "yes" -%}
            "rate_limiting_enabled": True,
            "rate_limit": f"{self.api.rate_limit_requests} requests per {self.api.rate_limit_window}s",
{% else -%}
            "rate_limiting_enabled": False,
{% endif -%}
        }

# Global configuration instance
config = AppConfig()

# Auto-validate on import in development
if os.getenv("ENVIRONMENT", "development") == "development":
    try:
        config.validate()
        if config.mcp.debug:
            print("✅ Configuration validation passed")
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        print("💡 Check your .env file and environment variables")