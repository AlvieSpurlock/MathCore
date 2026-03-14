import math       # sqrt, log, factorial, gcd
import itertools  # product, combinations for truth tables and set ops

# ============================================================
# PROPOSITIONAL LOGIC
# ============================================================

# Formula: p ∧ q
# Returns True only when both p and q are true
def LogicalAnd(p, q):
    return bool(p) and bool(q)                                  # Both must be true → complete p ∧ q

# Formula: p ∨ q
# Returns True when at least one of p or q is true
def LogicalOr(p, q):
    return bool(p) or bool(q)                                   # Either or both true → complete p ∨ q

# Formula: ¬p
# Returns the logical negation of p
def LogicalNot(p):
    return not bool(p)                                          # Flip truth value → complete ¬p

# Formula: p → q  ≡  ¬p ∨ q
# Returns False only when p is True and q is False — the material conditional
def LogicalImplies(p, q):
    return (not bool(p)) or bool(q)                             # False only when premise true, conclusion false

# Formula: p ↔ q  ≡  (p → q) ∧ (q → p)
# Returns True when p and q have the same truth value
def LogicalBiconditional(p, q):
    return bool(p) == bool(q)                                   # True iff both same value → complete p ↔ q

# Formula: ¬(p ∧ q)
# Returns False only when both p and q are True
def LogicalNand(p, q):
    return not (bool(p) and bool(q))                            # Negate the conjunction → complete p ↑ q

# Formula: ¬(p ∨ q)
# Returns True only when both p and q are False
def LogicalNor(p, q):
    return not (bool(p) or bool(q))                             # Negate the disjunction → complete p ↓ q

# Formula: p ⊕ q  ≡  (p ∨ q) ∧ ¬(p ∧ q)
# Returns True when exactly one of p or q is True — exclusive or
def LogicalXor(p, q):
    return bool(p) != bool(q)                                   # Different truth values → complete p ⊕ q

# Formula: ¬(p ⊕ q)  ≡  p ↔ q
# Returns True when p and q have the same truth value — logical equivalence
def LogicalXnor(p, q):
    return bool(p) == bool(q)                                   # Same truth values → complete XNOR

# Formula: ¬p ∧ ¬q  ≡  ¬(p ∨ q)  [De Morgan's law verification]
# Returns True only when both p and q are False — confirms De Morgan's NOR identity
def DeMorgansNor(p, q):
    nor    = not (bool(p) or bool(q))                           # Compute ¬(p ∨ q) directly
    demorg = (not bool(p)) and (not bool(q))                    # Compute ¬p ∧ ¬q via De Morgan's law
    return nor, demorg, nor == demorg                           # Return both sides and whether they match

# Formula: ¬p ∨ ¬q  ≡  ¬(p ∧ q)  [De Morgan's law verification]
# Returns True only when at least one of p or q is False — confirms De Morgan's NAND identity
def DeMorgansNand(p, q):
    nand   = not (bool(p) and bool(q))                          # Compute ¬(p ∧ q) directly
    demorg = (not bool(p)) or (not bool(q))                     # Compute ¬p ∨ ¬q via De Morgan's law
    return nand, demorg, nand == demorg                         # Return both sides and whether they match

# Formula: enumerate all 2^n truth assignments for n variables
# Returns a list of (assignment_tuple, result) pairs for a boolean function
# fn must accept n positional boolean arguments
def TruthTable(fn, n_vars):
    rows = []
    for assignment in itertools.product([False, True], repeat=n_vars):   # All 2^n combinations
        result = fn(*assignment)                                # Evaluate function on this row
        rows.append((assignment, bool(result)))                 # Store (inputs, output)
    return rows                                                 # Complete truth table

# Formula: a formula is a tautology iff it is True under every possible truth assignment
# Returns True if fn evaluates True for all 2^n_vars combinations
def IsTautology(fn, n_vars):
    return all(fn(*a) for a in itertools.product([False, True], repeat=n_vars))

# Formula: a formula is a contradiction iff it is False under every truth assignment
# Returns True if fn evaluates False for every combination
def IsContradiction(fn, n_vars):
    return not any(fn(*a) for a in itertools.product([False, True], repeat=n_vars))

# Formula: a formula is satisfiable iff there exists at least one True assignment
# Returns True if fn evaluates True for at least one combination
def IsSatisfiable(fn, n_vars):
    return any(fn(*a) for a in itertools.product([False, True], repeat=n_vars))

# Formula: two formulae φ and ψ are logically equivalent iff φ ↔ ψ is a tautology
# Returns True if fn1 and fn2 agree on every truth assignment
def AreLogicallyEquivalent(fn1, fn2, n_vars):
    for assignment in itertools.product([False, True], repeat=n_vars):
        if bool(fn1(*assignment)) != bool(fn2(*assignment)):    # Any mismatch → not equivalent
            return False
    return True                                                 # Same on every row → logically equivalent

# ============================================================
# PREDICATE LOGIC
# ============================================================

# Formula: ∀x ∈ domain : P(x)
# Returns True if predicate_fn returns True for every element in domain
def UniversalQuantifier(predicate_fn, domain):
    return all(bool(predicate_fn(x)) for x in domain)          # Must hold for all elements → ∀x P(x)

# Formula: ∃x ∈ domain : P(x)
# Returns True if predicate_fn returns True for at least one element in domain
def ExistentialQuantifier(predicate_fn, domain):
    return any(bool(predicate_fn(x)) for x in domain)          # At least one witness → ∃x P(x)

# Formula: ∃!x ∈ domain : P(x)
# Returns True if predicate_fn returns True for exactly one element in domain
def UniqueExistential(predicate_fn, domain):
    count = sum(1 for x in domain if bool(predicate_fn(x)))    # Count satisfying elements
    return count == 1                                           # Unique if exactly one → ∃!x P(x)

# Returns all elements of domain that satisfy the predicate — extension of the predicate
def PredicateExtension(predicate_fn, domain):
    return [x for x in domain if bool(predicate_fn(x))]        # Filter to satisfying elements

# Formula: ¬∀x P(x)  ≡  ∃x ¬P(x)
# Returns the counterexample witnessing the failure of a universal statement, or None if it holds
def UniversalCounterexample(predicate_fn, domain):
    for x in domain:
        if not bool(predicate_fn(x)):                          # First failure is the counterexample
            return x
    return None                                                 # None means ∀x P(x) holds

# ============================================================
# SET THEORY
# ============================================================

# Formula: A ∪ B  — all elements in A, B, or both
# Returns the union of sets A and B as a Python set
def SetUnion(A, B):
    return set(A) | set(B)                                      # Pipe operator → complete A ∪ B

# Formula: A ∩ B  — only elements in both A and B
# Returns the intersection of sets A and B
def SetIntersection(A, B):
    return set(A) & set(B)                                      # Ampersand operator → complete A ∩ B

# Formula: A \ B  — elements in A that are not in B
# Returns the set difference A minus B
def SetDifference(A, B):
    return set(A) - set(B)                                      # Minus operator → complete A \ B

# Formula: A △ B  ≡  (A \ B) ∪ (B \ A)
# Returns elements in exactly one of A or B — symmetric difference
def SymmetricDifference(A, B):
    return set(A) ^ set(B)                                      # XOR operator on sets → complete A △ B

# Formula: Aᶜ  ≡  U \ A  — all elements in the universal set but not in A
# Returns the complement of A relative to a given universal set
def SetComplement(A, universal):
    return set(universal) - set(A)                              # Remove A elements from universe → Aᶜ

# Formula: A ⊆ B  iff every element of A is also in B
# Returns True if A is a subset of B (including equal sets)
def IsSubset(A, B):
    return set(A) <= set(B)                                     # Subset check via ≤ operator

# Formula: A ⊂ B  iff A ⊆ B and A ≠ B
# Returns True if A is a proper subset of B — strictly contained
def IsProperSubset(A, B):
    return set(A) < set(B)                                      # Strict subset via < operator

# Formula: 𝒫(A)  — the set of all subsets of A, including ∅ and A itself
# Returns a list of frozensets representing all 2^|A| subsets of A
def PowerSet(A):
    A = list(A)
    result = []
    for r in range(len(A) + 1):                                 # Subsets of each size 0 to |A|
        for combo in itertools.combinations(A, r):
            result.append(frozenset(combo))                     # Store as frozenset for hashability
    return result                                               # Complete 𝒫(A) with 2^|A| elements

# Formula: A × B  ≡  { (a, b) | a ∈ A, b ∈ B }
# Returns the Cartesian product as a list of ordered pairs
def CartesianProduct(A, B):
    return [(a, b) for a in A for b in B]                      # All ordered pairs → complete A × B

# Formula: |A|  — the number of elements in A
# Returns the cardinality of set A
def Cardinality(A):
    return len(set(A))                                          # Count distinct elements → |A|

# Formula: A ∩ B = ∅
# Returns True if A and B share no elements — they are disjoint
def AreDisjoint(A, B):
    return len(set(A) & set(B)) == 0                           # Empty intersection → disjoint

# Formula: a partition of A is a collection of non-empty, pairwise disjoint sets whose union is A
# partition is a list of sets; returns True if they form a valid partition of A
def IsValidPartition(A, partition):
    A = set(A)
    union    = set()
    for part in partition:
        part = set(part)
        if len(part) == 0:                                      # Empty part → not a valid partition
            return False
        if not AreDisjoint(union, part):                        # Overlapping parts → invalid
            return False
        union |= part
    return union == A                                           # Must cover exactly A

# ============================================================
# RELATIONS
# ============================================================

# A relation R on domain is represented as a set of (a, b) tuples

# Formula: R is reflexive iff (a, a) ∈ R for every a in domain
def IsReflexive(relation, domain):
    relation = set(relation)
    return all((a, a) in relation for a in domain)              # Every element must relate to itself

# Formula: R is irreflexive iff (a, a) ∉ R for every a in domain
def IsIrreflexive(relation, domain):
    relation = set(relation)
    return all((a, a) not in relation for a in domain)          # No element relates to itself

# Formula: R is symmetric iff (a, b) ∈ R → (b, a) ∈ R
def IsSymmetric(relation, domain):
    relation = set(relation)
    return all((b, a) in relation for (a, b) in relation)       # Every pair must have its reverse

# Formula: R is antisymmetric iff (a, b) ∈ R ∧ (b, a) ∈ R → a = b
def IsAntisymmetric(relation, domain):
    relation = set(relation)
    for (a, b) in relation:
        if a != b and (b, a) in relation:                       # Mutual non-equal pair violates antisymmetry
            return False
    return True

# Formula: R is asymmetric iff (a, b) ∈ R → (b, a) ∉ R
def IsAsymmetric(relation, domain):
    relation = set(relation)
    return all((b, a) not in relation for (a, b) in relation)   # No pair can have its reverse

# Formula: R is transitive iff (a, b) ∈ R ∧ (b, c) ∈ R → (a, c) ∈ R
def IsTransitive(relation, domain):
    relation = set(relation)
    for (a, b) in relation:
        for (c, d) in relation:
            if b == c and (a, d) not in relation:               # Gap in chain → not transitive
                return False
    return True

# Formula: R is an equivalence relation iff it is reflexive, symmetric, and transitive
# Returns True and three individual checks
def IsEquivalenceRelation(relation, domain):
    ref  = IsReflexive(relation, domain)
    sym  = IsSymmetric(relation, domain)
    tran = IsTransitive(relation, domain)
    return ref and sym and tran, ref, sym, tran                 # Overall result plus individual checks

# Formula: R is a partial order iff it is reflexive, antisymmetric, and transitive
# Returns True and three individual checks
def IsPartialOrder(relation, domain):
    ref   = IsReflexive(relation, domain)
    anti  = IsAntisymmetric(relation, domain)
    tran  = IsTransitive(relation, domain)
    return ref and anti and tran, ref, anti, tran

# Formula: R is a total order iff it is a partial order and every pair is comparable
# (a, b) or (b, a) must be in R for every distinct a, b in domain
def IsTotalOrder(relation, domain):
    is_po, ref, anti, tran = IsPartialOrder(relation, domain)
    if not is_po:
        return False, ref, anti, tran, False
    relation = set(relation)
    domain   = list(domain)
    total    = all(
        (a, b) in relation or (b, a) in relation
        for i, a in enumerate(domain) for b in domain[i+1:]
    )
    return is_po and total, ref, anti, tran, total

# Formula: R ∘ S  — (a, c) ∈ R∘S iff ∃b : (a, b) ∈ S ∧ (b, c) ∈ R
# Returns the composition of relations R and S (R applied after S)
def RelationComposition(R, S):
    R = set(R); S = set(S)
    return {(a, c) for (a, b1) in S for (b2, c) in R if b1 == b2}   # Bridge through shared middle element

# Formula: equivalence classes partition domain into groups of mutually related elements
# Returns a list of frozensets — each is one equivalence class
def EquivalenceClasses(relation, domain):
    relation = set(relation)
    domain   = set(domain)
    classes  = []
    visited  = set()
    for a in domain:
        if a in visited:
            continue
        cls = frozenset(b for b in domain if (a, b) in relation and (b, a) in relation)
        if cls:
            classes.append(cls)
            visited |= cls
    return classes                                              # Complete list of equivalence classes

# Formula: transitive closure R⁺ — add (a, c) whenever (a, b) and (b, c) are in R
# Uses Warshall's algorithm; returns the transitive closure as a set of pairs
def TransitiveClosure(relation, domain):
    domain   = list(domain)
    n        = len(domain)
    idx      = {v: i for i, v in enumerate(domain)}            # Map elements to indices
    reach    = [[False] * n for _ in range(n)]
    for (a, b) in relation:
        if a in idx and b in idx:
            reach[idx[a]][idx[b]] = True                        # Seed reachability matrix
    for k in range(n):                                          # Warshall: try each intermediate vertex
        for i in range(n):
            for j in range(n):
                reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])
    return {(domain[i], domain[j]) for i in range(n) for j in range(n) if reach[i][j]}

# Formula: reflexive closure — add (a, a) for every a not already self-related
def ReflexiveClosure(relation, domain):
    return set(relation) | {(a, a) for a in domain}            # Union with identity pairs

# Formula: symmetric closure — add (b, a) for every (a, b) present
def SymmetricClosure(relation):
    R = set(relation)
    return R | {(b, a) for (a, b) in R}                        # Add reverses of all pairs

# ============================================================
# FUNCTIONS
# ============================================================

# A function is represented as a dict {input: output}
# domain and codomain are sets or lists

# Formula: f is injective (one-to-one) iff f(a) = f(b) → a = b
# Returns True if no two distinct inputs map to the same output
def IsInjective(function_dict, domain, codomain):
    values = [function_dict[x] for x in domain if x in function_dict]
    return len(values) == len(set(values))                      # All outputs distinct → injective

# Formula: f is surjective (onto) iff every element of codomain has a preimage in domain
# Returns True if the image of domain covers the entire codomain
def IsSurjective(function_dict, domain, codomain):
    image = {function_dict[x] for x in domain if x in function_dict}
    return image == set(codomain)                               # Image equals codomain → surjective

# Formula: f is bijective iff it is both injective and surjective
def IsBijective(function_dict, domain, codomain):
    return (IsInjective(function_dict, domain, codomain) and
            IsSurjective(function_dict, domain, codomain))     # Both properties → bijective

# Formula: (f ∘ g)(x)  ≡  f(g(x))
# Returns a new dict representing the composition of f and g over domain
# g is applied first, then f
def FunctionComposition(f, g, domain):
    result = {}
    for x in domain:
        if x in g and g[x] in f:
            result[x] = f[g[x]]                                 # Chain g then f → complete f ∘ g
    return result

# Formula: f⁻¹ exists iff f is bijective — swaps keys and values
# Returns the inverse function dict, or None if f is not bijective
def FunctionInverse(function_dict, domain, codomain):
    if not IsBijective(function_dict, domain, codomain):
        return None                                             # Inverse only defined for bijections
    return {v: k for k, v in function_dict.items()}            # Swap keys and values → f⁻¹

# Formula: the image of a function is the set of all output values
def FunctionImage(function_dict, domain):
    return {function_dict[x] for x in domain if x in function_dict}

# Formula: the preimage of y under f is {x ∈ domain | f(x) = y}
def FunctionPreimage(function_dict, y, domain):
    return {x for x in domain if function_dict.get(x) == y}    # All inputs mapping to y

# Formula: total number of functions from an n-set to an m-set = mⁿ
# Returns mⁿ — the count of all possible functions between two finite sets
def NumberOfFunctions(n, m):
    return m ** n                                               # Each of n inputs has m choices

# Formula: number of injections from an n-set to an m-set = P(m, n) = m!/(m−n)!
# Returns 0 if n > m (cannot inject a larger set into a smaller one)
def NumberOfInjections(n, m):
    if n > m:
        return 0                                                # Pigeonhole — no injection possible
    result = 1
    for i in range(n):
        result *= (m - i)                                       # m * (m-1) * ... * (m-n+1) → P(m,n)
    return result

# Formula: number of bijections between two n-sets = n!
def NumberOfBijections(n):
    return math.factorial(n)                                    # Every bijection is a permutation → n!

# ============================================================
# NUMBER THEORY
# ============================================================

# Formula: a | b  iff  b mod a = 0
# Returns True if a divides b evenly
def IsDivisible(b, a):
    if a == 0:                                                  # Division by zero is undefined
        return False
    return b % a == 0                                           # Remainder zero → a | b

# Formula: gcd(a, b) via Euclidean algorithm — largest integer dividing both a and b
def GCD(a, b):
    a, b = abs(a), abs(b)
    while b:                                                    # Euclidean algorithm
        a, b = b, a % b                                         # Replace (a, b) with (b, a mod b)
    return a                                                    # When b=0, a holds the gcd

# Formula: lcm(a, b)  ≡  |a * b| / gcd(a, b)
# Returns the least common multiple of a and b
def LCM(a, b):
    if a == 0 or b == 0:
        return 0                                                # LCM with zero is zero
    return abs(a * b) // GCD(a, b)                             # Divide product by gcd → lcm

# Formula: Extended Euclidean algorithm — finds x, y s.t. ax + by = gcd(a, b)
# Returns (gcd, x, y) satisfying the Bézout identity
def ExtendedGCD(a, b):
    if b == 0:
        return a, 1, 0                                          # Base case: gcd(a,0)=a with 1*a+0*0=a
    gcd, x1, y1 = ExtendedGCD(b, a % b)                       # Recurse
    x = y1                                                      # Back-substitute
    y = x1 - (a // b) * y1
    return gcd, x, y                                            # Complete Bézout coefficients

# Returns True if n is a prime number — only divisors are 1 and itself
def IsPrime(n):
    if n < 2:
        return False                                            # 0 and 1 are not prime
    if n == 2:
        return True                                             # 2 is the only even prime
    if n % 2 == 0:
        return False                                            # All other even numbers are composite
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:                                          # Found a factor → not prime
            return False
    return True                                                 # No factor found → prime

# Formula: prime factorization — express n as a product of prime powers
# Returns a list of (prime, exponent) pairs in ascending order of prime
def PrimeFactorization(n):
    if n < 2:
        return []                                               # No prime factors for 0 or 1
    factors = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            exp = 0
            while n % d == 0:
                exp += 1
                n //= d                                         # Divide out all copies of d
            factors.append((d, exp))                            # Record (prime, exponent)
        d += 1
    if n > 1:
        factors.append((n, 1))                                  # Remaining factor is prime
    return factors                                              # Complete factorization

# Formula: Sieve of Eratosthenes — all primes up to and including n
# Returns a sorted list of all primes ≤ n
def Primes(n):
    if n < 2:
        return []
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(math.sqrt(n)) + 1):
        if sieve[i]:
            for j in range(i * i, n + 1, i):
                sieve[j] = False                                # Mark multiples as composite
    return [i for i in range(2, n + 1) if sieve[i]]            # Collect surviving primes

# Formula: φ(n) = n · ∏(1 − 1/p) for each prime p dividing n
# Returns Euler's totient — the count of integers from 1 to n coprime to n
def EulersTotient(n):
    if n <= 0:
        return 0
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p                               # Apply multiplicative reduction
        p += 1
    if temp > 1:
        result -= result // temp                                # Final prime factor
    return result                                               # Complete φ(n)

# Formula: d(n) — number of positive divisors of n
# Returns the count of integers from 1 to n that divide n evenly
def DivisorCount(n):
    if n <= 0:
        return 0
    count = 0
    for i in range(1, int(math.sqrt(n)) + 1):
        if n % i == 0:
            count += 2 if i != n // i else 1                   # Count both i and n/i unless equal
    return count

# Formula: σ(n) — sum of all positive divisors of n
# Returns the sum of integers from 1 to n that divide n evenly
def DivisorSum(n):
    if n <= 0:
        return 0
    total = 0
    for i in range(1, int(math.sqrt(n)) + 1):
        if n % i == 0:
            total += i
            if i != n // i:
                total += n // i                                 # Add both i and n/i unless equal
    return total

# Formula: n is perfect iff σ(n) − n = n  ↔  σ(n) = 2n
# Returns True if the sum of proper divisors of n equals n
def IsPerfect(n):
    if n <= 1:
        return False
    return DivisorSum(n) - n == n                               # Proper divisor sum equals n → perfect

# Formula: (a + b) mod m
def ModularAdd(a, b, m):
    return (a + b) % m                                          # Reduce sum modulo m

# Formula: (a − b) mod m
def ModularSubtract(a, b, m):
    return (a - b) % m                                          # Reduce difference modulo m (Python % always ≥ 0)

# Formula: (a · b) mod m
def ModularMultiply(a, b, m):
    return (a * b) % m                                          # Reduce product modulo m

# Formula: aⁿ mod m using repeated squaring — O(log n) time
def ModularPower(base, exp, mod):
    return pow(int(base), int(exp), int(mod))                   # Python built-in uses fast exponentiation

# Formula: modular inverse x s.t. ax ≡ 1 (mod m) — exists iff gcd(a, m) = 1
# Returns x such that a*x ≡ 1 (mod m), or None if the inverse does not exist
def ModularInverse(a, m):
    gcd, x, _ = ExtendedGCD(a % m, m)
    if gcd != 1:
        return None                                             # No inverse when gcd ≠ 1
    return x % m                                               # Ensure positive result

# Formula: a ≡ b (mod m)  iff  m | (a − b)
# Returns True if a and b are congruent modulo m
def IsCongruent(a, b, m):
    return (a - b) % m == 0                                    # Congruent iff difference divisible by m

# Formula: ax ≡ b (mod m) — linear congruence
# Returns a list of all solutions x in [0, m), or empty list if no solution exists
# Solutions exist iff gcd(a, m) | b; there are gcd(a, m) distinct solutions mod m
def LinearCongruence(a, b, m):
    g = GCD(a, m)
    if b % g != 0:
        return []                                               # No solution when gcd does not divide b
    a, b, m = a // g, b // g, m // g                           # Reduce to simpler congruence
    inv = ModularInverse(a, m)
    if inv is None:
        return []
    x0 = (inv * b) % m
    g_orig = GCD(a * g, m * g) if g > 1 else g
    return [(x0 + k * m) % (m * g) for k in range(g)]         # All g distinct solutions

# Formula: Fermat's Little Theorem — if p is prime and p ∤ a, then aᵖ⁻¹ ≡ 1 (mod p)
# Returns (lhs, rhs, holds) verifying the congruence
def FermatsLittleTheorem(a, p):
    if not IsPrime(p):
        return None, None, False                                # Theorem only applies to primes
    lhs = ModularPower(a, p - 1, p)
    return lhs, 1, lhs == 1                                    # aᵖ⁻¹ mod p should equal 1

# Formula: Wilson's Theorem — p is prime iff (p−1)! ≡ −1 (mod p)
# Returns (lhs_mod_p, p-1, holds) for the given p
def WilsonsTheorem(p):
    if p < 2:
        return None, None, False
    lhs = math.factorial(p - 1) % p
    return lhs, (p - 1) % p, lhs == (p - 1) % p              # (p−1)! ≡ p−1 ≡ −1 (mod p)

# Formula: Chinese Remainder Theorem — find x s.t. x ≡ rᵢ (mod mᵢ) for all i
# remainders and moduli are equal-length lists; moduli must be pairwise coprime
# Returns the unique solution x in [0, M) where M = ∏mᵢ, or None if moduli not coprime
def ChineseRemainderTheorem(remainders, moduli):
    M = 1
    for m in moduli:
        M *= m                                                  # Product of all moduli
    x = 0
    for r, m in zip(remainders, moduli):
        Mi  = M // m                                            # M without this modulus
        inv = ModularInverse(Mi, m)
        if inv is None:
            return None                                         # Moduli must be pairwise coprime
        x += r * Mi * inv                                       # Contribute this residue's term
    return x % M                                               # Complete CRT solution

# ============================================================
# SEQUENCES AND RECURRENCES
# ============================================================

# Formula: aₙ = a + (n − 1)d  — nth term of an arithmetic sequence
# a is the first term, d the common difference, n is 1-indexed
def ArithmeticTerm(a, d, n):
    return a + (n - 1) * d                                     # Shift by (n-1) steps of size d

# Formula: Sₙ = n/2 · (2a + (n−1)d)  — sum of first n terms of an arithmetic sequence
def ArithmeticSum(a, d, n):
    return n * (2 * a + (n - 1) * d) / 2                      # Average of first and last times count

# Formula: aₙ = a · rⁿ⁻¹  — nth term of a geometric sequence (1-indexed)
def GeometricTerm(a, r, n):
    return a * (r ** (n - 1))                                  # Scale first term by ratio to the (n-1)th power

# Formula: Sₙ = a(rⁿ − 1)/(r − 1) for r ≠ 1, else Sₙ = n·a
# Returns the sum of the first n terms of a geometric sequence
def GeometricSum(a, r, n):
    if r == 1:
        return a * n                                            # Constant sequence → just multiply
    return a * (r ** n - 1) / (r - 1)                         # Standard geometric sum formula

# Formula: S∞ = a/(1 − r) for |r| < 1  — infinite geometric series
# Returns None if |r| ≥ 1 (series diverges)
def InfiniteGeometricSum(a, r):
    if abs(r) >= 1:
        return None                                             # Diverges — no finite sum
    return a / (1 - r)                                         # Complete infinite sum formula

# Formula: solve linear recurrence aₙ = c₁aₙ₋₁ + c₂aₙ₋₂ + ... with given initial values
# initial_values: list of known terms starting at a₀; coefficients: [c₁, c₂, ...]
# Returns the value of the nth term (0-indexed)
def LinearRecurrenceNthTerm(initial_values, coefficients, n):
    order  = len(coefficients)
    terms  = list(initial_values[:order])                       # Seed with initial values
    if n < order:
        return initial_values[n]                                # Already known
    for _ in range(n - order + 1):
        next_term = sum(coefficients[i] * terms[-(i+1)] for i in range(order))
        terms.append(next_term)
        if len(terms) > order:
            terms.pop(0)                                        # Keep only latest `order` terms
    return next_term                                            # Complete nth term

# Formula: arithmetic mean of a sequence
def SequenceMean(sequence):
    if not sequence:
        return 0
    return sum(sequence) / len(sequence)                       # Sum divided by count

# Formula: detect if a sequence is arithmetic — constant differences
# Returns (is_arithmetic, common_difference or None)
def IsArithmetic(sequence):
    if len(sequence) < 2:
        return True, None
    d = sequence[1] - sequence[0]
    for i in range(2, len(sequence)):
        if sequence[i] - sequence[i-1] != d:
            return False, None                                  # Inconsistent difference → not arithmetic
    return True, d

# Formula: detect if a sequence is geometric — constant ratios
# Returns (is_geometric, common_ratio or None)
def IsGeometric(sequence):
    if len(sequence) < 2:
        return True, None
    if sequence[0] == 0:
        return False, None                                      # Cannot compute ratio from zero
    r = sequence[1] / sequence[0]
    for i in range(2, len(sequence)):
        if sequence[i-1] == 0:
            return False, None
        if abs(sequence[i] / sequence[i-1] - r) > 1e-9:       # Float comparison with tolerance
            return False, None
    return True, r

# ============================================================
# GRAPH THEORY
# ============================================================

# Graphs are represented as adjacency dicts: {vertex: [neighbor, ...]}
# Weighted graphs use: {vertex: [(neighbor, weight), ...]}

# Returns the degree of vertex v in an unweighted adjacency list
def VertexDegree(adjacency, v):
    return len(adjacency.get(v, []))                           # Count neighbours

# Returns a sorted list of all vertex degrees — the degree sequence
def DegreeSequence(adjacency):
    return sorted(len(neighbors) for neighbors in adjacency.values())

# Formula: sum of degrees = 2 · |E| (handshaking lemma)
# Returns the number of edges implied by the adjacency list
def EdgeCount(adjacency):
    return sum(len(neighbors) for neighbors in adjacency.values()) // 2

# Returns True if the graph has an Euler circuit — every vertex has even degree and graph is connected
def IsEulerian(adjacency):
    if not IsConnected(adjacency):
        return False
    return all(len(neighbors) % 2 == 0 for neighbors in adjacency.values())

# Returns True if the graph has an Euler path but not a circuit — exactly 2 odd-degree vertices
def IsSemiEulerian(adjacency):
    if not IsConnected(adjacency):
        return False
    odd_count = sum(1 for neighbors in adjacency.values() if len(neighbors) % 2 != 0)
    return odd_count == 2                                       # Exactly two odd-degree endpoints

# BFS connectivity check — returns True if all vertices can be reached from any start vertex
def IsConnected(adjacency):
    if not adjacency:
        return True
    start   = next(iter(adjacency))
    visited = set()
    queue   = [start]
    while queue:
        v = queue.pop(0)
        if v in visited:
            continue
        visited.add(v)
        for neighbor in adjacency.get(v, []):
            if neighbor not in visited:
                queue.append(neighbor)
    return visited == set(adjacency.keys())                    # Must reach every vertex

# Returns True if graph is complete — every pair of distinct vertices is adjacent
def IsComplete(adjacency):
    n = len(adjacency)
    return all(len(neighbors) == n - 1 for neighbors in adjacency.values())

# Formula: a graph is bipartite iff it has no odd-length cycle — check via 2-colouring
# Returns (is_bipartite, partition_A, partition_B) or (False, None, None)
def IsBipartite(adjacency):
    color  = {}
    for start in adjacency:
        if start in color:
            continue
        queue = [start]
        color[start] = 0
        while queue:
            v = queue.pop(0)
            for neighbor in adjacency.get(v, []):
                if neighbor not in color:
                    color[neighbor] = 1 - color[v]             # Alternate colours
                    queue.append(neighbor)
                elif color[neighbor] == color[v]:              # Same colour → odd cycle
                    return False, None, None
    A = {v for v, c in color.items() if c == 0}
    B = {v for v, c in color.items() if c == 1}
    return True, A, B

# BFS traversal — returns vertices in breadth-first order starting from start
def BFS(adjacency, start):
    visited = []
    seen    = set()
    queue   = [start]
    seen.add(start)
    while queue:
        v = queue.pop(0)
        visited.append(v)
        for neighbor in sorted(adjacency.get(v, [])):          # Sort for determinism
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return visited

# DFS traversal — returns vertices in depth-first order starting from start
def DFS(adjacency, start):
    visited = []
    seen    = set()
    def _dfs(v):
        seen.add(v)
        visited.append(v)
        for neighbor in sorted(adjacency.get(v, [])):
            if neighbor not in seen:
                _dfs(neighbor)
    _dfs(start)
    return visited

# Formula: Dijkstra's shortest path algorithm on a weighted adjacency list
# adjacency: {v: [(neighbor, weight), ...]}
# Returns (distance, path) from start to end, or (inf, []) if unreachable
def ShortestPath(adjacency, start, end):
    import heapq
    dist  = {v: float('inf') for v in adjacency}
    dist[start] = 0
    prev  = {v: None for v in adjacency}
    heap  = [(0, start)]
    while heap:
        d, v = heapq.heappop(heap)
        if d > dist[v]:
            continue
        for neighbor, weight in adjacency.get(v, []):
            nd = d + weight
            if nd < dist[neighbor]:
                dist[neighbor] = nd
                prev[neighbor] = v
                heapq.heappush(heap, (nd, neighbor))
    path = []
    v = end
    while v is not None:
        path.append(v)
        v = prev[v]
    path.reverse()
    if path[0] != start:
        return float('inf'), []                                 # Unreachable
    return dist.get(end, float('inf')), path

# Formula: Kruskal's MST algorithm
# edges: list of (weight, u, v); vertices: set of all vertex labels
# Returns (total_weight, [(u, v, weight), ...]) — the MST edge list
def MinimumSpanningTree(edges, vertices):
    parent = {v: v for v in vertices}
    rank   = {v: 0 for v in vertices}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return False
        if rank[rx] < rank[ry]:
            rx, ry = ry, rx
        parent[ry] = rx
        if rank[rx] == rank[ry]:
            rank[rx] += 1
        return True

    mst_weight = 0
    mst_edges  = []
    for weight, u, v in sorted(edges):
        if union(u, v):
            mst_weight += weight
            mst_edges.append((u, v, weight))
    return mst_weight, mst_edges

# Formula: greedy graph colouring — assigns each vertex the smallest colour not used by its neighbours
# Returns a dict {vertex: colour_number} — colour numbers start at 0
def GreedyColoring(adjacency):
    color = {}
    for v in adjacency:
        neighbor_colors = {color[n] for n in adjacency[v] if n in color}
        c = 0
        while c in neighbor_colors:
            c += 1                                              # Find smallest unused colour
        color[v] = c
    return color

# Returns the number of colours used by greedy colouring — an upper bound on chromatic number
def ChromaticNumberBound(adjacency):
    coloring = GreedyColoring(adjacency)
    return max(coloring.values()) + 1 if coloring else 0

# ============================================================
# TREES
# ============================================================

# A tree is represented as an adjacency dict (undirected)
# A rooted tree may also be given as a parent dict or children dict

# Formula: a connected graph on n vertices is a tree iff it has exactly n−1 edges
def IsTree(adjacency):
    n = len(adjacency)
    e = EdgeCount(adjacency)
    return IsConnected(adjacency) and e == n - 1               # Connected + n-1 edges → tree

# Returns the height of a rooted tree (length of longest root-to-leaf path)
def TreeHeight(children, root):
    if not children.get(root):
        return 0                                                # Leaf node has height 0
    return 1 + max(TreeHeight(children, child) for child in children[root])

# Returns a list of leaf nodes (nodes with no children) in a rooted tree
def TreeLeaves(children, all_nodes):
    return [v for v in all_nodes if not children.get(v)]       # Leaves have empty children list

# Preorder traversal: root, then recursively each subtree left-to-right
def PreorderTraversal(children, root):
    result = [root]
    for child in children.get(root, []):
        result.extend(PreorderTraversal(children, child))
    return result

# Postorder traversal: children first, then root
def PostorderTraversal(children, root):
    result = []
    for child in children.get(root, []):
        result.extend(PostorderTraversal(children, child))
    result.append(root)
    return result

# Inorder traversal: left subtree, root, right subtree (binary trees — exactly 2 or 0 children)
def InorderTraversal(children, root):
    kids = children.get(root, [])
    if not kids:
        return [root]
    if len(kids) == 1:
        return InorderTraversal(children, kids[0]) + [root]
    return (InorderTraversal(children, kids[0]) +
            [root] +
            InorderTraversal(children, kids[1]))

# Formula: Cayley's formula — the number of labeled trees on n vertices = nⁿ⁻²
def NumberOfLabeledTrees(n):
    if n <= 0:
        return 0
    if n == 1:
        return 1
    if n == 2:
        return 1
    return n ** (n - 2)                                        # Cayley's formula: nⁿ⁻²

# Formula: Prüfer sequence encodes a labeled tree uniquely as a sequence of length n−2
# tree_edges: list of (u, v) for a labeled tree on vertices 1..n
# Returns the Prüfer sequence as a list
def PruferSequence(tree_edges, n):
    from collections import defaultdict
    degree = defaultdict(int)
    adj    = defaultdict(set)
    for u, v in tree_edges:
        adj[u].add(v); adj[v].add(u)
        degree[u] += 1; degree[v] += 1
    seq = []
    for _ in range(n - 2):
        leaf = min(v for v in range(1, n + 1) if degree[v] == 1)  # Smallest leaf
        neighbor = next(iter(adj[leaf]))
        seq.append(neighbor)
        adj[leaf].remove(neighbor); adj[neighbor].remove(leaf)
        degree[leaf] -= 1; degree[neighbor] -= 1
    return seq

# Formula: reconstruct a labeled tree from its Prüfer sequence
# Returns a list of (u, v) edges
def PruferToTree(prufer_seq):
    n      = len(prufer_seq) + 2
    degree = [1] * (n + 1)
    for v in prufer_seq:
        degree[v] += 1                                          # Degree = frequency in sequence + 1
    edges = []
    for v in prufer_seq:
        leaf = next(i for i in range(1, n + 1) if degree[i] == 1)
        edges.append((leaf, v))
        degree[leaf] -= 1; degree[v] -= 1
    last = [i for i in range(1, n + 1) if degree[i] == 1]
    edges.append((last[0], last[1]))                            # Final edge
    return edges

# ============================================================
# BOOLEAN ALGEBRA
# ============================================================

# Boolean values as integers: 0 = False, 1 = True

def BoolAnd(a, b):
    return int(bool(a) and bool(b))                            # a ∧ b

def BoolOr(a, b):
    return int(bool(a) or bool(b))                             # a ∨ b

def BoolNot(a):
    return int(not bool(a))                                    # ¬a

def BoolNand(a, b):
    return int(not (bool(a) and bool(b)))                      # ¬(a ∧ b)

def BoolNor(a, b):
    return int(not (bool(a) or bool(b)))                       # ¬(a ∨ b)

def BoolXor(a, b):
    return int(bool(a) != bool(b))                             # a ⊕ b

def BoolXnor(a, b):
    return int(bool(a) == bool(b))                             # a ↔ b

def BoolImplies(a, b):
    return int((not bool(a)) or bool(b))                       # a → b

# Formula: Quine-McCluskey minimisation (basic)
# minterms: list of integers (rows where output is 1), n_vars: number of variables
# Returns a list of essential prime implicants as (minterm_set, mask) tuples
# mask has 1 where variable is present, 0 where it has been eliminated ('don't care' = -1 in minterm repr)
def QuineMcCluskey(minterms, n_vars):
    def can_combine(a, b):
        diff = a ^ b
        return diff != 0 and (diff & (diff - 1)) == 0          # Exactly one bit differs

    def combine(a, b):
        return a & b, a ^ b                                     # Combined term and mask of changed bit

    groups   = {}
    for m in minterms:
        bc = bin(m).count('1')
        groups.setdefault(bc, set()).add(m)

    prime_implicants = set()
    current = {(m, 0): {m} for m in minterms}                  # (term, dont_care_mask): covered_minterms

    while current:
        next_level = {}
        used       = set()
        keys       = list(current.keys())
        for i, (ta, da) in enumerate(keys):
            for (tb, db) in keys[i+1:]:
                if da != db:
                    continue                                     # Must have same don't-care mask
                if can_combine(ta, tb):
                    new_term, changed = combine(ta, tb)
                    new_mask = da | changed
                    key = (new_term, new_mask)
                    next_level[key] = current[(ta, da)] | current[(tb, db)]
                    used.add((ta, da)); used.add((tb, db))
        for k, v in current.items():
            if k not in used:
                prime_implicants.add((k[0], k[1], frozenset(v)))
        current = next_level

    return [(term, mask, covered) for term, mask, covered in prime_implicants]

# Formula: DNF — disjunctive normal form — OR of AND clauses for each minterm
# truth_table: list of (assignment_tuple, result) as returned by TruthTable
# Returns a human-readable string representation
def ToDNF(truth_table):
    n_vars  = len(truth_table[0][0])
    labels  = [chr(65 + i) for i in range(n_vars)]             # A, B, C, ...
    clauses = []
    for assignment, result in truth_table:
        if result:
            literals = []
            for val, label in zip(assignment, labels):
                literals.append(label if val else f'¬{label}')
            clauses.append('(' + ' ∧ '.join(literals) + ')')
    return ' ∨ '.join(clauses) if clauses else '⊥'             # Contradiction if no minterms

# Formula: CNF — conjunctive normal form — AND of OR clauses for each maxterm
# Returns a human-readable string representation
def ToCNF(truth_table):
    n_vars  = len(truth_table[0][0])
    labels  = [chr(65 + i) for i in range(n_vars)]             # A, B, C, ...
    clauses = []
    for assignment, result in truth_table:
        if not result:
            literals = []
            for val, label in zip(assignment, labels):
                literals.append(f'¬{label}' if val else label) # Negate for maxterm
            clauses.append('(' + ' ∨ '.join(literals) + ')')
    return ' ∧ '.join(clauses) if clauses else '⊤'             # Tautology if no maxterms
