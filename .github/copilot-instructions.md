## Quick orientation for AI coding agents

This project is a Django 4.x REST API (Poetry-managed) with multiple apps (blog, companies, jobs, locations, reviews, users). The goal of these instructions is to surface concrete, discoverable facts so an AI can be productive immediately.

- Project entry points:
  - `manage.py` — standard Django CLI (runserver, makemigrations, migrate).
  - `config/settings.py` — central configuration (DB via env vars; special case when `GITHUB_WORKFLOW` is set for CI).
  - `config/urls.py` — app routers and auth endpoints are mounted here.

- How HTTP endpoints are organized (pattern to follow):
  - Each app typically defines a `routers.py` that registers DRF ViewSets with a router (examples: `companies/routers.py`, `blog/routers.py`, `users/routers.py`). When adding an endpoint, register its ViewSet in the app's `routers.py`, then import/include that router in `config/urls.py`.
  - ViewSets live in `app/views.py`, serializers live in `app/serializers.py`, models in `app/models.py`.

- Authentication & permissions
  - Default REST framework settings in `config/settings.py`: TokenAuthentication and `IsAuthenticated` as the default permission class. Many public auth endpoints are explicitly mounted in `config/urls.py` (e.g., register/login/logout) and may use different classes.

- Data model conventions
  - Most models inherit from `common.models.BaseModel` which provides `created_at`, `modified_at` and `deleted_at` fields — use these fields when reading/creating records.
  - UUID primary keys are used in some models (see `locations/models.py` for examples).

- External integrations & side-effects to be careful with
  - Cloudinary is the default file storage (see `config/settings.py` and `CLOUDINARY_STORAGE`). Avoid making changes that break upload/storage without updating env variables.
  - `locations.models.Address.get_coordinates()` uses GeoPy (Nominatim) and may perform network calls. Tests use `pytest-django` + sqlite (see `conftest.py`) and expect to avoid external network calls; prefer mocking geocoding in tests.

- Tests & developer workflows
  - Tests run with pytest: `pytest -q`. Pytest is configured via `pytest.ini` and test DB uses sqlite override in `conftest.py`.
  - Local dev: `python manage.py runserver`. Standard migration commands are used: `python manage.py makemigrations` and `python manage.py migrate` (see `README.md`).
  - Project metadata: `pyproject.toml` (Poetry) lists core deps. A `requirements.txt` exists (pinned) but the canonical project file is `pyproject.toml`.

- CI considerations
  - When `GITHUB_WORKFLOW` env var is present, `config/settings.py` switches DB config for GitHub Actions (Postgres). If adding DB-related changes, ensure they work with both the env-var conditional and the local env vars.

- Small contract for code changes
  - Inputs: modify or add Django models/views/serializers/routers per app conventions.
  - Outputs: new/modified endpoint available via app router and included in `config/urls.py`; tests should pass under `pytest` using `conftest.py` sqlite override.
  - Error modes: ensure migrations are added when models change; avoid network calls during tests (mock external services like geocoding and Cloudinary).

- Concrete examples to follow
  - Register a nested resource: look at `companies/routers.py` for using `rest_framework_nested` to attach `reviews` and `jobs` under `/companies/{company_pk}/...`.
  - Add an app-level router: create `myapp/routers.py`, register your ViewSets, then include the router in `config/urls.py` similar to existing imports.
  - Auth-protected endpoints: default permission is `IsAuthenticated`. To expose a public endpoint, set permission class explicitly on the View/ViewSet or mount a function-based view under `config/urls.py` like `register/`.

- Edge cases observed in this codebase
  - Many migrations exist — large historical migration chain. Avoid reordering or squashing without coordination.
  - Some commented-out code shows alternative auth (JWT) and session/auth views; don't delete these without confirming intent.

If anything here is unclear or you'd like me to expand sections (example patch for a new router, a test that mocks geocoding, or a checklist for submitting migrations), tell me which part and I'll iterate. 
