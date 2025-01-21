from time import time

class Fault:

    def __init__(self, type: str):
        self.__type = type
        self.__timeStamp = int(time())
        self.__isNotified = False
        self.__isReported = False

    def getAge(self):
        return int(time()) - self.__timeStamp

    def isNotified(self):
        return self.__isNotified

    def setNotified(self):
        self.__isNotified = True

    def isReported(self):
        return self.__isReported

    def setReported(self):
        self.__isReported = True