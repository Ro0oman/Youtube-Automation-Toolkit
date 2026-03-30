from typing import List, Dict, Any, Optional
from app.domain.models import Video, Recommendation, AnalyticsResult
from loguru import logger

class InsightsEngine:
    @staticmethod
    def generate_recommendations(user_videos: List[Video], trending_videos: List[Video]) -> List[Recommendation]:
        logger.info("Generating deep niche recommendations")
        recs = []
        
        # 1. Topic Performance Analysis
        top_ids = [v.metadata.id for v in sorted(user_videos, key=lambda x: x.stats.view_count, reverse=True)[:5]]
        top_titles_str = " ".join([v.metadata.title.lower() for v in user_videos if v.metadata.id in top_ids])
        
        # 2. Trending Gap Analysis
        for trend in trending_videos[:3]:
            # Focus on significant words from trending titles
            keywords = [w for w in trend.metadata.title.split() if len(w) > 4]
            if keywords and not any(kw.lower() in top_titles_str for kw in keywords):
                recs.append(Recommendation(
                    title=f"New Topic Opportunity: {trend.metadata.title[:30]}",
                    reason=f"This topic is viral in your niche but missing from your top performers.",
                    action=f"Create a video specifically about '{keywords[0]}' targeting this trend.",
                    potential_impact="High",
                    category="Growth"
                ))

        # 3. Format/Style Recommendations
        all_caps_titles = [v for v in user_videos if any(w.isupper() and len(w) > 3 for w in v.metadata.title.split())]
        if len(all_caps_titles) > 0:
            avg_views_caps = sum(v.stats.view_count for v in all_caps_titles) / len(all_caps_titles)
            avg_total = sum(v.stats.view_count for v in user_videos) / len(user_videos)
            
            if avg_views_caps > avg_total * 1.2:
                recs.append(Recommendation(
                    title=f"Optimize Title Style",
                    reason=f"Videos with high-impact uppercase words perform {((avg_views_caps/avg_total)-1)*100:.0f}% better on your channel.",
                    action="Try using 1-2 ALL CAPS words in your future titles for better CTR.",
                    potential_impact="Medium",
                    category="Optimization"
                ))

        # 4. Consistency Advice
        recs.append(Recommendation(
            title="Strategic Upload Schedule",
            reason="Consistency is the strongest signal for the YouTube algorithm recommendation engine.",
            action="Try to stick to a fixed schedule (e.g., every Tuesday) to build audience habit.",
            potential_impact="High",
            category="Strategy"
        ))

        return recs[:5]

    @staticmethod
    def calculate_evolution(current: Any, previous: Optional[Any]) -> Dict[str, Any]:
        """Calculates growth compared to previous analysis from database"""
        if not previous:
            return {"note": "First run. No historical data available yet."}
            
        evolution = {}
        for metric in ["avg_views", "engagement_rate", "upload_frequency_days"]:
            curr_val = getattr(current, metric)
            prev_val = getattr(previous, metric)
            
            if prev_val > 0:
                growth_pct = ((curr_val - prev_val) / prev_val) * 100
                evolution[f"{metric}_growth"] = round(growth_pct, 1)
                
        return evolution
