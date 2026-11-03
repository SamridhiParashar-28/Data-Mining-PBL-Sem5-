import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

DB_PATH = DATA_DIR / "employee_pipeline.db"
DATASET_PATH = DATA_DIR / "synthetic_employee_data.csv"
ARTIFACTS_PATH = DATA_DIR / "pipeline_cache.joblib"

SECRET_KEY = "dm_pbl_employee_pipeline_super_secret_jwt_key_2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

