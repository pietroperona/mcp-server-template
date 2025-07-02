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