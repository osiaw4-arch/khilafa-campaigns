# Islamic History (Flask)
Local:
  pip install -r requirements.txt
  python islamic_history_app.py
  # open http://127.0.0.1:8000

Render:
  Build:  pip install -r requirements.txt
  Start:  gunicorn -b 0.0.0.0:$PORT islamic_history_app:app
