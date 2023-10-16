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
    
    def search(self, keywords: List[str], max_size: int = 1000) -> Dict[str, str]:

        headers: Dict[str, str] = self._get_headers()

        url: str = "https://open.tiktokapis.com/v2/research/video/query/?fields=id,region_code,like_count,username,video_description,music_id,comment_count,share_count,view_count,effect_ids,hashtag_names,playlist_id,voice_to_text"  # noqa

        date_ranges: List[tuple[str,str]] = generate_date_ranges("20230101", 100)

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
                    }
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

    def get_user_info(
        self, username: str
    ) -> Dict[str, str]:
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

        return response.json()

    def search_keyword(
        self, keywords: List[str], paginate: bool = False, start_date: str, total_days: int, collect_max: int = 100
    ) -> List[Dict[str, str]]:
        """Search keyword from TikTok API.

        Args:
            keywords (str): TikTok keyword.
            paginate (bool): Whether to paginate. Defaults to False.
            start_date (str): Start date in YYYYMMDD format.
            total_days (int): Total number of days to collect.
            collect_max (int): Max number of videos to collect. Defaults to 100.

        Returns:
            List[Dict[str, str]]: Keyword info.
        """
        headers: Dict[str, str] = self._get_headers()

        url: str = "https://open.tiktokapis.com/v2/research/video/query/?fields=id,region_code,like_count,username,video_description,music_id,comment_count,share_count,view_count,effect_ids,hashtag_names,playlist_id,voice_to_text"  # noqa

        # dates: List[Tuple[str, str]] = generate_date_ranges(start_date, total_days)

        query: Dict[str, Any] = {
            "query": {
                "and": [
                    {
                        "operation": "IN",
                        "field_name": "region_code",
                        "field_values": ["US", "CA"],
                    },
                    {
                        "operation": "IN",
                        "field_name": "keyword",
                        "field_values": keywords,
                    },
                ]
            },
            "start_date": "20220601",
            "end_date": "20220630",
            # "max_count": 10,
        }

        response: Response = requests.post(
            url,
            headers=headers,
            json=query,
            timeout=30,
        )

        response_json: Dict[str, Any] = response.json()

        data: List[Dict[str, str]] = list()

        if paginate:
            has_more: bool = True

            while has_more and collect_max > len(data):
                has_more = response_json["data"]["has_more"]

                query["cursor"] = response_json["data"]["cursor"]

                query["search_id"] = response_json["data"]["search_id"]

                data.extend(response_json["data"]["videos"])

                response: Response = requests.post(
                    url,
                    headers=headers,
                    json=query,
                    timeout=30,
                )

                response_json = response.json()

                logging.info(f"Collected {len(data)} videos.")

            return data

        else:
            # Check if the response is successful
            response.raise_for_status()

            return response.json()
        
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), before=before_log(logger, logging.INFO))
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


if __name__ == "__main__":
    client = TiktokClient()

    # Get user info
    terms = ['climate', 'global warming', 'climate change']

    data = client.search(terms, max_size=25)

    a = 1
