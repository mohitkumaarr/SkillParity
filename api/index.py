import sys
import os

# Add backend directory to sys.path for Vercel Serverless Function runtime
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from main import app as fastapi_app

app = fastapi_app
handler = fastapi_app
