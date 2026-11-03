from fastapi import APIRouter, HTTPException, Depends
from app.database import get_all_users
from app.ml_pipeline.pipeline_manager import pipeline_manager
import pandas as pd

router = APIRouter(prefix="/api/admin", tags=["Admin & Dataset Explorer"])

@router.get("/stats")
def get_admin_dataset_stats():
    """Provides high-level dataset analytics, distribution breakdown, and registered user directory."""
    if not pipeline_manager.is_initialized:
        pipeline_manager.initialize()

    df = pipeline_manager.raw_df
    users = get_all_users()

    dept_counts = df["department"].value_counts().to_dict()
    dept_salaries = df.groupby("department")["monthly_income"].mean().round(2).to_dict()
    dept_attrition = (df.groupby("department")["attrition"].mean() * 100).round(1).to_dict()
    dept_promotion = (df.groupby("department")["promoted"].mean() * 100).round(1).to_dict()

    education_counts = {
        "High School (1)": int((df["education_level"] == 1).sum()),
        "Bachelor's (2)": int((df["education_level"] == 2).sum()),
        "Master's (3)": int((df["education_level"] == 3).sum()),
        "Doctorate (4)": int((df["education_level"] == 4).sum())
    }

    return {
        "dataset_summary": {
            "total_samples": len(df),
            "total_features": len(df.columns),
            "overall_promotion_rate": round(float(df["promoted"].mean() * 100), 1),
            "overall_attrition_rate": round(float(df["attrition"].mean() * 100), 1),
            "average_salary": round(float(df["monthly_income"].mean()), 2),
            "average_experience": round(float(df["total_working_years"].mean()), 1),
            "average_age": round(float(df["age"].mean()), 1)
        },
        "department_analytics": {
            "counts": dept_counts,
            "average_salaries": dept_salaries,
            "attrition_rates": dept_attrition,
            "promotion_rates": dept_promotion
        },
        "education_distribution": education_counts,
        "registered_users_count": len(users),
        "registered_users": users
    }

