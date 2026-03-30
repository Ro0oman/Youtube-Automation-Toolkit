from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.infra.database import Base

class ChannelDB(Base):
    __tablename__ = "channels"
    
    id = Column(String, primary_key=True)
    title = Column(String)
    description = Column(String)
    custom_url = Column(String)
    published_at = Column(DateTime)
    subscriber_count = Column(Integer)
    video_count = Column(Integer)
    view_count = Column(Integer)
    
    analyses = relationship("AnalysisDB", back_populates="channel")

class AnalysisDB(Base):
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(String, ForeignKey("channels.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    avg_views = Column(Float)
    engagement_rate = Column(Float)
    upload_frequency_days = Column(Float)
    
    # Store complex JSON data
    score = Column(JSON) # {overall, explanation, breakdown}
    trends = Column(JSON)
    recommendations = Column(JSON)
    interpretations = Column(JSON)
    evolution = Column(JSON)
    
    channel = relationship("ChannelDB", back_populates="analyses")

class VideoDB(Base):
    __tablename__ = "videos"
    
    id = Column(String, primary_key=True)
    channel_id = Column(String, ForeignKey("channels.id"))
    title = Column(String)
    published_at = Column(DateTime)
    view_count = Column(Integer)
    like_count = Column(Integer)
    comment_count = Column(Integer)
