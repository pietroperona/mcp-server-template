#!/usr/bin/env python3
"""
Pre-generation hook for MCP Server Template
Validates user input before project generation
"""
import re
import sys


def validate_project_name():
    """Validate project name"""
    project_name = "{{ cookiecutter.project_name }}"

    if not project_name or project_name.strip() == "":
        print("❌ Error: project_name cannot be empty")
        sys.exit(1)

    if len(project_name) > 50:
        print("❌ Error: project_name too long (max 50 characters)")
        sys.exit(1)

    print(f"✅ Project name: {project_name}")


def validate_project_slug():
    """Validate project slug for file/directory names"""
    project_slug = "{{ cookiecutter.project_slug }}"

    # Check for valid slug format (letters, numbers, hyphens)
    if not re.match(r"^[a-z0-9-]+$", project_slug):
        print(
            "❌ Error: project_slug must contain only lowercase letters, numbers, and hyphens"
        )
        print(f"   Got: {project_slug}")
        sys.exit(1)

    # Check slug doesn't start or end with hyphen
    if project_slug.startswith("-") or project_slug.endswith("-"):
        print("❌ Error: project_slug cannot start or end with hyphen")
        sys.exit(1)

    # Check for reserved names
    reserved_names = ["core", "tools", "docs", "test", "tests", "main", "app", "api"]
    if project_slug in reserved_names:
        print(
            f"❌ Error: '{project_slug}' is a reserved name. Choose a different name."
        )
        sys.exit(1)

    print(f"✅ Project slug: {project_slug}")


def validate_author_email():
    """Validate author email format"""
    email = "{{ cookiecutter.author_email }}"

    # Basic email validation
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        print("❌ Error: Invalid email format")
        print(f"   Got: {email}")
        print("   Expected format: user@domain.com")
        sys.exit(1)

    print(f"✅ Author email: {email}")


def validate_python_version():
    """Validate Python version"""
    python_version = "{{ cookiecutter.python_version }}"

    # Check if it's a valid Python version format
    version_pattern = r"^\d+\.\d+$"
    if not re.match(version_pattern, python_version):
        print("❌ Error: Invalid Python version format")
        print(f"   Got: {python_version}")
        print("   Expected format: 3.11")
        sys.exit(1)

    # Check minimum version
    major, minor = map(int, python_version.split("."))
    if major < 3 or (major == 3 and minor < 11):
        print("❌ Error: Python version must be 3.11 or higher")
        print(f"   Got: {python_version}")
        sys.exit(1)

    print(f"✅ Python version: {python_version}")


def validate_github_username():
    """Validate GitHub username format"""
    username = "{{ cookiecutter.github_username }}"

    # GitHub username validation
    if not re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$", username):
        print("❌ Error: Invalid GitHub username format")
        print(f"   Got: {username}")
        print("   GitHub usernames can only contain alphanumeric characters or hyphens")
        print("   Cannot start or end with hyphen")
        sys.exit(1)

    if len(username) > 39:
        print("❌ Error: GitHub username too long (max 39 characters)")
        sys.exit(1)

    print(f"✅ GitHub username: {username}")


def main():
    """Main validation function"""
    print("🔍 Validating template input...")
    print("=" * 50)

    try:
        validate_project_name()
        validate_project_slug()
        validate_author_email()
        validate_python_version()
        validate_github_username()

        print("=" * 50)
        print("✅ All validations passed!")
        print("🚀 Generating your MCP server project...")

    except KeyboardInterrupt:
        print("\n❌ Template generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected validation error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
