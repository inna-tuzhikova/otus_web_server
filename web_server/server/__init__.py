import logging
from pathlib import Path

from server.http_server import HTTPServer
from server.logger import init_logging

init_logging()
logger = logging.getLogger(__name__)


def run_server(
    host: str,
    port: int,
    workers: int,
    document_root: Path
):
    """Runs HTTP server on given host and port

    Args:
        host (str): host to run server
        port (int): port to run server
        workers (int): number of threads to process requests
        document_root (Path): root path to serve static files
    """
    server = HTTPServer(host, port, workers, document_root)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info('Gracefully shutdown')
        server.shutdown()
