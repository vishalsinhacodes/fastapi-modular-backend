class AppError(Exception):
    """Base class for application-level erros."""
    def __init__(self, message: str, code: str | None = None, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)
        
class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", code: str = "NOT_FOUND"):
        super().__init__(message=message, code=code, status_code=404)
        
class ConflictError(AppError):
    def __init__(self, message: str = "Conflict", code: str = "CONFLICT"):
        super().__init__(message=message, code=code, status_code=409)
        
class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized", code: str = "UNAUTHORIZED"):
        super().__init__(message=message, code=code, status_code=401)