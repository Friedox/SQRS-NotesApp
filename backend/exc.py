from typing import ClassVar


class ServiceException(ValueError):
    code: ClassVar[int] = 500

    def __init__(self, message: str):
        super().__init__(message)
