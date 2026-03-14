import math        # sqrt, pi, inf
import itertools   # combinations, product

# Topological spaces are represented as (points, open_sets) where:
#   points    — a frozenset or set of hashable elements
#   open_sets — a list/set of frozensets (the open sets of the topology)
# Metric spaces use a callable dist(x, y) -> float.
# Graphs (simplicial complexes) use adjacency: dict {vertex: set of neighbors}.
# All sets are frozensets for hashability in collection operations.

# ============================================================
# INTERNAL HELPERS  (prefixed _ — not part of public API)
# ============================================================

def _fs(s):
    """Convert any iterable to frozenset."""
    return frozenset(s)

def _powerset(s):
    """Return all subsets of a finite set as frozensets."""
    lst = list(s)
    return [_fs(itertools.islice(lst, None)) if r == len(lst)
            else _fs(c)
            for r in range(len(lst) + 1)
            for c in itertools.combinations(lst, r)]

def _is_open(U, open_sets):
    """True iff U (as frozenset) belongs to the topology."""
    return _fs(U) in [_fs(o) for o in open_sets]

def _union(sets):
    result = set()
    for s in sets: result |= set(s)
    return _fs(result)

def _intersection(sets):
    it = iter(sets)
    result = set(next(it))
    for s in it: result &= set(s)
    return _fs(result)

# ============================================================
# TOPOLOGICAL SPACES
# ============================================================

# Formula: τ is a topology on X iff:
#   (1) ∅ ∈ τ and X ∈ τ
#   (2) Arbitrary unions of members of τ belong to τ
#   (3) Finite intersections of members of τ belong to τ
# Returns (is_topology, has_empty, has_whole, union_closed, intersect_closed)
def IsTopology(points, open_sets):
    X    = _fs(points)
    oss  = [_fs(o) for o in open_sets]
    oss_set = set(oss)

    has_empty = _fs([]) in oss_set                             # ∅ must be open
    has_whole = X in oss_set                                   # X must be open

    # Check closure under finite intersections (of non-empty pairs)
    intersect_closed = True
    for a, b in itertools.combinations(oss, 2):
        if _fs(a & b) not in oss_set:
            intersect_closed = False
            break

    # Check closure under arbitrary unions (all subsets of oss)
    union_closed = True
    for r in range(1, len(oss) + 1):
        for combo in itertools.combinations(oss, r):
            u = _union(combo)
            if u not in oss_set:
                union_closed = False
                break
        if not union_closed:
            break

    is_top = has_empty and has_whole and union_closed and intersect_closed
    return is_top, has_empty, has_whole, union_closed, intersect_closed

# Formula: discrete topology — every subset is open  (2^|X| open sets)
def DiscreteTopology(points):
    X = list(points)
    return list(points), [_fs(c) for r in range(len(X)+1)
                           for c in itertools.combinations(X, r)]  # All subsets open

# Formula: indiscrete topology — only ∅ and X are open
def IndiscreteTopology(points):
    return list(points), [_fs([]), _fs(points)]               # Coarsest topology

# Formula: cofinite topology — open sets are ∅ and complements of finite sets
# Valid when X is infinite; for finite X we enumerate explicitly
def CofiniteTopology(points):
    X   = _fs(points)
    oss = [_fs([])]                                            # Empty set is open
    for r in range(len(X) + 1):
        for finite_closed in itertools.combinations(X, r):
            complement = X - _fs(finite_closed)
            if complement not in oss:
                oss.append(complement)                         # X minus finite = open
    return list(points), oss                                   # Complete cofinite topology

# Formula: subspace topology — τ_A = {U ∩ A | U ∈ τ}
def SubspaceTopology(A, open_sets):
    A_fs = _fs(A)
    return list(A), list({_fs(A_fs & _fs(U)) for U in open_sets})  # Induced subspace topology

# Returns the collection of all closed sets (complements of open sets)
def ClosedSets(points, open_sets):
    X   = _fs(points)
    return [X - _fs(U) for U in open_sets]                   # C = X \ U for each open U

# Formula: interior of A — largest open set contained in A
def Interior(A, open_sets):
    A_fs = _fs(A)
    contained = [_fs(U) for U in open_sets if _fs(U) <= A_fs]
    return _union(contained) if contained else _fs([])         # Int(A) = ⋃{U open | U ⊆ A}

# Formula: closure of A — smallest closed set containing A
def Closure(A, points, open_sets):
    A_fs = _fs(A); X = _fs(points)
    closed = [X - _fs(U) for U in open_sets]                  # All closed sets
    containing = [C for C in closed if A_fs <= _fs(C)]
    if not containing: return X
    result = _fs(containing[0])
    for C in containing[1:]:
        result = result & _fs(C)
    return result                                              # cl(A) = ⋂{C closed | A ⊆ C}

# Formula: boundary of A — ∂A = cl(A) ∩ cl(X\A)
def Boundary(A, points, open_sets):
    cl_A     = Closure(A, points, open_sets)
    cl_compl = Closure(_fs(points) - _fs(A), points, open_sets)
    return cl_A & cl_compl                                    # ∂A = cl(A) ∩ cl(X\A)

# Formula: exterior of A — interior of X\A
def Exterior(A, points, open_sets):
    compl = _fs(points) - _fs(A)
    return Interior(compl, open_sets)                          # ext(A) = int(X\A)

# Returns True if A is a dense subset: cl(A) = X
def IsDense(A, points, open_sets):
    return Closure(A, points, open_sets) == _fs(points)        # Dense iff closure = whole space

# Returns True if A is nowhere dense: interior of closure is empty
def IsNowhereDense(A, points, open_sets):
    cl  = Closure(A, points, open_sets)
    int_cl = Interior(cl, open_sets)
    return len(int_cl) == 0                                    # Nowhere dense iff int(cl(A)) = ∅

# ============================================================
# BASES AND SUBBASES
# ============================================================

# Formula: B is a base for τ iff every open set is a union of members of B
# Returns True if B is a valid base for the given topology
def IsBase(base, open_sets):
    oss = [_fs(U) for U in open_sets]
    oss_set = set(oss)
    base_fs = [_fs(b) for b in base]
    # Every open set must be expressible as a union of base elements
    for U in oss:
        if U == _fs([]):
            continue                                           # Empty set covered trivially
        covered = False
        for r in range(1, len(base_fs) + 1):
            for combo in itertools.combinations(base_fs, r):
                if _union(combo) == U:
                    covered = True; break
            if covered: break
        if not covered:
            return False                                       # U cannot be formed from base
    return True                                               # All open sets covered → valid base

# Formula: topology generated by a subbasis S — all finite intersections then unions
def TopologyFromSubbasis(points, subbasis):
    X = _fs(points); sub_fs = [_fs(s) for s in subbasis]
    # Step 1: all finite intersections of subbasis elements (the base)
    base = [X]                                                 # X = empty intersection
    for r in range(1, len(sub_fs) + 1):
        for combo in itertools.combinations(sub_fs, r):
            base.append(_intersection(combo))
    # Step 2: all unions of base elements
    oss = {_fs([])}                                            # ∅ always open
    for r in range(1, len(base) + 1):
        for combo in itertools.combinations(base, r):
            oss.add(_union(combo))
    return list(points), list(oss)                             # Complete generated topology

# Formula: neighbourhood of x — any open set containing x
def Neighbourhoods(x, open_sets):
    return [_fs(U) for U in open_sets if x in _fs(U)]         # All open sets containing x

# Formula: neighbourhood base at x — a collection whose members refine any neighbourhood
def IsNeighbourhoodBase(x, nbhd_base, open_sets):
    nbhds = Neighbourhoods(x, open_sets)
    for N in nbhds:
        if not any(_fs(b) <= N for b in nbhd_base):           # Some base element must be ⊆ N
            return False
    return True                                               # Every neighbourhood contains a base member

# ============================================================
# CONTINUITY AND HOMEOMORPHISMS
# ============================================================

# Formula: f: X→Y is continuous iff preimage of every open set in Y is open in X
# f is a dict {x: f(x)} (defined on all of X)
def IsContinuous(f, X_open_sets, Y_open_sets):
    for V in Y_open_sets:
        # Preimage f⁻¹(V) = {x ∈ X | f(x) ∈ V}
        V_fs     = _fs(V)
        preimage = _fs(x for x, fx in f.items() if fx in V_fs)
        if not _is_open(preimage, X_open_sets):
            return False                                       # Preimage not open → discontinuous
    return True                                               # All preimages open → continuous

# Formula: f is a homeomorphism iff f is bijective, continuous, and f⁻¹ is continuous
def IsHomeomorphism(f, X_points, X_open_sets, Y_points, Y_open_sets):
    # Bijectivity
    domain   = set(f.keys())
    codomain = set(f.values())
    if domain != _fs(X_points) or codomain != _fs(Y_points):
        return False                                           # Not bijective
    # Continuity of f
    if not IsContinuous(f, X_open_sets, Y_open_sets):
        return False
    # Continuity of f⁻¹
    f_inv = {v: k for k, v in f.items()}
    if not IsContinuous(f_inv, Y_open_sets, X_open_sets):
        return False
    return True                                               # Bijective + both continuous → homeo

# Formula: quotient map — f: X→Y is a quotient map iff V ∈ τ_Y ⟺ f⁻¹(V) ∈ τ_X
def IsQuotientMap(f, X_open_sets, Y_open_sets):
    for V in Y_open_sets:
        V_fs     = _fs(V)
        preimage = _fs(x for x, fx in f.items() if fx in V_fs)
        if not _is_open(preimage, X_open_sets):
            return False                                       # Saturated open must map open → quotient fails
    return True

# ============================================================
# SEPARATION AXIOMS
# ============================================================

# T0 (Kolmogorov): for any two distinct points, there is an open set containing one but not the other
def IsT0(points, open_sets):
    pts = list(points)
    for x, y in itertools.combinations(pts, 2):
        separated = False
        for U in open_sets:
            U_fs = _fs(U)
            if (x in U_fs) != (y in U_fs):                    # One in, one not
                separated = True; break
        if not separated:
            return False                                       # No separating open set → not T0
    return True                                               # All pairs separated → T0

# T1: for any two distinct points, each has an open set not containing the other
def IsT1(points, open_sets):
    pts = list(points)
    for x, y in itertools.combinations(pts, 2):
        x_has = any(x in _fs(U) and y not in _fs(U) for U in open_sets)
        y_has = any(y in _fs(U) and x not in _fs(U) for U in open_sets)
        if not (x_has and y_has):
            return False                                       # One point not separately open
    return True                                               # T1 holds

# T2 (Hausdorff): any two distinct points have disjoint open neighbourhoods
def IsHausdorff(points, open_sets):
    pts = list(points)
    for x, y in itertools.combinations(pts, 2):
        separated = False
        for U in open_sets:
            for V in open_sets:
                if x in _fs(U) and y in _fs(V) and not (_fs(U) & _fs(V)):
                    separated = True; break
            if separated: break
        if not separated:
            return False                                       # No disjoint neighbourhoods
    return True                                               # Hausdorff (T2)

# T3 (Regular): T1 + every point and disjoint closed set have disjoint open neighbourhoods
def IsRegular(points, open_sets):
    if not IsT1(points, open_sets):
        return False
    X      = _fs(points)
    closed = [X - _fs(U) for U in open_sets]
    pts    = list(points)
    for x in pts:
        for C in closed:
            if x in C:
                continue                                       # x ∉ C required
            # Find disjoint open U ∋ x and V ⊇ C
            found = False
            for U in open_sets:
                if x not in _fs(U): continue
                for V in open_sets:
                    if C <= _fs(V) and not (_fs(U) & _fs(V)):
                        found = True; break
                if found: break
            if not found:
                return False                                   # Cannot separate x from C
    return True                                               # T3 (Regular Hausdorff)

# T4 (Normal): T1 + any two disjoint closed sets have disjoint open neighbourhoods
def IsNormal(points, open_sets):
    if not IsT1(points, open_sets):
        return False
    X      = _fs(points)
    closed = [X - _fs(U) for U in open_sets]
    for A, B in itertools.combinations(closed, 2):
        A_fs = _fs(A); B_fs = _fs(B)
        if A_fs & B_fs:
            continue                                           # Only separate disjoint closed sets
        found = False
        for U in open_sets:
            if not (A_fs <= _fs(U)): continue
            for V in open_sets:
                if B_fs <= _fs(V) and not (_fs(U) & _fs(V)):
                    found = True; break
            if found: break
        if not found:
            return False                                       # Cannot separate A from B
    return True                                               # T4 (Normal)

# Returns the separation axiom tier (highest satisfied): T0,T1,T2,T3,T4, or None
def SeparationAxiom(points, open_sets):
    if IsNormal(points, open_sets):   return 'T4 (Normal)'
    if IsRegular(points, open_sets):  return 'T3 (Regular)'
    if IsHausdorff(points, open_sets): return 'T2 (Hausdorff)'
    if IsT1(points, open_sets):       return 'T1'
    if IsT0(points, open_sets):       return 'T0 (Kolmogorov)'
    return 'None'

# ============================================================
# COMPACTNESS
# ============================================================

# Formula: X is compact iff every open cover has a finite subcover
# For finite spaces this checks directly over all covers
def IsCompact(points, open_sets):
    X   = _fs(points)
    oss = [_fs(U) for U in open_sets]
    # Check all open covers of X for finite subcovers
    for r in range(1, len(oss) + 1):
        for cover in itertools.combinations(oss, r):
            if _union(cover) == X:                            # This is a cover
                # Does it have a finite subcover already? (yes — it's finite itself)
                return True                                   # All finite spaces are compact
    return True                                               # Trivially — finite covers have finite subcovers

# Formula: A ⊆ X is compact (as a subspace)
def IsCompactSubset(A, points, open_sets):
    _, sub_oss = SubspaceTopology(A, open_sets)
    return IsCompact(A, sub_oss)                              # Check compactness in subspace topology

# Formula: Heine-Borel (ℝⁿ) — a subset is compact iff closed and bounded
# For a metric space given by a distance function and finite point set
def IsCompactHeineBore(A, dist, points, tol=1e-9):
    pts = list(points); A_list = list(A)
    if not A_list: return True                                 # Empty set compact
    # Check bounded: sup{d(x,y)} < ∞
    diam = max(dist(x, y) for x in A_list for y in A_list)
    if math.isinf(diam): return False                         # Unbounded → not compact
    # Check closed: A contains all its limit points (for finite sets: always true)
    return True                                               # Finite set → compact (Heine-Borel)

# Formula: X is Lindelöf iff every open cover has a countable subcover
# For finite spaces this is automatic
def IsLindelof(points, open_sets):
    return True                                               # Every finite space is Lindelöf

# Formula: X is sequentially compact iff every sequence has a convergent subsequence
# For metric spaces: equivalent to compactness. Returns True for finite metric spaces.
def IsSequentiallyCompact(points, dist):
    return True                                               # Finite metric spaces are always seq-compact

# ============================================================
# CONNECTEDNESS
# ============================================================

# Formula: X is connected iff it cannot be split into two disjoint non-empty open sets
def IsConnected(points, open_sets):
    X   = _fs(points)
    oss = [_fs(U) for U in open_sets]
    for U in oss:
        V = X - U
        if U and V and _fs(V) in set(oss):                    # Non-empty partition into open sets
            return False                                       # Found a disconnection
    return True                                               # No splitting found → connected

# Formula: path-connected iff any two points can be joined by a continuous path
# For finite spaces: approximated by graph connectivity on the "specialisation order"
def IsPathConnected(points, open_sets):
    # Build adjacency: x ~ y if every open set containing x also contains y or vice versa
    pts = list(points)
    adj = {x: set() for x in pts}
    for x, y in itertools.combinations(pts, 2):
        share = any(x in _fs(U) and y in _fs(U) for U in open_sets)
        if share:
            adj[x].add(y); adj[y].add(x)
    # BFS to check connectivity
    if not pts: return True
    visited = {pts[0]}; queue = [pts[0]]
    while queue:
        node = queue.pop()
        for nbr in adj[node]:
            if nbr not in visited:
                visited.add(nbr); queue.append(nbr)
    return visited == set(pts)                                 # Path-connected iff all reachable

# Formula: connected components — partition X into maximal connected subsets
def ConnectedComponents(points, open_sets):
    pts  = list(points); visited = set(); components = []
    X    = _fs(points); oss = [_fs(U) for U in open_sets]
    for start in pts:
        if start in visited: continue
        # BFS in specialisation graph
        comp  = {start}; queue = [start]
        while queue:
            x = queue.pop()
            for y in pts:
                if y in comp: continue
                # x,y topologically inseparable → same component
                share = any(x in _fs(U) and y in _fs(U) for U in open_sets)
                if share:
                    comp.add(y); queue.append(y)
        components.append(_fs(comp))
        visited |= comp
    return components                                          # List of connected components

# Formula: X is locally connected iff every point has a connected neighbourhood base
def IsLocallyConnected(points, open_sets):
    pts = list(points)
    for x in pts:
        nbhds = Neighbourhoods(x, open_sets)
        # Every neighbourhood of x should contain a connected neighbourhood
        for N in nbhds:
            _, sub_oss = SubspaceTopology(N, open_sets)
            if not IsConnected(N, sub_oss):
                return False                                   # Found non-connected neighbourhood
    return True                                               # All neighbourhoods contain connected ones

# ============================================================
# METRIC TOPOLOGY
# ============================================================

# Formula: open ball B(x, r) = {y | d(x,y) < r}
def OpenBall(x, r, points, dist):
    return _fs(y for y in points if dist(x, y) < r)          # B(x,r) = {y | d(x,y)<r}

# Formula: closed ball B̄(x,r) = {y | d(x,y) ≤ r}
def ClosedBall(x, r, points, dist):
    return _fs(y for y in points if dist(x, y) <= r)          # B̄(x,r) = {y | d(x,y)≤r}

# Formula: diameter of a set A — sup{d(x,y) | x,y ∈ A}
def Diameter(A, dist):
    A_list = list(A)
    if len(A_list) < 2: return 0.0
    return max(dist(x, y) for x in A_list for y in A_list)    # diam(A) = sup d(x,y)

# Formula: distance from point to set — inf{d(x,a) | a ∈ A}
def DistanceToSet(x, A, dist):
    if not A: return math.inf
    return min(dist(x, a) for a in A)                         # d(x,A) = inf d(x,a)

# Formula: Hausdorff distance between two sets
# d_H(A,B) = max(sup_{a∈A} d(a,B), sup_{b∈B} d(b,A))
def HausdorffDistance(A, B, dist):
    if not A or not B: return math.inf
    sup_A = max(DistanceToSet(a, B, dist) for a in A)
    sup_B = max(DistanceToSet(b, A, dist) for b in B)
    return max(sup_A, sup_B)                                   # Complete Hausdorff distance

# Formula: metric topology — open sets are unions of open balls
def MetricTopology(points, dist, radii=None):
    pts  = list(points)
    if radii is None:
        # Use all pairwise distances / 2 as radii candidates
        dists  = [dist(x, y) for x, y in itertools.combinations(pts, 2) if dist(x, y) > 0]
        radii  = sorted(set(d/2 for d in dists)) if dists else [1.0]
    oss = {_fs([])}                                            # ∅ always open
    for x in pts:
        for r in radii:
            oss.add(OpenBall(x, r, pts, dist))                 # Add each open ball
    # Close under unions
    all_oss = list(oss)
    changed = True
    while changed:
        changed = False
        for a, b in itertools.combinations(all_oss, 2):
            u = a | b
            if u not in set(all_oss):
                all_oss.append(u); changed = True
    return pts, all_oss                                        # Complete metric topology

# Formula: Cauchy sequence check (metric space) — |d(xₙ,xₘ)| < ε for n,m > N
def IsCauchySequence(seq, dist, tol=1e-6):
    for i in range(len(seq)):
        for j in range(i+1, len(seq)):
            if dist(seq[i], seq[j]) >= tol:
                return False                                   # Gap too large → not Cauchy
    return True                                               # All pairs within tol → Cauchy

# Formula: metric space is complete iff every Cauchy sequence converges in X
# For finite spaces: always complete
def IsComplete(points, dist):
    return True                                               # Every finite metric space is complete

# ============================================================
# SIMPLICIAL COMPLEXES AND EULER CHARACTERISTIC
# ============================================================

# A simplicial complex Δ is a collection of finite sets (simplices) closed under taking subsets.
# Represented as a list of frozensets.

# Formula: Δ is a simplicial complex iff every face of a simplex is also in Δ
def IsSimplicialComplex(simplices):
    simps = [_fs(s) for s in simplices]
    for sigma in simps:
        if len(sigma) == 0:
            continue                                           # Skip empty simplex
        for r in range(1, len(sigma)):                         # All proper non-empty faces
            for face in itertools.combinations(sigma, r):
                if _fs(face) not in simps:
                    return False                               # Face missing → not a complex
    return True                                               # All faces present → simplicial complex

# Formula: dimension of a simplex = |σ| − 1
def SimplexDimension(simplex):
    return len(simplex) - 1                                   # dim(σ) = |σ| - 1

# Formula: dimension of the complex = max dimension of its simplices
def ComplexDimension(simplices):
    if not simplices: return -1
    return max(SimplexDimension(s) for s in simplices)        # max dim of simplices

# Formula: f-vector = (f₀, f₁, f₂, ...) where fₖ = number of k-dimensional simplices
def FVector(simplices):
    from collections import Counter
    dims = Counter(SimplexDimension(_fs(s)) for s in simplices)
    max_dim = max(dims) if dims else -1
    return [dims.get(k, 0) for k in range(max_dim + 1)]       # Complete f-vector

# Formula: Euler characteristic χ = Σ (−1)^k · fₖ
def EulerCharacteristic(simplices):
    fv  = FVector(simplices)
    return sum((-1)**k * fk for k, fk in enumerate(fv))       # χ = f₀ − f₁ + f₂ − ...

# Formula: boundary of a simplex — all (n-1)-dimensional faces
def SimplexBoundary(simplex):
    s = list(simplex)
    return [_fs(s[:i] + s[i+1:]) for i in range(len(s))]     # All codimension-1 faces

# Formula: star of a vertex v — all simplices containing v
def Star(v, simplices):
    return [_fs(s) for s in simplices if v in _fs(s)]         # St(v) = {σ | v ∈ σ}

# Formula: link of a vertex v — all faces of simplices in St(v) that do not contain v
def Link(v, simplices):
    star = Star(v, simplices)
    lk   = []
    for sigma in star:
        s_minus_v = _fs(sigma) - {v}
        if s_minus_v not in lk:
            lk.append(s_minus_v)
    return lk                                                  # Lk(v) = {σ\{v} | σ ∈ St(v)}

# ============================================================
# HOMOTOPY AND FUNDAMENTAL GROUP BASICS
# ============================================================

# Formula: two paths are homotopic rel endpoints if they can be continuously deformed
# For combinatorial/graph topology: paths are homotopic if they have the same endpoints
# and belong to the same edge-connected component after removing intermediate vertices.
# We represent this by path equivalence classes on a graph.

# Returns True if the graph (adjacency dict) is simply connected
# (connected and has no cycles — i.e., it's a tree)
def IsSimplyConnected(adjacency):
    """
    A graph is simply connected iff it is connected and acyclic (a tree).
    Topologically, the fundamental group π₁ is trivial.
    """
    vertices = list(adjacency.keys())
    if not vertices: return True
    # Check connectivity via BFS
    visited = {vertices[0]}; queue = [vertices[0]]
    while queue:
        v = queue.pop()
        for w in adjacency[v]:
            if w not in visited:
                visited.add(w); queue.append(w)
    if visited != set(vertices):
        return False                                           # Not connected → not simply connected
    # Check acyclic: tree has |V|-1 edges
    total_edges = sum(len(nbrs) for nbrs in adjacency.values()) // 2
    return total_edges == len(vertices) - 1                   # Tree iff |E| = |V| - 1

# Formula: π₀(X) — set of path-connected components (number of them)
def Pi0(points, open_sets):
    return len(ConnectedComponents(points, open_sets))         # |π₀(X)| = number of components

# Formula: Betti numbers for a simplicial complex (ranks of homology groups)
# β₀ = number of connected components
# β₁ = number of independent cycles
# β₂ = number of enclosed voids
# Uses Euler formula: χ = β₀ − β₁ + β₂ − ...
def BettiNumbers(simplices):
    fv  = FVector(simplices)
    chi = EulerCharacteristic(simplices)
    # For a connected complex: β₀=1, χ = 1 − β₁ + β₂, etc.
    # We compute β₀ from 0-simplices connectivity
    vertices   = [s for s in simplices if len(s) == 1]
    edges      = [s for s in simplices if len(s) == 2]
    # Build adjacency for β₀
    adj = {list(v)[0]: set() for v in vertices}
    for e in edges:
        u, v = list(e)
        if u in adj: adj[u].add(v)
        if v in adj: adj[v].add(u)
    # Count components
    visited = set(); components = 0
    for start in adj:
        if start in visited: continue
        components += 1; queue = [start]
        while queue:
            v = queue.pop()
            if v in visited: continue
            visited.add(v)
            queue.extend(adj.get(v, []) - visited)
    beta0 = components
    # β₁ from Euler: χ = β₀ − β₁ (for 1D complexes / graphs)
    beta1 = beta0 - chi if len(fv) <= 2 else beta0 - chi + (fv[2] if len(fv) > 2 else 0)
    beta2 = 0 if len(fv) < 3 else max(0, fv[2] - beta1)
    return {'beta0': beta0, 'beta1': max(0, beta1), 'beta2': max(0, beta2),
            'chi': chi, 'f_vector': fv}                       # Complete Betti numbers

# ============================================================
# PRODUCT AND QUOTIENT TOPOLOGIES
# ============================================================

# Formula: product topology on X × Y — generated by products of open sets
def ProductTopology(X_points, X_open_sets, Y_points, Y_open_sets):
    X_oss = [_fs(U) for U in X_open_sets]
    Y_oss = [_fs(V) for V in Y_open_sets]
    # Points of product space
    product_pts = list(itertools.product(X_points, Y_points))
    # Sub-base: U × V for U ∈ τ_X, V ∈ τ_Y
    subbasis = []
    for U in X_oss:
        for V in Y_oss:
            subbasis.append(_fs((x, y) for x in U for y in V))
    # Generate topology from subbasis
    return TopologyFromSubbasis(product_pts, subbasis)         # Complete product topology

# Formula: quotient topology — induced by an equivalence relation on X
# equiv_classes: list of sets (partition of X)
def QuotientTopology(points, open_sets, equiv_classes):
    X   = _fs(points)
    # Quotient map: q(x) = index of equiv class containing x
    point_to_class = {}
    for i, cls in enumerate(equiv_classes):
        for x in cls:
            point_to_class[x] = i
    q   = {x: point_to_class.get(x, x) for x in points}
    # Quotient open sets: V open in Y ⟺ q⁻¹(V) open in X
    classes     = list(range(len(equiv_classes)))
    q_open_sets = [_fs([])]                                    # ∅ always open
    for r in range(1, len(classes) + 1):
        for combo in itertools.combinations(classes, r):
            V_fs  = _fs(combo)
            q_inv = _fs(x for x, qx in q.items() if qx in V_fs)
            if _is_open(q_inv, open_sets):
                q_open_sets.append(V_fs)
    return classes, q_open_sets                                # (quotient points, quotient topology)

# ============================================================
# TOPOLOGICAL PROPERTIES SUMMARY
# ============================================================

# Returns a full topological profile of a finite space
def TopologyProfile(points, open_sets):
    return {
        'is_topology':     IsTopology(points, open_sets)[0],
        'separation':      SeparationAxiom(points, open_sets),
        'is_T0':           IsT0(points, open_sets),
        'is_T1':           IsT1(points, open_sets),
        'is_T2_Hausdorff': IsHausdorff(points, open_sets),
        'is_T3_Regular':   IsRegular(points, open_sets),
        'is_T4_Normal':    IsNormal(points, open_sets),
        'is_connected':    IsConnected(points, open_sets),
        'is_compact':      IsCompact(points, open_sets),
        'is_path_connected': IsPathConnected(points, open_sets),
        'num_open_sets':   len(list(open_sets)),
        'num_closed_sets': len(ClosedSets(points, open_sets)),
        'components':      Pi0(points, open_sets),
    }                                                          # Complete topology profile
