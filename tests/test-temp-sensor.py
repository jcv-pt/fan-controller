import os
import sys
import inspect
import time

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)

sys.path.insert(0, parentdir + '/fan-controller')

from config.config import Config
from log.logger import Logger
from engine.temperature.temperature import Temperature

config = Config(parentdir + '/data/config/default.ini')
logger = Logger(parentdir + '/data/logs/', 'Debug', verbose=True, debug=True)

temperature = Temperature(config,logger)

logger.info('Test', message='Temp sensor test activated [press ctrl+c to end the test]...')

try:
    while True:
        temp = temperature.read()
        logger.info('Test', message='Temp measured: {0}'.format(temp))
        time.sleep(5)
except KeyboardInterrupt:
    exit(0)