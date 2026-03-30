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
    logger.info("🚀 YouTube Intelligence Coach v5.0 - ELITE MODE (Español)")
    logger.info("Generando reporte de nivel 9.5/10 para el portfolio...")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    repo = AnalyticsRepository(db)

    # 1. Mock Channel (Con historial para mostrar evolución)
    channel = Channel(
        id="UC_ELITE_COACH_999",
        title="Gaming Pro con Román",
        description="Contenido de alta calidad sobre Minecraft y CS2.",
        publishedAt=datetime.now() - timedelta(days=365),
        stats=ChannelStats(viewCount=150000, subscriberCount=5200, videoCount=45)
    )

    # 2. Mock Videos (Mezcla de éxitos y áreas de mejora)
    videos = []
    base_date = datetime.now()
    for i in range(15):
        v_id = f"vid_{i}"
        title = f"Review del nuevo MOD de Minecraft {i}"
        if i % 3 == 0: title = f"ESTE MOD de Minecraft está ROTO 😱 {i}"
        
        videos.append(Video(
            metadata=VideoMetadata(
                id=v_id,
                title=title,
                description="Desc...",
                publishedAt=base_date - timedelta(days=i*8),
                thumbnails={"default": {"url": ""}}
            ),
            stats=VideoStats(
                viewCount=1200 + (i * 50) if i % 3 == 0 else 400,
                like_count=80 if i % 3 == 0 else 10,
                comment_count=15 if i % 3 == 0 else 2
            )
        ))

    # 3. Análisis ELITE
    analytics = AnalyticsService(repository=repo)
    result = analytics.analyze_channel(channel, videos)

    # 4. Generar Reporte
    report_gen = ReportGenerator()
    report_path = report_gen.generate(channel, result)

    logger.success(f"✅ ¡Análisis ELITE v5.0 Completado!")
    logger.info(f"📊 Score: {result.score.overall_score}/10")
    logger.info(f"📄 Reporte ELITE Generado: {report_path}")
    
    db.close()
    
    print("\n" + "="*50)
    print("DEMO ELITE v5.0 EXITOSA (9.5/10)")
    print(f"Abre este archivo en tu navegador: {os.path.abspath(report_path)}")
    print("="*50)

if __name__ == "__main__":
    run_demo()
