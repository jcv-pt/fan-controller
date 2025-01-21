import os
import glob
import time
import sys

from config.config import Config
from log.logger import Logger

class Temperature:
    __config = None
    __logger = None
    __device = None

    def __init__(self, config: Config, logger: Logger):
        self.__config = config
        self.__logger = logger

        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        devicePath = self.__config.get('Temperature', 'DevicePath') + self.__config.get('Temperature', 'DeviceFolder')
        deviceFolder = glob.glob(devicePath)

        if not deviceFolder:
            self.__logger.error('Temperature',message='Cannot open temperature device folder: {0}'.format(devicePath))
            return

        self.__device = deviceFolder[0] + self.__config.get('Temperature', 'DeviceFile')

    def read(self, scale = 'c'):
        if self.__device is None:
            return None

        try:
            lines = self.__readTempRaw()
            while lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines = self.__readTempRaw()

            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos + 2:]
                temp_c = float(temp_string) / 1000.0

                if scale == 'c':
                    return temp_c
                if scale == 'f':
                    return temp_c * 9.0 / 5.0 + 32.0
        except IOError as e:
            self.__logger.error('Temperature', message='Cannot read temp, I/O error({0}): {1}'.format(e.errno, e.strerror))
        except:  # handle other exceptions such as attribute errors
            self.__logger.error('Temperature',message='Cannot read temp, unknown error: {0}'.format(sys.exc_info()[0]))

        return None

    def __readTempRaw(self):
        f = open(self.__device, 'r')
        lines = f.readlines()
        f.close()
        return lines
