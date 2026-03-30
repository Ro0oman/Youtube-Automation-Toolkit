import sys
import os
from datetime import datetime, timedelta
from app.domain.models import Channel, ChannelStats, Video, VideoMetadata, VideoStats
from app.services.analytics_service import AnalyticsService
from app.infra.report_generator import ReportGenerator
from app.infra.database import engine, Base, SessionLocal
from app.infra.repository import AnalyticsRepository
from loguru import logger

def run_demo():
    logger.info("🚀 YouTube Intelligence COACH v4.0 - MODO DEMO (Español)")
    logger.info("Generando caso real de un canal con potencial pero bajo engagement...")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    repo = AnalyticsRepository(db)

    # 1. Mock Channel (Novato con potencial)
    channel = Channel(
        id="UC_COACH_DEMO_001",
        title="Aventuras Minecraft con Pepe",
        description="Explorando los mejores mods y construcciones épicas.",
        publishedAt=datetime.now() - timedelta(days=180),
        stats=ChannelStats(viewCount=5000, subscriberCount=150, videoCount=12)
    )

    # 2. Mock Videos (Vistas aceptables pero NO hay interacción)
    videos = []
    base_date = datetime.now()
    for i in range(8):
        v_id = f"vid_{i}"
        # Títulos normales (no optimizados)
        videos.append(Video(
            metadata=VideoMetadata(
                id=v_id,
                title=f"Probando mods de Minecraft episodio {i+1}",
                description="Hoy probamos un mod nuevo...",
                publishedAt=base_date - timedelta(days=i*15), # Frecuencia baja (cada 15 días)
                thumbnails={"default": {"url": ""}},
                tags=["minecraft", "mods"]
            ),
            stats=VideoStats(
                viewCount=800 + (i * 20),
                likeCount=5, # MUY BAJO
                commentCount=2 # MUY BAJO
            )
        ))

    # 3. Análisis COACH
    analytics = AnalyticsService(repository=repo)
    result = analytics.analyze_channel(channel, videos)

    # 4. Generar Reporte
    report_gen = ReportGenerator()
    report_path = report_gen.generate(channel, result)

    logger.success(f"✅ ¡Análisis del Coach Completado!")
    logger.info(f"📊 Puntuación: {result.score.overall_score}/10")
    logger.info(f"📄 Reporte COACH Generado: {report_path}")
    
    db.close()
    
    print("\n" + "="*50)
    print("DEMO COACH v4.0 EXITOSA")
    print(f"Abre este archivo en tu navegador: {os.path.abspath(report_path)}")
    print("="*50)

if __name__ == "__main__":
    run_demo()
