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

        self.__internalClock = 0
        self.__thread = threading.Thread(target=self.__run)

    def start(self):
        if self.__isRunning == False:
            self.__isRunning = True
            self.__thread.start()

    def getAvgPulses(self):
        return int(self.__pulseStack.getAverage())

    def getRepeatedPulses(self):
        if not self.__pulseStack.isFull():
            return 0
        return self.__pulseStack.getRepeated()

    def stop(self):
        self.__isRunning = False

    def shutdown(self):
        self.stop()
        time.sleep(3)  # Wait for two secs
        GPIO.cleanup(self.__devicePin)

    def __run(self):
        try:
            while self.__isRunning:
                # GPIO method add_event_detect() is a CPU intensive task, and since we are interested in measure fan idle in a timely manner
                # we dont need to continuously count RPM. Measure RPM in a 5 min interval is acceptable.
                if self.__internalClock <= 15:
                    self.__internalClock += 1
                    time.sleep(1)
                    continue
                # Enable pin reading
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.__devicePin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.add_event_detect(self.__devicePin, GPIO.FALLING, callback=self.__countPulse)
                # Read pulses
                self.__measurePulses()
                # Remove event from pin since its a CPU intensive task
                GPIO.cleanup(self.__devicePin)
                # Reset clock and sleep until next iteration
                self.__internalClock = 0
        except Exception as e:
            self.__logger.error('Tachometer', message='Error while reading FAN pulses: {0}'.format(repr(e)))

    def __measurePulses(self):
        self.__pulsesCounter = 0  # Reset pulse count
        time.sleep(1)  # Wait for one sec
        self.__pulseStack.push(self.__pulsesCounter)

    def __countPulse(self,channel):
        self.__pulsesCounter += 1