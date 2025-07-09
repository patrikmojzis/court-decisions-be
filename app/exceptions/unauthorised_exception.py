from app.exceptions.http_exception import HttpException


class UnauthorisedException(HttpException):

    def __init__(self):
        super().__init__(
            error_type='unauthorised',
            status_code=401,
            message='Unauthorized.'
        )