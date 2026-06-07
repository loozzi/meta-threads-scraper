import json
from typing import Optional

import requests as req

from src.schemas.threads import PaginationResponse, SearchResponse
from src.schemas.utils import Cookies
from src.utils.const import GRAPH_API, HEADERS
from src.utils.parser import (
    parse_detail_pagination_response,
    parse_pagination_response,
    parse_search_response,
)
from src.utils.payload import (
    get_detail_post_payload,
    get_feed_payload,
    get_search_payload,
    get_user_payload,
)


class ThreadsCrawler:
    def __init__(self, cookies: Optional[Cookies] = None, proxy: Optional[str] = None):
        self.__headers = HEADERS
        self.__proxy = proxy

        if cookies is None:
            self.__headers["x-root-field-name"] = "xdt_threads_logged_out_feed"
            self.__headers["x-fb-friendly-name"] = (
                "BarcelonaLoggedOutFeedPaginationQuery"
            )
            self.__headers["X-LOGGED-OUT-THREADS-MIGRATED-REQUEST"] = "true"
            self.__headers["x-csrftoken"] = "VkRNpSzzHAPj35wdPdO8NIN69d2D2Qkt"
            self.__cookies = None
        else:
            self.__headers["x-csrftoken"] = cookies.csrftoken
            self.__cookies = cookies.model_dump()

        self.__session = req.session()
        self.__session.headers.update(self.__headers)
        if self.__proxy:
            self.__session.proxies.update(
                {
                    "http": self.__proxy,
                    "https": self.__proxy,
                }
            )

    def _make_request(
        self, payload: dict, headers: Optional[dict] = {}, use_cookies: bool = False
    ) -> req.Response:
        response = self.__session.post(
            GRAPH_API,
            data=payload,
            cookies=self.__cookies if use_cookies else None,
            headers={**self.__headers, **headers},
            # verify=False,
        )

        if response.status_code != 200:
            print(f"Request failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            # response.raise_for_status()

        if response.json().get("status", "fail") == "fail":
            print(f"API returned failure status: {response.json()}")
            # raise Exception("API request failed")

        return response

    # Crawler
    def get_news_feed(
        self, limit: int = 10, cursor_after: Optional[str] = None
    ) -> PaginationResponse:
        is_logged_in = self.__cookies is not None
        payload = get_feed_payload(
            limit=limit, logged_in=is_logged_in, cursor_after=cursor_after
        )

        response = self._make_request(payload, use_cookies=True)

        return parse_pagination_response(response.json())

    def search_by_keyword(self, keyword: str, limit: int = 10) -> SearchResponse:
        payload = get_search_payload(keyword, limit)

        response = self._make_request(payload)

        return parse_search_response(response.json())

    def get_detail_post(
        self,
        post_id: str,
        limit: int = 10,
        cursor_after: Optional[str] = None,
        use_cookies: bool = False,
    ) -> PaginationResponse:
        payload = get_detail_post_payload(post_id, limit, cursor_after)
        custom_headers = {
            "x-root-field-name": "xdt_api__v1__text_feed__media_id__replies__connection",
            "x-fb-friendly-name": "BarcelonaPostPageDirectQuery",
        }

        response = self._make_request(
            payload, headers=custom_headers, use_cookies=use_cookies
        )

        return parse_detail_pagination_response(response.json())
