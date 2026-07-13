"""Domain-level errors raised by the service layer.

Routers catch these and translate them into HTTP responses. Nothing in this
module (or in services.py / repositories.py) should import FastAPI — that
keeps the business logic testable and reusable outside of a request context.
"""


class DomainError(Exception):
    """Base class for all service-layer errors."""


class NotFoundError(DomainError):
    def __init__(self, resource: str):
        self.resource = resource
        super().__init__(f"{resource} not found")


class ConflictError(DomainError):
    pass


class UnauthorizedError(DomainError):
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(message)


class ForbiddenError(DomainError):
    def __init__(self, message: str = "Not enough permissions"):
        super().__init__(message)
