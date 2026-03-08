import math  # Import math for factorial, comb, sqrt, log, floor, ceil

# ============================================================
# FACTORIALS AND BASIC COUNTING
# ============================================================

# Formula: n! = n * (n-1) * (n-2) * ... * 1
# Returns n factorial — the number of ways to arrange n distinct items in a sequence
# Returns 1 for n = 0 by convention — the empty arrangement
# Returns 0 if n is negative — undefined for negative integers
def Factorial(n):
    if n < 0:                                                   # Guard against negative input
        return 0                                                # Return 0 safely — undefined
    return math.factorial(n)                                    # Delegate to math.factorial → complete n!

# Formula: double factorial n!! = n * (n-2) * (n-4) * ... down to 1 or 2
# Returns the double factorial — product of every other integer down to 1 or 2
# Returns 1 for n = 0 and n = 1 by convention
# Returns 0 if n is negative
def DoubleFactorial(n):
    if n < 0:                                                   # Guard against negative input
        return 0                                                # Return 0 safely
    if n <= 1:                                                  # Base cases — 0!! = 1 and 1!! = 1
        return 1                                                # Return 1 by convention
    result = 1                                                  # Initialize product accumulator
    while n > 1:                                                # Multiply every other integer down to 2 or 1
        result *= n                                             # Multiply current value into result
        n      -= 2                                             # Step down by 2
    return result                                               # Return complete double factorial

# Formula: subfactorial !n = n! * Σₖ₌₀ⁿ (-1)^k / k!
# Returns the subfactorial — number of derangements of n items (permutations with no fixed points)
# Returns 1 for n = 0 by convention — one empty derangement
# Returns 0 if n is negative
def Subfactorial(n):
    if n < 0:                                                   # Guard against negative input
        return 0                                                # Return 0 safely
    if n == 0:                                                  # Base case — one empty derangement
        return 1                                                # Return 1 by convention
    if n == 1:                                                  # One item cannot be deranged
        return 0                                                # Return 0 — no valid derangement
    return round(math.factorial(n) / math.e)                    # n!/e rounded to nearest integer → complete !n

# Formula: falling factorial x^(n) = x * (x-1) * (x-2) * ... * (x-n+1)
# Returns the falling factorial — product of n consecutive integers starting at x and decreasing
# Returns 1 for n = 0 by convention
# Returns 0 if n is negative
def FallingFactorial(x, n):
    if n < 0:                                                   # Guard against negative n
        return 0                                                # Return 0 safely
    if n == 0:                                                  # Empty product is 1
        return 1                                                # Return 1 by convention
    result = 1                                                  # Initialize product accumulator
    for i in range(n):                                          # Multiply n consecutive descending terms
        result *= (x - i)                                       # Multiply (x - i) into product
    return result                                               # Return complete falling factorial

# Formula: rising factorial x^(n) = x * (x+1) * (x+2) * ... * (x+n-1)  (Pochhammer symbol)
# Returns the rising factorial — product of n consecutive integers starting at x and increasing
# Returns 1 for n = 0 by convention
# Returns 0 if n is negative
def RisingFactorial(x, n):
    if n < 0:                                                   # Guard against negative n
        return 0                                                # Return 0 safely
    if n == 0:                                                  # Empty product is 1
        return 1                                                # Return 1 by convention
    result = 1                                                  # Initialize product accumulator
    for i in range(n):                                          # Multiply n consecutive ascending terms
        result *= (x + i)                                       # Multiply (x + i) into product
    return result                                               # Return complete rising factorial

# Formula: primorial p# = product of all primes ≤ p
# Returns the primorial — the product of all prime numbers up to and including n
# Returns 1 if there are no primes up to n
def Primorial(n):
    if n < 2:                                                   # No primes below 2
        return 1                                                # Return 1 — empty product
    result = 1                                                  # Initialize product accumulator
    for k in range(2, n + 1):                                   # Check each integer from 2 to n
        if _IsPrime(k):                                         # Only include prime numbers
            result *= k                                         # Multiply prime into product
    return result                                               # Return complete primorial

# Internal helper — checks if a number is prime using trial division up to sqrt(n)
def _IsPrime(n):
    if n < 2:                                                   # 0 and 1 are not prime
        return False
    if n == 2:                                                  # 2 is the only even prime
        return True
    if n % 2 == 0:                                              # All other even numbers are not prime
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):               # Check odd divisors up to sqrt(n)
        if n % i == 0:                                          # Found a divisor — not prime
            return False
    return True                                                 # No divisors found → prime

# ============================================================
# PERMUTATIONS
# ============================================================

# Formula: P(n, r) = n! / (n - r)!
# Returns the number of r-permutations of n distinct objects — ordered selections without repetition
# Returns 0 if r > n or either is negative
def Permutations(n, r):
    if n < 0 or r < 0 or r > n:                                # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return math.factorial(n) // math.factorial(n - r)           # Divide n! by (n-r)! → complete P(n,r)

# Formula: n^r
# Returns the number of r-permutations with repetition — ordered selections where repeats are allowed
# Returns 0 if either is negative
def PermutationsWithRepetition(n, r):
    if n < 0 or r < 0:                                         # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return n ** r                                               # n choices for each of r positions → complete n^r

# Formula: n! / (n₁! * n₂! * ... * nₖ!)
# Returns the number of distinct arrangements of items where group sizes are given in the list
# The multinomial coefficient counts distinct permutations of a multiset
# Returns 0 if group sizes do not sum to n or any is negative
def MultisetPermutations(n, groups):
    if any(g < 0 for g in groups):                             # Guard against negative group sizes
        return 0                                                # Return 0 safely
    if sum(groups) != n:                                        # Group sizes must sum to total
        return 0                                                # Return 0 safely — inconsistent inputs
    denominator = 1                                             # Initialize denominator accumulator
    for g in groups:                                            # Multiply factorial of each group size
        denominator *= math.factorial(g)                        # Accumulate denominator product
    return math.factorial(n) // denominator                     # Divide n! by product → complete multinomial

# Formula: (n - 1)!
# Returns the number of ways to arrange n distinct objects in a circle
# One object is fixed to eliminate rotational equivalences
# Returns 0 if n is less than 1
def CircularPermutations(n):
    if n < 1:                                                   # Guard against invalid input
        return 0                                                # Return 0 safely
    return math.factorial(n - 1)                                # Fix one element and arrange the rest → complete (n-1)!

# Formula: (n - 1)! / 2  for necklace arrangements
# Returns the number of distinct necklace arrangements of n beads
# Divides circular permutations by 2 to account for reflections (flipping the necklace)
# Returns 0 if n is less than 1
def NecklacePermutations(n):
    if n < 1:                                                   # Guard against invalid input
        return 0                                                # Return 0 safely
    if n <= 2:                                                  # 1 or 2 beads have only one arrangement
        return 1                                                # Return 1
    return math.factorial(n - 1) // 2                           # Divide circular arrangements by 2 → complete necklace count

# Formula: D(n) = n! * Σₖ₌₀ⁿ (-1)^k / k!  ≈  n! / e
# Returns the number of derangements — permutations where no element appears in its original position
# Returns 0 if n is negative
def Derangements(n):
    if n < 0:                                                   # Guard against negative input
        return 0                                                # Return 0 safely
    if n == 0:                                                  # One empty derangement by convention
        return 1
    if n == 1:                                                  # Cannot derange a single element
        return 0
    return round(math.factorial(n) / math.e)                    # Round n!/e to nearest integer → complete D(n)

# Formula: probability of derangement = D(n) / n! → approaches 1/e as n grows
# Returns the probability that a random permutation of n items is a derangement
# Returns 0 if n is zero
def DerangementProbability(n):
    if n <= 0:                                                  # Guard against invalid input
        return 0                                                # Return 0 safely
    return Derangements(n) / math.factorial(n)                  # Divide derangements by total permutations → complete

# ============================================================
# COMBINATIONS
# ============================================================

# Formula: C(n, r) = n! / (r! * (n - r)!)
# Returns the binomial coefficient — number of ways to choose r items from n without regard to order
# Returns 0 if r > n or either is negative
def Combinations(n, r):
    if n < 0 or r < 0 or r > n:                                # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return math.comb(n, r)                                      # Delegate to math.comb → complete C(n,r)

# Formula: C(n + r - 1, r)  (stars and bars)
# Returns the number of ways to choose r items from n with repetition allowed and order irrelevant
# Returns 0 if either is negative
def CombinationsWithRepetition(n, r):
    if n < 0 or r < 0:                                         # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return math.comb(n + r - 1, r)                              # Stars and bars formula → complete C(n+r-1, r)

# Formula: C(n, r) = C(n, n-r)
# Returns True if the two binomial coefficients are equal — symmetry of Pascal's triangle
def CombinationSymmetry(n, r):
    return Combinations(n, r) == Combinations(n, n - r)         # Check both sides of symmetry → complete

# Formula: Pascal's identity — C(n, r) = C(n-1, r-1) + C(n-1, r)
# Returns True if Pascal's identity holds for the given n and r
def PascalsIdentity(n, r):
    if r <= 0 or r >= n:                                        # Edge cases where identity is trivially true
        return True                                             # Return True at boundaries
    return Combinations(n, r) == Combinations(n-1, r-1) + Combinations(n-1, r)  # Verify Pascal's identity → complete

# Formula: Σₖ₌₀ⁿ C(n, k) = 2^n
# Returns the sum of all binomial coefficients for a given n — always equals 2^n
def SumOfCombinations(n):
    if n < 0:                                                   # Guard against negative input
        return 0                                                # Return 0 safely
    return 2 ** n                                               # Sum of row n of Pascal's triangle equals 2^n → complete

# Formula: Vandermonde's identity — C(m+n, r) = Σₖ C(m,k)*C(n,r-k)
# Returns True if Vandermonde's identity holds for the given m, n, r
def VandermondeIdentity(m, n, r):
    left  = Combinations(m + n, r)                              # Left side of identity
    right = sum(Combinations(m, k) * Combinations(n, r - k) for k in range(r + 1))  # Sum of products
    return left == right                                        # Check equality → complete Vandermonde verification

# ============================================================
# PASCAL'S TRIANGLE
# ============================================================

# Formula: row n of Pascal's triangle = [C(n,0), C(n,1), ..., C(n,n)]
# Returns a single row of Pascal's triangle as a list
# Returns [1] for row 0
def PascalRow(n):
    if n < 0:                                                   # Guard against negative row
        return []                                               # Return empty list safely
    return [math.comb(n, k) for k in range(n + 1)]             # Compute each binomial coefficient → complete row

# Formula: full triangle up to row n — list of rows
# Returns Pascal's triangle as a list of lists up to and including row n
def PascalTriangle(n):
    if n < 0:                                                   # Guard against negative input
        return []                                               # Return empty list safely
    return [PascalRow(k) for k in range(n + 1)]                 # Build each row → complete triangle

# Formula: element at row n, column k = C(n, k)
# Returns a single element of Pascal's triangle at the specified position
# Returns 0 if position is out of bounds
def PascalElement(n, k):
    if n < 0 or k < 0 or k > n:                                # Guard against invalid position
        return 0                                                # Return 0 safely
    return math.comb(n, k)                                      # Direct binomial coefficient → complete

# Formula: diagonal sum of Pascal's triangle = Fibonacci numbers
# Returns the nth Fibonacci number using the diagonal sum property of Pascal's triangle
# This is an exact derivation — not an approximation
def PascalDiagonalFibonacci(n):
    if n < 0:                                                   # Guard against negative input
        return 0                                                # Return 0 safely
    total = 0                                                   # Initialize sum accumulator
    k     = 0                                                   # Start at the top of the diagonal
    while n - k >= k:                                           # Walk the diagonal while within triangle bounds
        total += math.comb(n - k, k)                           # Add the element at this diagonal position
        k     += 1                                              # Move to the next diagonal step
    return total                                                # Return complete diagonal sum = Fibonacci(n+1)

# Formula: hockey stick identity — Σₖ₌ᵣⁿ C(k, r) = C(n+1, r+1)
# Returns True if the hockey stick identity holds for the given n and r
def HockeyStickIdentity(n, r):
    if r < 0 or n < r:                                         # Guard against invalid inputs
        return True                                             # Trivially true at boundaries
    left  = sum(math.comb(k, r) for k in range(r, n + 1))      # Sum of the hockey stick column
    right = math.comb(n + 1, r + 1)                             # The handle of the hockey stick
    return left == right                                        # Verify identity → complete

# ============================================================
# BINOMIAL AND MULTINOMIAL THEOREMS
# ============================================================

# Formula: (x + y)^n = Σₖ₌₀ⁿ C(n,k) * x^(n-k) * y^k
# Returns the expanded terms of (x + y)^n as a list of (coefficient, x_power, y_power) tuples
# Each tuple represents one term in the binomial expansion
def BinomialExpansion(n, x = 1, y = 1):
    if n < 0:                                                   # Guard against negative exponent
        return []                                               # Return empty list safely
    terms = []                                                  # Initialize list of expansion terms
    for k in range(n + 1):                                      # Loop through each term in the expansion
        coeff   = math.comb(n, k)                               # Binomial coefficient C(n,k)
        x_power = n - k                                         # Exponent of x in this term
        y_power = k                                             # Exponent of y in this term
        value   = coeff * (x ** x_power) * (y ** y_power)      # Evaluate the term at given x and y
        terms.append((coeff, x_power, y_power, value))          # Append (coefficient, x_exp, y_exp, value)
    return terms                                                # Return complete expansion term list

# Formula: kth term of (x + y)^n = C(n, k) * x^(n-k) * y^k
# Returns the value of a specific term in the binomial expansion (k is 0-indexed)
# Returns 0 if k is out of bounds
def BinomialTerm(n, k, x = 1, y = 1):
    if n < 0 or k < 0 or k > n:                                # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return math.comb(n, k) * (x ** (n - k)) * (y ** k)         # Compute one term → complete C(n,k)*x^(n-k)*y^k

# Formula: (x + y)^n evaluated at x and y = Σ terms
# Returns the value of the full binomial expansion at given x and y — equals (x+y)^n directly
def BinomialExpansionValue(n, x, y):
    if n < 0:                                                   # Guard against negative exponent
        return 0                                                # Return 0 safely
    return (x + y) ** n                                         # Evaluate directly → complete (x+y)^n

# Formula: multinomial coefficient = n! / (k₁! * k₂! * ... * kₘ!)
# Returns the multinomial coefficient for a given list of group sizes
# Counts the number of ways to arrange n items divided into groups of specified sizes
# Returns 0 if group sizes do not sum to n or any is negative
def MultinomialCoefficient(n, groups):
    if any(g < 0 for g in groups):                             # Guard against negative group sizes
        return 0                                                # Return 0 safely
    if sum(groups) != n:                                        # Group sizes must sum to total
        return 0                                                # Return 0 safely — inconsistent inputs
    denominator = 1                                             # Initialize denominator accumulator
    for g in groups:                                            # Multiply factorial of each group size
        denominator *= math.factorial(g)                        # Accumulate denominator product
    return math.factorial(n) // denominator                     # Divide n! by product → complete multinomial coefficient

# Formula: general term of multinomial expansion — coefficient of x₁^k₁ * x₂^k₂ * ... * xₘ^kₘ
# Returns the value of a single multinomial expansion term given the powers of each variable
# powers must sum to n — values is a matching list of variable values
# Returns 0 if powers do not sum to n or lists are mismatched
def MultinomialTerm(n, powers, values):
    if sum(powers) != n:                                        # Guard — powers must sum to n
        return 0                                                # Return 0 safely
    if len(powers) != len(values):                              # Guard against mismatched lists
        return 0                                                # Return 0 safely
    coeff  = MultinomialCoefficient(n, powers)                  # Compute the multinomial coefficient
    product = 1                                                  # Initialize value product accumulator
    for v, p in zip(values, powers):                            # Multiply each value raised to its power
        product *= v ** p                                       # Accumulate variable^power product
    return coeff * product                                      # Multiply coefficient by value product → complete term

# ============================================================
# STIRLING NUMBERS
# ============================================================

# Formula: Stirling numbers of the second kind S(n, k)
# Returns the number of ways to partition a set of n elements into exactly k non-empty subsets
# Uses the explicit formula: S(n,k) = (1/k!) * Σⱼ₌₀ᵏ (-1)^(k-j) * C(k,j) * j^n
# Returns 0 if k > n or either is negative
def StirlingSecond(n, k):
    if n < 0 or k < 0 or k > n:                                # Guard against invalid inputs
        return 0                                                # Return 0 safely
    if k == 0:                                                  # Only one way to partition zero elements into zero subsets
        return 1 if n == 0 else 0                               # S(0,0) = 1, S(n>0, 0) = 0
    total = 0                                                   # Initialize sum accumulator
    for j in range(k + 1):                                      # Sum over j from 0 to k
        sign  = (-1) ** (k - j)                                 # Alternating sign
        total += sign * math.comb(k, j) * (j ** n)             # Add signed term to sum
    return total // math.factorial(k)                           # Divide by k! → complete S(n,k)

# Formula: Stirling numbers of the first kind  (unsigned) c(n, k)
# Returns the number of permutations of n elements with exactly k disjoint cycles
# Uses the recurrence: c(n,k) = c(n-1,k-1) + (n-1)*c(n-1,k)
# Returns 0 if k > n or either is negative
def StirlingFirst(n, k):
    if n < 0 or k < 0 or k > n:                                # Guard against invalid inputs
        return 0                                                # Return 0 safely
    if n == 0 and k == 0:                                       # Base case — one empty permutation
        return 1
    if n == 0 or k == 0:                                        # Other base cases are zero
        return 0
    # Build table bottom-up to avoid deep recursion
    table = [[0] * (n + 1) for _ in range(n + 1)]              # Initialize n+1 by n+1 table with zeros
    table[0][0] = 1                                             # Base case S(0,0) = 1
    for i in range(1, n + 1):                                   # Fill each row
        for j in range(1, i + 1):                               # Fill each column up to the diagonal
            table[i][j] = table[i-1][j-1] + (i-1) * table[i-1][j]  # Apply recurrence relation
    return table[n][k]                                          # Return the computed Stirling number

# Formula: Bell number B(n) = Σₖ₌₀ⁿ S(n,k)
# Returns the Bell number — total number of ways to partition a set of n elements
# B(n) is the sum of all Stirling numbers of the second kind for a given n
def BellNumber(n):
    if n < 0:                                                   # Guard against negative input
        return 0                                                # Return 0 safely
    return sum(StirlingSecond(n, k) for k in range(n + 1))     # Sum all second-kind Stirling numbers → complete B(n)

# ============================================================
# CATALAN NUMBERS AND SPECIAL SEQUENCES
# ============================================================

# Formula: C(n) = C(2n, n) / (n + 1)
# Returns the nth Catalan number — counts many combinatorial structures
# including valid bracket sequences, binary trees, and polygon triangulations
# Returns 0 if n is negative
def CatalanNumber(n):
    if n < 0:                                                   # Guard against negative input
        return 0                                                # Return 0 safely
    return math.comb(2 * n, n) // (n + 1)                       # Binomial coefficient divided by n+1 → complete C(n)

# Formula: F(n) = F(n-1) + F(n-2)  with F(0)=0, F(1)=1
# Returns the nth Fibonacci number using iterative computation
# Returns 0 if n is negative
def Fibonacci(n):
    if n < 0:                                                   # Guard against negative input
        return 0                                                # Return 0 safely
    if n == 0:                                                  # Base case F(0) = 0
        return 0
    if n == 1:                                                  # Base case F(1) = 1
        return 1
    a, b = 0, 1                                                 # Initialize first two Fibonacci values
    for _ in range(2, n + 1):                                   # Iterate from 2 to n
        a, b = b, a + b                                         # Shift values forward — new b = previous a + b
    return b                                                    # Return nth Fibonacci number

# Formula: T(n) = n * (n + 1) / 2
# Returns the nth triangular number — the sum of the first n positive integers
# Returns 0 if n is negative
def TriangularNumber(n):
    if n < 0:                                                   # Guard against negative input
        return 0                                                # Return 0 safely
    return n * (n + 1) // 2                                     # Multiply n by n+1 then halve → complete T(n)

# Formula: P(n) = n * (3n - 1) / 2
# Returns the nth pentagonal number
# Returns 0 if n is negative
def PentagonalNumber(n):
    if n < 0:                                                   # Guard against negative input
        return 0                                                # Return 0 safely
    return n * (3 * n - 1) // 2                                 # Apply pentagonal formula → complete P(n)

# Formula: H(n) = n * (2n - 1)
# Returns the nth hexagonal number
# Returns 0 if n is negative
def HexagonalNumber(n):
    if n < 0:                                                   # Guard against negative input
        return 0                                                # Return 0 safely
    return n * (2 * n - 1)                                      # Apply hexagonal formula → complete H(n)

# Formula: number of lattice paths from (0,0) to (m,n) using right and up steps = C(m+n, m)
# Returns the number of monotone lattice paths from the origin to (m, n)
# Each path consists of exactly m right-steps and n up-steps
# Returns 0 if either is negative
def LatticePaths(m, n):
    if m < 0 or n < 0:                                         # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return math.comb(m + n, m)                                  # Choose m positions for right-steps → complete C(m+n,m)

# Formula: Dyck paths of length 2n = Catalan number C(n)
# Returns the number of valid Dyck paths of length 2n
# A Dyck path never goes below the starting level — equivalent to balanced bracket sequences
def DyckPaths(n):
    if n < 0:                                                   # Guard against negative input
        return 0                                                # Return 0 safely
    return CatalanNumber(n)                                     # Dyck paths of length 2n equals the nth Catalan number → complete

# ============================================================
# SET PARTITIONS AND INCLUSION-EXCLUSION
# ============================================================

# Formula: number of subsets of a set of size n = 2^n
# Returns the total number of subsets (including empty set and full set) of an n-element set
# Returns 0 if n is negative
def NumberOfSubsets(n):
    if n < 0:                                                   # Guard against negative input
        return 0                                                # Return 0 safely
    return 2 ** n                                               # Each element is either in or out → complete 2^n

# Formula: number of non-empty subsets = 2^n - 1
# Returns the total number of non-empty subsets of an n-element set
# Returns 0 if n is negative
def NumberOfNonEmptySubsets(n):
    if n < 0:                                                   # Guard against negative input
        return 0                                                # Return 0 safely
    return 2 ** n - 1                                           # Subtract the empty set → complete 2^n - 1

# Formula: inclusion-exclusion — |A₁ ∪ A₂ ∪ ... ∪ Aₙ| = Σ|Aᵢ| - Σ|Aᵢ∩Aⱼ| + ...
# Returns the size of the union of sets using inclusion-exclusion given a list of individual sizes
# and a list of pairwise intersection sizes
# This simplified version handles two-set and three-set inclusion-exclusion
def InclusionExclusion(sizes, pairwise, triple = 0):
    total = sum(sizes)                                          # Add all individual set sizes
    total -= sum(pairwise)                                      # Subtract all pairwise intersections
    total += triple                                             # Add back the triple intersection if provided
    return total                                                # Return complete inclusion-exclusion result

# Formula: number of onto functions from n elements to k elements = k! * S(n, k)
# Returns the number of surjective (onto) functions from an n-element set to a k-element set
# Returns 0 if k > n or either is negative
def SurjectiveFunctions(n, k):
    if n < 0 or k < 0 or k > n:                                # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return math.factorial(k) * StirlingSecond(n, k)             # Scale Stirling number by k! → complete

# Formula: total functions from n-element set to k-element set = k^n
# Returns the number of all functions (not necessarily onto) from an n-set to a k-set
# Returns 0 if either is negative
def TotalFunctions(n, k):
    if n < 0 or k < 0:                                         # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return k ** n                                               # k choices for each of n elements → complete k^n

# Formula: injective functions from n-set to k-set = P(k, n) = k!/(k-n)!
# Returns the number of injective (one-to-one) functions from an n-set to a k-set
# Returns 0 if n > k or either is negative
def InjectiveFunctions(n, k):
    if n < 0 or k < 0 or n > k:                                # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return Permutations(k, n)                                   # Ordered selection without repetition → complete P(k,n)

# ============================================================
# GENERATING FUNCTIONS AND RECURRENCES
# ============================================================

# Formula: ordinary generating function coefficients — returns first n+1 terms
# Returns the first n+1 coefficients of the OGF for a given sequence formula
# sequence_fn must be a callable accepting a non-negative integer index k
def OGFCoefficients(sequence_fn, n):
    if n < 0:                                                   # Guard against negative n
        return []                                               # Return empty list safely
    return [sequence_fn(k) for k in range(n + 1)]              # Evaluate sequence at each index → complete coefficient list

# Formula: convolution of two sequences — (A*B)[n] = Σₖ₌₀ⁿ A[k] * B[n-k]
# Returns the convolution of two coefficient lists up to the length of the shorter list
# Corresponds to multiplying two ordinary generating functions
def ConvolveSequences(a, b):
    if not a or not b:                                          # Guard against empty inputs
        return []                                               # Return empty list safely
    n      = min(len(a), len(b))                                # Convolve up to the shorter length
    result = []                                                 # Initialize result list
    for i in range(n):                                          # Compute each convolution coefficient
        coeff = sum(a[k] * b[i - k] for k in range(i + 1))     # Sum products of matching index pairs
        result.append(coeff)                                    # Add computed coefficient to result
    return result                                               # Return complete convolution

# Formula: linear recurrence — aₙ = c₁*aₙ₋₁ + c₂*aₙ₋₂ + ... + cₖ*aₙ₋ₖ
# Returns the first n terms of a sequence defined by a linear recurrence
# initial_values is the list of starting values — coefficients is the list of recurrence multipliers
# Returns initial values extended by the recurrence up to n terms total
def LinearRecurrence(initial_values, coefficients, n):
    if not initial_values or not coefficients:                  # Guard against empty inputs
        return []                                               # Return empty list safely
    sequence = initial_values[:]                                # Start with a copy of the initial values
    k        = len(coefficients)                                # Order of the recurrence
    while len(sequence) < n:                                    # Generate terms until we reach n
        next_term = sum(coefficients[i] * sequence[-(i+1)] for i in range(min(k, len(sequence))))  # Apply recurrence
        sequence.append(next_term)                              # Append next computed term
    return sequence[:n]                                         # Return exactly n terms

# Formula: Fibonacci via linear recurrence aₙ = aₙ₋₁ + aₙ₋₂
# Returns the first n Fibonacci numbers as a list using the LinearRecurrence function
def FibonacciSequence(n):
    if n <= 0:                                                  # Guard against non-positive input
        return []                                               # Return empty list safely
    return LinearRecurrence([0, 1], [1, 1], n)                  # Fibonacci recurrence with seed [0,1] → complete

# Formula: Tribonacci — aₙ = aₙ₋₁ + aₙ₋₂ + aₙ₋₃
# Returns the first n Tribonacci numbers — each term is the sum of the three preceding terms
def TribonacciSequence(n):
    if n <= 0:                                                  # Guard against non-positive input
        return []                                               # Return empty list safely
    return LinearRecurrence([0, 0, 1], [1, 1, 1], n)            # Tribonacci recurrence with seed [0,0,1] → complete

# ============================================================
# GRAPH COUNTING
# ============================================================

# Formula: number of labeled graphs on n vertices = 2^C(n,2)
# Returns the number of distinct labeled simple graphs on n vertices
# Each pair of vertices either has an edge or does not → 2 choices per pair
# Returns 0 if n is negative
def LabeledGraphs(n):
    if n < 0:                                                   # Guard against negative input
        return 0                                                # Return 0 safely
    return 2 ** math.comb(n, 2)                                 # One choice per edge → complete 2^C(n,2)

# Formula: number of spanning trees of complete graph Kₙ = n^(n-2)  (Cayley's formula)
# Returns the number of labeled spanning trees of the complete graph on n vertices
# Returns 1 for n = 1 and n = 2 by convention
# Returns 0 if n is less than 1
def SpanningTrees(n):
    if n < 1:                                                   # Guard against invalid input
        return 0                                                # Return 0 safely
    if n <= 2:                                                  # Base cases — one spanning tree for 1 or 2 nodes
        return 1                                                # Return 1
    return n ** (n - 2)                                         # Apply Cayley's formula → complete n^(n-2)

# Formula: number of edges in complete graph Kₙ = C(n, 2) = n*(n-1)/2
# Returns the number of edges in the complete graph on n vertices
# Every pair of vertices is connected by exactly one edge
# Returns 0 if n is less than 2
def CompleteGraphEdges(n):
    if n < 2:                                                   # Guard against fewer than 2 vertices
        return 0                                                # Return 0 safely — no edges possible
    return math.comb(n, 2)                                      # Choose 2 vertices from n → complete C(n,2)

# Formula: chromatic polynomial of complete graph Kₙ at q colors = q * (q-1) * ... * (q-n+1)
# Returns the number of proper colorings of the complete graph Kₙ using q colors
# Each vertex must have a different color — so q must be at least n
# Returns 0 if q < n or either is negative
def CompleteGraphColorings(n, q):
    if n < 0 or q < 0 or q < n:                                # Guard against invalid inputs
        return 0                                                # Return 0 safely — cannot color with fewer colors than vertices
    return FallingFactorial(q, n)                               # q choices for first, q-1 for second, etc. → complete

# Formula: number of simple paths of length k in complete graph Kₙ = P(n, k+1)
# Returns the number of simple paths visiting exactly k+1 vertices in Kₙ
# Returns 0 if k+1 > n or inputs are invalid
def SimplePathsInComplete(n, k):
    if n < 0 or k < 0 or k + 1 > n:                           # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return Permutations(n, k + 1)                               # Choose and order k+1 vertices → complete P(n,k+1)
