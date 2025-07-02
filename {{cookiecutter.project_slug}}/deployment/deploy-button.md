# 🚀 One-Click Deploy to Render.com

Deploy {{cookiecutter.project_name}} to Render.com with one click!

## Quick Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo={{cookiecutter.github_username}}/{{cookiecutter.project_slug}})

## Manual Deploy Steps

### 1. Fork Repository
```bash
git clone https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.project_slug}}.git
cd {{cookiecutter.project_slug}}
2. Create Render Account

Go to render.com
Sign up with GitHub account
Connect your repository

3. Set Environment Variables
In Render Dashboard, set these SECRET variables:
{% if cookiecutter.auth_type == "API Key" -%}
API_KEY=your_actual_api_key_here
{% elif cookiecutter.auth_type == "Bearer Token" -%}
BEARER_TOKEN=your_actual_bearer_token_here
{% elif cookiecutter.auth_type == "OAuth2" -%}
CLIENT_ID=your_oauth_client_id
CLIENT_SECRET=your_oauth_client_secret
{% elif cookiecutter.auth_type == "Basic Auth" -%}
USERNAME=your_api_username
PASSWORD=your_api_password
{% endif -%}
Required:
API_BASE_URL=https://your-api-url.com
4. Deploy

Render detects render.yaml automatically
Your server will be at: https://{{cookiecutter.project_slug}}.onrender.com

Test Deployment
bashcurl https://{{cookiecutter.project_slug}}.onrender.com/health
Configure Claude Desktop
json{
  "mcpServers": {
    "{{cookiecutter.project_slug}}": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-fetch",
        "https://{{cookiecutter.project_slug}}.onrender.com"
      ]
    }
  }
}
Troubleshooting

Build Failed: Check environment variables
500 Error: Check logs in Render dashboard
Tools Missing: Verify Claude Desktop MCP config


Need help? Open an issue on GitHub!

### 3. Verifica file deployment completi
```bash
ls -la
# Dovresti vedere: render.yaml, Dockerfile, deploy-button.md