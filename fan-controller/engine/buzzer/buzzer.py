import RPi.GPIO as GPIO
import time
import threading

from config.config import Config
from log.logger import Logger

class Buzzer:
    __config = None
    __logger = None
    __devicePin = None
    __pinHighTime = 1
    __intermittentPinLowTime = 4
    __isActive = False
    __type = 'once'

    def __init__(self, config: Config, logger: Logger):
        self.__config = config
        self.__logger = logger

        self.__devicePin = int(self.__config.get('Buzzer', 'GPIOPin'))
        self.__pinHighTime = int(self.__config.get('Buzzer', 'PINHighTime'))
        self.__pinHighShortTime = float(self.__config.get('Buzzer', 'PINHighShortTime'))
        self.__intermittentPinLowTime = int(self.__config.get('Buzzer', 'IntermittentPINLowTime'))

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.__devicePin, GPIO.OUT, initial=GPIO.LOW)

    def buzzOnce(self, length = 'normal'):
        if length == 'normal':
            self.__type = 'once_normal'
        else:
            self.__type = 'once_short'
        self.__run()

    def buzzIntermittent(self):
        self.__type = 'intermittent'
        if self.__isActive == False:
            self.__thread = threading.Thread(target=self.__run)
            self.__thread.start()

    def stop(self):
        self.__isActive = False

    def shutdown(self):
        self.stop()
        GPIO.cleanup()

    def __run(self):
        if (self.__type == 'intermittent'):
            self.__isActive = True
            try:
                while self.__isActive:
                    GPIO.output(self.__devicePin, GPIO.HIGH)  # Buzzer will be switched on
                    time.sleep(self.__pinHighTime)  # Waitmode for y seconds
                    GPIO.output(self.__devicePin, GPIO.LOW)  # Buzzer will be switched off
                    time.sleep(self.__intermittentPinLowTime)  # Waitmode for x seconds
            except Exception as e:
                self.__logger.error('Buzzer',message='Error while setting GPIO pins: {0}'.format(repr(e)))

        if (self.__type == 'once_normal' or self.__type == 'once_short'):
            highTime = self.__pinHighTime if self.__type == 'once_normal' else self.__pinHighShortTime
            GPIO.output(self.__devicePin, GPIO.HIGH)  # Buzzer will be switched on
            time.sleep(highTime)  # Waitmode for x seconds
            GPIO.output(self.__devicePin, GPIO.LOW)  # Buzzer will be switched off