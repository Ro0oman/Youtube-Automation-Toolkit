import os
from dotenv import load_dotenv
from app.workflows.engine import WorkflowEngine
from loguru import logger

# Load environment variables from .env
load_dotenv()

def run_real_workflow():
    logger.info("Starting YouTube Automation Toolkit - Real Data Execution")
    
    # Ensure reports directory exists
    os.makedirs("reports", exist_ok=True)
    
    # Initialize Engine
    engine = WorkflowEngine()
    
    # Load the example workflow
    workflow_path = "app/workflows/weekly_report.yaml"
    if not os.path.exists(workflow_path):
        logger.error(f"Workflow file {workflow_path} not found!")
        return

    logger.info(f"Running workflow from file: {workflow_path}")
    
    try:
        # This will now use the real YouTubeService because we are not patching it
        context = engine.run_from_file(workflow_path)
        
        logger.success("--- Workflow Results (REAL DATA) ---")
        logger.info(f"Channel: {context['channel'].title}")
        logger.info(f"Avg Views: {context.get('analysis').avg_views if context.get('analysis') else 'N/A'}")
        logger.info(f"Engagement Rate: {context.get('analysis').engagement_rate if context.get('analysis') else 'N/A'}%")
        logger.info(f"Report Path: {context.get('report_path')}")
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    run_real_workflow()
