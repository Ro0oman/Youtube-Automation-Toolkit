from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.infra.models import ChannelDB, AnalysisDB, VideoDB
from app.domain.models import AnalyticsResult, Channel, Video
from typing import List, Optional

class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_analysis(self, result: AnalyticsResult, channel: Channel, videos: List[Video]):
        # 1. Update or create channel
        db_channel = self.db.query(ChannelDB).filter(ChannelDB.id == channel.id).first()
        if not db_channel:
            db_channel = ChannelDB(id=channel.id)
            self.db.add(db_channel)
        
        db_channel.title = channel.title
        db_channel.description = channel.description
        db_channel.custom_url = channel.custom_url
        db_channel.published_at = channel.published_at
        db_channel.subscriber_count = channel.stats.subscriber_count
        db_channel.video_count = channel.stats.video_count
        db_channel.view_count = channel.stats.view_count

        # 2. Add analysis record
        db_analysis = AnalysisDB(
            channel_id=channel.id,
            timestamp=result.timestamp,
            avg_views=result.avg_views,
            engagement_rate=result.engagement_rate,
            upload_frequency_days=result.upload_frequency_days,
            score=result.score.dict() if result.score else None,
            trends=result.trends,
            recommendations=[r.dict() for r in result.recommendations],
            interpretations={k: v.dict() for k, v in result.interpretations.items()},
            evolution=result.evolution
        )
        self.db.add(db_analysis)

        # 3. Update top videos
        for video in videos:
            db_video = self.db.query(VideoDB).filter(VideoDB.id == video.metadata.id).first()
            if not db_video:
                db_video = VideoDB(id=video.metadata.id, channel_id=channel.id)
                self.db.add(db_video)
            
            db_video.title = video.metadata.title
            db_video.published_at = video.metadata.published_at
            db_video.view_count = video.stats.view_count
            db_video.like_count = video.stats.like_count
            db_video.comment_count = video.stats.comment_count

        self.db.commit()

    def get_last_analysis(self, channel_id: str) -> Optional[AnalysisDB]:
        return self.db.query(AnalysisDB)\
            .filter(AnalysisDB.channel_id == channel_id)\
            .order_by(desc(AnalysisDB.timestamp))\
            .first()

    def get_history(self, channel_id: str, limit: int = 10) -> List[AnalysisDB]:
        return self.db.query(AnalysisDB)\
            .filter(AnalysisDB.channel_id == channel_id)\
            .order_by(desc(AnalysisDB.timestamp))\
            .limit(limit)\
            .all()
