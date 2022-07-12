from waitress import serve
from src.app import app
import os

serve(app, host='0.0.0.0', port=os.getenv('PORT'))