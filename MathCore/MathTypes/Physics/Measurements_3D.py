from MathTypes.Basic import BasicMath  # Import BasicMath for Cosine and Sine functions
from Config import Checks, RNG         # Import Checks and RNG from Config
import math                            # Import math for sqrt
from MathTypes.Physics import Physics_1D  # Import Physics_1D for 1D physics fallback calculations

def Density(mass, volume):
    return mass / volume

def Mass(density = 0, volume = 0, weight = 0, gravity = 0, force = 0, acceleration = 0):
    mass = 0
    if density > 0 or volume > 0:
        mass = density * volume
    elif weight > 0 or gravity > 0:
        mass = weight / gravity
    elif force > 0 or acceleration > 0:
        mass = force / acceleration
    return mass


def Weight(mass, gravity, density = 0, volume = 0, force = 0, acceleration = 0):
    if mass <= 0:
        Mass(density, volume, force, acceleration)
    return mass * gravity