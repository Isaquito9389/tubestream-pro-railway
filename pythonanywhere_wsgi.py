# ============================================================
# PythonAnywhere WSGI Configuration
# Remplacer [your-username] par votre vrai username
# ============================================================

import sys
import os

# Add project directory to sys.path
project_home = '/home/[your-username]/tubestream'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Environment variables
os.environ['DOWNLOAD_DIR'] = '/home/[your-username]/downloads'
os.environ['FLASK_DEBUG'] = 'false'

# Import Flask app (module `app`, variable `app` dans app.py)
from app import app as application

# Ensure required directories exist
os.makedirs(os.path.join(project_home, 'templates'), exist_ok=True)
os.makedirs(os.path.join(project_home, 'downloads'), exist_ok=True)
