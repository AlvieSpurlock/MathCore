import math  # Import math for sqrt, log, exp, pi, inf, factorial

# ============================================================
# LIMITS
# ============================================================

# Formula: lim f(x) as x → a  (numerical approximation)
# Returns the numerical limit of f as x approaches a from both sides
# f must be a callable Python function
# Uses a small delta to sample f just left and just right of a and averages them
# Returns 0 if f is undefined at both sample points
def Limit(f, a, delta = 1e-7):
    try:
        left  = f(a - delta)                                # Sample f just to the left of a → left-hand approach
        right = f(a + delta)                                # Sample f just to the right of a → right-hand approach
        return (left + right) / 2                           # Average both sides → numerical limit estimate
    except:
        return 0                                            # Return 0 safely if f is undefined near a

# Formula: lim f(x) as x → a from the left  (x → a⁻)
# Returns the left-hand limit — approaching a from values smaller than a
def LimitLeft(f, a, delta = 1e-7):
    try:
        return f(a - delta)                                 # Sample just below a → left-hand limit
    except:
        return 0                                            # Return 0 safely if undefined

# Formula: lim f(x) as x → a from the right  (x → a⁺)
# Returns the right-hand limit — approaching a from values larger than a
def LimitRight(f, a, delta = 1e-7):
    try:
        return f(a + delta)                                 # Sample just above a → right-hand limit
    except:
        return 0                                            # Return 0 safely if undefined

# Formula: limit exists if left-hand limit ≈ right-hand limit
# Returns True if the two-sided limit exists at a — left and right limits must agree within tolerance
def LimitExists(f, a, delta = 1e-7, tolerance = 1e-6):
    left  = LimitLeft(f, a, delta)                          # Calculate left-hand limit
    right = LimitRight(f, a, delta)                         # Calculate right-hand limit
    return abs(left - right) < tolerance                    # Limit exists if both sides agree → True if |L - R| < tolerance

# ============================================================
# DIFFERENTIATION — NUMERICAL
# ============================================================

# Formula: f'(x) ≈ (f(x+h) - f(x-h)) / 2h
# Returns the numerical derivative of f at x using the central difference method
# f must be a callable Python function
# Returns 0 if f is undefined at the sample points
def Derivative(f, x, h = 1e-7):
    try:
        return (f(x + h) - f(x - h)) / (2 * h)             # Apply central difference formula → complete f'(x) ≈ (f(x+h)-f(x-h))/2h
    except:
        return 0                                            # Return 0 safely if f is undefined near x

# Formula: f''(x) ≈ (f(x+h) - 2f(x) + f(x-h)) / h²
# Returns the numerical second derivative of f at x
def SecondDerivative(f, x, h = 1e-7):
    try:
        return (f(x + h) - 2 * f(x) + f(x - h)) / (h ** 2)  # Apply second difference formula → complete f''(x)
    except:
        return 0                                            # Return 0 safely

# Formula: f'''(x) ≈ (f(x+2h) - 2f(x+h) + 2f(x-h) - f(x-2h)) / 2h³
# Returns the numerical third derivative of f at x
def ThirdDerivative(f, x, h = 1e-5):
    try:
        return (f(x + 2*h) - 2*f(x + h) + 2*f(x - h) - f(x - 2*h)) / (2 * h ** 3)  # Apply third difference formula → complete f'''(x)
    except:
        return 0                                            # Return 0 safely

# Formula: nth derivative approximated by applying Derivative recursively n times
# Returns the nth numerical derivative of f at x
# n must be a positive integer — returns f(x) unchanged for n = 0
def NthDerivative(f, x, n, h = 1e-5):
    if n == 0:                                              # Base case — zeroth derivative is the function itself
        return f(x)                                         # Return f(x) directly
    if n == 1:                                              # First derivative uses standard central difference
        return Derivative(f, x, h)                         # Apply central difference → complete f'(x)
    inner = lambda t: Derivative(f, t, h)                  # Wrap first derivative as a new callable function
    return NthDerivative(inner, x, n - 1, h)               # Recurse — differentiate the derivative → complete f^(n)(x)

# ============================================================
# DIFFERENTIATION — RULES (SYMBOLIC HELPERS)
# ============================================================

# Formula: d/dx [x^n] = n * x^(n-1)
# Returns the derivative of a power function n*x^(n-1) evaluated at x
def PowerRule(coefficient, exponent, x):
    new_coefficient = coefficient * exponent                # Multiply coefficient by exponent → new leading coefficient
    new_exponent    = exponent - 1                          # Decrease exponent by 1 → complete power rule
    return new_coefficient * (x ** new_exponent)            # Evaluate the derived term at x → complete d/dx[c*x^n] = cn*x^(n-1)

# Formula: d/dx [f*g] = f'*g + f*g'
# Returns the derivative of a product of two functions at x using the product rule
# f and g must be callable Python functions
def ProductRule(f, g, x, h = 1e-7):
    f_val  = f(x)                                           # Evaluate f at x
    g_val  = g(x)                                           # Evaluate g at x
    f_deriv = Derivative(f, x, h)                           # Differentiate f at x → f'(x)
    g_deriv = Derivative(g, x, h)                           # Differentiate g at x → g'(x)
    return f_deriv * g_val + f_val * g_deriv                # Apply product rule → complete f'g + fg'

# Formula: d/dx [f/g] = (f'*g - f*g') / g²
# Returns the derivative of a quotient of two functions at x using the quotient rule
# Returns 0 if g(x) is effectively zero to avoid division by zero
def QuotientRule(f, g, x, h = 1e-7):
    f_val   = f(x)                                          # Evaluate f at x
    g_val   = g(x)                                          # Evaluate g at x
    if abs(g_val) < 1e-9:                                   # Guard against division by zero — g(x) must be nonzero
        return 0                                            # Return 0 safely
    f_deriv = Derivative(f, x, h)                           # Differentiate f at x → f'(x)
    g_deriv = Derivative(g, x, h)                           # Differentiate g at x → g'(x)
    return (f_deriv * g_val - f_val * g_deriv) / (g_val ** 2)  # Apply quotient rule → complete (f'g - fg') / g²

# Formula: d/dx [f(g(x))] = f'(g(x)) * g'(x)
# Returns the derivative of a composition of two functions at x using the chain rule
# f and g must be callable Python functions
def ChainRule(f, g, x, h = 1e-7):
    g_val   = g(x)                                          # Evaluate inner function g at x → g(x)
    f_deriv = Derivative(f, g_val, h)                       # Differentiate outer function f at g(x) → f'(g(x))
    g_deriv = Derivative(g, x, h)                           # Differentiate inner function g at x → g'(x)
    return f_deriv * g_deriv                                # Multiply both derivatives → complete f'(g(x)) * g'(x)

# ============================================================
# CRITICAL POINTS AND CURVE ANALYSIS
# ============================================================

# Formula: f'(x) = 0 at a critical point
# Returns True if x is a critical point of f — where the derivative is effectively zero
def IsCriticalPoint(f, x, h = 1e-7, tolerance = 1e-6):
    return abs(Derivative(f, x, h)) < tolerance             # Check if derivative is effectively zero → True if critical point

# Formula: f''(x) > 0 → local minimum,  f''(x) < 0 → local maximum,  f''(x) = 0 → inconclusive
# Returns "minimum", "maximum", or "inconclusive" based on the second derivative test at x
def SecondDerivativeTest(f, x, h = 1e-7):
    d2 = SecondDerivative(f, x, h)                          # Calculate second derivative at x
    if d2 > 1e-9:                                           # Positive second derivative → concave up → local minimum
        return "minimum"
    if d2 < -1e-9:                                          # Negative second derivative → concave down → local maximum
        return "maximum"
    return "inconclusive"                                   # Second derivative is zero → test gives no information

# Formula: f''(x) > 0 → concave up,  f''(x) < 0 → concave down
# Returns "concave up" or "concave down" based on the sign of the second derivative at x
def Concavity(f, x, h = 1e-7):
    d2 = SecondDerivative(f, x, h)                          # Calculate second derivative at x
    if d2 > 0:                                              # Positive second derivative → curve bends upward
        return "concave up"
    return "concave down"                                   # Negative second derivative → curve bends downward

# Formula: inflection point where f''(x) changes sign — approximate by finding where f''(x) ≈ 0
# Returns True if x is approximately an inflection point — second derivative near zero with sign change nearby
def IsInflectionPoint(f, x, h = 1e-5, tolerance = 1e-4):
    d2      = SecondDerivative(f, x, h)                     # Calculate second derivative at x
    d2_left = SecondDerivative(f, x - h, h)                 # Calculate second derivative just left of x
    d2_right= SecondDerivative(f, x + h, h)                 # Calculate second derivative just right of x
    near_zero    = abs(d2) < tolerance                      # Check if second derivative is near zero at x
    sign_change  = d2_left * d2_right < 0                   # Check if second derivative changes sign across x
    return near_zero or sign_change                         # Inflection if near zero or sign change detected

# Formula: slope of tangent line = f'(x0)
# Returns the equation of the tangent line at x0 as a callable lambda y = f'(x0)*(x-x0) + f(x0)
def TangentLine(f, x0, h = 1e-7):
    slope     = Derivative(f, x0, h)                        # Get slope of tangent → f'(x0)
    y_intercept = f(x0) - slope * x0                        # Calculate y-intercept → b = f(x0) - f'(x0)*x0
    return lambda x: slope * x + y_intercept                # Return tangent line as callable → y = f'(x0)*x + b

# Formula: slope of normal line = -1 / f'(x0)
# Returns the equation of the normal line at x0 as a callable — perpendicular to the tangent
# Returns the horizontal line y = f(x0) if f'(x0) is zero
def NormalLine(f, x0, h = 1e-7):
    slope = Derivative(f, x0, h)                            # Get slope of tangent first → f'(x0)
    if abs(slope) < 1e-9:                                   # If tangent is horizontal, normal is vertical — approximate as horizontal
        return lambda x: f(x0)                              # Return horizontal line at f(x0)
    normal_slope    = -1 / slope                            # Normal slope is negative reciprocal → -1/f'(x0)
    y_intercept     = f(x0) - normal_slope * x0             # Calculate y-intercept for normal line
    return lambda x: normal_slope * x + y_intercept         # Return normal line as callable

# ============================================================
# INTEGRATION — NUMERICAL
# ============================================================

# Formula: ∫f(x)dx ≈ h * Σf(xi)  (left Riemann sum)
# Returns a numerical approximation of the definite integral using left endpoint rectangles
# n = number of subintervals — higher n gives better accuracy
def RiemannLeft(f, a, b, n = 1000):
    if n == 0:                                              # Guard against division by zero
        return 0                                            # Return 0 safely
    h      = (b - a) / n                                    # Calculate width of each subinterval → h = (b-a)/n
    total  = 0                                              # Initialize area accumulator
    for i in range(n):                                      # Loop through each subinterval
        total += f(a + i * h)                               # Add function value at left endpoint → f(a + i*h)
    return total * h                                        # Multiply sum by width → complete left Riemann sum

# Formula: ∫f(x)dx ≈ h * Σf(xi+1)  (right Riemann sum)
# Returns a numerical approximation of the definite integral using right endpoint rectangles
def RiemannRight(f, a, b, n = 1000):
    if n == 0:                                              # Guard against division by zero
        return 0                                            # Return 0 safely
    h      = (b - a) / n                                    # Calculate subinterval width → h = (b-a)/n
    total  = 0                                              # Initialize area accumulator
    for i in range(1, n + 1):                               # Loop using right endpoints
        total += f(a + i * h)                               # Add function value at right endpoint → f(a + i*h)
    return total * h                                        # Multiply sum by width → complete right Riemann sum

# Formula: ∫f(x)dx ≈ (h/2) * Σ(f(xi) + f(xi+1))  (trapezoid rule)
# Returns a numerical approximation using trapezoids — more accurate than Riemann sums
def TrapezoidRule(f, a, b, n = 1000):
    if n == 0:                                              # Guard against division by zero
        return 0                                            # Return 0 safely
    h     = (b - a) / n                                     # Calculate subinterval width → h = (b-a)/n
    total = f(a) + f(b)                                     # Add the two endpoints first → f(a) + f(b)
    for i in range(1, n):                                   # Loop through all interior points
        total += 2 * f(a + i * h)                           # Interior points count twice → 2*f(xi)
    return (h / 2) * total                                  # Multiply by h/2 → complete trapezoid rule

# Formula: ∫f(x)dx ≈ (h/3) * [f(x0) + 4f(x1) + 2f(x2) + ... + f(xn)]  (Simpson's rule)
# Returns a numerical approximation using Simpson's rule — high accuracy parabolic approximation
# n must be even — rounds up to even if odd is passed
def SimpsonsRule(f, a, b, n = 1000):
    if n % 2 != 0:                                          # Simpson's rule requires an even number of intervals
        n += 1                                              # Round up to even if odd was passed
    if n == 0:                                              # Guard against division by zero
        return 0                                            # Return 0 safely
    h     = (b - a) / n                                     # Calculate subinterval width → h = (b-a)/n
    total = f(a) + f(b)                                     # Start with endpoints → f(a) + f(b)
    for i in range(1, n):                                   # Loop through all interior points
        weight = 4 if i % 2 != 0 else 2                    # Alternating weights — 4 for odd indices, 2 for even
        total += weight * f(a + i * h)                      # Apply weight and add to total
    return (h / 3) * total                                  # Multiply by h/3 → complete Simpson's rule

# ============================================================
# INTEGRATION — FUNDAMENTAL THEOREM
# ============================================================

# Formula: d/dx [∫a to x f(t) dt] = f(x)
# Verifies the Fundamental Theorem of Calculus Part 1 numerically at a given point
# Returns True if the derivative of the integral function equals f(x) within tolerance
def FundamentalTheoremPart1(f, a, x, tolerance = 1e-4):
    F = lambda t: SimpsonsRule(f, a, t, 1000)               # Define the integral function F(t) = ∫a to t f(u) du
    dF = Derivative(F, x)                                   # Differentiate F at x → should equal f(x)
    return abs(dF - f(x)) < tolerance                       # Check if derivative of integral equals f(x) → FTC Part 1

# Formula: ∫a to b f(x) dx = F(b) - F(a)
# Returns the definite integral using FTC Part 2 — numerically approximated via Simpson's rule
# This is an alias with a descriptive name emphasizing the evaluation theorem
def DefiniteIntegral(f, a, b, n = 1000):
    return SimpsonsRule(f, a, b, n)                         # Apply Simpson's rule as the best numerical antiderivative estimate → ∫a to b f(x) dx

# ============================================================
# SERIES AND CONVERGENCE
# ============================================================

# Formula: Taylor series — f(x) ≈ Σ f^(n)(a)/n! * (x-a)^n
# Returns the Taylor series approximation of f centered at a evaluated at x
# terms = number of terms to include — more terms gives better accuracy
def TaylorSeries(f, a, x, terms = 10):
    result = 0                                              # Initialize result accumulator
    for n in range(terms):                                  # Loop through each term index
        fn    = NthDerivative(f, a, n)                      # Calculate nth derivative of f at the center a → f^(n)(a)
        coeff = fn / math.factorial(n)                      # Divide by n! → Taylor coefficient f^(n)(a)/n!
        result += coeff * (x - a) ** n                      # Multiply by (x-a)^n and add to running total
    return result                                           # Return the Taylor polynomial approximation

# Formula: Maclaurin series — Taylor series centered at a = 0
# Returns the Maclaurin series approximation of f evaluated at x
def MaclaurinSeries(f, x, terms = 10):
    return TaylorSeries(f, 0, x, terms)                     # Maclaurin is Taylor centered at 0 → delegate to TaylorSeries

# Formula: geometric series sum = a / (1 - r)  for |r| < 1
# Returns the sum of an infinite geometric series
# Returns 0 if |r| >= 1 — series diverges
def GeometricSeriesSum(a, r):
    if abs(r) >= 1:                                         # Guard — series diverges if |r| is 1 or greater
        return 0                                            # Return 0 safely — infinite sum does not exist
    return a / (1 - r)                                      # Apply geometric series formula → complete S = a/(1-r)

# Formula: partial sum Sn = Σ f(k) for k from start to n
# Returns the partial sum of a series defined by f(k) up to n terms
# f must be a callable function of k
def PartialSum(f, start, n):
    return sum(f(k) for k in range(start, n + 1))           # Sum f(k) over all k from start to n → complete Sn

# Formula: ratio test — L = lim |a(n+1)/a(n)| as n → ∞
# Returns the ratio test limit numerically at a large n
# Returns "converges" if L < 1, "diverges" if L > 1, "inconclusive" if L = 1
# f must return the nth term of the series
def RatioTest(f, n = 1000):
    fn   = abs(f(n))                                        # Get |a(n)|
    fn1  = abs(f(n + 1))                                    # Get |a(n+1)|
    if fn == 0:                                             # Guard against division by zero
        return "inconclusive"                               # Cannot determine ratio if current term is zero
    L = fn1 / fn                                            # Calculate ratio → L = |a(n+1)/a(n)|
    if L < 1:                                               # L < 1 means terms shrink fast enough → convergent
        return "converges"
    if L > 1:                                               # L > 1 means terms grow → divergent
        return "diverges"
    return "inconclusive"                                   # L = 1 → ratio test gives no information

# ============================================================
# MULTIVARIABLE CALCULUS — PARTIAL DERIVATIVES
# ============================================================

# Formula: ∂f/∂x ≈ (f(x+h, y) - f(x-h, y)) / 2h
# Returns the partial derivative of f with respect to x at (x, y)
# f must accept two arguments (x, y)
def PartialX(f, x, y, h = 1e-7):
    try:
        return (f(x + h, y) - f(x - h, y)) / (2 * h)       # Central difference in x direction → complete ∂f/∂x
    except:
        return 0                                            # Return 0 safely if undefined

# Formula: ∂f/∂y ≈ (f(x, y+h) - f(x, y-h)) / 2h
# Returns the partial derivative of f with respect to y at (x, y)
def PartialY(f, x, y, h = 1e-7):
    try:
        return (f(x, y + h) - f(x, y - h)) / (2 * h)       # Central difference in y direction → complete ∂f/∂y
    except:
        return 0                                            # Return 0 safely if undefined

# Formula: ∂f/∂z ≈ (f(x, y, z+h) - f(x, y, z-h)) / 2h
# Returns the partial derivative of f with respect to z at (x, y, z)
# f must accept three arguments (x, y, z)
def PartialZ(f, x, y, z, h = 1e-7):
    try:
        return (f(x, y, z + h) - f(x, y, z - h)) / (2 * h) # Central difference in z direction → complete ∂f/∂z
    except:
        return 0                                            # Return 0 safely if undefined

# Formula: gradient = (∂f/∂x, ∂f/∂y)
# Returns the gradient vector of a 2-variable function at (x, y) as a tuple
# The gradient points in the direction of steepest ascent
def Gradient2D(f, x, y, h = 1e-7):
    dx = PartialX(f, x, y, h)                               # Partial derivative in x direction → ∂f/∂x
    dy = PartialY(f, x, y, h)                               # Partial derivative in y direction → ∂f/∂y
    return dx, dy                                           # Return gradient vector → complete ∇f = (∂f/∂x, ∂f/∂y)

# Formula: gradient = (∂f/∂x, ∂f/∂y, ∂f/∂z)
# Returns the gradient vector of a 3-variable function at (x, y, z) as a tuple
def Gradient3D(f, x, y, z, h = 1e-7):
    dx = PartialX(f, x, y, h)                               # Partial derivative in x direction
    dy = PartialY(f, x, y, h)                               # Partial derivative in y direction
    dz = PartialZ(f, x, y, z, h)                            # Partial derivative in z direction
    return dx, dy, dz                                       # Return full gradient vector → complete ∇f = (∂f/∂x, ∂f/∂y, ∂f/∂z)

# Formula: directional derivative = ∇f · u  where u is a unit vector
# Returns the rate of change of f in the direction of vector (ux, uy) at point (x, y)
# The direction vector is normalized automatically
# Returns 0 if direction vector has zero magnitude
def DirectionalDerivative2D(f, x, y, ux, uy, h = 1e-7):
    mag = math.sqrt(ux ** 2 + uy ** 2)                      # Calculate magnitude of direction vector
    if mag == 0:                                            # Guard against zero direction vector
        return 0                                            # Return 0 safely
    ux /= mag                                               # Normalize x component → unit vector
    uy /= mag                                               # Normalize y component → unit vector
    gx, gy = Gradient2D(f, x, y, h)                        # Calculate gradient at (x, y) → (∂f/∂x, ∂f/∂y)
    return gx * ux + gy * uy                                # Dot gradient with unit direction → complete D_u f = ∇f · u

# ============================================================
# ARC LENGTH AND AREA
# ============================================================

# Formula: L = ∫a to b sqrt(1 + (f'(x))²) dx
# Returns the arc length of f from x = a to x = b
# Numerically integrates the arc length formula using Simpson's rule
def ArcLength(f, a, b, n = 1000):
    integrand = lambda x: math.sqrt(1 + Derivative(f, x) ** 2)  # Define integrand → sqrt(1 + (f'(x))²)
    return SimpsonsRule(integrand, a, b, n)                 # Integrate the arc length integrand → complete L = ∫sqrt(1+f'²)dx

# Formula: A = ∫a to b |f(x)| dx
# Returns the area between f and the x-axis from a to b — uses absolute value to count all area as positive
def AreaUnderCurve(f, a, b, n = 1000):
    return SimpsonsRule(lambda x: abs(f(x)), a, b, n)       # Integrate absolute value → complete A = ∫|f(x)|dx

# Formula: A = ∫a to b (f(x) - g(x)) dx
# Returns the area between two curves f and g from a to b
# f should be the upper function and g the lower — use abs for guaranteed positive area
def AreaBetweenCurves(f, g, a, b, n = 1000):
    return SimpsonsRule(lambda x: abs(f(x) - g(x)), a, b, n)  # Integrate absolute difference → complete A = ∫|f-g|dx

# Formula: V = π * ∫a to b (f(x))² dx  (disk method — rotation around x-axis)
# Returns the volume of revolution when f is rotated around the x-axis
def VolumeOfRevolution(f, a, b, n = 1000):
    return math.pi * SimpsonsRule(lambda x: f(x) ** 2, a, b, n)  # Integrate f² then multiply by π → complete V = π∫f²dx
