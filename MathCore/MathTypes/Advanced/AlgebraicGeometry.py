import math        # sqrt, pi, log, exp
import itertools   # product, combinations

# Algebraic Geometry works over a field 𝔽.
# Affine varieties: zero sets of polynomials in 𝔽[x₁,...,xₙ].
# Polynomials in 1 variable: lists [a₀, a₁, ..., aₙ] (index = degree), entries are floats.
# Polynomials in 2 variables: dict {(i,j): coeff} representing Σ aᵢⱼ xⁱ yʲ.
# Points are tuples of floats or ints.
# All real/complex computations use float arithmetic with tolerance tol=1e-9.

_TOL = 1e-9

# ============================================================
# INTERNAL HELPERS  (prefixed _ — not part of public API)
# ============================================================

def _poly_eval1(coeffs, x):
    """Evaluate a univariate polynomial at x (Horner's method)."""
    result = 0.0
    for c in reversed(coeffs):
        result = result * x + c
    return result

def _poly_trim1(coeffs):
    p = list(coeffs)
    while len(p) > 1 and abs(p[-1]) < _TOL:
        p.pop()
    return p

def _poly_degree1(coeffs):
    p = _poly_trim1(coeffs)
    return len(p) - 1 if any(abs(c) > _TOL for c in p) else -1

def _poly_add1(f, g):
    n = max(len(f), len(g))
    r = [0.0] * n
    for i, c in enumerate(f): r[i] += c
    for i, c in enumerate(g): r[i] += c
    return _poly_trim1(r)

def _poly_mul1(f, g):
    if not f or not g: return [0.0]
    r = [0.0] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        for j, b in enumerate(g):
            r[i+j] += a * b
    return _poly_trim1(r)

def _poly_divmod1(f, g):
    f, g = list(f), _poly_trim1(list(g))
    if all(abs(c) < _TOL for c in g):
        raise ValueError('Division by zero polynomial')
    q = [0.0] * max(1, len(f) - len(g) + 1)
    r = list(f)
    dg = _poly_degree1(g)
    while _poly_degree1(r) >= dg and _poly_degree1(r) >= 0:
        dr   = _poly_degree1(r)
        coef = r[dr] / g[dg]
        q[dr - dg] = coef
        for k in range(dg + 1):
            r[dr - dg + k] -= coef * g[k]
        r = _poly_trim1(r)
    return _poly_trim1(q), r

def _gcd_poly1(f, g):
    f, g = _poly_trim1(list(f)), _poly_trim1(list(g))
    while any(abs(c) > _TOL for c in g):
        _, r = _poly_divmod1(f, g)
        f, g = g, r
    # Make monic
    if abs(f[-1]) > _TOL:
        lead = f[-1]
        f = [c / lead for c in f]
    return _poly_trim1(f)

def _eval2(poly2, x, y):
    """Evaluate a bivariate polynomial dict at (x, y)."""
    return sum(c * (x**i) * (y**j) for (i, j), c in poly2.items())

# ============================================================
# AFFINE VARIETIES (ZERO SETS)
# ============================================================

# Formula: V(f) = {x ∈ 𝔽 | f(x) = 0} — affine variety of a polynomial
# For univariate polynomials over ℝ, uses numerical root finding
def AffineVariety1D(coeffs, x_range=(-100, 100), n=10000):
    """
    Returns approximate real roots of f in [x_range[0], x_range[1]].
    Uses sign-change detection with n sample points.
    """
    a, b   = x_range
    h      = (b - a) / n
    roots  = []
    prev_x = a; prev_y = _poly_eval1(coeffs, a)
    for i in range(1, n + 1):
        x  = a + i * h
        y  = _poly_eval1(coeffs, x)
        if abs(y) < 1e-8:
            if not roots or abs(x - roots[-1]) > h:
                roots.append(round(x, 8))
        elif prev_y * y < 0:                                  # Sign change → root in (prev_x, x)
            # Bisection
            lo, hi = prev_x, x
            for _ in range(50):
                mid = (lo + hi) / 2
                if _poly_eval1(coeffs, mid) * _poly_eval1(coeffs, lo) <= 0:
                    hi = mid
                else:
                    lo = mid
            r = (lo + hi) / 2
            if not roots or abs(r - roots[-1]) > h:
                roots.append(round(r, 8))
        prev_x, prev_y = x, y
    return roots                                               # V(f) — real root list

# Formula: V(I) — variety of an ideal (intersection of V(fᵢ))
def AffineVarietyOfIdeal(polynomials_list, x_range=(-100,100), n=10000):
    """Intersection of zero sets of multiple univariate polynomials."""
    roots_each = [set(AffineVariety1D(f, x_range, n)) for f in polynomials_list]
    if not roots_each: return []
    common = roots_each[0]
    for rs in roots_each[1:]:
        common = {r for r in common if any(abs(r - s) < 1e-6 for s in rs)}
    return sorted(common)                                      # V(I) = ∩ V(fᵢ)

# Formula: V(f,g) in ℝ² — zero set of two polynomials (intersection of curves)
def AffineVariety2D(poly_f2, poly_g2, x_range=(-10,10), y_range=(-10,10), n=200):
    """
    Approximate intersection points of two bivariate curves in ℝ².
    Grid search + refinement.
    """
    dx = (x_range[1]-x_range[0])/n; dy = (y_range[1]-y_range[0])/n
    points = []
    for i in range(n):
        for j in range(n):
            x = x_range[0] + i*dx; y = y_range[0] + j*dy
            if abs(_eval2(poly_f2, x, y)) < 1e-2 and abs(_eval2(poly_g2, x, y)) < 1e-2:
                # Deduplicate
                if not any(abs(x-p[0])<dx and abs(y-p[1])<dy for p in points):
                    points.append((round(x,4), round(y,4)))
    return points                                              # Approximate V(f,g) in ℝ²

# Formula: Is a point p in the variety V(f)?
def IsOnVariety(p, coeffs_or_poly2):
    if isinstance(coeffs_or_poly2, list):
        val = _poly_eval1(coeffs_or_poly2, p)                 # Univariate case
    else:
        val = _eval2(coeffs_or_poly2, p[0], p[1])             # Bivariate case
    return abs(val) < _TOL                                     # On variety iff f(p) = 0

# ============================================================
# POLYNOMIAL RINGS AND IDEALS
# ============================================================

# Formula: ideal generated by polynomials I = ⟨f₁,...,fₖ⟩
# Returns True if h is in the ideal ⟨f,g⟩ (h = af + bg for some polynomials a,b)
def IsInIdeal(h, generators, x_range=(-50,50), n=5000):
    """
    Checks if h vanishes on V(generators): necessary condition for h ∈ I.
    Uses Nullstellensatz: if h ∈ √I then h vanishes on V(I).
    """
    variety = AffineVarietyOfIdeal(generators, x_range, n)
    return all(abs(_poly_eval1(h, r)) < 1e-6 for r in variety) if variety else True

# Formula: radical of ideal √I — {f | fⁿ ∈ I for some n}
# For principal ideals ⟨f⟩, √I = ⟨squarefree part of f⟩
def RadicalOfPrincipalIdeal(f):
    """Returns the squarefree part of f — the radical of the principal ideal ⟨f⟩."""
    df = PolynomialDerivative(f)                               # f'
    g  = _gcd_poly1(f, df)                                    # gcd(f, f')
    if _poly_degree1(g) == 0:
        return _poly_trim1(f)                                  # Already squarefree
    q, _ = _poly_divmod1(f, g)
    return _poly_trim1(q)                                      # f / gcd(f,f') = squarefree part

# Formula: resultant of f and g — eliminates a variable
# Res(f,g) = leading coeff of f ^(deg g) · Π (f(αᵢ)) over roots αᵢ of g
def Resultant(f, g):
    """
    Computes the resultant of two univariate polynomials via the Sylvester matrix determinant.
    Coefficients are stored ascending (index=degree), but the Sylvester matrix uses
    descending order — this function handles the conversion internally.
    Returns a scalar (the resultant).
    """
    f_asc, g_asc = _poly_trim1(list(f)), _poly_trim1(list(g))
    m, n         = _poly_degree1(f_asc), _poly_degree1(g_asc)
    if m < 0 or n < 0: return 0.0
    size = m + n
    if size == 0: return 1.0
    # Coefficients in DESCENDING degree order for Sylvester matrix
    f_desc = list(reversed(f_asc))                             # high → low degree
    g_desc = list(reversed(g_asc))
    matrix = [[0.0]*size for _ in range(size)]
    # n rows for f (shifted 0..n-1 positions to the right)
    for i in range(n):
        for j, c in enumerate(f_desc):
            if i + j < size:
                matrix[i][i + j] = c
    # m rows for g (shifted 0..m-1 positions to the right)
    for i in range(m):
        for j, c in enumerate(g_desc):
            if i + j < size:
                matrix[n + i][i + j] = c
    # Determinant via Gaussian elimination with partial pivoting
    mat = [row[:] for row in matrix]
    det = 1.0
    for col in range(size):
        pivot = next((row for row in range(col, size) if abs(mat[row][col]) > _TOL), None)
        if pivot is None: return 0.0
        if pivot != col:
            mat[col], mat[pivot] = mat[pivot], mat[col]
            det *= -1
        det *= mat[col][col]
        for row in range(col + 1, size):
            if abs(mat[col][col]) < _TOL: continue
            factor = mat[row][col] / mat[col][col]
            for k in range(col, size):
                mat[row][k] -= factor * mat[col][k]
    return det                                                 # Complete resultant

# Formula: discriminant of f — Res(f, f') / leading_coeff(f)^(n-1)
def Discriminant(f):
    """Discriminant of a univariate polynomial. Zero iff f has a repeated root."""
    f_trimmed = _poly_trim1(list(f))
    df        = PolynomialDerivative(f_trimmed)
    res       = Resultant(f_trimmed, df)
    lead      = f_trimmed[-1]
    n         = _poly_degree1(f_trimmed)
    if abs(lead) < _TOL or n <= 0: return 0.0
    return ((-1)**(n*(n-1)//2) * res) / lead                  # Complete discriminant

# ============================================================
# POLYNOMIAL OPERATIONS
# ============================================================

# Formula: (f+g)(x) — polynomial addition
def PolyAdd(f, g):
    return _poly_add1(f, g)                                   # Complete f + g

# Formula: (f·g)(x) — polynomial multiplication
def PolyMul(f, g):
    return _poly_mul1(f, g)                                   # Complete f · g

# Formula: polynomial division f = q·g + r
def PolyDivMod(f, g):
    return _poly_divmod1(f, g)                                 # (quotient, remainder)

# Formula: gcd(f,g) — greatest common divisor via Euclidean algorithm
def PolyGCD(f, g):
    return _gcd_poly1(f, g)                                   # Monic GCD

# Formula: lcm(f,g) = f·g / gcd(f,g)
def PolyLCM(f, g):
    gcd     = _gcd_poly1(f, g)
    product = _poly_mul1(f, g)
    lcm, _  = _poly_divmod1(product, gcd)
    return _poly_trim1(lcm)                                    # Complete LCM

# Formula: f(x) evaluated at x
def PolyEval(f, x):
    return _poly_eval1(f, x)                                  # Horner evaluation

# Formula: f'(x) — polynomial derivative
def PolynomialDerivative(f):
    if len(f) <= 1: return [0.0]
    return [(i+1)*f[i+1] for i in range(len(f)-1)]            # Differentiate term by term

# Formula: polynomial degree
def PolyDegree(f):
    return _poly_degree1(f)                                    # Degree of polynomial

# Formula: Is f square-free? — True iff gcd(f,f') = 1
def IsSquareFree(f):
    df  = PolynomialDerivative(f)
    g   = _gcd_poly1(f, df)
    return _poly_degree1(g) == 0                               # Square-free iff gcd(f,f')=const

# Formula: monic polynomial — divide by leading coefficient
def MakeMonic(f):
    f = _poly_trim1(list(f))
    if not f or abs(f[-1]) < _TOL: return f
    lead = f[-1]
    return [c / lead for c in f]                               # All coefficients / leading coeff

# Formula: homogeneous polynomial — all terms have the same degree d
def IsHomogeneous(poly2, d):
    return all(i+j == d for (i,j) in poly2 if abs(poly2[(i,j)]) > _TOL)  # Each term degree = d

# ============================================================
# CURVES IN ℝ²
# ============================================================

# Formula: tangent line to a curve f(x,y)=0 at a smooth point (x₀,y₀)
# Using implicit differentiation: fₓ·(x-x₀) + fᵧ·(y-y₀) = 0
def TangentLineImplicit(poly_f2, x0, y0, h=1e-6):
    fx = (_eval2(poly_f2, x0+h, y0) - _eval2(poly_f2, x0-h, y0)) / (2*h)
    fy = (_eval2(poly_f2, x0, y0+h) - _eval2(poly_f2, x0, y0-h)) / (2*h)
    return fx, fy, fx*x0 + fy*y0                              # (fx, fy, c) for fx·x + fy·y = c

# Formula: multiplicity of a root x₀ — number of times (x-x₀) divides f
def RootMultiplicity(f, x0, tol=1e-6):
    r = list(f); mult = 0
    while abs(_poly_eval1(r, x0)) < tol and _poly_degree1(r) > 0:
        q, _ = _poly_divmod1(r, [-x0, 1.0])                   # Divide by (x-x0)
        r    = _poly_trim1(q)
        mult += 1
    return mult                                                # Complete multiplicity

# Formula: smooth point on a curve — gradient ≠ 0 at the point
def IsSmoothPoint(poly_f2, x, y, h=1e-6):
    fx = (_eval2(poly_f2, x+h, y) - _eval2(poly_f2, x-h, y)) / (2*h)
    fy = (_eval2(poly_f2, x, y+h) - _eval2(poly_f2, x, y-h)) / (2*h)
    return math.sqrt(fx**2 + fy**2) > 1e-6                    # Smooth iff ∇f ≠ 0

# Formula: singular point — gradient = 0 at a point on the curve
def IsSingularPoint(poly_f2, x, y, h=1e-6):
    return not IsSmoothPoint(poly_f2, x, y, h)                 # Singular iff ∇f = 0

# Formula: genus of a smooth projective plane curve of degree d
# g = (d-1)(d-2)/2
def PlaneCurveGenus(degree):
    if degree < 1: return 0
    return (degree - 1) * (degree - 2) // 2                   # g = (d-1)(d-2)/2

# Formula: Bezout's theorem — number of intersection points of curves of degrees d1, d2
def BezoutNumber(d1, d2):
    return d1 * d2                                             # |V(f) ∩ V(g)| = d1·d2 (counted with mult)

# Formula: arithmetic genus of a curve via Hilbert polynomial
def ArithmeticGenus(degree):
    return PlaneCurveGenus(degree)                             # For smooth plane curves

# ============================================================
# PROJECTIVE GEOMETRY
# ============================================================

# Projective point in ℙ²: [x:y:z] represented as tuple (x,y,z) up to scaling

# Formula: homogenise an affine polynomial f(x,y) → F(X,Y,Z) of degree d
# F(X,Y,Z) = Z^d · f(X/Z, Y/Z)
def Homogenise(poly2, degree):
    """Returns the homogeneous version as a new poly2 dict with homogeneous coordinates."""
    homo = {}
    for (i, j), c in poly2.items():
        k = degree - i - j                                     # Z exponent for total degree d
        if k >= 0:
            homo[(i, j, k)] = c
    return homo                                                # {(i,j,k): coeff} with i+j+k=d

# Formula: dehomogenise F(X,Y,Z) → f(x,y) by setting Z=1
def Dehomogenise(homo_poly):
    return {(i, j): c for (i, j, k), c in homo_poly.items()}  # Set Z=1 → drop k exponent

# Formula: projective equivalence — [x₁:y₁:z₁] ~ [x₂:y₂:z₂] iff proportional
def ProjectiveEquivalent(p1, p2, tol=1e-9):
    x1,y1,z1 = p1; x2,y2,z2 = p2
    # Cross-product must be zero for proportionality
    return (abs(x1*y2 - x2*y1) < tol and
            abs(y1*z2 - y2*z1) < tol and
            abs(z1*x2 - z2*x1) < tol)                         # Projective equivalence check

# Formula: point at infinity of a projective curve — points with z=0
def PointsAtInfinity(poly2, degree, tol=1e-6):
    """Returns projective points [x:y:0] on the projectivisation of f."""
    homo = Homogenise(poly2, degree)
    # Set z=0 in homogenised version
    z0_poly = {}
    for (i, j, k), c in homo.items():
        if k == 0:
            z0_poly[(i, j)] = z0_poly.get((i, j), 0) + c
    # Find roots [x:y:0] of this degree-d homogeneous polynomial in x,y
    # Parametrise: y=1, find x roots (then also check y=0 case)
    result = []
    if z0_poly:
        univar = {}
        for (i, j), c in z0_poly.items():
            univar[i] = univar.get(i, 0) + c  # Set y=1
        max_deg = max(univar) if univar else 0
        coeffs  = [univar.get(i, 0) for i in range(max_deg+1)]
        roots   = AffineVariety1D(coeffs)
        result  = [(r, 1, 0) for r in roots]
    return result                                              # Points at infinity [x:1:0]

# Formula: cross-ratio of four collinear points (λ₁,λ₂,λ₃,λ₄)
# (λ₁,λ₂;λ₃,λ₄) = (λ₃-λ₁)(λ₄-λ₂) / ((λ₃-λ₂)(λ₄-λ₁))
def CrossRatio(l1, l2, l3, l4):
    num = (l3-l1) * (l4-l2)
    den = (l3-l2) * (l4-l1)
    if abs(den) < _TOL: return float('inf')
    return num / den                                           # Complete cross-ratio

# ============================================================
# ELLIPTIC CURVES
# ============================================================

# Short Weierstrass form: y² = x³ + ax + b  (characteristic ≠ 2,3)
# Points are (x, y) pairs or the string 'O' (point at infinity / identity)

# Formula: discriminant Δ = −16(4a³ + 27b²) — curve is non-singular iff Δ ≠ 0
def EllipticCurveDiscriminant(a, b):
    return -16 * (4*a**3 + 27*b**2)                           # Δ = −16(4a³+27b²)

# Formula: j-invariant j = −1728·(4a)³ / Δ
def JInvariant(a, b):
    delta = EllipticCurveDiscriminant(a, b)
    if abs(delta) < _TOL: return float('inf')                  # Singular curve
    return -1728 * (4*a)**3 / delta                            # j = 1728·4a³/Δ (standard form)

# Formula: Is a point P=(x,y) on the elliptic curve y²=x³+ax+b?
def IsOnEllipticCurve(P, a, b, tol=1e-6):
    if P == 'O': return True                                   # Identity is always on the curve
    x, y = P
    return abs(y**2 - (x**3 + a*x + b)) < tol                 # y² = x³+ax+b

# Formula: negation of a point — −(x,y) = (x,−y)
def EllipticNeg(P):
    if P == 'O': return 'O'
    return (P[0], -P[1])                                      # Reflect over x-axis

# Formula: point addition on elliptic curve y²=x³+ax+b
def EllipticAdd(P, Q, a, b, tol=1e-6):
    if P == 'O': return Q                                      # Identity: O+Q=Q
    if Q == 'O': return P                                      # Identity: P+O=P
    x1,y1 = P; x2,y2 = Q
    if abs(x1-x2) < tol and abs(y1+y2) < tol:
        return 'O'                                             # P+(-P)=O
    if abs(x1-x2) < tol and abs(y1-y2) < tol:                 # P=Q → doubling
        if abs(y1) < tol: return 'O'
        m = (3*x1**2 + a) / (2*y1)
    else:                                                      # General addition
        if abs(x2-x1) < tol: return 'O'
        m = (y2-y1) / (x2-x1)
    x3 = m**2 - x1 - x2
    y3 = m*(x1-x3) - y1
    return (x3, y3)                                            # Complete elliptic curve addition

# Formula: scalar multiplication [n]P = P+P+...+P (n times) via double-and-add
def EllipticMul(n, P, a, b):
    if n == 0: return 'O'
    if n < 0:  return EllipticMul(-n, EllipticNeg(P), a, b)
    result = 'O'; addend = P
    while n:
        if n % 2 == 1: result = EllipticAdd(result, addend, a, b)
        addend = EllipticAdd(addend, addend, a, b)
        n //= 2
    return result                                              # Complete double-and-add

# Formula: order of a point P — smallest n>0 with [n]P = O
def EllipticPointOrder(P, a, b, max_n=1000):
    Q = P
    for n in range(1, max_n+1):
        if Q == 'O': return n
        Q = EllipticAdd(Q, P, a, b)
    return None                                                # Order not found in range

# Formula: points on an elliptic curve over 𝔽ₚ (small prime p)
def EllipticCurvePoints_Fp(a, b, p):
    points = ['O']                                             # Include point at infinity
    for x in range(p):
        rhs = (x**3 + a*x + b) % p
        for y in range(p):
            if (y*y) % p == rhs:
                points.append((x, y))
    return points                                              # All points on E(𝔽ₚ)

# Formula: Hasse's theorem — #E(𝔽ₚ) is in [p+1−2√p, p+1+2√p]
def HasseInterval(p):
    bound = int(2 * math.sqrt(p))
    return (p + 1 - bound, p + 1 + bound)                     # Hasse bound interval

# ============================================================
# SINGULARITIES
# ============================================================

# Formula: singular locus of f — points where f = fₓ = fᵧ = 0
def SingularLocus(poly_f2, x_range=(-10,10), y_range=(-10,10), n=200, h=1e-5):
    """Returns approximate singular points of f(x,y)=0."""
    singular = []
    dx = (x_range[1]-x_range[0])/n; dy = (y_range[1]-y_range[0])/n
    for i in range(n):
        for j in range(n):
            x = x_range[0]+i*dx; y = y_range[0]+j*dy
            fval = _eval2(poly_f2, x, y)
            fx   = (_eval2(poly_f2, x+h, y) - _eval2(poly_f2, x-h, y)) / (2*h)
            fy   = (_eval2(poly_f2, x, y+h) - _eval2(poly_f2, x, y-h)) / (2*h)
            if abs(fval)<1e-2 and abs(fx)<1e-2 and abs(fy)<1e-2:
                if not any(abs(x-p[0])<dx and abs(y-p[1])<dy for p in singular):
                    singular.append((round(x,4), round(y,4)))
    return singular                                            # f = fₓ = fᵧ = 0

# Formula: node — isolated singular point where two smooth branches cross
def IsNodeSingularity(poly_f2, x0, y0, h=1e-5):
    """True if (x0,y0) is a node: Hessian has rank 2 (non-zero determinant)."""
    fxx = (_eval2(poly_f2,x0+h,y0)-2*_eval2(poly_f2,x0,y0)+_eval2(poly_f2,x0-h,y0)) / h**2
    fyy = (_eval2(poly_f2,x0,y0+h)-2*_eval2(poly_f2,x0,y0)+_eval2(poly_f2,x0,y0-h)) / h**2
    fxy = (_eval2(poly_f2,x0+h,y0+h)-_eval2(poly_f2,x0+h,y0-h)
           -_eval2(poly_f2,x0-h,y0+h)+_eval2(poly_f2,x0-h,y0-h)) / (4*h**2)
    hess_det = fxx*fyy - fxy**2
    return hess_det > 1e-6                                    # Node iff Hessian det > 0

# Formula: cusp — singular point where both branches have same tangent
def IsCuspSingularity(poly_f2, x0, y0, h=1e-5):
    """True if (x0,y0) appears to be a cusp: Hessian determinant ≤ 0."""
    fxx = (_eval2(poly_f2,x0+h,y0)-2*_eval2(poly_f2,x0,y0)+_eval2(poly_f2,x0-h,y0)) / h**2
    fyy = (_eval2(poly_f2,x0,y0+h)-2*_eval2(poly_f2,x0,y0)+_eval2(poly_f2,x0,y0-h)) / h**2
    fxy = (_eval2(poly_f2,x0+h,y0+h)-_eval2(poly_f2,x0+h,y0-h)
           -_eval2(poly_f2,x0-h,y0+h)+_eval2(poly_f2,x0-h,y0-h)) / (4*h**2)
    hess_det = fxx*fyy - fxy**2
    return hess_det <= 1e-6                                   # Cusp iff Hessian det ≤ 0

# Formula: delta-invariant δ of a singularity — correction to genus
# For a node: δ = 1; for an ordinary cusp: δ = 1 (same)
def DeltaInvariant(singularity_type):
    table = {'node': 1, 'cusp': 1, 'tacnode': 2, 'triple_point': 3}
    return table.get(singularity_type, None)                   # δ by singularity type

# ============================================================
# INTERSECTION THEORY
# ============================================================

# Formula: intersection number of two curves at a point (x₀,y₀)
# Approx: order of vanishing of g|_{f=0} at the point
def IntersectionMultiplicity(f_poly2, g_poly2, x0, y0, h=1e-5, n=10):
    """
    Approximates the intersection multiplicity of f and g at (x0,y0).
    Uses root multiplicity of g along f near the point.
    """
    # Restrict g to the tangent line through (x0,y0) on f
    fx = (_eval2(f_poly2, x0+h, y0) - _eval2(f_poly2, x0-h, y0)) / (2*h)
    fy = (_eval2(f_poly2, x0, y0+h) - _eval2(f_poly2, x0, y0-h)) / (2*h)
    if abs(fx) < 1e-10 and abs(fy) < 1e-10:
        return 2                                               # Singular point → mult ≥ 2
    # Count near-coincident roots of g on short segments through (x0,y0)
    count = 0
    for direction in range(n):
        angle = direction * math.pi / n
        dx, dy = math.cos(angle), math.sin(angle)
        for t in [-h*0.5, h*0.5]:
            val = _eval2(g_poly2, x0+t*dx, y0+t*dy)
            if abs(val) < 1e-3: count += 1
    return max(1, count // (2*n) + 1)                         # Approximate multiplicity

# Formula: genus-degree formula with singularities
# g = (d-1)(d-2)/2 - Σ δₚ  (over all singular points)
def GeometricGenus(degree, delta_invariants_sum):
    arith = PlaneCurveGenus(degree)                            # Arithmetic genus
    return max(0, arith - delta_invariants_sum)                # g_geom = g_arith − Σδₚ

# ============================================================
# ALGEBRAIC MAPS AND MORPHISMS
# ============================================================

# Formula: polynomial map φ: ℝ → ℝ given by a polynomial
def PolyMap(f, values):
    return [_poly_eval1(f, x) for x in values]                # φ(x) = f(x) for each x

# Formula: Frobenius endomorphism (over 𝔽ₚ) — x → x^p
def FrobeniusEndomorphism(x, p):
    return pow(int(x), p) % p if isinstance(x, int) else x**p  # φ_p(x) = x^p

# Formula: pullback of a function f by a map φ: V→W is f∘φ
def Pullback(f_values, phi_values):
    """Returns the pullback f∘φ as a list of values."""
    return [f_values[phi_v] if phi_v in f_values else None
            for phi_v in phi_values]                           # (φ*f)(x) = f(φ(x))

# Formula: dominant map — image is dense in the target variety
# For finite sets: dominant iff the image generates the whole target (surjective)
def IsDominant(phi, source, target, tol=1e-6):
    image = set(phi(x) for x in source)
    return len(image) >= len(target)                           # Image fills target → dominant

# Formula: birational equivalence — two varieties are birationally equivalent iff
# they have isomorphic function fields; equivalently, there exist inverse rational maps
def IsBirationallyEquivalent(genus1, genus2):
    return genus1 == genus2                                    # Same genus → birationally equiv (curves)

# ============================================================
# HILBERT FUNCTION AND DIMENSION
# ============================================================

# Formula: Hilbert function H(d) = dim(R_d/I_d)
# For a projective variety, counts degree-d monomials not in I
def HilbertFunction(variety_degree, d):
    """
    Hilbert function for a smooth projective curve of given degree.
    H(d) = d·(variety_degree) - (variety_degree - 1)(variety_degree - 2)/2 + 1 - g
    (Riemann-Roch approximation for large d)
    """
    g = PlaneCurveGenus(variety_degree)
    if d < 0: return 0
    if d == 0: return 1                                        # Only constants
    return max(0, d * variety_degree - g + 1)                  # Riemann-Roch: h⁰(𝒪(d)) = d·deg + 1 - g

# Formula: Hilbert polynomial — eventually equals Hilbert function
# P(d) = deg(X)·d^(dim X)/dim(X)! + lower order terms
def HilbertPolynomial(degree, dim=1):
    """
    Hilbert polynomial for a projective variety of given degree and dimension.
    Returns the polynomial as coefficients [a₀, a₁, ..., aₙ].
    For a curve (dim=1): P(d) = degree·d + 1 - genus.
    """
    g = PlaneCurveGenus(degree) if dim == 1 else 0
    if dim == 1:
        return [1 - g, degree]                                 # P(d) = degree·d + (1-g)
    if dim == 2:
        return [1, degree, degree*(degree-1)//2]               # P(d) for surface
    return [1] + [0]*dim                                       # Fallback

# Formula: arithmetic genus of a projective variety (from Hilbert polynomial)
def ArithmeticGenusFromHilbert(coeffs):
    """Arithmetic genus = 1 - P(0) where P is the Hilbert polynomial."""
    return 1 - coeffs[0]                                       # g_a = 1 - P(0)

# Formula: dimension of a variety — Krull dimension of its coordinate ring
def KrullDimension(n_vars, n_generators):
    """
    Estimates the Krull dimension of the coordinate ring 𝔽[x₁,...,xₙ]/(f₁,...,fₖ).
    By dimension theory: dim = n - k (for a complete intersection).
    """
    return max(0, n_vars - n_generators)                       # dim = n - k (complete intersection)

# Formula: degree of a variety — number of intersection points with a generic linear space
def VarietyDegree(poly_degree, dim=1):
    return poly_degree                                         # Degree of a hypersurface = polynomial degree

# ============================================================
# COMMON ALGEBRAIC CURVES
# ============================================================

# Returns the polynomial defining a conic (degree-2 curve) from 6 coefficients
# ax² + bxy + cy² + dx + ey + f = 0
def ConicPoly(a, b, c, d, e, f):
    poly = {}
    if a: poly[(2,0)] = a
    if b: poly[(1,1)] = b
    if c: poly[(0,2)] = c
    if d: poly[(1,0)] = d
    if e: poly[(0,1)] = e
    if f: poly[(0,0)] = f
    return poly                                                # Conic as bivariate poly dict

# Formula: discriminant of a conic B² - 4AC
def ConicDiscriminant(a, b, c):
    return b**2 - 4*a*c                                       # B²-4AC: <0 ellipse, =0 parabola, >0 hyperbola

# Formula: classify a conic
def ClassifyConic(a, b, c):
    disc = ConicDiscriminant(a, b, c)
    if abs(disc) < _TOL: return 'parabola'
    if disc < 0: return 'ellipse (or circle)'
    return 'hyperbola'                                        # Complete conic classification

# Cubic curve y² = x³ + ax + b (Weierstrass form) as a poly dict
def EllipticCurvePoly(a, b):
    return {(0,2):1, (3,0):-1, (1,0):-a, (0,0):-b}           # y²-x³-ax-b=0

# Nodal cubic: y² = x²(x+1) — a cubic with a node at origin
def NodalCubic():
    return {(0,2):1, (3,0):-1, (2,0):-1}                     # y²-x³-x²=0

# Cuspidal cubic: y² = x³ — a cubic with a cusp at origin
def CuspidalCubic():
    return {(0,2):1, (3,0):-1}                                # y²-x³=0

# Fermat curve: x^n + y^n = 1 → as polynomial dict
def FermatCurve(n):
    return {(n,0):1, (0,n):1, (0,0):-1}                      # xⁿ+yⁿ-1=0
