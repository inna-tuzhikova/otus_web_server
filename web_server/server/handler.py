import mimetypes
from pathlib import Path

from web_server.server.protocol import (
    Response,
    HTTP200OKResponse,
    HTTPError,
    HTTP404NotFound,
    HTTP405MethodNotAllowed,
    HTTP500InternalServerError,
    HTTP403Forbidden,
    Request,
    HTTPMethod
)


class BaseHTTPHandler:
    def __call__(self, request: Request) -> Response:
        if request.method == HTTPMethod.OPTIONS:
            handler = self.options
        elif request.method == HTTPMethod.GET:
            handler = self.get
        elif request.method == HTTPMethod.HEAD:
            handler = self.head
        elif request.method == HTTPMethod.POST:
            handler = self.post
        elif request.method == HTTPMethod.PUT:
            handler = self.put
        elif request.method == HTTPMethod.PATCH:
            handler = self.patch
        elif request.method == HTTPMethod.DELETE:
            handler = self.delete
        elif request.method == HTTPMethod.TRACE:
            handler = self.trace
        elif request.method == HTTPMethod.CONNECT:
            handler = self.connect
        else:
            handler = self.unknown_method_handler

        try:
            response = handler(request)
        except HTTPError as e:
            response = Response(
                status=e.status,
                reason=e.reason,
                body=e.body
            )
        except Exception as e:
            err_500 = HTTP500InternalServerError(body=str(e))
            response = Response(
                status=err_500.status,
                reason=err_500.reason,
                body=err_500.body
            )
        return response

    def options(self, request: Request) -> Response:
        raise HTTP405MethodNotAllowed

    def get(self, request: Request) -> Response:
        raise HTTP405MethodNotAllowed

    def head(self, request: Request) -> Response:
        raise HTTP405MethodNotAllowed

    def post(self, request: Request) -> Response:
        raise HTTP405MethodNotAllowed

    def put(self, request: Request) -> Response:
        raise HTTP405MethodNotAllowed

    def patch(self, request: Request) -> Response:
        raise HTTP405MethodNotAllowed

    def delete(self, request: Request) -> Response:
        raise HTTP405MethodNotAllowed

    def trace(self, request: Request) -> Response:
        raise HTTP405MethodNotAllowed

    def connect(self, request: Request) -> Response:
        raise HTTP405MethodNotAllowed

    def unknown_method_handler(self, request: Request) -> Response:
        raise HTTP405MethodNotAllowed(
            body=f'Unknown method: {request.method.value}'
        )


class StaticHandler(BaseHTTPHandler):
    def __init__(self, document_root: Path):
        self._document_root = document_root.absolute()

    def get(self, request: Request) -> Response:
        path = (self._document_root / request.uri.lstrip('/')).absolute()
        if not self._is_in_root(path):
            raise HTTP403Forbidden
        if not path.exists():
            raise HTTP404NotFound
        if path.is_dir():
            return self._file_response(path / 'index.html')
        elif path.is_file():
            return self._file_response(path)
        else:
            raise HTTP404NotFound

    def _file_response(self, path: Path):
        if path.is_file():
            with open(path, 'rb') as f:
                body = f.read()
            content_type = mimetypes.guess_type(path)[0] or 'text/html'
            return HTTP200OKResponse(
                body=body,
                headers={
                    'Content-type': content_type
                }
            )
        else:
            raise HTTP404NotFound

    def head(self, request: Request) -> Response:
        return HTTP200OKResponse()

    def _is_in_root(self, path: Path):
        result = True
        try:
            path.relative_to(self._document_root)
        except ValueError:
            result = False
        return result
