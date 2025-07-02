# MCP Server Template

A practical Cookiecutter template for building MCP servers that connect Claude AI to external APIs. Built with FastMCP and ready for Render.com deployment.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## What This Does

This template generates a complete MCP server project that lets Claude AI interact with any API. Think of it as a bridge between Claude and the external services you want to use.

**Example**: Generate a weather MCP server in 2 minutes, deploy it to Render.com, and suddenly Claude can check weather for any city in the world.

## Tech Stack

- **[FastMCP](https://github.com/jlowin/fastmcp)** - Python framework for MCP servers
- **[aiohttp](https://docs.aiohttp.org/)** - Async HTTP client for API calls  
- **[Pydantic](https://docs.pydantic.dev/)** - Configuration management
- **[Render.com](https://render.com)** - One-click deployment

## Quick Start

### 1. Generate Your Project

```bash
pip install cookiecutter
cookiecutter https://github.com/pietroperona/mcp-server-template
```

You'll be asked a few questions:
```
project_name: Weather MCP Server
author_name: Your Name
api_service_type: REST API
auth_type: API Key
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
├── main.py          # FastMCP server
└── .env.example     # Configuration template
```

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

### Render.com (Recommended)

1. Push your generated project to GitHub
2. Connect to Render.com
3. Set your environment variables
4. Your MCP server is live!

The template includes `render.yaml` with optimized settings for production.

### Docker

```bash
docker build -t my-mcp-server .
docker run -p 8000:8000 --env-file .env my-mcp-server
```

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

**"Authentication failed"**
- Check your API key is correct
- Verify the API_KEY_HEADER name
- Test API key in browser/Postman first

**"Tools not appearing in Claude"**  
- Restart Claude Desktop
- Check MCP configuration syntax
- Verify server starts without errors

**"Connection timeout"**
- Increase API_TIMEOUT in .env
- Check internet connection
- Verify API endpoint URL

## Development

### Run Tests
```bash
python core/auth.py      # Test authentication
python core/client.py    # Test API connection  
python main.py          # Start MCP server
```

### Debug Mode
```bash
DEBUG=true python main.py
```

Shows detailed request/response logs.

## Contributing

1. Fork the [repository](https://github.com/pietroperona/mcp-server-template)
2. Test your changes with different API types  
3. Update documentation
4. Submit pull request

## Why This Template?

Building MCP servers involves a lot of boilerplate:
- Authentication handling
- Error management  
- Rate limiting
- Configuration
- Deployment setup

This template gives you all of that instantly, so you can focus on connecting to your specific API.

**Built on proven tools**: [FastMCP](https://github.com/jlowin/fastmcp) for the MCP framework, [Model Context Protocol](https://modelcontextprotocol.io/) for Claude integration.

## License

MIT License - use for any purpose, commercial or personal.

---

**Ready to connect Claude to your favorite API?**

```bash
pip install cookiecutter
cookiecutter https://github.com/pietroperona/mcp-server-template
```