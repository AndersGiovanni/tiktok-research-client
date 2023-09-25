"""Collecting data from TikTok API."""
import logging
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Union

import requests
from dotenv import load_dotenv
from requests.models import Response

from tiktok_dynamics.config import DATA_DIR
from tiktok_dynamics.utils import save_json


logging.basicConfig(level=logging.INFO)

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

    def get_access_token(self) -> Response:
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

    def get_user_info(self, username: str) -> Response:
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
        self, keywords: List[str], paginate: bool = False, collect_max: int = 100
    ) -> List[Dict[str, str]]:
        """Search keyword from TikTok API.

        Args:
            keywords (str): TikTok keyword.
            paginate (bool): Whether to paginate. Defaults to False.
            collect_max (int): Max number of videos to collect. Defaults to 100.

        Returns:
            List[Dict[str, str]]: Keyword info.
        """
        headers: Dict[str, str] = self._get_headers()

        url: str = "https://open.tiktokapis.com/v2/research/video/query/?fields=id,region_code,like_count,username,video_description,music_id,comment_count,share_count,view_count,effect_ids,hashtag_names,playlist_id,voice_to_text"  # noqa

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


if __name__ == "__main__":
    client = TiktokClient()

    # Get user info
    user_info = client.get_user_info("joedotie")

    print(user_info)

    # Search keyword
    keyword_info = client.search_keyword(
        ["Donald Trump"], paginate=True, collect_max=100
    )

    # save to json
    save_json(DATA_DIR / "keyword_info.json", keyword_info)

    a = 1
