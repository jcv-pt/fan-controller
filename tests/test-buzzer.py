import os
import sys
import inspect
import time

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)

sys.path.insert(0, parentdir + '/fan-controller')

from config.config import Config
from log.logger import Logger
from engine.buzzer.buzzer import Buzzer

config = Config(parentdir + '/data/config/default.ini')
logger = Logger(parentdir + '/data/logs/', 'Debug', verbose=True, debug=True)

buzzer = Buzzer(config,logger)

logger.info('Test', message='Buzzer test activated [press ctrl+c to end the test]...')

buzzer.buzzIntermittent()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    buzzer.shutdown()

