from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any

class UserSignUp(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    employee_id: Optional[str] = None
    department: Optional[str] = "Engineering"

class UserSignIn(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class EmployeeProfileSchema(BaseModel):
    age: int = Field(30, ge=18, le=70)
    department: str = Field("Engineering")
    job_role: str = Field("Software Engineer")
    education_level: int = Field(3, ge=1, le=4)
    education_field: str = Field("Computer Science")
    monthly_income: float = Field(7500.0, ge=1000.0, le=50000.0)
    years_at_company: int = Field(4, ge=0, le=40)
    years_in_current_role: int = Field(2, ge=0, le=30)
    years_since_last_promotion: int = Field(2, ge=0, le=25)
    total_working_years: int = Field(7, ge=0, le=50)
    performance_rating: int = Field(4, ge=1, le=5)
    projects_completed: int = Field(8, ge=0, le=40)
    training_hours_last_year: int = Field(35, ge=0, le=200)
    overtime: str = Field("No")
    job_satisfaction: int = Field(4, ge=1, le=5)
    work_life_balance: int = Field(3, ge=1, le=5)
    environment_satisfaction: int = Field(4, ge=1, le=5)
    distance_from_home: int = Field(10, ge=1, le=100)
    stock_option_level: int = Field(1, ge=0, le=3)

class AnalysisRequest(BaseModel):
    analysis_type: str = Field(..., description="promotion, attrition, performance, skill_gap, compensation")
    profile_data: Optional[EmployeeProfileSchema] = None

class RetrainPipelineRequest(BaseModel):
    test_size: float = Field(0.2, ge=0.1, le=0.4)
    n_estimators: int = Field(100, ge=20, le=300)
    apply_smote: bool = True
    random_state: int = 42

