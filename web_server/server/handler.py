import datetime
import mimetypes
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from server.protocol import (
    HTTP200OKResponse,
    HTTP403Forbidden,
    HTTP404NotFound,
    HTTP405MethodNotAllowed,
    HTTP500InternalServerError,
    HTTPError,
    HTTPMethod,
    Request,
    Response,
)


class BaseHTTPHandler:
    def __call__(self, request: Request) -> Response:
        parsed_uri = urlparse(request.uri)
        query = parse_qs(parsed_uri.query)
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
            response = handler(request, unquote(parsed_uri.path), query)
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

    def options(
        self,
        request: Request,
        uri: str,
        query: dict[str, list]
    ) -> Response:
        raise HTTP405MethodNotAllowed

    def get(
        self,
        request: Request,
        uri: str,
        query: dict[str, list]
    ) -> Response:
        raise HTTP405MethodNotAllowed

    def head(
        self,
        request: Request,
        uri: str,
        query: dict[str, list]
    ) -> Response:
        raise HTTP405MethodNotAllowed

    def post(
        self,
        request: Request,
        uri: str,
        query: dict[str, list]
    ) -> Response:
        raise HTTP405MethodNotAllowed

    def put(
        self,
        request: Request,
        uri: str,
        query: dict[str, list]
    ) -> Response:
        raise HTTP405MethodNotAllowed

    def patch(
        self,
        request: Request,
        uri: str,
        query: dict[str, list]
    ) -> Response:
        raise HTTP405MethodNotAllowed

    def delete(
        self,
        request: Request,
        uri: str,
        query: dict[str, list]
    ) -> Response:
        raise HTTP405MethodNotAllowed

    def trace(
        self,
        request: Request,
        uri: str,
        query: dict[str, list]
    ) -> Response:
        raise HTTP405MethodNotAllowed

    def connect(
        self,
        request: Request,
        uri: str,
        query: dict[str, list]
    ) -> Response:
        raise HTTP405MethodNotAllowed

    def unknown_method_handler(
        self,
        request: Request,
        uri: str,
        query: dict[str, list]
    ) -> Response:
        raise HTTP405MethodNotAllowed(
            body=f'Unknown method: {request.method.value}'
        )


class StaticHandler(BaseHTTPHandler):
    def __init__(self, document_root: Path):
        self._document_root = document_root.resolve()

    def get(
        self,
        request: Request,
        uri: str,
        query: dict[str, list]
    ) -> Response:
        return self._get_file_response(uri, need_body=True)

    def head(
        self,
        request: Request,
        uri: str,
        query: dict[str, list]
    ) -> Response:
        return self._get_file_response(uri, need_body=False)

    def _get_file_response(self, uri: str, need_body: bool) -> Response:
        end_slash = uri.endswith('/')
        path = (self._document_root / uri.lstrip('/')).resolve()
        if not self._is_in_root(path):
            raise HTTP403Forbidden
        if not path.exists():
            raise HTTP404NotFound
        if path.is_dir():
            return self._prepare_file_response(path / 'index.html', need_body)
        elif path.is_file():
            if end_slash:
                raise HTTP404NotFound
            return self._prepare_file_response(path, need_body)
        else:
            raise HTTP404NotFound

    def _is_in_root(self, path: Path) -> bool:
        result = True
        try:
            path.relative_to(self._document_root)
        except ValueError:
            result = False
        return result

    def _prepare_file_response(self, path: Path, need_body: bool) -> Response:
        if path.is_file():
            if need_body:
                with open(path, 'rb') as f:
                    body = f.read()
            else:
                body = None
            return HTTP200OKResponse(
                body=body,
                headers=self._get_file_headers(path, body)
            )
        else:
            raise HTTP404NotFound

    def _get_file_headers(
        self,
        path: Path,
        body: bytes | None
    ) -> dict[str, str]:
        content_type = mimetypes.guess_type(path)[0] or 'text/html'
        headers = {
            'Date': datetime.datetime.utcnow().isoformat(),
            'Content-Length': (
                path.stat().st_size
                if body is None
                else len(body)
            ),
            'Content-Type': content_type,
            'Connection': 'close'
        }
        return headers
