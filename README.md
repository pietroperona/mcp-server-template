# MCP Server Template

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![FastMCP](https://img.shields.io/badge/FastMCP-0.4.0%2B-orange?style=flat-square)](https://github.com/jlowin/fastmcp)
[![Claude AI](https://img.shields.io/badge/Claude%20AI-Compatible-purple?style=flat-square)](https://www.anthropic.com/claude)
[![Deploy to Render](https://img.shields.io/badge/Deploy%20to-Render-green?style=flat-square&logo=render)](https://render.com/deploy)

A practical Cookiecutter template for building MCP servers that connect Claude AI to external APIs. Built with FastMCP and ready for Render.com deployment.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

*Last Updated: July 2025*

## Features at a Glance

- 🔌 **Multi-Platform Compatibility**: Works with Claude Desktop, Claude Web, and Claude API
- 🔒 **Comprehensive Auth Support**: API Key, Bearer Token, OAuth2, Basic Auth
- 🚦 **Rate Limiting**: Configurable request throttling to avoid API bans
- 🧩 **Ready-to-Use Tools**: 6 pre-built generic API tools adaptable to any service
- 🚀 **One-Click Deployment**: Render.com integration with pre-configured settings
- 🐳 **Docker Support**: Containerization for cloud deployments
- 🛠️ **Robust Error Handling**: Detailed error reporting and recovery
- 🧪 **Testable Components**: Each module can be tested independently
- 🔄 **Session Management Fix**: Prevents "Event loop is closed" errors

## What This Does

This template generates a complete MCP server project that lets Claude AI interact with any API. Think of it as a bridge between Claude and the external services you want to use.

**Example**: Generate a weather MCP server in 2 minutes, deploy it to Render.com, and suddenly Claude can check weather for any city in the world.

## Tech Stack

- **[FastMCP](https://github.com/jlowin/fastmcp)** - Python framework for MCP servers (v0.4.0+)
- **[aiohttp](https://docs.aiohttp.org/)** - Async HTTP client for API calls  
- **[Pydantic](https://docs.pydantic.dev/)** - Configuration management
- **[Render.com](https://render.com)** - One-click deployment

**Requirements**: Python 3.11 or newer

## Quick Start

### 1. Generate Your Project

```bash
pip install cookiecutter
cookiecutter https://github.com/pietroperona/mcp-server-template
```

You'll be asked a few questions:
```
project_name: Weather MCP Server
project_slug: weather-mcp-server  [auto-generated]
author_name: Your Name
author_email: you@example.com
github_username: yourusername
api_base_url: https://api.openweathermap.org/data/2.5
api_service_type: REST API
auth_type: API Key
include_rate_limiting: yes
include_caching: no
render_deployment: yes
docker_support: yes
license: MIT
```

### 2. Configure Your API

```bash
cd weather-mcp-server
cp .env.example .env
```

Edit `.env` with your API credentials:
```bash
API_BASE_URL=https://api.openweathermap.org/data/2.5
API_KEY=your_openweather_api_key
```

### 3. Install and Run

```bash
pip install -r requirements.txt
python main.py
```

Your MCP server is now running at `http://localhost:8000`

### 4. Connect to Claude Desktop

Add this to your Claude Desktop MCP configuration:
```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["weather-mcp-server/main.py"],
      "cwd": "weather-mcp-server"
    }
  }
}
```

Now Claude can check weather: *"What's the weather like in Tokyo?"*

### 5. Connect to Claude Web Browser (Claude.ai)

Your MCP server also exposes an SSE (Server-Sent Events) endpoint at `/sse` that can be used with Claude Web in browsers:

1. Deploy your MCP server to a public URL (see Deployment section)
2. In Claude Web, go to Settings → Claude API Tools
3. Add your MCP server's public URL + `/sse` endpoint:
   ```
   https://your-mcp-server.onrender.com/sse
   ```
4. Claude Web will now show your tools in the Tools menu

**Note**: The `/sse` endpoint is automatically included in all MCP servers generated with this template.

## What You Get

Every generated project includes:

### 6 Ready-to-Use Tools
- `get_api_status` - Check if your API is working
- `list_resources` - Browse available data (cities, users, etc.)
- `get_resource_by_id` - Get specific item details
- `create_resource` - Add new data
- `update_resource` - Modify existing data  
- `delete_resource` - Remove data

### Real Example: Weather API

When you ask Claude *"What's the weather in Paris?"*, here's what happens:

1. Claude calls `list_resources(resource_type="weather", location="Paris")`
2. Your MCP server hits `https://api.openweathermap.org/data/2.5/weather?q=Paris`
3. Claude gets the weather data and responds naturally

### Project Structure

```
weather-mcp-server/
├── core/
│   ├── config.py     # API credentials & settings
│   ├── auth.py       # Handle API authentication  
│   └── client.py     # HTTP client with retries
├── tools/
│   └── example_tools.py  # The 6 MCP tools
├── docs/             # Setup guides & troubleshooting
│   ├── configuration.md  # Detailed configuration options
│   ├── quick-start.md    # Getting started guide
│   ├── README.md         # Overview of documentation
│   └── troubleshooting.md # Common issues & solutions
├── main.py          # FastMCP server
└── .env.example     # Configuration template
```

Note: When your server runs, it may create directories that end with `_data/` (like `cache_data/`). These directories are automatically excluded from git via `.gitignore` as they contain runtime data that shouldn't be committed.

## Authentication Support

The template handles different auth methods:

**API Key** (most common)
```bash
API_KEY=your_key_here
API_KEY_HEADER=X-API-Key
```

**Bearer Token**
```bash
BEARER_TOKEN=your_token_here
```

**OAuth2** (for complex APIs)
```bash
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
```

**Basic Auth**
```bash
USERNAME=your_username  
PASSWORD=your_password
```

## Production Deployment

### Render.com (Recommended) 🚀

1. Push your generated project to GitHub
2. Connect to Render.com
3. Set your environment variables
4. Your MCP server is live!

The template includes `render.yaml` with optimized settings for production.

**Important for Claude Web Browser**: 
Make sure to note the public URL of your deployed service. Claude Web will connect to your MCP server via the `/sse` endpoint:
```
https://your-service-name.onrender.com/sse
```

### Docker 🐳

```bash
docker build -t my-mcp-server .
docker run -p 8000:8000 --env-file .env my-mcp-server
```

**For Claude Web**: Access the SSE endpoint at `http://your-docker-host:8000/sse`

## Real-World Examples

### Weather Service
```bash
# Generate project
cookiecutter https://github.com/pietroperona/mcp-server-template
# Project: Weather API Server
# API: OpenWeatherMap (free)
# Result: Claude can check weather worldwide
```

### News Headlines  
```bash
# Generate project  
cookiecutter https://github.com/pietroperona/mcp-server-template
# Project: News API Server
# API: NewsAPI.org (free tier)
# Result: Claude can fetch latest news
```

**Try it**: [NewsAPI.org](https://newsapi.org/) - 1000 free requests/day

### Stock Prices
```bash
# Generate project
cookiecutter https://github.com/pietroperona/mcp-server-template  
# Project: Stock Market Server
# API: Alpha Vantage (free)
# Result: Claude can look up stock prices
```

**Try it**: [Alpha Vantage](https://www.alphavantage.co/) - Free API key, 5 calls/minute

## Detailed Weather Example

Let's walk through building a weather MCP server:

### 1. Get OpenWeatherMap API Key
- Go to [openweathermap.org](https://openweathermap.org/api)
- Sign up for free account  
- Copy your API key

### 2. Generate Project
```bash
cookiecutter https://github.com/pietroperona/mcp-server-template

project_name: Weather MCP Server
project_slug: weather-mcp-server  
author_name: John Smith
api_service_type: REST API
auth_type: API Key
api_base_url: https://api.openweathermap.org/data/2.5
include_rate_limiting: yes
render_deployment: yes
```

### 3. Configure Environment
```bash
cd weather-mcp-server
cp .env.example .env
```

Edit `.env`:
```bash
API_BASE_URL=https://api.openweathermap.org/data/2.5
API_KEY=your_actual_api_key_here
API_KEY_HEADER=appid
```

### 4. Test Your Server
```bash
python main.py
```

### 5. Test with Claude
Ask Claude: *"Check the weather in London"*

Claude will use your tools:
```
Tool: list_resources
Parameters: resource_type="weather", q="London"
Result: Current weather data for London
```

## Customization

### Modify for Your API

The generated tools are generic but easy to customize:

```python
# In tools/example_tools.py
async def list_resources_async(resource_type: str = "weather", location: str = "London"):
    # Customize this for your API
    endpoint = f"/weather?q={location}"
    response = await client.get(endpoint)
    return response
```

### Add API-Specific Tools

```python
@mcp.tool()
def get_weather_forecast(city: str, days: int = 5) -> str:
    """Get weather forecast for a city"""
    result = run_async_tool(get_forecast_async, city, days)
    return json.dumps(result, indent=2)
```

### Configure Rate Limiting

```bash
# In .env
RATE_LIMIT_REQUESTS=60    # 60 requests
RATE_LIMIT_WINDOW=60      # per minute
```

## Troubleshooting

### Authentication Issues 🔑

**"Authentication failed"**
- Check your API key is correct
- Verify the API_KEY_HEADER name
- Test API key in browser/Postman first

### Tool Connection Issues 🔌

**"Tools not appearing in Claude"**  
- Restart Claude Desktop
- Check MCP configuration syntax
- Verify server starts without errors

**"Claude Web doesn't show my tools"**
- Make sure you're using the correct `/sse` endpoint
- Check CORS settings if hosting on a custom domain
- Verify your server is publicly accessible

### API Connection Issues 🌐

**"Connection timeout"**
- Increase API_TIMEOUT in .env
- Check internet connection
- Verify API endpoint URL

**"API versioning problems"**
- Some APIs (like OpenWeatherMap) don't use version prefixes in URLs
- Set `API_VERSION=none` or leave it empty in your .env file
- This template handles version-less APIs automatically

### Technical Issues 🛠️

**"Event loop is closed" errors**
- This is fixed in the latest template version (July 2025)
- The template now uses a better session management approach for aiohttp
- Each request creates a new session with proper cleanup
- Custom event loop handling prevents these errors

## Development

### Run Tests ✅
```bash
python core/auth.py      # Test authentication
python core/client.py    # Test API connection  
python main.py          # Start MCP server
```

### Debug Mode 🐛
```bash
DEBUG=true python main.py
```

Shows detailed request/response logs.

### Session Management 🔄

This template uses an optimized approach to manage aiohttp sessions:

```python
# Create a new session for each request (prevents "Event loop is closed" errors)
async with aiohttp.ClientSession() as session:
    async with session.request(...) as response:
        # Process response
```

This pattern ensures that:
- Each HTTP request gets a fresh session
- Sessions are properly closed after use
- No "Event loop is closed" errors occur
- Better handling of asyncio event loops

## Contributing

1. Fork the [repository](https://github.com/pietroperona/mcp-server-template)
2. Test your changes with different API types  
3. Update documentation
4. Submit pull request

## Why This Template?

Building MCP servers involves a lot of boilerplate:
- 🔐 Authentication handling
- ⚠️ Error management  
- 🚦 Rate limiting
- ⚙️ Configuration
- 🚀 Deployment setup

This template gives you all of that instantly, so you can focus on connecting to your specific API.

**Built on proven tools**: [FastMCP](https://github.com/jlowin/fastmcp) for the MCP framework, [Model Context Protocol](https://modelcontextprotocol.io/) for Claude integration.

**Works with**:
- 🖥️ Claude Desktop (via local MCP server)
- 🌐 Claude Web Browser (via `/sse` endpoint)
- 🤖 Claude API (via proxy configuration)

## License

MIT License - use for any purpose, commercial or personal.

---

## 🔄 Recent Updates

- **July 2025**: Fixed "Event loop is closed" errors with improved aiohttp session management
- **July 2025**: Added Claude Web Browser support via `/sse` endpoint
- **July 2025**: Improved API versioning with better handling of version-less APIs
- **July 2025**: Added better error handling and troubleshooting guidance

---

**Ready to connect Claude to your favorite API?** 🚀

```bash
pip install cookiecutter
cookiecutter https://github.com/pietroperona/mcp-server-template
```