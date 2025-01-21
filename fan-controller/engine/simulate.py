import os
import sys
import inspect
import numpy as np
import matplotlib.pyplot as plt

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(os.path.dirname(currentdir))

sys.path.insert(0, parentdir + '/fan-controller')

from engine.rotation.rotation import Rotation
from config.config import Config
from log.logger import Logger

config = Config(parentdir + '/data/config/default.ini')
logger = Logger(parentdir + '/data/logs/', 'Simulate')
rotation = Rotation(config, logger)

# Set min max temp and rotation
minTemp = float(config.get('Temperature', 'MinTemp'))
maxTemp = float(config.get('Temperature', 'MaxTemp'))

minRotationPercent = float(config.get('Fan', 'MinRotationPercent'))
maxRotationPercent = float(config.get('Fan', 'MaxRotationPercent'))

controlPointTemp = float(config.get('Temperature', 'ControlPointTemp'))
controlPointRotationPercent = float(config.get('Fan', 'ControlPointRotationPercent'))

# Plotting calculated curve
num_points = 100
t_values = np.linspace(minTemp, maxTemp, num_points)
x_values = []
y_values = []
for t in t_values:
    x, y = rotation.calculate(t)
    x_values.append(x)
    y_values.append(y)
plt.plot(x_values, y_values, color='green', label='Calculated Curve')

# Plotting Min and Max Temperature lines
x1, y1 = [0, 175], [minTemp, minTemp]
plt.plot(x1, y1, color='blue', label='Min Temp [{0}º]'.format(minTemp))

x1, y1 = [0, 175], [maxTemp, maxTemp]
plt.plot(x1, y1, color='red', label='Max Temp [{0}º]'.format(maxTemp))

# Plotting Min and Max Rotation lines
x1, y1 = [minRotationPercent, minRotationPercent], [-5, 40]
plt.plot(x1, y1, color='cyan', label='Min RPM [{0}%]'.format(minRotationPercent))

x1, y1 = [maxRotationPercent, maxRotationPercent], [-5, 40]
plt.plot(x1, y1, color='yellow', label='Max RPM [{0}%]'.format(maxRotationPercent))

plt.scatter([controlPointTemp], [controlPointRotationPercent], color='orange', label='Control Point TempXRot')

plt.legend()
plt.xlabel('RPM (%)')
plt.ylabel('Temperature (cº)')
plt.title('Fan Controller - Cubic Bezier Curve')
plt.grid(True)
plt.show()