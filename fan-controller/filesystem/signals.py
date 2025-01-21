import signal

class Signals:
    __isRunning = True

    def __init__(self):
        signal.signal(signal.SIGINT, self.requestShutdown)
        signal.signal(signal.SIGTERM, self.requestShutdown)

    def requestShutdown(self, *args):
        self.__isRunning = False

    def isRunning(self):
        return self.__isRunning