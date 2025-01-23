import os
import sys
import inspect
import time

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)

sys.path.insert(0, parentdir + '/fan-controller')

from config.config import Config
from log.logger import Logger
from engine.pwm.pwm import PWM

config = Config(parentdir + '/data/config/default.ini')
logger = Logger(parentdir + '/data/logs/', 'Debug', verbose=True, debug=True)

pwm = PWM(config,logger)

logger.info('Test', message='PWM test activated [press ctrl+c to end the test]...')

maxRotation = int(config.get('Fan', 'MaxRotationPercent'))
minRotation = int(config.get('Fan', 'MinRotationPercent'))

try:
    while True:
        logger.info('Test', message='Setting PWM to max rotation...')
        pwm.setDutyCycle(maxRotation)
        time.sleep(10)
        logger.info('Test', message='Setting PWM to min rotation...')
        pwm.setDutyCycle(minRotation)
        time.sleep(10)
except KeyboardInterrupt:
    exit(0)