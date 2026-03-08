import math  # Import math for sqrt, log, pow

# ============================================================
# LINEAR EQUATIONS
# ============================================================

# Formula: y = mx + b
# Returns y — the output of a linear equation given slope, x, and y-intercept
def Linear(m, x, b):
    return m * x + b                        # Multiply slope by x then add intercept → complete y = mx + b

# Formula: m = (y2 - y1) / (x2 - x1)
# Returns slope — rise over run between two points
# Returns 0 if x values are equal to avoid division by zero
def Slope(x1, y1, x2, y2):
    if x2 - x1 == 0:                        # Guard against division by zero — vertical line has undefined slope
        return 0                            # Return 0 safely
    return (y2 - y1) / (x2 - x1)           # Divide rise by run → complete m = (y2-y1)/(x2-x1)

# Formula: b = y - m*x
# Returns y-intercept — the value of y when x is zero
def YIntercept(m, x, y):
    return y - m * x                        # Subtract m*x from y → complete b = y - mx

# Formula: x = (y - b) / m
# Returns x — solving a linear equation for x given y, slope, and intercept
# Returns 0 if slope is zero to avoid division by zero
def SolveLinearForX(m, b, y):
    if m == 0:                              # Guard against division by zero — horizontal line never reaches y unless b == y
        return 0                            # Return 0 safely
    return (y - b) / m                      # Subtract intercept from y then divide by slope → complete x = (y-b)/m

# Formula: x = (b2 - b1) / (m1 - m2)
# Returns the x-value where two lines intersect — set equal and solve
# Returns 0 if slopes are equal to avoid division by zero — parallel lines never intersect
def LineIntersectionX(m1, b1, m2, b2):
    if m1 - m2 == 0:                        # Guard against division by zero — parallel lines have no intersection
        return 0                            # Return 0 safely
    return (b2 - b1) / (m1 - m2)           # Divide intercept difference by slope difference → complete x = (b2-b1)/(m1-m2)

# Formula: y = m1*x + b1  (using the x from LineIntersectionX)
# Returns the y-value where two lines intersect
def LineIntersectionY(m1, b1, m2, b2):
    x = LineIntersectionX(m1, b1, m2, b2)  # Find the x-coordinate of the intersection first
    return Linear(m1, x, b1)               # Plug x back into the first line → complete y = m1*x + b1

# ============================================================
# QUADRATIC EQUATIONS
# ============================================================

# Formula: y = ax² + bx + c
# Returns y — the output of a quadratic equation
def Quadratic(a, b, c, x):
    return a * (x ** 2) + b * x + c        # Compute each term and sum → complete y = ax² + bx + c

# Formula: discriminant = b² - 4ac
# Returns the discriminant — determines the nature of the roots
# Positive → two real roots, zero → one real root, negative → two complex roots
def Discriminant(a, b, c):
    return (b ** 2) - (4 * a * c)          # Square b then subtract 4ac → complete Δ = b² - 4ac

# Formula: x = (-b ± sqrt(b² - 4ac)) / 2a
# Returns (x1, x2) — both roots of a quadratic equation
# Returns (0, 0) if a is zero — not a quadratic
# Returns complex roots as strings if discriminant is negative
def QuadraticRoots(a, b, c):
    if a == 0:                              # Guard — if a is zero this is not a quadratic equation
        return 0, 0                         # Return 0 safely — caller should use linear solver instead
    d = Discriminant(a, b, c)              # Calculate discriminant to determine root type
    if d < 0:                               # Negative discriminant → complex (imaginary) roots
        real = -b / (2 * a)                # Real part of both roots → -b / 2a
        imag = math.sqrt(-d) / (2 * a)    # Imaginary part → sqrt(-Δ) / 2a
        return f"{real} + {imag}i", f"{real} - {imag}i"  # Return both complex roots as formatted strings
    x1 = (-b + math.sqrt(d)) / (2 * a)    # Positive root → complete x1 = (-b + sqrt(Δ)) / 2a
    x2 = (-b - math.sqrt(d)) / (2 * a)    # Negative root → complete x2 = (-b - sqrt(Δ)) / 2a
    return x1, x2                          # Return both real roots

# Formula: vertex_x = -b / 2a
# Returns the x-coordinate of the vertex — the axis of symmetry of the parabola
# Returns 0 if a is zero to avoid division by zero
def VertexX(a, b):
    if a == 0:                              # Guard against division by zero — no vertex if not quadratic
        return 0                            # Return 0 safely
    return -b / (2 * a)                    # Negate b then divide by 2a → complete x = -b/2a

# Formula: vertex_y = c - b² / 4a
# Returns the y-coordinate of the vertex — the minimum or maximum of the parabola
# Returns 0 if a is zero to avoid division by zero
def VertexY(a, b, c):
    if a == 0:                              # Guard against division by zero — no vertex if not quadratic
        return 0                            # Return 0 safely
    return c - (b ** 2) / (4 * a)         # Subtract b²/4a from c → complete y = c - b²/4a

# ============================================================
# POLYNOMIAL EVALUATION
# ============================================================

# Formula: p(x) = c[0]*x^n + c[1]*x^(n-1) + ... + c[n]
# Returns the value of a polynomial at x given a list of coefficients
# Coefficients are ordered from highest degree to constant term — e.g. [2, -3, 1] = 2x² - 3x + 1
def EvaluatePolynomial(coefficients, x):
    result = 0                              # Initialize result accumulator
    degree = len(coefficients) - 1         # Highest degree is one less than the number of coefficients
    for i, c in enumerate(coefficients):   # Loop through each coefficient with its index
        result += c * (x ** (degree - i))  # Multiply coefficient by x raised to its degree → add to running total
    return result                           # Return the fully evaluated polynomial value

# Formula: Same as above — checks if p(x) == 0 within a small tolerance
# Returns True if x is a root of the polynomial — i.e. the polynomial evaluates to zero at x
def IsRoot(coefficients, x, tolerance = 1e-9):
    return abs(EvaluatePolynomial(coefficients, x)) < tolerance  # Evaluate and check if effectively zero → True if root

# ============================================================
# EXPONENTS AND LOGARITHMS
# ============================================================

# Formula: result = base ^ exponent
# Returns the result of raising a base to a power
def Power(base, exponent):
    return base ** exponent                 # Raise base to exponent → complete result = base^exponent

# Formula: result = base ^ (1/n)
# Returns the nth root of a value — generalizes square root to any root
# Returns 0 if n is zero to avoid division by zero
def NthRoot(value, n):
    if n == 0:                              # Guard against division by zero — zeroth root is undefined
        return 0                            # Return 0 safely
    return value ** (1 / n)                # Raise value to the power of 1/n → complete result = value^(1/n)

# Formula: log_b(x) = log(x) / log(b)
# Returns the logarithm of x in any base using the change of base formula
# Returns 0 if x or base is zero or negative to avoid domain errors
def LogBase(x, base):
    if x <= 0 or base <= 0 or base == 1:   # Guard against log domain errors — x and base must be positive, base ≠ 1
        return 0                            # Return 0 safely
    return math.log(x) / math.log(base)    # Divide natural log of x by natural log of base → complete log_b(x)

# Formula: ln(x) = log_e(x)
# Returns the natural logarithm of x
# Returns 0 if x is zero or negative to avoid domain errors
def NaturalLog(x):
    if x <= 0:                              # Guard against log domain error — ln undefined for non-positive values
        return 0                            # Return 0 safely
    return math.log(x)                      # Apply natural log → complete ln(x)

# Formula: result = e^x
# Returns e raised to the power of x — the inverse of the natural logarithm
def Exponential(x):
    return math.exp(x)                      # Raise e to x → complete e^x

# ============================================================
# ABSOLUTE VALUE AND INEQUALITIES
# ============================================================

# Formula: |x|
# Returns the absolute value of x — always non-negative
def AbsoluteValue(x):
    return abs(x)                           # Return distance from zero → complete |x|

# Formula: |a - b|
# Returns the absolute difference between two values — distance between them on the number line
def AbsoluteDifference(a, b):
    return abs(a - b)                       # Subtract then take absolute value → complete |a - b|

# Formula: clamp — returns value constrained between min and max
# Returns value if within range, otherwise returns the nearest boundary
def Clamp(value, min_val, max_val):
    if value < min_val:                     # If value is below the lower bound...
        return min_val                      # Return the lower bound instead
    if value > max_val:                     # If value is above the upper bound...
        return max_val                      # Return the upper bound instead
    return value                            # Value is within range — return it unchanged

# ============================================================
# RATIOS AND PROPORTIONS
# ============================================================

# Formula: ratio = a / b
# Returns the ratio of a to b
# Returns 0 if b is zero to avoid division by zero
def Ratio(a, b):
    if b == 0:                              # Guard against division by zero — ratio with zero denominator is undefined
        return 0                            # Return 0 safely
    return a / b                            # Divide a by b → complete ratio = a/b

# Formula: x = (a * d) / b  where a/b = x/d  (cross multiply)
# Returns the missing value in a proportion a/b = x/d
# Returns 0 if b is zero to avoid division by zero
def SolveProportion(a, b, d):
    if b == 0:                              # Guard against division by zero — denominator cannot be zero
        return 0                            # Return 0 safely
    return (a * d) / b                      # Cross multiply and divide → complete x = (a*d)/b

# Formula: percent = (part / whole) * 100
# Returns the percentage that part is of whole
# Returns 0 if whole is zero to avoid division by zero
def Percentage(part, whole):
    if whole == 0:                          # Guard against division by zero — cannot take percent of zero
        return 0                            # Return 0 safely
    return (part / whole) * 100            # Divide part by whole then scale to percentage → complete % = (part/whole)*100

# Formula: part = (percent / 100) * whole
# Returns the part — what a given percentage of a whole equals
def PercentageOf(percent, whole):
    return (percent / 100) * whole         # Convert percent to decimal then multiply by whole → complete part = (%/100)*whole

# Formula: change = ((new - old) / old) * 100
# Returns the percentage change between an old and new value
# Returns 0 if old is zero to avoid division by zero
def PercentageChange(old, new):
    if old == 0:                            # Guard against division by zero — cannot calculate change from zero
        return 0                            # Return 0 safely
    return ((new - old) / old) * 100       # Divide difference by original then scale → complete % change = ((new-old)/old)*100

# ============================================================
# SEQUENCES AND SERIES
# ============================================================

# Formula: a_n = a1 + (n - 1) * d
# Returns the nth term of an arithmetic sequence — starts at a1, increases by d each step
def ArithmeticTerm(a1, d, n):
    return a1 + (n - 1) * d                # Add common difference times position offset to first term → complete a_n = a1 + (n-1)d

# Formula: S_n = n/2 * (a1 + a_n)
# Returns the sum of the first n terms of an arithmetic sequence
def ArithmeticSum(a1, d, n):
    an = ArithmeticTerm(a1, d, n)          # Calculate the nth term first → a_n = a1 + (n-1)d
    return (n / 2) * (a1 + an)             # Multiply n/2 by the sum of first and last terms → complete S_n = n/2*(a1+an)

# Formula: a_n = a1 * r^(n-1)
# Returns the nth term of a geometric sequence — starts at a1, multiplies by r each step
def GeometricTerm(a1, r, n):
    return a1 * (r ** (n - 1))             # Raise ratio to position offset then multiply by first term → complete a_n = a1*r^(n-1)

# Formula: S_n = a1 * (1 - r^n) / (1 - r)
# Returns the sum of the first n terms of a geometric sequence
# Returns n * a1 if r equals 1 to avoid division by zero
def GeometricSum(a1, r, n):
    if r == 1:                              # Special case — if ratio is 1 all terms are equal to a1
        return n * a1                       # Sum is simply n times the first term → n * a1
    return a1 * (1 - r ** n) / (1 - r)    # Apply geometric sum formula → complete S_n = a1*(1-r^n)/(1-r)

# Formula: S = a1 / (1 - r)  (only valid when |r| < 1)
# Returns the sum of an infinite geometric series — converges only when |r| < 1
# Returns 0 if |r| >= 1 since the series diverges
def InfiniteGeometricSum(a1, r):
    if abs(r) >= 1:                         # Guard — series diverges if |r| is 1 or greater
        return 0                            # Return 0 safely — infinite sum does not exist
    return a1 / (1 - r)                    # Divide first term by 1 minus ratio → complete S = a1/(1-r)

# ============================================================
# FACTORING AND GCD / LCM
# ============================================================

# Formula: GCD via Euclidean algorithm
# Returns the greatest common divisor of two integers
def GCD(a, b):
    a = int(abs(a))                         # Take absolute value and convert to int — GCD is always positive
    b = int(abs(b))                         # Take absolute value and convert to int
    while b:                                # Loop until remainder is zero — Euclidean algorithm
        a, b = b, a % b                     # Replace a with b and b with the remainder → progress toward GCD
    return a                                # When b is zero, a holds the GCD → return it

# Formula: LCM = |a * b| / GCD(a, b)
# Returns the least common multiple of two integers
# Returns 0 if either value is zero to avoid division by zero
def LCM(a, b):
    if a == 0 or b == 0:                    # Guard — LCM with zero is always zero
        return 0                            # Return 0 safely
    return abs(a * b) // GCD(a, b)         # Divide product of both values by their GCD → complete LCM = |a*b|/GCD(a,b)

# Formula: checks if n is divisible by d with no remainder
# Returns True if a is divisible by b — i.e. b is a factor of a
def IsDivisible(a, b):
    if b == 0:                              # Guard against division by zero — nothing is divisible by zero
        return False                        # Return False safely
    return a % b == 0                       # Check if remainder is zero → True if b divides a evenly

# Formula: trial division up to sqrt(n)
# Returns True if n is a prime number — divisible only by 1 and itself
def IsPrime(n):
    if n < 2:                               # Numbers less than 2 are not prime by definition
        return False                        # Return False — 0 and 1 are not prime
    if n == 2:                              # 2 is the only even prime number
        return True                         # Return True immediately
    if n % 2 == 0:                          # All other even numbers are not prime
        return False                        # Return False — divisible by 2
    for i in range(3, int(math.sqrt(n)) + 1, 2):  # Check odd divisors up to sqrt(n) — even ones already eliminated
        if n % i == 0:                      # If n is divisible by any odd number up to sqrt(n)...
            return False                    # Not prime — has a factor other than 1 and itself
    return True                             # No factors found → n is prime

# Formula: factor out all prime divisors iteratively
# Returns a list of prime factors of n in ascending order
def PrimeFactors(n):
    n = int(abs(n))                         # Take absolute value and convert to int — prime factors are positive
    factors = []                            # Initialize empty list to accumulate prime factors
    d = 2                                   # Start trial division at 2 — the smallest prime
    while d * d <= n:                       # Only need to check up to sqrt(n)
        while n % d == 0:                   # While d divides n evenly...
            factors.append(d)               # Add d to the factor list
            n //= d                         # Divide n by d to eliminate this factor
        d += 1                              # Move to the next candidate divisor
    if n > 1:                               # If n is still greater than 1 after the loop it is itself prime
        factors.append(n)                   # Add the remaining prime factor
    return factors                          # Return the complete list of prime factors

# ============================================================
# SYSTEMS OF EQUATIONS
# ============================================================

# Formula: Cramer's rule for 2x2 systems
#          a1x + b1y = c1
#          a2x + b2y = c2
#          x = (c1*b2 - c2*b1) / (a1*b2 - a2*b1)
#          y = (a1*c2 - a2*c1) / (a1*b2 - a2*b1)
# Returns (x, y) solution to a 2x2 linear system
# Returns (0, 0) if the determinant is zero — system has no unique solution
def SolveSystem2x2(a1, b1, c1, a2, b2, c2):
    det = a1 * b2 - a2 * b1                # Calculate the determinant of the coefficient matrix → a1*b2 - a2*b1
    if det == 0:                            # Guard — determinant of zero means parallel or identical lines
        return 0, 0                         # Return 0 safely — no unique solution exists
    x = (c1 * b2 - c2 * b1) / det         # Apply Cramer's rule for x → x = (c1*b2 - c2*b1) / det
    y = (a1 * c2 - a2 * c1) / det         # Apply Cramer's rule for y → y = (a1*c2 - a2*c1) / det
    return x, y                             # Return the unique solution → complete (x, y)

# Formula: substitution — solve one equation for y then substitute into the other
#          Given: y = m1*x + b1  and  y = m2*x + b2
#          Set equal: m1*x + b1 = m2*x + b2  →  x = (b2 - b1) / (m1 - m2)
# Returns (x, y) intersection of two lines in slope-intercept form
# Returns (0, 0) if lines are parallel — no intersection
def SolveSlopeIntercept(m1, b1, m2, b2):
    if m1 - m2 == 0:                        # Guard — parallel lines have no intersection
        return 0, 0                         # Return 0 safely
    x = (b2 - b1) / (m1 - m2)             # Solve for x by setting both lines equal → x = (b2-b1)/(m1-m2)
    y = m1 * x + b1                         # Substitute x back into first equation → complete y = m1*x + b1
    return x, y                             # Return the intersection point → complete (x, y)

# ============================================================
# FUNCTIONS AND INVERSES
# ============================================================

# Formula: f(g(x)) — function composition
# Returns the result of applying g first then f — f composed with g evaluated at x
# Both f and g must be callable Python functions
def Compose(f, g, x):
    return f(g(x))                          # Apply g to x first then apply f to the result → complete f(g(x))

# Formula: checks if f(f_inverse(x)) ≈ x  within tolerance
# Returns True if f_inverse appears to be the inverse of f at the given x value
# Both must be callable Python functions
def IsInverse(f, f_inverse, x, tolerance = 1e-9):
    return abs(f(f_inverse(x)) - x) < tolerance  # Compose f with f_inverse and check if result equals x → True if inverse

# Formula: average rate of change = (f(x2) - f(x1)) / (x2 - x1)
# Returns the average rate of change of a function between two x values
# f must be a callable Python function
# Returns 0 if x values are equal to avoid division by zero
def AverageRateOfChange(f, x1, x2):
    if x2 - x1 == 0:                        # Guard against division by zero — no change in x means undefined rate
        return 0                            # Return 0 safely
    return (f(x2) - f(x1)) / (x2 - x1)    # Divide change in output by change in input → complete Δf/Δx

# ============================================================
# INEQUALITIES
# ============================================================

# Formula: solves ax + b < c  →  x < (c - b) / a
# Returns the boundary value where ax + b = c and the direction of the inequality
# Returns (boundary, direction_string) — e.g. (3.0, "x < 3.0")
# Returns (0, "undefined") if a is zero to avoid division by zero
def SolveLinearInequality(a, b, c, symbol = "<"):
    if a == 0:                              # Guard against division by zero — if a is zero x drops out
        return 0, "undefined"               # Return safely — no x term to solve for
    boundary = (c - b) / a                  # Solve for x at equality → x = (c-b)/a
    if a < 0:                               # If a is negative the inequality flips when dividing both sides by a
        flipped = {"<": ">", ">": "<", "<=": ">=", ">=": "<="}  # Map each symbol to its flipped version
        symbol  = flipped.get(symbol, symbol)  # Flip the inequality symbol → direction reverses for negative a
    return boundary, f"x {symbol} {boundary}"  # Return boundary value and human-readable inequality string
