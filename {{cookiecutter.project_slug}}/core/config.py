"""
Configuration management for {{cookiecutter.project_name}}
Auto-generated from mcp-server-template
"""

import os

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class APIConfig(BaseSettings):
    """{{cookiecutter.api_service_type}} API configuration"""

    # API Connection Settings
    base_url: str = Field(env="API_BASE_URL", description="Base URL for the API")
    version: str = Field(default="v1", env="API_VERSION", description="API version")
    timeout: int = Field(
        default=30, env="API_TIMEOUT", description="Request timeout in seconds"
    )

    # Authentication Configuration
    # Fields depend on the selected authentication type
    auth_type: str = "{{cookiecutter.auth_type}}"

    # API Key Authentication
    api_key: str = Field(
        default="", env="API_KEY", description="API key for authentication"
    )
    api_key_header: str = Field(
        default="X-API-Key", env="API_KEY_HEADER", description="Header name for API key"
    )

    # Bearer Token Authentication
    bearer_token: str = Field(
        default="", env="BEARER_TOKEN", description="Bearer token for authentication"
    )

    # OAuth2 Authentication
    client_id: str = Field(default="", env="CLIENT_ID", description="OAuth2 client ID")
    client_secret: str = Field(
        default="", env="CLIENT_SECRET", description="OAuth2 client secret"
    )
    oauth_scope: str = Field(
        default="read,write", env="OAUTH_SCOPE", description="OAuth2 scope"
    )
    redirect_uri: str = Field(
        default="http://localhost:8080/callback",
        env="OAUTH_REDIRECT_URI",
        description="OAuth2 redirect URI",
    )

    # Basic Auth Authentication
    username: str = Field(
        default="", env="USERNAME", description="Username for basic authentication"
    )
    password: str = Field(
        default="", env="PASSWORD", description="Password for basic authentication"
    )

    # Rate Limiting Configuration (if enabled)
    include_rate_limiting: bool = {{cookiecutter.include_rate_limiting == "yes"}}
    rate_limit_requests: int = Field(
        default=100,
        env="RATE_LIMIT_REQUESTS",
        description="Max requests per time window",
    )
    rate_limit_window: int = Field(
        default=3600,
        env="RATE_LIMIT_WINDOW",
        description="Rate limit time window in seconds",
    )

    @property
    def full_api_url(self) -> str:
        """Get the complete API URL"""
        if self.version and self.version.lower() != "none":
            return f"{self.base_url.rstrip('/')}/{self.version}"
        return self.base_url.rstrip("/")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # Ignore extra environment variables
        "validate_assignment": True,
    }


class MCPConfig(BaseSettings):
    """MCP Server configuration"""

    server_name: str = Field(
        default="{{cookiecutter.project_slug}}", env="MCP_SERVER_NAME"
    )
    server_version: str = Field(
        default="{{cookiecutter.project_version}}", env="MCP_SERVER_VERSION"
    )
    host: str = Field(default="0.0.0.0", env="MCP_HOST")
    port: int = Field(default=8000, env="MCP_PORT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    environment: str = Field(default="development", env="ENVIRONMENT")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


# Cache config class
class CacheConfig(BaseSettings):
    """Caching configuration"""

    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    cache_ttl: int = Field(default=300, env="CACHE_TTL")

    model_config = {"env_file": ".env", "extra": "ignore"}


class AppConfig:
    """Main application configuration container"""

    def __init__(self):
        self.api = APIConfig()
        self.mcp = MCPConfig()

        # Initialize cache if enabled
        include_caching = {{cookiecutter.include_caching == "yes"}}
        if include_caching:
            self.cache = CacheConfig()

    def validate(self) -> bool:
        """Validate all configuration settings"""
        missing_settings = []

        # Check required API settings based on auth type
        auth_type = "{{cookiecutter.auth_type}}"

        if auth_type == "API Key":
            if not self.api.api_key:
                missing_settings.append("API_KEY")
        elif auth_type == "Bearer Token":
            if not self.api.bearer_token:
                missing_settings.append("BEARER_TOKEN")
        elif auth_type == "OAuth2":
            if not self.api.client_id:
                missing_settings.append("CLIENT_ID")
            if not self.api.client_secret:
                missing_settings.append("CLIENT_SECRET")
        elif auth_type == "Basic Auth":
            if not self.api.username:
                missing_settings.append("USERNAME")
            if not self.api.password:
                missing_settings.append("PASSWORD")

        if not self.api.base_url:
            missing_settings.append("API_BASE_URL")

        if missing_settings:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_settings)}"
            )

        return True

    def get_debug_info(self) -> dict:
        """Get non-sensitive configuration info for debugging"""
        include_rate_limiting = {{cookiecutter.include_rate_limiting == "yes"}}

        info = {
            "server_name": self.mcp.server_name,
            "server_version": self.mcp.server_version,
            "api_base_url": self.api.base_url,
            "environment": self.mcp.environment,
            "debug_mode": self.mcp.debug,
            "rate_limiting_enabled": include_rate_limiting,
        }

        # Add rate limiting info if enabled
        if include_rate_limiting:
            info["rate_limit"] = (
                f"{self.api.rate_limit_requests} requests per {self.api.rate_limit_window}s"
            )

        return info


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
