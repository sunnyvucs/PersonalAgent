@echo off
echo Starting Agent-SK...
call venv\Scripts\activate
pip install -r requirements.txt -q
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
