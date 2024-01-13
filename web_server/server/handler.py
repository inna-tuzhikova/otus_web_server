from pathlib import Path

from web_server.server.protocol import (
    Response,
    HTTP405MethodNotAllowed,
    HTTP500InternalServerError,
    Request,
    Method, HTTPError
)


class BaseHTTPHandler:
    def __call__(self, request: Request) -> Response:
        if request.method == Method.OPTIONS:
            handler = self.options
        elif request.method == Method.GET:
            handler = self.get
        elif request.method == Method.HEAD:
            handler = self.head
        elif request.method == Method.POST:
            handler = self.post
        elif request.method == Method.PUT:
            handler = self.put
        elif request.method == Method.PATCH:
            handler = self.patch
        elif request.method == Method.DELETE:
            handler = self.delete
        elif request.method == Method.TRACE:
            handler = self.trace
        elif request.method == Method.CONNECT:
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
        self._document_root = document_root

    def get(self, request: Request) -> Response:
        pass

    def head(self, request: Request) -> Response:
        pass
