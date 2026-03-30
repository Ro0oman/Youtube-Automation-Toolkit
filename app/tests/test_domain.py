import pytest
from app.domain.scoring import ScoreCalculator
from app.domain.models import Channel, ChannelStats
from datetime import datetime

def test_calculate_channel_score_perfect():
    channel = Channel(
        id="test_id",
        title="Test Channel",
        description="Desc",
        publishedAt=datetime.now(),
        stats=ChannelStats(viewCount=1000000, subscriberCount=1000, videoCount=100)
    )
    
    # 5% engagement, 2 day frequency
    score = ScoreCalculator.calculate_channel_score(
        channel=channel,
        avg_views=5000, 
        engagement_rate=5.0, 
        upload_frequency=2.0
    )
    
    assert score.overall_score >= 8.0
    assert "None" in score.biggest_issue

def test_calculate_channel_score_low_engagement():
    channel = Channel(
        id="test_id",
        title="Test Channel",
        description="Desc",
        publishedAt=datetime.now(),
        stats=ChannelStats(viewCount=1000, subscriberCount=1000, videoCount=10)
    )
    
    # 0.1% engagement
    score = ScoreCalculator.calculate_channel_score(
        channel=channel,
        avg_views=100, 
        engagement_rate=0.1, 
        upload_frequency=5.0
    )
    
    assert score.overall_score < 5.0
    assert "Engagement" in score.biggest_issue

def test_interpret_metrics_consistency_critical():
    # 30 days gap is CRITICAL
    interpretations = ScoreCalculator.interpret_metrics(
        avg_views=100,
        engagement_rate=2.0,
        upload_frequency=30.0
    )
    
    assert interpretations["consistency"].status.value == "CRITICAL"
