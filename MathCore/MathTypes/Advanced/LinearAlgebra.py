import math  # sqrt, acos, pi, cos, sin, fabs

# Matrices are represented as lists of lists in row-major order:
#   [[row0_col0, row0_col1, ...], [row1_col0, ...], ...]
# Vectors are plain lists: [x, y, z, ...]
# All functions work with floats; integer inputs are accepted and auto-cast.

# ============================================================
# INTERNAL HELPERS  (prefixed _ — not part of public API)
# ============================================================

def _rows(M):
    return len(M)

def _cols(M):
    return len(M[0]) if M else 0

def _ident(n):
    """Return the n×n identity matrix."""
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

def _copy(M):
    """Return a deep copy of a matrix."""
    return [[float(M[i][j]) for j in range(_cols(M))] for i in range(_rows(M))]

def _submatrix(M, row, col):
    """Return M with the given row and column removed — used for cofactor expansion."""
    return [[M[i][j] for j in range(_cols(M)) if j != col]
            for i in range(_rows(M)) if i != row]

# ============================================================
# VECTORS
# ============================================================

# Formula: a + b  — component-wise addition of two vectors
# Returns a new vector of the same length; raises ValueError if lengths differ
def VectorAdd(a, b):
    if len(a) != len(b):                                        # Dimensions must match for addition
        raise ValueError('Vectors must have the same length')
    return [a[i] + b[i] for i in range(len(a))]                # Add each component → complete a + b

# Formula: a − b  — component-wise subtraction
# Returns a new vector; raises ValueError if lengths differ
def VectorSubtract(a, b):
    if len(a) != len(b):
        raise ValueError('Vectors must have the same length')
    return [a[i] - b[i] for i in range(len(a))]                # Subtract each component → complete a − b

# Formula: c · a  — multiply every component of a by scalar c
# Returns a new scaled vector
def VectorScale(c, a):
    return [c * a[i] for i in range(len(a))]                   # Scale each component → complete c·a

# Formula: ‖a‖  =  √(Σaᵢ²)  — Euclidean (L2) norm of a vector
# Returns a non-negative float
def VectorMagnitude(a):
    return math.sqrt(sum(x ** 2 for x in a))                   # Square-root of sum of squares → ‖a‖

# Formula: â  =  a / ‖a‖  — unit vector in the direction of a
# Returns a vector with magnitude 1; raises ValueError if a is the zero vector
def VectorNormalize(a):
    mag = VectorMagnitude(a)
    if mag == 0:
        raise ValueError('Cannot normalize the zero vector')
    return [x / mag for x in a]                                 # Divide each component by magnitude → â

# Formula: a · b  =  Σ aᵢbᵢ  — scalar (inner) product of two vectors
# Returns a float; raises ValueError if lengths differ
def DotProduct(a, b):
    if len(a) != len(b):
        raise ValueError('Vectors must have the same length')
    return sum(a[i] * b[i] for i in range(len(a)))             # Sum of component products → a · b

# Formula: a × b  — cross product of two 3-vectors (undefined for other dimensions)
# Returns a 3-vector perpendicular to both a and b
def CrossProduct(a, b):
    if len(a) != 3 or len(b) != 3:
        raise ValueError('Cross product is only defined for 3-dimensional vectors')
    return [
        a[1] * b[2] - a[2] * b[1],                             # i component
        a[2] * b[0] - a[0] * b[2],                             # j component
        a[0] * b[1] - a[1] * b[0],                             # k component
    ]                                                           # Complete a × b

# Formula: a × b = ‖a‖‖b‖sin(θ)  →  θ = arccos(a·b / (‖a‖‖b‖))
# Returns the angle between a and b in degrees; 0 for parallel, 90 for orthogonal
def AngleBetween(a, b):
    dot   = DotProduct(a, b)
    mag_a = VectorMagnitude(a)
    mag_b = VectorMagnitude(b)
    if mag_a == 0 or mag_b == 0:
        raise ValueError('Cannot compute angle with a zero vector')
    cosine = dot / (mag_a * mag_b)
    cosine = max(-1.0, min(1.0, cosine))                        # Clamp for floating-point safety
    return math.degrees(math.acos(cosine))                      # Complete arccos → angle in degrees

# Formula: a · b = 0  →  orthogonal
# Returns True if the dot product of a and b is zero (within floating-point tolerance)
def AreOrthogonal(a, b, tol=1e-9):
    return abs(DotProduct(a, b)) < tol                          # Zero dot product → orthogonal

# Formula: proj_b(a)  =  (a·b / b·b) · b  — projection of a onto b
# Returns the vector projection of a onto b
def VectorProjection(a, b):
    bb = DotProduct(b, b)
    if bb == 0:
        raise ValueError('Cannot project onto the zero vector')
    scalar = DotProduct(a, b) / bb                              # Scalar coefficient of b
    return VectorScale(scalar, b)                               # Scale b → complete projection

# Formula: scalar projection  s  =  a·b / ‖b‖  — signed length of projection
# Returns a float (positive if same direction as b, negative if opposite)
def ScalarProjection(a, b):
    mag_b = VectorMagnitude(b)
    if mag_b == 0:
        raise ValueError('Cannot project onto the zero vector')
    return DotProduct(a, b) / mag_b                             # Complete scalar projection

# Formula: a⊥  =  a − proj_b(a)  — rejection of a from b (component of a ⊥ to b)
# Returns the component of a perpendicular to b
def VectorRejection(a, b):
    proj = VectorProjection(a, b)
    return VectorSubtract(a, proj)                              # a minus its projection onto b

# Formula: p  =  a · (b × c)  — scalar triple product (volume of parallelepiped)
# Returns a float; only defined for 3-vectors
def ScalarTripleProduct(a, b, c):
    return DotProduct(a, CrossProduct(b, c))                    # a · (b × c)

# Formula: a × (b × c)  — vector triple product
# Returns a 3-vector; uses BAC-CAB identity: b(a·c) − c(a·b)
def VectorTripleProduct(a, b, c):
    return VectorSubtract(
        VectorScale(DotProduct(a, c), b),                       # b(a·c)
        VectorScale(DotProduct(a, b), c),                       # c(a·b)
    )                                                           # Complete BAC-CAB

# Formula: ‖a − b‖  — Euclidean distance between two points (as vectors)
def VectorDistance(a, b):
    return VectorMagnitude(VectorSubtract(a, b))               # Distance = magnitude of difference

# Formula: Cauchy-Schwarz:  |a·b| ≤ ‖a‖ · ‖b‖
# Returns (lhs, rhs, holds) — both sides and whether the inequality is satisfied
def CauchySchwarz(a, b):
    lhs = abs(DotProduct(a, b))
    rhs = VectorMagnitude(a) * VectorMagnitude(b)
    return lhs, rhs, lhs <= rhs + 1e-9                         # True whenever lhs ≤ rhs

# Formula: Triangle inequality:  ‖a + b‖ ≤ ‖a‖ + ‖b‖
# Returns (lhs, rhs, holds)
def TriangleInequality(a, b):
    lhs = VectorMagnitude(VectorAdd(a, b))
    rhs = VectorMagnitude(a) + VectorMagnitude(b)
    return lhs, rhs, lhs <= rhs + 1e-9

# ============================================================
# MATRIX OPERATIONS
# ============================================================

# Formula: A + B  — element-wise matrix addition
# Returns a new matrix; raises ValueError if dimensions differ
def MatrixAdd(A, B):
    if _rows(A) != _rows(B) or _cols(A) != _cols(B):
        raise ValueError('Matrices must have identical dimensions for addition')
    return [[A[i][j] + B[i][j] for j in range(_cols(A))] for i in range(_rows(A))]

# Formula: A − B  — element-wise matrix subtraction
def MatrixSubtract(A, B):
    if _rows(A) != _rows(B) or _cols(A) != _cols(B):
        raise ValueError('Matrices must have identical dimensions for subtraction')
    return [[A[i][j] - B[i][j] for j in range(_cols(A))] for i in range(_rows(A))]

# Formula: c · A  — multiply every entry of A by scalar c
def MatrixScale(c, A):
    return [[c * A[i][j] for j in range(_cols(A))] for i in range(_rows(A))]

# Formula: (AB)ᵢⱼ  =  Σₖ AᵢₖBₖⱼ  — standard matrix multiplication
# A must be m×n and B must be n×p; result is m×p
def MatrixMultiply(A, B):
    m, n, p = _rows(A), _cols(A), _cols(B)
    if n != _rows(B):
        raise ValueError(f'Inner dimensions must match: A is {m}×{n}, B is {_rows(B)}×{p}')
    return [[sum(A[i][k] * B[k][j] for k in range(n))
             for j in range(p)] for i in range(m)]             # Complete (AB)ᵢⱼ = ΣAᵢₖBₖⱼ

# Formula: Aᵀ  — flip rows and columns
# Returns the transpose of A; an m×n matrix becomes n×m
def Transpose(A):
    return [[A[i][j] for i in range(_rows(A))] for j in range(_cols(A))]

# Formula: tr(A)  =  Σ Aᵢᵢ  — sum of main diagonal entries
# Defined only for square matrices
def Trace(A):
    if _rows(A) != _cols(A):
        raise ValueError('Trace is only defined for square matrices')
    return sum(A[i][i] for i in range(_rows(A)))               # Sum diagonal → complete tr(A)

# Formula: Aⁿ  — repeated matrix multiplication A · A · ... · A  (n times)
# n must be a non-negative integer; A must be square; A⁰ returns the identity
def MatrixPower(A, n):
    if _rows(A) != _cols(A):
        raise ValueError('Matrix power is only defined for square matrices')
    if n < 0:
        raise ValueError('Negative powers require the matrix inverse — use MatrixInverse first')
    result = _ident(_rows(A))                                   # Start from identity (A⁰)
    for _ in range(n):
        result = MatrixMultiply(result, A)                      # Accumulate A each iteration
    return result                                               # Complete Aⁿ

# Formula: A ⊗ B  — Kronecker product, a block matrix of size (mr × np)
# Each entry A[i][j] is replaced by the block A[i][j]·B
def KroneckerProduct(A, B):
    m, n = _rows(A), _cols(A)
    p, q = _rows(B), _cols(B)
    R = [[0.0] * (n * q) for _ in range(m * p)]
    for i in range(m):
        for j in range(n):
            for k in range(p):
                for l in range(q):
                    R[i * p + k][j * q + l] = A[i][j] * B[k][l]   # Block entry → A[i][j]·B[k][l]
    return R                                                    # Complete A ⊗ B

# Formula: [A | B]  — horizontal concatenation of two matrices with the same row count
def HStack(A, B):
    if _rows(A) != _rows(B):
        raise ValueError('Matrices must have the same number of rows for HStack')
    return [A[i] + B[i] for i in range(_rows(A))]              # Concatenate each row → complete [A|B]

# Formula: [A ; B]  — vertical concatenation of two matrices with the same column count
def VStack(A, B):
    if _cols(A) != _cols(B):
        raise ValueError('Matrices must have the same number of columns for VStack')
    return _copy(A) + _copy(B)                                  # Stack rows → complete [A;B]

# Returns the i-th row of matrix A as a vector (list)
def GetRow(A, i):
    return list(A[i])

# Returns the j-th column of matrix A as a vector (list)
def GetCol(A, j):
    return [A[i][j] for i in range(_rows(A))]

# Returns the main diagonal of a square matrix as a vector
def Diagonal(A):
    n = min(_rows(A), _cols(A))
    return [A[i][i] for i in range(n)]                         # Collect diagonal entries

# Constructs a diagonal matrix from a vector of diagonal values
def DiagonalMatrix(v):
    n = len(v)
    return [[float(v[i]) if i == j else 0.0 for j in range(n)] for i in range(n)]

# Formula: Hadamard (element-wise) product A ∘ B
def HadamardProduct(A, B):
    if _rows(A) != _rows(B) or _cols(A) != _cols(B):
        raise ValueError('Matrices must have identical dimensions for Hadamard product')
    return [[A[i][j] * B[i][j] for j in range(_cols(A))] for i in range(_rows(A))]

# ============================================================
# MATRIX PROPERTIES
# ============================================================

# Returns True if A is square (number of rows equals number of columns)
def IsSquare(A):
    return _rows(A) == _cols(A)                                 # Square iff m = n

# Formula: Aᵀ = A  — A is symmetric iff every off-diagonal entry equals its mirror
def IsSymmetric(A, tol=1e-9):
    if not IsSquare(A):
        return False
    n = _rows(A)
    return all(abs(A[i][j] - A[j][i]) < tol for i in range(n) for j in range(n))

# Formula: Aᵀ = −A  — A is skew-symmetric iff Aᵢⱼ = −Aⱼᵢ for all i, j
def IsSkewSymmetric(A, tol=1e-9):
    if not IsSquare(A):
        return False
    n = _rows(A)
    return all(abs(A[i][j] + A[j][i]) < tol for i in range(n) for j in range(n))

# Formula: AᵀA = I  — A is orthogonal iff its transpose is also its inverse
def IsOrthogonal(A, tol=1e-9):
    if not IsSquare(A):
        return False
    n = _rows(A)
    ATA = MatrixMultiply(Transpose(A), A)
    I   = _ident(n)
    return all(abs(ATA[i][j] - I[i][j]) < tol for i in range(n) for j in range(n))

# Returns True if A is the n×n identity matrix
def IsIdentity(A, tol=1e-9):
    if not IsSquare(A):
        return False
    n = _rows(A)
    return all(
        abs(A[i][j] - (1.0 if i == j else 0.0)) < tol
        for i in range(n) for j in range(n)
    )

# Returns True if every entry of A is zero
def IsZeroMatrix(A, tol=1e-9):
    return all(abs(A[i][j]) < tol for i in range(_rows(A)) for j in range(_cols(A)))

# Returns True if A is diagonal — all off-diagonal entries are zero
def IsDiagonal(A, tol=1e-9):
    if not IsSquare(A):
        return False
    n = _rows(A)
    return all(abs(A[i][j]) < tol for i in range(n) for j in range(n) if i != j)

# Returns True if A is upper triangular — all entries below the main diagonal are zero
def IsUpperTriangular(A, tol=1e-9):
    if not IsSquare(A):
        return False
    n = _rows(A)
    return all(abs(A[i][j]) < tol for i in range(n) for j in range(i))

# Returns True if A is lower triangular — all entries above the main diagonal are zero
def IsLowerTriangular(A, tol=1e-9):
    if not IsSquare(A):
        return False
    n = _rows(A)
    return all(abs(A[i][j]) < tol for i in range(n) for j in range(i + 1, n))

# Returns True if A is positive definite — all eigenvalues are strictly positive
# Uses Sylvester's criterion: all leading principal minors must be positive
def IsPositiveDefinite(A, tol=1e-9):
    if not IsSquare(A) or not IsSymmetric(A, tol):
        return False
    n = _rows(A)
    for k in range(1, n + 1):
        sub = [[A[i][j] for j in range(k)] for i in range(k)]  # k×k leading principal submatrix
        if Determinant(sub) <= tol:
            return False                                        # Non-positive minor → not PD
    return True                                                 # All minors positive → positive definite

# Returns True if A is idempotent — A² = A
def IsIdempotent(A, tol=1e-9):
    if not IsSquare(A):
        return False
    A2 = MatrixMultiply(A, A)
    n  = _rows(A)
    return all(abs(A2[i][j] - A[i][j]) < tol for i in range(n) for j in range(n))

# Returns True if A is involutory — A² = I
def IsInvolutory(A, tol=1e-9):
    if not IsSquare(A):
        return False
    A2 = MatrixMultiply(A, A)
    return IsIdentity(A2, tol)

# Returns True if A is nilpotent — Aᵏ = 0 for some positive integer k ≤ n
def IsNilpotent(A, tol=1e-9):
    if not IsSquare(A):
        return False
    n   = _rows(A)
    Ak  = _ident(n)
    for _ in range(n):
        Ak = MatrixMultiply(Ak, A)
        if IsZeroMatrix(Ak, tol):
            return True                                         # Found k such that Aᵏ = 0
    return False

# ============================================================
# DETERMINANTS
# ============================================================

# Formula: det(A) via cofactor expansion along the first row (recursive)
# Returns the determinant of a square matrix; raises ValueError if not square
def Determinant(A):
    if not IsSquare(A):
        raise ValueError('Determinant is only defined for square matrices')
    n = _rows(A)
    if n == 1:
        return A[0][0]                                          # 1×1 base case
    if n == 2:
        return A[0][0] * A[1][1] - A[0][1] * A[1][0]          # 2×2 formula: ad − bc
    # Cofactor expansion along row 0
    det = 0.0
    for j in range(n):
        sign = (-1) ** j                                        # Alternating sign pattern
        det += sign * A[0][j] * Determinant(_submatrix(A, 0, j))   # Cofactor term
    return det                                                  # Complete det(A)

# Formula: Mᵢⱼ  — minor of A at (i, j): determinant of A with row i and column j deleted
def Minor(A, i, j):
    return Determinant(_submatrix(A, i, j))                    # Determinant of reduced matrix

# Formula: Cᵢⱼ  =  (−1)^(i+j) · Mᵢⱼ  — cofactor of A at position (i, j)
def Cofactor(A, i, j):
    return ((-1) ** (i + j)) * Minor(A, i, j)                  # Sign-adjusted minor → cofactor

# Formula: C  — the cofactor matrix (each entry is the cofactor of A at that position)
# Returns the matrix of cofactors (same size as A)
def CofactorMatrix(A):
    n = _rows(A)
    return [[Cofactor(A, i, j) for j in range(n)] for i in range(n)]

# Formula: adj(A)  =  Cᵀ  — transpose of the cofactor matrix
# The adjugate satisfies A · adj(A) = det(A) · I
def Adjugate(A):
    return Transpose(CofactorMatrix(A))                         # Transpose of cofactors → adj(A)

# ============================================================
# MATRIX INVERSE
# ============================================================

# Formula: A⁻¹  =  adj(A) / det(A)  — inverse via adjugate (exact, symbolic)
# For large matrices the Gauss-Jordan version below is more numerically stable
# Returns None if A is singular (det = 0)
def MatrixInverseAdjugate(A):
    if not IsSquare(A):
        raise ValueError('Inverse is only defined for square matrices')
    det = Determinant(A)
    if abs(det) < 1e-12:
        return None                                             # Singular matrix — no inverse
    adj = Adjugate(A)
    return [[adj[i][j] / det for j in range(_rows(A))] for i in range(_rows(A))]

# Formula: A⁻¹ via Gauss-Jordan elimination on [A | I] → [I | A⁻¹]
# More numerically stable for larger matrices; returns None if A is singular
def MatrixInverse(A):
    if not IsSquare(A):
        raise ValueError('Inverse is only defined for square matrices')
    n  = _rows(A)
    # Build augmented matrix [A | I]
    aug = [list(map(float, A[i])) + [1.0 if i == j else 0.0 for j in range(n)]
           for i in range(n)]
    for col in range(n):
        # Partial pivoting — find the row with the largest absolute value in this column
        pivot_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
        aug[col], aug[pivot_row] = aug[pivot_row], aug[col]     # Swap rows
        pivot = aug[col][col]
        if abs(pivot) < 1e-12:
            return None                                         # Singular — no inverse
        # Scale pivot row so leading entry becomes 1
        aug[col] = [x / pivot for x in aug[col]]
        # Eliminate all other rows
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            aug[row] = [aug[row][k] - factor * aug[col][k] for k in range(2 * n)]
    # Extract right half — the computed inverse
    return [[aug[i][j + n] for j in range(n)] for i in range(n)]

# Formula: pseudo-inverse via (AᵀA)⁻¹Aᵀ (left inverse when A has full column rank)
# Returns None if AᵀA is singular (columns of A are linearly dependent)
def PseudoInverse(A):
    At   = Transpose(A)
    AtA  = MatrixMultiply(At, A)
    inv  = MatrixInverse(AtA)
    if inv is None:
        return None                                             # AᵀA singular — columns not independent
    return MatrixMultiply(inv, At)                             # Complete (AᵀA)⁻¹Aᵀ

# ============================================================
# LINEAR SYSTEMS
# ============================================================

# Solve Ax = b using Gaussian elimination with partial pivoting.
# A is an n×n matrix; b is a length-n vector.
# Returns the solution vector x, or None if the system has no unique solution.
def SolveLinearSystem(A, b):
    n   = _rows(A)
    # Build augmented matrix [A | b]
    aug = [list(map(float, A[i])) + [float(b[i])] for i in range(n)]

    for col in range(n):
        # Partial pivoting
        pivot_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
        aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
        if abs(aug[col][col]) < 1e-12:
            return None                                         # Singular or inconsistent system

        # Eliminate below the pivot
        for row in range(col + 1, n):
            factor = aug[row][col] / aug[col][col]
            aug[row] = [aug[row][k] - factor * aug[col][k] for k in range(n + 1)]

    # Back substitution
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = aug[i][n]
        for j in range(i + 1, n):
            x[i] -= aug[i][j] * x[j]
        x[i] /= aug[i][i]                                      # Solve for each variable in turn
    return x                                                    # Complete solution vector x

# Formula: x = A⁻¹b  — solve via matrix inverse (useful when solving many right-hand sides)
# Returns None if A is singular
def SolveViaInverse(A, b):
    inv = MatrixInverse(A)
    if inv is None:
        return None                                             # No inverse — system has no unique solution
    return [sum(inv[i][j] * b[j] for j in range(len(b))) for i in range(_rows(A))]

# Formula: Cramer's rule — xᵢ = det(Aᵢ) / det(A)
# Aᵢ is A with column i replaced by b.
# Returns the solution vector; returns None if det(A) = 0
def CramersRule(A, b):
    n   = _rows(A)
    det = Determinant(A)
    if abs(det) < 1e-12:
        return None                                             # Singular — Cramer's rule not applicable
    x = []
    for i in range(n):
        # Build Aᵢ — copy A, replace column i with b
        Ai = [list(row) for row in A]
        for row in range(n):
            Ai[row][i] = b[row]
        x.append(Determinant(Ai) / det)                        # xᵢ = det(Aᵢ) / det(A)
    return x                                                    # Complete Cramer solution vector

# Formula: Gauss-Jordan on augmented [A|b] to reduced row echelon form
# Returns the RREF of [A|b] as a matrix — useful for seeing consistency and free variables
def ReducedRowEchelon(A, b):
    n   = _rows(A)
    m   = _cols(A)
    aug = [list(map(float, A[i])) + [float(b[i])] for i in range(n)]
    pivot_col = 0
    pivot_row = 0
    while pivot_row < n and pivot_col < m:
        # Find the pivot in this column from current row downward
        max_row = max(range(pivot_row, n), key=lambda r: abs(aug[r][pivot_col]))
        if abs(aug[max_row][pivot_col]) < 1e-12:
            pivot_col += 1                                      # No pivot here — move right
            continue
        aug[pivot_row], aug[max_row] = aug[max_row], aug[pivot_row]
        # Scale pivot row
        pv = aug[pivot_row][pivot_col]
        aug[pivot_row] = [x / pv for x in aug[pivot_row]]
        # Eliminate all other rows
        for row in range(n):
            if row == pivot_row:
                continue
            factor = aug[row][pivot_col]
            aug[row] = [aug[row][k] - factor * aug[pivot_row][k] for k in range(m + 1)]
        pivot_row += 1
        pivot_col += 1
    return aug                                                  # Complete RREF of [A|b]

# Checks whether the system Ax = b is consistent (has at least one solution).
# Uses the rank test: consistent iff rank([A|b]) == rank(A)
def IsConsistent(A, b):
    rref_ab = ReducedRowEchelon(A, b)
    m       = _cols(A)
    # Count zero rows in A part only
    rank_ab = sum(1 for row in rref_ab if any(abs(row[j]) > 1e-9 for j in range(m + 1)))
    rank_a  = sum(1 for row in rref_ab if any(abs(row[j]) > 1e-9 for j in range(m)))
    return rank_ab == rank_a                                    # Consistent iff ranks agree

# ============================================================
# EIGENVALUES AND EIGENVECTORS
# ============================================================

# Formula: characteristic polynomial coefficients for a 2×2 matrix
# det(A − λI) = λ² − tr(A)λ + det(A)
# Returns (a, b, c) for ax² + bx + c = 0  (a = 1 always here)
def CharacteristicPoly2x2(A):
    if _rows(A) != 2 or _cols(A) != 2:
        raise ValueError('CharacteristicPoly2x2 requires a 2×2 matrix')
    t = Trace(A)
    d = Determinant(A)
    return 1.0, -t, d                                           # λ² − tr·λ + det = 0

# Formula: eigenvalues of a 2×2 matrix via the quadratic formula applied to char poly
# Returns a list of eigenvalues (real or None for complex eigenvalues)
def Eigenvalues2x2(A):
    if _rows(A) != 2 or _cols(A) != 2:
        raise ValueError('Eigenvalues2x2 requires a 2×2 matrix')
    _, b, c = CharacteristicPoly2x2(A)                         # λ² + bλ + c = 0
    disc    = b * b - 4 * c
    if disc < 0:
        r   = -b / 2
        im  = math.sqrt(-disc) / 2
        return [complex(r, im), complex(r, -im)]               # Complex conjugate pair
    sq   = math.sqrt(disc)
    return [(-b + sq) / 2, (-b - sq) / 2]                     # Two real eigenvalues

# Formula: eigenvector for a 2×2 matrix corresponding to a given real eigenvalue
# Solves (A − λI)v = 0; returns a unit eigenvector or None if degenerate
def Eigenvector2x2(A, eigenvalue):
    n     = 2
    AminL = [[A[i][j] - (eigenvalue if i == j else 0) for j in range(n)] for i in range(n)]
    # Find a non-zero row to build the eigenvector
    for i in range(n):
        row = AminL[i]
        if abs(row[0]) > 1e-9 or abs(row[1]) > 1e-9:
            # Eigenvector perpendicular to this row: [−row[1], row[0]]
            v = [-row[1], row[0]]
            mag = VectorMagnitude(v)
            if mag > 1e-12:
                return VectorNormalize(v)                       # Return unit eigenvector
    return None                                                 # Degenerate case

# Formula: eigenvalues of a 3×3 matrix via the characteristic polynomial
# det(A − λI) = −λ³ + tr(A)λ² − (sum of 2×2 principal minors)λ + det(A) = 0
# Uses Cardano-adjacent numerical root finding (Newton's method on cubic)
def Eigenvalues3x3(A):
    if _rows(A) != 3 or _cols(A) != 3:
        raise ValueError('Eigenvalues3x3 requires a 3×3 matrix')
    t  = Trace(A)
    d  = Determinant(A)
    # Sum of 2×2 principal minors (cofactors of diagonal)
    p  = (A[0][0]*A[1][1] - A[0][1]*A[1][0] +
          A[0][0]*A[2][2] - A[0][2]*A[2][0] +
          A[1][1]*A[2][2] - A[1][2]*A[2][1])
    # Coefficients of −λ³ + tλ² − pλ + d = 0  →  λ³ − tλ² + pλ − d = 0
    # Find roots numerically with Newton's method seeded from companion matrix approach
    def f(x):
        return x**3 - t*x**2 + p*x - d
    def df(x):
        return 3*x**2 - 2*t*x + p

    roots   = []
    # Try three initial seeds spread around the expected range
    seeds   = [t / 3 + k * (abs(t) + 1) / 3 for k in (-1, 0, 1)]
    for seed in seeds:
        x = float(seed)
        for _ in range(200):
            fx  = f(x)
            dfx = df(x)
            if abs(dfx) < 1e-14:
                break
            x -= fx / dfx                                       # Newton step
        if abs(f(x)) < 1e-6:
            # Check it is not a duplicate
            if not any(abs(x - r) < 1e-4 for r in roots):
                roots.append(round(x, 10))

    # Deflate the polynomial to find any remaining roots
    if len(roots) == 1:
        # Deflate: (λ − r₁)(λ² + bλ + c) where b = r₁ − t, c = d/r₁ (approx)
        r1 = roots[0]
        b2 = r1 - t
        c2 = r1**2 - t*r1 + p
        disc = b2**2 - 4*c2
        if disc >= 0:
            sq = math.sqrt(disc)
            roots += [(-b2 + sq)/2, (-b2 - sq)/2]
        else:
            r  = -b2 / 2
            im = math.sqrt(-disc) / 2
            roots += [complex(r, im), complex(r, -im)]
    elif len(roots) == 2:
        # Third root by Vieta: product of roots = d (with sign)
        r3 = d / (roots[0] * roots[1]) if abs(roots[0] * roots[1]) > 1e-12 else t - roots[0] - roots[1]
        roots.append(round(r3, 10))

    return roots[:3]                                            # Return the three eigenvalues

# Formula: spectral radius  ρ(A)  =  max|λᵢ|  — the largest absolute eigenvalue
# Works for 2×2 and 3×3 matrices
def SpectralRadius(A):
    if _rows(A) == 2:
        eigs = Eigenvalues2x2(A)
    elif _rows(A) == 3:
        eigs = Eigenvalues3x3(A)
    else:
        raise ValueError('SpectralRadius supports 2×2 and 3×3 matrices')
    return max(abs(e) for e in eigs)                            # Max absolute eigenvalue → ρ(A)

# Formula: power iteration — finds the dominant (largest-magnitude) eigenvalue and eigenvector
# Iterates  v_{k+1} = A·vₖ / ‖A·vₖ‖  until convergence
# Returns (eigenvalue, eigenvector) or (None, None) if it does not converge
def PowerIteration(A, max_iter=1000, tol=1e-10):
    n  = _rows(A)
    if not IsSquare(A):
        raise ValueError('Power iteration requires a square matrix')
    # Start from a random-ish vector (deterministic: use [1, 1, ..., 1] normalised)
    v  = VectorNormalize([1.0] * n)
    eigenvalue = 0.0
    for _ in range(max_iter):
        # Multiply A by v
        Av = [sum(A[i][j] * v[j] for j in range(n)) for i in range(n)]
        new_eigenvalue = DotProduct(Av, v)                      # Rayleigh quotient approximation
        v_new = VectorNormalize(Av)
        if abs(new_eigenvalue - eigenvalue) < tol:
            return new_eigenvalue, v_new                        # Converged
        eigenvalue = new_eigenvalue
        v          = v_new
    return eigenvalue, v                                        # Return best estimate after max iterations

# Formula: inverse power iteration — finds the smallest-magnitude eigenvalue
# Solves A·w = v at each step instead of multiplying by A
def InversePowerIteration(A, max_iter=1000, tol=1e-10):
    n = _rows(A)
    if not IsSquare(A):
        raise ValueError('Inverse power iteration requires a square matrix')
    v          = VectorNormalize([1.0] * n)
    eigenvalue = 0.0
    for _ in range(max_iter):
        w = SolveLinearSystem(A, v)
        if w is None:
            return None, None                                   # A is singular — smallest eigenvalue is 0
        new_eigenvalue = 1.0 / DotProduct(w, v)                # Reciprocal of dominant eig of A⁻¹
        v_new          = VectorNormalize(w)
        if abs(new_eigenvalue - eigenvalue) < tol:
            return new_eigenvalue, v_new
        eigenvalue = new_eigenvalue
        v          = v_new
    return eigenvalue, v

# Formula: diagonalisation — A = PDP⁻¹ where D is diagonal and P holds eigenvectors (2×2 only)
# Returns (P, D, P_inv) or None if A is not diagonalisable
def Diagonalize2x2(A):
    eigs = Eigenvalues2x2(A)
    if any(isinstance(e, complex) for e in eigs):
        return None                                             # Complex eigenvalues → not real-diagonalisable
    vecs = [Eigenvector2x2(A, e) for e in eigs]
    if any(v is None for v in vecs):
        return None                                             # Could not find eigenvectors
    P    = Transpose(vecs)                                      # Columns are eigenvectors
    D    = DiagonalMatrix(eigs)
    Pinv = MatrixInverse(P)
    if Pinv is None:
        return None                                             # Eigenvectors not independent → degenerate
    return P, D, Pinv                                          # Complete A = PDP⁻¹

# ============================================================
# VECTOR SPACES
# ============================================================

# Formula: rank of A  — number of non-zero rows in RREF(A)
# The rank equals the dimension of the column space (and row space) of A
def Rank(A):
    rref = ReducedRowEchelon(A, [0.0] * _rows(A))             # RREF with zero right-hand side
    return sum(1 for row in rref if any(abs(v) > 1e-9 for v in row[:-1]))  # Count non-zero rows

# Formula: nullity(A)  =  n − rank(A)  (Rank-Nullity Theorem)
# Returns the dimension of the null space of A
def Nullity(A):
    return _cols(A) - Rank(A)                                  # Rank + Nullity = number of columns

# Formula: null space basis — set of vectors x such that Ax = 0
# Returns a list of basis vectors for the null space; empty list if only the trivial solution
def NullSpace(A):
    n      = _cols(A)
    rref   = ReducedRowEchelon(A, [0.0] * _rows(A))
    # Identify pivot columns and free columns
    pivots = {}
    for row in rref:
        for j in range(n):
            if abs(row[j]) > 1e-9:
                pivots[j] = row                                 # Map pivot column → row
                break
    free_cols = [j for j in range(n) if j not in pivots]
    if not free_cols:
        return []                                               # Only trivial solution
    basis = []
    for fc in free_cols:
        vec = [0.0] * n
        vec[fc] = 1.0                                          # Free variable = 1, others = 0
        for pc, row in pivots.items():
            vec[pc] = -row[fc]                                 # Express pivot var in terms of free
        basis.append(vec)
    return basis                                                # Complete null space basis

# Formula: column space basis — set of linearly independent columns of A
# Returns the pivot columns of A as a list of vectors
def ColumnSpace(A):
    n    = _cols(A)
    rref = ReducedRowEchelon(A, [0.0] * _rows(A))
    # Find pivot column indices
    pivot_cols = []
    for row in rref:
        for j in range(n):
            if abs(row[j]) > 1e-9:
                pivot_cols.append(j)
                break
    # Return the corresponding original columns
    return [GetCol(A, j) for j in pivot_cols]                  # Pivot columns span the column space

# Formula: row space basis — non-zero rows of RREF(A)
# Returns the non-zero rows of the RREF as basis vectors for the row space
def RowSpace(A):
    n    = _cols(A)
    rref = ReducedRowEchelon(A, [0.0] * _rows(A))
    return [row[:n] for row in rref if any(abs(v) > 1e-9 for v in row[:n])]

# Formula: a set of vectors is linearly independent iff their rank equals their count
# Returns True if the vectors v1, v2, ..., vk are linearly independent
def AreLinearlyIndependent(vectors):
    if not vectors:
        return True
    A    = Transpose(vectors)                                   # Columns are the vectors
    return Rank(A) == len(vectors)                             # Independent iff rank equals count

# Formula: span check — is vector v in the span of the columns of A?
# Returns True if the system A·x = v is consistent
def IsInSpan(A, v):
    return IsConsistent(A, v)                                  # v in col(A) iff Ax = v is consistent

# Formula: coordinate vector [v]_B — express v in terms of basis B
# B is a list of basis vectors; returns the coordinates, or None if B is not a basis for v's space
def CoordinateVector(v, B):
    A   = Transpose(B)                                         # Columns are basis vectors
    return SolveLinearSystem(A, v)                             # Solve B·x = v for coordinate vector

# Formula: change-of-basis matrix from basis B to basis C
# Returns the matrix P such that [v]_C = P [v]_B
def ChangeOfBasisMatrix(B, C):
    B_mat = Transpose(B)                                        # Columns = B vectors
    C_mat = Transpose(C)                                        # Columns = C vectors
    C_inv = MatrixInverse(C_mat)
    if C_inv is None:
        return None                                             # C is not a valid basis
    return MatrixMultiply(C_inv, B_mat)                        # Complete change-of-basis P = C⁻¹B

# ============================================================
# ORTHOGONALITY
# ============================================================

# Formula: Gram-Schmidt process — convert a set of linearly independent vectors into an orthonormal basis
# Returns a list of orthonormal vectors spanning the same space as the input vectors
# If a vector is (numerically) zero after projection, it is skipped (handles linear dependence gracefully)
def GramSchmidt(vectors, tol=1e-10):
    orthonormal = []
    for v in vectors:
        # Subtract projections onto all previously found orthonormal vectors
        w = list(v)
        for u in orthonormal:
            coeff = DotProduct(v, u)                            # Project v onto u
            w = VectorSubtract(w, VectorScale(coeff, u))       # Subtract that component
        if VectorMagnitude(w) > tol:
            orthonormal.append(VectorNormalize(w))             # Normalise and add to the set
    return orthonormal                                          # Complete orthonormal basis

# Formula: QR decomposition — A = QR where Q is orthogonal and R is upper triangular
# A must have at least as many rows as columns; columns must be linearly independent
# Returns (Q, R) or (None, None) if decomposition fails
def QRDecomposition(A):
    m  = _rows(A)
    n  = _cols(A)
    cols = [GetCol(A, j) for j in range(n)]                    # Extract columns of A
    Q_cols = GramSchmidt(cols)
    if len(Q_cols) != n:
        return None, None                                       # Columns were linearly dependent
    Q = Transpose(Q_cols)                                       # Q: orthonormal columns
    R = [[DotProduct(Q_cols[i], cols[j]) if i <= j else 0.0   # R is upper triangular: Rᵢⱼ = qᵢ·aⱼ
          for j in range(n)] for i in range(n)]
    return Q, R                                                 # Complete A = QR

# Formula: orthogonal projection of vector v onto subspace spanned by columns of A
# proj = A(AᵀA)⁻¹Aᵀv  — projection onto col(A)
def OrthogonalProjectionOntoSubspace(v, A):
    pseudo = PseudoInverse(A)
    if pseudo is None:
        return None                                             # Columns not independent
    # A · pseudo · v = A(AᵀA)⁻¹Aᵀv
    Apseudo = MatrixMultiply(A, pseudo)
    return [sum(Apseudo[i][j] * v[j] for j in range(len(v))) for i in range(_rows(Apseudo))]

# Formula: least squares solution — minimise ‖Ax − b‖² via normal equations AᵀAx = Aᵀb
# Returns x* = (AᵀA)⁻¹Aᵀb, or None if AᵀA is singular
def LeastSquares(A, b):
    At  = Transpose(A)
    AtA = MatrixMultiply(At, A)
    Atb = [sum(At[i][j] * b[j] for j in range(len(b))) for i in range(_rows(At))]
    return SolveLinearSystem(AtA, Atb)                         # Solve normal equations

# Formula: check whether two vectors are orthonormal (unit length and orthogonal to each other)
def AreOrthonormal(vectors, tol=1e-9):
    n = len(vectors)
    for i in range(n):
        if abs(VectorMagnitude(vectors[i]) - 1.0) > tol:       # Each must be a unit vector
            return False
        for j in range(i + 1, n):
            if abs(DotProduct(vectors[i], vectors[j])) > tol:  # Each pair must be orthogonal
                return False
    return True                                                 # All unit and mutually orthogonal

# ============================================================
# MATRIX DECOMPOSITIONS
# ============================================================

# Formula: LU decomposition — A = LU where L is unit lower triangular and U is upper triangular
# Uses Doolittle's method with partial pivoting (returns PA = LU where P is the permutation)
# Returns (L, U, P) where P is the permutation matrix, or (None, None, None) if A is singular
def LUDecomposition(A):
    if not IsSquare(A):
        raise ValueError('LU decomposition requires a square matrix')
    n   = _rows(A)
    L   = _ident(n)
    U   = _copy(A)
    P   = _ident(n)                                             # Track row swaps
    for col in range(n):
        # Partial pivoting
        pivot_row = max(range(col, n), key=lambda r: abs(U[r][col]))
        if abs(U[pivot_row][col]) < 1e-12:
            return None, None, None                             # Singular matrix
        if pivot_row != col:
            U[col], U[pivot_row] = U[pivot_row], U[col]
            P[col], P[pivot_row] = P[pivot_row], P[col]
            for k in range(col):
                L[col][k], L[pivot_row][k] = L[pivot_row][k], L[col][k]
        # Eliminate below pivot
        for row in range(col + 1, n):
            factor      = U[row][col] / U[col][col]
            L[row][col] = factor                                # Store multiplier in L
            U[row]      = [U[row][k] - factor * U[col][k] for k in range(n)]
    return L, U, P                                             # Complete PA = LU

# Formula: Cholesky decomposition — A = LLᵀ where L is lower triangular
# Only valid for real symmetric positive-definite matrices
# Returns L or None if A is not positive definite
def CholeskyDecomposition(A):
    if not IsSquare(A) or not IsSymmetric(A) or not IsPositiveDefinite(A):
        return None                                             # Must be symmetric positive definite
    n = _rows(A)
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                val = A[i][i] - s
                if val < 0:
                    return None                                 # Not positive definite
                L[i][j] = math.sqrt(val)                       # Diagonal entry
            else:
                if abs(L[j][j]) < 1e-12:
                    return None
                L[i][j] = (A[i][j] - s) / L[j][j]             # Off-diagonal entry
    return L                                                    # Complete Cholesky factor L

# Formula: SVD of a 2×2 matrix — A = UΣVᵀ
# Returns (U, Sigma, Vt) where Sigma is a list of singular values (not a matrix)
# For a 2×2 matrix this is done analytically via the SVD equations
def SVD2x2(A):
    if _rows(A) != 2 or _cols(A) != 2:
        raise ValueError('SVD2x2 requires a 2×2 matrix')
    # Compute AᵀA (2×2 symmetric) then find its eigenvalues (= squared singular values)
    AtA  = MatrixMultiply(Transpose(A), A)
    eigs = Eigenvalues2x2(AtA)
    # Singular values are √|eigenvalue| — sort descending
    sigmas = sorted([math.sqrt(max(0.0, e.real if isinstance(e, complex) else e))
                     for e in eigs], reverse=True)
    # Right singular vectors = eigenvectors of AᵀA
    V_cols = []
    for e in sorted([e.real if isinstance(e, complex) else e for e in eigs], reverse=True):
        v = Eigenvector2x2(AtA, e)
        if v is None:
            v = [1.0, 0.0]
        V_cols.append(v)
    V  = Transpose(V_cols)                                      # V: 2×2
    Vt = Transpose(V)
    # Left singular vectors = Avᵢ / σᵢ
    U_cols = []
    for i, sigma in enumerate(sigmas):
        col_v = GetCol(V, i)
        Av    = [sum(A[r][c] * col_v[c] for c in range(2)) for r in range(2)]
        if sigma > 1e-12:
            U_cols.append(VectorNormalize(Av))
        else:
            U_cols.append([1.0, 0.0])                          # Arbitrary unit vector for zero singular value
    U = Transpose(U_cols)                                       # U: 2×2
    return U, sigmas, Vt                                        # Complete A = UΣVᵀ

# Formula: Jacobi SVD iteration for general m×n matrices (m ≥ n)
# Returns (U, sigma, Vt) via one-sided Jacobi rotations; convergent but may be slow for large n
def SVD(A, max_iter=500, tol=1e-10):
    m  = _rows(A)
    n  = _cols(A)
    if m < n:
        # Transpose and swap U/Vt in output
        U, s, Vt = SVD(Transpose(A), max_iter, tol)
        return Transpose(Vt), s, Transpose(U)
    # Start: V = I, work on B = A (we will compute U at the end)
    B  = _copy(A)
    V  = _ident(n)
    for _ in range(max_iter):
        converged = True
        for p in range(n - 1):
            for q in range(p + 1, n):
                # Compute elements of BᵀB block
                alpha  = sum(B[k][p] ** 2 for k in range(m))
                beta   = sum(B[k][q] ** 2 for k in range(m))
                gamma  = sum(B[k][p] * B[k][q] for k in range(m))
                if abs(gamma) < tol * math.sqrt(alpha * beta + 1e-20):
                    continue                                     # Already orthogonal — skip
                converged = False
                zeta      = (beta - alpha) / (2.0 * gamma)
                t         = (1.0 / (abs(zeta) + math.sqrt(1 + zeta ** 2))) * (1 if zeta >= 0 else -1)
                c         = 1.0 / math.sqrt(1 + t ** 2)
                s_val     = c * t
                # Apply Jacobi rotation to B
                for k in range(m):
                    bp, bq        = B[k][p], B[k][q]
                    B[k][p]       = c * bp - s_val * bq
                    B[k][q]       = s_val * bp + c * bq
                # Accumulate into V
                for k in range(n):
                    vp, vq        = V[k][p], V[k][q]
                    V[k][p]       = c * vp - s_val * vq
                    V[k][q]       = s_val * vp + c * vq
        if converged:
            break
    # Extract singular values and normalise columns of B into U
    sigmas = []
    U_cols = []
    for j in range(n):
        col    = GetCol(B, j)
        sigma  = VectorMagnitude(col)
        sigmas.append(sigma)
        if sigma > 1e-12:
            U_cols.append(VectorNormalize(col))
        else:
            # Arbitrary unit vector — handle zero singular value
            unit = [1.0 if k == j else 0.0 for k in range(m)]
            U_cols.append(unit)
    # Sort by descending singular value
    order  = sorted(range(n), key=lambda j: -sigmas[j])
    sigmas = [sigmas[j] for j in order]
    U_cols = [U_cols[j] for j in order]
    V_cols = [GetCol(V, j) for j in order]
    U  = Transpose(U_cols)
    Vt = [GetRow(Transpose(V_cols), i) for i in range(n)]
    return U, sigmas, Vt                                        # Complete A = UΣVᵀ

# Formula: condition number  κ(A)  =  σ_max / σ_min
# Large condition numbers indicate a nearly singular (ill-conditioned) matrix
def ConditionNumber(A):
    _, sigmas, _ = SVD(A)
    if min(sigmas) < 1e-14:
        return float('inf')                                     # Singular matrix → infinite condition number
    return max(sigmas) / min(sigmas)                            # Complete κ(A) = σ_max / σ_min

# Formula: matrix norm  ‖A‖_F  =  √(Σᵢⱼ Aᵢⱼ²)  — Frobenius norm
def FrobeniusNorm(A):
    return math.sqrt(sum(A[i][j] ** 2 for i in range(_rows(A)) for j in range(_cols(A))))

# Formula: ‖A‖₁  — maximum absolute column sum
def MatrixNorm1(A):
    return max(sum(abs(A[i][j]) for i in range(_rows(A))) for j in range(_cols(A)))

# Formula: ‖A‖∞  — maximum absolute row sum
def MatrixNormInf(A):
    return max(sum(abs(A[i][j]) for j in range(_cols(A))) for i in range(_rows(A)))

# Formula: matrix exponential  e^A  ≈  Σₖ Aᵏ/k!  via Taylor series truncated at max_terms
def MatrixExponential(A, max_terms=20):
    if not IsSquare(A):
        raise ValueError('Matrix exponential is only defined for square matrices')
    n      = _rows(A)
    result = _ident(n)                                          # k=0 term: A⁰/0! = I
    Ak     = _ident(n)
    fact   = 1.0
    for k in range(1, max_terms):
        Ak   = MatrixMultiply(Ak, A)
        fact *= k
        term = MatrixScale(1.0 / fact, Ak)
        result = MatrixAdd(result, term)                        # Accumulate k-th term Aᵏ/k!
    return result                                               # Complete e^A approximation
