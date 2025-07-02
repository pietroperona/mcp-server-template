# {{cookiecutter.project_name}} Documentation

{{cookiecutter.project_description}}

**Generated from**: [mcp-server-template](https://github.com/{{cookiecutter.github_username}}/mcp-server-template)  
**Author**: {{cookiecutter.author_name}} <{{cookiecutter.author_email}}>  
**Version**: {{cookiecutter.project_version}}  
**API Type**: {{cookiecutter.api_service_type}}  
**Authentication**: {{cookiecutter.auth_type}}  

## 📚 Documentation Index

- [🚀 Quick Start Guide](quick-start.md) - Get up and running in 5 minutes
- [⚙️ Configuration Guide](configuration.md) - Complete configuration reference
- [🔧 API Integration](api-integration.md) - How to customize for your API
- [🛠️ Development Guide](development.md) - Local development setup
- [🚀 Deployment Guide](deployment.md) - Deploy to Render.com and Docker
- [🔍 Troubleshooting](troubleshooting.md) - Common issues and solutions
- [📖 API Reference](api-reference.md) - Complete tool reference

## 🎯 What This Project Does

This MCP (Model Context Protocol) server provides Claude AI with tools to interact with {{cookiecutter.api_service_type}} APIs. It includes:

✅ **Authentication** - {{cookiecutter.auth_type}} support  
✅ **CRUD Operations** - Create, Read, Update, Delete resources  
✅ **Error Handling** - Robust error handling and retries  
{% if cookiecutter.include_rate_limiting == "yes" -%}
✅ **Rate Limiting** - Automatic rate limit management  
{% endif -%}
{% if cookiecutter.include_caching == "yes" -%}
✅ **Caching** - Redis-based response caching  
{% endif -%}
✅ **Production Ready** - One-click Render.com deployment  

## 🚀 Quick Start

1. **Configure API credentials** in `.env`
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Run server**: `python main.py`
4. **Test tools**: Server runs on `http://localhost:8000`

## 🔧 Available Tools

- `get_api_status` - Check API connectivity and authentication
- `list_resources` - List available resources with pagination
- `get_resource_by_id` - Get detailed resource information
- `create_resource` - Create new resources
- `update_resource` - Update existing resources  
- `delete_resource` - Delete resources

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.project_slug}}/issues)
- **Discussions**: [GitHub Discussions](https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.project_slug}}/discussions)
- **Email**: {{cookiecutter.author_email}}

---

**Generated from [mcp-server-template](https://github.com/{{cookiecutter.github_username}}/mcp-server-template)** 🍪