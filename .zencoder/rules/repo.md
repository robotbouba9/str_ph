# Repository Overview

- Project: Mobile Store Inventory (Flask)
- Entrypoint: app.py (Flask instance: app)
- Web server: gunicorn
- Python: requirements.txt
- Templates: Jinja2 in templates/
- Database: SQLAlchemy (SQLite by default, PostgreSQL via DATABASE_URL)
- Exports: Excel via openpyxl, PDFs via reportlab/weasyprint (if used)

## Environment

- APP_ENV: development|production|testing (uses config.py)
- SECRET_KEY: required in production (auto-generated on Render)
- DATABASE_URL: e.g. postgres://... (auto-normalized to postgresql+psycopg2 in config.py)

## Local Run

```bash
python run_web.py    # dev server 0.0.0.0:5000
```

## Production Run

```bash
gunicorn -w 2 -k gthread -b 0.0.0.0:$PORT app:app
```

## Deployment (Render)

- File: render.yaml present
- Build: pip install -r requirements.txt
- Start: gunicorn -w 2 -k gthread -b 0.0.0.0:$PORT app:app
- Plan: free (ephemeral disk). Use PostgreSQL service for persistence.

## Notes

- If using WeasyPrint on Render, system packages may be required (libcairo2, pango, gdk-pixbuf2, libffi, shared-mime-info).
- SQLite is fine for dev; for production use PostgreSQL.# Repository Overview

- Project: Mobile Store Inventory (Flask)
- Entrypoint: app.py (Flask instance: app)
- Web server: gunicorn
- Python: requirements.txt
- Templates: Jinja2 in templates/
- Database: SQLAlchemy (SQLite by default, PostgreSQL via DATABASE_URL)
- Exports: Excel via openpyxl, PDFs via reportlab/weasyprint (if used)

## Environment

- APP_ENV: development|production|testing (uses config.py)
- SECRET_KEY: required in production (auto-generated on Render)
- DATABASE_URL: e.g. postgres://... (auto-normalized to postgresql+psycopg2 in config.py)

## Local Run

```bash
python run_web.py    # dev server 0.0.0.0:5000
```

## Production Run

```bash
gunicorn -w 2 -k gthread -b 0.0.0.0:$PORT app:app
```

## Deployment (Render)

- File: render.yaml present
- Build: pip install -r requirements.txt
- Start: gunicorn -w 2 -k gthread -b 0.0.0.0:$PORT app:app
- Plan: free (ephemeral disk). Use PostgreSQL service for persistence.

## Notes

- If using WeasyPrint on Render, system packages may be required (libcairo2, pango, gdk-pixbuf2, libffi, shared-mime-info).
- SQLite is fine for dev; for production use PostgreSQL.
