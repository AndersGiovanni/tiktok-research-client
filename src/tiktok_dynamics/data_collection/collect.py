"""Collecting data from TikTok API."""
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

        url: str = "https://open.tiktokapis.com/v2/research/video/query/?fields=id,region_code,like_count,username,video_description,music_id,comment_count,share_count,view_count,effect_ids,hashtag_names,playlist_id,voice_to_text"  # noqa

        date_ranges: List[tuple[str, str]] = generate_date_ranges("20230101", 100)

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

        data: List[Dict[str, str]] = list()

        for date_range in date_ranges:
            has_more_data: bool = True

            query["start_date"] = date_range[0]

            query["end_date"] = date_range[1]

            # Check if we have reached the max size
            if len(data) >= max_size:
                break

            # Keep querying until there is no more data
            while has_more_data:
                response: Dict[str, str] = self.fetch_data(url, query)

                data.extend(response["data"]["videos"])

                has_more_data = response["data"]["has_more"]

                query["cursor"] = response["data"]["cursor"]

                query["search_id"] = response["data"]["search_id"]

                # Check if we have reached the max size or there is no more data
                if not has_more_data or len(data) >= max_size:
                    del query["cursor"]
                    del query["search_id"]
                    break

        logging.info(f"Collected {len(data)} videos.")

        return data

    def get_user_info(self, username: str) -> Dict[str, str]:
        """Get user info from TikTok API.

        Args:
            username (str): TikTok username.

        Returns:
            Dict[str, str]: User info.
        """
        headers: Dict[str, str] = self._get_headers()

        url: str = "https://open.tiktokapis.com/v2/research/user/info/?fields=display_name,bio_description,avatar_url,is_verified,follower_count,following_count,likes_count,video_count"  # noqa

        payload: Dict[str, str] = {
            "username": username,
        }

        response: Response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30,
        )

        # Check if the response is successful
        response.raise_for_status()

        data = response.json()["data"]

        data["videos"] = self._get_user_videos(username)

        return data

    def search_keyword(
        self,
        keywords: List[str],
        paginate: bool = True,
        collect_max: int = 100,
        start_date: str = "2021-01-01",
        total_days: int = 100,
        region_code: str = "US",
        collect_comments: bool = False,
    ) -> List[Dict[str, str]]:
        """Search keyword from TikTok API.

        Args:
            keywords (str): TikTok keyword.
            paginate (bool): Whether to paginate. Defaults to False.
            start_date (str): Start date in YYYYMMDD format.
            total_days (int): Total number of days to collect.
            collect_max (int): Max number of videos to collect. Defaults to 100.
            start_date (str): What should the start date be? Default: 2022-01-01
            total_days (int): How big of a window should we look for? Collect max has higher priority. Default: 100 days
            region_code (str): Which regions/countries? Separate by ','. Select 'ALL' for all countries. Default: US
            collect_comments (bool): Whether to collect comments. Defaults to False.

        Returns:
            List[Dict[str, str]]: Keyword info.
        """
        headers: Dict[str, str] = self._get_headers()

        url: str = "https://open.tiktokapis.com/v2/research/video/query/?fields=id,region_code,like_count,username,video_description,music_id,comment_count,share_count,view_count,effect_ids,hashtag_names,playlist_id,voice_to_text"  # noqa

        date_ranges: List[tuple[str, str]] = generate_date_ranges(
            start_date, total_days
        )

        query: Dict[str, Any] = {
            "query": {
                "and": [
                    {
                        "operation": "IN",
                        "field_name": "keyword",
                        "field_values": keywords,
                    },
                ]
            },
            "start_date": date_ranges[0][0],
            "end_date": date_ranges[0][1],
            "max_count": collect_max if collect_max <= 100 else 100,
        }

        if region_code != "ALL":
            query["query"]["and"].append(
                {
                    "operation": "IN",
                    "field_name": "region_code",
                    "field_values": region_code.split(","),
                }
            )

        response: Response = requests.post(
            url,
            headers=headers,
            json=query,
            timeout=30,
        )

        response.raise_for_status()

        date_ranges.pop(0)

        response_json: Dict[str, Any] = response.json()

        data: List[Dict[str, str]] = list()

        if paginate:
            # has_more: bool = True
            has_more = response_json["data"]["has_more"]

            while (has_more or len(date_ranges) > 0) and collect_max > len(data):
                query["cursor"] = response_json["data"]["cursor"]

                query["search_id"] = response_json["data"]["search_id"]

                data.extend(response_json["data"]["videos"])

                response: Response = requests.post(
                    url,
                    headers=headers,
                    json=query,
                    timeout=30,
                )

                response.raise_for_status()

                response_json = response.json()

                # Log start and end date
                logging.info(
                    f"Start date: {query['start_date']}, end date: {query['end_date']}"
                )
                logging.info(f"Collected {len(data)} videos.")

                has_more: bool = response_json["data"]["has_more"]

                if response_json["data"]["has_more"] is False and len(date_ranges) > 0:
                    query["start_date"] = date_ranges[0][0]
                    query["end_date"] = date_ranges[0][1]

                    date_ranges.pop(0)

                    has_more = True

        else:
            # Check if the response is successful
            response.raise_for_status()

        if collect_comments:
            for idx, video in tqdm(
                enumerate(data),
                desc="Collecting comments",
                total=len(data),
                smoothing=0.1,
            ):
                if video["comment_count"] > 0:
                    comments = self._get_comments(video["id"])
                    data[idx]["comments"] = comments

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
            print(f"An error occurred: {e}")
            return None  # or however you want to handle failures
        else:
            return response.json()  # Assuming the response is JSON formatted
            data = response.json()

    def _get_comments(self, video_id: int, max_count: int = 10) -> List[Dict[str, str]]:
        url: str = "https://open.tiktokapis.com/v2/research/video/comment/list/?fields=id,like_count,create_time,text,video_id,parent_comment_id"

        headers: Dict[str, str] = self._get_headers()

        query: Dict[str, Any] = {
            "video_id": video_id,
            "max_count": max_count if max_count <= 100 else 100,
        }

        response: Response = requests.post(
            url,
            headers=headers,
            json=query,
            timeout=30,
        )

        # if repo
        if response.status_code == 500:
            logging.info(f"ID: {video_id}\nError: {response.json()}")
            return []

        comments: List[Dict[str, str]] = response.json()["data"]["comments"]

        if response.json()["data"]["has_more"] and len(comments) < max_count:
            while response.json()["data"]["has_more"]:
                query["cursor"] = response.json()["data"]["cursor"]
                response: Response = requests.post(
                    url,
                    headers=headers,
                    json=query,
                    timeout=30,
                )

                if response.status_code == 500:
                    logging.info(f"ID: {video_id}\nError: {response.json()}")
                    return comments

                comments.extend(response.json()["data"]["comments"])

        else:
            comments = response.json()["data"]["comments"]

        return comments

    def _get_user_videos(
        self, username: str, start_date: str = "2021-01-01"
    ) -> List[Dict[str, str]]:
        """Get user videos from TikTok API.

        Args:
            username (str): TikTok username.

        Returns:
            List[Dict[str, str]]: User videos.
        """
        headers: Dict[str, str] = self._get_headers()

        url: str = "https://open.tiktokapis.com/v2/research/video/query/?fields=id,region_code,like_count,username,video_description,music_id,comment_count,share_count,view_count,effect_ids,hashtag_names,playlist_id,voice_to_text"  # noqa

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
            has_more: bool = True

            while has_more:
                query["start_date"] = start_date
                query["end_date"] = end_date

                response: Response = requests.post(
                    url,
                    headers=headers,
                    json=query,
                    timeout=30,
                )

                if response.status_code == 500:
                    logging.info(f"ID: {username}\nError: {response.json()}")
                    return videos

                videos.extend(response.json()["data"]["videos"])

                has_more: bool = response.json()["data"]["has_more"]

                if has_more:
                    query["cursor"] = response.json()["data"]["cursor"]

                    query["search_id"] = response.json()["data"]["search_id"]

            # remove cursor and search_id
            query.pop("cursor", None)
            query.pop("search_id", None)

        return videos


if __name__ == "__main__":
    client = TiktokClient()

    # Get user info
    terms = ["climate", "global warming", "climate change"]

    data = client.search(terms, max_size=25)

    # a = 1
