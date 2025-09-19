Blog with Admin-only Writing and Dark/Midnight Theme

Quickstart

- Python 3.10+
- PowerShell commands below are for Windows.

Setup

1) Create and activate a virtualenv

   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

2) Install dependencies

   pip install -r requirements.txt

3) Set environment variables (recommended)

   $env:FLASK_APP = "app.py"
   $env:SECRET_KEY = "change-this-secret"
   $env:ADMIN_PASSWORD = "your-strong-password"

4) Run the app

   python app.py

   Or with Flask dev server:
   flask run --reload

Usage

- Public: Home page lists published posts; click to read.
- Theme: Click the moon/sun button to toggle light/midnight. Preference saves in localStorage.
- Admin: Login at /admin/login using ADMIN_PASSWORD. Create, edit, publish/unpublish, and delete posts.

Notes

- A local SQLite database file (blog.db) is created on first run.
- Default admin password is "changeme" if ADMIN_PASSWORD is not set (change it!).
- Posts are written in Markdown and safely sanitized before rendering.

