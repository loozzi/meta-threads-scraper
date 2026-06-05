from pydantic import BaseModel, Field

class Cookies(BaseModel):
    csrftoken: str = Field(..., description="csrf token")
    sessionid: str = Field(..., description="session id")