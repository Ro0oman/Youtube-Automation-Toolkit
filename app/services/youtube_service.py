import os
from googleapiclient.discovery import build
from loguru import logger
from typing import List, Optional, Dict, Any
from app.domain.models import Channel, Video, VideoMetadata, VideoStats, ChannelStats
from dotenv import load_dotenv

load_dotenv()

class YouTubeService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            logger.error("YOUTUBE_API_KEY not found in environment")
            # We don't raise here to allow Mocking/Demo Mode
        else:
            self.youtube = build("youtube", "v3", developerKey=self.api_key)

    def get_channel_info(self, channel_id: str) -> Channel:
        logger.info(f"Fetching info for channel: {channel_id}")
        request = self.youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        )
        response = request.execute()
        
        if not response.get("items"):
            raise ValueError(f"Channel {channel_id} not found")
            
        item = response["items"][0]
        snippet = item["snippet"]
        stats = item["statistics"]
        
        return Channel(
            id=item["id"],
            title=snippet["title"],
            description=snippet["description"],
            customUrl=snippet.get("customUrl"),
            publishedAt=snippet["publishedAt"],
            stats=ChannelStats(
                viewCount=int(stats["viewCount"]),
                subscriberCount=int(stats.get("subscriberCount", 0)),
                videoCount=int(stats["videoCount"])
            )
        )

    def get_videos(self, channel_id: str, max_results: int = 50) -> List[Video]:
        logger.info(f"Fetching up to {max_results} videos for channel: {channel_id}")
        
        # 1. Get uploads playlist ID
        channel_request = self.youtube.channels().list(
            part="contentDetails",
            id=channel_id
        )
        channel_response = channel_request.execute()
        uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        
        # 2. Get video IDs from playlist
        videos_request = self.youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=max_results
        )
        videos_response = videos_request.execute()
        
        video_ids = [item["snippet"]["resourceId"]["videoId"] for item in videos_response.get("items", [])]
        if not video_ids:
            return []
            
        # 3. Get detailed stats for each video
        stats_request = self.youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids)
        )
        stats_response = stats_request.execute()
        
        videos = []
        for item in stats_response.get("items", []):
            snippet = item["snippet"]
            stats = item["statistics"]
            
            video = Video(
                metadata=VideoMetadata(
                    id=item["id"],
                    title=snippet["title"],
                    description=snippet["description"],
                    publishedAt=snippet["publishedAt"],
                    thumbnails=snippet["thumbnails"],
                    tags=snippet.get("tags"),
                    categoryId=snippet.get("categoryId")
                ),
                stats=VideoStats(
                    viewCount=int(stats["viewCount"]),
                    likeCount=int(stats.get("likeCount", 0)),
                    commentCount=int(stats.get("commentCount", 0)),
                    favoriteCount=int(stats.get("favoriteCount", 0))
                )
            )
            videos.append(video)
            
        return videos

    def search_videos(self, query: str, max_results: int = 5, published_after: Optional[str] = None) -> List[Any]:
        """Search for videos in a niche (useful for recommendations)"""
        logger.info(f"Searching for trending videos: {query}")
        search_request = self.youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            order="viewCount",
            maxResults=max_results,
            publishedAfter=published_after
        )
        response = search_request.execute()
        
        # Return simplified video list
        results = []
        for item in response.get("items", []):
            results.append({
                "id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"]
            })
        return results
