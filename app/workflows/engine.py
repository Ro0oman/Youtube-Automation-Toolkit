import yaml
import json
from loguru import logger
from typing import Dict, Any, List
from app.models.schemas import WorkflowConfig, WorkflowStep, Channel, Video, AnalyticsResult
from app.services.youtube_service import YouTubeService
from app.services.analytics_service import AnalyticsService
from app.services.notification_service import NotificationService
from app.services.report_service import ReportService

class WorkflowEngine:
    def __init__(self):
        self.youtube_service = YouTubeService()
        self.analytics_service = AnalyticsService()
        self.notification_service = NotificationService()
        self.report_service = ReportService()
        self.context: Dict[str, Any] = {}

    def run_from_file(self, file_path: str):
        logger.info(f"Loading workflow from: {file_path}")
        with open(file_path, 'r') as f:
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                config_data = yaml.safe_load(f)
            else:
                config_data = json.load(f)
        
        config = WorkflowConfig(**config_data)
        return self.run(config)

    def run(self, config: WorkflowConfig):
        logger.info(f"Starting workflow: {config.name}")
        self.context = {}
        
        for step in config.steps:
            try:
                self._execute_step(step)
            except Exception as e:
                logger.error(f"Error in step {step.name}: {e}")
                raise e
        
        logger.info(f"Workflow {config.name} completed successfully")
        return self.context

    def _execute_step(self, step: WorkflowStep):
        logger.info(f"Executing step: {step.name} ({step.action})")
        
        if step.action == "fetch_channel":
            channel_id = step.params.get("channel_id")
            self.context["channel"] = self.youtube_service.get_channel_info(channel_id)
            
        elif step.action == "fetch_videos":
            channel_id = step.params.get("channel_id")
            max_results = step.params.get("max_results", 50)
            self.context["videos"] = self.youtube_service.get_videos(channel_id, max_results)
            
        elif step.action == "analyze_stats":
            channel = self.context.get("channel")
            videos = self.context.get("videos")
            if not channel or not videos:
                raise ValueError("Context missing channel or videos for analysis")
            self.context["analysis"] = self.analytics_service.analyze_channel(channel, videos)
            
        elif step.action == "generate_report":
            channel = self.context.get("channel")
            analysis = self.context.get("analysis")
            if not channel or not analysis:
                raise ValueError("Context missing channel or analysis for report")
            self.context["report_path"] = self.report_service.generate_report(channel, analysis)
            
        elif step.action == "generate_recommendations":
            videos = self.context.get("videos")
            if not videos:
                raise ValueError("Context missing videos for generating recommendations")
            
            # Step 1: Extract keywords from user's top videos
            analysis = self.context.get("analysis")
            top_videos = analysis.top_videos if analysis else videos[:5]
            query = " ".join([v.metadata.title.split()[0] for v in top_videos[:2]])
            
            # Step 2: Search for trending videos in this niche
            # (Last 30 days)
            from datetime import datetime, timedelta
            last_30_days = (datetime.now() - timedelta(days=30)).isoformat() + "Z"
            
            trending = self.youtube_service.search_videos(query=query, max_results=5, published_after=last_30_days)
            
            # Step 3: Generate the actual recommendations
            recs = self.analytics_service.generate_niche_recommendations(videos, trending)
            
            if analysis:
                analysis.recommendations = recs
            self.context["recommendations"] = recs

        elif step.action == "send_notification":
            message_template = step.params.get("message", "Workflow {name} completed")
            # Simple template replacement
            message = message_template.format(
                channel_name=self.context.get("channel").title if self.context.get("channel") else "Unknown",
                avg_views=self.context.get("analysis").avg_views if self.context.get("analysis") else "N/A"
            )
            self.notification_service.notify(message)
            
        else:
            raise ValueError(f"Unknown action: {step.action}")
