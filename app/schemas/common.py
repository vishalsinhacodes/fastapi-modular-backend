from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None