import math  # Import math for sqrt, log, exp, sin, cos, tan, pi, factorial

# ============================================================
# POLYNOMIAL DIFFERENTIATION — SYMBOLIC
# ============================================================

# Formula: d/dx [c * x^n] = c * n * x^(n-1)
# Returns the derivative of a single power term as a (coefficient, exponent) tuple
# The input is a single term described by its coefficient and exponent
def DiffPowerTerm(coefficient, exponent):
    new_coefficient = coefficient * exponent                    # Multiply coefficient by exponent → new leading coefficient
    new_exponent    = exponent - 1                              # Reduce exponent by 1 → complete power rule
    return (new_coefficient, new_exponent)                      # Return derived term as (coefficient, exponent) tuple

# Formula: d/dx [Σ aₙxⁿ] = Σ n*aₙx^(n-1)
# Returns the symbolic derivative of a polynomial as a new coefficient list
# Input coefficients are ordered from highest degree to constant  (e.g. [2, -3, 1] = 2x²-3x+1)
# Returns [0] for a constant polynomial whose derivative is zero
def DiffPolynomial(coefficients):
    degree = len(coefficients) - 1                              # Degree of the polynomial = number of terms minus 1
    if degree == 0:                                             # Derivative of a constant is zero
        return [0]                                              # Return [0] — the zero polynomial
    result = []                                                 # Initialize list to hold derived coefficients
    for i, coeff in enumerate(coefficients[:-1]):               # Loop through all terms except the constant
        power       = degree - i                                # Current power of this term = degree minus index
        new_coeff   = coeff * power                             # Multiply coefficient by its power → power rule
        result.append(new_coeff)                                # Add the new coefficient to the result
    return result                                               # Return derived polynomial coefficients — one degree lower

# Formula: evaluates Σ aₙxⁿ at a given x
# Returns the value of a polynomial given its coefficient list and an x value
# Used internally to evaluate both the original and derived polynomials
def EvalPoly(coefficients, x):
    degree = len(coefficients) - 1                              # Starting degree = highest index
    result = 0                                                  # Initialize accumulator
    for i, coeff in enumerate(coefficients):                    # Loop through each coefficient
        power   = degree - i                                    # Power for this term = degree minus position
        result += coeff * (x ** power)                          # Add coeff * x^power to running total
    return result                                               # Return evaluated polynomial value

# Formula: derivative of polynomial evaluated at x
# Returns the numerical value of the derivative of a polynomial at a given x
# Differentiates symbolically then evaluates at x — exact for polynomials
def DiffPolynomialAt(coefficients, x):
    derived = DiffPolynomial(coefficients)                      # Differentiate symbolically → get derived coefficients
    return EvalPoly(derived, x)                                 # Evaluate the derived polynomial at x → complete d/dx p(x) at x

# Formula: nth derivative of a polynomial  (apply power rule n times)
# Returns the coefficient list of the nth derivative of a polynomial
# Returns [0] once the polynomial has been differentiated to zero
def DiffPolynomialNth(coefficients, n):
    result = coefficients[:]                                    # Start with a copy of the original coefficients
    for _ in range(n):                                          # Apply differentiation n times
        result = DiffPolynomial(result)                         # Differentiate once per iteration
        if result == [0]:                                       # Stop early if polynomial collapsed to zero
            return [0]                                          # All higher derivatives of a constant are zero
    return result                                               # Return nth derivative coefficient list

# Formula: antiderivative — ∫ aₙxⁿ dx = aₙ/(n+1) * x^(n+1) + C
# Returns the symbolic antiderivative of a polynomial as a new coefficient list
# The constant of integration C is omitted — represented as trailing 0
def IntegratePolynomial(coefficients):
    degree = len(coefficients) - 1                              # Degree of the polynomial
    result = []                                                 # Initialize list to hold integrated coefficients
    for i, coeff in enumerate(coefficients):                    # Loop through each term
        power     = degree - i                                  # Current power of this term
        new_power = power + 1                                   # After integration the power increases by 1
        if new_power == 0:                                      # Guard against division by zero — should not occur here
            result.append(0)                                    # Append 0 safely
        else:
            result.append(coeff / new_power)                    # Divide coefficient by new power → integration rule
    result.append(0)                                            # Append 0 for the constant of integration C
    return result                                               # Return integrated polynomial coefficients

# ============================================================
# DIFFERENTIATION RULES — SYMBOLIC EVALUATION
# ============================================================

# Formula: d/dx [f + g] = f' + g'
# Returns the derivative of a sum of two functions at x using the sum rule
# f and g must be callable Python functions
def SumRule(f, g, x, h = 1e-7):
    f_prime = (f(x + h) - f(x - h)) / (2 * h)                 # Differentiate f at x → f'(x)
    g_prime = (g(x + h) - g(x - h)) / (2 * h)                 # Differentiate g at x → g'(x)
    return f_prime + g_prime                                    # Add derivatives → complete (f+g)' = f' + g'

# Formula: d/dx [f - g] = f' - g'
# Returns the derivative of a difference of two functions at x
def DifferenceRule(f, g, x, h = 1e-7):
    f_prime = (f(x + h) - f(x - h)) / (2 * h)                 # Differentiate f at x → f'(x)
    g_prime = (g(x + h) - g(x - h)) / (2 * h)                 # Differentiate g at x → g'(x)
    return f_prime - g_prime                                    # Subtract derivatives → complete (f-g)' = f' - g'

# Formula: d/dx [c * f] = c * f'
# Returns the derivative of a constant multiple of a function at x
def ConstantMultipleRule(c, f, x, h = 1e-7):
    f_prime = (f(x + h) - f(x - h)) / (2 * h)                 # Differentiate f at x → f'(x)
    return c * f_prime                                          # Scale by constant → complete (c*f)' = c*f'

# Formula: d/dx [f * g] = f'g + fg'
# Returns the derivative of a product of two functions at x using the product rule
def ProductRule(f, g, x, h = 1e-7):
    f_val   = f(x)                                              # Evaluate f at x → f(x)
    g_val   = g(x)                                              # Evaluate g at x → g(x)
    f_prime = (f(x + h) - f(x - h)) / (2 * h)                 # Differentiate f → f'(x)
    g_prime = (g(x + h) - g(x - h)) / (2 * h)                 # Differentiate g → g'(x)
    return f_prime * g_val + f_val * g_prime                    # Apply product rule → complete f'g + fg'

# Formula: d/dx [f / g] = (f'g - fg') / g²
# Returns the derivative of a quotient of two functions at x using the quotient rule
# Returns 0 if g(x) is effectively zero to avoid division by zero
def QuotientRule(f, g, x, h = 1e-7):
    f_val   = f(x)                                              # Evaluate f at x
    g_val   = g(x)                                              # Evaluate g at x
    if abs(g_val) < 1e-9:                                       # Guard against division by zero
        return 0                                                # Return 0 safely — quotient undefined here
    f_prime = (f(x + h) - f(x - h)) / (2 * h)                 # Differentiate f → f'(x)
    g_prime = (g(x + h) - g(x - h)) / (2 * h)                 # Differentiate g → g'(x)
    return (f_prime * g_val - f_val * g_prime) / (g_val ** 2)  # Apply quotient rule → complete (f'g - fg') / g²

# Formula: d/dx [f(g(x))] = f'(g(x)) * g'(x)
# Returns the derivative of a composition of two functions at x using the chain rule
def ChainRule(f, g, x, h = 1e-7):
    g_val   = g(x)                                              # Evaluate inner function at x → g(x)
    f_prime = (f(g_val + h) - f(g_val - h)) / (2 * h)          # Differentiate f at g(x) → f'(g(x))
    g_prime = (g(x + h) - g(x - h)) / (2 * h)                  # Differentiate g at x → g'(x)
    return f_prime * g_prime                                    # Multiply → complete f'(g(x)) * g'(x)

# Formula: d/dx [f(g(h(x)))] = f'(g(h(x))) * g'(h(x)) * h'(x)
# Returns the derivative of a triple composition at x using the extended chain rule
# f, g, inner must all be callable Python functions
def ChainRuleTriple(f, g, inner, x, h = 1e-7):
    i_val   = inner(x)                                          # Evaluate innermost function → inner(x)
    g_val   = g(i_val)                                          # Evaluate middle function at inner(x) → g(inner(x))
    f_prime = (f(g_val + h) - f(g_val - h)) / (2 * h)          # Differentiate f at g(inner(x)) → f'(...)
    g_prime = (g(i_val + h) - g(i_val - h)) / (2 * h)          # Differentiate g at inner(x) → g'(inner(x))
    i_prime = (inner(x + h) - inner(x - h)) / (2 * h)          # Differentiate inner at x → inner'(x)
    return f_prime * g_prime * i_prime                          # Multiply all three → complete triple chain rule

# ============================================================
# DERIVATIVES OF STANDARD FUNCTIONS — SYMBOLIC
# ============================================================

# Formula: d/dx [x^n] = n * x^(n-1)
# Returns the derivative of x^n evaluated at x
# Returns 0 for n = 0 since the derivative of a constant is zero
def DiffPower(n, x):
    if n == 0:                                                  # Derivative of x^0 = 1 is zero
        return 0                                                # Return 0 safely
    return n * (x ** (n - 1))                                   # Apply power rule → complete n*x^(n-1)

# Formula: d/dx [e^x] = e^x
# Returns the derivative of e^x at x — it is its own derivative
def DiffExp(x):
    return math.exp(x)                                          # e^x is its own derivative → complete d/dx[e^x] = e^x

# Formula: d/dx [a^x] = a^x * ln(a)
# Returns the derivative of a^x at x
# Returns 0 if a is non-positive to avoid domain errors in log
def DiffExpBase(a, x):
    if a <= 0:                                                  # Guard against log of non-positive base
        return 0                                                # Return 0 safely — undefined
    return (a ** x) * math.log(a)                               # Multiply a^x by ln(a) → complete d/dx[a^x] = a^x*ln(a)

# Formula: d/dx [ln(x)] = 1/x
# Returns the derivative of the natural log at x
# Returns 0 if x is non-positive to avoid domain errors
def DiffLn(x):
    if x <= 0:                                                  # Guard against log of non-positive number
        return 0                                                # Return 0 safely — ln undefined for x ≤ 0
    return 1 / x                                                # Reciprocal of x → complete d/dx[ln(x)] = 1/x

# Formula: d/dx [log_a(x)] = 1 / (x * ln(a))
# Returns the derivative of log base a of x at x
# Returns 0 if x ≤ 0 or a ≤ 0 or a = 1
def DiffLog(a, x):
    if x <= 0 or a <= 0 or a == 1:                             # Guard against domain errors
        return 0                                                # Return 0 safely
    return 1 / (x * math.log(a))                                # Apply log derivative formula → complete 1/(x*ln(a))

# Formula: d/dx [sin(x)] = cos(x)
# Returns the derivative of sin at x in radians
def DiffSin(x):
    return math.cos(x)                                          # Derivative of sin is cos → complete d/dx[sin(x)] = cos(x)

# Formula: d/dx [cos(x)] = -sin(x)
# Returns the derivative of cos at x in radians
def DiffCos(x):
    return -math.sin(x)                                         # Derivative of cos is negative sin → complete d/dx[cos(x)] = -sin(x)

# Formula: d/dx [tan(x)] = sec²(x) = 1 / cos²(x)
# Returns the derivative of tan at x in radians
# Returns 0 if cos(x) is effectively zero — tan is undefined there
def DiffTan(x):
    cos_x = math.cos(x)                                         # Calculate cos(x) first
    if abs(cos_x) < 1e-9:                                       # Guard against division by zero
        return 0                                                # Return 0 safely — tan undefined at this x
    return 1 / (cos_x ** 2)                                     # Reciprocal of cos²(x) → complete d/dx[tan] = sec²(x)

# Formula: d/dx [arcsin(x)] = 1 / sqrt(1 - x²)
# Returns the derivative of arcsin at x
# Returns 0 if x is outside (-1, 1) — arcsin undefined at the endpoints
def DiffArcsin(x):
    if abs(x) >= 1:                                             # Guard against sqrt of negative or zero
        return 0                                                # Return 0 safely — derivative undefined at ±1
    return 1 / math.sqrt(1 - x ** 2)                            # Apply arcsin derivative → complete 1/sqrt(1-x²)

# Formula: d/dx [arccos(x)] = -1 / sqrt(1 - x²)
# Returns the derivative of arccos at x
# Returns 0 if x is outside (-1, 1)
def DiffArccos(x):
    if abs(x) >= 1:                                             # Guard against sqrt of negative or zero
        return 0                                                # Return 0 safely
    return -1 / math.sqrt(1 - x ** 2)                           # Negate arcsin derivative → complete -1/sqrt(1-x²)

# Formula: d/dx [arctan(x)] = 1 / (1 + x²)
# Returns the derivative of arctan at x — defined for all real x
def DiffArctan(x):
    return 1 / (1 + x ** 2)                                     # Reciprocal of (1+x²) → complete d/dx[arctan(x)]

# Formula: d/dx [sinh(x)] = cosh(x)
# Returns the derivative of the hyperbolic sine at x
def DiffSinh(x):
    return math.cosh(x)                                         # Derivative of sinh is cosh → complete d/dx[sinh(x)] = cosh(x)

# Formula: d/dx [cosh(x)] = sinh(x)
# Returns the derivative of the hyperbolic cosine at x
def DiffCosh(x):
    return math.sinh(x)                                         # Derivative of cosh is sinh → complete d/dx[cosh(x)] = sinh(x)

# Formula: d/dx [tanh(x)] = sech²(x) = 1 - tanh²(x)
# Returns the derivative of the hyperbolic tangent at x
def DiffTanh(x):
    return 1 - math.tanh(x) ** 2                                # Apply tanh derivative identity → complete 1 - tanh²(x)

# ============================================================
# IMPLICIT DIFFERENTIATION
# ============================================================

# Formula: dy/dx = -Fx / Fy  where Fx = ∂F/∂x  and  Fy = ∂F/∂y
# Returns dy/dx for an implicit equation F(x, y) = 0 at a given point (x, y)
# F must be a callable accepting two arguments (x, y)
# Returns 0 if Fy is effectively zero — vertical tangent at this point
def ImplicitDerivative(F, x, y, h = 1e-7):
    Fx = (F(x + h, y) - F(x - h, y)) / (2 * h)                # Partial derivative of F with respect to x → ∂F/∂x
    Fy = (F(x, y + h) - F(x, y - h)) / (2 * h)                # Partial derivative of F with respect to y → ∂F/∂y
    if abs(Fy) < 1e-9:                                          # Guard against division by zero — vertical tangent
        return 0                                                # Return 0 safely
    return -Fx / Fy                                             # Apply implicit differentiation formula → complete dy/dx = -Fx/Fy

# Formula: d²y/dx² using implicit differentiation applied twice
# Returns the second implicit derivative at (x, y)
# Uses the first implicit derivative as a callable and differentiates it again numerically
def ImplicitSecondDerivative(F, x, y, h = 1e-5):
    def dydx(xi, yi):                                           # Define dy/dx as a function of (x, y)
        return ImplicitDerivative(F, xi, yi, h)                 # Compute dy/dx at any point
    Fx  = (F(x + h, y) - F(x - h, y)) / (2 * h)               # ∂F/∂x at (x, y)
    Fy  = (F(x, y + h) - F(x, y - h)) / (2 * h)               # ∂F/∂y at (x, y)
    if abs(Fy) < 1e-9:                                          # Guard against division by zero
        return 0                                                # Return 0 safely
    dydx_val = -Fx / Fy                                         # First implicit derivative at (x, y)
    # Estimate d²y/dx² by perturbing x and recomputing dy/dx while updating y via Euler step
    y_plus  = y + dydx_val * h                                  # Approximate y at x+h using first derivative
    y_minus = y - dydx_val * h                                  # Approximate y at x-h using first derivative
    dydx_plus  = dydx(x + h, y_plus)                            # dy/dx at (x+h, y_plus)
    dydx_minus = dydx(x - h, y_minus)                           # dy/dx at (x-h, y_minus)
    return (dydx_plus - dydx_minus) / (2 * h)                   # Central difference of first derivative → complete d²y/dx²

# Formula: tangent slope at a point on an implicit curve = ImplicitDerivative
# Returns the equation of the tangent line to F(x,y)=0 at (x0, y0) as a callable
def ImplicitTangentLine(F, x0, y0, h = 1e-7):
    slope = ImplicitDerivative(F, x0, y0, h)                    # Get slope of tangent → dy/dx at (x0, y0)
    b     = y0 - slope * x0                                     # Compute y-intercept → b = y0 - slope*x0
    return lambda x: slope * x + b                              # Return tangent line as callable → y = slope*x + b

# ============================================================
# LOGARITHMIC DIFFERENTIATION
# ============================================================

# Formula: d/dx [f^g] = f^g * (g' * ln(f) + g * f'/f)
# Returns the derivative of f(x)^g(x) at x using logarithmic differentiation
# f and g must be callable Python functions  — f(x) must be positive at x
# Returns 0 if f(x) is non-positive to avoid domain errors in log
def LogDiff(f, g, x, h = 1e-7):
    f_val   = f(x)                                              # Evaluate f at x
    g_val   = g(x)                                              # Evaluate g at x
    if f_val <= 0:                                              # Guard against log of non-positive value
        return 0                                                # Return 0 safely — logarithmic diff undefined here
    f_prime = (f(x + h) - f(x - h)) / (2 * h)                  # Differentiate f → f'(x)
    g_prime = (g(x + h) - g(x - h)) / (2 * h)                  # Differentiate g → g'(x)
    log_deriv = g_prime * math.log(f_val) + g_val * (f_prime / f_val)  # d/dx[ln(f^g)] = g'*ln(f) + g*f'/f
    return (f_val ** g_val) * log_deriv                         # Multiply f^g by log derivative → complete d/dx[f^g]

# Formula: d/dx [product of n functions] using logarithmic differentiation
# Returns the derivative of the product f1*f2*...*fn at x
# All functions must be callable and positive at x
# Returns 0 if any function evaluates to zero or negative at x
def LogDiffProduct(functions, x, h = 1e-7):
    values  = [f(x) for f in functions]                         # Evaluate all functions at x
    if any(v <= 0 for v in values):                             # Guard — all values must be positive for log
        return 0                                                # Return 0 safely
    product = 1                                                 # Initialize product accumulator
    for v in values:                                            # Multiply all function values together
        product *= v                                            # Build the product f1*f2*...*fn
    log_sum = 0                                                 # Initialize sum of logarithmic derivative terms
    for i, f in enumerate(functions):                           # Loop through each function
        f_prime  = (f(x + h) - f(x - h)) / (2 * h)            # Differentiate this function → f_i'(x)
        log_sum += f_prime / values[i]                          # Add f_i'/f_i to the log derivative sum
    return product * log_sum                                    # Multiply product by sum → complete log diff of product

# ============================================================
# L'HÔPITAL'S RULE
# ============================================================

# Formula: lim f/g as x→a = lim f'/g' as x→a  (when f and g both → 0 or both → ±∞)
# Returns the limit of f(x)/g(x) as x approaches a using L'Hôpital's rule
# Applies the rule up to max_iterations times — returns 0 if it never resolves
# f and g must be callable Python functions
def LHopital(f, g, a, max_iterations = 5, h = 1e-7, tolerance = 1e-9):
    for _ in range(max_iterations):                             # Apply the rule up to max_iterations times
        f_val = f(a)                                            # Evaluate f at the limit point
        g_val = g(a)                                            # Evaluate g at the limit point
        if abs(g_val) > tolerance:                              # If denominator is nonzero we can evaluate directly
            return f_val / g_val                                # Limit exists as a simple ratio → return f/g
        f_prime = lambda x: (f(x + h) - f(x - h)) / (2 * h)   # Define f' as central difference
        g_prime = lambda x: (g(x + h) - g(x - h)) / (2 * h)   # Define g' as central difference
        f = f_prime                                             # Replace f with f' for the next iteration
        g = g_prime                                             # Replace g with g' for the next iteration
    f_val = f(a)                                                # Final attempt after all iterations
    g_val = g(a)                                                # Final denominator check
    if abs(g_val) < tolerance:                                  # Still indeterminate after max iterations
        return 0                                                # Return 0 safely — limit could not be resolved
    return f_val / g_val                                        # Return best available ratio

# Formula: checks if a limit is 0/0 or ∞/∞ indeterminate form
# Returns True if f(a)/g(a) is an indeterminate form at x = a
def IsIndeterminate(f, g, a, tolerance = 1e-6):
    try:
        f_val = abs(f(a))                                       # Evaluate |f(a)|
        g_val = abs(g(a))                                       # Evaluate |g(a)|
        both_zero = f_val < tolerance and g_val < tolerance     # Check 0/0 form
        both_inf  = f_val > 1e10 and g_val > 1e10              # Check ∞/∞ form
        return both_zero or both_inf                            # Indeterminate if either condition holds
    except:
        return False                                            # Return False safely if evaluation fails

# ============================================================
# NEWTON'S METHOD
# ============================================================

# Formula: xₙ₊₁ = xₙ - f(xₙ) / f'(xₙ)
# Returns an approximation of a root of f near x0 using Newton's method
# Iterates up to max_iterations times — stops early if convergence is reached
# Returns x0 unchanged if f'(x) is effectively zero at any step
def NewtonsMethod(f, x0, max_iterations = 100, tolerance = 1e-10, h = 1e-7):
    x = x0                                                      # Start at the initial guess
    for _ in range(max_iterations):                             # Iterate up to max_iterations times
        f_val   = f(x)                                          # Evaluate f at current x
        f_prime = (f(x + h) - f(x - h)) / (2 * h)             # Differentiate f at current x → f'(x)
        if abs(f_prime) < 1e-12:                                # Guard against division by zero — flat tangent
            return x                                            # Return current best guess if derivative is zero
        x_new = x - f_val / f_prime                             # Apply Newton's formula → xₙ₊₁ = xₙ - f/f'
        if abs(x_new - x) < tolerance:                          # Check convergence — stop if change is tiny
            return x_new                                        # Return converged root
        x = x_new                                               # Update x for next iteration
    return x                                                    # Return best approximation after all iterations

# Formula: finds multiple roots by applying Newton's method from multiple starting points
# Returns a list of unique approximate roots of f found by sampling starting points across [a, b]
# Deduplicates roots within the given tolerance
def FindRoots(f, a, b, num_starts = 50, tolerance = 1e-6, h = 1e-7):
    roots   = []                                                # Initialize empty list of found roots
    step    = (b - a) / num_starts                              # Evenly space starting points across [a, b]
    for i in range(num_starts):                                 # Loop through each starting point
        x0   = a + i * step                                     # Calculate this starting position
        root = NewtonsMethod(f, x0, tolerance = tolerance, h = h)  # Apply Newton's method from this start
        if a <= root <= b:                                      # Only keep roots inside the search interval
            duplicate = any(abs(root - r) < tolerance for r in roots)  # Check if this root is already found
            if not duplicate:                                   # Only add genuinely new roots
                roots.append(root)                              # Add unique root to the list
    roots.sort()                                                # Sort roots in ascending order
    return roots                                                # Return list of unique roots

# Formula: order of convergence of Newton's method ≈ 2 for simple roots
# Returns the number of iterations Newton's method needed to converge to a root near x0
# Returns -1 if Newton's method did not converge within max_iterations
def NewtonsConvergenceCount(f, x0, max_iterations = 100, tolerance = 1e-10, h = 1e-7):
    x = x0                                                      # Start at initial guess
    for i in range(max_iterations):                             # Count iterations
        f_val   = f(x)                                          # Evaluate f
        f_prime = (f(x + h) - f(x - h)) / (2 * h)             # Differentiate f
        if abs(f_prime) < 1e-12:                                # Guard against flat tangent
            return -1                                           # Did not converge — return -1
        x_new = x - f_val / f_prime                             # Newton step
        if abs(x_new - x) < tolerance:                          # Converged
            return i + 1                                        # Return iteration count (1-indexed)
        x = x_new
    return -1                                                   # Did not converge within limit → return -1

# ============================================================
# RELATED RATES
# ============================================================

# Formula: dy/dt = (dy/dx) * (dx/dt)  via chain rule
# Returns dy/dt given the derivative dy/dx at x and the rate dx/dt
# This is the standard related rates setup — how fast y changes given how fast x changes
def RelatedRate(dydx, dxdt):
    return dydx * dxdt                                          # Multiply derivatives → complete dy/dt = (dy/dx)*(dx/dt)

# Formula: dA/dt = 2πr * (dr/dt)  for a circle with changing radius
# Returns the rate of change of a circle's area given the rate of change of its radius
def CircleAreaRate(r, drdt):
    return 2 * math.pi * r * drdt                               # Multiply 2πr by dr/dt → complete dA/dt = 2πr*(dr/dt)

# Formula: dV/dt = 4πr² * (dr/dt)  for a sphere with changing radius
# Returns the rate of change of a sphere's volume given the rate of change of its radius
def SphereVolumeRate(r, drdt):
    return 4 * math.pi * r ** 2 * drdt                          # Multiply 4πr² by dr/dt → complete dV/dt = 4πr²*(dr/dt)

# Formula: dV/dt = πr² * (dh/dt)  for a cylinder with fixed radius and changing height
# Returns the rate of change of a cylinder's volume given the rate of change of its height
def CylinderVolumeRate(r, dhdt):
    return math.pi * r ** 2 * dhdt                              # Multiply πr² by dh/dt → complete dV/dt = πr²*(dh/dt)

# Formula: dz/dt via Pythagorean related rate — z² = x² + y²
# Returns dz/dt given x, y, dx/dt, and dy/dt for two legs of a right triangle
# Returns 0 if z is effectively zero to avoid division by zero
def PythagoreanRate(x, y, dxdt, dydt):
    z = math.sqrt(x ** 2 + y ** 2)                              # Calculate hypotenuse → z = sqrt(x²+y²)
    if z < 1e-9:                                                # Guard against division by zero
        return 0                                                # Return 0 safely
    return (x * dxdt + y * dydt) / z                            # Apply related rate formula → complete dz/dt = (x*dx/dt + y*dy/dt)/z

# Formula: shadow rate — ds/dt using similar triangles
# Returns the rate at which a shadow length changes given a person walking away from a light
# person_height = height of the person, light_height = height of the light source
# x = distance from light to person, dxdt = walking speed
# Returns 0 if (light_height - person_height) is zero to avoid division by zero
def ShadowLengthRate(person_height, light_height, x, dxdt):
    denominator = light_height - person_height                  # Difference in heights — determines shadow ratio
    if abs(denominator) < 1e-9:                                 # Guard against division by zero
        return 0                                                # Return 0 safely — no shadow differential
    ratio = person_height / denominator                         # Similar triangles ratio
    return ratio * dxdt                                         # Scale by walking rate → complete ds/dt

# ============================================================
# LINEARIZATION AND DIFFERENTIALS
# ============================================================

# Formula: L(x) = f(a) + f'(a) * (x - a)
# Returns the linear approximation (tangent line) of f at a evaluated at x
# This is the best linear estimate of f near the point a
def Linearization(f, a, x, h = 1e-7):
    f_a     = f(a)                                              # Evaluate f at center point a → f(a)
    f_prime = (f(a + h) - f(a - h)) / (2 * h)                  # Differentiate f at a → f'(a)
    return f_a + f_prime * (x - a)                              # Apply linearization formula → complete L(x) = f(a) + f'(a)*(x-a)

# Formula: dy = f'(x) * dx
# Returns the differential dy — the approximate change in f for a small change dx in x
def Differential(f, x, dx, h = 1e-7):
    f_prime = (f(x + h) - f(x - h)) / (2 * h)                  # Differentiate f at x → f'(x)
    return f_prime * dx                                         # Multiply by dx → complete dy = f'(x)*dx

# Formula: relative error ≈ |dy/y|  where dy = f'(x)*dx
# Returns the relative error in f(x) given an absolute error dx in x
# Returns 0 if f(x) is effectively zero to avoid division by zero
def RelativeError(f, x, dx, h = 1e-7):
    f_val = f(x)                                                # Evaluate f at x → f(x)
    if abs(f_val) < 1e-12:                                      # Guard against division by zero
        return 0                                                # Return 0 safely
    dy = Differential(f, x, dx, h)                              # Calculate differential → dy = f'(x)*dx
    return abs(dy / f_val)                                      # Divide by f(x) → complete relative error = |dy/y|

# Formula: percentage error ≈ |dy/y| * 100
# Returns the percentage error in f(x) given an absolute measurement error dx
def PercentageError(f, x, dx, h = 1e-7):
    return RelativeError(f, x, dx, h) * 100                     # Scale relative error by 100 → complete percentage error

# ============================================================
# HIGHER ORDER AND SPECIAL DERIVATIVES
# ============================================================

# Formula: f^(n)(x) via repeated central difference
# Returns the nth numerical derivative of f at x
# Recursively wraps the central difference — each layer adds one derivative
def NthDerivative(f, x, n, h = 1e-5):
    if n == 0:                                                  # Base case — zeroth derivative is the function itself
        return f(x)                                             # Return f(x) directly
    if n == 1:                                                  # First derivative uses central difference directly
        return (f(x + h) - f(x - h)) / (2 * h)                 # Central difference → f'(x)
    inner = lambda t: NthDerivative(f, t, n - 1, h)             # Wrap (n-1)th derivative as a new callable
    return (inner(x + h) - inner(x - h)) / (2 * h)             # Differentiate the wrapper → complete f^(n)(x)

# Formula: mixed partial ∂²f / ∂x∂y ≈ [f(x+h,y+h) - f(x+h,y-h) - f(x-h,y+h) + f(x-h,y-h)] / 4h²
# Returns the mixed second partial derivative of f at (x, y)
# f must accept two arguments (x, y)
def MixedPartial(f, x, y, h = 1e-5):
    try:
        return (f(x+h, y+h) - f(x+h, y-h) - f(x-h, y+h) + f(x-h, y-h)) / (4 * h ** 2)  # Four-point mixed partial formula
    except:
        return 0                                                # Return 0 safely if f is undefined nearby

# Formula: Jacobian matrix of a vector function F: Rⁿ → Rᵐ evaluated at a point
# Returns the Jacobian as a 2D list — rows are output components, columns are input variables
# F must be a list of callables each accepting a list of values
# point must be a list of coordinate values
def Jacobian(F, point, h = 1e-7):
    m      = len(F)                                             # Number of output components
    n      = len(point)                                         # Number of input variables
    J      = [[0.0] * n for _ in range(m)]                     # Initialize m×n Jacobian matrix with zeros
    for i in range(m):                                          # Loop through each output component
        for j in range(n):                                      # Loop through each input variable
            point_plus  = point[:]                              # Copy point for forward perturbation
            point_minus = point[:]                              # Copy point for backward perturbation
            point_plus[j]  += h                                 # Perturb jth variable forward
            point_minus[j] -= h                                 # Perturb jth variable backward
            J[i][j] = (F[i](point_plus) - F[i](point_minus)) / (2 * h)  # Central difference → ∂Fᵢ/∂xⱼ
    return J                                                    # Return completed Jacobian matrix

# Formula: Hessian matrix — Hᵢⱼ = ∂²f / ∂xᵢ∂xⱼ
# Returns the Hessian matrix of a scalar function f at a given point as a 2D list
# f must accept a list of coordinate values — point must be a list
def Hessian(f, point, h = 1e-5):
    n = len(point)                                              # Number of variables
    H = [[0.0] * n for _ in range(n)]                          # Initialize n×n Hessian matrix with zeros
    for i in range(n):                                          # Loop through rows
        for j in range(n):                                      # Loop through columns
            if i == j:                                          # Diagonal — pure second partial ∂²f/∂xᵢ²
                p_plus  = point[:]
                p_minus = point[:]
                p_plus[i]  += h
                p_minus[i] -= h
                H[i][j] = (f(p_plus) - 2*f(point) + f(p_minus)) / (h ** 2)  # Second difference formula
            else:                                               # Off-diagonal — mixed partial ∂²f/∂xᵢ∂xⱼ
                pp = point[:]
                pm = point[:]
                mp = point[:]
                mm = point[:]
                pp[i] += h;  pp[j] += h                        # Both forward
                pm[i] += h;  pm[j] -= h                        # i forward, j backward
                mp[i] -= h;  mp[j] += h                        # i backward, j forward
                mm[i] -= h;  mm[j] -= h                        # Both backward
                H[i][j] = (f(pp) - f(pm) - f(mp) + f(mm)) / (4 * h ** 2)  # Four-point mixed partial
    return H                                                    # Return completed Hessian matrix

# ============================================================
# CURVE SKETCHING UTILITIES
# ============================================================

# Formula: scan [a, b] for sign changes in f'(x) to locate critical points
# Returns a list of approximate critical points of f in the interval [a, b]
# A critical point is where f'(x) ≈ 0 — located by sign change detection
def FindCriticalPoints(f, a, b, steps = 1000, h = 1e-7):
    critical = []                                               # Initialize list of found critical points
    dx       = (b - a) / steps                                  # Step size across the interval
    prev_d   = None                                             # Previous derivative value for sign change detection
    for i in range(steps + 1):                                  # Loop through all sample points
        xi = a + i * dx                                         # Current x value
        try:
            di = (f(xi + h) - f(xi - h)) / (2 * h)             # Derivative at xi
        except:
            prev_d = None                                       # Reset if function undefined here
            continue
        if prev_d is not None and prev_d * di < 0:             # Sign change detected → critical point between xi-dx and xi
            mid = xi - dx / 2                                   # Approximate critical point as midpoint
            refined = NewtonsMethod(lambda x: (f(x+h)-f(x-h))/(2*h), mid, h=h)  # Refine with Newton's on f'
            if a <= refined <= b:                               # Keep only points inside the interval
                duplicate = any(abs(refined - c) < 1e-6 for c in critical)
                if not duplicate:
                    critical.append(refined)                    # Add unique critical point
        prev_d = di                                             # Update previous derivative
    critical.sort()                                             # Sort in ascending order
    return critical                                             # Return all found critical points

# Formula: scan [a, b] for sign changes in f''(x) to locate inflection points
# Returns a list of approximate inflection points of f in the interval [a, b]
def FindInflectionPoints(f, a, b, steps = 1000, h = 1e-5):
    inflections = []                                            # Initialize list of found inflection points
    dx          = (b - a) / steps                               # Step size
    prev_d2     = None                                          # Previous second derivative value
    for i in range(steps + 1):                                  # Loop through all sample points
        xi = a + i * dx                                         # Current x
        try:
            d2i = (f(xi + h) - 2*f(xi) + f(xi - h)) / (h ** 2)  # Second derivative at xi
        except:
            prev_d2 = None
            continue
        if prev_d2 is not None and prev_d2 * d2i < 0:          # Sign change in f'' → inflection between points
            mid = xi - dx / 2                                   # Approximate inflection as midpoint
            inflections.append(round(mid, 8))                   # Add to list rounded for display
        prev_d2 = d2i                                           # Update previous second derivative
    return inflections                                          # Return all found inflection points

# Formula: classify each critical point using the second derivative test
# Returns a list of (x, classification) tuples for all critical points in [a, b]
# Classification is "minimum", "maximum", or "inconclusive"
def ClassifyCriticalPoints(f, a, b, steps = 1000, h = 1e-5):
    criticals = FindCriticalPoints(f, a, b, steps, h)           # Find all critical points first
    results   = []                                              # Initialize results list
    for xc in criticals:                                        # Loop through each critical point
        d2 = (f(xc + h) - 2*f(xc) + f(xc - h)) / (h ** 2)    # Second derivative at xc
        if d2 > 1e-6:                                           # Positive → concave up → local minimum
            results.append((xc, "minimum"))
        elif d2 < -1e-6:                                        # Negative → concave down → local maximum
            results.append((xc, "maximum"))
        else:                                                   # Near zero → inconclusive
            results.append((xc, "inconclusive"))
    return results                                              # Return list of (x, classification) pairs
