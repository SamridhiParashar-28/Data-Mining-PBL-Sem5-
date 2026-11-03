import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.config import DB_PATH

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT UNIQUE,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'employee',
        department TEXT DEFAULT 'Engineering',
        created_at TEXT NOT NULL
    )
    """)
    
    # Employee Profile table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employee_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        age INTEGER DEFAULT 30,
        department TEXT DEFAULT 'Engineering',
        job_role TEXT DEFAULT 'Software Engineer',
        education_level INTEGER DEFAULT 3,
        education_field TEXT DEFAULT 'Computer Science',
        monthly_income REAL DEFAULT 7500.0,
        years_at_company INTEGER DEFAULT 4,
        years_in_current_role INTEGER DEFAULT 2,
        years_since_last_promotion INTEGER DEFAULT 2,
        total_working_years INTEGER DEFAULT 7,
        performance_rating INTEGER DEFAULT 4,
        projects_completed INTEGER DEFAULT 8,
        training_hours_last_year INTEGER DEFAULT 35,
        overtime TEXT DEFAULT 'No',
        job_satisfaction INTEGER DEFAULT 4,
        work_life_balance INTEGER DEFAULT 3,
        environment_satisfaction INTEGER DEFAULT 4,
        distance_from_home INTEGER DEFAULT 10,
        stock_option_level INTEGER DEFAULT 1,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    # Analysis History table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        analysis_type TEXT NOT NULL,
        summary TEXT,
        result_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    conn.commit()
    conn.close()

def create_user(name: str, email: str, password_hash: str, employee_id: str, department: str = "Engineering", role: str = "employee") -> Optional[int]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        now = datetime.utcnow().isoformat()
        cursor.execute(
            "INSERT INTO users (employee_id, name, email, password_hash, role, department, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (employee_id, name, email.lower().strip(), password_hash, role, department, now)
        )
        user_id = cursor.lastrowid
        
        # Initialize default profile
        cursor.execute(
            """INSERT INTO employee_profiles 
            (user_id, age, department, job_role, education_level, education_field, monthly_income,
             years_at_company, years_in_current_role, years_since_last_promotion, total_working_years,
             performance_rating, projects_completed, training_hours_last_year, overtime,
             job_satisfaction, work_life_balance, environment_satisfaction, distance_from_home,
             stock_option_level, updated_at)
            VALUES (?, 29, ?, 'Software Engineer', 3, 'Computer Science', 6800.0, 3, 2, 2, 6, 4, 7, 32, 'No', 4, 3, 4, 12, 1, ?)""",
            (user_id, department, now)
        )
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def seed_demo_user():
    """Seeds a ready-to-test demo user if not already present."""
    from app.auth import hash_password
    demo_email = "alex.rivera@enterprise.ai"
    existing = get_user_by_email(demo_email)
    if not existing:
        pwd_hash = hash_password("Pipeline2026!")
        user_id = create_user(
            name="Alexandra Rivera",
            email=demo_email,
            password_hash=pwd_hash,
            employee_id="EMP-1001",
            department="Engineering",
            role="employee"
        )
        if user_id:
            save_employee_profile(user_id, {
                "age": 31,
                "department": "Engineering",
                "job_role": "Software Engineer",
                "education_level": 3,
                "education_field": "Computer Science",
                "monthly_income": 7600.0,
                "years_at_company": 4,
                "years_in_current_role": 2,
                "years_since_last_promotion": 2,
                "total_working_years": 8,
                "performance_rating": 4,
                "projects_completed": 9,
                "training_hours_last_year": 38,
                "overtime": "No",
                "job_satisfaction": 4,
                "work_life_balance": 3,
                "environment_satisfaction": 4,
                "distance_from_home": 10,
                "stock_option_level": 1
            })
            print("[Database] Demo user alex.rivera@enterprise.ai seeded.")

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_employee_profile(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employee_profiles WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_employee_profile(user_id: int, profile_data: Dict[str, Any]) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    
    # Check if profile exists
    cursor.execute("SELECT id FROM employee_profiles WHERE user_id = ?", (user_id,))
    exists = cursor.fetchone()
    
    fields = [
        "age", "department", "job_role", "education_level", "education_field",
        "monthly_income", "years_at_company", "years_in_current_role",
        "years_since_last_promotion", "total_working_years", "performance_rating",
        "projects_completed", "training_hours_last_year", "overtime",
        "job_satisfaction", "work_life_balance", "environment_satisfaction",
        "distance_from_home", "stock_option_level"
    ]
    
    values = [profile_data.get(f) for f in fields]
    
    if exists:
        set_clause = ", ".join([f"{f} = ?" for f in fields]) + ", updated_at = ?"
        cursor.execute(f"UPDATE employee_profiles SET {set_clause} WHERE user_id = ?", values + [now, user_id])
    else:
        cols = ", ".join(fields) + ", user_id, updated_at"
        placeholders = ", ".join(["?"] * len(fields)) + ", ?, ?"
        cursor.execute(f"INSERT INTO employee_profiles ({cols}) VALUES ({placeholders})", values + [user_id, now])
        
    conn.commit()
    conn.close()
    return True

def log_analysis_history(user_id: int, analysis_type: str, summary: str, result_dict: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute(
        "INSERT INTO analysis_history (user_id, analysis_type, summary, result_json, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, analysis_type, summary, json.dumps(result_dict), now)
    )
    conn.commit()
    conn.close()

def get_user_analysis_history(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, analysis_type, summary, result_json, created_at FROM analysis_history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        item = dict(r)
        try:
            item["result"] = json.loads(item["result_json"])
        except Exception:
            item["result"] = {}
        results.append(item)
    return results

def get_all_users() -> List[Dict[str, Any]]:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, employee_id, name, email, role, department, created_at FROM users ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Ensure tables exist immediately on import
init_db()
