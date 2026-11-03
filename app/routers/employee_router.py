from fastapi import APIRouter, HTTPException, Depends
from app.schemas.schemas import EmployeeProfileSchema
from app.database import get_employee_profile, save_employee_profile
from app.auth import get_current_user
from typing import Dict, Any

router = APIRouter(prefix="/api/employee", tags=["Employee Profile"])

PRESET_PROFILES = [
    {
        "id": "high_performer",
        "title": "High Performer (Fast-Track Candidate)",
        "badge": "Promotion Ready",
        "description": "Exemplary rating (5/5), 11 completed initiatives, 45 training hours, positive engagement.",
        "data": {
            "age": 32,
            "department": "Engineering",
            "job_role": "Engineering Lead",
            "education_level": 3,
            "education_field": "Computer Science",
            "monthly_income": 9800.0,
            "years_at_company": 5,
            "years_in_current_role": 3,
            "years_since_last_promotion": 2,
            "total_working_years": 9,
            "performance_rating": 5,
            "projects_completed": 12,
            "training_hours_last_year": 48,
            "overtime": "No",
            "job_satisfaction": 5,
            "work_life_balance": 4,
            "environment_satisfaction": 5,
            "distance_from_home": 8,
            "stock_option_level": 2
        }
    },
    {
        "id": "burnout_attrition",
        "title": "Severe Burnout & Flight Risk",
        "badge": "High Attrition Risk",
        "description": "Consistent overtime, low work-life balance (1/5), long commute, high project load.",
        "data": {
            "age": 29,
            "department": "Engineering",
            "job_role": "Software Engineer",
            "education_level": 2,
            "education_field": "Computer Science",
            "monthly_income": 6200.0,
            "years_at_company": 3,
            "years_in_current_role": 2,
            "years_since_last_promotion": 3,
            "total_working_years": 6,
            "performance_rating": 4,
            "projects_completed": 14,
            "training_hours_last_year": 12,
            "overtime": "Yes",
            "job_satisfaction": 2,
            "work_life_balance": 1,
            "environment_satisfaction": 2,
            "distance_from_home": 38,
            "stock_option_level": 0
        }
    },
    {
        "id": "underpaid_senior",
        "title": "Underpaid Domain Expert",
        "badge": "Equity Adjustment Needed",
        "description": "10 years experience and solid rating, but compensation significantly below market curve.",
        "data": {
            "age": 36,
            "department": "Research & Development",
            "job_role": "Research Scientist",
            "education_level": 4,
            "education_field": "Life Sciences",
            "monthly_income": 4900.0,
            "years_at_company": 7,
            "years_in_current_role": 4,
            "years_since_last_promotion": 4,
            "total_working_years": 11,
            "performance_rating": 4,
            "projects_completed": 9,
            "training_hours_last_year": 28,
            "overtime": "No",
            "job_satisfaction": 3,
            "work_life_balance": 3,
            "environment_satisfaction": 3,
            "distance_from_home": 14,
            "stock_option_level": 1
        }
    },
    {
        "id": "developing_junior",
        "title": "Developing Junior Associate",
        "badge": "Skill Growth Phase",
        "description": "New to company, strong motivation, requires targeted skill training and mentoring.",
        "data": {
            "age": 24,
            "department": "Sales",
            "job_role": "Sales Representative",
            "education_level": 2,
            "education_field": "Marketing",
            "monthly_income": 4100.0,
            "years_at_company": 1,
            "years_in_current_role": 1,
            "years_since_last_promotion": 1,
            "total_working_years": 2,
            "performance_rating": 3,
            "projects_completed": 5,
            "training_hours_last_year": 20,
            "overtime": "No",
            "job_satisfaction": 4,
            "work_life_balance": 4,
            "environment_satisfaction": 4,
            "distance_from_home": 11,
            "stock_option_level": 0
        }
    }
]

@router.get("/profile")
def get_profile(current_user: dict = Depends(get_current_user)):
    profile = get_employee_profile(current_user["id"])
    if not profile:
        raise HTTPException(status_code=404, detail="Employee profile not found.")
    return profile

@router.post("/profile")
def update_profile(profile_data: EmployeeProfileSchema, current_user: dict = Depends(get_current_user)):
    success = save_employee_profile(current_user["id"], profile_data.model_dump())
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save employee profile.")
    return {"success": True, "message": "Employee profile successfully updated."}

@router.get("/presets")
def get_preset_profiles():
    return PRESET_PROFILES

