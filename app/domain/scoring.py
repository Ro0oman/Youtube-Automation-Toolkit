from typing import Dict, List
from app.domain.models import ChannelScore, Video, MetricStatus, MetricInterpretation, Channel
from app.core.config import settings

class ScoreCalculator:
    @staticmethod
    def calculate_channel_score(channel: Channel, avg_views: float, engagement_rate: float, upload_frequency: float) -> ChannelScore:
        # 1. Scoring Logic
        e_score = min(engagement_rate / settings.min_engagement_threshold * 5, 10)
        c_score = max(0, 10 - (upload_frequency / settings.max_upload_gap_days * 2))
        subs = max(1, channel.stats.subscriber_count)
        p_score = min(avg_views / subs * 10, 10)
        
        weights = {"Engagement": 0.4, "Consistency": 0.3, "Performance": 0.3}
        overall = (e_score * weights["Engagement"]) + (c_score * weights["Consistency"]) + (p_score * weights["Performance"])
        
        # 2. Explanation Logic (v4.0 Coach Spanish)
        issues = []
        if e_score < 4: issues.append("Interacción (Engagement)")
        if c_score < 4: issues.append("Consistencia (Frecuencia)")
        if p_score < 4: issues.append("Crecimiento (Vistas)")
        
        biggest_issue = issues[0] if issues else "Nada"
        
        explanation = f"Tu puntuación de canal es {overall:.1f}/10. "
        if biggest_issue != "Nada":
            explanation += f"El área principal de mejora es {biggest_issue}. Un canal saludable necesita equilibrio entre calidad y ritmo."
        else:
            explanation += "¡Excelente trabajo! Tu canal está rindiendo por encima de la media en todos los pilares."

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
            label="Tasa de Interacción",
            benchmark=f"{settings.min_engagement_threshold:.1f}%+",
            note="Mide cuántos likes y comentarios recibes por cada vista.",
            what_it_means="La gente ve tus vídeos pero no interactúa → YouTube los recomienda menos.",
            target_value=f"{max(engagement_rate + 1.5, settings.min_engagement_threshold + 0.5):.1f}%",
            action_priority="Alta" if e_status != MetricStatus.GOOD else "Media"
        )
        
        # Upload Frequency
        c_status = MetricStatus.GOOD if upload_frequency <= settings.max_upload_gap_days else MetricStatus.CRITICAL
        interpretations["consistency"] = MetricInterpretation(
            value=f"{upload_frequency:.1f} días",
            status=c_status,
            label="Frecuencia de Publicación",
            benchmark=f"Cada {settings.max_upload_gap_days} días",
            note="Promedio de tiempo entre cada subida.",
            what_it_means="YouTube no detecta un patrón claro → No logra construir un hábito en tu audiencia.",
            target_value=f"7.0 días",
            action_priority="Crítica" if c_status == MetricStatus.CRITICAL else "Baja"
        )
        
        # Average Views
        interpretations["views"] = MetricInterpretation(
            value=f"{int(avg_views)}",
            status=MetricStatus.GOOD if avg_views > 1000 else MetricStatus.WARNING,
            label="Vistas Promedio",
            benchmark="1,000+ vistas",
            note="Vistas promedio de tus últimos vídeos.",
            what_it_means="Pocas vistas indican que tus títulos o miniaturas no están captando la atención.",
            target_value=f"{int(avg_views * 1.5)}",
            action_priority="Media"
        )
        
        return interpretations
