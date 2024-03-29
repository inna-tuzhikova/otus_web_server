import enum
from io import BufferedReader, BufferedWriter


class HTTPMethod(enum.Enum):
    """HTTP methods"""

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
    """HTTP versions"""

    HTTP_0_9 = 'HTTP/0.9'
    HTTP_1_0 = 'HTTP/1.0'
    HTTP_1_1 = 'HTTP/1.1'
    HTTP_2 = 'HTTP/2'
    HTTP_3 = 'HTTP/3'


class HTTPError(Exception):
    """Base HTTP error"""

    def __init__(
        self,
        status: int,
        reason: str,
        body: bytes | str | None = None
    ):
        super()
        self.status = status
        self.reason = reason
        self.body = body


class HTTP400BadRequest(HTTPError):
    """HTTP error with status code 400 Bad Request"""

    def __init__(self, body: bytes | str | None = None):
        super().__init__(status=400, reason='Bad Request', body=body)


class HTTP403Forbidden(HTTPError):
    """HTTP error with status code 403 Forbidden"""

    def __init__(self, body: bytes | str | None = None):
        super().__init__(status=403, reason='Forbidden', body=body)


class HTTP404NotFound(HTTPError):
    """HTTP error with status code 404 Not Found"""

    def __init__(self, body: bytes | str | None = None):
        super().__init__(status=404, reason='Not Found', body=body)


class HTTP405MethodNotAllowed(HTTPError):
    """HTTP error with status code 405 Method Not Allowed"""

    def __init__(self, body: bytes | str | None = None):
        super().__init__(status=405, reason='Method Not Allowed', body=body)


class HTTP500InternalServerError(HTTPError):
    """HTTP error with status code 500 Internal Server Error"""

    def __init__(self, body: bytes | str | None = None):
        super().__init__(status=500, reason='Internal Server Error', body=body)


class Request:
    """Client HTTP request"""

    def __init__(
        self,
        method: HTTPMethod,
        uri: str,
        version: HTTPVersion,
        headers: dict[str, str] | None = None,
        body: bytes | None = None
    ):
        self.method = method
        self.uri = uri
        self.version = version
        self.headers = headers
        self.body = body

    def __str__(self) -> str:
        return (
            f'{self.method.value} {self.uri} {self.version.value}\n'
            f'headers: {self.headers}'
        )


class Response:
    """HTTP response to client"""

    def __init__(
        self,
        status: int,
        reason: str,
        headers: dict[str, str] | None = None,
        body: bytes | str | None = None
    ):
        self.status = status
        self.reason = reason
        self.headers = headers
        self.body = body

    def __str__(self) -> str:
        return (
            f'{HTTPVersion.HTTP_1_1.value} {self.status} {self.reason}\n'
            f'headers: {self.headers}'
        )


class HTTP200OKResponse(Response):
    """HTTP response with status code 200 OK"""

    def __init__(
        self,
        headers: dict[str, str] | None = None,
        body: bytes | str | None = None
    ):
        super().__init__(status=200, reason='OK', headers=headers, body=body)


class HTTProtocol:
    """Static class for making io operations with HTTP format"""

    MAX_LINE = 64 * 1024
    MAX_HEADERS = 100
    META_ENCODING = 'iso-8859-1'

    @staticmethod
    def get_request(reader: BufferedReader) -> Request:
        """Reads, parses and transforms client HTTP request"""
        method, uri, version = HTTProtocol._parse_starting_line(reader)
        headers = HTTProtocol._parse_headers(reader)
        if not headers.get('Host'):
            raise HTTP400BadRequest(body='Invalid headers: no `Host` header')
        return Request(
            method=method,
            uri=uri,
            version=version,
            headers=headers
        )

    @staticmethod
    def send_response(response: Response, writer: BufferedWriter) -> None:
        """Sends HTTP response to client"""
        starting_line = (
            f'{HTTPVersion.HTTP_1_1.value} '
            f'{response.status} '
            f'{response.reason}'
            f'\r\n'
        )
        writer.write(starting_line.encode(HTTProtocol.META_ENCODING))
        if not response.headers:
            response.headers = dict()
        response.headers['Server'] = 'python'
        for k, v in response.headers.items():
            header_line = f'{k}: {v}\r\n'
            writer.write(header_line.encode(HTTProtocol.META_ENCODING))

        writer.write(b'\r\n')
        if response.body:
            if isinstance(response.body, str):
                response.body = response.body.encode(HTTProtocol.META_ENCODING)
            writer.write(response.body)
        writer.flush()
        writer.close()

    @staticmethod
    def _parse_starting_line(
        reader: BufferedReader
    ) -> tuple[HTTPMethod, str, HTTPVersion]:
        raw_bytes = reader.readline(HTTProtocol.MAX_LINE + 1)
        if len(raw_bytes) > HTTProtocol.MAX_LINE:
            raise HTTP400BadRequest(body='Request starting line is too long')

        starting_line = str(raw_bytes, HTTProtocol.META_ENCODING)
        words = starting_line.rstrip('\r\n').split()
        if len(words) != 3:
            raise HTTP400BadRequest(body='Malformed request starting line')

        method, uri, version = words
        try:
            method = HTTPMethod(method)
        except ValueError:
            raise HTTP405MethodNotAllowed(body=f'Unknown method: {method}')
        try:
            version = HTTPVersion(version)
        except ValueError:
            raise HTTP400BadRequest(body=f'Unknown HTTP version: {version}')
        if version != HTTPVersion.HTTP_1_1:
            raise HTTP400BadRequest(body=(
                f'Unsupported HTTP version: {version}. '
                f'Only {HTTPVersion.HTTP_1_1.value} is supported'
            ))
        return method, uri, version

    @staticmethod
    def _parse_headers(reader: BufferedReader) -> dict[str, str]:
        headers = []
        while True:
            line = reader.readline(HTTProtocol.MAX_LINE + 1)
            if len(line) > HTTProtocol.MAX_LINE:
                raise HTTP400BadRequest(body='Request line is too long')
            if line in (b'\r\n', b'\n', b''):
                break
            headers.append(line)
            if len(headers) > HTTProtocol.MAX_HEADERS:
                raise HTTP400BadRequest(body='Too many headers')
        result = {}
        for h in headers:
            h = h.decode(HTTProtocol.META_ENCODING)
            k, v = h.split(': ', maxsplit=1)
            result[k] = v
        return result
