#!/usr/bin/env python3
"""
{{cookiecutter.project_name}} - MCP Server
{{cookiecutter.project_description}}

Generated from mcp-server-template
Author: {{cookiecutter.author_name}} <{{cookiecutter.author_email}}>
Version: {{cookiecutter.project_version}}
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# ✅ FastMCP import
from mcp.server.fastmcp import FastMCP

# Import our modules
from core.config import config
from core.auth import auth, test_authentication
from core.client import client, test_client
from tools import register_all_tools, get_available_tools

# ===================================
# 📊 DATA STORAGE (like smartaces pattern)
# ===================================
DATA_DIR = "{{cookiecutter.project_slug}}_data"

def save_api_data(data_type: str, data: Dict[str, Any]) -> None:
    """
    Save API data to file for debugging and monitoring
    
    Args:
        data_type: Type of data being saved
        data: Data dictionary to save
    """
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_type}_{timestamp}.json"
        filepath = os.path.join(DATA_DIR, filename)
        
        # Add metadata
        data['saved_at'] = datetime.now().isoformat()
        data['server_name'] = config.mcp.server_name
        data['server_version'] = config.mcp.server_version
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        if config.mcp.debug:
            print(f"💾 Data saved to: {filepath}")
        
    except Exception as e:
        print(f"❌ Error saving data: {str(e)}")

# ===================================
# 🚀 SERVER SETUP
# ===================================

# Get port from environment (Render sets this automatically)
PORT = int(os.environ.get("PORT", 8000))

# Initialize FastMCP server
mcp = FastMCP(
    name=config.mcp.server_name,
    host=config.mcp.host,
    port=PORT
)

# ===================================
# 📚 RESOURCES (for Claude Desktop integration)
# ===================================

@mcp.resource("{{cookiecutter.project_slug}}://status")
def get_server_status() -> str:
    """
    Get current server status and configuration
    
    This resource provides real-time server status information
    for monitoring and debugging purposes.
    """
    try:
        status_info = {
            "server_name": config.mcp.server_name,
            "server_version": config.mcp.server_version,
            "environment": config.mcp.environment,
            "debug_mode": config.mcp.debug,
            "api_base_url": config.api.base_url,
            "auth_type": "{{cookiecutter.auth_type}}",
{% if cookiecutter.include_rate_limiting == "yes" -%}
            "rate_limiting": {
                "enabled": True,
                "max_requests": config.api.rate_limit_requests,
                "time_window": config.api.rate_limit_window
            },
{% else -%}
            "rate_limiting": {"enabled": False},
{% endif -%}
            "available_tools": get_available_tools(),
            "last_updated": datetime.now().isoformat()
        }
        
        content = f"# {{cookiecutter.project_name}} Server Status\n\n"
        content += f"**Status**: ✅ Running\n"
        content += f"**Version**: {status_info['server_version']}\n"
        content += f"**Environment**: {status_info['environment']}\n"
        content += f"**API**: {status_info['api_base_url']}\n"
        content += f"**Authentication**: {{cookiecutter.auth_type}}\n\n"
        
        content += f"## Available Tools ({len(status_info['available_tools'])})\n"
        for tool in status_info['available_tools']:
            content += f"- `{tool}`\n"
        
        content += f"\n## Configuration\n"
        content += f"- **Debug Mode**: {status_info['debug_mode']}\n"
        content += f"- **Rate Limiting**: {status_info['rate_limiting']['enabled']}\n"
{% if cookiecutter.include_rate_limiting == "yes" -%}
        if status_info['rate_limiting']['enabled']:
            content += f"  - Max Requests: {status_info['rate_limiting']['max_requests']}\n"
            content += f"  - Time Window: {status_info['rate_limiting']['time_window']}s\n"
{% endif -%}
        
        content += f"\n*Last Updated: {status_info['last_updated']}*\n"
        
        return content
        
    except Exception as e:
        return f"# Server Status Error\n\nError retrieving status: {str(e)}\n"

@mcp.resource("{{cookiecutter.project_slug}}://logs")
def get_recent_logs() -> str:
    """
    Get recent server logs and activity
    
    Shows recent API calls, errors, and system events.
    """
    try:
        if not os.path.exists(DATA_DIR):
            return "# No Logs Available\n\nNo API data has been logged yet."
        
        log_files = []
        for filename in os.listdir(DATA_DIR):
            if filename.endswith('.json'):
                log_files.append(filename)
        
        log_files.sort(reverse=True)  # Most recent first
        
        content = f"# Recent {{cookiecutter.project_name}} Activity\n\n"
        
        if log_files:
            content += f"**Total Log Files**: {len(log_files)}\n\n"
            
            # Show recent files
            content += "## Recent Activity\n"
            for filename in log_files[:5]:  # Show last 5 files
                file_parts = filename.replace('.json', '').split('_')
                if len(file_parts) >= 3:
                    data_type = '_'.join(file_parts[:-2])
                    date_part = file_parts[-2]
                    time_part = file_parts[-1]
                    
                    content += f"- **{data_type}** - {date_part} {time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}\n"
            
            if len(log_files) > 5:
                content += f"\n*... and {len(log_files) - 5} more files*\n"
        else:
            content += "No activity logs found.\n"
        
        return content
        
    except Exception as e:
        return f"# Logs Error\n\nError retrieving logs: {str(e)}\n"

# ===================================
# 🎯 PROMPTS (for Claude Desktop)
# ===================================

@mcp.prompt()
def api_integration_guide(resource_type: str = "users") -> str:
    """Generate a guide for integrating with the {{cookiecutter.api_service_type}} API"""
    return f"""You are an expert at {{cookiecutter.api_service_type}} API integration using {{cookiecutter.project_name}}.

Help the user interact with the API using the available MCP tools. Here's what you can do:

## Available Operations

1. **Check API Status**
   - Use `get_api_status()` to verify connectivity and authentication
   - This should be your first step for any integration

2. **List Resources** 
   - Use `list_resources(resource_type="{resource_type}")` to browse available data
   - Common resource types: users, orders, products, projects, tasks

3. **Get Specific Items**
   - Use `get_resource_by_id(resource_type, resource_id)` for detailed information
   - Useful for examining individual records

4. **Create New Resources**
   - Use `create_resource(resource_type, data)` to add new items
   - Data should be valid JSON for the resource type

5. **Update Existing Resources**
   - Use `update_resource(resource_type, resource_id, data)` to modify items
   - Use PATCH-style updates when possible

6. **Delete Resources**
   - Use `delete_resource(resource_type, resource_id)` to remove items
   - Be careful with this operation!

## Best Practices

- Always check API status first
- Start with listing resources to understand the data structure
- Use small limits when exploring (limit=5)
- Check error messages for API-specific requirements
- Respect rate limits and be patient with large operations

## Getting Started

1. Run `get_api_status()` to verify everything is working
2. Try `list_resources(resource_type="{resource_type}", limit=5)` to see sample data
3. Pick an ID from the results and try `get_resource_by_id("{resource_type}", "ID_HERE")`

What would you like to do with the {{cookiecutter.api_service_type}} API?"""

@mcp.prompt()
def troubleshooting_guide() -> str:
    """Generate a troubleshooting guide for common {{cookiecutter.project_name}} issues"""
    return f"""You are helping troubleshoot {{cookiecutter.project_name}} integration issues.

## Common Issues & Solutions

### 1. Authentication Problems
**Symptoms**: "Authentication failed", "401 Unauthorized", "Invalid credentials"

**Solutions**:
- Run `get_api_status()` to check authentication
- Verify {{cookiecutter.auth_type}} credentials in environment variables
{% if cookiecutter.auth_type == "API Key" -%}
- Check API_KEY is set correctly
- Verify API_KEY_HEADER if using custom header name
{% elif cookiecutter.auth_type == "Bearer Token" -%}
- Check BEARER_TOKEN is set and not expired
- Verify token has required permissions
{% elif cookiecutter.auth_type == "OAuth2" -%}
- Check CLIENT_ID and CLIENT_SECRET are correct
- Verify OAuth2 flow is completed
- Check if tokens need refresh
{% elif cookiecutter.auth_type == "Basic Auth" -%}
- Check USERNAME and PASSWORD are correct
- Verify account has API access
{% endif -%}

### 2. API Connectivity Issues
**Symptoms**: "Connection failed", "Timeout", "Network error"

**Solutions**:
- Check API_BASE_URL is correct
- Verify internet connectivity
- Check if API service is down
- Increase timeout if requests are slow

### 3. Resource Not Found
**Symptoms**: "404 Not Found", "Resource does not exist"

**Solutions**:
- Verify resource_type spelling
- Check resource_id format
- List resources first to see available data
- Check API documentation for correct endpoints

### 4. Rate Limiting
**Symptoms**: "429 Too Many Requests", "Rate limit exceeded"

**Solutions**:
{% if cookiecutter.include_rate_limiting == "yes" -%}
- Wait for rate limit window to reset
- Reduce request frequency
- Check RATE_LIMIT_REQUESTS and RATE_LIMIT_WINDOW settings
{% else -%}
- Wait before retrying requests
- Consider implementing rate limiting
- Contact API provider about limits
{% endif -%}

### 5. Data Format Issues
**Symptoms**: "Invalid JSON", "Bad Request", "Validation error"

**Solutions**:
- Check JSON syntax in create/update operations
- Verify required fields are included
- Check data types match API expectations
- Look at successful responses for format examples

## Debugging Steps

1. **Start with Status Check**get_api_status()
2. **Test Basic Connectivity**
list_resources(resource_type="users", limit=1)
3. **Check Configuration**
- Review server status resource
- Verify environment variables
- Check debug logs

4. **Test Authentication Separately**
- Use auth validation tools
- Check token expiration
- Verify permissions

What specific issue are you experiencing? I'll help you diagnose and fix it."""

# ===================================
# 🔧 STARTUP VALIDATION
# ===================================

async def validate_startup():
 """
 Validate system configuration and connectivity during startup
 """
 print(f"🚀 Starting {{cookiecutter.project_name}} v{config.mcp.server_version}")
 print(f"🔧 Environment: {config.mcp.environment}")
 print(f"🌐 API Base URL: {config.api.base_url}")
 print(f"🔐 Authentication: {{cookiecutter.auth_type}}")
 
 try:
     # Validate configuration
     config.validate()
     print("✅ Configuration validation passed")
     
     # Test authentication (if not in production)
     if config.mcp.environment != "production":
         auth_valid = await auth.validate_auth()
         if auth_valid:
             print("✅ Authentication test passed")
         else:
             print("⚠️ Authentication test failed - check credentials")
     
     # Test API connectivity (optional)
     if config.mcp.debug:
         api_healthy = await client.health_check()
         if api_healthy:
             print("✅ API connectivity verified")
         else:
             print("⚠️ API health check failed - API may be unavailable")
     
     return True
     
 except Exception as e:
     print(f"❌ Startup validation failed: {e}")
     if config.mcp.environment == "development":
         raise  # Stop in development
     return False  # Continue in production

def main():
 """Main server entry point"""
 
 # ===================================
 # 🔧 CONFIGURATION VALIDATION
 # ===================================
 print("🔧 Validating configuration...")
 try:
     config.validate()
     debug_info = config.get_debug_info()
     print(f"✅ Configuration valid")
     
     if config.mcp.debug:
         print(f"🔍 Debug info: {debug_info}")
         
 except Exception as e:
     print(f"❌ Configuration validation failed: {e}")
     print("💡 Check your .env file and environment variables")
     sys.exit(1)
 
 # ===================================
 # 🔧 TOOL REGISTRATION
 # ===================================
 print("🔧 Registering MCP tools...")
 try:
     register_all_tools(mcp)
     available_tools = get_available_tools()
     print(f"✅ {len(available_tools)} tools registered successfully")
     
 except Exception as e:
     print(f"❌ Tool registration failed: {e}")
     sys.exit(1)
 
 # ===================================
 # 📁 DATA DIRECTORY SETUP
 # ===================================
 os.makedirs(DATA_DIR, exist_ok=True)
 print(f"📁 Data directory: {DATA_DIR}")
 
 # ===================================
 # 🚀 SERVER STARTUP
 # ===================================
 print(f"\n🚀 Starting {{cookiecutter.project_name}} MCP Server")
 print(f"📊 Server: {config.mcp.server_name}")
 print(f"🌍 Host: {config.mcp.host}:{PORT}")
 print(f"🔗 API: {config.api.base_url}")
{% if cookiecutter.render_deployment == "yes" -%}
 print(f"🚀 Deployment: Render.com ready")
{% endif -%}
 print(f"🎯 Transport: SSE (Server-Sent Events)")
 
 # Run startup validation (async)
 if config.mcp.debug:
     try:
         asyncio.run(validate_startup())
     except Exception as e:
         print(f"⚠️ Startup validation had issues: {e}")
 
 print(f"\n✅ {{cookiecutter.project_name}} is ready!")
 print(f"💡 Use with Claude Desktop or MCP-compatible clients")
 
 # ✅ Start the MCP server
 mcp.run(transport='sse')

if __name__ == "__main__":
 main()