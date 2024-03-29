import logging
import socket
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from server.handler import BaseHTTPHandler, StaticHandler
from server.logger import init_logging
from server.protocol import (
    HTTP500InternalServerError,
    HTTPError,
    HTTProtocol,
    Request,
    Response,
)

init_logging()
logger = logging.getLogger(__name__)


class HTTPServer:
    """Multithreading HTTP socket server"""

    def __init__(
        self,
        host: str,
        port: int,
        workers: int,
        document_root: Path
    ):
        self._host = host
        self._port = port
        self._workers = workers
        self._document_root = document_root
        self._server_sock: socket.socket | None = None
        self._thread_pool: ThreadPoolExecutor | None = None
        self._static_handler: BaseHTTPHandler | None = None

    def serve_forever(self) -> None:
        """Runs server and serves client connections"""
        if self._server_sock is None:
            self._check_document_root()
            self._server_sock = self._create_server_socket()
            self._thread_pool = ThreadPoolExecutor(max_workers=self._workers)
            self._static_handler = StaticHandler(self._document_root)

            logger.info(
                'Server %s:%s is ready to accept client connections',
                self._host, self._port
            )
            while True:
                client_sock = self._accept_client_connection()
                self._thread_pool.submit(self._serve_client, client_sock)
        else:
            raise RuntimeError('Server is already running')

    def shutdown(self) -> None:
        """Closes server socket and waits for running requests to be resolved"""
        self._server_sock.close()
        try:
            self._thread_pool.shutdown()
        except KeyboardInterrupt:
            logger.info('Immediate shutdown')
            self._thread_pool.shutdown(wait=False)

    def _check_document_root(self) -> None:
        if self._document_root.is_file() or not self._document_root.is_dir():
            raise NotADirectoryError(
                f'Document root {self._document_root} is not an existing dir. '
                f'Cannot start server'
            )

    def _create_server_socket(self) -> socket.socket:
        result = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=0
        )
        result.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        result.bind((self._host, self._port))
        result.listen()
        return result

    def _accept_client_connection(self) -> socket.socket:
        client_sock, _ = self._server_sock.accept()
        return client_sock

    def _serve_client(self, client_sock: socket.socket) -> None:
        try:
            reader = client_sock.makefile('rb')
            request = HTTProtocol.get_request(reader)
            response = self._handle_request(request)
            logger.info('Request: %s.\nResponse: %s', request, response)
            self._send_response(response, client_sock)
        except ConnectionResetError:
            client_sock = None
        except Exception as e:
            self._send_error(e, client_sock)
        if client_sock:
            client_sock.close()

    def _handle_request(self, request: Request) -> Response:
        handler = self._get_handler(request)
        response = handler(request)
        return response

    def _get_handler(self, request: Request) -> BaseHTTPHandler:
        return self._static_handler

    def _send_response(
        self,
        response: Response,
        client_sock: socket.socket
    ) -> None:
        writer = client_sock.makefile('wb')
        HTTProtocol.send_response(response, writer)

    def _send_error(self, err: Exception, client_sock: socket.socket) -> None:
        if isinstance(err, HTTPError):
            response = Response(
                status=err.status,
                reason=err.reason,
                body=err.body
            )
        else:
            err_500 = HTTP500InternalServerError(body=str(err))
            response = Response(
                status=err_500.status,
                reason=err_500.reason,
                body=err_500.body
            )
        self._send_response(response, client_sock)
