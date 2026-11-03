from fastapi import APIRouter, HTTPException, Depends, Response
from app.schemas.schemas import RetrainPipelineRequest
from app.ml_pipeline.pipeline_manager import pipeline_manager
import json

router = APIRouter(prefix="/api/pipeline", tags=["Pipeline Visualization & Diagnostics"])

@router.get("/visualize")
def get_pipeline_telemetry():
    """Returns comprehensive 8-stage data mining pipeline telemetry."""
    data = pipeline_manager.get_pipeline_visualization_data()
    return data

@router.post("/retrain")
def retrain_pipeline(params: RetrainPipelineRequest):
    """Re-executes the data mining pipeline with user-customized hyperparameters."""
    try:
        updated_data = pipeline_manager.retrain_pipeline(
            test_size=params.test_size,
            n_estimators=params.n_estimators,
            apply_smote=params.apply_smote,
            random_state=params.random_state
        )
        return {
            "success": True,
            "message": "Pipeline successfully retrained with updated hyperparameters!",
            "telemetry": updated_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrain pipeline: {str(e)}")

@router.get("/export-config")
def export_pipeline_configuration():
    """Exports full pipeline architecture and evaluation metrics as JSON."""
    data = pipeline_manager.get_pipeline_visualization_data()
    json_bytes = json.dumps(data, indent=2).encode("utf-8")
    
    response = Response(content=json_bytes, media_type="application/json")
    response.headers["Content-Disposition"] = "attachment; filename=pipeline_configuration_audit.json"
    return response

