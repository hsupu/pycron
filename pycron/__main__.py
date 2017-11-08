import os
import sys

if not __package__:
    path = os.path.join(os.path.dirname(__file__), os.pardir)
    sys.path.insert(0, path)

import logging
import argparse
import signal
import asyncio
import asyncio.subprocess

from logging.handlers import TimedRotatingFileHandler

from pycron.config import parse_config_files
from pycron.pycron import Pycron


def handle_loop(loop, args):
    global_config, task_configs = parse_config_files(args.config_dir)
    log_config = global_config.pop('log')

    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_config['level']))

    log_file = log_config['file']
    with open(log_file, 'a') as fd:
        fd.close()

    logger_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s : %(message)s')

    log2console_handler = logging.StreamHandler()
    log2console_handler.setFormatter(logger_formatter)
    logger.addHandler(log2console_handler)

    log2file_handler = TimedRotatingFileHandler(log_file, when='d', interval=1, backupCount=7)
    log2file_handler.setFormatter(logger_formatter)
    logger.addHandler(log2file_handler)

    # # logging.getLogger("asyncio").setLevel(logging.WARNING)
    # logger = logging.getLogger("yacron")
    #
    pycron = Pycron(loop, global_config, task_configs)

    loop.add_signal_handler(signal.SIGINT, pycron.stop)
    loop.add_signal_handler(signal.SIGTERM, pycron.stop)
    try:
        loop.run_until_complete(pycron.run())
    finally:
        loop.remove_signal_handler(signal.SIGINT)
        loop.remove_signal_handler(signal.SIGTERM)


def main(args):  # pragma: no cover
    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
    try:
        handle_loop(loop, args)
    finally:
        loop.close()


if __name__ == '__main__':  # pragma: no cover
    parser = argparse.ArgumentParser(description="A cron for python.")
    parser.add_argument('-c', "--config-dir")
    args = parser.parse_args()

    main(args)
