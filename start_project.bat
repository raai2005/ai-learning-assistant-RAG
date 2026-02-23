@echo off
echo Starting AI Learning Assistant...
start cmd /k "echo Starting Backend... && cd backend && .\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"
start cmd /k "echo Starting Frontend... && cd frontend && npm run dev"
echo Services are launching in separate windows!
pause
