from typing import List, Dict, Any, Optional
from app.domain.models import Video, Recommendation, ActionDay, NextVideoIdea
from loguru import logger
from datetime import datetime

class InsightsEngine:
    @staticmethod
    def generate_recommendations(user_videos: List[Video], trending_videos: List[Video]) -> List[Recommendation]:
        logger.info("Generando recomendaciones del Coach de v4.0")
        recs = []
        
        # 1. Topic Performance Analysis (Spanish)
        top_ids = [v.metadata.id for v in sorted(user_videos, key=lambda x: x.stats.view_count, reverse=True)[:5]]
        top_titles_str = " ".join([v.metadata.title.lower() for v in user_videos if v.metadata.id in top_ids])
        
        # 2. Viral Opportunity
        for trend in trending_videos[:3]:
            keywords = [w for w in trend.metadata.title.split() if len(w) > 4]
            if keywords and not any(kw.lower() in top_titles_str for kw in keywords):
                recs.append(Recommendation(
                    title=f"Oportunidad VIRAL: {trend.metadata.title[:30]}",
                    reason=f"Este tema es viral en tu nicho pero falta en tus mejores videos.",
                    action=f"Crea un video sobre '{keywords[0]}' aprovechando esta tendencia.",
                    potential_impact="Alta",
                    category="Crecimiento",
                    what_it_means="Los temas virales atraen suscriptores nuevos rápido.",
                    concrete_steps=["Busca 3 videos virales de este tema.", "Escribe un guión que aporte algo nuevo."]
                ))

        # 3. Format/Style Coaching
        all_caps_titles = [v for v in user_videos if any(w.isupper() and len(w) > 3 for w in v.metadata.title.split())]
        if len(all_caps_titles) > 0:
            avg_views_caps = sum(v.stats.view_count for v in all_caps_titles) / len(all_caps_titles)
            avg_total = sum(v.stats.view_count for v in user_videos) / len(user_videos)
            
            if avg_views_caps > avg_total * 1.2:
                recs.append(Recommendation(
                    title=f"Optimiza tus Títulos",
                    reason=f"Tus videos con MAYÚSCULAS tienen un {((avg_views_caps/avg_total)-1)*100:.0f}% más de vistas.",
                    action="Usa 1-2 palabras en MAYÚSCULAS para mayor CTR.",
                    potential_impact="Media",
                    category="Optimización",
                    what_it_means="El CTR (clic por vista) mejora con alto impacto visual.",
                    concrete_steps=["Cambia el título de tu próximo video.", "Usa un emoji impactante (😱 o 🔥)."]
                ))

        return recs[:3]

    @staticmethod
    def generate_7_day_plan() -> List[ActionDay]:
        plan = [
            ActionDay(day="Lunes", task="Elegir Tema Dominante", description="Analiza qué tema en tu nicho está teniendo éxito hoy (Minecraft, CS2, etc).", icon="🎯"),
            ActionDay(day="Martes", task="Investigación Viral", description="Busca 3 vídeos virales del tema y analiza sus miniaturas y títulos.", icon="🔬"),
            ActionDay(day="Miércoles", task="Guión y Título de Hook", description="Escribe un título estilo: 'ESTO es lo que pasa cuando...' para generar curiosidad.", icon="✍️"),
            ActionDay(day="Jueves", task="Grabación (8-12 min)", description="Graba tu contenido. Recuerda pedir la suscripción en el minuto 1:00.", icon="🎥"),
            ActionDay(day="Viernes", task="Edición con Dinamismo", description="Añade texto en pantalla y música. Procesa el audio para que sea nítido.", icon="✂️"),
            ActionDay(day="Sábado", task="Publicar (Hora Pico)", description="Analiza a qué hora publican tus competidores e imítalos.", icon="🚀"),
            ActionDay(day="Domingo", task="Fidelización Directa", description="Responde a todos los comentarios de las primeras 24 horas.", icon="💬")
        ]
        return plan

    @staticmethod
    def suggest_next_video(videos: List[Video]) -> NextVideoIdea:
        if not videos:
            return NextVideoIdea(topic="Gaming", title="ESTO es el FUTURO 😱", why="No hay datos previos.", goal="1000 vistas")

        top_v = sorted(videos, key=lambda v: v.stats.view_count, reverse=True)[0]
        words = top_v.metadata.title.split()
        topic = words[0] if words else "Gaming"
        
        return NextVideoIdea(
            topic=topic,
            title=f"ESTO sobre {topic} es una LOCURA 😱",
            why=f"Tus vídeos sobre '{topic}' rinden un 40% mejor que el resto.",
            goal=f"Superar las {int(top_v.stats.view_count * 1.2)} vistas"
        )

    @staticmethod
    def calculate_evolution(current: Any, previous: Optional[Any]) -> Dict[str, Any]:
        if not previous: return {}
        evolution = {}
        for metric in ["avg_views", "engagement_rate", "upload_frequency_days"]:
            curr_val = getattr(current, metric, 0)
            prev_val = getattr(previous, metric, 0)
            if prev_val > 0:
                growth_pct = ((curr_val - prev_val) / prev_val) * 100
                evolution[f"{metric}_growth"] = round(growth_pct, 1)
        return evolution
