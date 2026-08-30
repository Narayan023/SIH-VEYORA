"""
NutriLens AI - Application Launcher
Starts the FastAPI backend and serves the Single Page Application UI on http://localhost:8000
"""

import sys
import os
import uvicorn

# Configure UTF-8 on Windows
sys.stdout.reconfigure(encoding='utf-8')

# Ensure backend directory is in python search path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database import init_db

if __name__ == "__main__":
    print("=" * 65)
    print("  🥦 NutriLens AI — Personalized Food-to-Fitness Intelligence")
    print("  🏆 Smart India Hackathon (SIH) — Student Innovation Prototype")
    print("=" * 65)
    print("  Initializing SQLite database & Indian food catalog...")
    init_db()
    print("  ✓ Database initialized successfully.")
    print("  Starting FastAPI & Web Application Server...")
    print("  ▶ Application available at: http://localhost:8000")
    print("=" * 65)

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False, app_dir=backend_dir)
