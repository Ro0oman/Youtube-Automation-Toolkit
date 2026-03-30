from typing import List, Dict, Any, Optional
from app.domain.models import Video, AnalyticsResult, Channel, Recommendation, ActionDay, NextVideoIdea
from app.domain.scoring import ScoreCalculator
from app.domain.insights import InsightsEngine
from loguru import logger
from datetime import datetime

class AnalyticsService:
    def __init__(self, repository: Optional[Any] = None):
        self.repo = repository
        self.scorer = ScoreCalculator()
        self.insights = InsightsEngine()

    def analyze_channel(self, channel: Channel, videos: List[Video]) -> AnalyticsResult:
        logger.info(f"Análisis ELITE COACH v5.0 para: {channel.title}")
        
        if not videos:
            return self._empty_result(channel.id)

        # 1. Base Metrics
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

        # 2. Score y Interpretraciones Spanish v5.0
        score = self.scorer.calculate_channel_score(channel, avg_views, engagement_rate, upload_frequency)
        interpretations = self.scorer.interpret_metrics(avg_views, engagement_rate, upload_frequency)

        # 3. Evolution Tracking
        previous_analysis = self.repo.get_last_analysis(channel.id) if self.repo else None
        evolution = self.insights.calculate_evolution(
            type('obj', (object,), {"avg_views": avg_views, "engagement_rate": engagement_rate, "upload_frequency_days": upload_frequency}),
            previous_analysis
        )

        # 4. COACH Features v5.0
        dias_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        hoy_idx = datetime.now().weekday()
        generic_plan = self.insights.generate_7_day_plan()
        
        real_day_plan = []
        for i in range(7):
            idx = (hoy_idx + i) % 7
            real_day_plan.append(ActionDay(
                day=dias_es[idx],
                task=generic_plan[i].task,
                description=generic_plan[i].description,
                icon=generic_plan[i].icon
            ))

        next_video = self.insights.suggest_next_video(videos)
        recommendations = self.insights.generate_recommendations(videos, [])

        # Priority Ranking v5.0
        priorities = []
        if upload_frequency > 10: priorities.append("Subir 1 vídeo por semana (MÍNIMO)")
        if engagement_rate < 2.0: priorities.append("Mejorar títulos y Call-to-Action")
        if not priorities: priorities.append("Mantener el ritmo de crecimiento actual")

        result = AnalyticsResult(
            channel_id=channel.id,
            avg_views=round(avg_views, 2),
            engagement_rate=round(engagement_rate, 2),
            upload_frequency_days=round(upload_frequency, 2),
            top_videos=sorted(videos, key=lambda v: v.stats.view_count, reverse=True)[:5],
            trends={},
            recommendations=recommendations,
            score=score,
            interpretations=interpretations,
            evolution=evolution,
            report_path=None,
            action_plan=real_day_plan,
            next_video=next_video,
            priorities=priorities
        )

        if self.repo:
            self.repo.save_analysis(result, channel, videos)

        return result

    def _empty_result(self, channel_id: str) -> AnalyticsResult:
        return AnalyticsResult(
            channel_id=channel_id, avg_views=0, engagement_rate=0, upload_frequency_days=0,
            top_videos=[], trends={}, recommendations=[]
        )
