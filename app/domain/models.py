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
    category: str = "Growth" 
    what_it_means: Optional[str] = None # Added for v4.0 Coach
    concrete_steps: List[str] = [] # Added for v4.0 Coach

class MetricInterpretation(BaseModel):
    value: Any
    status: MetricStatus
    label: str
    benchmark: Optional[str] = None
    note: Optional[str] = None
    what_it_means: Optional[str] = None # v4.0
    target_value: Optional[str] = None # v4.0
    action_priority: str = "Medium" # v4.0

class ChannelScore(BaseModel):
    overall_score: float # 0 to 10
    explanation: str
    biggest_issue: str
    breakdown: Dict[str, float] # e.g. {"Engagement": 4.5, "Consistency": 3.0}

class ActionDay(BaseModel):
    day: str # e.g. "Lunes"
    task: str
    description: str
    icon: str = "📝"

class NextVideoIdea(BaseModel):
    topic: str
    title: str
    why: str
    goal: str

class AnalyticsResult(BaseModel):
    channel_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    avg_views: float
    engagement_rate: float
    upload_frequency_days: float
    top_videos: List[Video]
    trends: Dict[str, Any]
    recommendations: List[Recommendation] = []
    score: Optional[Any] = None # Using Any for complex score object
    interpretations: Dict[str, MetricInterpretation] = {}
    evolution: Dict[str, Any] = {}
    report_path: Optional[str] = None
    
    # Coach v4.0 Fields
    action_plan: List[ActionDay] = []
    next_video: Optional[NextVideoIdea] = None
    priorities: List[str] = []
