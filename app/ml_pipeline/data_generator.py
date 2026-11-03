import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple
from app.config import DATASET_PATH

DEPARTMENTS = ["Engineering", "Sales", "Research & Development", "Human Resources", "Marketing", "Operations"]

ROLES_BY_DEPT = {
    "Engineering": ["Software Engineer", "Systems Architect", "QA Engineer", "DevOps Engineer", "Engineering Lead"],
    "Sales": ["Sales Executive", "Account Manager", "Sales Representative", "Sales Director"],
    "Research & Development": ["Research Scientist", "Laboratory Technician", "R&D Manager"],
    "Human Resources": ["HR Specialist", "Recruiter", "HR Manager"],
    "Marketing": ["Marketing Specialist", "Brand Strategist", "Digital Marketer"],
    "Operations": ["Operations Analyst", "Logistics Coordinator", "Operations Manager"]
}

EDUCATION_FIELDS = ["Computer Science", "Life Sciences", "Medical", "Marketing", "Technical Degree", "Business"]

def generate_synthetic_dataset(num_samples: int = 1500, random_state: int = 42, save: bool = True) -> pd.DataFrame:
    """
    Generates a realistic, highly educational HR employee dataset.
    Features include demographic, organizational, compensation, and psychometric metrics.
    Includes natural class imbalance (~16% promotion, ~18% attrition) and minor missing values
    to showcase genuine data mining preprocessing steps (imputation, scaling, outlier removal).
    """
    np.random.seed(random_state)
    
    # 1. Demographics & Tenure
    age = np.clip(np.random.normal(37, 8, num_samples).astype(int), 21, 62)
    total_working_years = np.clip(age - 21 - np.random.randint(0, 4, num_samples), 0, 40)
    years_at_company = np.array([np.random.randint(0, max(1, twy + 1)) for twy in total_working_years])
    years_in_current_role = np.array([np.random.randint(0, max(1, yac + 1)) for yac in years_at_company])
    years_since_last_promotion = np.array([np.random.randint(0, max(1, yicr + 1)) for yicr in years_in_current_role])
    
    # 2. Department & Role
    departments = np.random.choice(DEPARTMENTS, size=num_samples, p=[0.30, 0.22, 0.20, 0.08, 0.10, 0.10])
    job_roles = [np.random.choice(ROLES_BY_DEPT[dept]) for dept in departments]
    
    # 3. Education
    education_level = np.random.choice([1, 2, 3, 4], size=num_samples, p=[0.12, 0.38, 0.40, 0.10])  # 1:HS, 2:Bach, 3:Master, 4:PhD
    education_field = np.random.choice(EDUCATION_FIELDS, size=num_samples)
    
    # 4. Compensation (correlated with experience, education, role)
    base_salary = 3200 + (total_working_years * 380) + (education_level * 600) + np.random.normal(0, 900, num_samples)
    monthly_income = np.clip(base_salary, 2400, 24000).round(2)
    
    # 5. Performance & Engagement Metrics
    performance_rating = np.random.choice([1, 2, 3, 4, 5], size=num_samples, p=[0.05, 0.15, 0.50, 0.22, 0.08])
    projects_completed = np.clip(np.random.poisson(lam=7, size=num_samples), 1, 25)
    training_hours_last_year = np.clip(np.random.normal(34, 14, num_samples).astype(int), 0, 95)
    
    overtime_prob = np.where(departments == "Sales", 0.40, 0.25)
    overtime = np.array(["Yes" if np.random.rand() < p else "No" for p in overtime_prob])
    
    job_satisfaction = np.random.choice([1, 2, 3, 4, 5], size=num_samples, p=[0.10, 0.18, 0.42, 0.22, 0.08])
    work_life_balance = np.random.choice([1, 2, 3, 4, 5], size=num_samples, p=[0.10, 0.20, 0.45, 0.18, 0.07])
    environment_satisfaction = np.random.choice([1, 2, 3, 4, 5], size=num_samples, p=[0.08, 0.20, 0.44, 0.20, 0.08])
    distance_from_home = np.clip(np.random.exponential(scale=12, size=num_samples).astype(int), 1, 60)
    stock_option_level = np.random.choice([0, 1, 2, 3], size=num_samples, p=[0.40, 0.35, 0.18, 0.07])
    
    # 6. Targets Construction with Realistic Correlational Logits
    # Promotion Target (Imbalanced ~ 16-18% positive)
    promo_score = (
        0.75 * (performance_rating - 3)
        + 0.12 * (projects_completed - 7)
        + 0.03 * (training_hours_last_year - 33)
        + 0.40 * (years_in_current_role >= 2).astype(int)
        - 0.35 * (years_since_last_promotion >= 3).astype(int)
        + 0.25 * (overtime == "Yes").astype(int)
        + 0.20 * (job_satisfaction >= 4).astype(int)
        + np.random.normal(0, 0.5, num_samples)
    )
    # Target top ~17% for promotion
    promo_threshold = np.percentile(promo_score, 83)
    promoted = (promo_score >= promo_threshold).astype(int)
    
    # Attrition Target (Imbalanced ~ 16-18% positive)
    attrition_score = (
        1.10 * (overtime == "Yes").astype(int)
        - 0.55 * (job_satisfaction - 3)
        - 0.50 * (work_life_balance - 3)
        + 0.02 * (distance_from_home - 12)
        - 0.35 * stock_option_level
        - 0.00012 * (monthly_income - 6500)
        + 0.30 * (years_since_last_promotion >= 3).astype(int)
        + np.random.normal(0, 0.5, num_samples)
    )
    # Target top ~17% for attrition risk
    attrition_threshold = np.percentile(attrition_score, 83)
    attrition = (attrition_score >= attrition_threshold).astype(int)
    
    # Performance Category (Multi-class: Low, Medium, High)
    perf_score = (
        performance_rating * 0.4 
        + (projects_completed / 10.0) * 0.3 
        + (training_hours_last_year / 40.0) * 0.2 
        + (1.0 if overtime[0] == "Yes" else 0.0) * 0.1
    )
    # Thresholds for categories
    perf_cat = []
    for pr, pc, th in zip(performance_rating, projects_completed, training_hours_last_year):
        score = pr * 0.4 + (pc / 8.0) * 0.35 + (th / 35.0) * 0.25
        if score < 2.3:
            perf_cat.append("Needs Improvement")
        elif score > 3.6:
            perf_cat.append("Top Performer")
        else:
            perf_cat.append("Strong Contributor")
            
    employee_ids = [f"EMP-{1001 + i}" for i in range(num_samples)]
    
    df = pd.DataFrame({
        "employee_id": employee_ids,
        "age": age,
        "department": departments,
        "job_role": job_roles,
        "education_level": education_level,
        "education_field": education_field,
        "monthly_income": monthly_income,
        "years_at_company": years_at_company,
        "years_in_current_role": years_in_current_role,
        "years_since_last_promotion": years_since_last_promotion,
        "total_working_years": total_working_years,
        "performance_rating": performance_rating,
        "projects_completed": projects_completed,
        "training_hours_last_year": training_hours_last_year,
        "overtime": overtime,
        "job_satisfaction": job_satisfaction,
        "work_life_balance": work_life_balance,
        "environment_satisfaction": environment_satisfaction,
        "distance_from_home": distance_from_home,
        "stock_option_level": stock_option_level,
        "promoted": promoted,
        "attrition": attrition,
        "performance_category": perf_cat
    })
    
    # 7. Inject ~2.5% Missing Values intentionally in realistic columns for preprocessing showcase
    missing_indices = np.random.choice(num_samples, size=int(num_samples * 0.025), replace=False)
    df.loc[missing_indices, "training_hours_last_year"] = np.nan
    
    missing_inc_indices = np.random.choice(num_samples, size=int(num_samples * 0.02), replace=False)
    df.loc[missing_inc_indices, "monthly_income"] = np.nan
    
    # 8. Inject 4-5 extreme outliers in monthly_income and distance_from_home to showcase IQR outlier handling
    outlier_indices = np.random.choice(num_samples, size=5, replace=False)
    df.loc[outlier_indices[0], "monthly_income"] = 48500.0  # Massive salary outlier
    df.loc[outlier_indices[1], "distance_from_home"] = 125    # Distance outlier
    
    if save:
        DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(DATASET_PATH, index=False)
        print(f"[Dataset] Generated {num_samples} records and saved to {DATASET_PATH}")
        print(f"  - Promotion Rate: {promoted.mean()*100:.1f}% ({promoted.sum()} positive)")
        print(f"  - Attrition Rate: {attrition.mean()*100:.1f}% ({attrition.sum()} positive)")
        
    return df

if __name__ == "__main__":
    generate_synthetic_dataset()
