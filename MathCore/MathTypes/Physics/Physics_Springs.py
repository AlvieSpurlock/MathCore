import math  # sqrt, pi, cos, sin

# All units: mass (kg), distance/displacement (m), force (N),
# time (s), energy (J), spring constant k (N/m), g = 9.8 m/s².

# ============================================================
# HOOKE'S LAW
# ============================================================

# Formula: F_spring = −k·x
# Returns the restoring force of a spring displaced by x from equilibrium.
# Negative sign: force opposes displacement (restoring direction).
# Returns the magnitude; sign convention: negative = restoring.
def SpringForce(k, x):
    return -k * x                                              # Complete F = −kx (restoring)

# Formula: F_applied = k·x  — force needed to hold spring at displacement x
def AppliedForceToHold(k, x):
    return k * x                                               # F_applied = kx (no negative)

# Formula: x = F / k  — displacement caused by applied force
def SpringDisplacement(force, k):
    if k <= 0:                                                 # Guard against invalid k
        return 0.0
    return force / k                                           # Complete x = F/k

# Formula: k = F / x  — spring constant from force and displacement
def SpringConstant(force, x):
    if x == 0:                                                 # Guard against zero displacement
        return 0.0
    return force / x                                           # Complete k = F/x

# Formula: k_eff for springs in series: 1/k_eff = 1/k1 + 1/k2 + ...
def SpringConstantSeries(*k_values):
    if any(k <= 0 for k in k_values):                         # Guard against invalid constants
        return 0.0
    recip = sum(1.0 / k for k in k_values)
    return 1.0 / recip                                         # Complete k_eff (series)

# Formula: k_eff for springs in parallel: k_eff = k1 + k2 + ...
def SpringConstantParallel(*k_values):
    return sum(k_values)                                       # Complete k_eff (parallel)

# Formula: natural length after stretch — L_new = L_0 + x
def SpringLength(natural_length, displacement):
    return natural_length + displacement                       # Total stretched length

# ============================================================
# SPRING POTENTIAL ENERGY
# ============================================================

# Formula: PE_spring = ½·k·x²
def SpringPE(k, x):
    return 0.5 * k * x ** 2                                   # Complete PE_spring = ½kx²

# Formula: x = √(2·PE / k)  — displacement from stored PE
def DisplacementFromPE(pe, k):
    if k <= 0:
        return 0.0
    return math.sqrt(2.0 * pe / k)                            # Complete x = √(2PE/k)

# Formula: k = 2·PE / x²  — spring constant from PE and displacement
def SpringConstantFromPE(pe, x):
    if x == 0:
        return 0.0
    return 2.0 * pe / x ** 2                                  # k = 2PE/x²

# Formula: W_spring = −ΔPE_spring = ½k(x_i² − x_f²)
# Work done BY the spring as it moves from x_i to x_f
def WorkDoneBySpring(k, x_initial, x_final):
    return 0.5 * k * (x_initial ** 2 - x_final ** 2)          # W_spring = −ΔPE_spring

# Formula: W_applied = ΔPE_spring (work done AGAINST spring to compress/stretch it)
def WorkDoneAgainstSpring(k, x_initial, x_final):
    return SpringPE(k, x_final) - SpringPE(k, x_initial)      # W_applied = ΔPE_spring

# ============================================================
# SIMPLE HARMONIC MOTION — POSITION, VELOCITY, ACCELERATION
# ============================================================

# SHM equations:  x(t) = A·cos(ωt + φ)
#                 v(t) = −A·ω·sin(ωt + φ)
#                 a(t) = −A·ω²·cos(ωt + φ) = −ω²·x(t)
# A = amplitude (m), ω = angular frequency (rad/s), φ = phase angle (rad)

# Returns position of mass on spring at time t
def SHM_Position(amplitude, omega, t, phase=0.0):
    return amplitude * math.cos(omega * t + phase)             # x(t) = A·cos(ωt+φ)

# Returns velocity at time t in SHM
def SHM_Velocity(amplitude, omega, t, phase=0.0):
    return -amplitude * omega * math.sin(omega * t + phase)    # v(t) = −Aω·sin(ωt+φ)

# Returns acceleration at time t in SHM
def SHM_Acceleration(amplitude, omega, t, phase=0.0):
    return -amplitude * omega ** 2 * math.cos(omega * t + phase)  # a(t) = −Aω²·cos(ωt+φ)

# Returns acceleration from position alone: a = −ω²·x
def SHM_AccelFromPosition(omega, x):
    return -(omega ** 2) * x                                   # Complete a = −ω²x

# Maximum velocity occurs at equilibrium (x=0): v_max = A·ω
def SHM_MaxVelocity(amplitude, omega):
    return amplitude * omega                                   # v_max = Aω

# Maximum acceleration occurs at maximum displacement: a_max = A·ω²
def SHM_MaxAcceleration(amplitude, omega):
    return amplitude * omega ** 2                              # a_max = Aω²

# Velocity at a given displacement x: v = ω·√(A²−x²)
def SHM_VelocityAtPosition(amplitude, omega, x):
    under = amplitude ** 2 - x ** 2
    if under < 0:                                              # x outside allowed range
        return 0.0
    return omega * math.sqrt(under)                            # v = ω√(A²−x²)

# ============================================================
# PERIOD AND FREQUENCY
# ============================================================

# Formula: ω = √(k/m)  — angular frequency of spring-mass system
def AngularFrequency(k, mass):
    if mass <= 0 or k <= 0:                                    # Guard against invalid inputs
        return 0.0
    return math.sqrt(k / mass)                                 # Complete ω = √(k/m)

# Formula: T = 2π√(m/k)  — period of spring-mass oscillator
def Period(mass, k):
    if mass <= 0 or k <= 0:
        return 0.0
    return 2.0 * math.pi * math.sqrt(mass / k)                # Complete T = 2π√(m/k)

# Formula: f = 1/T = (1/2π)·√(k/m)  — frequency of oscillation (Hz)
def Frequency(mass, k):
    T = Period(mass, k)
    return 1.0 / T if T > 0 else 0.0                          # f = 1/T

# Formula: T_pendulum = 2π√(L/g)  — period of simple pendulum
def PendulumPeriod(length, g=9.8):
    if length <= 0:
        return 0.0
    return 2.0 * math.pi * math.sqrt(length / g)              # T = 2π√(L/g)

# Formula: f_pendulum = 1/(2π)·√(g/L)
def PendulumFrequency(length, g=9.8):
    T = PendulumPeriod(length, g)
    return 1.0 / T if T > 0 else 0.0                          # f = 1/T

# Period from angular frequency: T = 2π/ω
def PeriodFromOmega(omega):
    if omega <= 0:
        return 0.0
    return 2.0 * math.pi / omega                               # T = 2π/ω

# Angular frequency from period
def OmegaFromPeriod(period):
    if period <= 0:
        return 0.0
    return 2.0 * math.pi / period                              # ω = 2π/T

# Spring constant from known mass and period
def SpringConstantFromPeriod(mass, period):
    if period <= 0:
        return 0.0
    return mass * (2.0 * math.pi / period) ** 2                # k = m·(2π/T)²

# Mass from known spring constant and period
def MassFromPeriod(k, period):
    if period <= 0:
        return 0.0
    return k * (period / (2.0 * math.pi)) ** 2                 # m = k·(T/2π)²

# ============================================================
# SPRING VIBRATION — ENERGY DURING OSCILLATION
# ============================================================

# Total mechanical energy in SHM: E = ½·k·A²  (constant, conserved)
def SHM_TotalEnergy(k, amplitude):
    return 0.5 * k * amplitude ** 2                            # E_SHM = ½kA²

# KE at position x during SHM: KE = ½k(A²−x²)
def SHM_KE_AtPosition(k, amplitude, x):
    if abs(x) > amplitude:                                     # Outside amplitude bounds
        return 0.0
    return 0.5 * k * (amplitude ** 2 - x ** 2)                # KE = ½k(A²−x²)

# PE at position x during SHM: PE = ½kx²
def SHM_PE_AtPosition(k, x):
    return 0.5 * k * x ** 2                                    # PE = ½kx²

# Amplitude from total energy and spring constant
def AmplitudeFromEnergy(total_energy, k):
    if k <= 0:
        return 0.0
    return math.sqrt(2.0 * total_energy / k)                   # A = √(2E/k)

# Position where KE = PE (energy split 50/50): x = A/√2
def EquipartitionPosition(amplitude):
    return amplitude / math.sqrt(2.0)                          # x = A/√2

# ============================================================
# SPRING FORCES — STATIC AND DYNAMIC
# ============================================================

# Equilibrium stretch under gravity: x_eq = mg/k
def EquilibriumStretch(mass, k, g=9.8):
    if k <= 0:
        return 0.0
    return mass * g / k                                        # x_eq = mg/k

# Net force on mass at position x from equilibrium
def NetSpringForce(k, x, mass=0, g=9.8, include_gravity=False):
    f_spring = -k * x                                          # Restoring force
    f_grav   = mass * g if include_gravity else 0.0            # Gravity (optional)
    return f_spring + f_grav                                   # Net force on mass

# Force on a spring system compressed/stretched by x
def SpringNetForce(k, x):
    return -k * x                                              # F_net = −kx

# Spring force components when spring hangs mass vertically
def VerticalSpringForces(k, x_from_natural, mass, g=9.8):
    f_spring  = k * x_from_natural                             # Spring pull upward
    f_gravity = mass * g                                       # Weight downward
    f_net     = f_spring - f_gravity                           # Net force on mass
    return {'F_spring': f_spring, 'F_gravity': f_gravity, 'F_net': f_net}

# ============================================================
# SPRING STRETCH WITH MOMENTUM
# ============================================================

# Two-block spring system at rest — total momentum = 0
# When the spring releases, blocks fly apart with equal & opposite momenta.

# Formula: p_total = 0 → m1·v1 = −m2·v2
# Given one velocity, returns the other (by conservation of momentum)
def SpringReleaseVelocities(m1, m2, v1=None, v2=None):
    """
    Spring compressed between two blocks initially at rest.
    p_total = 0 → m1·v1 + m2·v2 = 0 → v2 = −m1·v1/m2.
    Provide either v1 or v2 (not both).
    Returns (v1, v2).
    """
    if v1 is not None:
        v2_calc = -(m1 * v1) / m2 if m2 > 0 else 0.0
        return v1, v2_calc                                     # v2 = −m1v1/m2
    if v2 is not None:
        v1_calc = -(m2 * v2) / m1 if m1 > 0 else 0.0
        return v1_calc, v2                                     # v1 = −m2v2/m1
    return 0.0, 0.0                                            # Default — no motion

# Energy stored in compressed spring = KE of both blocks after release
def SpringEnergyToKE(k, compression):
    return SpringPE(k, compression)                            # All PE → KE at release

# ============================================================
# SPRING BEFORE / AFTER CUT (with Momentum)
# ============================================================

# System: two masses connected by a spring.
# Before cut: system may be moving together.
# After cut: spring releases → blocks separate.
# Total momentum is CONSERVED before and after the cut.

# From lecture (image 3 & 4):
# Before cut: m1=2kg + m2=5kg compressed spring, v_system=2m/s
# P_total_before = (m1+m2)·v = 7·2 = 14 kg·m/s
# After cut: P_total = 14 = m1·v1 + m2·v2
# If v2 = 8 m/s → v1 = (14 − 5·8)/2 = (14−40)/2 = −13 m/s (moves backward)

def TotalMomentumBefore(m1, m2, v_system):
    """Total momentum of two-mass system moving together before spring is cut."""
    return (m1 + m2) * v_system                                # p_tot = (m1+m2)·v

def VelocityAfterCut(p_total, m1, m2, v2):
    """
    After spring is cut, find v1 given total momentum and v2.
    p_total = m1·v1 + m2·v2 → v1 = (p_total − m2·v2) / m1
    """
    if m1 <= 0:
        return 0.0
    return (p_total - m2 * v2) / m1                            # Complete v1 = (p−m2v2)/m1

def SpringCutFullAnalysis(m1, m2, v_system, v2_after):
    """
    Full before/after analysis for a spring cut problem.
    Returns dict with all momentum and velocity values.
    """
    p_before = TotalMomentumBefore(m1, m2, v_system)
    v1_after = VelocityAfterCut(p_before, m1, m2, v2_after)
    p1_after = m1 * v1_after
    p2_after = m2 * v2_after
    p_after  = p1_after + p2_after
    ke_before = 0.5 * (m1 + m2) * v_system ** 2
    ke_after  = 0.5 * m1 * v1_after ** 2 + 0.5 * m2 * v2_after ** 2
    return {
        'p_before':  p_before,
        'p_after':   p_after,
        'conserved': abs(p_before - p_after) < 1e-9,
        'v1_after':  v1_after,
        'v2_after':  v2_after,
        'KE_before': ke_before,
        'KE_after':  ke_after,
        'KE_from_spring': ke_after - ke_before,                # Energy added by spring
    }                                                          # Complete cut analysis

# Spring stretch from equilibrium for a hanging mass
def SpringStretch(mass, k, g=9.8):
    return mass * g / k if k > 0 else 0.0                     # x = mg/k at equilibrium

# Momentum of each block after spring releases from compressed state at rest
def SpringReleaseWithMomentum(m1, m2, k, compression):
    pe_spring = SpringPE(k, compression)                       # Energy to distribute
    # Energy splits: ½m1v1² + ½m2v2² = PE, and m1v1 = −m2v2
    # → v1 = √(2·PE·m2 / (m1(m1+m2))), v2 = −m1v1/m2
    v1 = math.sqrt(2.0 * pe_spring * m2 / (m1 * (m1 + m2))) if (m1 > 0 and m2 > 0) else 0.0
    v2 = -(m1 * v1) / m2 if m2 > 0 else 0.0
    p1 = m1 * v1
    p2 = m2 * v2
    return {
        'v1': v1, 'v2': v2,
        'p1': p1, 'p2': p2,
        'p_total': p1 + p2,                                    # Should be ≈ 0
        'KE1': 0.5*m1*v1**2, 'KE2': 0.5*m2*v2**2,
        'KE_total': 0.5*m1*v1**2 + 0.5*m2*v2**2,
        'PE_spring': pe_spring,
    }                                                          # Complete release analysis
