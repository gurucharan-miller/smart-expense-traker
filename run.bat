@echo off
echo Starting Smart Expense Tracker...
start http://127.0.0.1:8000/
call .\.venv\Scripts\activate.bat
python manage.py runserver
pause
