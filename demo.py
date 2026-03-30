import sys
import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from app.domain.models import Channel, ChannelStats, Video, VideoMetadata, VideoStats
from app.services.analytics_service import AnalyticsService
from app.infra.report_generator import ReportGenerator
from app.infra.database import engine, Base, SessionLocal
from app.infra.repository import AnalyticsRepository
from loguru import logger

def run_demo():
    logger.info("🚀 Starting YouTube Intelligence PRO - DEMO MODE")
    logger.info("No API Key required. Generating showcase data...")

    # 1. Setup Database
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    repo = AnalyticsRepository(db)

    # 2. Setup Mock Data (Perfect Channel)
    channel = Channel(
        id="UC_SHOWCASE_123",
        title="Gaming Excellence Pro",
        description="The ultimate destination for pro-level gameplay and tutorials.",
        publishedAt=datetime.now() - timedelta(days=365),
        stats=ChannelStats(viewCount=1500000, subscriberCount=12500, videoCount=84)
    )

    # Generate some mock videos
    videos = []
    base_date = datetime.now()
    for i in range(10):
        v_id = f"vid_{i}"
        videos.append(Video(
            metadata=VideoMetadata(
                id=v_id,
                title=f"HOW TO MASTER THE NEW {['MAP', 'WEAPON', 'AGENT'][i%3]} 🤯",
                description="Tutorial description...",
                publishedAt=base_date - timedelta(days=i*4),
                thumbnails={"default": {"url": ""}},
                tags=["gaming", "tutorial"]
            ),
            stats=VideoStats(
                viewCount=12000 - (i * 800),
                likeCount=600 - (i * 40),
                commentCount=45 - (i * 3)
            )
        ))

    # 3. Run Analysis
    analytics = AnalyticsService(repository=repo)
    result = analytics.analyze_channel(channel, videos)

    # 4. Generate Report
    report_gen = ReportGenerator()
    report_path = report_gen.generate(channel, result)

    logger.success(f"✅ Demo Analysis Complete!")
    logger.info(f"📊 Channel Score: {result.score.overall_score}/10")
    logger.info(f"📄 Report Generated at: {report_path}")
    
    db.close()
    
    print("\n" + "="*50)
    print("DEMO SUCCESSFUL")
    print(f"Open this file in your browser: {os.path.abspath(report_path)}")
    print("="*50)

if __name__ == "__main__":
    run_demo()
