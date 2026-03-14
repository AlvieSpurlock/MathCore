import math  # sqrt, pi, cos, sin, fabs

# All energies in Joules (J), masses in kg, velocities in m/s,
# heights in m, forces in N, distances in m, time in s, power in W.
# g defaults to 9.8 m/s² throughout.

# ============================================================
# KINETIC ENERGY
# ============================================================

# Formula: KE = ½mv²
# Returns the translational kinetic energy of an object
def KineticEnergy(mass, velocity):
    return 0.5 * mass * velocity ** 2                          # Complete KE = ½mv²

# Formula: v = √(2·KE / m)
# Returns the speed of an object given its kinetic energy and mass
def VelocityFromKE(ke, mass):
    if mass <= 0:                                              # Guard against invalid mass
        return 0.0
    return math.sqrt(2.0 * ke / mass)                         # Complete v = √(2KE/m)

# Formula: m = 2·KE / v²
# Returns the mass required to have a given KE at a given speed
def MassFromKE(ke, velocity):
    if velocity == 0:                                          # Guard against division by zero
        return 0.0
    return 2.0 * ke / velocity ** 2                           # Complete m = 2KE/v²

# Formula: ΔKE = KE_f − KE_i
# Returns the change in kinetic energy between two states
def DeltaKE(mass, v_initial, v_final):
    return KineticEnergy(mass, v_final) - KineticEnergy(mass, v_initial)  # ΔKE

# Formula: KE_rot = ½·I·ω²  — rotational kinetic energy
# I = moment of inertia (kg·m²), ω = angular velocity (rad/s)
def RotationalKE(moment_of_inertia, angular_velocity):
    return 0.5 * moment_of_inertia * angular_velocity ** 2    # Complete KE_rot = ½Iω²

# Formula: KE_total = KE_trans + KE_rot  — total KE for rolling object
def TotalKERolling(mass, velocity, moment_of_inertia, radius):
    ke_t = KineticEnergy(mass, velocity)                       # Translational part
    omega = velocity / radius if radius > 0 else 0             # ω = v/r for rolling
    ke_r = RotationalKE(moment_of_inertia, omega)              # Rotational part
    return ke_t + ke_r                                         # Complete KE_total

# ============================================================
# GRAVITATIONAL POTENTIAL ENERGY
# ============================================================

# Formula: GPE = m·g·h
# Returns gravitational potential energy; h measured from chosen reference level
def GravitationalPE(mass, height, g=9.8):
    return mass * g * height                                   # Complete GPE = mgh

# Formula: h = GPE / (m·g)
# Returns height from known gravitational PE and mass
def HeightFromGPE(gpe, mass, g=9.8):
    if mass <= 0 or g <= 0:                                    # Guard against invalid inputs
        return 0.0
    return gpe / (mass * g)                                    # Complete h = GPE/(mg)

# Formula: ΔGPE = m·g·Δh  — change in gravitational PE over a height change
def DeltaGPE(mass, h_initial, h_final, g=9.8):
    return mass * g * (h_final - h_initial)                    # ΔGPE = mgΔh

# Formula: path independence — GPE depends only on height, not on path taken
# Returns True confirming GPE of 3 paths with same Δh are equal
def PathIndependenceCheck(mass, height, g=9.8):
    gpe_direct = GravitationalPE(mass, height, g)              # Straight drop
    gpe_ramp   = GravitationalPE(mass, height, g)              # Via ramp (same Δh)
    gpe_stairs = GravitationalPE(mass, height, g)              # Via stairs (same Δh)
    return gpe_direct == gpe_ramp == gpe_stairs, gpe_direct    # Path-independent — all equal

# ============================================================
# SPRING POTENTIAL ENERGY
# ============================================================

# Formula: PE_spring = ½·k·x²
# k = spring constant (N/m), x = displacement from equilibrium (m)
def SpringPE(k, x):
    return 0.5 * k * x ** 2                                    # Complete PE_spring = ½kx²

# Formula: x = √(2·PE_spring / k)
# Returns compression/extension given spring PE and spring constant
def DisplacementFromSpringPE(pe_spring, k):
    if k <= 0:                                                 # Guard against invalid k
        return 0.0
    return math.sqrt(2.0 * pe_spring / k)                     # Complete x = √(2PE/k)

# ============================================================
# MECHANICAL ENERGY
# ============================================================

# Formula: ME = KE + GPE  — total mechanical energy (no spring)
def MechanicalEnergy(mass, velocity, height, g=9.8):
    return KineticEnergy(mass, velocity) + GravitationalPE(mass, height, g)  # ME = KE + GPE

# Formula: ME = KE + GPE + PE_spring  — total mechanical energy with spring
def MechanicalEnergyWithSpring(mass, velocity, height, k, x, g=9.8):
    return (KineticEnergy(mass, velocity)
            + GravitationalPE(mass, height, g)
            + SpringPE(k, x))                                  # ME = KE + GPE + PE_spring

# Formula: fraction of ME that is KE at a given position
def KEFraction(ke, total_me):
    if total_me == 0:                                          # Guard against zero total
        return 0.0
    return ke / total_me                                       # KE/ME → e.g. 0.3 = 30%

# Formula: fraction of ME that is PE
def PEFraction(pe, total_me):
    if total_me == 0:
        return 0.0
    return pe / total_me                                       # PE/ME → e.g. 0.7 = 70%

# Returns (PE, KE) at a given fraction of max height, given total ME
# Example from lecture: at 70% of max height → PE=7J, KE=3J for ME=10J
def EnergyAtHeightFraction(total_me, height_fraction):
    pe = total_me * height_fraction                            # PE proportional to h
    ke = total_me - pe                                         # KE = ME − PE
    return pe, ke                                              # (PE, KE) at that height

# ============================================================
# THERMAL ENERGY
# ============================================================

# Formula: Q = m·c·ΔT  — heat energy (thermal energy change)
# c = specific heat capacity (J/(kg·K)), ΔT = temperature change (K or °C)
def ThermalEnergy(mass, specific_heat, delta_T):
    return mass * specific_heat * delta_T                      # Complete Q = mcΔT

# Formula: ΔT = Q / (m·c)  — temperature change from heat input
def DeltaTempFromHeat(heat, mass, specific_heat):
    if mass <= 0 or specific_heat <= 0:                        # Guard against invalid inputs
        return 0.0
    return heat / (mass * specific_heat)                       # ΔT = Q/(mc)

# Formula: E_thermal_lost = ΔKE_lost  — energy lost to friction becomes thermal
# Returns thermal energy generated by friction over a distance
def FrictionThermalEnergy(friction_force, distance):
    return friction_force * distance                           # Q_friction = f·d

# Formula: ΔE_thermal = μ·m·g·d  — thermal energy from kinetic friction on flat surface
def KineticFrictionHeat(mu_k, mass, distance, g=9.8):
    return mu_k * mass * g * distance                         # Complete ΔE_thermal = μmgd

# ============================================================
# CHEMICAL ENERGY (stored energy in bonds)
# ============================================================

# Chemical energy is converted to other forms — these track conversions.

# Formula: E_chem → KE + heat  — efficiency of chemical→mechanical conversion
# efficiency: fraction [0,1] converted to useful mechanical work
def ChemicalToMechanical(chemical_energy, efficiency=1.0):
    mechanical = chemical_energy * efficiency                  # Useful mechanical output
    heat_lost  = chemical_energy * (1.0 - efficiency)         # Wasted as heat
    return mechanical, heat_lost                               # (mechanical, heat_lost)

# Formula: fuel energy from mass × specific energy
# specific_energy in J/kg (e.g. gasoline ≈ 46e6, hydrogen ≈ 142e6)
def FuelEnergy(fuel_mass, specific_energy):
    return fuel_mass * specific_energy                         # E_chem = m_fuel × e_specific

# ============================================================
# CONSERVATION OF ENERGY
# ============================================================

# Formula: E_i = E_f  (no non-conservative forces)
# KE_i + GPE_i = KE_f + GPE_f → ½mv_i² + mgh_i = ½mv_f² + mgh_f
# Returns final velocity given initial state (mass cancels out)
def FinalVelocityConservation(v_initial, h_initial, h_final, g=9.8):
    v2 = v_initial ** 2 + 2.0 * g * (h_initial - h_final)    # From energy conservation
    if v2 < 0:                                                 # Cannot reach this height
        return None
    return math.sqrt(v2)                                       # Complete v_f = √(v_i² + 2gΔh)

# Returns final height given initial state and final velocity
def FinalHeightConservation(v_initial, h_initial, v_final, g=9.8):
    return h_initial + (v_initial ** 2 - v_final ** 2) / (2.0 * g)  # h_f from conservation

# Formula: maximum height reached (v_f = 0 at peak)
# h_max = h_initial + v_initial² / (2g)
def MaxHeightConservation(v_initial, h_initial=0, g=9.8):
    return h_initial + v_initial ** 2 / (2.0 * g)             # Complete h_max

# Formula: E_i + W_nc = E_f  — with non-conservative work (e.g. friction, applied force)
# W_nc = work done by non-conservative forces (negative for friction)
def FinalVelocityWithFriction(mass, v_initial, h_initial, h_final, friction_force, distance, g=9.8):
    e_initial = MechanicalEnergy(mass, v_initial, h_initial, g)
    w_nc      = -friction_force * distance                     # Friction removes energy
    e_final   = e_initial + w_nc
    ke_final  = e_final - GravitationalPE(mass, h_final, g)
    if ke_final < 0:
        return 0.0                                             # All KE gone — object stops
    return math.sqrt(2.0 * ke_final / mass)                   # v_f from remaining KE

# Classic slide problem: v_f at bottom of slide (starts at rest)
# From lecture: 2kg cube from h=10m → v_f = 12.52 m/s
def SlideBottomVelocity(mass, h_top, h_bottom=0, v_initial=0, g=9.8):
    return FinalVelocityConservation(v_initial, h_top, h_bottom, g)  # v_f at bottom

# Returns full energy state dict at a point on the slide
def EnergyStateAtHeight(mass, velocity, height, g=9.8):
    ke  = KineticEnergy(mass, velocity)
    gpe = GravitationalPE(mass, height, g)
    me  = ke + gpe
    return {'KE': ke, 'GPE': gpe, 'ME': me,
            'KE_fraction': KEFraction(ke, me),
            'GPE_fraction': PEFraction(gpe, me)}               # Complete energy state dict

# ============================================================
# WORK AND WORK-ENERGY THEOREM
# ============================================================

# Formula: W = F·d·cos(θ)  — work done by a constant force
# θ is angle between force vector and displacement vector
def Work(force, distance, angle_deg=0):
    theta = math.radians(angle_deg)
    return force * distance * math.cos(theta)                  # Complete W = Fd·cos θ

# Formula: W_net = ΔKE  — work-energy theorem
# Returns the net work done on an object from its change in KE
def WorkEnergyTheorem(mass, v_initial, v_final):
    return DeltaKE(mass, v_initial, v_final)                   # W_net = ΔKE = ½m(v_f²−v_i²)

# Formula: W = ΔKE → F·d = ½m·v_f² − ½m·v_i²
# Returns force required to accelerate mass over a distance
def ForceFromWorkEnergyTheorem(mass, v_initial, v_final, distance):
    delta_ke = DeltaKE(mass, v_initial, v_final)
    return delta_ke / distance if distance != 0 else 0.0       # F = ΔKE / d

# Formula: W = −ΔPE  (for conservative forces only)
# Work done by conservative force = negative change in PE
def WorkByConservativeForce(pe_initial, pe_final):
    return -(pe_final - pe_initial)                            # W_conservative = −ΔPE

# Formula: W_gravity = −ΔGP = m·g·(h_i − h_f)
def WorkByGravity(mass, h_initial, h_final, g=9.8):
    return mass * g * (h_initial - h_final)                    # W_gravity = mg(h_i − h_f)

# Formula: W_spring = −ΔPE_spring = ½k(x_i² − x_f²)
def WorkBySpring(k, x_initial, x_final):
    return 0.5 * k * (x_initial ** 2 - x_final ** 2)          # W_spring = ½k(x_i²−x_f²)

# ============================================================
# IS WORK? — WORD PROBLEM PARSER
# ============================================================

# Work requires: (1) an applied force, (2) displacement in direction of force.
# W = F·d·cos θ = 0 when θ = 90° or d = 0.

# Keyword sets for classification
_FORCE_WORDS   = {'push', 'pull', 'lift', 'carry', 'throw', 'apply', 'kick',
                  'drag', 'drop', 'falls', 'shot', 'fired', 'moves', 'slides',
                  'applied', 'exerts', 'hits'}
_NO_DISP_WORDS = {'wall', 'immovable', 'stationary', 'still', 'does not move',
                  'stays put', 'exhausted', 'pushes against'}
_PERP_WORDS    = {'constant speed', 'horizontal', 'across', 'level', 'side',
                  'perpendicular', 'normal', 'waiter', 'carries', 'above his head'}
_GRAVITY_WORDS = {'falls', 'drops', 'free fall', 'thrown', 'projectile'}

def IsWork(problem_text):
    """
    Parses a physics word problem and determines whether work is done.

    Returns a dict:
      is_work   : bool   — True if work is done
      reason    : str    — explanation
      W_formula : str    — relevant formula hint

    Rules applied (from lecture examples):
      1. Force applied to immovable object (wall, no displacement) → NOT work
      2. Force perpendicular to displacement (waiter carrying tray) → NOT work
      3. Gravity does work when object has vertical displacement
      4. Lifting, throwing, or any net displacement in force direction → IS work
    """
    text  = problem_text.lower()
    words = set(text.split())

    # Rule 1: no displacement — pushing against something immovable
    for nw in _NO_DISP_WORDS:
        if nw in text:
            return {'is_work': False,
                    'reason':  'No displacement occurs — force applied to immovable object.',
                    'W_formula': 'W = F·d·cos θ = 0 (d = 0)'}

    # Rule 2: force perpendicular to motion — waiter / constant horizontal carry
    # Carrying upward force while moving horizontally → θ = 90° → cos 90° = 0
    carries = 'carries' in text or 'carrying' in text
    horizontal = 'horizontal' in text or 'across' in text or 'constant speed' in text
    above_head = 'above' in text and ('head' in text or 'shoulder' in text)
    if (carries or above_head) and horizontal:
        return {'is_work': False,
                'reason': 'Applied force is perpendicular to displacement (θ=90°) — cos 90°=0.',
                'W_formula': 'W = F·d·cos(90°) = 0'}

    # Rule 3: gravity does work — free fall or vertical displacement downward
    for gw in _GRAVITY_WORDS:
        if gw in text:
            return {'is_work': True,
                    'reason': 'Gravity exerts a downward force and the object displaces downward.',
                    'W_formula': 'W = m·g·h (gravity does positive work)'}

    # Rule 4: lifting — force and displacement both upward
    if 'lift' in text or 'raises' in text or 'picks up' in text:
        return {'is_work': True,
                'reason': 'Applied force and displacement are in the same direction (upward).',
                'W_formula': 'W = F·d·cos(0°) = F·d'}

    # Rule 5: general motion with applied force
    for fw in _FORCE_WORDS:
        if fw in text:
            return {'is_work': True,
                    'reason': 'A force is applied and the object undergoes displacement.',
                    'W_formula': 'W = F·d·cos θ'}

    # Default: cannot determine
    return {'is_work': None,
            'reason': 'Cannot determine — check for a force AND displacement in the same direction.',
            'W_formula': 'W = F·d·cos θ'}

# Batch check — returns list of results for multiple problems
def IsWorkBatch(problems):
    return [{'problem': p, **IsWork(p)} for p in problems]    # Run IsWork on each problem

# ============================================================
# RELATING POTENTIAL ENERGY TO FORCE
# ============================================================

# Formula: F(x) = −dU/dx  — force from potential energy function
# For a constant force over Δx: ΔU(x) = −W = −F(x)·Δx
# → F(x) = −ΔU(x) / Δx

def ForceFromPotential(delta_U, delta_x):
    """
    Returns the conservative force from the change in potential energy.
    F = −ΔU/Δx  (negative gradient of potential)
    Positive result → force in +x direction.
    """
    if delta_x == 0:                                           # Guard division by zero
        return 0.0
    return -delta_U / delta_x                                  # Complete F = −ΔU/Δx

def WorkFromPotentialChange(pe_initial, pe_final):
    """
    W = −ΔU = −(U_f − U_i) = U_i − U_f
    Positive work → conservative force transfers PE into KE.
    """
    return pe_initial - pe_final                               # Complete W = −ΔU

def PotentialChangeFromWork(work_done):
    """ΔU = −W  — potential energy decreases when conservative force does positive work."""
    return -work_done                                          # ΔU = −W

# Formula: U(x) for common conservative forces
def GravitationalPotential_x(mass, height, g=9.8):
    return mass * g * height                                   # U_gravity = mgh

def SpringPotential_x(k, x):
    return 0.5 * k * x ** 2                                   # U_spring = ½kx²

def ElectricPotentialEnergy(charge, electric_potential):
    return charge * electric_potential                         # U_electric = qV

# ============================================================
# POWER
# ============================================================

# Formula: P_avg = W / Δt  — average power
def PowerAvg(work, time):
    if time <= 0:                                              # Guard against zero/negative time
        return 0.0
    return work / time                                         # Complete P_avg = W/Δt

# Formula: P = F·v  — instantaneous power from force and velocity
def PowerFromForce(force, velocity, angle_deg=0):
    theta = math.radians(angle_deg)
    return force * velocity * math.cos(theta)                  # Complete P = F·v·cos θ

# Formula: P = dW/dt  — approximated numerically
def InstantaneousPower(delta_work, delta_t):
    if delta_t <= 0:
        return 0.0
    return delta_work / delta_t                                # dW/dt approximation

# Formula: W = P·Δt  — work done at constant power over time
def WorkFromPower(power, time):
    return power * time                                        # W = P·Δt

# Formula: time = W / P
def TimeFromPowerWork(work, power):
    if power <= 0:
        return 0.0
    return work / power                                        # t = W/P

# Unit conversions for power
def WattsToHorsepower(watts):
    return watts / 746.0                                       # 1 hp = 746 W

def HorsepowerToWatts(hp):
    return hp * 746.0                                          # 1 hp = 746 W

def WattsToFtLbPerSec(watts):
    return watts / 1.35582                                     # 1 ft·lb/s = 1.356 W

# Efficiency: P_out / P_in
def PowerEfficiency(power_output, power_input):
    if power_input <= 0:
        return 0.0
    return power_output / power_input                          # η = P_out / P_in

# ============================================================
# ENERGY EXAMPLES — COMMON MULTI-STEP SCENARIOS
# ============================================================

# Projectile energy analysis — cannon ball example from lecture
# m=2kg, v0y=20m/s, v0x=5m/s, g=9.8
# Returns full energy profile: launch, apex, landing
def CannonBallEnergyProfile(mass, v0x, v0y, g=9.8):
    # Launch
    v_launch   = math.sqrt(v0x**2 + v0y**2)
    ke_launch  = KineticEnergy(mass, v_launch)
    gpe_launch = 0.0                                           # Reference height = 0

    # Apex (v_y = 0)
    h_max    = MaxHeightConservation(v0y, 0, g)
    ke_apex  = KineticEnergy(mass, v0x)                        # Only horizontal KE at apex
    gpe_apex = GravitationalPE(mass, h_max, g)
    me_apex  = ke_apex + gpe_apex

    # Landing (same height as launch, y=0)
    v_land   = v_launch                                        # Speed same as launch (no friction)
    ke_land  = KineticEnergy(mass, v_land)
    gpe_land = 0.0

    return {
        'launch': {'KE': ke_launch, 'GPE': gpe_launch, 'ME': ke_launch},
        'apex':   {'KE': ke_apex,   'GPE': gpe_apex,   'ME': me_apex, 'h_max': h_max},
        'land':   {'KE': ke_land,   'GPE': gpe_land,   'ME': ke_land},
    }                                                          # Complete energy profile

# Roller-coaster / slide multi-step energy tracking
# heights: list of [h0, h1, h2, ...], v_initial at h0
def RollerCoasterEnergyTrack(mass, heights, v_initial, g=9.8):
    results = []
    for h in heights:
        v   = FinalVelocityConservation(v_initial, heights[0], h, g)
        ke  = KineticEnergy(mass, v) if v is not None else 0.0
        gpe = GravitationalPE(mass, h, g)
        results.append({'height': h, 'velocity': v, 'KE': ke, 'GPE': gpe, 'ME': ke+gpe})
    return results                                             # Energy state at each height

# Energy lost to friction on a slide
def EnergyLostToFriction(mass, v_initial, h_initial, v_final, h_final, g=9.8):
    me_i = MechanicalEnergy(mass, v_initial, h_initial, g)
    me_f = MechanicalEnergy(mass, v_final, h_final, g)
    return me_i - me_f                                         # ΔE_lost = ME_i − ME_f ≥ 0

# ============================================================
# MAGNETIC FIELD ENERGY (stored in field)
# ============================================================

# Formula: U_B = B²·V / (2·μ₀)  — energy density in a magnetic field
# B = magnetic field (T), V = volume (m³), μ₀ = 4π×10⁻⁷ H/m
def MagneticFieldEnergy(B, volume, mu0=4 * math.pi * 1e-7):
    return (B ** 2 * volume) / (2.0 * mu0)                    # U_B = B²V / (2μ₀)

# Formula: u_B = B² / (2·μ₀)  — energy density (J/m³)
def MagneticEnergyDensity(B, mu0=4 * math.pi * 1e-7):
    return B ** 2 / (2.0 * mu0)                               # u_B = B²/(2μ₀)

# Formula: U_L = ½·L·I²  — energy stored in inductor
# L = inductance (H), I = current (A)
def InductorEnergy(inductance, current):
    return 0.5 * inductance * current ** 2                     # U_L = ½LI²

# Formula: current from inductor energy
def CurrentFromInductorEnergy(energy, inductance):
    if inductance <= 0:
        return 0.0
    return math.sqrt(2.0 * energy / inductance)                # I = √(2U/L)

# Formula: work done by magnetic force on moving charge = 0 (always perpendicular)
# Magnetic force never does work — it only changes direction of velocity
def WorkByMagneticForce():
    return 0.0                                                 # W_B = 0 always

# Formula: magnetic braking force power dissipation
# Eddy current braking: P = (B²·L²·v²) / R (simplified rail model)
def MagneticBrakingPower(B, length, velocity, resistance):
    if resistance <= 0:
        return 0.0
    return (B ** 2 * length ** 2 * velocity ** 2) / resistance  # P_braking

# ============================================================
# TRAIN MOVEMENT WITH MAGNETIC FIELD EFFECTS
# ============================================================

# Maglev train: magnetic levitation + linear motor propulsion
# Levitation force must equal weight for stable float
def MaglevLevitationCondition(mass, B, area, mu0=4 * math.pi * 1e-7, g=9.8):
    """
    Returns required magnetic pressure (B²/2μ₀) to levitate a train of given mass.
    Levitation: F_mag = weight → B²·A/(2μ₀) = mg
    """
    weight           = mass * g
    required_pressure = weight / area if area > 0 else 0.0
    required_B       = math.sqrt(2.0 * mu0 * required_pressure)
    return {'weight': weight,
            'required_pressure': required_pressure,
            'required_B': required_B}                          # Complete levitation condition

# Eddy current braking distance for a maglev/rail system
def MagneticBrakingDistance(mass, v_initial, B, length, resistance):
    """
    Estimates braking distance using energy dissipation model.
    Assumes constant braking force approximation: F = B²L²v/R (at v_initial).
    """
    ke_initial    = KineticEnergy(mass, v_initial)
    braking_force = (B**2 * length**2 * v_initial) / resistance if resistance > 0 else 0
    distance      = ke_initial / braking_force if braking_force > 0 else float('inf')
    return distance                                            # Approximate braking distance

# Train kinetic energy at speed (accounts for rotational mass of wheels)
# α = rotational mass correction factor (≈1.1 for typical trains)
def TrainKE(mass, velocity, rotational_factor=1.1):
    return rotational_factor * KineticEnergy(mass, velocity)   # KE_train ≈ α·½mv²

# Train power required to maintain constant speed against drag
# F_drag = c·v² (aerodynamic) + rolling resistance
def TrainPowerRequired(velocity, drag_coeff, rolling_resistance_force):
    aero_drag = drag_coeff * velocity ** 2
    total_drag = aero_drag + rolling_resistance_force
    return PowerFromForce(total_drag, velocity)                # P = F_total · v

# Energy for train trip: E = P·t  or  E = F_avg·d
def TrainTripEnergy(power, time):
    return power * time                                        # E = P·t (Joules)

# ============================================================
# ENERGY TYPE SUMMARY UTILITY
# ============================================================

# Returns a complete energy breakdown for an object in motion at a height
# with optional spring compression and thermal losses
def EnergyBreakdown(mass, velocity, height, k=0, x=0,
                    thermal_energy=0, chemical_energy=0, g=9.8):
    ke      = KineticEnergy(mass, velocity)
    gpe     = GravitationalPE(mass, height, g)
    spe     = SpringPE(k, x)
    mech    = ke + gpe + spe
    total   = mech + thermal_energy + chemical_energy
    return {
        'KE':          ke,
        'GPE':         gpe,
        'SpringPE':    spe,
        'Thermal':     thermal_energy,
        'Chemical':    chemical_energy,
        'Mechanical':  mech,
        'Total':       total,
    }                                                          # Complete energy breakdown
