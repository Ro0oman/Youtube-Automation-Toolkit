from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from loguru import logger
from typing import Dict, List, Optional
import uuid
import os
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.youtube_service import YouTubeService
from app.services.analytics_service import AnalyticsService
from app.workflows.engine import WorkflowEngine
from app.models.schemas import AnalyticsResult, WorkflowConfig

app = FastAPI(title="YouTube Automation Toolkit")
scheduler = BackgroundScheduler()
engine = WorkflowEngine()

# In-memory storage for workflow statuses
workflow_jobs: Dict[str, Dict] = {}

class ChannelRequest(BaseModel):
    channel_id: str

@app.on_event("startup")
def startup_event():
    logger.info("Starting YouTube Automation Toolkit API")
    scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    logger.info("Shutting down scheduler")
    scheduler.shutdown()

@app.post("/analyze-channel", response_model=AnalyticsResult)
async def analyze_channel(request: ChannelRequest):
    """Fetch and analyze channel data synchronously"""
    try:
        yt = YouTubeService()
        analytics = AnalyticsService()
        
        channel = yt.get_channel_info(request.channel_id)
        videos = yt.get_videos(request.channel_id, max_results=50)
        
        result = analytics.analyze_channel(channel, videos)
        return result
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run-workflow")
async def run_workflow(config: WorkflowConfig, background_tasks: BackgroundTasks):
    """Run a custom workflow in the background"""
    job_id = str(uuid.uuid4())
    workflow_jobs[job_id] = {"status": "pending", "name": config.name}
    
    background_tasks.add_task(execute_workflow_task, job_id, config)
    
    return {"job_id": job_id, "message": "Workflow started in background"}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    """Check the status of a background workflow job"""
    job = workflow_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

def execute_workflow_task(job_id: str, config: WorkflowConfig):
    """Background task executor"""
    workflow_jobs[job_id]["status"] = "running"
    try:
        result = engine.run(config)
        workflow_jobs[job_id]["status"] = "completed"
        workflow_jobs[job_id]["result"] = result
    except Exception as e:
        logger.error(f"Workflow {job_id} failed: {e}")
        workflow_jobs[job_id]["status"] = "failed"
        workflow_jobs[job_id]["error"] = str(e)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
