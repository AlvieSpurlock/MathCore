import math  # Import math for sin, cos, tan, asin, acos, atan, atan2, sqrt, pi, hypot

# ============================================================
# CORE TRIGONOMETRIC FUNCTIONS
# ============================================================

# Formula: sin(θ)
# Returns the sine of an angle in degrees — opposite over hypotenuse in a right triangle
def Sin(degrees):
    return math.sin(math.radians(degrees))                  # Convert to radians then apply sine → complete sin(θ)

# Formula: cos(θ)
# Returns the cosine of an angle in degrees — adjacent over hypotenuse in a right triangle
def Cos(degrees):
    return math.cos(math.radians(degrees))                  # Convert to radians then apply cosine → complete cos(θ)

# Formula: tan(θ)
# Returns the tangent of an angle in degrees — opposite over adjacent in a right triangle
# Returns 0 if cos(θ) is effectively zero to avoid division by zero — tangent is undefined at 90° and 270°
def Tan(degrees):
    if abs(math.cos(math.radians(degrees))) < 1e-9:         # Guard against division by zero — cos(90°) = 0
        return 0                                            # Return 0 safely — tangent undefined at this angle
    return math.tan(math.radians(degrees))                  # Convert to radians then apply tangent → complete tan(θ)

# ============================================================
# RECIPROCAL TRIGONOMETRIC FUNCTIONS
# ============================================================

# Formula: csc(θ) = 1 / sin(θ)
# Returns the cosecant of an angle in degrees — hypotenuse over opposite
# Returns 0 if sin(θ) is effectively zero to avoid division by zero
def Csc(degrees):
    s = math.sin(math.radians(degrees))                     # Calculate sin(θ) first
    if abs(s) < 1e-9:                                       # Guard against division by zero — sin(0°) = 0
        return 0                                            # Return 0 safely — cosecant undefined at this angle
    return 1 / s                                            # Reciprocal of sine → complete csc(θ) = 1/sin(θ)

# Formula: sec(θ) = 1 / cos(θ)
# Returns the secant of an angle in degrees — hypotenuse over adjacent
# Returns 0 if cos(θ) is effectively zero to avoid division by zero
def Sec(degrees):
    c = math.cos(math.radians(degrees))                     # Calculate cos(θ) first
    if abs(c) < 1e-9:                                       # Guard against division by zero — cos(90°) = 0
        return 0                                            # Return 0 safely — secant undefined at this angle
    return 1 / c                                            # Reciprocal of cosine → complete sec(θ) = 1/cos(θ)

# Formula: cot(θ) = 1 / tan(θ) = cos(θ) / sin(θ)
# Returns the cotangent of an angle in degrees — adjacent over opposite
# Returns 0 if sin(θ) is effectively zero to avoid division by zero
def Cot(degrees):
    s = math.sin(math.radians(degrees))                     # Calculate sin(θ) first
    if abs(s) < 1e-9:                                       # Guard against division by zero — sin(0°) = 0
        return 0                                            # Return 0 safely — cotangent undefined at this angle
    return math.cos(math.radians(degrees)) / s              # Divide cosine by sine → complete cot(θ) = cos(θ)/sin(θ)

# ============================================================
# INVERSE TRIGONOMETRIC FUNCTIONS
# ============================================================

# Formula: θ = arcsin(x)
# Returns the angle in degrees whose sine is x
# Input must be in [-1, 1] — returns 0 outside this range
def Asin(x):
    if x < -1 or x > 1:                                    # Guard against domain error — arcsin only defined on [-1, 1]
        return 0                                            # Return 0 safely
    return math.degrees(math.asin(x))                       # Apply inverse sine then convert to degrees → complete θ = arcsin(x)

# Formula: θ = arccos(x)
# Returns the angle in degrees whose cosine is x
# Input must be in [-1, 1] — returns 0 outside this range
def Acos(x):
    if x < -1 or x > 1:                                    # Guard against domain error — arccos only defined on [-1, 1]
        return 0                                            # Return 0 safely
    return math.degrees(math.acos(x))                       # Apply inverse cosine then convert to degrees → complete θ = arccos(x)

# Formula: θ = arctan(x)
# Returns the angle in degrees whose tangent is x
# Output is always in (-90°, 90°)
def Atan(x):
    return math.degrees(math.atan(x))                       # Apply inverse tangent then convert to degrees → complete θ = arctan(x)

# Formula: θ = atan2(y, x)
# Returns the angle in degrees of a vector (x, y) measured from the positive X axis
# Handles all four quadrants correctly — output is in (-180°, 180°]
def Atan2(y, x):
    return math.degrees(math.atan2(y, x))                   # Apply two-argument arctangent then convert to degrees → complete θ = atan2(y, x)

# ============================================================
# PYTHAGOREAN IDENTITIES
# ============================================================

# Formula: sin²(θ) + cos²(θ) = 1
# Verifies the fundamental Pythagorean identity at a given angle in degrees
# Returns True if sin²(θ) + cos²(θ) equals 1 within tolerance — should always be True for valid input
def PythagoreanIdentity(degrees, tolerance = 1e-9):
    return abs(Sin(degrees) ** 2 + Cos(degrees) ** 2 - 1) < tolerance  # Check if sum of squares equals 1 → True always for real angles

# Formula: sin²(θ) = (1 - cos(2θ)) / 2
# Returns sin²(θ) using the half-angle power reduction identity
def SinSquared(degrees):
    return (1 - Cos(2 * degrees)) / 2                       # Apply power reduction for sin² → complete sin²(θ) = (1-cos(2θ))/2

# Formula: cos²(θ) = (1 + cos(2θ)) / 2
# Returns cos²(θ) using the half-angle power reduction identity
def CosSquared(degrees):
    return (1 + Cos(2 * degrees)) / 2                       # Apply power reduction for cos² → complete cos²(θ) = (1+cos(2θ))/2

# Formula: 1 + tan²(θ) = sec²(θ)
# Verifies the tangent-secant Pythagorean identity at a given angle in degrees
# Returns True if 1 + tan²(θ) equals sec²(θ) within tolerance
# Returns False for angles where tan or sec is undefined (e.g. 90°)
def TanSecIdentity(degrees, tolerance = 1e-9):
    if abs(math.cos(math.radians(degrees))) < 1e-9:         # Skip undefined angles where cos(θ) = 0
        return False                                        # Identity cannot be evaluated at this angle
    return abs(1 + Tan(degrees) ** 2 - Sec(degrees) ** 2) < tolerance  # Check 1+tan²=sec² within tolerance

# Formula: 1 + cot²(θ) = csc²(θ)
# Verifies the cotangent-cosecant Pythagorean identity at a given angle in degrees
# Returns False for angles where cot or csc is undefined (e.g. 0°)
def CotCscIdentity(degrees, tolerance = 1e-9):
    if abs(math.sin(math.radians(degrees))) < 1e-9:         # Skip undefined angles where sin(θ) = 0
        return False                                        # Identity cannot be evaluated at this angle
    return abs(1 + Cot(degrees) ** 2 - Csc(degrees) ** 2) < tolerance  # Check 1+cot²=csc² within tolerance

# ============================================================
# ANGLE SUM AND DIFFERENCE IDENTITIES
# ============================================================

# Formula: sin(A + B) = sin(A)cos(B) + cos(A)sin(B)
# Returns sin of the sum of two angles in degrees
def SinSum(A, B):
    return Sin(A) * Cos(B) + Cos(A) * Sin(B)               # Apply angle addition formula → complete sin(A+B)

# Formula: sin(A - B) = sin(A)cos(B) - cos(A)sin(B)
# Returns sin of the difference of two angles in degrees
def SinDiff(A, B):
    return Sin(A) * Cos(B) - Cos(A) * Sin(B)               # Apply angle subtraction formula → complete sin(A-B)

# Formula: cos(A + B) = cos(A)cos(B) - sin(A)sin(B)
# Returns cos of the sum of two angles in degrees
def CosSum(A, B):
    return Cos(A) * Cos(B) - Sin(A) * Sin(B)               # Apply angle addition formula → complete cos(A+B)

# Formula: cos(A - B) = cos(A)cos(B) + sin(A)sin(B)
# Returns cos of the difference of two angles in degrees
def CosDiff(A, B):
    return Cos(A) * Cos(B) + Sin(A) * Sin(B)               # Apply angle subtraction formula → complete cos(A-B)

# Formula: tan(A + B) = (tan(A) + tan(B)) / (1 - tan(A)*tan(B))
# Returns tan of the sum of two angles in degrees
# Returns 0 if the denominator is effectively zero — tangent undefined at this combination
def TanSum(A, B):
    denominator = 1 - Tan(A) * Tan(B)                      # Calculate denominator → 1 - tan(A)*tan(B)
    if abs(denominator) < 1e-9:                             # Guard against division by zero — undefined combination
        return 0                                            # Return 0 safely
    return (Tan(A) + Tan(B)) / denominator                  # Divide summed tangents by denominator → complete tan(A+B)

# Formula: tan(A - B) = (tan(A) - tan(B)) / (1 + tan(A)*tan(B))
# Returns tan of the difference of two angles in degrees
# Returns 0 if the denominator is effectively zero
def TanDiff(A, B):
    denominator = 1 + Tan(A) * Tan(B)                      # Calculate denominator → 1 + tan(A)*tan(B)
    if abs(denominator) < 1e-9:                             # Guard against division by zero
        return 0                                            # Return 0 safely
    return (Tan(A) - Tan(B)) / denominator                  # Divide differenced tangents by denominator → complete tan(A-B)

# ============================================================
# DOUBLE AND HALF ANGLE IDENTITIES
# ============================================================

# Formula: sin(2θ) = 2*sin(θ)*cos(θ)
# Returns sin of double an angle in degrees
def Sin2x(degrees):
    return 2 * Sin(degrees) * Cos(degrees)                  # Multiply 2 by sin and cos → complete sin(2θ) = 2sin(θ)cos(θ)

# Formula: cos(2θ) = cos²(θ) - sin²(θ)
# Returns cos of double an angle in degrees
def Cos2x(degrees):
    return Cos(degrees) ** 2 - Sin(degrees) ** 2            # Subtract sin² from cos² → complete cos(2θ) = cos²(θ)-sin²(θ)

# Formula: tan(2θ) = 2*tan(θ) / (1 - tan²(θ))
# Returns tan of double an angle in degrees
# Returns 0 if denominator is effectively zero
def Tan2x(degrees):
    denominator = 1 - Tan(degrees) ** 2                     # Calculate denominator → 1 - tan²(θ)
    if abs(denominator) < 1e-9:                             # Guard against division by zero
        return 0                                            # Return 0 safely
    return (2 * Tan(degrees)) / denominator                 # Divide 2*tan(θ) by denominator → complete tan(2θ)

# Formula: sin(θ/2) = ±sqrt((1 - cos(θ)) / 2)
# Returns sin of half an angle in degrees — positive value returned (sign depends on quadrant of θ/2)
def SinHalf(degrees):
    return math.sqrt((1 - Cos(degrees)) / 2)                # Take root of (1-cos(θ))/2 → complete |sin(θ/2)|

# Formula: cos(θ/2) = ±sqrt((1 + cos(θ)) / 2)
# Returns cos of half an angle in degrees — positive value returned (sign depends on quadrant of θ/2)
def CosHalf(degrees):
    return math.sqrt((1 + Cos(degrees)) / 2)                # Take root of (1+cos(θ))/2 → complete |cos(θ/2)|

# Formula: tan(θ/2) = sin(θ) / (1 + cos(θ))
# Returns tan of half an angle in degrees
# Returns 0 if denominator is effectively zero
def TanHalf(degrees):
    denominator = 1 + Cos(degrees)                          # Calculate denominator → 1 + cos(θ)
    if abs(denominator) < 1e-9:                             # Guard against division by zero
        return 0                                            # Return 0 safely
    return Sin(degrees) / denominator                       # Divide sin(θ) by denominator → complete tan(θ/2) = sin(θ)/(1+cos(θ))

# ============================================================
# RIGHT TRIANGLE SOLVERS
# ============================================================

# Formula: opposite = hypotenuse * sin(θ)
# Returns the side opposite to angle θ in a right triangle given hypotenuse and angle in degrees
def OppositeFromHypotenuse(hypotenuse, degrees):
    return hypotenuse * Sin(degrees)                        # Multiply hypotenuse by sin(θ) → complete opposite = hyp*sin(θ)

# Formula: adjacent = hypotenuse * cos(θ)
# Returns the side adjacent to angle θ in a right triangle given hypotenuse and angle in degrees
def AdjacentFromHypotenuse(hypotenuse, degrees):
    return hypotenuse * Cos(degrees)                        # Multiply hypotenuse by cos(θ) → complete adjacent = hyp*cos(θ)

# Formula: hypotenuse = opposite / sin(θ)
# Returns the hypotenuse given the opposite side and angle in degrees
# Returns 0 if sin(θ) is effectively zero to avoid division by zero
def HypotenuseFromOpposite(opposite, degrees):
    s = Sin(degrees)                                        # Calculate sin(θ)
    if abs(s) < 1e-9:                                       # Guard against division by zero
        return 0                                            # Return 0 safely
    return opposite / s                                     # Divide opposite by sin(θ) → complete hyp = opp/sin(θ)

# Formula: hypotenuse = adjacent / cos(θ)
# Returns the hypotenuse given the adjacent side and angle in degrees
# Returns 0 if cos(θ) is effectively zero to avoid division by zero
def HypotenuseFromAdjacent(adjacent, degrees):
    c = Cos(degrees)                                        # Calculate cos(θ)
    if abs(c) < 1e-9:                                       # Guard against division by zero
        return 0                                            # Return 0 safely
    return adjacent / c                                     # Divide adjacent by cos(θ) → complete hyp = adj/cos(θ)

# Formula: opposite = adjacent * tan(θ)
# Returns the opposite side given the adjacent side and angle in degrees
def OppositeFromAdjacent(adjacent, degrees):
    return adjacent * Tan(degrees)                          # Multiply adjacent by tan(θ) → complete opp = adj*tan(θ)

# Formula: adjacent = opposite / tan(θ)
# Returns the adjacent side given the opposite side and angle in degrees
# Returns 0 if tan(θ) is effectively zero to avoid division by zero
def AdjacentFromOpposite(opposite, degrees):
    t = Tan(degrees)                                        # Calculate tan(θ)
    if abs(t) < 1e-9:                                       # Guard against division by zero
        return 0                                            # Return 0 safely
    return opposite / t                                     # Divide opposite by tan(θ) → complete adj = opp/tan(θ)

# Formula: θ = arctan(opposite / adjacent)
# Returns the angle in degrees given the opposite and adjacent sides of a right triangle
# Returns 0 if adjacent is zero to avoid division by zero
def AngleFromSides(opposite, adjacent):
    if adjacent == 0:                                       # Guard against division by zero — vertical case
        return 90.0 if opposite > 0 else -90.0             # Return 90° or -90° for a vertical right triangle
    return Atan(opposite / adjacent)                        # Apply arctan(opp/adj) → complete θ = arctan(opp/adj)

# ============================================================
# HYPERBOLIC FUNCTIONS
# ============================================================

# Formula: sinh(x) = (e^x - e^(-x)) / 2
# Returns the hyperbolic sine of x
def Sinh(x):
    return math.sinh(x)                                     # Apply hyperbolic sine → complete sinh(x)

# Formula: cosh(x) = (e^x + e^(-x)) / 2
# Returns the hyperbolic cosine of x
def Cosh(x):
    return math.cosh(x)                                     # Apply hyperbolic cosine → complete cosh(x)

# Formula: tanh(x) = sinh(x) / cosh(x)
# Returns the hyperbolic tangent of x
def Tanh(x):
    return math.tanh(x)                                     # Apply hyperbolic tangent → complete tanh(x)

# Formula: cosh²(x) - sinh²(x) = 1
# Verifies the fundamental hyperbolic identity at a given value of x
# Returns True if cosh²(x) - sinh²(x) equals 1 within tolerance — should always be True
def HyperbolicIdentity(x, tolerance = 1e-9):
    return abs(Cosh(x) ** 2 - Sinh(x) ** 2 - 1) < tolerance  # Check cosh²-sinh²=1 within tolerance → True always

# ============================================================
# POLAR AND CARTESIAN COORDINATES
# ============================================================

# Formula: x = r * cos(θ),  y = r * sin(θ)
# Returns (x, y) Cartesian coordinates from polar coordinates (r, θ) where θ is in degrees
def PolarToCartesian(r, degrees):
    x = r * Cos(degrees)                                    # Horizontal component → r*cos(θ)
    y = r * Sin(degrees)                                    # Vertical component → r*sin(θ)
    return x, y                                             # Return both Cartesian components → complete (x, y)

# Formula: r = sqrt(x² + y²),  θ = atan2(y, x)
# Returns (r, θ) polar coordinates from Cartesian coordinates (x, y) where θ is in degrees
def CartesianToPolar(x, y):
    r     = math.hypot(x, y)                                # Calculate radial distance → r = sqrt(x²+y²)
    theta = Atan2(y, x)                                     # Calculate angle using atan2 → θ = atan2(y, x) in degrees
    return r, theta                                         # Return both polar components → complete (r, θ)

# ============================================================
# WAVE AND PERIODIC FUNCTIONS
# ============================================================

# Formula: f(x) = A * sin(Bx + C) + D
# Returns the value of a sinusoidal wave at position x
# A = amplitude, B = angular frequency, C = phase shift, D = vertical shift
def SineWave(x, amplitude, frequency, phase_shift = 0, vertical_shift = 0):
    return amplitude * Sin(frequency * x + phase_shift) + vertical_shift  # Apply general sine wave formula → complete A*sin(Bx+C)+D

# Formula: f(x) = A * cos(Bx + C) + D
# Returns the value of a cosine wave at position x
def CosineWave(x, amplitude, frequency, phase_shift = 0, vertical_shift = 0):
    return amplitude * Cos(frequency * x + phase_shift) + vertical_shift  # Apply general cosine wave formula → complete A*cos(Bx+C)+D

# Formula: period = 360 / |B|  (in degrees)
# Returns the period of a sinusoidal function with angular frequency B
# Returns 0 if frequency is zero to avoid division by zero
def WavePeriod(frequency):
    if frequency == 0:                                      # Guard against division by zero — zero frequency has no period
        return 0                                            # Return 0 safely
    return 360 / abs(frequency)                             # Divide full rotation by frequency → complete period = 360/|B|

# Formula: frequency = 1 / period
# Returns the frequency of a wave from its period
# Returns 0 if period is zero to avoid division by zero
def WaveFrequency(period):
    if period == 0:                                         # Guard against division by zero
        return 0                                            # Return 0 safely
    return 1 / period                                       # Reciprocal of period → complete f = 1/T

# Formula: phase_shift = -C / B
# Returns the horizontal phase shift of a sinusoidal function
# Returns 0 if frequency is zero to avoid division by zero
def PhaseShift(phase_constant, frequency):
    if frequency == 0:                                      # Guard against division by zero
        return 0                                            # Return 0 safely
    return -phase_constant / frequency                      # Negate phase constant and divide by frequency → complete shift = -C/B
