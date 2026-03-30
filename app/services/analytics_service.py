from typing import List, Dict, Any, Optional
from app.domain.models import Video, AnalyticsResult, Channel, Recommendation
from app.domain.scoring import ScoreCalculator
from app.domain.insights import InsightsEngine
from loguru import logger
from datetime import datetime, timedelta

class AnalyticsService:
    def __init__(self, repository: Optional[Any] = None):
        self.repo = repository
        self.scorer = ScoreCalculator()
        self.insights = InsightsEngine()

    def analyze_channel(self, channel: Channel, videos: List[Video]) -> AnalyticsResult:
        logger.info(f"Performing deep analysis for channel: {channel.title}")
        
        if not videos:
            return self._empty_result(channel.id)

        # 1. Base Metrics (Pure Python Implementation)
        views = [v.stats.view_count for v in videos]
        avg_views = sum(views) / len(views)
        
        total_engagement = sum((v.stats.like_count or 0) + (v.stats.comment_count or 0) for v in videos)
        total_views = sum(views)
        engagement_rate = (total_engagement / total_views * 100) if total_views > 0 else 0
        
        sorted_videos = sorted(videos, key=lambda v: v.metadata.published_at)
        upload_frequency = 0
        if len(sorted_videos) > 1:
            diffs = [(sorted_videos[i].metadata.published_at - sorted_videos[i-1].metadata.published_at).total_seconds() / (24*3600) 
                     for i in range(1, len(sorted_videos))]
            upload_frequency = abs(sum(diffs) / len(diffs))

        # 2. Domain Scoring & Interpretation
        score = self.scorer.calculate_channel_score(channel, avg_views, engagement_rate, upload_frequency)
        interpretations = self.scorer.interpret_metrics(avg_views, engagement_rate, upload_frequency)

        # 3. Insights & Evolution
        # Fetch historical data from repository if available
        previous_analysis = None
        if self.repo:
            previous_analysis = self.repo.get_last_analysis(channel.id)
            
        evolution = self.insights.calculate_evolution(
            # Simplified object for the engine
            type('obj', (object,), {
                "avg_views": avg_views, 
                "engagement_rate": engagement_rate, 
                "upload_frequency_days": upload_frequency
            }),
            previous_analysis
        )

        # 4. Trends (Last 30 days)
        now = datetime.now(sorted_videos[0].metadata.published_at.tzinfo)
        last_30_days = [v for v in videos if v.metadata.published_at > (now - timedelta(days=30))]
        trends = {
            "recent_videos_count": len(last_30_days),
            "recent_avg_views": sum(v.stats.view_count for v in last_30_days) / len(last_30_days) if last_30_days else 0,
            "is_growing": len(last_30_days) > 0
        }

        # 5. Recommendations
        # (In a real scenario, trending_videos would come from YouTubeService search)
        # For now we use the engine's internal logic
        recommendations = self.insights.generate_recommendations(videos, [])

        result = AnalyticsResult(
            channel_id=channel.id,
            avg_views=round(avg_views, 2),
            engagement_rate=round(engagement_rate, 2),
            upload_frequency_days=round(upload_frequency, 2),
            top_videos=sorted(videos, key=lambda v: v.stats.view_count, reverse=True)[:5],
            trends=trends,
            recommendations=recommendations,
            score=score,
            interpretations=interpretations,
            evolution=evolution
        )

        # 6. Persist if repository is active
        if self.repo:
            self.repo.save_analysis(result, channel, videos)

        return result

    def _empty_result(self, channel_id: str) -> AnalyticsResult:
        return AnalyticsResult(
            channel_id=channel_id,
            avg_views=0,
            engagement_rate=0,
            upload_frequency_days=0,
            top_videos=[],
            trends={},
            recommendations=[]
        )
