import math  # Import math for trigonometric functions and radian conversion

# ============================================================
# ARITHMETIC FUNCTIONS
# ============================================================

# Formula: result = start + arg1 + arg2 + ...
# Returns the sum of a starting value and any number of additional values
def add(start, *args):
    result = start          # Initialize result with the starting value
    for num in args:        # Loop through each additional number provided
        result += num       # Add current number to running total → accumulates sum
    return result           # Return final sum → complete addition

# Formula: result = start - arg1 - arg2 - ...
# Returns start minus any number of values subtracted in order
def sub(start, *args):
    result = start          # Initialize result with the starting value
    for num in args:        # Loop through each additional number provided
        result -= num       # Subtract current number from running total → accumulates subtraction
    return result           # Return final difference → complete subtraction

# Formula: result = start * arg1 * arg2 * ...
# Returns the product of a starting value and any number of additional values
def multi(start, *args):
    result = start          # Initialize result with the starting value
    for num in args:        # Loop through each additional number provided
        result *= num       # Multiply running total by current number → accumulates product
    return result           # Return final product → complete multiplication

# Formula: result = start / arg1 / arg2 / ...
# Returns start divided by any number of values in order
def div(start, *args):
    result = start          # Initialize result with the starting value
    for num in args:        # Loop through each additional number provided
        result /= num       # Divide running total by current number → accumulates division
    return result           # Return final quotient → complete division

# Formula: result = base % var
# Returns the remainder after dividing base by var
def mod(base, var):
    return base % var       # Divide base by var and return the remainder → complete modulo

# ============================================================
# TRIGONOMETRIC FUNCTIONS
# ============================================================

# Formula: cos(angle)
# Returns the cosine of an angle
# Converts degrees to radians first if isDegrees is True
def Cosine(angle, isDegrees = True):
    if isDegrees:                        # If angle is in degrees...
        angle = math.radians(angle)      # Convert degrees to radians — math.cos only accepts radians
    return math.cos(angle)               # Calculate cosine of angle → complete cos(angle)

# Formula: sin(angle)
# Returns the sine of an angle
# Converts degrees to radians first if isDegrees is True
def Sine(angle, isDegrees = True):
    if isDegrees:                        # If angle is in degrees...
        angle = math.radians(angle)      # Convert degrees to radians — math.sin only accepts radians
    return math.sin(angle)               # Calculate sine of angle → complete sin(angle)

# Formula: tan(angle)
# Returns the tangent of an angle
# Converts degrees to radians first if isDegrees is True
def Tangent(angle, isDegrees = True):
    if isDegrees:                        # If angle is in degrees...
        angle = math.radians(angle)      # Convert degrees to radians — math.tan only accepts radians
    return math.tan(angle)               # Calculate tangent of angle → complete tan(angle)