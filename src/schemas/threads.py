from pydantic import BaseModel, Field
from typing import Optional, List, Tuple, Literal


class SelfThreadInfo(BaseModel):
    self_thread_length: int 
    post_position_in_self_thread: int


class Post(BaseModel):
    post_id: str = Field(..., description="Post id")
    code: str = Field(..., description="Post code")
    username: str = Field(..., description="Username")
    user_pk: str = Field(..., description="User primary key")
    is_verified: bool = Field(..., description="Verified status")
    caption: str = Field(..., description="Caption of post")
    accessibility_caption: Optional[str] = None
    media_type: Literal[1, 8, 19] = 19
    # 1 = image, 8 = carousel, 19 = text only
    image_url: Optional[str] = None
    carousel_media: List[dict] = []
    likes: int = 0
    replies: int = 0
    reposts: int = 0
    quotes: int = 0
    reshares: Optional[int] = 0
    thread_info: SelfThreadInfo
    taken_at: int = Field(..., description="Time post thread")


class UserSearchResult(BaseModel):
    user_id: str
    pk: str
    username: str
    full_name: str
    profile_pic_url: Optional[str] = None
    is_verified: bool = False
    is_active_on_text_post_app: bool = False


class SearchResponse(BaseModel):
    status: str = 'ok'
    users: List[UserSearchResult] = []


class PaginationResponse(BaseModel):
    status: str = 'ok'
    has_next_page: bool = False
    end_cursor: Optional[str] = None
    posts: List[Post] = []

