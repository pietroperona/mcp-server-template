# ⚙️ Configuration Guide

Complete configuration reference for {{cookiecutter.project_name}}.

## 📋 Environment Variables

All configuration is done through environment variables. Copy `.env.example` to `.env` and customize.

### 🔐 Authentication Configuration

{% if cookiecutter.auth_type == "API Key" -%}
#### API Key Authentication

```bash
# Required: Your API key
API_KEY=your_api_key_here

# Optional: Custom header name (default: X-API-Key)
API_KEY_HEADER=X-API-Key
```

**Where to find your API key:**
- Check your API provider's dashboard
- Look for "API Keys", "Developer", or "Integration" sections
- Generate a new key if needed

{% elif cookiecutter.auth_type == "Bearer Token" -%}
#### Bearer Token Authentication

```bash
# Required: Your bearer token
BEARER_TOKEN=your_bearer_token_here
```

**Token format:**
- Usually starts with `Bearer ` or just the token
- May be a JWT token
- Check your API documentation for format

{% elif cookiecutter.auth_type == "OAuth2" -%}
#### OAuth2 Authentication

```bash
# Required: OAuth2 client credentials
CLIENT_ID=your_oauth_client_id
CLIENT_SECRET=your_oauth_client_secret

# Optional: OAuth2 configuration
OAUTH_SCOPE=read,write
OAUTH_REDIRECT_URI=http://localhost:8080/callback
```

**OAuth2 Setup:**
1. Register your application with the API provider
2. Get client ID and secret
3. Configure redirect URI
4. Set appropriate scopes

{% elif cookiecutter.auth_type == "Basic Auth" -%}
#### Basic Authentication

```bash
# Required: Username and password
USERNAME=your_api_username
PASSWORD=your_api_password
```

**Credentials:**
- Use your API account username/password
- Some APIs use email as username
- Check if you need a separate API account

{% endif -%}

### 🌐 API Configuration

```bash
# Required: Base URL of your API
API_BASE_URL=https://api.example.com

# Optional: API version (default: v1)
API_VERSION=v1

# Optional: Request timeout in seconds (default: 30)
API_TIMEOUT=30
```

**API Base URL Examples:**
- REST API: `https://api.example.com`
- GraphQL: `https://api.example.com/graphql`
- Custom: `https://company.example.com/api`

### 🚀 MCP Server Configuration

```bash
# Optional: Server configuration
MCP_SERVER_NAME={{cookiecutter.project_slug}}
MCP_SERVER_VERSION={{cookiecutter.project_version}}
MCP_HOST=0.0.0.0
MCP_PORT=8000

# Optional: Environment settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

**Environment Values:**
- `development` - Local development with debug features
- `staging` - Pre-production testing
- `production` - Live deployment

**Log Levels:**
- `DEBUG` - Detailed debugging info
- `INFO` - General information
- `WARNING` - Warning messages only
- `ERROR` - Error messages only

{% if cookiecutter.include_rate_limiting == "yes" -%}
### ⚡ Rate Limiting Configuration

```bash
# Optional: Rate limiting settings
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

**Rate Limiting Explained:**
- `RATE_LIMIT_REQUESTS` - Maximum requests allowed
- `RATE_LIMIT_WINDOW` - Time window in seconds
- Example: 100 requests per 3600 seconds (1 hour)

**Recommended Settings:**
- **Conservative**: 50 requests per hour
- **Standard**: 100 requests per hour
- **Aggressive**: 500 requests per hour

{% endif -%}

{% if cookiecutter.include_caching == "yes" -%}
### 💾 Caching Configuration

```bash
# Optional: Redis caching
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300
```

**Caching Options:**
- `REDIS_URL` - Redis connection string
- `CACHE_TTL` - Cache time-to-live in seconds

**Redis URL Formats:**
- Local: `redis://localhost:6379/0`
- Remote: `redis://user:pass@host:port/db`
- Secure: `rediss://host:port/db`

{% endif -%}

## 🔧 Advanced Configuration

### Custom Headers

Add custom headers to all API requests:

```python
# In core/client.py, modify _make_request method
custom_headers = {
    "User-Agent": "{{cookiecutter.project_name}}/{{cookiecutter.project_version}}",
    "Accept": "application/json",
    "Custom-Header": "custom-value"
}
```

### Request Retry Configuration

Modify retry behavior in `core/client.py`:

```python
# Retry settings
max_retries = 3           # Number of retry attempts
base_delay = 1.0          # Initial delay between retries
backoff_multiplier = 2    # Exponential backoff multiplier
```

### Timeout Configuration

Configure different timeouts for different operations:

```python
# In core/client.py
timeouts = {
    "connect": 5,      # Connection timeout
    "read": 30,        # Read timeout
    "total": 60        # Total timeout
}
```

## 🏗️ Configuration Validation

The server validates configuration on startup:

### Required Variables Check

```python
# These variables are required and checked:
{% if cookiecutter.auth_type == "API Key" -%}
- API_KEY
{% elif cookiecutter.auth_type == "Bearer Token" -%}
- BEARER_TOKEN
{% elif cookiecutter.auth_type == "OAuth2" -%}
- CLIENT_ID
- CLIENT_SECRET
{% elif cookiecutter.auth_type == "Basic Auth" -%}
- USERNAME
- PASSWORD
{% endif -%}
- API_BASE_URL
```

### Validation Rules

- **API_BASE_URL** must start with `http://` or `https://`
- **Timeouts** must be positive integers
- **Rate limits** must be positive integers
- **Authentication** credentials must not be empty

## 🌍 Environment-Specific Configuration

### Development Environment

```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
API_TIMEOUT=60
{% if cookiecutter.include_rate_limiting == "yes" -%}
RATE_LIMIT_REQUESTS=1000
{% endif -%}
```

### Production Environment

```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
API_TIMEOUT=30
{% if cookiecutter.include_rate_limiting == "yes" -%}
RATE_LIMIT_REQUESTS=100
{% endif -%}
```

### Testing Environment

```bash
ENVIRONMENT=testing
DEBUG=true
LOG_LEVEL=DEBUG
API_BASE_URL=https://api-staging.example.com
{% if cookiecutter.include_rate_limiting == "yes" -%}
RATE_LIMIT_REQUESTS=500
{% endif -%}
```

## 🔒 Security Best Practices

### Environment Variables Security

1. **Never commit `.env` files** to version control
2. **Use different credentials** for each environment
3. **Rotate API keys** regularly
4. **Use least privilege** - minimal required permissions
5. **Monitor API usage** for unusual activity

### Production Security

```bash
# Use environment variables in production, not .env files
export API_KEY="your_production_api_key"
export API_BASE_URL="https://api.example.com"
export ENVIRONMENT="production"
export DEBUG="false"
```

### Render.com Configuration

Set environment variables in Render Dashboard:

1. Go to your service → Environment
2. Add variables as **secrets** (not public)
3. Never expose sensitive data in logs

## 🧪 Testing Configuration

### Validate Your Configuration

```bash
# Test configuration loading
python -c "
from core.config import config
print('✅ Configuration loaded successfully')
print(f'API Base URL: {config.api.base_url}')
print(f'Environment: {config.mcp.environment}')
"
```

### Test Authentication

```bash
# Test authentication
python core/auth.py
```

### Test API Connectivity

```bash
# Test API connection
python core/client.py
```

## 🔧 Troubleshooting Configuration

### Common Issues

**"Missing required environment variables"**
- Check `.env` file exists and has correct variables
- Verify variable names match exactly
- Check for extra spaces or quotes

**"Configuration validation failed"**
- Verify API_BASE_URL format (must include http/https)
- Check all required variables are set
- Ensure numeric values are valid

**"Authentication failed"**
- Verify credentials are correct
- Check API endpoint is accessible
- Ensure API key has required permissions

### Debug Configuration

Enable debug mode to see configuration details:

```bash
DEBUG=true python main.py
```

This will show:
- Loaded configuration values (without secrets)
- Authentication status
- API connectivity status
- Available tools

---

**Next:** [🔧 API Integration Guide](api-integration.md)