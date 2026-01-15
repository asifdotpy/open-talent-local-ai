import os
import sys

# Add the service root directory to sys.path
# This allows 'from app.main import app' to work in tests
service_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if service_root not in sys.path:
    sys.path.insert(0, service_root)
