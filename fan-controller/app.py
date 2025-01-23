import os
import argparse
import time

from datetime import datetime
from time import sleep

from log.logger import Logger
from config.config import Config
from utils.utils import Utils
from engine.engine import Engine
from filesystem.signals import Signals

class App:

    def run(self):

        # Initialize app args
        argParser = argparse.ArgumentParser(description='Raspberry PI : Fan Controller - Controls & manages PWM fans')
        argParser.add_argument('--verbose', dest='verbose', type=int, default=1, help='Weather to display logging output')
        argParser.add_argument('--debug', dest='debug', type=int, default=0, help='Weather to print debug data to console')

        args = argParser.parse_args()

        # Initialize app var
        app = {
            'rid': datetime.today().strftime('%Y-%m-%d_%H%M%S'),
            'stime': time.time(),
            'sdate': datetime.today().strftime('%Y-%m-%d'),
            'path': os.path.abspath(os.getcwd()),
            'verbose': bool(args.verbose),
            'debug': bool(args.debug),
        }

        # Initialize logger & config
        config = Config(app['path'] + '/data/config/default.ini')
        logger = Logger(app['path'] + '/data/logs/', app['rid'], verbose=app['verbose'], debug=app['debug'], maxLogLines=int(config.get('Logs', 'MaxLogLines')), maxFilesCount=int(config.get('Logs', 'MaxFilesCount')))

        # Initialize & start engine
        engine = Engine(config, logger)
        engine.start()

        # Initialize OS signals
        osSignals = Signals()
        while osSignals.isRunning():
            sleep(1)

        engine.stop()

        # Report & cleanup
        logger.info(message='Process completed in ' + Utils.secondsToHours(time.time() - app['stime']))
        logger.purge()

        # Exit
        if logger.hasErrors() is True:
            exit(1)

        exit(0)