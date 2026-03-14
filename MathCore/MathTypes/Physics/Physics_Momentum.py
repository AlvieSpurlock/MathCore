import math  # sqrt, fabs

# All units: mass (kg), velocity (m/s), momentum (kg·m/s),
# force (N), time (s), distance (m), g = 9.8 m/s².

# ============================================================
# MOMENTUM
# ============================================================

# Formula: p = m·v  — linear momentum (vector; positive = +x direction)
def Momentum(mass, velocity):
    return mass * velocity                                     # Complete p = mv

# Formula: v = p / m
def VelocityFromMomentum(momentum, mass):
    if mass <= 0:                                              # Guard against invalid mass
        return 0.0
    return momentum / mass                                     # v = p/m

# Formula: m = p / v
def MassFromMomentum(momentum, velocity):
    if velocity == 0:
        return 0.0
    return momentum / velocity                                 # m = p/v

# Returns the momenta of all objects in a system as a list
def SystemMomenta(masses, velocities):
    return [m * v for m, v in zip(masses, velocities)]        # [p1, p2, ..., pn]

# Formula: p_total = Σ mᵢ·vᵢ  — total momentum of a system
def TotalMomentum(masses, velocities):
    return sum(m * v for m, v in zip(masses, velocities))     # Complete p_total

# Change in momentum: Δp = m·(v_f − v_i)
def DeltaMomentum(mass, v_initial, v_final):
    return mass * (v_final - v_initial)                       # Δp = mΔv

# ============================================================
# IMPULSE
# ============================================================

# Formula: J = F·Δt  — impulse from constant force over time interval
def Impulse(force, delta_t):
    return force * delta_t                                     # Complete J = FΔt

# Formula: J = Δp = m·(v_f − v_i)  — impulse-momentum theorem
def ImpulseFromMomentumChange(mass, v_initial, v_final):
    return DeltaMomentum(mass, v_initial, v_final)             # J = Δp

# Formula: F_avg = J / Δt  — average force from impulse
def AverageForceFromImpulse(impulse, delta_t):
    if delta_t <= 0:                                           # Guard against zero time
        return 0.0
    return impulse / delta_t                                   # F_avg = J/Δt

# Formula: F_avg = m·Δv / Δt  — average force directly from velocity change
def AverageForce(mass, v_initial, v_final, delta_t):
    if delta_t <= 0:
        return 0.0
    return mass * (v_final - v_initial) / delta_t             # F_avg = mΔv/Δt

# Formula: Δt = J / F  — duration of impact from impulse and average force
def ImpactTime(impulse, avg_force):
    if avg_force == 0:
        return 0.0
    return impulse / avg_force                                 # Δt = J/F

# Impulse is a vector — returns (impulse_x, impulse_y) for 2D force at angle
def Impulse2D(force, delta_t, angle_deg):
    theta = math.radians(angle_deg)
    jx    = force * math.cos(theta) * delta_t
    jy    = force * math.sin(theta) * delta_t
    return jx, jy                                             # (Jx, Jy)

# ============================================================
# CONSERVATION OF MOMENTUM
# ============================================================

# Formula: p_total_before = p_total_after  (no external forces)
# Returns True if total momentum is conserved between two states
def IsConserved(p_before_list, p_after_list, tol=1e-6):
    return abs(sum(p_before_list) - sum(p_after_list)) < tol  # Check conservation

# One-dimensional: two objects, find v2_final given all else
# m1·v1i + m2·v2i = m1·v1f + m2·v2f
def FindFinalVelocity_2Body(m1, v1i, m2, v2i, v1f):
    """
    Conservation of momentum for two bodies.
    Solves for v2f given v1f.
    """
    numerator = m1 * v1i + m2 * v2i - m1 * v1f
    if m2 <= 0:
        return 0.0
    return numerator / m2                                      # v2f = (p_total − m1v1f)/m2

# Simple inelastic (lock together): (m1+m2)·v_f = m1·v1i + m2·v2i
# From lecture: 500kg@10m/s + 500kg@0 → v_f = 5 m/s
def InelasticFinalVelocity(m1, v1i, m2, v2i=0):
    total_mass     = m1 + m2
    total_momentum = m1 * v1i + m2 * v2i
    if total_mass <= 0:
        return 0.0
    return total_momentum / total_mass                         # v_f = p_total/(m1+m2)

# Three-body conservation: find v3f given v1f and v2f
def ThreeBodyConservation(m1, v1i, m2, v2i, m3, v3i, m1_=None, v1f=None, m2_=None, v2f=None):
    p_before = m1*v1i + m2*v2i + m3*v3i
    p_known_after = (m1_ or m1) * (v1f or v1i) + (m2_ or m2) * (v2f or v2i)
    p3_after = p_before - p_known_after
    return p3_after / m3 if m3 > 0 else 0.0                   # v3f = (p_total − p1f − p2f)/m3

# ============================================================
# CENTER OF MASS
# ============================================================

# Formula: x_cm = Σ(mᵢ·xᵢ) / Σmᵢ  — 1D center of mass
def CenterOfMass1D(masses, positions):
    total_mass = sum(masses)
    if total_mass <= 0:
        return 0.0
    return sum(m * x for m, x in zip(masses, positions)) / total_mass  # x_cm

# Formula: x_cm, y_cm  — 2D center of mass
def CenterOfMass2D(masses, x_positions, y_positions):
    total_mass = sum(masses)
    if total_mass <= 0:
        return 0.0, 0.0
    x_cm = sum(m*x for m,x in zip(masses, x_positions)) / total_mass
    y_cm = sum(m*y for m,y in zip(masses, y_positions)) / total_mass
    return x_cm, y_cm                                         # (x_cm, y_cm)

# Formula: v_cm = Σ(mᵢ·vᵢ) / Σmᵢ  — velocity of center of mass
def CenterOfMassVelocity(masses, velocities):
    total_mass = sum(masses)
    if total_mass <= 0:
        return 0.0
    return sum(m*v for m,v in zip(masses, velocities)) / total_mass  # v_cm

# Formula: a_cm = F_net_external / M_total  — acceleration of CM
def CenterOfMassAcceleration(net_external_force, total_mass):
    if total_mass <= 0:
        return 0.0
    return net_external_force / total_mass                     # a_cm = F_ext / M

# Displacement of CM in time t: x_cm(t) = x_cm(0) + v_cm·t
def CenterOfMassPosition(x_cm_initial, v_cm, t):
    return x_cm_initial + v_cm * t                            # x_cm(t) = x_cm0 + v_cm·t

# Reduced mass for two-body problem: μ = m1·m2 / (m1+m2)
def ReducedMass(m1, m2):
    if m1 + m2 <= 0:
        return 0.0
    return m1 * m2 / (m1 + m2)                               # μ = m1m2/(m1+m2)

# ============================================================
# NEWTON'S SECOND LAW — MOMENTUM FORM
# ============================================================

# Formula: F_net = dp/dt  — Newton's second law in momentum form
# For constant mass: F_net = m·a = m·dv/dt
def NewtonSecondLaw_Momentum(delta_p, delta_t):
    if delta_t <= 0:
        return 0.0
    return delta_p / delta_t                                   # F = Δp/Δt

# Formula: F·Δt = Δp  → rearranged impulse-momentum theorem
# Useful when force is known and we want Δp
def MomentumChangeFromForce(force, delta_t):
    return force * delta_t                                     # Δp = F·Δt

# Newton's 3rd Law applied to collisions: F_12 = −F_21
# Forces are equal in magnitude, opposite in direction, same duration
def NewtonThirdCollisionForces(impulse_on_1):
    return impulse_on_1, -impulse_on_1                        # (J_on_1, J_on_2) — equal & opposite

# ============================================================
# SPRING STRETCH AND MOMENTUM
# ============================================================

# Static spring with hanging mass — stretch at equilibrium
def SpringEquilibriumStretch(mass, k, g=9.8):
    if k <= 0:
        return 0.0
    return mass * g / k                                        # x_eq = mg/k

# Momentum of a mass on a spring at a given phase of SHM
# x(t) = A·cos(ωt), v(t) = −A·ω·sin(ωt), p(t) = m·v(t)
def SpringMomentumAtTime(mass, amplitude, k, t, phase=0.0):
    omega = math.sqrt(k / mass) if mass > 0 and k > 0 else 0.0
    v     = -amplitude * omega * math.sin(omega * t + phase)
    return mass * v                                            # p(t) = mv(t)

# Max momentum of mass on spring: p_max = m·A·ω
def SpringMaxMomentum(mass, amplitude, k):
    omega = math.sqrt(k / mass) if mass > 0 and k > 0 else 0.0
    return mass * amplitude * omega                            # p_max = mAω

# ============================================================
# BEFORE AND AFTER CUT — MOMENTUM ANALYSIS
# ============================================================

# System: two masses m1 and m2 joined by a compressed spring.
# Moving together at v_system before cut.
# After cut: spring releases and they separate.

def BeforeCutState(m1, m2, v_system):
    """
    State of the two-block spring system before the spring is cut.
    Both masses move at v_system together.
    """
    p1      = m1 * v_system
    p2      = m2 * v_system
    p_total = p1 + p2
    ke      = 0.5 * (m1 + m2) * v_system ** 2
    return {
        'm1': m1, 'm2': m2, 'v_system': v_system,
        'p1': p1, 'p2': p2, 'p_total': p_total,
        'KE': ke,
    }                                                          # Complete before-cut state

def AfterCutState(m1, m2, p_total, v2_after):
    """
    State after spring cut. Given p_total (conserved) and v2_after,
    solve for v1_after.
    p_total = m1·v1 + m2·v2 → v1 = (p_total − m2·v2) / m1
    """
    v1_after = (p_total - m2 * v2_after) / m1 if m1 > 0 else 0.0
    p1 = m1 * v1_after
    p2 = m2 * v2_after
    ke = 0.5 * m1 * v1_after ** 2 + 0.5 * m2 * v2_after ** 2
    return {
        'v1': v1_after, 'v2': v2_after,
        'p1': p1, 'p2': p2, 'p_total': p1 + p2,
        'KE': ke,
        'conserved': abs((p1 + p2) - p_total) < 1e-9,
    }                                                          # Complete after-cut state

def SpringCutProblem(m1, m2, v_system, v2_after):
    """
    Full spring-cut problem from lecture:
    Example — m1=2kg, m2=5kg, v_sys=2m/s → p_tot=14 kg·m/s
    After cut: v2=8m/s → v1 = (14−5·8)/2 = −13 m/s
    Returns full before and after state.
    """
    before = BeforeCutState(m1, m2, v_system)
    after  = AfterCutState(m1, m2, before['p_total'], v2_after)
    return {'before': before, 'after': after,
            'spring_KE_released': after['KE'] - before['KE']}  # KE added by spring release

# Without initial motion — spring compressed between stationary masses
def SpringCutFromRest(m1, m2, v2_after):
    """
    Spring cut when system initially at rest (p_total = 0).
    Conservation: 0 = m1·v1 + m2·v2 → v1 = −m2·v2/m1
    """
    v1 = -(m2 * v2_after) / m1 if m1 > 0 else 0.0
    p1 = m1 * v1; p2 = m2 * v2_after
    ke = 0.5*m1*v1**2 + 0.5*m2*v2_after**2
    return {
        'v1': v1, 'v2': v2_after,
        'p1': p1, 'p2': p2, 'p_total': p1+p2,                 # ≈ 0
        'KE': ke,
    }                                                          # Complete rest-cut state

# ============================================================
# ANGULAR MOMENTUM
# ============================================================

# Formula: L = r × p = m·v·r·sin θ  (for point mass)
# r = radius (m), v = speed (m/s), θ = angle between r and v (deg)
def AngularMomentum(mass, velocity, radius, angle_deg=90):
    theta = math.radians(angle_deg)
    return mass * velocity * radius * math.sin(theta)          # L = mvr·sin θ

# Formula: L = I·ω  — angular momentum from moment of inertia
def AngularMomentumFromI(moment_of_inertia, angular_velocity):
    return moment_of_inertia * angular_velocity                # L = Iω

# Formula: τ = dL/dt = I·α  — torque from rate of change of L
def TorqueFromAngularMomentum(delta_L, delta_t):
    if delta_t <= 0:
        return 0.0
    return delta_L / delta_t                                   # τ = ΔL/Δt

# Conservation of angular momentum: I1·ω1 = I2·ω2
def FinalAngularVelocity(I1, omega1, I2):
    if I2 <= 0:
        return 0.0
    return I1 * omega1 / I2                                    # ω2 = I1ω1/I2

# ============================================================
# ROCKET PROPULSION (variable mass)
# ============================================================

# Formula: F_thrust = v_exhaust · (dm/dt)
# v_exhaust = exhaust speed relative to rocket (m/s)
# dm/dt = rate of mass loss (kg/s), negative since mass decreases
def RocketThrust(exhaust_speed, mass_flow_rate):
    return exhaust_speed * mass_flow_rate                      # F_thrust = v_ex · (dm/dt)

# Tsiolkovsky rocket equation: Δv = v_ex · ln(m_i/m_f)
def RocketDeltaV(exhaust_speed, mass_initial, mass_final):
    if mass_final <= 0 or mass_initial <= 0:
        return 0.0
    return exhaust_speed * math.log(mass_initial / mass_final) # Δv = v_ex·ln(m_i/m_f)

# Required propellant mass for a given Δv
def RocketPropellantMass(delta_v, exhaust_speed, mass_payload):
    if exhaust_speed <= 0:
        return 0.0
    ratio       = math.exp(delta_v / exhaust_speed)
    mass_initial = ratio * mass_payload
    return mass_initial - mass_payload                         # m_prop = m_i − m_f
