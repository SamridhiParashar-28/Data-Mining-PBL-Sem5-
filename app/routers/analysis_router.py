from fastapi import APIRouter, HTTPException, Depends, Response
from app.schemas.schemas import AnalysisRequest
from app.database import get_employee_profile, log_analysis_history, get_user_analysis_history
from app.auth import get_current_user
from app.ml_pipeline.pipeline_manager import pipeline_manager
import io
import csv

router = APIRouter(prefix="/api/analysis", tags=["Employee Analysis"])

@router.post("/run")
def run_analysis(request: AnalysisRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    # Use profile from request or database
    if request.profile_data:
        profile_dict = request.profile_data.model_dump()
    else:
        profile_dict = get_employee_profile(user_id)
        if not profile_dict:
            raise HTTPException(status_code=400, detail="Please submit your employee profile first.")

    # Execute ML inferences
    results = pipeline_manager.predict_employee(profile_dict, analysis_type=request.analysis_type)
    
    # Format summary for history
    summary_text = ""
    if "promotion" in results:
        summary_text += f"Promotion: {results['promotion']['probability_pct']}% | "
    if "attrition" in results:
        summary_text += f"Attrition: {results['attrition']['risk_tier']} ({results['attrition']['attrition_pct']}%) | "
    if "performance" in results:
        summary_text += f"Score: {results['performance']['composite_score']} | "
    if "compensation" in results:
        summary_text += f"Comp: {results['compensation']['status']} | "
    
    summary_text = summary_text.rstrip(" | ")

    # Log to database
    log_analysis_history(user_id, request.analysis_type, summary_text, results)

    return {
        "success": True,
        "employee_name": current_user["name"],
        "employee_id": current_user["employee_id"],
        "analysis_type": request.analysis_type,
        "results": results
    }

@router.get("/history")
def get_history(current_user: dict = Depends(get_current_user)):
    history = get_user_analysis_history(current_user["id"], limit=15)
    return history

@router.get("/export-csv")
def export_csv_report(current_user: dict = Depends(get_current_user)):
    profile = get_employee_profile(current_user["id"])
    if not profile:
        raise HTTPException(status_code=404, detail="No profile found to export.")

    # Run full analysis
    results = pipeline_manager.predict_employee(profile, analysis_type="all")

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["EMPLOYEE PERFORMANCE & PREDICTION PIPELINE - INDIVIDUAL REPORT"])
    writer.writerow([])
    writer.writerow(["Employee ID", current_user["employee_id"]])
    writer.writerow(["Name", current_user["name"]])
    writer.writerow(["Email", current_user["email"]])
    writer.writerow(["Department", profile.get("department")])
    writer.writerow(["Job Role", profile.get("job_role")])
    writer.writerow(["Monthly Income", f"${profile.get('monthly_income', 0):,.2f}"])
    writer.writerow(["Total Experience", f"{profile.get('total_working_years')} Years"])
    writer.writerow([])
    writer.writerow(["DATA MINING PIPELINE ANALYSIS RESULTS"])
    writer.writerow(["Metric / Pipeline Stage", "Model Output", "Confidence / Details"])

    promo = results.get("promotion", {})
    writer.writerow(["Promotion Readiness", promo.get("prediction", "N/A"), f"{promo.get('probability_pct', 0)}% (Confidence: {promo.get('confidence_pct', 0)}%)"])

    attr = results.get("attrition", {})
    writer.writerow(["Attrition Risk Tier", attr.get("risk_tier", "N/A"), f"{attr.get('attrition_pct', 0)}% (Confidence: {attr.get('confidence_pct', 0)}%)"])

    perf = results.get("performance", {})
    writer.writerow(["Performance Band", perf.get("performance_band", "N/A"), f"Score: {perf.get('composite_score', 0)} (Percentile: {perf.get('percentile', 0)}%)"])

    comp = results.get("compensation", {})
    writer.writerow(["Compensation Fairness", comp.get("status", "N/A"), f"Actual: ${comp.get('actual_salary', 0):,.2f} vs Market Benchmark: ${comp.get('benchmark_salary', 0):,.2f} ({comp.get('equity_ratio_pct', 0)}%)"])

    skill = results.get("skill_gap", {})
    writer.writerow(["Skill Development Status", skill.get("status", "N/A"), f"Target: {skill.get('recommended_target_hours', 45)} hrs / Completed: {skill.get('current_training_hours', 0)} hrs"])

    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=employee_{current_user['employee_id']}_report.csv"
    return response

