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

# FastMCP import
from mcp.server.fastmcp import FastMCP

# Import our modules
from core.config import config
from core.auth import auth, test_authentication
from core.client import client, test_client
from tools import register_all_tools, get_available_tools

# Data storage directory
DATA_DIR = "{{cookiecutter.project_slug}}_data"

def save_api_data(data_type: str, data: Dict[str, Any]) -> None:
    """Save API data to file for debugging and monitoring"""
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

# Get port from environment (Render sets this automatically)
PORT = int(os.environ.get("PORT", 8000))

# Initialize FastMCP server
mcp = FastMCP(
    name=config.mcp.server_name,
    host=config.mcp.host,
    port=PORT
)

@mcp.resource("{{cookiecutter.project_slug}}://status")
def get_server_status() -> str:
    """Get current server status and configuration"""
    try:
        content = f"# {{cookiecutter.project_name}} Server Status\n\n"
        content += f"**Status**: ✅ Running\n"
        content += f"**Version**: {config.mcp.server_version}\n"
        content += f"**Environment**: {config.mcp.environment}\n"
        content += f"**API**: {config.api.base_url}\n"
        content += f"**Authentication**: {{cookiecutter.auth_type}}\n\n"
        
        tools = get_available_tools()
        content += f"## Available Tools ({len(tools)})\n"
        for tool in tools:
            content += f"- `{tool}`\n"
        
        content += f"\n*Last Updated: {datetime.now().isoformat()}*\n"
        return content
        
    except Exception as e:
        return f"# Server Status Error\n\nError: {str(e)}\n"

@mcp.prompt()
def api_integration_guide(resource_type: str = "users") -> str:
    """Generate a guide for integrating with the API"""
    return f"""You are an expert at {{cookiecutter.api_service_type}} API integration.

## Available Operations

1. **Check Status**: `get_api_status()` 
2. **List Resources**: `list_resources(resource_type="{resource_type}")`
3. **Get Item**: `get_resource_by_id(resource_type, resource_id)`
4. **Create**: `create_resource(resource_type, data)`
5. **Update**: `update_resource(resource_type, resource_id, data)`
6. **Delete**: `delete_resource(resource_type, resource_id)`

Start with `get_api_status()` to verify connectivity."""

def main():
    """Main server entry point"""
    
    print("🔧 Validating configuration...")
    try:
        config.validate()
        print("✅ Configuration valid")
        
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        sys.exit(1)
    
    print("🔧 Registering MCP tools...")
    try:
        register_all_tools(mcp)
        tools = get_available_tools()
        print(f"✅ {len(tools)} tools registered")
        
    except Exception as e:
        print(f"❌ Tool registration failed: {e}")
        sys.exit(1)
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print(f"\n🚀 Starting {{cookiecutter.project_name}} MCP Server")
    print(f"📊 Server: {config.mcp.server_name}")
    print(f"🌍 Host: {config.mcp.host}:{PORT}")
    print(f"🔗 API: {config.api.base_url}")
    
    print(f"\n✅ {{cookiecutter.project_name}} is ready!")
    
    # Start the MCP server
    mcp.run(transport='sse')

if __name__ == "__main__":
    main()