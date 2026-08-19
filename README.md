# Vtab Office Suite 365 — Python Edition V7

V7 is a fully source-based rebuild compatible with Python 3.14. It removes the version-specific `runtime.pkl` and `cloudpickle` components used in V6.

## Run in VS Code

Open this folder and run:

```powershell
python app.py
```

Or use your selected Python 3.14 interpreter:

```powershell
& C:\Users\ADMIN\AppData\Local\Python\pythoncore-3.14-64\python.exe app.py
```

Then open <http://127.0.0.1:8000>.

Keep the following files together:

- `app.py`
- `style.css`
- `app.js`
- `vtab_office_suite.db`

No third-party Python packages, Node.js, React, Flask or npm are required.

## Demo accounts

| Access | Email | Password |
|---|---|---|
| Administrator | `admin@vtaboffice365.com` | `Admin@123` |
| Employee | `user@vtaboffice365.com` | `User@123` |

Change these passwords before using real company data.

## Included functionality

- Unified database-backed login and secure sessions
- Quick Access customization
- General and administrator-only application launchers
- Application creation, visibility, logo and brand-color controls
- Release publishing and detailed release centre
- HR leave requests, self-appraisals and payroll payslip downloads
- Security audit history and application registry API
- Responsive desktop and mobile interface

## Configuration

```powershell
$env:VTAB_SECRET_KEY = "replace-with-a-long-random-secret"
$env:VTAB_HOST = "127.0.0.1"
$env:VTAB_PORT = "8000"
python app.py
```

Set `VTAB_DB_PATH` to use a different SQLite database location.
