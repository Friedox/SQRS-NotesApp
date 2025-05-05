from typing import ClassVar


class ServiceException(ValueError):
    code: ClassVar[int] = 500

    def __init__(self, message: str):
        super().__init__(message)


class EmailAlreadyInUseError(ServiceException):
    code = 400

    def __init__(self, email: str):
        super().__init__(f"Email '{email}' already in use.")
