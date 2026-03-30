import os
from dotenv import load_dotenv
from app.services.youtube_service import YouTubeService
from loguru import logger

load_dotenv()

def verify():
    api_key = os.getenv("YOUTUBE_API_KEY")
    channel_id = "UCp6mySOpP-MrCRzMozlWUUQ"
    
    if not api_key or "your_youtube_api_key_here" in api_key:
        logger.error("API Key not set in .env")
        return

    logger.info(f"Verifying YouTube API for Channel ID: {channel_id}")
    try:
        yt = YouTubeService()
        channel = yt.get_channel_info(channel_id)
        logger.success(f"Connection Successful!")
        logger.info(f"Channel Title: {channel.title}")
        logger.info(f"Subscribers: {channel.stats.subscriber_count}")
        logger.info(f"Videos: {channel.stats.video_count}")
    except Exception as e:
        logger.error(f"Verification failed: {e}")

if __name__ == "__main__":
    verify()
