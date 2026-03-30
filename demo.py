from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from app.workflows.engine import WorkflowEngine
from app.models.schemas import Channel, ChannelStats, Video, VideoMetadata, VideoStats, AnalyticsResult
from loguru import logger
import os

# --- Mock Data Setup ---

def get_mock_channel(*args, **kwargs):
    return Channel(
        id="UC_MOCK_123",
        title="Python Automation Pro",
        description="A channel dedicated to Python and Automation.",
        publishedAt=datetime.now() - timedelta(days=365),
        stats=ChannelStats(viewCount=1500000, subscriberCount=25000, videoCount=120)
    )

def get_mock_videos(*args, **kwargs):
    return [
        Video(
            metadata=VideoMetadata(
                id=f"vid_{i}",
                title=f"How to automate YouTube with Python - Part {i}",
                description="Tutorial on YouTube API.",
                publishedAt=datetime.now() - timedelta(days=i*5),
                thumbnails={}
            ),
            stats=VideoStats(viewCount=1000 * (10-i), likeCount=50 * (i+1), commentCount=10)
        ) for i in range(5)
    ]

# --- Demo Execution ---

@patch('app.services.youtube_service.YouTubeService.get_channel_info', side_effect=get_mock_channel)
@patch('app.services.youtube_service.YouTubeService.get_videos', side_effect=get_mock_videos)
@patch('app.services.notification_service.NotificationService.notify')
def run_demo(mock_notify, mock_videos, mock_channel):
    logger.info("Starting YouTube Automation Toolkit - Mock Demo")
    
    # Ensure reports directory exists
    os.makedirs("reports", exist_ok=True)
    
    # Initialize Engine
    engine = WorkflowEngine()
    
    # Load the example workflow
    workflow_path = "app/workflows/weekly_report.yaml"
    if not os.path.exists(workflow_path):
        logger.error(f"Workflow file {workflow_path} not found!")
        return

    logger.info(f"Running workflow from file: {workflow_path}")
    
    try:
        context = engine.run_from_file(workflow_path)
        
        logger.success("--- Workflow Results ---")
        logger.info(f"Channel: {context['channel'].title}")
        logger.info(f"Avg Views: {context['analysis'].avg_views}")
        logger.info(f"Engagement Rate: {context['analysis'].engagement_rate}%")
        logger.info(f"Report Path: {context['report_path']}")
        
        # Verify notification was "sent"
        if mock_notify.called:
            logger.info(f"Notification Sent: {mock_notify.call_args[0][0]}")
            
    except Exception as e:
        logger.error(f"Demo failed: {e}")

if __name__ == "__main__":
    # Ensure we don't actually try to hit the API by providing a dummy key
    os.environ["YOUTUBE_API_KEY"] = "MOCK_KEY"
    run_demo()
