import math        # sqrt, pi, atan2, etc.
import itertools   # combinations for composite bodies

# Center of Mass module for MathCore.
# Conventions:
#   Masses in kg, positions in m, velocities in m/s.
#   2D points are (x, y) tuples; 3D points are (x, y, z) tuples.
#   Continuous shapes return exact closed-form results.

_TOL = 1e-12  # numerical zero threshold

# ============================================================
# DISCRETE CENTER OF MASS — 1D
# ============================================================

def CoM1D(masses, positions):
    """
    Center of mass of n particles on a line.
    x_cm = Σ(mᵢ xᵢ) / Σmᵢ
    """
    M = sum(masses)
    if abs(M) < _TOL:
        raise ValueError('Total mass is zero — center of mass undefined.')
    return sum(m * x for m, x in zip(masses, positions)) / M   # x_cm

def TotalMass(masses):
    """Sum of all masses in a system."""
    return sum(masses)                                           # M = Σmᵢ

def MassWeightedSum1D(masses, positions):
    """Numerator Σ(mᵢ xᵢ) — useful as an intermediate value."""
    return sum(m * x for m, x in zip(masses, positions))       # Σmᵢxᵢ

def CoMFromReference1D(masses, positions, reference):
    """
    CoM measured from a custom reference point r.
    Equivalent to shifting all positions by −r before computing CoM.
    """
    shifted = [x - reference for x in positions]
    return CoM1D(masses, shifted)                               # x_cm relative to r

def MissingMassPosition1D(known_masses, known_positions, total_mass, cm_target):
    """
    Given a known subset of masses and their positions, the total system mass,
    and the desired CoM position, finds the position of the remaining mass.
    x_unknown = (M · x_cm − Σmᵢxᵢ) / m_unknown
    """
    m_known = sum(known_masses)
    m_unknown = total_mass - m_known
    if abs(m_unknown) < _TOL:
        raise ValueError('No remaining mass to place.')
    numerator = total_mass * cm_target - MassWeightedSum1D(known_masses, known_positions)
    return numerator / m_unknown                                # position of unknown mass

def SplitCoM1D(m1, x1, m2, x2):
    """
    Fast two-body CoM on a line.
    x_cm = (m1·x1 + m2·x2) / (m1 + m2)
    """
    return (m1 * x1 + m2 * x2) / (m1 + m2)                   # direct two-body formula

def CoMDistance1D(masses, positions):
    """
    Returns (x_cm, distances_from_cm) — how far each particle is from the CoM.
    """
    x_cm = CoM1D(masses, positions)
    return x_cm, [x - x_cm for x in positions]                 # displacements from CoM

def BalancePoint1D(masses, positions):
    """
    Returns the fulcrum position where the system is in rotational balance.
    Identical to CoM1D — included for physical intuition.
    """
    return CoM1D(masses, positions)                             # balance point = CoM

# ============================================================
# DISCRETE CENTER OF MASS — 2D
# ============================================================

def CoM2D(masses, points):
    """
    Center of mass of n particles in a plane.
    (x_cm, y_cm) where x_cm = Σmᵢxᵢ/M, y_cm = Σmᵢyᵢ/M
    """
    M = sum(masses)
    if abs(M) < _TOL:
        raise ValueError('Total mass is zero.')
    x_cm = sum(m * p[0] for m, p in zip(masses, points)) / M
    y_cm = sum(m * p[1] for m, p in zip(masses, points)) / M
    return x_cm, y_cm                                          # 2D CoM coordinates

def CoMFromReference2D(masses, points, reference):
    """CoM measured from a custom 2D reference point (rx, ry)."""
    rx, ry = reference
    shifted = [(p[0] - rx, p[1] - ry) for p in points]
    return CoM2D(masses, shifted)                              # CoM relative to reference

def MassWeightedSum2D(masses, points):
    """(Σmᵢxᵢ, Σmᵢyᵢ) — numerators for the CoM formula."""
    sx = sum(m * p[0] for m, p in zip(masses, points))
    sy = sum(m * p[1] for m, p in zip(masses, points))
    return sx, sy                                              # weighted sums

def DistanceFromCoM2D(masses, points):
    """Returns (x_cm, y_cm) and list of Euclidean distances from CoM to each particle."""
    x_cm, y_cm = CoM2D(masses, points)
    dists = [math.sqrt((p[0]-x_cm)**2 + (p[1]-y_cm)**2) for p in points]
    return x_cm, y_cm, dists                                   # CoM + distance list

def CoMOfTriangle2D(v1, v2, v3):
    """
    CoM of a uniform triangle with vertices v1, v2, v3.
    Formula: centroid = ((x1+x2+x3)/3, (y1+y2+y3)/3)
    """
    x_cm = (v1[0] + v2[0] + v3[0]) / 3
    y_cm = (v1[1] + v2[1] + v3[1]) / 3
    return x_cm, y_cm                                          # centroid = CoM for uniform triangle

def CoMOfPolygon2D(vertices):
    """
    CoM of a uniform polygon (equal area density) using the shoelace / centroid formula.
    (x_cm, y_cm) = (1/6A) Σ (xᵢ + xᵢ₊₁)(xᵢyᵢ₊₁ − xᵢ₊₁yᵢ)
    """
    n = len(vertices)
    A = 0.0; cx = 0.0; cy = 0.0
    for i in range(n):
        x0, y0 = vertices[i]
        x1, y1 = vertices[(i + 1) % n]
        cross = x0 * y1 - x1 * y0
        A  += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    A *= 0.5
    if abs(A) < _TOL:
        raise ValueError('Degenerate polygon — zero area.')
    cx /= (6 * A); cy /= (6 * A)
    return cx, cy                                              # polygon centroid

# ============================================================
# DISCRETE CENTER OF MASS — 3D
# ============================================================

def CoM3D(masses, points):
    """
    Center of mass of n particles in 3D space.
    (x_cm, y_cm, z_cm) = Σmᵢ(xᵢ,yᵢ,zᵢ) / M
    """
    M = sum(masses)
    if abs(M) < _TOL:
        raise ValueError('Total mass is zero.')
    x_cm = sum(m * p[0] for m, p in zip(masses, points)) / M
    y_cm = sum(m * p[1] for m, p in zip(masses, points)) / M
    z_cm = sum(m * p[2] for m, p in zip(masses, points)) / M
    return x_cm, y_cm, z_cm                                    # 3D CoM coordinates

def DistanceFromCoM3D(masses, points):
    """Returns (x_cm, y_cm, z_cm) and list of distances from CoM."""
    x_cm, y_cm, z_cm = CoM3D(masses, points)
    dists = [math.sqrt((p[0]-x_cm)**2+(p[1]-y_cm)**2+(p[2]-z_cm)**2) for p in points]
    return x_cm, y_cm, z_cm, dists                             # 3D distances from CoM

def CoMOfTetrahedron3D(v1, v2, v3, v4):
    """
    CoM of a uniform tetrahedron.
    Formula: centroid = (v1+v2+v3+v4) / 4
    """
    x_cm = (v1[0]+v2[0]+v3[0]+v4[0]) / 4
    y_cm = (v1[1]+v2[1]+v3[1]+v4[1]) / 4
    z_cm = (v1[2]+v2[2]+v3[2]+v4[2]) / 4
    return x_cm, y_cm, z_cm                                    # centroid of tetrahedron

# ============================================================
# CONTINUOUS BODIES — CLOSED-FORM RESULTS
# ============================================================

def CoMUniformRod(length, x0=0.0):
    """
    CoM of a uniform rod of length L starting at x0.
    x_cm = x0 + L/2
    """
    return x0 + length / 2                                     # midpoint of rod

def CoMLinearDensityRod(a, b, lambda_fn, n=10000):
    """
    CoM of a rod from x=a to x=b with linear density λ(x).
    x_cm = ∫ x·λ(x) dx / ∫ λ(x) dx   (numerical integration)
    """
    dx = (b - a) / n
    xs = [a + (i + 0.5) * dx for i in range(n)]
    lambdas = [lambda_fn(x) for x in xs]
    num = sum(x * lam for x, lam in zip(xs, lambdas)) * dx
    den = sum(lambdas) * dx
    if abs(den) < _TOL:
        raise ValueError('Total linear mass is zero.')
    return num / den                                           # CoM of variable-density rod

def CoMUniformRectangle(width, height, x0=0.0, y0=0.0):
    """
    CoM of a uniform rectangle with bottom-left corner at (x0, y0).
    (x_cm, y_cm) = (x0 + W/2, y0 + H/2)
    """
    return x0 + width / 2, y0 + height / 2                    # geometric center

def CoMRightTriangle(base, height, x0=0.0, y0=0.0):
    """
    CoM of a uniform right triangle with the right angle at (x0, y0).
    (x_cm, y_cm) = (x0 + b/3, y0 + h/3)
    """
    return x0 + base / 3, y0 + height / 3                     # 1/3 from each right-angle leg

def CoMSemicircle(radius, y0=0.0):
    """
    CoM of a uniform solid semicircle (flat side on the x-axis).
    y_cm = y0 + 4r/(3π)
    """
    return 0.0, y0 + (4 * radius) / (3 * math.pi)            # above the diameter

def CoMSemicircularArc(radius, y0=0.0):
    """
    CoM of a uniform semicircular arc (wire half-ring).
    y_cm = y0 + 2r/π
    """
    return 0.0, y0 + (2 * radius) / math.pi                  # arc CoM (higher than solid)

def CoMSolidHemisphere(radius, z0=0.0):
    """
    CoM of a solid uniform hemisphere.
    z_cm = z0 + 3r/8
    """
    return z0 + (3 * radius) / 8                              # 3r/8 from flat face

def CoMHollowHemisphere(radius, z0=0.0):
    """
    CoM of a hollow hemispherical shell.
    z_cm = z0 + r/2
    """
    return z0 + radius / 2                                    # r/2 from open face

def CoMSolidCone(height, z0=0.0):
    """
    CoM of a solid uniform cone above its base.
    z_cm = z0 + h/4
    """
    return z0 + height / 4                                    # 1/4 height from base

def CoMHollowConicalShell(height, z0=0.0):
    """
    CoM of a hollow conical shell (lateral surface only).
    z_cm = z0 + h/3
    """
    return z0 + height / 3                                    # 1/3 height from base

def CoMSolidCylinder(height, z0=0.0):
    """
    CoM of a solid uniform cylinder.
    z_cm = z0 + h/2
    """
    return z0 + height / 2                                    # midheight

def CoMQuarterCircle(radius):
    """
    CoM of a uniform solid quarter-circle in the first quadrant.
    (x_cm, y_cm) = (4r/3π, 4r/3π)
    """
    d = (4 * radius) / (3 * math.pi)
    return d, d                                               # symmetric about y=x

def CoMSolidSphere():
    """
    CoM of a uniform solid sphere is at its geometric center.
    Returns (0, 0, 0) relative to center.
    """
    return 0.0, 0.0, 0.0                                     # trivially at center

# ============================================================
# COMPOSITE BODY CENTER OF MASS
# ============================================================

def CompositeCoM1D(components):
    """
    CoM of a composite 1D system.
    components: list of (mass, x_cm_of_component)
    Use negative mass to represent a removed / hollow region.
    """
    masses   = [c[0] for c in components]
    positions= [c[1] for c in components]
    return CoM1D(masses, positions)                           # composite 1D CoM

def CompositeCoM2D(components):
    """
    CoM of a composite 2D system.
    components: list of (mass, (x_cm, y_cm))
    Negative mass subtracts a cut-out.
    """
    masses = [c[0] for c in components]
    points = [c[1] for c in components]
    return CoM2D(masses, points)                              # composite 2D CoM

def CompositeCoM3D(components):
    """
    CoM of a composite 3D system.
    components: list of (mass, (x, y, z))
    """
    masses = [c[0] for c in components]
    points = [c[1] for c in components]
    return CoM3D(masses, points)                             # composite 3D CoM

def RemoveCircleFromRectangle(rect_w, rect_h, rect_mass, hole_r, hole_cx, hole_cy):
    """
    CoM of a rectangle with a circular hole.
    Treats the hole as negative mass: m_hole = m_rect · (π r²)/(W·H)
    """
    area_rect = rect_w * rect_h
    area_hole = math.pi * hole_r ** 2
    m_hole    = rect_mass * (area_hole / area_rect)        # proportional mass of hole
    components = [(rect_mass, (rect_w/2, rect_h/2)),
                  (-m_hole,   (hole_cx, hole_cy))]
    return CompositeCoM2D(components)                       # CoM with hole removed

def TwoHalfSystem(m1, x1, m2, x2):
    """
    Convenience: CoM of two sub-bodies (e.g., a dumbbell).
    """
    return CompositeCoM1D([(m1, x1), (m2, x2)])            # dumbbell CoM

# ============================================================
# CENTER OF MASS IN PHYSICS PROBLEMS
# ============================================================

def CoMVelocity1D(masses, velocities):
    """
    Velocity of the center of mass: v_cm = Σ(mᵢvᵢ) / M
    """
    M = sum(masses)
    if abs(M) < _TOL:
        raise ValueError('Total mass is zero.')
    return sum(m * v for m, v in zip(masses, velocities)) / M  # v_cm

def CoMVelocity2D(masses, velocities):
    """
    2D velocity of the center of mass.
    (vx_cm, vy_cm) = Σ(mᵢ vᵢ) / M
    """
    M = sum(masses)
    vx = sum(m * v[0] for m, v in zip(masses, velocities)) / M
    vy = sum(m * v[1] for m, v in zip(masses, velocities)) / M
    return vx, vy                                             # 2D v_cm

def CoMAcceleration(masses, forces):
    """
    Acceleration of CoM: a_cm = F_net / M
    F_net = Σ Fᵢ (net external force on system)
    """
    M = sum(masses)
    F_net = sum(forces)
    return F_net / M                                         # a_cm = F_ext/M

def CoMAfterExplosion1D(total_mass, vcm_before, m1, v1_after):
    """
    After an explosion, CoM velocity is unchanged (no external force).
    Finds v2 of the second fragment.
    M·v_cm = m1·v1 + m2·v2  →  v2 = (M·v_cm − m1·v1) / m2
    """
    m2 = total_mass - m1
    if abs(m2) < _TOL:
        raise ValueError('Second fragment has zero mass.')
    v2 = (total_mass * vcm_before - m1 * v1_after) / m2
    return v2, m2                                           # (v2, mass of second fragment)

def CoMFixedAfterInternalForces(masses, initial_positions, displacements):
    """
    If only internal forces act, the CoM does not move.
    Given that one object displaces by Δx, finds the displacement of others
    to keep CoM fixed.  Returns required displacement for the last particle.
    masses:            list of masses
    initial_positions: initial positions
    displacements:     known Δx for all but last particle (last = None or 0)
    """
    M = sum(masses)
    x_cm = CoM1D(masses, initial_positions)                 # CoM before (fixed)
    # New CoM must equal old CoM: Σmᵢ(xᵢ + Δxᵢ) / M = x_cm
    # → Σmᵢ·Δxᵢ = 0
    known_shift = sum(m * d for m, d in zip(masses[:-1], displacements[:-1]))
    return -known_shift / masses[-1]                        # Δx of last particle

def ExplosionCoMCheck(masses, velocities_after):
    """
    Verifies momentum conservation after an explosion (or any internal-only event).
    Returns (p_before_assumed_zero, p_after, is_conserved).
    If system starts at rest, p_before = 0.
    """
    p_after = sum(m * v for m, v in zip(masses, velocities_after))
    return 0.0, p_after, abs(p_after) < 1e-6               # momentum check

def CoMTrajectory(total_mass, vcm_x, vcm_y, g=9.8):
    """
    After an explosion in the air, the CoM continues its original parabolic path.
    Returns CoM position at time t: (x_cm(t), y_cm(t))
    """
    def position(x0, y0, t):
        x_cm = x0 + vcm_x * t
        y_cm = y0 + vcm_y * t - 0.5 * g * t**2
        return x_cm, y_cm
    return position                                        # callable (x0,y0,t)→(x,y)

# ============================================================
# CENTER OF MASS FRAME (CoM Frame / Zero-Momentum Frame)
# ============================================================

def CoMFrameVelocities1D(masses, velocities):
    """
    Velocities in the center of mass frame.
    v'ᵢ = vᵢ − v_cm
    In the CoM frame, total momentum = 0.
    """
    v_cm = CoMVelocity1D(masses, velocities)
    v_prime = [v - v_cm for v in velocities]
    return v_cm, v_prime                                   # (v_cm, list of CoM-frame velocities)

def CoMFrameVelocities2D(masses, velocities):
    """2D velocities in the CoM frame."""
    vx_cm, vy_cm = CoMVelocity2D(masses, velocities)
    v_prime = [(v[0]-vx_cm, v[1]-vy_cm) for v in velocities]
    return (vx_cm, vy_cm), v_prime                        # CoM velocity + frame velocities

def KineticEnergyCoMFrame1D(masses, velocities):
    """
    KE in the CoM frame = KE_total − ½M v_cm²
    This is the kinetic energy available for inelastic processes.
    """
    M      = sum(masses)
    v_cm   = CoMVelocity1D(masses, velocities)
    ke_lab = sum(0.5 * m * v**2 for m, v in zip(masses, velocities))
    ke_cm  = ke_lab - 0.5 * M * v_cm**2
    return ke_cm, ke_lab, v_cm                            # (KE_cm, KE_lab, v_cm)

def RelativeVelocity1D(v1, v2):
    """Relative velocity of particle 1 w.r.t. particle 2: v_rel = v1 − v2"""
    return v1 - v2                                        # v_rel

def ReducedMass(m1, m2):
    """Reduced mass μ = m1·m2 / (m1 + m2) — governs relative motion."""
    return (m1 * m2) / (m1 + m2)                        # μ

def RelativeKE1D(m1, v1, m2, v2):
    """
    KE of relative motion in CoM frame.
    KE_rel = ½μ v_rel²
    """
    mu    = ReducedMass(m1, m2)
    v_rel = RelativeVelocity1D(v1, v2)
    return 0.5 * mu * v_rel**2                          # ½μ v_rel²

# ============================================================
# PARALLEL AXIS THEOREM & MOMENT OF INERTIA
# ============================================================

def ParallelAxisTheorem(I_cm, mass, distance):
    """
    Parallel axis theorem: I = I_cm + m·d²
    Shifts the moment of inertia from the CoM axis to a parallel axis at distance d.
    """
    return I_cm + mass * distance**2                    # I_cm + md²

def PerpendiculaAxisTheorem(I_x, I_y):
    """
    Perpendicular axis theorem (flat lamina):
    I_z = I_x + I_y
    Valid for a flat object in the x-y plane.
    """
    return I_x + I_y                                   # I_z = I_x + I_y

def MomentOfInertiaPointMasses(masses, distances_from_axis):
    """
    Moment of inertia of a set of point masses about an axis.
    I = Σ mᵢ rᵢ²
    """
    return sum(m * r**2 for m, r in zip(masses, distances_from_axis))  # I = Σmr²

def I_SolidSphere(mass, radius):
    """I_cm = 2/5 m r²"""
    return (2/5) * mass * radius**2

def I_HollowSphere(mass, radius):
    """I_cm = 2/3 m r²"""
    return (2/3) * mass * radius**2

def I_SolidCylinder(mass, radius):
    """I_cm = 1/2 m r² (about symmetry axis)"""
    return (1/2) * mass * radius**2

def I_HollowCylinder(mass, radius):
    """I_cm = m r² (thin-walled hollow cylinder about axis)"""
    return mass * radius**2

def I_ThinRod_Center(mass, length):
    """I_cm = 1/12 m L² (about center)"""
    return (1/12) * mass * length**2

def I_ThinRod_End(mass, length):
    """I = 1/3 m L² (about one end)"""
    return (1/3) * mass * length**2

def I_RectangularPlate(mass, width, height):
    """I_cm = m(w²+h²)/12 (about center, perpendicular to plate)"""
    return mass * (width**2 + height**2) / 12

def AxisShiftCombined(components):
    """
    Total moment of inertia of a composite body about a common axis.
    components: list of (I_cm, mass, distance_from_new_axis)
    I_total = Σ (I_cm_i + m_i d_i²)
    """
    return sum(ParallelAxisTheorem(I, m, d) for I, m, d in components)  # composite I

# ============================================================
# WORD PROBLEM HELPERS  (used by the DebugUI parser)
# ============================================================

def ParseCoMProblem1D(text):
    """
    Lightweight natural-language parser for 1D CoM word problems.
    Extracts (masses, positions) from common phrasings and returns
    a result dict, or None if the text cannot be parsed.

    Recognises patterns like:
        "2 kg at 1 m and 3 kg at 4 m"
        "mass 3 kg at position 2 m"
        "m=5 x=4, m=2 x=7"
        "particle of mass 5 at position 0 m"
    """
    import re
    pairs = []

    # Pattern A: "N kg at [position] X"
    pA = re.findall(
        r'(\d+\.?\d*)\s*kg\s*at\s*(?:position\s+|x\s*=\s*|pos\s*=?\s*)?(-?\d+\.?\d*)',
        text, re.IGNORECASE)
    if pA:
        pairs = [(float(m), float(x)) for m, x in pA]

    # Pattern B: "mass N [kg] at [position] X"
    if not pairs:
        pB = re.findall(
            r'mass\s+(\d+\.?\d*)\s*k?g?\s*at\s*(?:position\s+|x\s*=\s*)?(-?\d+\.?\d*)',
            text, re.IGNORECASE)
        if pB:
            pairs = [(float(m), float(x)) for m, x in pB]

    # Pattern C: m=N x=X notation
    if not pairs:
        pC = re.findall(r'm\s*=\s*(\d+\.?\d*)\s*[,;]?\s*x\s*=\s*(-?\d+\.?\d*)', text, re.IGNORECASE)
        if pC:
            pairs = [(float(m), float(x)) for m, x in pC]

    # Pattern D: collect all masses and positions in order (fallback)
    if not pairs:
        ms = re.findall(r'(?:mass|m)\s*[=:]?\s*(\d+\.?\d*)\s*k?g?', text, re.IGNORECASE)
        xs = re.findall(r'(?:position|pos|x)\s*[=:]?\s*(-?\d+\.?\d*)\s*m?', text, re.IGNORECASE)
        if ms and xs and len(ms) == len(xs):
            pairs = [(float(m), float(x)) for m, x in zip(ms, xs)]

    if not pairs:
        return None

    masses    = [p[0] for p in pairs]
    positions = [p[1] for p in pairs]
    x_cm      = CoM1D(masses, positions)

    return {
        'masses':       masses,
        'positions':    positions,
        'M_total':      sum(masses),
        'x_cm':         x_cm,
        'weighted_sum': MassWeightedSum1D(masses, positions),
    }

def ParseCoMProblem2D(text):
    """
    Parser for 2D CoM word problems.
    Expects patterns like: "mass 3 at (2, 5)", "m=2 (x,y)=(1,3)"
    """
    import re
    pairs = []
    # Pattern: mass value at (x, y)
    pat = re.findall(
        r'(?:mass\s*=?\s*)?(\d+\.?\d*)\s*(?:kg)?\s*(?:at|@|placed at|located at)?\s*\(?\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*\)?',
        text, re.IGNORECASE)
    if pat:
        pairs = [(float(m), (float(x), float(y))) for m, x, y in pat]

    if not pairs:
        return None

    masses = [p[0] for p in pairs]
    points = [p[1] for p in pairs]
    x_cm, y_cm = CoM2D(masses, points)

    return {
        'masses':  masses,
        'points':  points,
        'M_total': sum(masses),
        'x_cm':    x_cm,
        'y_cm':    y_cm,
    }

def StepByStepCoM1D(masses, positions):
    """
    Returns a list of step strings for a detailed worked solution.
    Each step is a (label, expression, result) tuple.
    """
    M     = sum(masses)
    num   = MassWeightedSum1D(masses, positions)
    x_cm  = num / M
    steps = []
    steps.append(('Formula',        'x_cm = Σ(mᵢ·xᵢ) / Σmᵢ',    ''))
    steps.append(('Total mass',     f'M = {" + ".join(str(m) for m in masses)} = {M}', f'{M} kg'))
    for i, (m, x) in enumerate(zip(masses, positions), 1):
        steps.append((f'  m{i}·x{i}', f'{m} × {x}', f'{m*x}'))
    steps.append(('Weighted sum',   f'Σ(mᵢxᵢ) = {" + ".join(f"{m}×{x}" for m,x in zip(masses,positions))}', f'{num}'))
    steps.append(('Result',         f'x_cm = {num} / {M}', f'{x_cm:.6f} m'))
    return steps                                              # list of step tuples

def StepByStepCoM2D(masses, points):
    """Step-by-step solution for 2D CoM — returns list of step tuples."""
    M = sum(masses)
    sx, sy = MassWeightedSum2D(masses, points)
    x_cm, y_cm = sx/M, sy/M
    steps = []
    steps.append(('Formula', 'x_cm = Σ(mᵢxᵢ)/M,  y_cm = Σ(mᵢyᵢ)/M', ''))
    steps.append(('Total mass', f'M = {M}', f'{M} kg'))
    steps.append(('Σmᵢxᵢ', f'{" + ".join(f"{m}×{p[0]}" for m,p in zip(masses,points))} = {sx}', f'{sx}'))
    steps.append(('Σmᵢyᵢ', f'{" + ".join(f"{m}×{p[1]}" for m,p in zip(masses,points))} = {sy}', f'{sy}'))
    steps.append(('x_cm', f'{sx} / {M}', f'{x_cm:.6f} m'))
    steps.append(('y_cm', f'{sy} / {M}', f'{y_cm:.6f} m'))
    return steps
