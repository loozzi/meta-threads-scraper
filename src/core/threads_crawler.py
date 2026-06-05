import json

from typing import Optional
import requests as req

from src.utils.const import GRAPH_API, HEADERS
from src.utils.payload import get_feed_payload, get_user_payload, get_search_payload
from src.schemas.utils import Cookies




class ThreadsCrawler():
    def __init__(self, cookies: Optional[Cookies]=None):
        self.__headers = HEADERS

        if cookies is None:
            self.__headers["x-root-field-name"] = "xdt_threads_logged_out_feed"
            self.__headers["x-fb-friendly-name"] = "BarcelonaLoggedOutFeedPaginationQuery"
            self.__headers["X-LOGGED-OUT-THREADS-MIGRATED-REQUEST"] = "true"
            self.__headers["x-csrftoken"] = "VkRNpSzzHAPj35wdPdO8NIN69d2D2Qkt"
            self.__cookies = None
        else:
            self.__headers["x-csrftoken"] = cookies.csrftoken
            self.__cookies = cookies.model_dump()

        self.__session = req.session()
        self.__session.headers.update(self.__headers)
    
    def _make_request(self, payload: dict, headers: Optional[dict] = {}, use_cookies: bool = False) -> req.Response:
        return self.__session.post(
            GRAPH_API, 
            data=payload,
            cookies=self.__cookies if use_cookies else None,
            headers={
                **self.__headers,
                **headers
            },
            verify=False
        )

    # Crawler
    def get_news_feed(self, limit: int = 10) -> dict:
        is_logged_in = self.__cookies is not None
        payload = get_feed_payload(limit=limit, logged_in=is_logged_in)
        
        response = self._make_request(payload, use_cookies=True)

        return response