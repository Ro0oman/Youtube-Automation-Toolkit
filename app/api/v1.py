from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infra.database import get_db
from app.infra.repository import AnalyticsRepository
from app.services.youtube_service import YouTubeService
from app.services.analytics_service import AnalyticsService
from app.infra.report_generator import ReportGenerator
from app.domain.models import AnalyticsResult
from pydantic import BaseModel
import os

router = APIRouter()

class ChannelRequest(BaseModel):
    channel_id: str
    max_results: int = 20

@router.post("/analyze-channel", response_model=AnalyticsResult)
async def analyze_channel(request: ChannelRequest, db: Session = Depends(get_db)):
    """Fetch, analyze, and persist channel data"""
    try:
        repo = AnalyticsRepository(db)
        yt = YouTubeService()
        analytics = AnalyticsService(repository=repo)
        
        # 1. Fetch
        channel = yt.get_channel_info(request.channel_id)
        videos = yt.get_videos(request.channel_id, max_results=request.max_results)
        
        # 2. Analyze & Persist (repo is injected into service)
        result = analytics.analyze_channel(channel, videos)
        
        # 3. Generate Report
        report_gen = ReportGenerator()
        report_gen.generate(channel, result)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{channel_id}")
async def get_history(channel_id: str, db: Session = Depends(get_db)):
    """Retrieve historical analysis for a channel"""
    repo = AnalyticsRepository(db)
    history = repo.get_history(channel_id)
    return history

@router.get("/report/latest/{channel_id}")
async def get_latest_report(channel_id: str, db: Session = Depends(get_db)):
    """Get path to the latest generated report"""
    repo = AnalyticsRepository(db)
    last = repo.get_last_analysis(channel_id)
    if not last:
        raise HTTPException(status_code=404, detail="No analysis found for this channel")
    
    # Logic to find the newest .html file for this channel in reports/
    reports_dir = "reports"
    files = [f for f in os.listdir(reports_dir) if f.startswith(f"report_{channel_id}_")]
    if not files:
        raise HTTPException(status_code=404, detail="Report file not found")
    
    latest_file = sorted(files)[-1]
    return {"report_path": os.path.join(reports_dir, latest_file)}
