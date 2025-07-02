# MCP Server Template

**Cookiecutter template for creating production-ready MCP (Model Context Protocol) servers with one-click Render.com deployment.**

Generate MCP servers for any API integration in minutes! Perfect for connecting Claude AI to REST APIs, GraphQL endpoints, or custom web services.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## 🎯 What This Template Creates

This Cookiecutter template generates a complete MCP server project with:

✅ **Multiple Authentication Types** - API Key, Bearer Token, OAuth2, Basic Auth  
✅ **Production-Ready Architecture** - Modular, scalable, well-documented  
✅ **6 Generic MCP Tools** - CRUD operations for any API  
✅ **One-Click Deployment** - Render.com ready with automated setup  
✅ **Rate Limiting & Caching** - Built-in performance optimizations  
✅ **Comprehensive Documentation** - Quick start, configuration, troubleshooting  
✅ **Error Handling & Retry Logic** - Robust API integration  
✅ **Docker Support** - Container-ready for any deployment  

## 🚀 Quick Start

### 1. Install Cookiecutter
```bash
pip install cookiecutter
```

### 2. Generate Your MCP Server
```bash
cookiecutter https://github.com/yourusername/mcp-server-template
```

### 3. Answer the Prompts
```
project_name [My MCP Server]: Shopify Order Manager
author_name [Your Name]: John Doe
api_service_type [REST API]: REST API
auth_type [API Key]: API Key
render_deployment [yes]: yes
```

### 4. Your Server is Ready!
```bash
cd shopify-order-manager
cp .env.example .env
# Edit .env with your API credentials
pip install -r requirements.txt
python main.py
```

🎉 **MCP server running at `http://localhost:8000`**

## 🛠️ Template Features

### 🏗️ **Modular Architecture**
```
your-mcp-server/
├── core/                    # Authentication, HTTP client, configuration
├── tools/                   # MCP tool definitions
├── docs/                    # Complete documentation
├── deployment/              # Render.com + Docker configs
└── main.py                  # Server entry point
```

### 🔧 **Built-in MCP Tools**
- `get_api_status` - API connectivity and health checks
- `list_resources` - Browse API resources with pagination
- `get_resource_by_id` - Fetch specific resources
- `create_resource` - Create new resources
- `update_resource` - Modify existing resources
- `delete_resource` - Remove resources

### 🔐 **Authentication Support**
- **API Key** - Simple header-based authentication
- **Bearer Token** - JWT and OAuth2 token support
- **OAuth2** - Full OAuth2 flow with automatic refresh
- **Basic Auth** - Username/password authentication
- **Custom** - Extensible for any auth method

### ⚡ **Performance Features**
- Rate limiting with token bucket algorithm
- Redis caching for API responses
- Retry logic with exponential backoff
- Connection pooling and timeouts
- Request/response logging

## 🌟 Example Use Cases

### E-commerce Integration
```bash
# Generate Shopify MCP server
cookiecutter https://github.com/yourusername/mcp-server-template
# → Connect Claude to Shopify API for order management
```

### Payment Processing
```bash
# Generate Stripe MCP server  
cookiecutter https://github.com/yourusername/mcp-server-template
# → Connect Claude to Stripe API for payment operations
```

### Project Management
```bash
# Generate GitHub MCP server
cookiecutter https://github.com/yourusername/mcp-server-template
# → Connect Claude to GitHub API for repository management
```

### CRM Integration
```bash
# Generate Salesforce MCP server
cookiecutter https://github.com/yourusername/mcp-server-template
# → Connect Claude to Salesforce API for customer data
```

## 🚀 One-Click Deployment

### Deploy to Render.com

1. **Generate your project** with this template
2. **Push to GitHub** 
3. **Click Deploy to Render** button in your generated README
4. **Set environment variables** in Render dashboard
5. **Your MCP server is live!**

### Deploy with Docker

```bash
# Generated projects include Dockerfile
docker build -t my-mcp-server .
docker run -p 8000:8000 --env-file .env my-mcp-server
```

## 📚 Generated Documentation

Every generated project includes comprehensive documentation:

- **📖 README.md** - Project overview and setup
- **🚀 Quick Start Guide** - 5-minute setup instructions  
- **⚙️ Configuration Guide** - Complete environment variable reference
- **🔧 API Integration Guide** - Customize for your specific API
- **🛠️ Development Guide** - Local development workflow
- **🚀 Deployment Guide** - Production deployment instructions
- **🔍 Troubleshooting Guide** - Common issues and solutions

## 🎨 Customization Options

### Template Variables

The template supports extensive customization:

```json
{
  "project_name": "My MCP Server",
  "project_description": "MCP server for external API integration",
  "author_name": "Your Name",
  "author_email": "you@example.com",
  "api_service_type": ["REST API", "GraphQL", "Custom"],
  "auth_type": ["API Key", "Bearer Token", "OAuth2", "Basic Auth"],
  "include_rate_limiting": ["yes", "no"],
  "include_caching": ["yes", "no"],
  "render_deployment": ["yes", "no"],
  "docker_support": ["yes", "no"]
}
```

### Post-Generation Hooks

Automatic setup after generation:
- ✅ Git repository initialization
- ✅ Virtual environment creation
- ✅ Dependencies installation
- ✅ Environment file setup
- ✅ Initial commit

## 🧪 Development

### Prerequisites

- Python 3.11+
- Cookiecutter
- Git

### Testing the Template

```bash
# Clone this repository
git clone https://github.com/yourusername/mcp-server-template
cd mcp-server-template

# Test template generation
cookiecutter .

# Test the generated project
cd your-generated-project
pip install -r requirements.txt
python main.py
```

### Contributing

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Test with different configuration options
5. Submit a pull request

## 📦 Template Structure

```
mcp-server-template/
├── cookiecutter.json                   # Template configuration
├── hooks/                              # Post-generation automation
│   ├── pre_gen_project.py             # Input validation
│   └── post_gen_project.py            # Setup automation
├── {{cookiecutter.project_slug}}/     # Generated project template
│   ├── core/                          # Core modules
│   ├── tools/                         # MCP tools
│   ├── docs/                          # Documentation
│   ├── deployment/                    # Deployment configs
│   └── main.py                        # Server entry point
└── README.md                          # This file
```

## 🎯 Examples

### Generated Shopify Integration

```python
# Generated tools automatically work with any API
result = await client.get("/admin/api/2023-10/orders.json")
orders = result.get("orders", [])

# MCP tools are instantly available in Claude:
# "List my recent Shopify orders"
# "Get details for order #1234"
# "Create a new product"
```

### Generated Stripe Integration

```python
# Same tools, different API - zero code changes needed
result = await client.get("/v1/payments")
payments = result.get("data", [])

# Claude can now:
# "Show me recent payments"
# "Get payment details for pay_123"
# "Create a new payment intent"
```

## 🆘 Support

- **📖 Documentation**: Each generated project includes complete docs
- **🐛 Issues**: [GitHub Issues](https://github.com/yourusername/mcp-server-template/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/yourusername/mcp-server-template/discussions)
- **📧 Email**: your-email@example.com

## 📄 License

This template is released under the MIT License. Generated projects inherit this license unless changed.

## 🙏 Acknowledgments

- **Model Context Protocol** - The standard that makes this possible
- **Claude AI** - The AI assistant this integrates with
- **FastMCP** - The Python MCP framework
- **Cookiecutter** - Template generation tool
- **Render.com** - Deployment platform

---

**Start building your MCP server now!** 🚀

```bash
pip install cookiecutter
cookiecutter https://github.com/yourusername/mcp-server-template
```