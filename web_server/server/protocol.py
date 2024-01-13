import enum


class HTTPMethod(enum.Enum):
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


class HTTP400BadRequest(HTTPError):
    def __init__(self, body=None):
        super().__init__(status=400, reason='Bad Request', body=body)


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

    def __str__(self):
        return (
            f'{self.method.value} {self.uri} {self.version.value}\n'
            f'headers: {self.headers}'
        )


class Response:
    def __init__(
        self,
        status: int,
        reason: str,
        headers: dict[str, str] | None = None,
        body: bytes | None = None
    ):
        self.status = status
        self.reason = reason
        self.headers = headers
        self.body = body

    def __str__(self):
        return (
            f'{HTTPVersion.HTTP_1_1.value} {self.status} {self.reason}\n'
            f'headers: {self.headers}'
        )


class HTTProtocol:
    MAX_LINE = 64 * 1024
    MAX_HEADERS = 100
    META_ENCODING = 'iso-8859-1'

    @staticmethod
    def get_request(rfile) -> Request:
        method, uri, version = HTTProtocol._parse_starting_line(rfile)
        headers = HTTProtocol._parse_headers(rfile)
        if not headers.get('Host'):
            raise HTTP400BadRequest(body='Invalid headers: no `Host` header')
        return Request(
            method=method,
            uri=uri,
            version=version,
            headers=headers
        )

    @staticmethod
    def send_response(response: Response, wfile) -> None:
        starting_line = (
            f'{HTTPVersion.HTTP_1_1.value} '
            f'{response.status} '
            f'{response.reason}'
            f'\r\n'
        )
        wfile.write(starting_line.encode(HTTProtocol.META_ENCODING))

        if response.headers:
            for k, v in response.headers.items():
                header_line = f'{k}: {v}\r\n'
                wfile.write(header_line.encode(HTTProtocol.META_ENCODING))

        wfile.write(b'\r\n')
        if response.body:
            wfile.write(response.body)
        wfile.flush()
        wfile.close()

    @staticmethod
    def _parse_starting_line(rfile) -> tuple[HTTPMethod, str, HTTPVersion]:
        raw_bytes = rfile.readline(HTTProtocol.MAX_LINE + 1)
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
    def _parse_headers(rfile):
        headers = []
        while True:
            line = rfile.readline(HTTProtocol.MAX_LINE + 1)
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
