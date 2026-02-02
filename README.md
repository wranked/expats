# expats

A Django application for managing expatriate data, including blogs, companies, jobs, locations, and reviews.

## Prerequisites

- Python 3.13
- uv (for dependency management)

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd expats
   ```

2. Install uv (if not already installed):
   ```bash
   # Windows (PowerShell)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Install dependencies:
   ```bash
   uv sync
   ```

4. Set up the database:
   ```bash
   uv run python manage.py migrate
   ```

5. (Optional) Create a superuser:
   ```bash
   uv run python manage.py createsuperuser
   ```

6. (Optional) Load initial data:
   ```bash
   uv run python manage.py loaddata fixtures/companies.json fixtures/countries.json
   ```

## Running the Application

To start the development server:
```bash
uv run python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`.

## Running Tests

To run the test suite:
```bash
uv run pytest
```

For test coverage:
```bash
uv run pytest --cov
```

## Development Workflow

- Make changes to models or code
- Create migrations if needed:
  ```bash
  uv run python manage.py makemigrations
  ```
- Apply migrations:
  ```bash
  uv run python manage.py migrate
  ```
- Run tests to ensure everything works
- Commit your changes

## Managing Dependencies

- Add a package:
  ```bash
  uv add <package-name>
  ```
- Remove a package:
  ```bash
  uv remove <package-name>
  ```
- Update dependencies:
  ```bash
  uv lock --upgrade
  ```

## Project Structure

- `apps/`: Django apps (blog, companies, jobs, locations, reviews, users, common)
- `config/`: Django settings
- `fixtures/`: Initial data
- `pyproject.toml`: Project metadata and dependencies (PEP 621)
- `uv.lock`: Locked dependencies for reproducible installs