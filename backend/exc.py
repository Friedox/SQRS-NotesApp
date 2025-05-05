from typing import ClassVar


class ServiceException(ValueError):
    code: ClassVar[int] = 500

    def __init__(self, message: str):
        super().__init__(message)


class EmailAlreadyInUseError(ServiceException):
    code = 400

    def __init__(self, email: str):
        super().__init__(f"Email '{email}' already in use.")


class InvalidCredentialsError(ServiceException):
    code = 401

    def __init__(self):
        super().__init__("Invalid credentials.")


class UserNotFoundError(ServiceException):
    code = 404

    def __init__(self):
        super().__init__("User not found.")


class NoteNotFoundError(ServiceException):
    code = 404

    def __init__(self, note_id: int):
        super().__init__(f"Note with ID {note_id} not found")
