import os
from jinja2 import Environment, FileSystemLoader
from app.domain.models import Channel, AnalyticsResult
from app.core.config import settings
from datetime import datetime

class ReportGenerator:
    def __init__(self, template_dir: str = "app/templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.template = self.env.get_template("report_template.html")

    def generate(self, channel: Channel, result: AnalyticsResult, chart_path: str = "") -> str:
        # Prepare data for template
        html_content = self.template.render(
            channel=channel,
            result=result,
            chart_path=chart_path,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        # Ensure output directory exists
        os.makedirs(settings.report_output_dir, exist_ok=True)
        
        # Create filename
        filename = f"report_{channel.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        file_path = os.path.join(settings.report_output_dir, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return file_path
