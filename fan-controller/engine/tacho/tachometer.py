import RPi.GPIO as GPIO
import time
import threading

from config.config import Config
from log.logger import Logger
from .stack import Stack

class Tachometer:
    __config = None
    __logger = None
    __devicePin = None
    __pulsesPerRev = 1
    __pulsesCounter = 0
    __pulsesMin = 0
    __isRunning = False

    def __init__(self, config: Config, logger: Logger):

        self.__config = config
        self.__logger = logger

        self.__devicePin = int(self.__config.get('Fan', 'TachoGPIOPin'))
        self.__pulsesPerRev = int(self.__config.get('Fan', 'TachoPulsesPerRev'))
        self.__pulseStack = Stack(15)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.__devicePin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(self.__devicePin, GPIO.FALLING, callback=self.__countPulse)

        self.__thread = threading.Thread(target=self.__run)

    def start(self):
        if self.__isRunning == False:
            self.__isRunning = True
            self.__thread.start()

    def getAvgPulses(self):
        return int(self.__pulseStack.getAverage())

    def getRepeatedPulses(self):
        return self.__pulseStack.getRepeated()

    def stop(self):
        self.__isRunning = False

    def shutdown(self):
        self.stop()
        time.sleep(2)  # Wait for two secs
        GPIO.cleanup()

    def __run(self):
        try:
            while self.__isRunning:
                self.__measurePulses()
        except Exception as e:
            self.__logger.error('Tachometer', message='Error while reading FAN pulses: {0}'.format(repr(e)))

    def __measurePulses(self):
        self.__pulsesCounter = 0  # Reset pulse count
        time.sleep(1)  # Wait for one sec
        self.__pulseStack.push(self.__pulsesCounter)

    def __countPulse(self,channel):
        self.__pulsesCounter += 1