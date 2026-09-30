# VTAB Office Suite 365

VTAB 365 is a centralized enterprise workspace portal. It serves as an application launcher and a Single Sign-On (SSO) Identity Provider for downstream corporate applications.

## Features
* **Secure Authentication:** Passwordless-style OTP verification via Brevo email API.
* **SSO Provider:** Generates cryptographically signed JWT assertions for downstream apps.
* **Workspace Launcher:** Role-based application grids and customizable "Quick Access" tiles.
* **Admin Portal:** Full CRUD management for applications, user roles, and release announcements.
* **Audit Trail:** Comprehensive security logging for logins, app launches, and administrative actions.

## Prerequisites
* **Python 3.10+**
* **PostgreSQL Database** (e.g., Supabase)
* **Brevo Account** (for sending OTP emails)

## Environment Variables
The application strictly follows 12-factor app principles. You must define the following environment variables before starting the server (typically handled in `start_server.py`):

* `DATABASE_URL` - Your PostgreSQL connection string.
* `VTAB_SECRET_KEY` - A secure random string used to cryptographically sign HTTP sessions.
* `VTAB_SSO_SECRET` - A secure random string used to sign outgoing SSO JWTs.
* `BREVO_API_KEY` - Your Brevo v3 API key for sending emails.

## Running the Application
1. Ensure your dependencies are installed (e.g., `psycopg2`).
2. Do not commit `start_server.py` if it contains hardcoded secrets (it is in `.gitignore`).
3. Run the server:
   ```bash
   python start_server.py
   ```
4. Open your browser and navigate to `http://localhost:8000`.

## Architecture
This application is built as a lightweight, zero-dependency (framework-wise) Python server using `BaseHTTPRequestHandler` and `ThreadingHTTPServer`. It uses standard HTML/CSS/JS on the frontend with server-side rendering.
