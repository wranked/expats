uv sync
uv run python manage.py migrate --noinput
uv run python manage.py collectstatic --noinput --clear