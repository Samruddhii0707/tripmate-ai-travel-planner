# TRIPMATE AI – Intelligent & Personalized Travel Planning System

A beginner-friendly Flask + SQLite college PBL MVP. It contains working authentication, trip generation, budget calculation, itinerary modification, hotels, simulated bookings, travel history, dashboard, multilingual UI and an AI-style assistant.

## Run
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. `python -m venv venv`
4. Windows: `venv\Scripts\activate`
5. `pip install -r requirements.txt`
6. `python app.py`
7. Open `http://127.0.0.1:5000`

Demo login:
- Email: `demo@tripmate.ai`
- Password: `demo123`

## Notes
- SQLite database is created automatically.
- Transport and hotel results are demo data.
- Weather, maps and external travel APIs are represented as API-ready integration points in the UI.
- The recommendation engine is rule-based and personalised from destination, budget, duration, travellers and travel style.
- For production, replace demo authentication with Flask-Login, password hashing such as Werkzeug, CSRF protection, secure secrets, and real API credentials.
