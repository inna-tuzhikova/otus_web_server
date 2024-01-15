import logging


def init_logging() -> None:
    """Sets basic logging settings"""
    logging.basicConfig(
        filename=None,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S',
        level=logging.INFO
    )
