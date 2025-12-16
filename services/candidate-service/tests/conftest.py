import sys
from pathlib import Path

# Ensure tests import the candidate-service main module
service_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(service_dir))
