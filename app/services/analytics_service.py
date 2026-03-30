from typing import List, Dict, Any, Optional
from app.models.schemas import Video, AnalyticsResult, Channel, Recommendation
from loguru import logger
from datetime import datetime, timedelta
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

class AnalyticsService:
    def __init__(self):
        pass

    def analyze_channel(self, channel: Channel, videos: List[Video]) -> AnalyticsResult:
        logger.info(f"Analyzing stats for channel: {channel.title}")
        
        if not videos:
            return AnalyticsResult(
                channel_id=channel.id,
                avg_views=0,
                engagement_rate=0,
                upload_frequency_days=0,
                top_videos=[],
                trends={},
                recommendations=[]
            )

        if HAS_PANDAS:
            # Convert to DataFrame for easier analysis
            df = pd.DataFrame([
                {
                    "id": v.metadata.id,
                    "title": v.metadata.title,
                    "views": v.stats.view_count,
                    "likes": v.stats.like_count or 0,
                    "comments": v.stats.comment_count or 0,
                    "published_at": v.metadata.published_at
                } for v in videos
            ])

            avg_views = df["views"].mean()
            
            # Engagement Rate = (Likes + Comments) / Views
            total_views = df["views"].sum()
            total_engagement = df["likes"].sum() + df["comments"].sum()
            engagement_rate = (total_engagement / total_views * 100) if total_views > 0 else 0

            # Upload Frequency (Average days between uploads)
            df = df.sort_values("published_at")
            df["diff"] = df["published_at"].diff().dt.total_seconds() / (24 * 3600)
            upload_frequency = abs(df["diff"].mean()) if len(df) > 1 else 0

            # Top Performing Videos (by views)
            top_videos_df = df.sort_values("views", ascending=False).head(5)
            top_video_ids = top_videos_df["id"].tolist()
            top_videos = [v for v in videos if v.metadata.id in top_video_ids]

            # Trends (last 30 days vs previous 30 days)
            trends = self._calculate_trends(df)
        else:
            logger.warning("Pandas not found. Using fallback analytic logic.")
            # Fallback logic using pure Python
            views = [v.stats.view_count for v in videos]
            avg_views = sum(views) / len(views)
            
            total_engagement = sum((v.stats.like_count or 0) + (v.stats.comment_count or 0) for v in videos)
            total_views = sum(views)
            engagement_rate = (total_engagement / total_views * 100) if total_views > 0 else 0
            
            sorted_videos = sorted(videos, key=lambda v: v.metadata.published_at)
            if len(sorted_videos) > 1:
                diffs = [(sorted_videos[i].metadata.published_at - sorted_videos[i-1].metadata.published_at).total_seconds() / (24*3600) 
                         for i in range(1, len(sorted_videos))]
                upload_frequency = abs(sum(diffs) / len(diffs))
            else:
                upload_frequency = 0
                
            top_videos = sorted(videos, key=lambda v: v.stats.view_count, reverse=True)[:5]
            trends = {"note": "Trends calculation requires pandas"}

        return AnalyticsResult(
            channel_id=channel.id,
            avg_views=round(avg_views, 2),
            engagement_rate=round(engagement_rate, 2),
            upload_frequency_days=round(upload_frequency, 2),
            top_videos=top_videos,
            trends=trends,
            recommendations=[]
        )

    def generate_niche_recommendations(self, user_videos: List[Video], trending_videos: List[Video]) -> List[Recommendation]:
        """Generate actionable recommendations based on trending content in the niche"""
        logger.info("Generating niche recommendations")
        recommendations = []
        
        # 1. Topic Gap Analysis
        user_titles = " ".join([v.metadata.title.lower() for v in user_videos])
        
        for trend in trending_videos[:3]:
            # Simple keyword check
            trend_keywords = [word for word in trend.metadata.title.split() if len(word) > 4]
            is_new_topic = not any(kw.lower() in user_titles for kw in trend_keywords)
            
            if is_new_topic:
                recommendations.append(Recommendation(
                    title=f"Explora el tema: '{trend.metadata.title[:40]}...'",
                    reason="Este tema está teniendo mucho éxito en videos similares de otros canales.",
                    action=f"Considera crear un video sobre '{trend_keywords[0]}' desde tu perspectiva única.",
                    potential_impact="High"
                ))

        # 2. Engagement Strategy
        recommendations.append(Recommendation(
            title="Optimiza tus Call-to-Action",
            reason="Los canales con alta tasa de crecimiento suelen pedir likes/subs en los primeros 2 minutos.",
            action="Prueba añadir un recordatorio visual de suscripción a mitad del video.",
            potential_impact="Medium"
        ))

        # 3. Community Interaction
        recommendations.append(Recommendation(
            title="Usa la pestaña de Comunidad",
            reason="Interactuar con encuestas aumenta un 20% la visibilidad de tus próximos videos.",
            action="Haz una encuesta preguntando qué tema quieren ver a continuación.",
            potential_impact="Medium"
        ))

        return recommendations[:5]

    def _calculate_trends(self, df: Any) -> Dict[str, Any]:
        if not HAS_PANDAS:
            return {}
        now = datetime.now(df["published_at"].iloc[0].tzinfo)
        last_30_days = df[df["published_at"] > (now - timedelta(days=30))]
        prev_30_days = df[(df["published_at"] <= (now - timedelta(days=30))) & 
                          (df["published_at"] > (now - timedelta(days=60)))]

        trends = {
            "views_growth_pct": 0,
            "recent_avg_views": 0,
            "videos_last_30_days": len(last_30_days)
        }

        if len(last_30_days) > 0 and len(prev_30_days) > 0:
            last_avg = last_30_days["views"].mean()
            prev_avg = prev_30_days["views"].mean()
            if prev_avg > 0:
                trends["views_growth_pct"] = round(((last_avg - prev_avg) / prev_avg) * 100, 2)
            trends["recent_avg_views"] = round(last_avg, 2)

        return trends
