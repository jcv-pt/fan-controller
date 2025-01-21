from time import sleep, time
from config.config import Config
from log.logger import Logger
from .failure.failure import Failures
from .buzzer.buzzer import Buzzer
from .rotation.rotation import Rotation
from .tacho.tachometer import Tachometer
from .temperature.temperature import Temperature
from .relay.relay import Relay
from .pwm.pwm import PWM

import os
import threading
import traceback

class Engine:
    __config = None
    __logger = None
    __thread = None
    __rotation = None
    __temperature = None
    __buzzer = None
    __relay = None
    __pwm = None
    __tachometer = None
    __running = False
    __currentRotationPercent = -1
    __fanShutdownGraceTime = 0
    __fanShutdownTimeStamp = None
    __fanShutdownIsStopped = False
    __failureManifest = {}

    def __init__(self, config: Config, logger: Logger):
        self.__config = config
        self.__logger = logger

        # Initialize configs
        self.__minTemp = int(self.__config.get('Temperature', 'MinTemp'))
        self.__minRotationPercent = int(self.__config.get('Fan', 'MinRotationPercent'))
        self.__maxRotationPercent = int(self.__config.get('Fan', 'MaxRotationPercent'))
        self.__fanShutdownGraceTime = int(self.__config.get('Fan', 'ShutdownGraceTime'))

        # Initialize class modules
        self.__failures = Failures()
        self.__buzzer = Buzzer(self.__config,self.__logger)
        self.__temperature = Temperature(self.__config, self.__logger)
        self.__relay = Relay(self.__config, self.__logger)
        self.__pwm = PWM(self.__config, self.__logger)
        self.__rotation = Rotation(self.__config, self.__logger)
        self.__tachometer = Tachometer(self.__config, self.__logger)

    def start(self):
        self.__running = True
        # Start the tachometer
        self.__tachometer.start()
        # Signal with buzzer
        self.__buzzer.buzzOnce()
        # Start the run thread
        self.__thread = threading.Thread(target=self.__run)
        self.__thread.start()

    def stop(self):
        self.__logger.info('Engine', message='Stop signal received, terminating engine thread...')
        self.__running = False
        # Shutdown libs
        self.__buzzer.shutdown()
        self.__tachometer.shutdown()

    def isRunning(self):
        return self.__running

    def __run(self):
        while self.__running:
            curTime = int(time())

            # Process iteration every 5 secs
            if curTime % 5 == 0:
                try:
                    self.__iterate()
                except Exception as ex:
                    self.__logger.error('Engine',message='CRASH, entering crash mode, engine iteration reported a failure: {0}'.format(repr(ex)))
                    self.__logger.error('Engine',message='- Stack: {0}'.format(traceback.format_exc()))
                    self.__crash()

            sleep(1)

    def __iterate(self):
        sensorTemp = self.__temperature.read()

        # Check for good temperature reading, otherwise report a failure
        faultId = 'temp_reading'
        if sensorTemp is None:
            # Report
            if self.__failures.exists(faultId) == False:
                self.__logger.warning('Engine',message='Temperature reading value is not valid...')
                self.__failures.report(faultId)
            # Create a new fault
            fault = self.__failures.getFault(faultId)
            if fault.getAge() > 60 and fault.isReported() == False:
                self.__logger.error('Engine', message='Temperature could not be read for > 60 secs, entering PANIC mode.')
                self.__panic()
                fault.setReported()
        elif self.__failures.exists(faultId):
            # Get fault
            fault = self.__failures.getFault(faultId)
            if fault.isReported() == True:
                self.__reset()
            self.__failures.clear(faultId)

        outputRotation,outputTemperature = [None,None] if sensorTemp is None else self.__rotation.calculate(sensorTemp)

        # Check rotation was properly calculated, otherwise report a failure
        faultId = 'rotation_calculation'
        if outputRotation is None and (sensorTemp is not None and sensorTemp >= self.__minTemp):
            # Report
            if self.__failures.exists(faultId) == False:
                self.__logger.warning('Engine', message='Rotation calculated value is not valid...')
                self.__failures.report(faultId)
            # Create a new fault
            fault = self.__failures.getFault(faultId)
            if fault.getAge() > 60 and fault.isReported() == False:
                self.__logger.error('Engine', message='Rotation could not be calculated for > 60 secs, entering PANIC mode.')
                self.__panic()
                fault.setReported()
        elif self.__failures.exists(faultId):
            # Get fault
            fault = self.__failures.getFault(faultId)
            if fault.isReported() == True:
                self.__reset()
            self.__failures.clear(faultId)

        # Check good value reading from tachometer, otherwise report failure
        tachAvgPulses = self.__tachometer.getAvgPulses()
        tachRepPulses = self.__tachometer.getRepeatedPulses()
        faultId = 'rotation_tachometer'
        if self.__fanShutdownIsStopped is False and tachRepPulses > 0:
            # Report
            if self.__failures.exists(faultId) == False:
                self.__failures.report(faultId)
            # Get fault
            fault = self.__failures.getFault(faultId)
            # Notify if more than 2 mins
            if fault.getAge() > 120 and fault.isNotified() == False:
                self.__logger.warning('Engine',message='Tachometer is reporting a possible fault with fan RPM...')
                fault.setNotified()
            if fault.getAge() > 300 and fault.isReported() == False:
                self.__logger.error('Engine',message='Tachometer has reported a possible fan fault for over 5 mins, entering PANIC mode.')
                self.__panic()
                fault.setReported()
        elif self.__failures.exists(faultId):
            # Get fault
            fault = self.__failures.getFault(faultId)
            if fault.isReported() == True:
                self.__reset()
            self.__failures.clear(faultId)

        # Apply rotation bounds
        if outputRotation is not None:
            outputRotation = int(outputRotation)
            if outputRotation < self.__minRotationPercent:
                outputRotation = self.__minRotationPercent
            if outputRotation > self.__maxRotationPercent:
                outputRotation = self.__maxRotationPercent

        # Check for fan shutdown conditions
        if sensorTemp is not None and sensorTemp < self.__minTemp:
            # Assign shutdown start of grace period
            if self.__fanShutdownTimeStamp is None:
                self.__fanShutdownTimeStamp = int(time())
                self.__logger.info('Engine', message='Fan shutdown conditions meet, starting grace period of {0} mins'.format(self.__fanShutdownGraceTime))
            # Check if we can shut down the fans
            if (int(time()) - self.__fanShutdownTimeStamp) / 60 >= self.__fanShutdownGraceTime and self.__fanShutdownIsStopped is False:
                self.__fanShutdownIsStopped = True
                self.__relay.off()
                self.__logger.info('Engine', message='Fan shutdown grace period reached, stopping fans')
        else:
            # Check if the fans are shutdown, if so start them up
            if self.__fanShutdownIsStopped is True:
                self.__fanShutdownIsStopped = False
                self.__relay.on()
                self.__logger.info('Engine', message='Fan min temperature reached, re-starting fans')

        # Set duty cycle if fans are running
        if self.__fanShutdownIsStopped is False and outputRotation is not None and self.__currentRotationPercent != outputRotation:
            self.__currentRotationPercent = outputRotation
            self.__pwm.setDutyCycle(self.__currentRotationPercent)

        self.__logger.info('Engine', message='Iteration measured: Temp [{0}C], RPM [{1}%], Tach [{2},{3}], Fan Status [{4}]'.format(sensorTemp, self.__currentRotationPercent, tachAvgPulses, tachRepPulses, 'ON' if self.__fanShutdownIsStopped is False else 'OFF'))

    def __panic(self):
        self.__logger.info('Engine', message='Panic mode requested, setting Relay [ON], Duty Cycle[MAX], Buzzer:[Intermittent]')
        self.__relay.on()
        self.__pwm.setDutyCycle(self.__maxRotationPercent)
        self.__buzzer.buzzIntermittent()

    def __reset(self):
        self.__logger.info('Engine', message='Reset requested, engine values restored to default')
        self.__fanShutdownIsStopped = False
        self.__fanShutdownTimeStamp = None
        self.__currentRotationPercent = -1
        self.__relay.on()
        self.__buzzer.stop()
        self.__buzzer.buzzOnce()

    def __crash(self):
        self.__relay.on()
        self.__pwm.setDutyCycle(self.__maxRotationPercent)
        self.stop()
        os._exit(1)
