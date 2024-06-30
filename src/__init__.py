import os
import time
from dotenv import load_dotenv

load_dotenv()

# Change time to UTC
os.environ["TZ"] = "UTC"
time.tzset()

APP_ENV = os.environ["APP_ENV"]
IS_LOCAL = os.getenv("IS_LOCAL", False) == "true"

PACKAGE_NAME = "fastapi-service"
__package__ = PACKAGE_NAME
__version__ = "0.1.0"  # Manually set version
__description__ = "A FastAPI service with OpenTelemetry"
__author__ = "MaxC"
__author_email__ = "MaxC@gmail.com"

#TODO: add KUBE stuff here
