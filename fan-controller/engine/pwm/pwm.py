from rpi_hardware_pwm import HardwarePWM

from config.config import Config
from log.logger import Logger

class PWM:
    __config = None
    __logger = None
    __pwm = None

    def __init__(self, config: Config, logger: Logger):
        self.__config = config
        self.__logger = logger

        self.__pwmChannel = int(self.__config.get('PWM', 'Channel'))
        self.__pwmChipNo = int(self.__config.get('PWM', 'ChipNo'))
        self.__pwmFrequency = int(self.__config.get('PWM', 'Frequency'))

        self.__pwm = HardwarePWM(pwm_channel=self.__pwmChannel, hz=60, chip=self.__pwmChipNo)
        self.setFrequency(self.__pwmFrequency)
        self.__pwm.start(100) # full duty cycle

    def setDutyCycle(self, dutyCycle: int):
        self.__pwm.change_duty_cycle(dutyCycle)
        self.__logger.info('PWM', message='Setting duty cycle to {0}'.format(dutyCycle))

    def setFrequency(self, frequency: float):
        self.__pwm.change_frequency(frequency)
        self.__logger.info('PWM', message='Setting frequency to {0}'.format(frequency))