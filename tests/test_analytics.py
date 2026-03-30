import pytest
from unittest.mock import MagicMock, patch
from app.services.analytics_service import AnalyticsService
from app.models.schemas import Video, VideoMetadata, VideoStats, Channel, ChannelStats
from datetime import datetime

@pytest.fixture
def mock_channel():
    return Channel(
        id="UC123",
        title="Test Channel",
        description="A test channel",
        publishedAt=datetime(2020, 1, 1),
        stats=ChannelStats(viewCount=1000, subscriberCount=100, videoCount=10)
    )

@pytest.fixture
def mock_videos():
    return [
        Video(
            metadata=VideoMetadata(id="v1", title="Video 1", description="desc", publishedAt=datetime(2024, 1, 1), thumbnails={}),
            stats=VideoStats(viewCount=100, likeCount=10, commentCount=2)
        ),
        Video(
            metadata=VideoMetadata(id="v2", title="Video 2", description="desc", publishedAt=datetime(2024, 1, 5), thumbnails={}),
            stats=VideoStats(viewCount=200, likeCount=20, commentCount=4)
        )
    ]

def test_analytics_calculations(mock_channel, mock_videos):
    service = AnalyticsService()
    result = service.analyze_channel(mock_channel, mock_videos)
    
    assert result.avg_views == 150.0
    assert result.engagement_rate == 12.0 # (30+6)/300 * 100
    assert result.upload_frequency_days == 4.0 # 4 days between uploads
    assert len(result.top_videos) == 2

def test_empty_videos(mock_channel):
    service = AnalyticsService()
    result = service.analyze_channel(mock_channel, [])
    assert result.avg_views == 0
    assert result.engagement_rate == 0
