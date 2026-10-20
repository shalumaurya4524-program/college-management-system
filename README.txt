COLLEGE MANAGEMENT SYSTEM — RUN GUIDE
=====================================

TECH STACK
- Frontend: HTML, CSS, JavaScript
- Backend: Python Flask
- SQL database: SQLite (database file is created automatically)

REQUIREMENTS
- Python 3.10 or newer
- Internet is optional at runtime; Google Fonts are used only for visual styling.

RUN ON WINDOWS (VS CODE)
1. Extract the ZIP file.
2. Open the College_Management_System folder in VS Code.
3. Open Terminal > New Terminal.
4. Create a virtual environment (optional but recommended):
   python -m venv .venv
5. Activate it:
   PowerShell: .\.venv\Scripts\Activate.ps1
   If activation is blocked, use Command Prompt:
   .venv\Scripts\activate.bat
6. Install Flask:
   python -m pip install -r requirements.txt
7. Start the application:
   python app.py
8. Open the URL shown in the terminal, usually:
   http://127.0.0.1:5000

DEMO LOGIN
Username: admin
Password: admin123

FEATURES
- Admin login/logout
- Dashboard counts and recent students
- Student create/list/search/delete
- Faculty create/list/delete
- Course create/list/delete
- Attendance create/list (one status per student/date; can be updated)
- Results create/list with grade calculation
- SQLite database initialized automatically with sample records

IMPORTANT
- This is a classroom/demo project. The demo login is hard-coded and is NOT
  suitable for production use. Do not deploy publicly as-is.
- For a real deployment, use hashed passwords, CSRF protection, authorization
  for each role, environment-based secret keys, validation, and secure hosting.
- Data is saved in college.db in this folder. Keep a backup before deleting it.
- To reset the sample database, stop the server and delete college.db, then run
  python app.py again.
