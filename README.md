# meta-threads-scraper

Thư viện Python để cào (scrape) dữ liệu từ [Threads](https://www.threads.com) (Meta) thông qua các GraphQL endpoint nội bộ của nền tảng: feed bài viết, tìm kiếm người dùng, chi tiết bài viết, thông tin & bài viết của người dùng.

> ⚠️ Đây là dự án sử dụng các API không chính thức (reverse-engineered) của Threads. Hãy dùng có trách nhiệm, tuân thủ Điều khoản dịch vụ của Meta và pháp luật hiện hành. Cookie/session là thông tin nhạy cảm — không commit chúng lên git.

## Yêu cầu

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) (quản lý dependency, khuyến nghị) hoặc `pip`

## Cài đặt

```bash
# Cài bằng uv (đọc pyproject.toml / uv.lock)
uv sync

# Hoặc bằng pip
pip install -e .
```

Dependency chính: `requests`, `pydantic`, `pydantic-settings`, `python-dotenv`.

## Cấu hình

Một số luồng cần đăng nhập (ví dụ lấy thông tin người dùng) thông qua cookie phiên đăng nhập từ trình duyệt. Tạo file `.env` ở thư mục gốc nếu bạn muốn nạp biến môi trường (dự án đã gọi `load_dotenv()`):

```env
THREADS_SESSION_ID=...
THREADS_CSRF_TOKEN=...
```

Để lấy `csrftoken` và `sessionid`:
1. Đăng nhập vào https://www.threads.com bằng trình duyệt.
2. Mở DevTools → tab Application/Storage → Cookies, sao chép giá trị của `csrftoken` và `sessionid`.

## Cấu trúc dự án

```
src/
├── core/
│   └── threads_crawler.py   # Class ThreadsCrawler — entry point chính để gọi API
├── schemas/
│   ├── threads.py           # Pydantic models: Post, PaginationResponse, SearchResponse...
│   └── utils.py             # Cookies model (csrftoken, sessionid)
├── utils/
│   ├── const.py             # URL endpoint GraphQL & headers mặc định
│   ├── payload.py           # Hàm build payload cho từng loại request
│   └── parser.py            # Hàm parse JSON response thành các model ở schemas
└── main.py                  # Ví dụ chạy thử crawler
```

## Sử dụng

### Khởi tạo crawler

```python
from src.core.threads_crawler import ThreadsCrawler
from src.schemas.utils import Cookies

# Không cần đăng nhập (chế độ logged-out)
crawler = ThreadsCrawler()

# Hoặc đăng nhập bằng cookie để truy cập đầy đủ tính năng
cookies = Cookies(
    csrftoken="<your_csrftoken>",
    sessionid="<your_sessionid>",
)
crawler = ThreadsCrawler(cookies=cookies)

# Có thể đi qua proxy
crawler = ThreadsCrawler(cookies=cookies, proxy="http://user:pass@host:port")
```

### Lấy news feed

```python
feed = crawler.get_news_feed(limit=10, cursor_after=None)
print(feed.posts)
print(feed.has_next_page, feed.end_cursor)
```

### Tìm kiếm người dùng theo từ khóa

```python
result = crawler.search_by_keyword("bạn trai", limit=10)
for user in result.users:
    print(user.username, user.full_name)
```

### Lấy chi tiết bài viết (kèm replies)

```python
detail = crawler.get_detail_post("3912145323434720686", limit=10, cursor_after=None)
print(detail.posts)
```

### Lấy user_id từ username

```python
user_id = crawler.get_user_id("mth_ys.06")
print(user_id)
```

### Lấy thông tin & bài viết của người dùng

```python
if user_id:
    user_info = crawler.get_user_info(user_id, cursor_after=None)
    print(user_info.posts)
```

## Chạy thử nhanh

File [src/main.py](src/main.py) chứa ví dụ end-to-end (lấy `user_id` từ username rồi lấy thông tin người dùng):

```bash
uv run python -m src.main
# hoặc
python -m src.main
```

## Dữ liệu trả về

Các phương thức trả về model Pydantic được định nghĩa trong [src/schemas/threads.py](src/schemas/threads.py):

- `PaginationResponse`: `status`, `has_next_page`, `end_cursor`, `posts: List[Post]`
- `SearchResponse`: `status`, `users: List[UserSearchResult]`
- `Post`: thông tin bài viết — `post_id`, `username`, `caption`, `likes`, `replies`, `reposts`, `media_type`, `image_url`, `taken_at`, ...
- `UserSearchResult`: `user_id`, `pk`, `username`, `full_name`, `profile_pic_url`, `is_verified`, ...

## Lưu ý

- Một số endpoint yêu cầu header/payload (`fb_dtsg`, `lsd`, `doc_id`, ...) có thể thay đổi theo phiên bản Threads — nếu request thất bại, hãy lấy lại các giá trị này từ request thực tế trên trình duyệt (DevTools → Network).
- Không hardcode cookie/session trực tiếp trong code khi commit; hãy nạp từ biến môi trường hoặc file cấu hình cục bộ không được track bởi git.
