from typing import Optional

from src.schemas.threads import PaginationResponse, Post, SearchResponse, SelfThreadInfo, UserSearchResult


def _parse_post_obj(post: dict) -> Optional[Post]:
    try:
        info = post['text_post_app_info']
        candidates = post['image_versions2']['candidates']
        carousel = post.get('carousel_media')
        user = post['user']
        self_thread = info.get('self_thread_info') or {}

        if carousel:
            image_url = None
            carousel_media = [
                {'url': m['image_versions2']['candidates'][0]['url'], 'width': m['image_versions2']['candidates'][0]['width'], 'height': m['image_versions2']['candidates'][0]['height']}
                for m in carousel
                if m.get('image_versions2') and m['image_versions2'].get('candidates')
            ]
        elif candidates:
            image_url = candidates[0]['url']
            carousel_media = []
        else:
            image_url = None
            carousel_media = []

        return Post(
            post_id=post['pk'],
            code=post['code'],
            username=user['username'],
            user_pk=user['pk'],
            is_verified=user.get('is_verified', False),
            caption=post.get('caption', {}).get('text', '') if post.get('caption') else '',
            accessibility_caption=post.get('accessibility_caption'),
            media_type=post.get('media_type', 19),
            image_url=image_url,
            carousel_media=carousel_media,
            likes=post.get('like_count', 0),
            replies=info.get('direct_reply_count', 0),
            reposts=info.get('repost_count', 0),
            quotes=info.get('quote_count', 0),
            reshares=info.get('reshare_count') or 0,
            thread_info=SelfThreadInfo(
                self_thread_length=self_thread.get('self_thread_length', 1),
                post_position_in_self_thread=self_thread.get('post_position_in_self_thread', 1),
            ),
            taken_at=post['taken_at'],
        )
    except Exception:
        return None


def parse_post_detail(item: dict) -> Optional[Post]:
    try:
        node = item.get('node') or {}
        if node.get('text_post_app_thread'):
            thread = node['text_post_app_thread']
        else:
            thread = item['text_post_app_thread']
        return _parse_post_obj(thread['thread_items'][0]['post'])
    except Exception:
        return None


def parse_search_response(response: dict) -> SearchResponse:
    status = response.get('status')
    if status != 'ok':
        return SearchResponse(status=status)

    edges = response['data']['xdt_api__v1__users__search_connection']['edges']
    users = [
        UserSearchResult(
            user_id=node['id'],
            pk=node['pk'],
            username=node['username'],
            full_name=node.get('full_name', ''),
            profile_pic_url=node.get('profile_pic_url'),
            is_verified=node.get('is_verified', False),
            is_active_on_text_post_app=node.get('is_active_on_text_post_app', False),
        )
        for edge in edges
        if (node := edge.get('node'))
    ]
    return SearchResponse(status=status, users=users)


def parse_pagination_response(response: dict) -> PaginationResponse:
    status = response.get('status')
    if status != 'ok':
        return PaginationResponse(status=status)

    posts = []
    edges = response['data']['feedData']['edges']
    for edge in edges:
        p = parse_post_detail(edge)
        if p is not None:
            posts.append(p)

    print(f"Success: {len(posts)} - Error: {len(edges) - len(posts)}")

    return PaginationResponse(
        status=status,
        has_next_page=response['data']['feedData']['page_info']['has_next_page'],
        end_cursor=response['data']['feedData']['page_info']['end_cursor'],
        posts=posts
    )


def parse_detail_pagination_response(response: dict) -> PaginationResponse:
    status = response.get('status')
    if status != 'ok':
        return PaginationResponse(status=status)

    posts = []
    edges = response['data']['data']['edges']
    for edge in edges:
        node = edge.get('node') or {}
        for thread_item in node.get('thread_items', []):
            post_data = thread_item.get('post')
            if post_data:
                p = _parse_post_obj(post_data)
                if p is not None:
                    posts.append(p)

    print(f"Success: {len(posts)} - Error: {len(edges) - len(posts)}")

    return PaginationResponse(
        status=status,
        has_next_page=response['data']['data']['page_info']['has_next_page'],
        end_cursor=response['data']['data']['page_info']['end_cursor'],
        posts=posts
    )

def parse_user_detail_pagination_response(response: dict) -> PaginationResponse:
    status = response.get('status')

    if status != 'ok':
        return PaginationResponse(status=status)

    posts = []
    edges = response['data']['mediaData']['edges']
    for edge in edges:
        node = edge.get('node') or {}
        for thread_item in node.get('thread_items', []):
            post_data = thread_item.get('post')
            if post_data:
                p = _parse_post_obj(post_data)
                if p is not None:
                    posts.append(p)

    print(f"Success: {len(posts)} - Error: {len(edges) - len(posts)}")

    return PaginationResponse(
        status=status,
        has_next_page=response['data']['mediaData']['page_info']['has_next_page'],
        end_cursor=response['data']['mediaData']['page_info']['end_cursor'],
        posts=posts
    )
    
def parse_user_id(response: dict) -> Optional[str]:
    try:
        payloads = response["payload"]["payloads"]
        for route_data in payloads.values():
            user_id = (
                route_data
                .get("result", {})
                .get("exports", {})
                .get("rootView", {})
                .get("props", {})
                .get("user_id")
            )
            if user_id:
                return user_id
    except (KeyError, AttributeError):
        return None

    return None
