from math import sqrt
from config.config import Config
from log.logger import Logger

class Rotation:

    def __init__(self, config: Config, logger: Logger):
        self.__config = config
        self.__logger = logger

    def calculate(self, currentTemperature: float):
        """
        Calculates the rotation based on temperature.

        Parameters:
        - currentTemperature (float): Temperature in degrees Celsius.

        Returns:
        - int : Returns in percentage the rpm to apply;
        """

        minTemp = float(self.__config.get('Temperature', 'MinTemp'))
        maxTemp = float(self.__config.get('Temperature', 'MaxTemp'))

        minRotationPercent = float(self.__config.get('Fan', 'MinRotationPercent'))
        maxRotationPercent = float(self.__config.get('Fan', 'MaxRotationPercent'))

        controlPointTemp = float(self.__config.get('Temperature', 'ControlPointTemp'))
        controlPointRotationPercent = float(self.__config.get('Fan', 'ControlPointRotationPercent'))

        minRpmTemp = (minRotationPercent, minTemp)
        cntRpmTemp = (controlPointRotationPercent, controlPointTemp)
        maxRpmTemp = (maxRotationPercent, maxTemp)

        normTemp = self.__tempToNorm(currentTemperature, minTemp, controlPointTemp, maxTemp)

        if normTemp == None:
            return [None,None]

        output = self.__quadratic_bezier(normTemp, minRpmTemp, cntRpmTemp, maxRpmTemp)

        self.__logger.debug('Rotation', message='Calculation: minTemp,maxTemp[{0},{1}], minRot,maxRot[{2},{3}], maxTemp-minTemp[{4}], curTemp[{5}], normTemp[{6}] output[{7},{8}]'.format(minTemp, maxTemp, minRotationPercent, maxRotationPercent, maxTemp - minTemp, currentTemperature, normTemp, output[0],output[1]))

        return output

    def __quadratic_bezier(self, normTemp, minRpmTemp, cntRpmTemp, maxRpmTemp):
        """
        Calculate a point on a quadratic Bézier curve at a specific parameter t.

        Parameters:
        - normTemp (float): Normalized temperature param between 0 and 1;
        - minRpmTemp, cntRpmTemp, maxRpmTemp (tuple): Control points, each defined as (x, y).

        Returns:
        - (float, float): The (x,y)(rotationPercent, temperature) coordinates of the point on the curve at parameter t.
        """
        x = (1 - normTemp) ** 2 * minRpmTemp[0] + 2 * (1 - normTemp) * normTemp * cntRpmTemp[0] + normTemp ** 2 * maxRpmTemp[0]
        y = (1 - normTemp) ** 2 * minRpmTemp[1] + 2 * (1 - normTemp) * normTemp * cntRpmTemp[1] + normTemp ** 2 * maxRpmTemp[1]

        return x, y

    def __tempToNorm(self, temp, minTemp, cntTemp, maxTemp):
        # Coefficients for the quadratic equation
        a = maxTemp - 2 * cntTemp + minTemp
        b = 2 * (cntTemp - minTemp)
        c = minTemp - temp

        # Calculate the discriminant
        discriminant = b ** 2 - 4 * a * c

        # Check if there are real solutions
        if discriminant < 0:
            return None

        # Calculate the two possible values for t
        sqrt_discriminant = sqrt(discriminant)
        t1 = (-b + sqrt_discriminant) / (2 * a)
        t2 = (-b - sqrt_discriminant) / (2 * a)

        # Filter and return only positive t values within the range [0, 1]
        if 0 <= t1 <= 1:
            return t1
        elif 0 <= t2 <= 1:
            return t2
        else:
            return None