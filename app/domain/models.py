from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MetricStatus(str, Enum):
    GOOD = "GOOD"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class VideoStats(BaseModel):
    view_count: int = Field(alias="viewCount")
    like_count: Optional[int] = Field(None, alias="likeCount")
    comment_count: Optional[int] = Field(None, alias="commentCount")
    favorite_count: Optional[int] = Field(None, alias="favoriteCount")

class VideoMetadata(BaseModel):
    id: str
    title: str
    description: str
    published_at: datetime = Field(alias="publishedAt")
    thumbnails: Dict[str, Any]
    tags: Optional[List[str]] = None
    category_id: Optional[str] = Field(None, alias="categoryId")

class Video(BaseModel):
    metadata: VideoMetadata
    stats: VideoStats

class ChannelStats(BaseModel):
    view_count: int = Field(alias="viewCount")
    subscriber_count: int = Field(alias="subscriberCount")
    video_count: int = Field(alias="videoCount")

class Channel(BaseModel):
    id: str
    title: str
    description: str
    custom_url: Optional[str] = Field(None, alias="customUrl")
    published_at: datetime = Field(alias="publishedAt")
    stats: ChannelStats

class Recommendation(BaseModel):
    title: str
    reason: str
    action: str
    potential_impact: str # e.g. "High", "Medium"
    category: str = "Growth" # Growth, Strategy, Optimization

class MetricInterpretation(BaseModel):
    value: Any
    status: MetricStatus
    label: str
    benchmark: Optional[str] = None
    note: Optional[str] = None

class ChannelScore(BaseModel):
    overall_score: float # 0 to 10
    explanation: str
    biggest_issue: str
    breakdown: Dict[str, float] # e.g. {"Engagement": 4.5, "Consistency": 3.0}

class AnalyticsResult(BaseModel):
    channel_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    avg_views: float
    engagement_rate: float
    upload_frequency_days: float
    top_videos: List[Video]
    trends: Dict[str, Any]
    recommendations: List[Recommendation] = []
    score: Optional[ChannelScore] = None
    interpretations: Dict[str, MetricInterpretation] = {}
    evolution: Dict[str, Any] = {} # Growth compared to previous analysis
    report_path: Optional[str] = None
