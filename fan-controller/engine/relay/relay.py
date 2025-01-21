import RPi.GPIO as GPIO

from config.config import Config
from log.logger import Logger

class Relay:
    __config = None
    __initialState = None
    __onState = None

    def __init__(self, config: Config, logger: Logger):
        self.__config = config
        self.__logger = logger

        self.__devicePin = int(self.__config.get('Relay', 'GPIOPin'))
        self.__initialState = int(self.__config.get('Relay', 'InitialState'))
        self.__onState = int(self.__config.get('Relay', 'OnState'))

        if self.__initialState == 1:
            state = GPIO.HIGH
        else:
            state = GPIO.LOW

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.__devicePin, GPIO.OUT, initial=state)

        self.__logger.info('Relay', message='Initializing Relay: GPIOPin [{0}], InitialState [{1}], OnState [{2}]'.format(self.__devicePin, self.__initialState, self.__onState))

    def on(self):
        GPIO.output(self.__devicePin, GPIO.HIGH if self.__onState == 1 else GPIO.LOW)
        self.__logger.info('Relay', message='Setting state to ON')

    def off(self):
        GPIO.output(self.__devicePin, GPIO.LOW if self.__onState == 1 else GPIO.HIGH)
        self.__logger.info('Relay', message='Setting state to OFF')