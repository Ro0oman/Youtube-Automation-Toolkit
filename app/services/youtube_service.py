import os
from googleapiclient.discovery import build
from loguru import logger
from typing import List, Optional, Dict, Any
from app.models.schemas import Video, VideoMetadata, VideoStats, Channel, ChannelStats
from dotenv import load_dotenv

load_dotenv()

class YouTubeService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY not found in environment variables")
        
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
            stats=ChannelStats(**stats)
        )

    def get_videos(self, channel_id: str, max_results: int = 50) -> List[Video]:
        logger.info(f"Fetching latest {max_results} videos for channel: {channel_id}")
        
        # First, get the 'uploads' playlist ID
        channel_request = self.youtube.channels().list(
            part="contentDetails",
            id=channel_id
        )
        channel_response = channel_request.execute()
        uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # Fetch videos from the uploads playlist
        videos = []
        next_page_token = None
        
        while len(videos) < max_results:
            playlist_request = self.youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=uploads_playlist_id,
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page_token
            )
            playlist_response = playlist_request.execute()

            video_ids = [item["contentDetails"]["videoId"] for item in playlist_response["items"]]
            if not video_ids:
                break
            
            # Fetch detailed stats for these videos
            video_details = self._get_video_details(video_ids)
            videos.extend(video_details)

            next_page_token = playlist_response.get("nextPageToken")
            if not next_page_token:
                break

        return videos

    def _get_video_details(self, video_ids: List[str]) -> List[Video]:
        request = self.youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids)
        )
        response = request.execute()
        
        videos = []
        for item in response.get("items", []):
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
                stats=VideoStats(**stats)
            )
            videos.append(video)
            
        return videos

    def search_videos(self, query: str, max_results: int = 10, published_after: Optional[str] = None) -> List[Video]:
        """Search for videos by keyword/topic"""
        logger.info(f"Searching for videos with query: {query}")
        
        search_params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "order": "viewCount"
        }
        
        if published_after:
            search_params["publishedAfter"] = published_after
            
        request = self.youtube.search().list(**search_params)
        response = request.execute()
        
        video_ids = [item["id"]["videoId"] for item in response.get("items", [])]
        if not video_ids:
            return []
            
        return self._get_video_details(video_ids)
