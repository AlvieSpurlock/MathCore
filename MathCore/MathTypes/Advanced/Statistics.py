import math  # Import math for sqrt, log, exp, pi, erf, factorial

# ============================================================
# DESCRIPTIVE STATISTICS — CENTRAL TENDENCY
# ============================================================

# Formula: μ = Σxᵢ / n
# Returns the arithmetic mean — sum of all values divided by the count
# Returns 0 if the list is empty to avoid division by zero
def Mean(data):
    if not data:                                                # Guard against empty list
        return 0                                                # Return 0 safely
    return sum(data) / len(data)                                # Divide total sum by number of values → complete μ = Σx/n

# Formula: middle value when sorted — or average of two middle values for even n
# Returns the median — the value that splits the sorted data in half
# Returns 0 if the list is empty
def Median(data):
    if not data:                                                # Guard against empty list
        return 0                                                # Return 0 safely
    sorted_data = sorted(data)                                  # Sort data in ascending order
    n           = len(sorted_data)                              # Count total values
    mid         = n // 2                                        # Find the middle index
    if n % 2 == 1:                                              # Odd count — single middle value
        return sorted_data[mid]                                 # Return the exact middle value
    else:                                                       # Even count — average of two middle values
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2   # Average both middle values → complete median

# Formula: most frequently occurring value(s)
# Returns a list of mode values — there may be one mode, multiple modes, or all values if no repeats
# Returns empty list if data is empty
def Mode(data):
    if not data:                                                # Guard against empty list
        return []                                               # Return empty list safely
    frequency = {}                                              # Build a frequency dictionary
    for value in data:                                          # Count how many times each value appears
        frequency[value] = frequency.get(value, 0) + 1         # Increment count for this value
    max_count = max(frequency.values())                         # Find the highest frequency
    modes     = [k for k, v in frequency.items() if v == max_count]  # Collect all values with that frequency
    return sorted(modes)                                        # Return modes in sorted order

# Formula: (max + min) / 2
# Returns the midrange — the average of the largest and smallest values
# Returns 0 if the list is empty
def Midrange(data):
    if not data:                                                # Guard against empty list
        return 0                                                # Return 0 safely
    return (max(data) + min(data)) / 2                          # Average the extremes → complete midrange = (max+min)/2

# Formula: weighted mean = Σ(xᵢ * wᵢ) / Σwᵢ
# Returns the weighted mean given a list of values and a matching list of weights
# Returns 0 if weights sum to zero or lists are empty
def WeightedMean(values, weights):
    if not values or not weights:                               # Guard against empty inputs
        return 0                                                # Return 0 safely
    total_weight = sum(weights)                                 # Sum all weights
    if total_weight == 0:                                       # Guard against zero total weight
        return 0                                                # Return 0 safely — undefined
    weighted_sum = sum(v * w for v, w in zip(values, weights))  # Multiply each value by its weight and sum
    return weighted_sum / total_weight                          # Divide by total weight → complete weighted mean

# Formula: geometric mean = (x₁ * x₂ * ... * xₙ)^(1/n)
# Returns the geometric mean — the nth root of the product of all values
# Returns 0 if any value is non-positive — geometric mean undefined for non-positive values
def GeometricMean(data):
    if not data:                                                # Guard against empty list
        return 0                                                # Return 0 safely
    if any(x <= 0 for x in data):                              # Guard against non-positive values — log undefined
        return 0                                                # Return 0 safely
    log_sum = sum(math.log(x) for x in data)                   # Sum natural logs of all values
    return math.exp(log_sum / len(data))                        # Exponentiate average log → complete geometric mean

# Formula: harmonic mean = n / Σ(1/xᵢ)
# Returns the harmonic mean — used for rates and ratios
# Returns 0 if any value is zero or list is empty
def HarmonicMean(data):
    if not data:                                                # Guard against empty list
        return 0                                                # Return 0 safely
    if any(x == 0 for x in data):                              # Guard against division by zero
        return 0                                                # Return 0 safely — harmonic mean undefined
    reciprocal_sum = sum(1 / x for x in data)                  # Sum reciprocals of all values
    return len(data) / reciprocal_sum                           # Divide count by sum of reciprocals → complete harmonic mean

# ============================================================
# DESCRIPTIVE STATISTICS — SPREAD AND VARIABILITY
# ============================================================

# Formula: range = max - min
# Returns the range — the spread between the largest and smallest values
# Returns 0 if the list is empty
def Range(data):
    if not data:                                                # Guard against empty list
        return 0                                                # Return 0 safely
    return max(data) - min(data)                                # Subtract min from max → complete range

# Formula: σ² = Σ(xᵢ - μ)² / n  (population)  or  s² = Σ(xᵢ - x̄)² / (n-1)  (sample)
# Returns the variance — the average squared deviation from the mean
# population=True uses n (population variance)  — population=False uses n-1 (sample variance)
# Returns 0 if there are insufficient data points
def Variance(data, population = True):
    n = len(data)                                               # Count values
    if n == 0:                                                  # Guard against empty list
        return 0                                                # Return 0 safely
    if not population and n < 2:                                # Sample variance requires at least 2 values
        return 0                                                # Return 0 safely
    mu      = Mean(data)                                        # Calculate the mean first
    sq_diff = sum((x - mu) ** 2 for x in data)                 # Sum of squared deviations from mean
    divisor = n if population else n - 1                        # Use n for population, n-1 for sample
    return sq_diff / divisor                                    # Divide by divisor → complete variance formula

# Formula: σ = sqrt(σ²)
# Returns the standard deviation — the square root of the variance
# population=True uses population variance — population=False uses sample variance
def StandardDeviation(data, population = True):
    return math.sqrt(Variance(data, population))                # Square root of variance → complete standard deviation

# Formula: IQR = Q3 - Q1
# Returns the interquartile range — the spread of the middle 50% of data
# Returns 0 if the list is empty
def IQR(data):
    if not data:                                                # Guard against empty list
        return 0                                                # Return 0 safely
    return Percentile(data, 75) - Percentile(data, 25)          # Q3 minus Q1 → complete IQR

# Formula: CV = (σ / μ) * 100
# Returns the coefficient of variation — standard deviation as a percentage of the mean
# Returns 0 if the mean is zero to avoid division by zero
def CoefficientOfVariation(data, population = True):
    mu = Mean(data)                                             # Calculate the mean
    if mu == 0:                                                 # Guard against division by zero
        return 0                                                # Return 0 safely
    return (StandardDeviation(data, population) / abs(mu)) * 100  # Scale relative std dev to percentage → complete CV

# Formula: MAD = Σ|xᵢ - μ| / n
# Returns the mean absolute deviation — average distance from the mean
# Returns 0 if the list is empty
def MeanAbsoluteDeviation(data):
    if not data:                                                # Guard against empty list
        return 0                                                # Return 0 safely
    mu = Mean(data)                                             # Calculate the mean
    return sum(abs(x - mu) for x in data) / len(data)          # Average absolute deviations → complete MAD

# Formula: pth percentile using linear interpolation
# Returns the value at the pth percentile of the data  (p between 0 and 100)
# Returns 0 if the list is empty or p is out of range
def Percentile(data, p):
    if not data or not (0 <= p <= 100):                         # Guard against empty list or invalid p
        return 0                                                # Return 0 safely
    sorted_data = sorted(data)                                  # Sort data ascending
    n           = len(sorted_data)                              # Count values
    index       = (p / 100) * (n - 1)                          # Compute fractional index position
    lower       = int(index)                                    # Integer part → lower index
    upper       = min(lower + 1, n - 1)                         # Upper index — clamped to list bounds
    fraction    = index - lower                                 # Fractional part for interpolation
    return sorted_data[lower] + fraction * (sorted_data[upper] - sorted_data[lower])  # Linear interpolation → complete percentile

# Formula: quartiles are the 25th, 50th, and 75th percentiles
# Returns a tuple (Q1, Q2, Q3) — the three quartile values
def Quartiles(data):
    q1 = Percentile(data, 25)                                   # First quartile → 25th percentile
    q2 = Percentile(data, 50)                                   # Second quartile → median (50th percentile)
    q3 = Percentile(data, 75)                                   # Third quartile → 75th percentile
    return (q1, q2, q3)                                         # Return all three as a tuple

# Formula: five-number summary = (min, Q1, median, Q3, max)
# Returns a tuple with the five key values that describe the distribution shape
def FiveNumberSummary(data):
    if not data:                                                # Guard against empty list
        return (0, 0, 0, 0, 0)                                  # Return zeros safely
    q1, q2, q3 = Quartiles(data)                                # Calculate quartiles
    return (min(data), q1, q2, q3, max(data))                   # Return complete five-number summary tuple

# ============================================================
# DESCRIPTIVE STATISTICS — SHAPE
# ============================================================

# Formula: skewness = [n / ((n-1)(n-2))] * Σ[(xᵢ-x̄)/s]³
# Returns the sample skewness — measures asymmetry of the distribution
# Positive = right tail, Negative = left tail, Zero = symmetric
# Returns 0 if standard deviation is zero or fewer than 3 data points
def Skewness(data):
    n = len(data)                                               # Count values
    if n < 3:                                                   # Need at least 3 values for skewness
        return 0                                                # Return 0 safely
    mu = Mean(data)                                             # Calculate mean
    s  = StandardDeviation(data, population = False)            # Sample standard deviation
    if s == 0:                                                  # Guard against division by zero
        return 0                                                # Return 0 safely — no spread means no skew
    cube_sum = sum(((x - mu) / s) ** 3 for x in data)          # Sum of cubed standardized deviations
    return (n / ((n - 1) * (n - 2))) * cube_sum                 # Apply bias correction factor → complete sample skewness

# Formula: excess kurtosis = [n(n+1)/((n-1)(n-2)(n-3))] * Σ[(xᵢ-x̄)/s]⁴ - 3(n-1)²/((n-2)(n-3))
# Returns the sample excess kurtosis — measures the heaviness of the tails
# Positive = heavier tails than normal, Negative = lighter tails, Zero = normal
# Returns 0 if standard deviation is zero or fewer than 4 data points
def Kurtosis(data):
    n = len(data)                                               # Count values
    if n < 4:                                                   # Need at least 4 values for kurtosis
        return 0                                                # Return 0 safely
    mu = Mean(data)                                             # Calculate mean
    s  = StandardDeviation(data, population = False)            # Sample standard deviation
    if s == 0:                                                  # Guard against division by zero
        return 0                                                # Return 0 safely
    fourth_sum = sum(((x - mu) / s) ** 4 for x in data)        # Sum of fourth-power standardized deviations
    term1      = (n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3)) * fourth_sum   # Scaled fourth moment
    term2      = (3 * (n - 1) ** 2) / ((n - 2) * (n - 3))      # Bias correction term
    return term1 - term2                                        # Subtract correction → complete excess kurtosis

# Formula: z = (x - μ) / σ
# Returns the z-score — how many standard deviations x is from the mean
# Returns 0 if standard deviation is zero
def ZScore(x, mu, sigma):
    if sigma == 0:                                              # Guard against division by zero
        return 0                                                # Return 0 safely — no spread
    return (x - mu) / sigma                                     # Subtract mean then divide by std dev → complete z = (x-μ)/σ

# Formula: x = μ + z * σ
# Returns the raw value corresponding to a z-score given the mean and standard deviation
def ZScoreToValue(z, mu, sigma):
    return mu + z * sigma                                       # Multiply z by std dev then add mean → complete x = μ + z*σ

# ============================================================
# PROBABILITY DISTRIBUTIONS
# ============================================================

# Formula: P(X = k) = C(n,k) * p^k * (1-p)^(n-k)
# Returns the probability of exactly k successes in n trials with success probability p
# Returns 0 if inputs are invalid
def BinomialPMF(n, k, p):
    if not (0 <= p <= 1) or k < 0 or k > n:                    # Guard against invalid inputs
        return 0                                                # Return 0 safely
    comb = math.factorial(n) // (math.factorial(k) * math.factorial(n - k))  # Binomial coefficient C(n,k)
    return comb * (p ** k) * ((1 - p) ** (n - k))              # Multiply all three terms → complete binomial PMF

# Formula: P(X ≤ k) = Σᵢ₌₀ᵏ C(n,i) * p^i * (1-p)^(n-i)
# Returns the cumulative binomial probability — probability of at most k successes
def BinomialCDF(n, k, p):
    if not (0 <= p <= 1) or k < 0:                             # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return sum(BinomialPMF(n, i, p) for i in range(min(k, n) + 1))  # Sum PMF from 0 to k → complete CDF

# Formula: P(X = k) = (λ^k * e^(-λ)) / k!
# Returns the Poisson probability of exactly k events given average rate λ
# Returns 0 if k is negative or λ is non-positive
def PoissonPMF(lam, k):
    if lam <= 0 or k < 0:                                      # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return (lam ** k * math.exp(-lam)) / math.factorial(k)     # Apply Poisson PMF formula → complete P(X=k)

# Formula: P(X ≤ k) = Σᵢ₌₀ᵏ (λ^i * e^(-λ)) / i!
# Returns the cumulative Poisson probability — probability of at most k events
def PoissonCDF(lam, k):
    if lam <= 0 or k < 0:                                      # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return sum(PoissonPMF(lam, i) for i in range(k + 1))       # Sum PMF from 0 to k → complete Poisson CDF

# Formula: f(x) = (1 / (σ√(2π))) * e^(-(x-μ)²/(2σ²))
# Returns the normal distribution probability density at x
# Returns 0 if standard deviation is non-positive
def NormalPDF(x, mu, sigma):
    if sigma <= 0:                                              # Guard against invalid standard deviation
        return 0                                                # Return 0 safely
    exponent = -((x - mu) ** 2) / (2 * sigma ** 2)             # Compute exponent term → -(x-μ)²/(2σ²)
    return (1 / (sigma * math.sqrt(2 * math.pi))) * math.exp(exponent)  # Multiply normalization constant → complete PDF

# Formula: Φ(x) = (1 + erf((x-μ)/(σ√2))) / 2
# Returns the cumulative normal distribution — probability that X ≤ x
# Uses the error function for numerical approximation
def NormalCDF(x, mu = 0, sigma = 1):
    if sigma <= 0:                                              # Guard against invalid standard deviation
        return 0                                                # Return 0 safely
    z = (x - mu) / (sigma * math.sqrt(2))                      # Standardize x → z = (x-μ)/(σ√2)
    return (1 + math.erf(z)) / 2                               # Apply erf approximation → complete Φ(x)

# Formula: P(a ≤ X ≤ b) = Φ(b) - Φ(a)
# Returns the probability that a normal random variable falls between a and b
def NormalProbBetween(a, b, mu = 0, sigma = 1):
    return NormalCDF(b, mu, sigma) - NormalCDF(a, mu, sigma)    # Subtract CDFs → complete P(a≤X≤b)

# Formula: f(x) = λe^(-λx)  for x ≥ 0
# Returns the exponential distribution probability density at x
# Returns 0 if x is negative or λ is non-positive
def ExponentialPDF(lam, x):
    if lam <= 0 or x < 0:                                      # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return lam * math.exp(-lam * x)                             # Multiply rate by decaying exponential → complete PDF

# Formula: F(x) = 1 - e^(-λx)  for x ≥ 0
# Returns the cumulative exponential probability — probability that X ≤ x
def ExponentialCDF(lam, x):
    if lam <= 0 or x < 0:                                      # Guard against invalid inputs
        return 0                                                # Return 0 safely
    return 1 - math.exp(-lam * x)                               # Subtract decaying exponential from 1 → complete CDF

# Formula: f(x) = 1/(b-a)  for a ≤ x ≤ b
# Returns the uniform distribution probability density — constant across [a, b]
# Returns 0 outside the interval or if a equals b
def UniformPDF(x, a, b):
    if b == a:                                                  # Guard against zero-width interval
        return 0                                                # Return 0 safely
    if x < a or x > b:                                         # Outside interval — probability is zero
        return 0                                                # Return 0
    return 1 / (b - a)                                          # Constant density → complete uniform PDF

# Formula: F(x) = (x - a) / (b - a)  for a ≤ x ≤ b
# Returns the cumulative uniform probability — fraction of interval covered up to x
def UniformCDF(x, a, b):
    if b == a:                                                  # Guard against zero-width interval
        return 0                                                # Return 0 safely
    if x <= a:                                                  # Below interval — no probability
        return 0
    if x >= b:                                                  # Above interval — full probability
        return 1
    return (x - a) / (b - a)                                    # Linear fraction of interval → complete CDF

# ============================================================
# SAMPLING AND ESTIMATION
# ============================================================

# Formula: standard error = σ / √n
# Returns the standard error of the mean — how much sample means vary from the true mean
# Returns 0 if n is zero or negative
def StandardError(sigma, n):
    if n <= 0:                                                  # Guard against invalid sample size
        return 0                                                # Return 0 safely
    return sigma / math.sqrt(n)                                 # Divide std dev by root of n → complete SE = σ/√n

# Formula: margin of error = z * (σ / √n)
# Returns the margin of error for a population mean estimate at a given z-score
# Common z values: 1.645 = 90%, 1.960 = 95%, 2.576 = 99%
# Returns 0 if n is zero or negative
def MarginOfError(z, sigma, n):
    if n <= 0:                                                  # Guard against invalid sample size
        return 0                                                # Return 0 safely
    return z * StandardError(sigma, n)                          # Scale standard error by z → complete margin of error

# Formula: CI = (x̄ - ME, x̄ + ME)
# Returns the confidence interval as a (lower, upper) tuple
# Uses z-score for the desired confidence level
def ConfidenceInterval(mean, z, sigma, n):
    me = MarginOfError(z, sigma, n)                             # Calculate margin of error first
    return (mean - me, mean + me)                               # Subtract and add ME from mean → complete CI tuple

# Formula: n = (z * σ / E)²
# Returns the minimum sample size needed to estimate a mean within margin E
# Returns 0 if E is zero or negative
def RequiredSampleSize(z, sigma, E):
    if E <= 0:                                                  # Guard against zero or negative margin
        return 0                                                # Return 0 safely
    return math.ceil((z * sigma / E) ** 2)                      # Square the ratio and round up → complete n = (zσ/E)²

# Formula: point estimate = x̄  (sample mean as best single estimate of population mean)
# Returns the sample mean as the point estimate for the population mean
def PointEstimate(sample):
    return Mean(sample)                                         # Point estimate is simply the sample mean → complete

# Formula: pooled variance = ((n1-1)*s1² + (n2-1)*s2²) / (n1+n2-2)
# Returns the pooled variance from two samples — used in two-sample t-tests
# Returns 0 if combined degrees of freedom is zero
def PooledVariance(data1, data2):
    n1, n2 = len(data1), len(data2)                             # Get sample sizes
    if n1 + n2 - 2 == 0:                                       # Guard against zero degrees of freedom
        return 0                                                # Return 0 safely
    s1_sq  = Variance(data1, population = False)                # Sample variance of first group
    s2_sq  = Variance(data2, population = False)                # Sample variance of second group
    return ((n1 - 1) * s1_sq + (n2 - 1) * s2_sq) / (n1 + n2 - 2)  # Weighted average → complete pooled variance

# ============================================================
# HYPOTHESIS TESTING
# ============================================================

# Formula: z = (x̄ - μ₀) / (σ / √n)
# Returns the one-sample z-test statistic
# Tests whether a sample mean differs significantly from a hypothesized population mean
# Returns 0 if standard error is zero
def ZTestStatistic(sample_mean, pop_mean, sigma, n):
    se = StandardError(sigma, n)                                # Calculate standard error
    if se == 0:                                                 # Guard against division by zero
        return 0                                                # Return 0 safely
    return (sample_mean - pop_mean) / se                        # Standardize the difference → complete z-statistic

# Formula: t = (x̄ - μ₀) / (s / √n)
# Returns the one-sample t-test statistic
# Used when population standard deviation is unknown — uses sample std dev instead
# Returns 0 if standard error is zero
def TTestStatistic(sample, hypothesized_mean):
    n  = len(sample)                                            # Sample size
    if n == 0:                                                  # Guard against empty sample
        return 0                                                # Return 0 safely
    se = StandardError(StandardDeviation(sample, population = False), n)  # Sample standard error
    if se == 0:                                                 # Guard against division by zero
        return 0                                                # Return 0 safely
    return (Mean(sample) - hypothesized_mean) / se             # Standardize difference → complete t-statistic

# Formula: t = (x̄₁ - x̄₂) / (sp * √(1/n1 + 1/n2))  where sp = sqrt(pooled variance)
# Returns the two-sample t-test statistic — tests if two group means are equal
# Returns 0 if pooled standard error is zero
def TwoSampleTTest(data1, data2):
    n1, n2   = len(data1), len(data2)                           # Get sample sizes
    if n1 == 0 or n2 == 0:                                     # Guard against empty samples
        return 0                                                # Return 0 safely
    sp       = math.sqrt(PooledVariance(data1, data2))          # Pooled standard deviation
    se       = sp * math.sqrt(1/n1 + 1/n2)                     # Standard error of the difference
    if se == 0:                                                 # Guard against division by zero
        return 0                                                # Return 0 safely
    return (Mean(data1) - Mean(data2)) / se                     # Standardize difference → complete two-sample t-stat

# Formula: p-value from z = 2 * (1 - Φ(|z|))  (two-tailed)
# Returns the two-tailed p-value corresponding to a z-test statistic
# Smaller p-value = stronger evidence against the null hypothesis
def PValueFromZ(z):
    return 2 * (1 - NormalCDF(abs(z)))                          # Double the one-tail area → complete two-tailed p-value

# Formula: chi-squared statistic = Σ (observed - expected)² / expected
# Returns the chi-squared test statistic for goodness of fit or independence
# Returns 0 if any expected value is zero
def ChiSquaredStatistic(observed, expected):
    if len(observed) != len(expected):                          # Guard against mismatched list lengths
        return 0                                                # Return 0 safely
    if any(e == 0 for e in expected):                           # Guard against division by zero
        return 0                                                # Return 0 safely
    return sum((o - e) ** 2 / e for o, e in zip(observed, expected))  # Sum squared deviations over expected → complete χ²

# Formula: reject null if |z| > z_critical or p < alpha
# Returns True if the null hypothesis is rejected at the given significance level
# Uses the two-tailed z-test for simplicity
def RejectNull(z_stat, alpha = 0.05):
    p_value = PValueFromZ(z_stat)                               # Calculate the two-tailed p-value from z
    return p_value < alpha                                      # Reject if p-value is below significance level

# ============================================================
# CORRELATION AND REGRESSION
# ============================================================

# Formula: r = Σ(xᵢ-x̄)(yᵢ-ȳ) / (n-1) * sx * sy
# Returns the Pearson correlation coefficient r — measures linear association strength
# r = 1 perfect positive, r = -1 perfect negative, r = 0 no linear correlation
# Returns 0 if either standard deviation is zero or lists are mismatched
def PearsonCorrelation(x_data, y_data):
    n = len(x_data)                                             # Count data points
    if n != len(y_data) or n < 2:                              # Guard against mismatched or insufficient data
        return 0                                                # Return 0 safely
    sx = StandardDeviation(x_data, population = False)          # Sample std dev of x
    sy = StandardDeviation(y_data, population = False)          # Sample std dev of y
    if sx == 0 or sy == 0:                                     # Guard against division by zero
        return 0                                                # Return 0 safely — no variation in one variable
    x_mean = Mean(x_data)                                       # Mean of x
    y_mean = Mean(y_data)                                       # Mean of y
    cov    = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_data, y_data)) / (n - 1)  # Sample covariance
    return cov / (sx * sy)                                      # Divide by product of std devs → complete r

# Formula: rs = 1 - (6 * Σd²) / (n * (n²-1))
# Returns Spearman's rank correlation coefficient — non-parametric correlation
# Works on ranks rather than raw values — handles non-linear monotonic relationships
# Returns 0 if fewer than 2 data points or lists are mismatched
def SpearmanCorrelation(x_data, y_data):
    n = len(x_data)                                             # Count data points
    if n != len(y_data) or n < 2:                              # Guard against mismatched or insufficient data
        return 0                                                # Return 0 safely
    x_ranks = _Rank(x_data)                                     # Assign ranks to x values
    y_ranks = _Rank(y_data)                                     # Assign ranks to y values
    d_sq    = sum((rx - ry) ** 2 for rx, ry in zip(x_ranks, y_ranks))  # Sum of squared rank differences
    return 1 - (6 * d_sq) / (n * (n ** 2 - 1))                # Apply Spearman formula → complete rs

# Internal helper — assigns ranks to a list with ties averaged
def _Rank(data):
    sorted_vals = sorted(enumerate(data), key = lambda x: x[1])  # Sort by value keeping original indices
    ranks       = [0] * len(data)                               # Initialize rank list
    i           = 0                                             # Start rank index
    while i < len(sorted_vals):                                 # Loop through sorted values
        j = i                                                   # Find end of tied group
        while j < len(sorted_vals) - 1 and sorted_vals[j][1] == sorted_vals[j+1][1]:
            j += 1                                              # Advance through all tied values
        avg_rank = (i + j) / 2 + 1                             # Average rank for tied group (1-indexed)
        for k in range(i, j + 1):                              # Assign average rank to all tied items
            ranks[sorted_vals[k][0]] = avg_rank                 # Place rank at original index
        i = j + 1                                               # Move to next non-tied group
    return ranks                                                # Return list of ranks

# Formula: covariance = Σ(xᵢ-x̄)(yᵢ-ȳ) / (n-1)
# Returns the sample covariance — how much two variables move together
# Positive = same direction, Negative = opposite direction, Zero = no linear relationship
# Returns 0 if lists are mismatched or fewer than 2 data points
def Covariance(x_data, y_data):
    n = len(x_data)                                             # Count data points
    if n != len(y_data) or n < 2:                              # Guard against mismatched or insufficient data
        return 0                                                # Return 0 safely
    x_mean = Mean(x_data)                                       # Mean of x
    y_mean = Mean(y_data)                                       # Mean of y
    return sum((x - x_mean) * (y - y_mean) for x, y in zip(x_data, y_data)) / (n - 1)  # Complete sample covariance

# Formula: b1 = Σ(xᵢ-x̄)(yᵢ-ȳ) / Σ(xᵢ-x̄)²  and  b0 = ȳ - b1*x̄
# Returns the (slope, intercept) of the simple linear regression line y = b0 + b1*x
# Returns (0, 0) if x variance is zero or data is insufficient
def LinearRegression(x_data, y_data):
    n = len(x_data)                                             # Count data points
    if n != len(y_data) or n < 2:                              # Guard against mismatched or insufficient data
        return (0, 0)                                           # Return (0,0) safely
    x_mean  = Mean(x_data)                                      # Mean of x
    y_mean  = Mean(y_data)                                      # Mean of y
    ss_xy   = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_data, y_data))  # Cross-deviations
    ss_xx   = sum((x - x_mean) ** 2 for x in x_data)           # Squared deviations of x
    if ss_xx == 0:                                              # Guard against division by zero — no x variation
        return (0, 0)                                           # Return (0,0) safely
    slope     = ss_xy / ss_xx                                   # Slope = cross-deviations / x variance
    intercept = y_mean - slope * x_mean                         # Intercept = ȳ - b1*x̄
    return (slope, intercept)                                    # Return (b1, b0) tuple

# Formula: ŷ = b0 + b1*x
# Returns the predicted y value for a given x using a regression line
def Predict(x, slope, intercept):
    return intercept + slope * x                                # Plug x into the regression line → complete ŷ = b0 + b1*x

# Formula: R² = 1 - SS_res / SS_tot
# Returns the coefficient of determination — how much variance in y is explained by x
# R² = 1 means perfect fit, R² = 0 means the model explains nothing
# Returns 0 if total sum of squares is zero
def RSquared(x_data, y_data):
    slope, intercept = LinearRegression(x_data, y_data)        # Fit the regression line
    y_mean   = Mean(y_data)                                     # Mean of actual y values
    ss_tot   = sum((y - y_mean) ** 2 for y in y_data)          # Total sum of squares
    if ss_tot == 0:                                             # Guard against division by zero
        return 0                                                # Return 0 safely — no variance to explain
    ss_res   = sum((y - Predict(x, slope, intercept)) ** 2 for x, y in zip(x_data, y_data))  # Residual sum of squares
    return 1 - ss_res / ss_tot                                  # Subtract residual ratio → complete R²

# Formula: residual = yᵢ - ŷᵢ
# Returns a list of residuals — the difference between each actual y and its predicted value
def Residuals(x_data, y_data):
    slope, intercept = LinearRegression(x_data, y_data)        # Fit the regression line
    return [y - Predict(x, slope, intercept) for x, y in zip(x_data, y_data)]  # Subtract predictions from actuals

# ============================================================
# COUNTING AND FREQUENCY
# ============================================================

# Formula: frequency count — how many times each unique value appears
# Returns a dictionary mapping each unique value to its count
def FrequencyTable(data):
    table = {}                                                  # Initialize empty frequency dictionary
    for value in data:                                          # Loop through every value
        table[value] = table.get(value, 0) + 1                 # Increment count for this value
    return dict(sorted(table.items()))                          # Return sorted dictionary

# Formula: relative frequency = count / n
# Returns a dictionary mapping each unique value to its relative frequency (proportion)
# Returns empty dict if data is empty
def RelativeFrequency(data):
    if not data:                                                # Guard against empty list
        return {}                                               # Return empty dict safely
    n     = len(data)                                           # Total count
    table = FrequencyTable(data)                                # Get raw frequency counts
    return {k: v / n for k, v in table.items()}                # Divide each count by n → complete relative frequency

# Formula: cumulative frequency — running total of counts
# Returns a list of cumulative frequencies matching the sorted unique values
def CumulativeFrequency(data):
    if not data:                                                # Guard against empty list
        return []                                               # Return empty list safely
    table  = FrequencyTable(data)                               # Get frequency of each unique value
    keys   = sorted(table.keys())                               # Sort the keys
    cumul  = []                                                 # Initialize cumulative list
    total  = 0                                                  # Running total
    for k in keys:                                              # Loop through sorted keys
        total += table[k]                                       # Add this value's count to the running total
        cumul.append((k, total))                                # Append (value, cumulative count) pair
    return cumul                                                # Return list of cumulative frequency pairs

# Formula: outlier detection using IQR — values below Q1-1.5*IQR or above Q3+1.5*IQR
# Returns a list of values that are statistical outliers using the Tukey fence method
def Outliers(data):
    if not data:                                                # Guard against empty list
        return []                                               # Return empty list safely
    q1, _, q3 = Quartiles(data)                                 # Get Q1 and Q3
    iqr        = q3 - q1                                        # Calculate IQR
    lower      = q1 - 1.5 * iqr                                 # Lower Tukey fence
    upper      = q3 + 1.5 * iqr                                 # Upper Tukey fence
    return [x for x in data if x < lower or x > upper]         # Return values outside the fences → complete outlier list

# Formula: standardize all values — transform to z-scores
# Returns a list of z-scores for every value in data
# Returns list of zeros if standard deviation is zero
def Standardize(data):
    mu    = Mean(data)                                          # Calculate mean
    sigma = StandardDeviation(data, population = True)          # Population standard deviation
    if sigma == 0:                                              # Guard against division by zero
        return [0] * len(data)                                  # Return zeros safely
    return [(x - mu) / sigma for x in data]                    # Subtract mean and divide by std dev → complete z-scores

# Formula: normalize to [0, 1] range — (x - min) / (max - min)
# Returns a list of values scaled to the range [0, 1]
# Returns list of zeros if max equals min
def Normalize(data):
    if not data:                                                # Guard against empty list
        return []                                               # Return empty list safely
    lo = min(data)                                              # Minimum value
    hi = max(data)                                              # Maximum value
    if hi == lo:                                                # Guard against division by zero — all values equal
        return [0.0] * len(data)                               # Return zeros safely
    return [(x - lo) / (hi - lo) for x in data]                # Scale each value to [0,1] → complete normalization
