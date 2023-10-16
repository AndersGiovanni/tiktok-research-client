"""Collecting data from TikTok API."""
import datetime
import logging
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

import requests
from dotenv import load_dotenv
from requests.models import Response
from tenacity import retry, stop_after_attempt, wait_fixed, before_log

from tiktok_dynamics.config import DATA_DIR
from tiktok_dynamics.utils import generate_date_ranges
from tiktok_dynamics.utils import save_json
from tqdm import tqdm

from tiktok_dynamics.config import DATA_DIR
from tiktok_dynamics.utils import save_json, generate_date_ranges


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class TiktokClient:
    """TikTok API client."""

    def __init__(self) -> None:
        """Initialize TikTok API client."""
        self.access_token: Union[str, None] = None

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for TikTok API."""
        access_token: Dict[str, str] = self.get_access_token()

        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token['access_token']}",
        }

    def get_access_token(self) -> Dict[str, str]:
        """Get access token from TikTok API.

        The access token is valid for 7200 seconds.

        Returns:
            Dict[str, str]: Access token and its expiration time.
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache",
        }

        payload = {
            "client_key": os.environ["CLIENT_KEY"],
            "client_secret": os.environ["CLIENT_SECRET"],
            "grant_type": os.environ["GRANT_TYPE"],
        }

        response: Response = requests.post(
            "https://open.tiktokapis.com/v2/oauth/token/",
            headers=headers,
            data=payload,
            timeout=30,
        )

        # Check if the response is successful
        response.raise_for_status()

        return response.json()

    def query(self, query: Dict[Any, Any], url: str) -> Dict[str, str]:
        """Query TikTok API.

        Args:
            query (Dict[Any, Any]): Custom query. Follow the documentation from https://developers.tiktok.com/doc/research-api-specs-query-videos/ # noqa
            url (str): TikTok API url.

        Returns:
            Response: Response from TikTok API.
        """

        headers: Dict[str, str] = self._get_headers()

        response: Response = requests.post(
            url,
            headers=headers,
            json=query,
            timeout=30,
        )

        # Check if the response is successful
        response.raise_for_status()

        return response.json()

    def search(self, keywords: List[str], max_size: int = 1000) -> List[Dict[str, str]]:
        headers: Dict[str, str] = self._get_headers()

        url: str = "https://open.tiktokapis.com/v2/research/video/query/?fields=id,region_code,like_count,username,video_description,music_id,comment_count,share_count,view_count,effect_ids,hashtag_names,playlist_id,voice_to_text,create_time"  # noqa

        date_ranges: List[tuple[str, str]] = generate_date_ranges("2023-01-01", 100)

        query: Dict[str, Any] = {
            "query": {
                "and": [
                    {
                        "operation": "IN",
                        "field_name": "keyword",
                        "field_values": keywords,
                    },
                    {
                        "operation": "IN",
                        "field_name": "hashtag_name",
                        "field_values": keywords,
                    },
                ]
            },
            "max_count": 100,
        }

        videos: List[Dict[str, str]] = list()

        for date_range in date_ranges:
            query["start_date"] = date_range[0]

            query["end_date"] = date_range[1]

            # Check if we have reached the max size
            if len(videos) >= max_size:
                break

            # Keep querying until there is no more data
            videos.extend(self._cursor_iterator(url, query))

        logging.info(f"Collected {len(videos)} videos.")

        logging.info("Decoding timestamps...")
        for idx, video in enumerate(videos):
            videos[idx]["create_time"] = datetime.datetime.utcfromtimestamp(
                video["create_time"]
            ).strftime("%Y-%m-%d")

        return videos

    def get_user(self, username: str) -> Dict[str, str]:
        """Get user data and videos from TikTok API.

        Args:
            username (str): TikTok username.

        Returns:
            Dict[str, str]: User info.
        """

        url: str = "https://open.tiktokapis.com/v2/research/user/info/?fields=display_name,bio_description,avatar_url,is_verified,follower_count,following_count,likes_count,video_count"  # noqa

        query: Dict[str, str] = {
            "username": username,
        }

        data = self.fetch_data(url, query)

        data["videos"] = self._get_user_videos(username)

        return data

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        before=before_log(logger, logging.INFO),
    )
    def fetch_data(self, url: str, query: Dict[str, Any]) -> Dict[str, str]:
        """Query TikTok API.

        Args:
            url (str): TikTok API url.
            query (Dict[Any, Any]): Custom query. Follow the documentation from https://developers.tiktok.com/doc/research-api-specs-query-videos/ # noqa

        Returns:
            response (Dict[str, str]): Response from TikTok API.
        """

        headers: Dict[str, str] = self._get_headers()

        try:
            response: Response = requests.post(
                url,
                headers=headers,
                json=query,
                timeout=30,
            )
            response.raise_for_status()  # This will raise a HTTPError for bad responses (4xx and 5xx)
        except requests.RequestException as e:
            logging.error(f"An error occurred: {e}")
            return None  # or however you want to handle failures
        else:
            return response.json()  # Assuming the response is JSON formatted

    def _get_comments(self, video_id: int) -> List[Dict[str, str]]:
        url: str = "https://open.tiktokapis.com/v2/research/video/comment/list/?fields=id,like_count,create_time,text,video_id,parent_comment_id,reply_count"

        query: Dict[str, Any] = {
            "video_id": video_id,
            "max_count": 100,
        }

        comments: List[Dict[str, str]] = list()

        has_more_data: bool = True

        while (
            has_more_data and len(comments) < 1000
        ):  # 1000 is the max number of comments we can get
            response: Dict[str, str] = self.fetch_data(url, query)

            comments.extend(response["data"]["comments"])

            has_more_data = response["data"]["has_more"]

            query["cursor"] = response["data"]["cursor"]

            # Check if we have reached the max size or there is no more data
            if not has_more_data:
                del query["cursor"]
                break

        return comments

    def _get_user_videos(
        self, username: str, start_date: str = "2023-01-01", max_size: int = 1000
    ) -> List[Dict[str, str]]:
        """Get user videos from TikTok API.

        Args:
            username (str): TikTok username.

        Returns:
            List[Dict[str, str]]: User videos.
        """

        url: str = "https://open.tiktokapis.com/v2/research/video/query/?fields=id,region_code,like_count,username,video_description,music_id,comment_count,share_count,view_count,effect_ids,hashtag_names,playlist_id,voice_to_text,create_time"  # noqa

        date_ranges: List[tuple[str, str]] = generate_date_ranges(start_date, 1000)

        query: Dict[str, Any] = {
            "query": {
                "and": [
                    {
                        "operation": "EQ",
                        "field_name": "username",
                        "field_values": [username],
                    },
                ]
            },
            "max_count": 100,
        }

        videos: List[Dict[str, str]] = list()

        for start_date, end_date in date_ranges:
            query["start_date"] = start_date

            query["end_date"] = end_date

            videos.extend(self._cursor_iterator(url, query, max_size))

        return videos

    def _cursor_iterator(
        self, url, query, max_size: int = 1000
    ) -> List[Dict[str, str]]:
        has_more_data: bool = True

        data: List[Dict[str, str]] = list()

        while has_more_data and len(data) < max_size:
            response: Dict[str, str] = self.fetch_data(url, query)

            if response is None:
                return data

            data.extend(response["data"]["videos"])

            has_more_data = response["data"]["has_more"]

            # Check if we have reached the max size or there is no more data
            if not has_more_data:
                return data

            query["cursor"] = response["data"]["cursor"]

            query["search_id"] = response["data"]["search_id"]


if __name__ == "__main__":
    client = TiktokClient()

    # Get user info
    terms = ["climate", "global warming", "climate change"]

    # data = client.search(terms, max_size=1000)

    user = "filspixel"

    data = client.get_user(user)

    save_json(DATA_DIR / f"user/{user}.json", data)

    a = 1
