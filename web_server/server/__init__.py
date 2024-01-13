from pathlib import Path

from server.http_server import HTTPServer


def run_server(
    host: str,
    port: int,
    workers: int,
    document_root: Path
):
    server = HTTPServer(host, port, workers, document_root)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Gracefully shutdown')
        server.shutdown()
