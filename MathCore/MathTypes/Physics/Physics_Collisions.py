import math  # sqrt, fabs

# All units: mass (kg), velocity (m/s), momentum (kg·m/s),
# force (N), time (s), energy (J), position (m).
# Sign convention: rightward = positive velocity.

# ============================================================
# INTERNAL HELPERS
# ============================================================

def _ke(mass, velocity):
    return 0.5 * mass * velocity ** 2

def _pe(mass, height, g=9.8):
    return mass * g * height

def _momentum(mass, velocity):
    return mass * velocity

# ============================================================
# COLLISION CLASSIFICATION
# ============================================================

# Returns collision type based on KE conservation ratio
def ClassifyCollision(m1, v1i, m2, v2i, v1f, v2f, tol=0.01):
    ke_before = _ke(m1, v1i) + _ke(m2, v2i)
    ke_after  = _ke(m1, v1f) + _ke(m2, v2f)
    ke_ratio  = ke_after / ke_before if ke_before > 0 else 1.0
    # Check if objects stick together
    if abs(v1f - v2f) < tol:
        return 'perfectly_inelastic'
    if abs(ke_ratio - 1.0) < tol:
        return 'elastic'
    if ke_after < ke_before:
        return 'inelastic'
    return 'super_elastic'                                     # Spring-assisted collision

# Returns True if momentum is conserved (within tolerance)
def MomentumConserved(m1, v1i, m2, v2i, v1f, v2f, tol=1e-6):
    p_before = m1*v1i + m2*v2i
    p_after  = m1*v1f + m2*v2f
    return abs(p_before - p_after) < tol                      # True iff conserved

# Returns True if kinetic energy is conserved (elastic collision)
def KineticEnergyConserved(m1, v1i, m2, v2i, v1f, v2f, tol=1e-6):
    ke_before = _ke(m1,v1i) + _ke(m2,v2i)
    ke_after  = _ke(m1,v1f) + _ke(m2,v2f)
    return abs(ke_before - ke_after) < tol                    # True iff elastic

# ============================================================
# BEFORE COLLISION STATE
# ============================================================

def BeforeCollisionState(m1, v1i, m2, v2i, h1=0, h2=0, x1=0, x2=0, g=9.8):
    """
    Complete state of both objects before collision.
    Returns full dict: position, velocity, momentum, KE, PE, ME for each object.
    """
    p1   = _momentum(m1, v1i);  p2   = _momentum(m2, v2i)
    ke1  = _ke(m1, v1i);        ke2  = _ke(m2, v2i)
    pe1  = _pe(m1, h1, g);      pe2  = _pe(m2, h2, g)
    me1  = ke1 + pe1;           me2  = ke2 + pe2
    return {
        'obj1': {'mass':m1, 'position':x1, 'height':h1, 'velocity':v1i,
                 'momentum':p1, 'KE':ke1, 'PE':pe1, 'ME':me1},
        'obj2': {'mass':m2, 'position':x2, 'height':h2, 'velocity':v2i,
                 'momentum':p2, 'KE':ke2, 'PE':pe2, 'ME':me2},
        'system': {
            'total_mass':    m1+m2,
            'total_momentum': p1+p2,
            'total_KE':      ke1+ke2,
            'total_PE':      pe1+pe2,
            'total_ME':      me1+me2,
            'relative_velocity': v1i - v2i,
        },
    }                                                          # Complete before state

# ============================================================
# DURING COLLISION STATE
# ============================================================

def DuringCollisionState(m1, v1i, m2, v2i, delta_t, h1=0, h2=0, x1=0, x2=0, g=9.8):
    """
    Estimated state mid-collision.
    At maximum compression (perfectly inelastic moment):
    both objects move at center-of-mass velocity v_cm.
    Force is estimated from impulse over collision time.
    """
    p_total = m1*v1i + m2*v2i
    total_m = m1 + m2
    v_cm    = p_total / total_m if total_m > 0 else 0.0       # Common velocity at max compression

    # Average force (impulse approximation for each object)
    f1 = m1 * (v_cm - v1i) / delta_t if delta_t > 0 else 0.0  # Force on obj1
    f2 = m2 * (v_cm - v2i) / delta_t if delta_t > 0 else 0.0  # Force on obj2 (= −f1)

    ke_cm  = _ke(total_m, v_cm)                                # KE at max compression
    pe1    = _pe(m1, h1, g);  pe2 = _pe(m2, h2, g)
    return {
        'v_cm':          v_cm,
        'obj1_velocity': v_cm,
        'obj2_velocity': v_cm,
        'obj1_force':    f1,
        'obj2_force':    f2,                                   # Newton's 3rd: f2 = −f1
        'total_momentum': p_total,
        'KE_at_max_compression': ke_cm,
        'PE_stored_in_deformation': ((_ke(m1,v1i)+_ke(m2,v2i)) - ke_cm),
        'collision_time': delta_t,
    }                                                          # Complete during state

# ============================================================
# AFTER COLLISION — ELASTIC
# ============================================================

# Formula: elastic collision final velocities (1D)
# v1f = (m1−m2)v1i + 2m2·v2i) / (m1+m2)
# v2f = (m2−m1)v2i + 2m1·v1i) / (m1+m2)
def ElasticFinalVelocities(m1, v1i, m2, v2i):
    total = m1 + m2
    if total <= 0:
        return 0.0, 0.0
    v1f = ((m1-m2)*v1i + 2.0*m2*v2i) / total
    v2f = ((m2-m1)*v2i + 2.0*m1*v1i) / total
    return v1f, v2f                                            # Complete elastic final v

def AfterCollisionElastic(m1, v1i, m2, v2i, h1=0, h2=0, g=9.8):
    """Full after-state for an elastic collision."""
    v1f, v2f = ElasticFinalVelocities(m1, v1i, m2, v2i)
    p1  = _momentum(m1, v1f); p2  = _momentum(m2, v2f)
    ke1 = _ke(m1, v1f);       ke2 = _ke(m2, v2f)
    pe1 = _pe(m1, h1, g);     pe2 = _pe(m2, h2, g)
    return {
        'type': 'elastic',
        'obj1': {'velocity':v1f, 'momentum':p1, 'KE':ke1, 'PE':pe1, 'ME':ke1+pe1},
        'obj2': {'velocity':v2f, 'momentum':p2, 'KE':ke2, 'PE':pe2, 'ME':ke2+pe2},
        'system': {
            'total_momentum': p1+p2,
            'total_KE':       ke1+ke2,
            'KE_conserved':   True,
            'momentum_conserved': True,
            'relative_velocity_after': v1f-v2f,               # = −(v1i−v2i) for elastic
        },
    }                                                          # Complete elastic after state

# ============================================================
# AFTER COLLISION — PERFECTLY INELASTIC
# ============================================================

# Formula: v_f = (m1·v1i + m2·v2i) / (m1+m2)  — objects stick together
# From lecture: 500kg@10m/s + 500kg@0 → v_f = 5m/s
def PerfectlyInelasticFinalVelocity(m1, v1i, m2, v2i=0):
    total = m1 + m2
    if total <= 0:
        return 0.0
    return (m1*v1i + m2*v2i) / total                          # v_f = p_total/(m1+m2)

def AfterCollisionPerfectlyInelastic(m1, v1i, m2, v2i=0, h=0, g=9.8):
    """Full after-state for a perfectly inelastic collision (objects lock together)."""
    v_f   = PerfectlyInelasticFinalVelocity(m1, v1i, m2, v2i)
    m_tot = m1 + m2
    p_f   = _momentum(m_tot, v_f)
    ke_f  = _ke(m_tot, v_f)
    pe_f  = _pe(m_tot, h, g)
    ke_i  = _ke(m1, v1i) + _ke(m2, v2i)
    ke_lost = ke_i - ke_f
    return {
        'type': 'perfectly_inelastic',
        'combined': {
            'mass': m_tot, 'velocity': v_f,
            'momentum': p_f, 'KE': ke_f, 'PE': pe_f, 'ME': ke_f+pe_f,
        },
        'system': {
            'total_momentum':  p_f,
            'total_KE_after':  ke_f,
            'KE_lost':         ke_lost,                        # Energy → deformation/heat
            'KE_conserved':    False,
            'momentum_conserved': True,
        },
    }                                                          # Complete perfectly inelastic after

# ============================================================
# AFTER COLLISION — PARTIALLY INELASTIC
# ============================================================

# Partially inelastic: momentum conserved, some KE lost (not elastic, not perfectly inelastic)
# Requires knowing one final velocity to solve for the other.
def AfterCollisionInelastic(m1, v1i, m2, v2i, v1f, h1=0, h2=0, g=9.8):
    """
    Partially inelastic collision. Given v1f, solve for v2f via momentum conservation.
    p_before = p_after → v2f = (m1·v1i + m2·v2i − m1·v1f) / m2
    """
    p_total = m1*v1i + m2*v2i
    v2f     = (p_total - m1*v1f) / m2 if m2 > 0 else 0.0
    p1      = _momentum(m1,v1f); p2 = _momentum(m2,v2f)
    ke1     = _ke(m1,v1f);       ke2 = _ke(m2,v2f)
    pe1     = _pe(m1,h1,g);      pe2 = _pe(m2,h2,g)
    ke_i    = _ke(m1,v1i) + _ke(m2,v2i)
    ke_f    = ke1 + ke2
    return {
        'type': 'inelastic',
        'obj1': {'velocity':v1f, 'momentum':p1, 'KE':ke1, 'PE':pe1, 'ME':ke1+pe1},
        'obj2': {'velocity':v2f, 'momentum':p2, 'KE':ke2, 'PE':pe2, 'ME':ke2+pe2},
        'system': {
            'total_momentum':     p1+p2,
            'total_KE_before':    ke_i,
            'total_KE_after':     ke_f,
            'KE_lost':            ke_i - ke_f,
            'momentum_conserved': True,
            'KE_conserved':       False,
        },
    }                                                          # Complete inelastic after state

# ============================================================
# FULL COLLISION ANALYSIS — ALL THREE PHASES
# ============================================================

def FullElasticCollisionAnalysis(m1, v1i, m2, v2i, delta_t=0.01,
                                  h1=0, h2=0, x1=0, x2=0, g=9.8):
    """
    Complete elastic collision: before, during, and after states.
    Example from lecture (image 1): bouncing objects — energy conserved.
    """
    before = BeforeCollisionState(m1, v1i, m2, v2i, h1, h2, x1, x2, g)
    during = DuringCollisionState(m1, v1i, m2, v2i, delta_t, h1, h2, x1, x2, g)
    after  = AfterCollisionElastic(m1, v1i, m2, v2i, h1, h2, g)
    return {'before': before, 'during': during, 'after': after,
            'type': 'elastic',
            'KE_change': after['system']['total_KE'] - before['system']['total_KE'],
            'momentum_change': after['system']['total_momentum'] - before['system']['total_momentum']}

def FullInelasticCollisionAnalysis(m1, v1i, m2, v2i, delta_t=0.01,
                                    h1=0, h2=0, x1=0, x2=0, g=9.8):
    """
    Complete perfectly inelastic collision: before, during, after.
    Example from lecture (image 2): 500kg + 500kg lock together.
    """
    before = BeforeCollisionState(m1, v1i, m2, v2i, h1, h2, x1, x2, g)
    during = DuringCollisionState(m1, v1i, m2, v2i, delta_t, h1, h2, x1, x2, g)
    after  = AfterCollisionPerfectlyInelastic(m1, v1i, m2, v2i, max(h1,h2), g)
    return {'before': before, 'during': during, 'after': after,
            'type': 'perfectly_inelastic',
            'KE_lost': after['system']['KE_lost'],
            'momentum_conserved': True}

# ============================================================
# ELASTIC COLLISION — SPECIAL CASES
# ============================================================

# Equal masses: objects exchange velocities
def ElasticEqualMass(v1i, v2i):
    return v2i, v1i                                            # v1f=v2i, v2f=v1i

# Heavy object hits light stationary: heavy barely slows
def ElasticHeavyHitsLight(m1, v1i, m2):
    total = m1 + m2
    v1f = (m1-m2)*v1i / total
    v2f = 2.0*m1*v1i / total
    return v1f, v2f                                            # v2f ≈ 2v1i when m1>>m2

# Light object hits heavy stationary: light bounces back ~same speed
def ElasticLightHitsHeavy(m1, v1i, m2):
    return ElasticFinalVelocities(m1, v1i, m2, 0.0)           # v1f ≈ −v1i when m2>>m1

# Coefficient of restitution: e = |v_rel_after| / |v_rel_before|
# e = 1 → elastic, e = 0 → perfectly inelastic
def CoefficientOfRestitution(v1i, v2i, v1f, v2f):
    v_rel_before = v1i - v2i
    v_rel_after  = v1f - v2f
    if abs(v_rel_before) < 1e-14:
        return 0.0
    return abs(v_rel_after) / abs(v_rel_before)                # e = |Δv_after|/|Δv_before|

# Final velocities using coefficient of restitution + momentum conservation
def CollisionWithRestitution(m1, v1i, m2, v2i, e):
    # e·(v1i−v2i) = v2f−v1f  (restitution)
    # m1v1i+m2v2i = m1v1f+m2v2f  (momentum)
    p_total = m1*v1i + m2*v2i
    # v2f = (p_total + m1·e·(v1i−v2i)) / (m1+m2)
    total = m1 + m2
    if total <= 0:
        return 0.0, 0.0
    v2f = (p_total + m1*e*(v1i-v2i)) / total
    v1f = v2f - e*(v1i-v2i)
    return v1f, v2f                                            # Final velocities via e

# ============================================================
# 2D ELASTIC COLLISION
# ============================================================

# Two-body 2D elastic collision. Object 2 initially at rest.
# Returns (v1f, theta1, v2f, theta2) — final speeds and angles.
def Elastic2DCollision(m1, v1i, m2, theta1_deg):
    """
    2D elastic collision with m2 initially at rest.
    theta1 = scattering angle of m1 relative to original direction.
    Uses conservation of KE and momentum in x and y.
    """
    theta1 = math.radians(theta1_deg)
    # From elastic 2D formulas with m2 at rest:
    # v1f = v1i·cos(θ1)·(m1-m2)/(m1+m2) + correction (simplified: use energy methods)
    # For equal masses: v1f=0 at 90° scatter
    total = m1 + m2
    v1f   = v1i * math.cos(theta1) * (m1-m2) / total + 0      # Simplified 1D projection
    v2fx  = (2.0*m1*v1i) / total - v1f * math.cos(theta1)
    v2fy  = -v1f * math.sin(theta1)
    v2f   = math.sqrt(v2fx**2 + v2fy**2)
    theta2 = math.degrees(math.atan2(v2fy, v2fx)) if v2f > 0 else 0.0
    return v1f, theta1_deg, v2f, theta2                        # Final speeds and angles

# 2D component-wise collision: given all final velocities in x and y
def Collision2DState(m1, v1xi, v1yi, m2, v2xi, v2yi,
                     v1xf, v1yf, v2xf, v2yf, h1=0, h2=0, g=9.8):
    """Returns full 2D before/after momentum and energy analysis."""
    # Before
    p1xi=m1*v1xi; p1yi=m1*v1yi; p2xi=m2*v2xi; p2yi=m2*v2yi
    ke_i = _ke(m1, math.sqrt(v1xi**2+v1yi**2)) + _ke(m2, math.sqrt(v2xi**2+v2yi**2))
    # After
    p1xf=m1*v1xf; p1yf=m1*v1yf; p2xf=m2*v2xf; p2yf=m2*v2yf
    ke_f = _ke(m1, math.sqrt(v1xf**2+v1yf**2)) + _ke(m2, math.sqrt(v2xf**2+v2yf**2))
    return {
        'before': {'px_total': p1xi+p2xi, 'py_total': p1yi+p2yi, 'KE': ke_i},
        'after':  {'px_total': p1xf+p2xf, 'py_total': p1yf+p2yf, 'KE': ke_f},
        'px_conserved': abs((p1xi+p2xi)-(p1xf+p2xf)) < 1e-6,
        'py_conserved': abs((p1yi+p2yi)-(p1yf+p2yf)) < 1e-6,
        'KE_change':    ke_f - ke_i,
    }                                                          # Complete 2D collision state

# ============================================================
# ENERGY ANALYSIS DURING COLLISION PHASES
# ============================================================

# Energy budget: where does the lost KE go?
def CollisionEnergyBudget(m1, v1i, m2, v2i, v1f, v2f):
    ke_before    = _ke(m1,v1i) + _ke(m2,v2i)
    ke_after     = _ke(m1,v1f) + _ke(m2,v2f)
    ke_lost      = ke_before - ke_after
    p_before     = m1*v1i + m2*v2i
    p_after      = m1*v1f + m2*v2f
    return {
        'KE_before':    ke_before,
        'KE_after':     ke_after,
        'KE_lost':      ke_lost,
        'KE_lost_%':    100.0*ke_lost/ke_before if ke_before > 0 else 0.0,
        'p_before':     p_before,
        'p_after':      p_after,
        'p_conserved':  abs(p_before-p_after) < 1e-6,
        'collision_type': ClassifyCollision(m1,v1i,m2,v2i,v1f,v2f),
        'e':            CoefficientOfRestitution(v1i,v2i,v1f,v2f),
    }                                                          # Complete energy budget

# Full state snapshot at any moment given mass, velocity, height, position
def ObjectState(mass, velocity, height=0, position=0, g=9.8):
    """Universal state snapshot for any object at any phase."""
    return {
        'mass':     mass,
        'position': position,
        'height':   height,
        'velocity': velocity,
        'momentum': _momentum(mass, velocity),
        'KE':       _ke(mass, velocity),
        'PE':       _pe(mass, height, g),
        'ME':       _ke(mass, velocity) + _pe(mass, height, g),
        'speed':    abs(velocity),
        'direction': 'right' if velocity > 0 else ('left' if velocity < 0 else 'stationary'),
    }                                                          # Complete object state

# Acceleration during collision from force and mass
def CollisionAcceleration(force, mass):
    if mass <= 0:
        return 0.0
    return force / mass                                        # a = F/m during collision
