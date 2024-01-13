import enum


class Method(enum.Enum):
    OPTIONS = 'OPTIONS'
    GET = 'GET'
    HEAD = 'HEAD'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'
    TRACE = 'TRACE'
    CONNECT = 'CONNECT'


class HTTPVersion(enum.Enum):
    HTTP_0_9 = 'HTTP/0.9'
    HTTP_1_0 = 'HTTP/1.0'
    HTTP_1_1 = 'HTTP/1.1'
    HTTP_2 = 'HTTP/2'
    HTTP_3 = 'HTTP/3'


class HTTPError(Exception):
    def __init__(self, status: int, reason: str, body=None):
        super()
        self.status = status
        self.reason = reason
        self.body = body


class HTTP403Forbidden(HTTPError):
    def __init__(self, body=None):
        super().__init__(status=403, reason='Forbidden', body=body)


class HTTP404NotFound(HTTPError):
    def __init__(self, body=None):
        super().__init__(status=404, reason='Not Found', body=body)


class HTTP405MethodNotAllowed(HTTPError):
    def __init__(self, body=None):
        super().__init__(status=405, reason='Method Not Allowed', body=body)


class HTTP500InternalServerError(HTTPError):
    def __init__(self, body=None):
        super().__init__(status=500, reason='Internal Server Error', body=body)


class Request:
    def __init__(
        self,
        method: Method,
        uri: str,
        version: HTTPVersion,
        headers: list[tuple[str, str]] | None = None,
        body: bytes | None = None
    ):
        self.method = method
        self.uri = uri
        self.version = version
        self.headers = headers
        self.body = body


class Response:
    def __init__(
        self,
        status,
        reason: str,
        headers: list[tuple[str, str]] | None = None,
        body: bytes | None = None
    ):
        self.status = status
        self.reason = reason
        self.headers = headers
        self.body = body


class HTTProtocol:

    @staticmethod
    def get_request(rfile) -> Request:
        pass

    @staticmethod
    def send_response(response: Response, wfile) -> None:
        pass
