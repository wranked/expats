# Project Rules and Guidelines

## Overview
This document outlines the standard rules, architecture, and best practices for Django-based projects. It serves as a template that can be copied to new repositories for consistent development.

## Tech Stack
- **Python**: 3.13 (latest stable version)
- **Framework**: Django 5.2 (latest LTS with async support)
- **API**: Django REST Framework (DRF) with DRF Spectacular for OpenAPI docs
- **Database**: PostgreSQL
- **Dependency Management**: uv (fast, modern Python package manager)
- **Environment**: Virtual environment auto-managed by uv
- **Testing**: pytest with pytest-django
- **Coverage**: pytest-cov for code coverage
- **Linting/Formatting**: Follow Django best practices; use Black/Flake8 if needed

## Project Structure
```
project-root/
├── .github/
│   ├── copilot-instructions.md  # Points to rules.md
│   └── workflows/               # CI/CD pipelines
├── apps/                        # Django apps (recommended for organization)
│   ├── app1/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── constants.py         # Use TextChoices for choices
│   │   └── urls.py
│   └── common/                  # Shared utilities
├── config/                      # Django settings (renamed from project name)
├── fixtures/                    # Initial data
├── manage.py
├── pyproject.toml               # PEP 621 format for uv
├── uv.lock                      # Locked dependencies
├── pytest.ini                   # Test configuration
└── README.md
```

Alternatively, apps can be placed directly in the project root for smaller projects.

## Architecture Principles
- **Modular Apps**: Separate concerns into Django apps (e.g., users, blog, companies).
- **DRF for APIs**: Use ViewSets, Serializers, and Routers for REST APIs.
- **Constants**: Define choices in `constants.py` using `models.TextChoices`.
- **Base Models**: Use a `BaseModel` with common fields (created_at, updated_at).
- **Async Support**: Leverage Django 5.x async views where appropriate.
- **Security**: Use DRF permissions, authentication, and CORS headers.

## Design Patterns
- **Repository Pattern**: Encapsulate data access in managers/querysets.
- **Factory Pattern**: Use for test data creation.
- **Choices**: Always use `TextChoices` for model fields with fixed options.
- **Signals**: For decoupled logic (e.g., post-save actions).
- **Custom User Model**: Extend `AbstractUser` for flexibility.

## Database Conventions
- **Table Naming**: Always follow Django's default table naming convention: `appname_modelname` (all lowercase).
  - ✅ Correct: `companies_company`, `pdf_processor_pdfdocument`, `blog_post`
  - ❌ Incorrect: `pdf_documents`, `extracted_data`, `Company`
- **Explicit db_table**: Only set `db_table` in `Meta` class if you need to override the default. When you do, always use the format `appname_modelname`.
- **Consistency**: This ensures predictable table names and easier maintenance across all apps.

## Development Workflow
1. **Setup**:
   - Clone repo
   - Install Python 3.13
   - Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh` (macOS/Linux) or `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"` (Windows)
   - `uv sync`
   - `uv run python manage.py migrate`
   - `uv run python manage.py createsuperuser`

2. **Coding**:
   - Run commands: `uv run python manage.py <command>`
   - Migrations: `uv run python manage.py makemigrations` then `migrate`
   - Testing: `uv run pytest` (aim for 80%+ coverage)
   - Commit regularly with descriptive messages

3. **Dependency Management**:
   - Add package: `uv add <package-name>`
   - Remove package: `uv remove <package-name>`
   - Update dependencies: `uv lock --upgrade`
   - Sync environment: `uv sync`

4. **Best Practices**:
   - Write tests for new features
   - Use type hints where possible
   - Follow Django's naming conventions
   - Document APIs with DRF Spectacular

## Common Issues and Solutions
- **Migration Recursion**: Use `TextChoices` and avoid hardcoded choices in models.
- **Dependency Conflicts**: Use uv to manage versions; `uv.lock` ensures reproducibility.
- **Async Errors**: Ensure compatible libraries for Django 5.2.
- **Testing**: Use fixtures and factories for reliable tests.
- **Vercel Deployment**: Use PEP 621 `pyproject.toml` format; uv handles installation automatically.

## Bootstrapping a New Project
1. Create new repo
2. Copy `rules.md` and adapt
3. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh` (or Windows equivalent)
4. Initialize project: `uv init`
5. Add dependencies: `uv add django djangorestframework`
6. Create project: `uv run django-admin startproject config .`
7. Follow structure above

This rules file ensures consistency across projects. Update as needed for new standards.