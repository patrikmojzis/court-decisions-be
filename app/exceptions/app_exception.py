class AppException(Exception):
    def __init__(self, error_type: str):
        self._error_type = error_type
        super().__init__(self._error_type)