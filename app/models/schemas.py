from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

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

class AnalyticsResult(BaseModel):
    channel_id: str
    avg_views: float
    engagement_rate: float
    upload_frequency_days: float
    top_videos: List[Video]
    trends: Dict[str, Any]
    recommendations: List[Recommendation] = []

class WorkflowStep(BaseModel):
    name: str
    action: str
    params: Dict[str, Any] = {}

class WorkflowConfig(BaseModel):
    name: str
    description: Optional[str] = None
    steps: List[WorkflowStep]
    schedule: Optional[str] = None # Cron expression or interval
