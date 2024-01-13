from argparse import ArgumentParser
from pathlib import Path

from web_server.server import run_server


def main():
    parser = ArgumentParser('Runs python web server')
    parser.add_argument('host', type=str, help='Host to run server')
    parser.add_argument('port', type=int, help='Port to run server')
    parser.add_argument('--workers', '-w', type=int, default=5,
                        help='Number of workers to process requests')
    parser.add_argument('--root', '-r', type=Path,
                        default=Path('/www/data'),
                        help='Path to root for static files')
    args = parser.parse_args()

    run_server(
        host=args.host,
        port=args.port,
        workers=args.workers,
        document_root=args.root
    )


if __name__ == '__main__':
    main()
