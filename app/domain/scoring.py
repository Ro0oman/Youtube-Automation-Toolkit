from typing import Dict, List
from app.domain.models import ChannelScore, Video, MetricStatus, MetricInterpretation, Channel
from app.core.config import settings

class ScoreCalculator:
    @staticmethod
    def calculate_channel_score(channel: Channel, avg_views: float, engagement_rate: float, upload_frequency: float) -> ChannelScore:
        # 1. Scoring Logic
        # Engagement Score (0-10)
        e_score = min(engagement_rate / settings.min_engagement_threshold * 5, 10)
        
        # Consistency Score (0-10)
        c_score = max(0, 10 - (upload_frequency / settings.max_upload_gap_days * 2))
        
        # Performance Score (0-10, based on views vs subscribers)
        subs = max(1, channel.stats.subscriber_count)
        p_score = min(avg_views / subs * 10, 10)
        
        weights = {"Engagement": 0.4, "Consistency": 0.3, "Performance": 0.3}
        overall = (e_score * weights["Engagement"]) + (c_score * weights["Consistency"]) + (p_score * weights["Performance"])
        
        # 2. Explanation Logic
        issues = []
        if e_score < 4: issues.append("Engagement")
        if c_score < 4: issues.append("Consistency")
        if p_score < 4: issues.append("Performance")
        
        biggest_issue = issues[0] if issues else "None"
        
        explanation = f"Your channel score is {overall:.1f}/10. "
        if biggest_issue != "None":
            explanation += f"The primary area for improvement is {biggest_issue}. "
        else:
            explanation += "Your channel is performing significantly well across all major metrics."

        return ChannelScore(
            overall_score=round(overall, 1),
            explanation=explanation,
            biggest_issue=biggest_issue,
            breakdown={
                "Engagement": round(e_score, 1),
                "Consistency": round(c_score, 1),
                "Performance": round(p_score, 1)
            }
        )

    @staticmethod
    def interpret_metrics(avg_views: float, engagement_rate: float, upload_frequency: float) -> Dict[str, MetricInterpretation]:
        interpretations = {}
        
        # Engagement
        e_status = MetricStatus.GOOD if engagement_rate >= settings.min_engagement_threshold else MetricStatus.WARNING
        interpretations["engagement"] = MetricInterpretation(
            value=f"{engagement_rate:.2f}%",
            status=e_status,
            label="Engagement Rate",
            benchmark=f"{settings.min_engagement_threshold*100:.1f}%+",
            note="Reflects how much your audience interacts with your videos."
        )
        
        # Upload Frequency
        c_status = MetricStatus.GOOD if upload_frequency <= settings.max_upload_gap_days else MetricStatus.CRITICAL
        interpretations["consistency"] = MetricInterpretation(
            value=f"{upload_frequency:.1f} days",
            status=c_status,
            label="Post Frequency",
            benchmark=f"Under {settings.max_upload_gap_days} days",
            note="Average time between video uploads."
        )
        
        return interpretations
