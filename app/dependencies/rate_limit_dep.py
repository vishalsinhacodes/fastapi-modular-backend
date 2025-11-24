from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.rate_limiter import rate_limit
from app.core.security import get_current_user
from app.models.user import UserModel

def rate_limit_dependency(
    request: Request,
    current_user: UserModel = Depends(get_current_user),
) -> None:
    route = request.url.path
    rate_limit(user_id=current_user, route=route, limit=10, window_seconds=60)