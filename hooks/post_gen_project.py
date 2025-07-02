#!/usr/bin/env python3
"""
Post-generation hook for MCP Server Template
Automatically sets up the generated project
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description, optional=False):
    """Run shell command with error handling"""
    try:
        print(f"🔧 {description}...")
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✅ {description} completed successfully")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        if optional:
            print(f"⚠️ {description} skipped (optional): {e}")
            return False
        else:
            print(f"❌ {description} failed: {e}")
            if e.stderr:
                print(f"   Error: {e.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with unexpected error: {e}")
        return False


def check_prerequisites():
    """Check if required tools are available"""
    print("🔍 Checking prerequisites...")
    
    # Check Python
    try:
        import sys
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        print(f"✅ Python {python_version} detected")
    except Exception as e:
        print(f"❌ Python check failed: {e}")
        return False
    
    # Check pip
    pip_available = run_command("pip --version", "Checking pip", optional=True)
    if not pip_available:
        pip_available = run_command("python -m pip --version", "Checking pip (alternative)", optional=True)
    
    # Check git
    git_available = run_command("git --version", "Checking git", optional=True)
    
    return True


def initialize_git_repository():
    """Initialize git repository and make initial commit"""
    if not shutil.which("git"):
        print("⚠️ Git not found, skipping repository initialization")
        return False
    
    success = True
    
    # Initialize repository
    success &= run_command("git init", "Initializing git repository", optional=True)
    
    if success:
        # Configure git if needed (only for this repo)
        run_command('git config user.name "{{ cookiecutter.author_name }}"', "Setting git user name", optional=True)
        run_command('git config user.email "{{ cookiecutter.author_email }}"', "Setting git user email", optional=True)
        
        # Add all files
        success &= run_command("git add .", "Adding files to git", optional=True)
        
        # Make initial commit
        if success:
            commit_message = "🎉 Initial commit from mcp-server-template"
            success &= run_command(f'git commit -m "{commit_message}"', "Making initial commit", optional=True)
    
    return success


def setup_python_environment():
    """Set up Python virtual environment and install dependencies"""
    project_name = "{{ cookiecutter.project_slug }}"
    
    # Create virtual environment
    venv_created = run_command(
        f"python -m venv venv",
        "Creating virtual environment",
        optional=True
    )
    
    if venv_created:
        # Determine activation script path
        if os.name == 'nt':  # Windows
            activate_script = "venv\\Scripts\\activate"
            pip_command = "venv\\Scripts\\pip"
        else:  # Unix/Linux/macOS
            activate_script = "venv/bin/activate"
            pip_command = "venv/bin/pip"
        
        # Install dependencies in virtual environment
        if os.path.exists("requirements.txt"):
            install_success = run_command(
                f"{pip_command} install -r requirements.txt",
                "Installing dependencies in virtual environment",
                optional=True
            )
            
            if install_success:
                print("🎉 Virtual environment setup completed!")
                print(f"📝 To activate: source {activate_script}")
                return True
    
    # Fallback: install in current environment
    print("📦 Installing dependencies in current Python environment...")
    return run_command(
        "pip install -r requirements.txt",
        "Installing dependencies",
        optional=True
    )


def setup_environment_file():
    """Set up .env file from template"""
    if os.path.exists(".env.example"):
        if not os.path.exists(".env"):
            try:
                shutil.copy(".env.example", ".env")
                print("✅ Created .env file from template")
                print("📝 Don't forget to edit .env with your actual API credentials!")
                return True
            except Exception as e:
                print(f"⚠️ Could not create .env file: {e}")
                return False
        else:
            print("✅ .env file already exists")
            return True
    else:
        print("⚠️ .env.example not found, skipping .env creation")
        return False


def create_data_directory():
    """Create data directory for the application"""
    project_slug = "{{ cookiecutter.project_slug }}"
    data_dir = f"{project_slug}_data"
    
    try:
        os.makedirs(data_dir, exist_ok=True)
        print(f"✅ Created data directory: {data_dir}")
        
        # Create .gitkeep to track empty directory
        gitkeep_path = os.path.join(data_dir, ".gitkeep")
        with open(gitkeep_path, "w") as f:
            f.write("# Keep this directory in git\n")
        
        return True
    except Exception as e:
        print(f"⚠️ Could not create data directory: {e}")
        return False


def display_next_steps():
    """Display next steps for the user"""
    project_name = "{{ cookiecutter.project_name }}"
    project_slug = "{{ cookiecutter.project_slug }}"
    auth_type = "{{ cookiecutter.auth_type }}"
    api_service = "{{ cookiecutter.api_service_type }}"
    
    print("\n" + "=" * 60)
    print(f"🎉 {project_name} has been created successfully!")
    print("=" * 60)
    
    print("\n📁 Project Structure:")
    print(f"   📂 {project_slug}/")
    print(f"   ├── 🔧 core/           # Authentication & HTTP client")
    print(f"   ├── 🛠️ tools/          # MCP tools (6 tools ready)")
    print(f"   ├── 📚 docs/           # Complete documentation")
    print(f"   ├── 🚀 deployment/     # Render.com & Docker configs")
    print(f"   ├── 📄 main.py         # MCP server entry point")
    print(f"   ├── ⚙️ .env            # Configuration (EDIT THIS!)")
    print(f"   └── 📋 requirements.txt # Python dependencies")
    
    print(f"\n🎯 Your MCP Server Configuration:")
    print(f"   📡 API Type: {api_service}")
    print(f"   🔐 Auth Type: {auth_type}")
    print(f"   🛠️ Tools: 6 generic CRUD tools")
    print(f"   📊 Features: Rate limiting, error handling, logging")
    
    print("\n🚀 Next Steps:")
    print("\n1️⃣ Configure your API credentials:")
    print(f"   📝 Edit .env file with your {auth_type} credentials")
    
    if auth_type == "API Key":
        print(f"   🔑 Set API_KEY=your_actual_api_key")
    elif auth_type == "Bearer Token":
        print(f"   🎫 Set BEARER_TOKEN=your_actual_token")
    elif auth_type == "OAuth2":
        print(f"   🔐 Set CLIENT_ID and CLIENT_SECRET")
    elif auth_type == "Basic Auth":
        print(f"   👤 Set USERNAME and PASSWORD")
    
    print(f"   🌐 Set API_BASE_URL=https://your-api-url.com")
    
    print("\n2️⃣ Test your MCP server:")
    print(f"   🧪 python main.py")
    print(f"   ✅ Server should start at http://localhost:8000")
    
    print("\n3️⃣ Configure Claude Desktop:")
    print(f"   📝 Add MCP server to Claude Desktop configuration")
    print(f"   📖 See docs/quick-start.md for detailed instructions")
    
    print("\n4️⃣ Deploy to production:")
    print(f"   🚀 Push to GitHub and deploy to Render.com")
    print(f"   📖 See deployment/deploy-button.md for one-click deploy")
    
    print("\n📚 Documentation:")
    print(f"   📖 docs/README.md           # Project overview")
    print(f"   🚀 docs/quick-start.md      # 5-minute setup guide")
    print(f"   ⚙️ docs/configuration.md    # Complete config reference")
    print(f"   🔍 docs/troubleshooting.md  # Problem solving guide")
    
    print("\n💡 Useful Commands:")
    print(f"   🧪 python core/auth.py      # Test authentication")
    print(f"   🌐 python core/client.py    # Test API connectivity")
    print(f"   📊 python main.py           # Start MCP server")
    
    print(f"\n🆘 Need Help?")
    print(f"   📖 Full documentation in docs/ directory")
    print(f"   🐛 GitHub Issues: https://github.com/{{ cookiecutter.github_username }}/{project_slug}/issues")
    print(f"   📧 Email: {{ cookiecutter.author_email }}")
    
    print("\n" + "=" * 60)
    print("🎯 Happy coding with your new MCP server! 🚀")
    print("=" * 60)


def main():
    """Main setup function"""
    print("🚀 Setting up your MCP server project...")
    print("=" * 50)
    
    try:
        # Check prerequisites
        check_prerequisites()
        
        # Setup steps
        setup_environment_file()
        create_data_directory()
        
        # Optional setup steps
        setup_python_environment()
        initialize_git_repository()
        
        # Success message
        display_next_steps()
        
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Setup failed with unexpected error: {e}")
        print("💡 You can still use the project, just follow the manual setup steps in docs/")
        sys.exit(1)


if __name__ == "__main__":
    main()