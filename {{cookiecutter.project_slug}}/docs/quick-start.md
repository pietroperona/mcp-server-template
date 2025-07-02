# 🚀 Quick Start Guide

Get {{cookiecutter.project_name}} running in 5 minutes!

## 📋 Prerequisites

- Python {{cookiecutter.python_version}}+
- {{cookiecutter.api_service_type}} API access
{% if cookiecutter.auth_type == "API Key" -%}
- Valid API key
{% elif cookiecutter.auth_type == "Bearer Token" -%}
- Valid bearer token
{% elif cookiecutter.auth_type == "OAuth2" -%}
- OAuth2 client credentials
{% elif cookiecutter.auth_type == "Basic Auth" -%}
- Username and password
{% endif -%}

## ⚡ 5-Minute Setup

### 1. Clone & Install
```bash
git clone https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.project_slug}}.git
cd {{cookiecutter.project_slug}}
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

**Required variables:**
```bash
API_BASE_URL=https://your-api.com
{% if cookiecutter.auth_type == "API Key" -%}
API_KEY=your_api_key_here
{% elif cookiecutter.auth_type == "Bearer Token" -%}
BEARER_TOKEN=your_bearer_token_here
{% elif cookiecutter.auth_type == "OAuth2" -%}
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
{% elif cookiecutter.auth_type == "Basic Auth" -%}
USERNAME=your_username
PASSWORD=your_password
{% endif -%}
```

### 3. Test Connection
```bash
python -c "
import asyncio
from core.auth import test_authentication
asyncio.run(test_authentication())
"
```

### 4. Start Server
```bash
python main.py
```

🎉 **Server running at**: `http://localhost:8000`

## 🧪 Test Your Setup

### Test API Status
```bash
curl http://localhost:8000/tools/get_api_status
```

### Test Resource Listing
```bash
curl "http://localhost:8000/tools/list_resources?resource_type=users&limit=5"
```

## 🔧 Configure Claude Desktop

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "{{cookiecutter.project_slug}}": {
      "command": "python",
      "args": ["{{cookiecutter.project_slug}}/main.py"],
      "cwd": "{{cookiecutter.project_slug}}"
    }
  }
}
```

## ✅ Verify Tools in Claude

Ask Claude: *"What tools do you have available?"*

You should see:
- ✅ get_api_status
- ✅ list_resources  
- ✅ get_resource_by_id
- ✅ create_resource
- ✅ update_resource
- ✅ delete_resource

## 🚀 Deploy to Production

**One-click deploy to Render.com:**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo={{cookiecutter.github_username}}/{{cookiecutter.project_slug}})

See [Deployment Guide](deployment.md) for detailed instructions.

## 🆘 Having Issues?

### Quick Troubleshooting

**Authentication Failed?**
- Verify credentials in `.env`
- Check API endpoint is correct
- Run `python core/auth.py` to test auth

**Connection Failed?**
- Verify `API_BASE_URL` is correct
- Check internet connection
- Try `python core/client.py` to test connectivity

**Tools Not Available?**
- Check MCP configuration in Claude Desktop
- Restart Claude Desktop after config changes
- Verify server is running on correct port

**Still stuck?** Check the [full troubleshooting guide](troubleshooting.md).

## 📚 Next Steps

- [⚙️ Configuration Guide](configuration.md) - Detailed configuration options
- [🔧 API Integration](api-integration.md) - Customize for your specific API
- [🛠️ Development Guide](development.md) - Local development workflow

---

**Need help?** Open an issue on [GitHub](https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.project_slug}}/issues) 🆘