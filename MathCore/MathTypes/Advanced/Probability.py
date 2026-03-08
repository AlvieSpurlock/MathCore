import math  # Import math for sqrt, log, exp, pi, factorial, comb

# ============================================================
# FUNDAMENTAL PROBABILITY
# ============================================================

# Formula: P(A) = favorable outcomes / total outcomes
# Returns the classical probability of an event
# Returns 0 if total outcomes is zero to avoid division by zero
def ClassicalProbability(favorable, total):
    if total == 0:                                              # Guard against division by zero
        return 0                                                # Return 0 safely — undefined probability
    return favorable / total                                    # Divide favorable by total → complete P(A) = f/n

# Formula: P(A) = 1 - P(A')
# Returns the probability of the complement — the event NOT occurring
# Returns 0 if p is outside [0, 1]
def Complement(p):
    if not (0 <= p <= 1):                                       # Guard against invalid probability
        return 0                                                # Return 0 safely
    return 1 - p                                                # Subtract from 1 → complete P(A') = 1 - P(A)

# Formula: P(A ∪ B) = P(A) + P(B) - P(A ∩ B)
# Returns the probability of A or B occurring — the union of two events
# Returns 0 if any probability is outside [0, 1]
def UnionProbability(p_a, p_b, p_a_and_b):
    if not (0 <= p_a <= 1 and 0 <= p_b <= 1 and 0 <= p_a_and_b <= 1):  # Guard against invalid probabilities
        return 0                                                # Return 0 safely
    return p_a + p_b - p_a_and_b                               # Add individual probabilities minus overlap → complete P(A∪B)

# Formula: P(A ∩ B) = P(A) + P(B) - P(A ∪ B)
# Returns the probability of both A and B occurring — the intersection
# Returns 0 if any probability is outside [0, 1]
def IntersectionProbability(p_a, p_b, p_a_or_b):
    if not (0 <= p_a <= 1 and 0 <= p_b <= 1 and 0 <= p_a_or_b <= 1):  # Guard against invalid probabilities
        return 0                                                # Return 0 safely
    return p_a + p_b - p_a_or_b                                # Rearrange union formula → complete P(A∩B)

# Formula: P(A ∪ B) = P(A) + P(B)  when A and B are mutually exclusive
# Returns the probability of A or B when the two events cannot both occur
# Returns 0 if any probability is outside [0, 1]
def MutuallyExclusiveUnion(p_a, p_b):
    if not (0 <= p_a <= 1 and 0 <= p_b <= 1):                  # Guard against invalid probabilities
        return 0                                                # Return 0 safely
    return p_a + p_b                                            # Add directly — no overlap to subtract → complete P(A∪B)

# Formula: P(A ∩ B) = P(A) * P(B)  when A and B are independent
# Returns the probability of both A and B when the two events do not affect each other
# Returns 0 if any probability is outside [0, 1]
def IndependentIntersection(p_a, p_b):
    if not (0 <= p_a <= 1 and 0 <= p_b <= 1):                  # Guard against invalid probabilities
        return 0                                                # Return 0 safely
    return p_a * p_b                                            # Multiply directly → complete P(A∩B) = P(A)*P(B)

# Formula: two events are mutually exclusive if P(A ∩ B) = 0
# Returns True if two events cannot both occur at the same time
def AreMutuallyExclusive(p_a_and_b, tolerance = 1e-9):
    return abs(p_a_and_b) < tolerance                           # Check if intersection is effectively zero → complete

# Formula: two events are independent if P(A ∩ B) = P(A) * P(B)
# Returns True if knowing one event occurred tells us nothing about the other
def AreIndependent(p_a, p_b, p_a_and_b, tolerance = 1e-9):
    return abs(p_a_and_b - p_a * p_b) < tolerance              # Check if intersection equals product → complete

# ============================================================
# CONDITIONAL PROBABILITY
# ============================================================

# Formula: P(A|B) = P(A ∩ B) / P(B)
# Returns the conditional probability of A given that B has occurred
# Returns 0 if P(B) is zero to avoid division by zero
def ConditionalProbability(p_a_and_b, p_b):
    if p_b == 0:                                                # Guard against division by zero
        return 0                                                # Return 0 safely — B cannot occur
    return p_a_and_b / p_b                                      # Divide intersection by P(B) → complete P(A|B)

# Formula: P(A ∩ B) = P(A|B) * P(B)
# Returns the joint probability of A and B using the multiplication rule
# Returns 0 if any probability is outside [0, 1]
def MultiplicationRule(p_a_given_b, p_b):
    if not (0 <= p_a_given_b <= 1 and 0 <= p_b <= 1):          # Guard against invalid probabilities
        return 0                                                # Return 0 safely
    return p_a_given_b * p_b                                    # Multiply conditional by prior → complete P(A∩B)

# Formula: Bayes' theorem — P(A|B) = P(B|A) * P(A) / P(B)
# Returns the posterior probability of A given B using Bayes' theorem
# Returns 0 if P(B) is zero to avoid division by zero
def Bayes(p_b_given_a, p_a, p_b):
    if p_b == 0:                                                # Guard against division by zero
        return 0                                                # Return 0 safely — B has zero probability
    return (p_b_given_a * p_a) / p_b                            # Multiply likelihood by prior then divide by evidence → complete Bayes

# Formula: P(B) = Σ P(B|Aᵢ) * P(Aᵢ)  (total probability over a partition)
# Returns the total probability of B given a list of partition probabilities P(Aᵢ)
# and a list of likelihoods P(B|Aᵢ)
# Returns 0 if lists have different lengths
def TotalProbability(p_b_given_a_list, p_a_list):
    if len(p_b_given_a_list) != len(p_a_list):                  # Guard against mismatched lists
        return 0                                                # Return 0 safely
    return sum(pb_a * pa for pb_a, pa in zip(p_b_given_a_list, p_a_list))  # Sum products of each likelihood and prior → complete

# Formula: P(Aᵢ|B) = P(B|Aᵢ)*P(Aᵢ) / Σ P(B|Aⱼ)*P(Aⱼ)
# Returns a list of posterior probabilities for each event in a partition given evidence B
# Uses the extended form of Bayes' theorem over a full partition
# Returns list of zeros if total probability is zero
def BayesPartition(p_b_given_a_list, p_a_list):
    if len(p_b_given_a_list) != len(p_a_list):                  # Guard against mismatched lists
        return []                                               # Return empty list safely
    total = TotalProbability(p_b_given_a_list, p_a_list)        # Calculate total probability P(B)
    if total == 0:                                              # Guard against division by zero
        return [0] * len(p_a_list)                              # Return zeros safely
    return [(pb_a * pa) / total for pb_a, pa in zip(p_b_given_a_list, p_a_list)]  # Normalize each term → complete posteriors

# Formula: odds = P(A) / (1 - P(A))
# Returns the odds in favor of an event as a ratio  (e.g. 3.0 means 3-to-1 in favor)
# Returns 0 if p equals 1 to avoid division by zero
def OddsInFavor(p):
    if p == 1:                                                  # Guard against division by zero
        return 0                                                # Return 0 safely — certain event has infinite odds
    if not (0 <= p <= 1):                                       # Guard against invalid probability
        return 0                                                # Return 0 safely
    return p / (1 - p)                                          # Divide probability by its complement → complete odds

# Formula: P(A) = odds / (1 + odds)
# Returns the probability from odds in favor
# Returns 0 if odds is negative
def OddsToProb(odds):
    if odds < 0:                                                # Guard against invalid negative odds
        return 0                                                # Return 0 safely
    return odds / (1 + odds)                                    # Divide odds by one plus odds → complete P(A)

# ============================================================
# COMBINATORICS FOR PROBABILITY
# ============================================================

# Formula: n! = n * (n-1) * ... * 1
# Returns n factorial — the number of ways to arrange n distinct items
# Returns 1 for n = 0 by convention
# Returns 0 if n is negative
def Factorial(n):
    if n < 0:                                                   # Guard against negative input
        return 0                                                # Return 0 safely — undefined
    return math.factorial(n)                                    # Delegate to math.factorial → complete n!

# Formula: P(n, r) = n! / (n - r)!
# Returns the number of permutations — ordered arrangements of r items from n
# Returns 0 if r > n or either is negative
def Permutations(n, r):
    if r > n or n < 0 or r < 0:                                # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return math.factorial(n) // math.factorial(n - r)           # Divide n! by (n-r)! → complete P(n,r)

# Formula: C(n, r) = n! / (r! * (n - r)!)
# Returns the number of combinations — unordered selections of r items from n
# Returns 0 if r > n or either is negative
def Combinations(n, r):
    if r > n or n < 0 or r < 0:                                # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return math.comb(n, r)                                      # Delegate to math.comb → complete C(n,r)

# Formula: circular permutations = (n - 1)!
# Returns the number of ways to arrange n items in a circle
# Circular arrangements fix one item and arrange the rest
# Returns 0 if n is less than 1
def CircularPermutations(n):
    if n < 1:                                                   # Guard against invalid input
        return 0                                                # Return 0 safely
    return math.factorial(n - 1)                                # Factorial of n-1 → complete circular arrangements

# Formula: permutations with repetition = n^r
# Returns the number of ordered sequences of r items chosen from n with replacement
# Returns 0 if either is negative
def PermutationsWithRepetition(n, r):
    if n < 0 or r < 0:                                         # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return n ** r                                               # Raise n to the power r → complete n^r

# Formula: combinations with repetition = C(n + r - 1, r)
# Returns the number of ways to choose r items from n with repetition allowed (order irrelevant)
# Returns 0 if either is negative
def CombinationsWithRepetition(n, r):
    if n < 0 or r < 0:                                         # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return math.comb(n + r - 1, r)                              # Stars and bars formula → complete C(n+r-1, r)

# Formula: multinomial coefficient = n! / (n₁! * n₂! * ... * nₖ!)
# Returns the number of ways to arrange n items split into groups of sizes given in the list
# Returns 0 if the group sizes do not sum to n or any is negative
def Multinomial(n, groups):
    if any(g < 0 for g in groups):                             # Guard against negative group sizes
        return 0                                                # Return 0 safely
    if sum(groups) != n:                                        # Guard against groups not summing to total
        return 0                                                # Return 0 safely — inconsistent inputs
    denominator = 1                                             # Initialize denominator product
    for g in groups:                                            # Multiply factorials of each group size
        denominator *= math.factorial(g)                        # Accumulate product of group factorials
    return math.factorial(n) // denominator                     # Divide n! by product → complete multinomial coefficient

# ============================================================
# DISCRETE RANDOM VARIABLES
# ============================================================

# Formula: E(X) = Σ xᵢ * P(xᵢ)
# Returns the expected value — the probability-weighted average of all outcomes
# values and probs must be matching lists — probabilities must sum to 1
# Returns 0 if lists are mismatched or empty
def ExpectedValue(values, probs):
    if len(values) != len(probs) or not values:                 # Guard against mismatched or empty inputs
        return 0                                                # Return 0 safely
    return sum(x * p for x, p in zip(values, probs))           # Multiply each value by its probability and sum → complete E(X)

# Formula: E(X²) = Σ xᵢ² * P(xᵢ)
# Returns the expected value of X squared — used to compute variance
def ExpectedValueSquared(values, probs):
    if len(values) != len(probs) or not values:                 # Guard against mismatched or empty inputs
        return 0                                                # Return 0 safely
    return sum(x**2 * p for x, p in zip(values, probs))        # Square each value before weighting → complete E(X²)

# Formula: Var(X) = E(X²) - [E(X)]²
# Returns the variance of a discrete random variable
# Returns 0 if lists are mismatched or empty
def Variance(values, probs):
    if len(values) != len(probs) or not values:                 # Guard against mismatched or empty inputs
        return 0                                                # Return 0 safely
    ex  = ExpectedValue(values, probs)                          # Calculate E(X)
    ex2 = ExpectedValueSquared(values, probs)                   # Calculate E(X²)
    return ex2 - ex ** 2                                        # Subtract square of mean → complete Var(X) = E(X²) - [E(X)]²

# Formula: σ = sqrt(Var(X))
# Returns the standard deviation of a discrete random variable
def StandardDeviation(values, probs):
    var = Variance(values, probs)                               # Calculate variance first
    if var < 0:                                                 # Guard against floating-point negatives near zero
        return 0                                                # Return 0 safely
    return math.sqrt(var)                                       # Square root of variance → complete standard deviation

# Formula: E(aX + b) = a*E(X) + b
# Returns the expected value of a linear transformation of a random variable
def LinearTransformExpected(a, ex, b):
    return a * ex + b                                           # Scale and shift expected value → complete E(aX+b)

# Formula: Var(aX + b) = a²*Var(X)
# Returns the variance of a linear transformation — note the constant b does not affect variance
def LinearTransformVariance(a, var_x):
    return a ** 2 * var_x                                       # Square the scale factor → complete Var(aX+b) = a²*Var(X)

# Formula: E(X + Y) = E(X) + E(Y)
# Returns the expected value of the sum of two independent random variables
def SumExpected(ex, ey):
    return ex + ey                                              # Add expected values → complete E(X+Y) = E(X) + E(Y)

# Formula: Var(X + Y) = Var(X) + Var(Y)  when X and Y are independent
# Returns the variance of the sum of two independent random variables
def SumVariance(var_x, var_y):
    return var_x + var_y                                        # Add variances → complete Var(X+Y) for independent variables

# Formula: checks if a probability distribution is valid — all probs in [0,1] and sum to 1
# Returns True if the list of probabilities forms a valid probability distribution
def IsValidDistribution(probs, tolerance = 1e-9):
    if not probs:                                               # Guard against empty list
        return False                                            # Empty list is not a valid distribution
    if any(p < 0 or p > 1 for p in probs):                     # All probabilities must be in [0, 1]
        return False                                            # Invalid if any probability is out of range
    return abs(sum(probs) - 1) < tolerance                      # Probabilities must sum to 1 within tolerance → complete

# ============================================================
# NAMED DISCRETE DISTRIBUTIONS
# ============================================================

# Formula: P(X = k) = C(n,k) * p^k * (1-p)^(n-k)
# Returns the binomial probability of exactly k successes in n independent trials
# Each trial has success probability p
# Returns 0 if inputs are invalid
def BinomialPMF(n, k, p):
    if not (0 <= p <= 1) or k < 0 or k > n or n < 0:           # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return math.comb(n, k) * (p ** k) * ((1 - p) ** (n - k))   # Binomial coefficient times two probability terms → complete

# Formula: E(X) = np  for Binomial(n, p)
# Returns the expected number of successes in n trials
def BinomialMean(n, p):
    return n * p                                                # Multiply trials by success probability → complete E(X) = np

# Formula: Var(X) = np(1-p)  for Binomial(n, p)
# Returns the variance of a binomial distribution
def BinomialVariance(n, p):
    return n * p * (1 - p)                                      # Multiply n, p, and q together → complete Var(X) = npq

# Formula: P(X = k) = (λ^k * e^(-λ)) / k!
# Returns the Poisson probability of exactly k events given average rate λ
# Returns 0 if k is negative or λ is non-positive
def PoissonPMF(lam, k):
    if lam <= 0 or k < 0:                                      # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return (lam ** k * math.exp(-lam)) / math.factorial(k)     # Numerator divided by k factorial → complete Poisson PMF

# Formula: E(X) = Var(X) = λ  for Poisson(λ)
# Returns the mean and variance of a Poisson distribution — they are equal
def PoissonMeanVariance(lam):
    return lam                                                  # Both mean and variance equal λ → complete

# Formula: P(X = k) = (1-p)^(k-1) * p  for k = 1, 2, 3, ...
# Returns the geometric probability — probability that first success occurs on trial k
# Returns 0 if p is outside (0, 1] or k is less than 1
def GeometricPMF(p, k):
    if not (0 < p <= 1) or k < 1:                              # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return ((1 - p) ** (k - 1)) * p                             # Failures before success times success prob → complete

# Formula: E(X) = 1/p  for Geometric(p)
# Returns the expected number of trials until the first success
# Returns 0 if p is zero to avoid division by zero
def GeometricMean(p):
    if p == 0:                                                  # Guard against division by zero
        return 0                                                # Return 0 safely
    return 1 / p                                                # Reciprocal of success probability → complete E(X) = 1/p

# Formula: Var(X) = (1-p) / p²  for Geometric(p)
# Returns the variance of a geometric distribution
# Returns 0 if p is zero to avoid division by zero
def GeometricVariance(p):
    if p == 0:                                                  # Guard against division by zero
        return 0                                                # Return 0 safely
    return (1 - p) / (p ** 2)                                   # Divide complement by p squared → complete Var(X)

# Formula: P(X = k) = C(k-1, r-1) * p^r * (1-p)^(k-r)
# Returns the negative binomial probability — probability that the rth success occurs on trial k
# Returns 0 if inputs are invalid
def NegativeBinomialPMF(r, k, p):
    if not (0 < p <= 1) or k < r or r < 1:                     # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return math.comb(k - 1, r - 1) * (p ** r) * ((1 - p) ** (k - r))  # Apply negative binomial formula → complete

# Formula: P(X = k) = C(K,k) * C(N-K, n-k) / C(N, n)
# Returns the hypergeometric probability — drawing k successes from a finite population
# N = population size, K = successes in population, n = sample size, k = observed successes
# Returns 0 if inputs are invalid
def HypergeometricPMF(N, K, n, k):
    if k < max(0, n - (N - K)) or k > min(n, K):               # Guard against out-of-range k
        return 0                                                # Return 0 safely
    if N < 0 or K < 0 or n < 0:                                # Guard against negative inputs
        return 0                                                # Return 0 safely
    return math.comb(K, k) * math.comb(N - K, n - k) / math.comb(N, n)  # Product of two combinations divided by total → complete

# Formula: E(X) = n * K/N  for Hypergeometric
# Returns the expected number of successes when drawing n from a population of N with K successes
def HypergeometricMean(N, K, n):
    if N == 0:                                                  # Guard against division by zero
        return 0                                                # Return 0 safely
    return n * (K / N)                                          # Scale sample size by population success rate → complete

# ============================================================
# CONTINUOUS DISTRIBUTIONS
# ============================================================

# Formula: f(x) = (1 / (σ√(2π))) * e^(-(x-μ)²/(2σ²))
# Returns the normal probability density at x given mean μ and standard deviation σ
# Returns 0 if σ is non-positive
def NormalPDF(x, mu = 0, sigma = 1):
    if sigma <= 0:                                              # Guard against invalid standard deviation
        return 0                                                # Return 0 safely
    exponent = -((x - mu) ** 2) / (2 * sigma ** 2)             # Compute the exponent → -(x-μ)²/(2σ²)
    return (1 / (sigma * math.sqrt(2 * math.pi))) * math.exp(exponent)  # Scale by normalization constant → complete PDF

# Formula: Φ(x) = (1 + erf((x-μ)/(σ√2))) / 2
# Returns the cumulative normal probability — P(X ≤ x)
# Returns 0 if σ is non-positive
def NormalCDF(x, mu = 0, sigma = 1):
    if sigma <= 0:                                              # Guard against invalid standard deviation
        return 0                                                # Return 0 safely
    return (1 + math.erf((x - mu) / (sigma * math.sqrt(2)))) / 2  # Apply error function approximation → complete Φ(x)

# Formula: P(a ≤ X ≤ b) = Φ(b) - Φ(a)
# Returns the probability that a normal variable falls strictly between a and b
def NormalBetween(a, b, mu = 0, sigma = 1):
    return NormalCDF(b, mu, sigma) - NormalCDF(a, mu, sigma)    # Subtract CDFs → complete P(a≤X≤b)

# Formula: inverse standard normal — find x such that Φ(x) = p
# Returns the z-score corresponding to a given cumulative probability p
# Uses a rational approximation accurate to about 4.5 decimal places
# Returns 0 if p is outside (0, 1)
def InverseNormalCDF(p):
    if not (0 < p < 1):                                         # Guard against out-of-range probability
        return 0                                                # Return 0 safely
    if p < 0.5:                                                 # Lower half — use symmetry after computing upper
        return -InverseNormalCDF(1 - p)                         # Reflect using symmetry of normal distribution
    t = math.sqrt(-2 * math.log(1 - p))                         # Approximation variable t from p
    # Rational approximation coefficients for the upper tail
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    numerator   = c0 + c1 * t + c2 * t ** 2                    # Numerator of rational approximation
    denominator = 1 + d1 * t + d2 * t ** 2 + d3 * t ** 3      # Denominator of rational approximation
    return t - numerator / denominator                          # Subtract ratio → complete inverse normal approximation

# Formula: f(x) = λe^(-λx)  for x ≥ 0
# Returns the exponential probability density at x given rate λ
# Returns 0 if x is negative or λ is non-positive
def ExponentialPDF(lam, x):
    if lam <= 0 or x < 0:                                      # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return lam * math.exp(-lam * x)                             # Rate times decaying exponential → complete PDF

# Formula: F(x) = 1 - e^(-λx)  for x ≥ 0
# Returns the cumulative exponential probability — P(X ≤ x)
def ExponentialCDF(lam, x):
    if lam <= 0 or x < 0:                                      # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return 1 - math.exp(-lam * x)                               # Subtract decaying exponential from 1 → complete CDF

# Formula: E(X) = 1/λ  for Exponential(λ)
# Returns the mean of an exponential distribution — the average time between events
def ExponentialMean(lam):
    if lam <= 0:                                                # Guard against invalid rate
        return 0                                                # Return 0 safely
    return 1 / lam                                              # Reciprocal of rate → complete E(X) = 1/λ

# Formula: f(x) = 1/(b-a)  for a ≤ x ≤ b
# Returns the uniform probability density — constant across the interval [a, b]
# Returns 0 outside the interval or if a equals b
def UniformPDF(x, a, b):
    if b == a:                                                  # Guard against zero-width interval
        return 0                                                # Return 0 safely
    if x < a or x > b:                                         # Outside the interval
        return 0                                                # Return 0 — zero probability outside support
    return 1 / (b - a)                                          # Constant height → complete uniform PDF

# Formula: F(x) = (x - a) / (b - a)  for a ≤ x ≤ b
# Returns the cumulative uniform probability — fraction of interval covered
def UniformCDF(x, a, b):
    if b == a:                                                  # Guard against zero-width interval
        return 0                                                # Return 0 safely
    if x <= a:                                                  # At or below lower bound
        return 0                                                # No probability accumulated yet
    if x >= b:                                                  # At or above upper bound
        return 1                                                # Full probability accumulated
    return (x - a) / (b - a)                                    # Linear fraction → complete uniform CDF

# Formula: E(X) = (a + b) / 2  for Uniform(a, b)
# Returns the mean of a uniform distribution — the midpoint of the interval
def UniformMean(a, b):
    return (a + b) / 2                                          # Average the endpoints → complete E(X) = (a+b)/2

# Formula: Var(X) = (b - a)² / 12  for Uniform(a, b)
# Returns the variance of a uniform distribution
def UniformVariance(a, b):
    return (b - a) ** 2 / 12                                    # Square the width and divide by 12 → complete Var(X)

# ============================================================
# LAW OF LARGE NUMBERS AND CENTRAL LIMIT THEOREM
# ============================================================

# Formula: sampling distribution mean = μ
# Returns the mean of the sampling distribution of the sample mean
# Equal to the population mean — the sample mean is an unbiased estimator
def SamplingDistributionMean(mu):
    return mu                                                   # Mean of sampling distribution equals population mean → complete

# Formula: sampling distribution std dev = σ / √n  (standard error)
# Returns the standard deviation of the sampling distribution of the sample mean
# Returns 0 if n is non-positive
def SamplingDistributionStdDev(sigma, n):
    if n <= 0:                                                  # Guard against invalid sample size
        return 0                                                # Return 0 safely
    return sigma / math.sqrt(n)                                 # Divide population std dev by root n → complete standard error

# Formula: CLT z-score = (x̄ - μ) / (σ / √n)
# Returns the z-score for a sample mean under the Central Limit Theorem
# Returns 0 if standard error is zero
def CLTZScore(sample_mean, mu, sigma, n):
    se = SamplingDistributionStdDev(sigma, n)                   # Calculate standard error
    if se == 0:                                                 # Guard against division by zero
        return 0                                                # Return 0 safely
    return (sample_mean - mu) / se                              # Standardize the sample mean → complete CLT z-score

# Formula: P(x̄ ≤ value) using CLT
# Returns the probability that a sample mean is at most a given value
# Valid when sample size is large enough for CLT to apply (n ≥ 30 typically)
def CLTProbabilityBelow(value, mu, sigma, n):
    z = CLTZScore(value, mu, sigma, n)                          # Convert to z-score using CLT
    return NormalCDF(z)                                         # Look up standard normal CDF → complete P(x̄ ≤ value)

# Formula: P(a ≤ x̄ ≤ b) using CLT
# Returns the probability that a sample mean falls between two values
def CLTProbabilityBetween(a, b, mu, sigma, n):
    za = CLTZScore(a, mu, sigma, n)                             # z-score for lower bound
    zb = CLTZScore(b, mu, sigma, n)                             # z-score for upper bound
    return NormalCDF(zb) - NormalCDF(za)                        # Subtract CDFs → complete P(a ≤ x̄ ≤ b)

# ============================================================
# MARKOV CHAINS
# ============================================================

# Formula: next state vector = current state vector × transition matrix
# Returns the next state probability vector given the current state vector and transition matrix
# state_vector is a list of probabilities — transition_matrix is a list of lists
# Returns a list of zeros if dimensions are mismatched
def MarkovNextState(state_vector, transition_matrix):
    n = len(state_vector)                                       # Number of states
    if len(transition_matrix) != n:                             # Guard against dimension mismatch
        return [0] * n                                          # Return zeros safely
    next_state = []                                             # Initialize next state vector
    for col in range(n):                                        # Loop through each destination state
        total = sum(state_vector[row] * transition_matrix[row][col] for row in range(n))  # Sum contributions from all current states
        next_state.append(total)                                # Add computed probability for this destination
    return next_state                                           # Return complete next state vector

# Formula: state after k steps = initial state × T^k
# Returns the state probability vector after k steps through a Markov chain
# Applies the transition matrix k times iteratively
def MarkovAfterSteps(state_vector, transition_matrix, k):
    current = state_vector[:]                                   # Start with a copy of the initial state
    for _ in range(k):                                          # Apply transition k times
        current = MarkovNextState(current, transition_matrix)   # Step forward one transition
    return current                                              # Return final state vector after k steps

# Formula: stationary distribution satisfies π = π * T  (fixed point)
# Returns the approximate stationary distribution by iterating the chain until convergence
# Runs up to max_iterations steps — returns current state if convergence not reached
def StationaryDistribution(state_vector, transition_matrix, max_iterations = 1000, tolerance = 1e-10):
    current = state_vector[:]                                   # Start with initial state
    for _ in range(max_iterations):                             # Iterate until convergence
        next_s = MarkovNextState(current, transition_matrix)    # Compute next state
        if all(abs(next_s[i] - current[i]) < tolerance for i in range(len(current))):  # Check convergence
            return next_s                                       # Return converged stationary distribution
        current = next_s                                        # Update current state for next iteration
    return current                                              # Return best approximation after max iterations

# ============================================================
# SIMULATION AND RANDOM SAMPLING
# ============================================================

# Formula: simulate n Bernoulli trials each with success probability p
# Returns the number of successes in n trials using a deterministic pseudo-random approach
# Uses a linear congruential generator seeded by the seed parameter for reproducibility
def SimulateBernoulli(n, p, seed = 42):
    if not (0 <= p <= 1) or n < 0:                             # Guard against invalid inputs
        return 0                                                # Return 0 safely
    successes = 0                                               # Initialize success counter
    state     = seed                                            # Seed the pseudo-random state
    for _ in range(n):                                          # Run n trials
        state  = (state * 1664525 + 1013904223) & 0xFFFFFFFF   # Linear congruential update → pseudo-random step
        rand   = (state & 0x7FFFFFFF) / 0x7FFFFFFF             # Normalize to [0, 1]
        if rand < p:                                            # Compare to success threshold
            successes += 1                                      # Count success
    return successes                                            # Return total successes from n trials

# Formula: sample mean from n simulated Bernoulli trials
# Returns the observed proportion of successes — estimate of p
def SimulateBernoulliProportion(n, p, seed = 42):
    if n <= 0:                                                  # Guard against zero trials
        return 0                                                # Return 0 safely
    return SimulateBernoulli(n, p, seed) / n                    # Divide successes by trials → complete observed proportion

# Formula: empirical probability from simulation = successes / trials
# Returns the empirical probability of success after running n simulated trials
# Wraps SimulateBernoulliProportion for semantic clarity
def EmpiricalProbability(n, p, seed = 42):
    return SimulateBernoulliProportion(n, p, seed)              # Delegate to proportion calculator → complete empirical P

# Formula: expected value approximation from simulation
# Returns the estimated expected value of a discrete distribution from a simulated sample
# weights are treated as probabilities and must sum to 1
def SimulatedExpectedValue(values, probs, n_trials = 10000, seed = 42):
    if len(values) != len(probs) or not values:                 # Guard against mismatched or empty inputs
        return 0                                                # Return 0 safely
    total  = 0                                                  # Initialize sum accumulator
    state  = seed                                               # Seed pseudo-random state
    for _ in range(n_trials):                                   # Run n_trials simulations
        state     = (state * 1664525 + 1013904223) & 0xFFFFFFFF  # Update random state
        rand      = (state & 0x7FFFFFFF) / 0x7FFFFFFF            # Normalize to [0, 1]
        cumul     = 0                                           # Cumulative probability tracker
        for value, prob in zip(values, probs):                  # Walk through the distribution
            cumul += prob                                       # Add this outcome's probability
            if rand < cumul:                                    # Check if this outcome was sampled
                total += value                                  # Add outcome value to running total
                break                                           # Move to next trial
    return total / n_trials                                     # Divide sum by trials → complete simulated E(X)

# ============================================================
# INFORMATION THEORY
# ============================================================

# Formula: H(X) = -Σ p(x) * log₂(p(x))
# Returns the Shannon entropy of a probability distribution in bits
# Measures the average uncertainty or information content
# Returns 0 if the list is empty or all probabilities are zero
def ShannonEntropy(probs):
    if not probs:                                               # Guard against empty list
        return 0                                                # Return 0 safely
    entropy = 0                                                 # Initialize entropy accumulator
    for p in probs:                                             # Loop through each probability
        if p > 0:                                               # Skip zero probabilities — 0*log(0) = 0 by convention
            entropy -= p * math.log2(p)                        # Subtract p*log₂(p) contribution
    return entropy                                              # Return total entropy in bits

# Formula: H(X) using natural log — entropy in nats
# Returns the natural entropy of a probability distribution in nats (base e)
def NaturalEntropy(probs):
    if not probs:                                               # Guard against empty list
        return 0                                                # Return 0 safely
    entropy = 0                                                 # Initialize entropy accumulator
    for p in probs:                                             # Loop through each probability
        if p > 0:                                               # Skip zero probabilities
            entropy -= p * math.log(p)                         # Subtract p*ln(p) contribution
    return entropy                                              # Return total entropy in nats

# Formula: max entropy = log₂(n)  for n equally likely outcomes
# Returns the maximum possible entropy for n outcomes — achieved when all are equally likely
# Returns 0 if n is less than 1
def MaxEntropy(n):
    if n < 1:                                                   # Guard against invalid number of outcomes
        return 0                                                # Return 0 safely
    return math.log2(n)                                         # Log base 2 of outcome count → complete max entropy

# Formula: information content of one outcome = -log₂(p)
# Returns the self-information of a single event with probability p in bits
# Rare events carry more information — certain events carry zero
# Returns 0 if p is zero or negative to avoid domain errors
def SelfInformation(p):
    if p <= 0:                                                  # Guard against log of non-positive probability
        return 0                                                # Return 0 safely
    if p > 1:                                                   # Guard against invalid probability
        return 0                                                # Return 0 safely
    return -math.log2(p)                                        # Negative log₂ of probability → complete self-information

# Formula: KL divergence D(P||Q) = Σ p(x) * log(p(x)/q(x))
# Returns the Kullback-Leibler divergence — how different distribution P is from reference Q
# Measures information lost when Q is used to approximate P
# Returns 0 if lists are mismatched or any q(x) is zero when p(x) > 0
def KLDivergence(p_probs, q_probs):
    if len(p_probs) != len(q_probs):                            # Guard against mismatched lists
        return 0                                                # Return 0 safely
    divergence = 0                                              # Initialize divergence accumulator
    for p, q in zip(p_probs, q_probs):                         # Loop through each outcome pair
        if p > 0 and q == 0:                                   # P assigns probability where Q assigns zero → infinite divergence
            return float('inf')                                 # Return infinity — Q cannot represent P here
        if p > 0:                                               # Only add when p > 0 — 0*log(0/q) = 0 by convention
            divergence += p * math.log(p / q)                  # Add p*log(p/q) contribution
    return divergence                                           # Return total KL divergence
