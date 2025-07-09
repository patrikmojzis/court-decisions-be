from app.exceptions.app_exception import AppException


class HttpException(AppException):

    def __init__(self, error_type, status_code, *, message=None, data=None):
        super().__init__(error_type)
        self._message = message
        self._error_type = error_type
        self._status_code = status_code
        self._data = data

    def dict(self):
        return {
            "error_type": self._error_type,
            "message": self._message,
            "data": self._data
        }

    @property
    def status_code(self):
        return self._status_code

    @property
    def error_type(self):
        return self._error_type
