import os
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
from jinja2 import Environment, FileSystemLoader
from loguru import logger
from datetime import datetime
from app.models.schemas import AnalyticsResult, Channel

class ReportService:
    def __init__(self, output_dir: str = "reports", template_dir: str = "app/templates"):
        self.output_dir = output_dir
        self.template_dir = template_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def generate_report(self, channel: Channel, result: AnalyticsResult) -> str:
        logger.info(f"Generating report for: {channel.title}")
        
        # 1. Generate Chart
        chart_path = self._generate_charts(result)
        
        # 2. Render HTML
        template = self.env.get_template("report_template.html")
        html_content = template.render(
            channel=channel,
            result=result,
            chart_path=os.path.basename(chart_path),
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        report_filename = f"report_{channel.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        report_path = os.path.join(self.output_dir, report_filename)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        logger.info(f"Report generated: {report_path}")
        return report_path

    def _generate_charts(self, result: AnalyticsResult) -> str:
        if not HAS_MATPLOTLIB:
            logger.warning("Matplotlib not found. Skipping chart generation.")
            return ""

        if not result.top_videos:
            return ""

        # Chart 1: Top 5 Videos by Views
        titles = [v.metadata.title[:20] + "..." for v in result.top_videos]
        views = [v.stats.view_count for v in result.top_videos]

        plt.figure(figsize=(10, 6))
        plt.barh(titles, views, color='skyblue')
        plt.xlabel('Views')
        plt.title('Top 5 Videos by View Count')
        plt.gca().invert_yaxis()
        plt.tight_layout()

        chart_filename = f"chart_{result.channel_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        chart_path = os.path.join(self.output_dir, chart_filename)
        plt.savefig(chart_path)
        plt.close()
        
        return chart_path
