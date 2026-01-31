# expats

A Django application for managing expatriate data, including blogs, companies, jobs, locations, and reviews.

## Prerequisites

- Python 3.13
- Poetry (for dependency management)

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd expats
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Set up the database:
   ```bash
   poetry run python manage.py migrate
   ```

4. (Optional) Create a superuser:
   ```bash
   poetry run python manage.py createsuperuser
   ```

5. (Optional) Load initial data:
   ```bash
   poetry run python manage.py loaddata fixtures/companies.json fixtures/countries.json
   ```

## Running the Application

To start the development server:
```bash
poetry run python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`.

## Running Tests

To run the test suite:
```bash
poetry run pytest
```

For test coverage:
```bash
poetry run pytest --cov
```

## Development Workflow

- Make changes to models or code
- Create migrations if needed:
  ```bash
  poetry run python manage.py makemigrations
  ```
- Apply migrations:
  ```bash
  poetry run python manage.py migrate
  ```
- Run tests to ensure everything works
- Commit your changes

## Project Structure

- `apps/`: Django apps (blog, companies, jobs, locations, reviews, users, common)
- `config/`: Django settings
- `fixtures/`: Initial data
- `pyproject.toml`: Poetry dependencies