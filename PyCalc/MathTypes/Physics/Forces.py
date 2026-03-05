from MathTypes.Basic import BasicMath  # Import BasicMath for Cosine and Sine functions
from Config import Checks, RNG         # Import Checks and RNG from Config
import math                            # Import math for sqrt
from MathTypes.Physics import Physics_2D, Physics_3D  # Import Physics_2D and Physics_3D

# ============================================================
# F = ma UTILITY FUNCTIONS
# ============================================================

# Formula: F = m * a
# Returns force — mass multiplied by acceleration
def Force(mass, acceleration):
    return mass * acceleration              # Multiply mass by acceleration → complete F = ma

# Formula: a = F / m
# Returns acceleration — force divided by mass
# Returns 0 if mass is zero to avoid division by zero
def Acceleration(force, mass):
    if mass == 0:                           # Guard against division by zero — cannot accelerate zero mass
        return 0                            # Return 0 safely
    return force / mass                     # Divide force by mass → complete a = F/m

# Formula: m = F / a
# Returns mass — force divided by acceleration
# Returns 0 if acceleration is zero to avoid division by zero
def Mass(force, acceleration):
    if acceleration == 0:                   # Guard against division by zero — cannot derive mass from zero acceleration
        return 0                            # Return 0 safely
    return force / acceleration             # Divide force by acceleration → complete m = F/a

# ============================================================
# FRICTION
# ============================================================

# Formula: Ff = μ * Fn
# Returns friction force — coefficient of friction multiplied by normal force
def FrictionForce(mu, normal_force):
    return mu * normal_force                # Multiply friction coefficient by normal force → complete Ff = μFn

# Formula: μ = Ff / Fn
# Returns the coefficient of friction — friction force divided by normal force
# Returns 0 if normal force is zero to avoid division by zero
def FrictionCoefficient(friction_force, normal_force):
    if normal_force == 0:                   # Guard against division by zero — no normal force means no friction
        return 0                            # Return 0 safely
    return friction_force / normal_force    # Divide friction force by normal force → complete μ = Ff/Fn

# Formula: Fn = m * g
# Returns normal force on a flat surface — mass multiplied by gravity
def NormalForce(mass, g = 9.8):
    return mass * g                         # Multiply mass by gravity → complete Fn = mg

# Formula: Fn = m * g * cos(angle)
# Returns normal force on an inclined surface — accounts for the angle of the slope
def NormalForceIncline(mass, angle, g = 9.8, isDegrees = True):
    return mass * g * Physics_2D.IHat(1, angle, isDegrees)  # Multiply mass * g by cos(angle) → complete Fn = mg*cos(θ)

# Formula: F_parallel = m * g * sin(angle)
# Returns the component of gravity pulling the object down the incline
def FrictionForceIncline(mass, angle, g = 9.8, isDegrees = True):
    return mass * g * Physics_2D.JHat(1, angle, isDegrees)  # Multiply mass * g by sin(angle) → complete F_parallel = mg*sin(θ)

# ============================================================
# TORQUE AND ROTATION
# ============================================================

# Formula: τ = r * F * sin(angle)
# Returns torque — the rotational force applied at a distance
def Torque(r, force, angle, isDegrees = True):
    return r * force * Physics_2D.JHat(1, angle, isDegrees)  # Multiply r * F by sin(angle) → complete τ = rF*sin(θ)

# Formula: α = τ / I
# Returns angular acceleration — torque divided by moment of inertia
# Returns 0 if moment of inertia is zero to avoid division by zero
def AngularAcceleration(torque, moment_of_inertia):
    if moment_of_inertia == 0:              # Guard against division by zero — no inertia means undefined rotation
        return 0                            # Return 0 safely
    return torque / moment_of_inertia       # Divide torque by moment of inertia → complete α = τ/I

# Formula: I = m * r²
# Returns moment of inertia for a point mass — mass multiplied by radius squared
def MomentOfInertia(mass, r):
    return mass * (r ** 2)                  # Multiply mass by radius squared → complete I = mr²

# Formula: L = I * ω
# Returns angular momentum — moment of inertia multiplied by angular velocity
def AngularMomentum(moment_of_inertia, angular_velocity):
    return moment_of_inertia * angular_velocity  # Multiply moment of inertia by angular velocity → complete L = Iω

# Formula: ω = v / r
# Returns angular velocity — linear velocity divided by radius
# Returns 0 if radius is zero to avoid division by zero
def AngularVelocity(linear_velocity, r):
    if r == 0:                              # Guard against division by zero — cannot rotate at zero radius
        return 0                            # Return 0 safely
    return linear_velocity / r             # Divide linear velocity by radius → complete ω = v/r

# Formula: v = ω * r
# Returns linear velocity from rotation — angular velocity multiplied by radius
def LinearVelocityFromRotation(angular_velocity, r):
    return angular_velocity * r            # Multiply angular velocity by radius → complete v = ωr

# ============================================================
# WORK AND ENERGY
# ============================================================

# Formula: W = F * d * cos(angle)
# Returns work done — force times distance in the direction of motion
def Work(force, distance, angle = 0, isDegrees = True):
    return force * distance * Physics_2D.IHat(1, angle, isDegrees)  # Multiply F * d by cos(angle) → complete W = Fd*cos(θ)

# Formula: KE = ½ * m * v²
# Returns kinetic energy — energy of a moving object
def KineticEnergy(mass, velocity):
    return 0.5 * mass * (velocity ** 2)    # Multiply ½ by mass and velocity squared → complete KE = ½mv²

# Formula: PE = m * g * h
# Returns gravitational potential energy — energy stored by height
def PotentialEnergy(mass, height, g = 9.8):
    return mass * g * height               # Multiply mass by gravity and height → complete PE = mgh

# Formula: ME = KE + PE
# Returns total mechanical energy — sum of kinetic and potential energy
def MechanicalEnergy(mass, velocity, height, g = 9.8):
    ke = KineticEnergy(mass, velocity)     # Calculate kinetic energy → ½mv²
    pe = PotentialEnergy(mass, height, g)  # Calculate potential energy → mgh
    return ke + pe                         # Sum kinetic and potential energy → complete ME = KE + PE

# Formula: P = W / t
# Returns power — work done divided by time taken
# Returns 0 if time is zero to avoid division by zero
def Power(work, time):
    if time == 0:                           # Guard against division by zero — cannot calculate power at zero time
        return 0                            # Return 0 safely
    return work / time                      # Divide work by time → complete P = W/t

# Formula: P = F * v
# Returns power from force and velocity — force multiplied by velocity
def PowerFromForce(force, velocity):
    return force * velocity                 # Multiply force by velocity → complete P = Fv

# ============================================================
# MOMENTUM AND IMPULSE
# ============================================================

# Formula: p = m * v
# Returns momentum — mass multiplied by velocity
def Momentum(mass, velocity):
    return mass * velocity                  # Multiply mass by velocity → complete p = mv

# Formula: J = F * t
# Returns impulse — force applied over a time interval
def Impulse(force, time):
    return force * time                     # Multiply force by time → complete J = Ft

# Formula: J = Δp = m * (v2 - v1)
# Returns impulse from change in momentum — mass times change in velocity
def ImpulseFromMomentum(mass, v1, v2):
    return mass * (v2 - v1)                 # Multiply mass by velocity change → complete J = m(v2-v1)

# Formula: v_final = (m1*v1 + m2*v2) / (m1 + m2)
# Returns final velocity after a perfectly inelastic collision — objects stick together
# Returns 0 if total mass is zero to avoid division by zero
def CollisionInelastic(m1, v1, m2, v2):
    total_mass = m1 + m2                                        # Sum both masses → total mass after collision
    if total_mass == 0:                                         # Guard against division by zero — no mass means undefined velocity
        return 0                                                # Return 0 safely
    return (m1 * v1 + m2 * v2) / total_mass                    # Divide combined momentum by total mass → complete v = (m1v1+m2v2)/(m1+m2)

# Formula: v1' = ((m1-m2)*v1 + 2*m2*v2) / (m1+m2)
#          v2' = ((m2-m1)*v2 + 2*m1*v1) / (m1+m2)
# Returns (v1_final, v2_final) after a perfectly elastic collision — kinetic energy is conserved
# Returns (0, 0) if total mass is zero to avoid division by zero
def CollisionElastic(m1, v1, m2, v2):
    total_mass = m1 + m2                                        # Sum both masses → total mass of the system
    if total_mass == 0:                                         # Guard against division by zero — no mass means undefined velocity
        return 0, 0                                             # Return 0 safely
    v1_final = ((m1 - m2) * v1 + 2 * m2 * v2) / total_mass    # Calculate v1 after collision → complete v1'
    v2_final = ((m2 - m1) * v2 + 2 * m1 * v1) / total_mass    # Calculate v2 after collision → complete v2'
    return v1_final, v2_final                                   # Return both final velocities → complete elastic collision

# ============================================================
# GRAVITY BETWEEN TWO MASSES
# ============================================================

# Formula: F = G * (m1 * m2) / r²
# Returns gravitational force between two masses
# G = gravitational constant (6.674 × 10⁻¹¹ N·m²/kg²)
# Returns 0 if distance is zero to avoid division by zero
def GravitationalForce(m1, m2, r, G = 6.674e-11):
    if r == 0:                              # Guard against division by zero — masses cannot occupy the same point
        return 0                            # Return 0 safely
    return G * (m1 * m2) / (r ** 2)        # Multiply G by both masses divided by distance squared → complete F = Gm1m2/r²

# Formula: g = G * M / r²
# Returns gravitational field strength at a distance from a mass
# Returns 0 if distance is zero to avoid division by zero
def GravitationalField(M, r, G = 6.674e-11):
    if r == 0:                              # Guard against division by zero — cannot be at center of mass
        return 0                            # Return 0 safely
    return G * M / (r ** 2)                # Multiply G by mass divided by distance squared → complete g = GM/r²

# ============================================================
# GRAVITY AS A FORCE
# ============================================================

# Formula: Fg = m * g
# Returns gravitational force on an object — the downward pull due to gravity
# This is the weight of the object — distinct from gravitational force between two masses
def GravityForce(mass, g = 9.8):
    return mass * g                         # Multiply mass by gravity → complete Fg = mg

# Formula: Fg = m * g  (returned as negative Y to represent downward direction)
# Returns gravitational force as a signed value — negative means downward
# Use this when direction matters, such as when summing forces in a 2D/3D system
def GravityForceDirectional(mass, g = 9.8):
    return -(mass * g)                      # Negate to point downward → Fg acts in -Y direction

# Formula: h = ½ * g * t²  (from rest)
# Returns the distance an object falls from rest under gravity in a given time
def FreeFallDistance(time, g = 9.8):
    return 0.5 * g * (time ** 2)           # Multiply ½ by g and time squared → complete h = ½gt²

# Formula: v = g * t  (from rest)
# Returns the velocity of a free-falling object after a given time, starting from rest
def FreeFallVelocity(time, g = 9.8):
    return g * time                         # Multiply gravity by time → complete v = gt

# Formula: t = sqrt(2h / g)
# Returns the time it takes for an object to fall a given height from rest
# Returns 0 if gravity is zero to avoid division by zero
def FreeFallTime(height, g = 9.8):
    if g == 0:                              # Guard against division by zero — no gravity means no free fall
        return 0                            # Return 0 safely
    return math.sqrt((2 * height) / g)     # Take square root of 2h/g → complete t = sqrt(2h/g)

# ============================================================
# TENSION
# ============================================================

# Formula: T = m * g
# Returns tension in a rope supporting a stationary hanging mass — equals weight when at rest
def TensionHanging(mass, g = 9.8):
    return mass * g                         # Multiply mass by gravity → complete T = mg (no acceleration)

# Formula: T = m * (g + a)
# Returns tension in a rope when the object is accelerating upward
# Use positive a for upward acceleration, negative a for downward acceleration
def TensionAccelerating(mass, acceleration, g = 9.8):
    return mass * (g + acceleration)        # Add acceleration to gravity then multiply by mass → complete T = m(g+a)

# Formula: T = m * g * cos(angle)
# Returns tension in a rope at an angle — the vertical component must support the weight
# Returns the tension magnitude needed to hold the mass at the given angle from vertical
def TensionAtAngle(mass, angle, g = 9.8, isDegrees = True):
    cos_a = Physics_2D.IHat(1, angle, isDegrees)  # Get cos(angle) — horizontal component ratio
    if cos_a == 0:                                 # Guard against division by zero — angle of 90° means infinite tension
        return 0                                   # Return 0 safely — rope would be horizontal, cannot support weight
    return (mass * g) / cos_a                      # Divide weight by cos(angle) → complete T = mg/cos(θ)

# Formula: T = (2 * m1 * m2 * g) / (m1 + m2)
# Returns tension in the rope of an Atwood machine — two hanging masses connected over a pulley
# Returns 0 if total mass is zero to avoid division by zero
def TensionAtwood(m1, m2, g = 9.8):
    total_mass = m1 + m2                           # Sum both masses → denominator of Atwood formula
    if total_mass == 0:                            # Guard against division by zero — no mass means no tension
        return 0                                   # Return 0 safely
    return (2 * m1 * m2 * g) / total_mass          # Multiply 2*m1*m2*g divided by total mass → complete T = 2m1m2g/(m1+m2)

# Formula: a = (m1 - m2) * g / (m1 + m2)
# Returns the acceleration of an Atwood machine — net force divided by total mass
# Returns 0 if total mass is zero to avoid division by zero
def AtwoodAcceleration(m1, m2, g = 9.8):
    total_mass = m1 + m2                           # Sum both masses → total inertia of the system
    if total_mass == 0:                            # Guard against division by zero — no mass means no acceleration
        return 0                                   # Return 0 safely
    return ((m1 - m2) * g) / total_mass            # Divide net gravitational force by total mass → complete a = (m1-m2)g/(m1+m2)

# ============================================================
# CENTRIPETAL FORCE
# ============================================================

# Formula: Fc = m * v² / r
# Returns centripetal force — the inward force required to keep an object moving in a circle
# Returns 0 if radius is zero to avoid division by zero
def CentripetalForce(mass, velocity, r):
    if r == 0:                              # Guard against division by zero — cannot have circular motion with zero radius
        return 0                            # Return 0 safely
    return mass * (velocity ** 2) / r      # Multiply mass by velocity squared divided by radius → complete Fc = mv²/r

# Formula: Fc = m * ω² * r
# Returns centripetal force from angular velocity — useful when rotation rate is known instead of linear speed
def CentripetalForceFromOmega(mass, angular_velocity, r):
    return mass * (angular_velocity ** 2) * r  # Multiply mass by angular velocity squared and radius → complete Fc = mω²r

# Formula: ac = v² / r
# Returns centripetal acceleration — the inward acceleration of circular motion
# Returns 0 if radius is zero to avoid division by zero
def CentripetalAcceleration(velocity, r):
    if r == 0:                              # Guard against division by zero — no radius means undefined circular motion
        return 0                            # Return 0 safely
    return (velocity ** 2) / r             # Divide velocity squared by radius → complete ac = v²/r

# Formula: v = sqrt(Fc * r / m)
# Returns the velocity needed to maintain circular motion given a centripetal force
# Returns 0 if mass or radius is zero to avoid division by zero
def CentripetalVelocity(centripetal_force, r, mass):
    if mass == 0 or r == 0:                # Guard against division by zero — no mass or radius means undefined velocity
        return 0                           # Return 0 safely
    return math.sqrt((centripetal_force * r) / mass)  # Take square root of Fr/m → complete v = sqrt(Fc*r/m)

# Formula: T = 2π * r / v
# Returns the period of circular motion — time for one full revolution
# Returns 0 if velocity is zero to avoid division by zero
def CircularPeriod(r, velocity):
    if velocity == 0:                      # Guard against division by zero — no velocity means no revolution
        return 0                           # Return 0 safely
    return (2 * math.pi * r) / velocity   # Divide circumference by velocity → complete T = 2πr/v

# Formula: f = v / (2π * r)
# Returns the frequency of circular motion — revolutions per second
# Returns 0 if radius is zero to avoid division by zero
def CircularFrequency(velocity, r):
    if r == 0:                             # Guard against division by zero — no radius means undefined frequency
        return 0                           # Return 0 safely
    return velocity / (2 * math.pi * r)   # Divide velocity by circumference → complete f = v/(2πr)

# ============================================================
# EQUILIBRIUM
# ============================================================

# Formula: ΣF = 0  (static — net force is zero, net torque is zero)
# Returns True if the object is in static equilibrium — all forces and torques cancel out
# Accepts a list of force magnitudes and checks if they sum to zero within a small tolerance
def IsStaticEquilibrium(forces, torques = None, tolerance = 1e-9):
    net_force = sum(forces)                                     # Sum all force magnitudes → should be zero if balanced
    net_torque = sum(torques) if torques else 0                 # Sum all torques if provided → should also be zero
    force_balanced  = abs(net_force)  < tolerance               # Check if net force is effectively zero within tolerance
    torque_balanced = abs(net_torque) < tolerance               # Check if net torque is effectively zero within tolerance
    return force_balanced and torque_balanced                   # Both must be zero for true static equilibrium

# Formula: ΣF = 0  (net force is zero but object may be moving at constant velocity)
# Returns True if the object is in dynamic equilibrium — moving at constant velocity with no net force
# Dynamic equilibrium differs from static in that velocity is nonzero but acceleration is zero
def IsDynamicEquilibrium(forces, velocity, tolerance = 1e-9):
    net_force = sum(forces)                                     # Sum all force magnitudes → must be zero for constant velocity
    force_balanced = abs(net_force) < tolerance                 # Check if net force is effectively zero
    is_moving      = abs(velocity)  > tolerance                 # Check if object actually has nonzero velocity
    return force_balanced and is_moving                         # Forces balanced AND object moving → dynamic equilibrium

# Formula: F_net = ΣF
# Returns the net force from a list of signed force values
# Positive values are in the positive direction, negative values oppose
def NetForceFromList(forces):
    return sum(forces)                                          # Sum all signed forces → complete ΣF

# Formula: F_balance = -ΣF_others
# Returns the single force needed to bring a system into equilibrium
# This is the force that exactly cancels all existing forces
def EquilibriumForce(forces):
    return -sum(forces)                                         # Negate the sum of all forces → the balancing force needed

# ============================================================
# TERMINAL VELOCITY
# ============================================================

# Formula: v_t = sqrt(2mg / (ρ * A * Cd))
# Returns terminal velocity — the maximum speed reached when drag force equals gravitational force
# ρ   = fluid density (kg/m³) — default is air at sea level (1.225 kg/m³)
# A   = cross-sectional area of the object (m²)
# Cd  = drag coefficient — dimensionless (e.g. 0.47 for a sphere, 1.0 for a flat plate)
# Returns 0 if any denominator component is zero to avoid division by zero
def TerminalVelocity(mass, area, drag_coefficient, fluid_density = 1.225, g = 9.8):
    denominator = fluid_density * area * drag_coefficient       # Calculate drag denominator → ρ * A * Cd
    if denominator == 0:                                        # Guard against division by zero — no drag means undefined terminal velocity
        return 0                                                # Return 0 safely
    return math.sqrt((2 * mass * g) / denominator)             # Take square root of 2mg/denominator → complete v_t = sqrt(2mg/ρACd)

# Formula: Fd = ½ * ρ * v² * A * Cd
# Returns aerodynamic drag force on a moving object
# This is the resistive force that opposes motion through a fluid
def DragForce(velocity, area, drag_coefficient, fluid_density = 1.225):
    return 0.5 * fluid_density * (velocity ** 2) * area * drag_coefficient  # Multiply all drag terms → complete Fd = ½ρv²ACd

# Formula: v_t = sqrt(2mg / (ρ * A * Cd))  →  check if v ≈ v_t
# Returns True if the object has effectively reached terminal velocity
# Uses a tolerance percentage — default is within 1% of terminal velocity
def IsAtTerminalVelocity(velocity, mass, area, drag_coefficient, fluid_density = 1.225, g = 9.8, tolerance = 0.01):
    vt = TerminalVelocity(mass, area, drag_coefficient, fluid_density, g)  # Calculate terminal velocity for this object
    if vt == 0:                                                            # Guard against zero terminal velocity
        return False                                                       # Cannot be at terminal velocity if it doesn't exist
    return abs(velocity - vt) / vt < tolerance                            # Check if current velocity is within tolerance% of terminal velocity

# Formula: t ≈ m / (ρ * A * Cd * v_t) * ln(...)  — simplified as time constant τ = m / b where b = ½ρACd*v_t
# Returns the drag time constant — how quickly the object approaches terminal velocity
# Smaller τ means faster approach to terminal velocity
# Returns 0 if terminal velocity or drag coefficient is zero to avoid division by zero
def TerminalVelocityTimeConstant(mass, area, drag_coefficient, fluid_density = 1.225, g = 9.8):
    vt = TerminalVelocity(mass, area, drag_coefficient, fluid_density, g)  # Get terminal velocity first
    if vt == 0:                                                            # Guard against zero terminal velocity
        return 0                                                           # Return 0 safely
    b = 0.5 * fluid_density * area * drag_coefficient * vt                # Calculate linear drag coefficient b = ½ρACd*vt
    if b == 0:                                                             # Guard against zero drag
        return 0                                                           # Return 0 safely
    return mass / b                                                        # Divide mass by drag coefficient → complete τ = m/b

# ============================================================
# FORCES 2D
# ============================================================

# Represents a single 2D force vector
# Stores x, y, angle, and magnitude only — mass lives on the object not the force
class Force2D:
    x = 0
    y = 0
    angle = 0
    magnitude = 0

    def __init__(self, x, y, angle = 0, magnitude = 0):
        self.x = x
        self.y = y

        if magnitude == 0:                                          # If magnitude not provided...
            self.magnitude = math.sqrt(x**2 + y**2)                # Derive magnitude from components → sqrt(x² + y²)
        else:
            self.magnitude = magnitude                              # Use provided magnitude directly

        if angle == 0:                                              # If angle not provided...
            self.angle = Physics_2D.VectorAngle2D(x, y)            # Derive angle from components → atan2(y, x)
        else:
            self.angle = angle                                      # Use provided angle directly

# Represents a physical object with mass that has forces acting on it
# Mass lives here — on the object — not on individual forces
# Normal force is automatically derived from mass and gravity on creation
# All derived quantities (acceleration, momentum, energy) come from mass + net force
class Forces2D:
    def __init__(self, mass, g = 9.8):
        self.forces   = []                                          # Initialize empty list to store Force2D objects
        self.mass     = mass                                        # Store object mass — this is the single mass all forces act upon
        self.g        = g                                           # Store gravity — used for normal force and potential energy (default 9.8 m/s²)
        self.velocity = 0                                           # Initialize velocity — updated via UpdateVelocity after forces are applied
        self.height   = 0                                           # Initialize height — used for potential energy calculations
        self.normal   = NormalForce(mass, g)                        # Derive normal force automatically → Fn = mg (flat surface default)

    # Formula: Fn = m * g * cos(angle)
    # Recalculates normal force for an inclined surface — call this when the object is on a slope
    def SetIncline(self, angle, isDegrees = True):
        self.normal = NormalForceIncline(self.mass, angle, self.g, isDegrees)  # Update normal force for slope → Fn = mg*cos(θ)

    # Formula: Fg = m * g  (downward — negative Y)
    # Adds gravity as a downward force on the object — call this once after creating the object
    # Gravity points in the negative Y direction in 2D → (0, -mg)
    def ApplyGravity(self):
        fg    = self.mass * self.g                                  # Calculate gravitational force magnitude → Fg = mg
        force = Force2D(0, -fg)                                     # Create downward force — negative Y is down in 2D
        self.forces.append(force)                                   # Add gravity to the force list like any other force

    def AddForce(self, x, y, angle = 0, magnitude = 0):
        phForce = Force2D(x, y, angle, magnitude)                  # Create a new Force2D object from provided values
        self.forces.append(phForce)                                 # Add the new force to the forces list

    # Formula: Fx_net = Σ(f.magnitude * cos(f.angle))
    #          Fy_net = Σ(f.magnitude * sin(f.angle))
    #          magnitude_net = sqrt(Fx_net² + Fy_net²)
    #          angle_net = atan2(Fy_net, Fx_net)
    # Returns a Force2D representing the single combined result of all forces
    def NetForce(self):
        Fx = 0  # Initialize net X force accumulator
        Fy = 0  # Initialize net Y force accumulator

        for f in self.forces:                                       # Loop through every force in the list
            Fx += Physics_2D.IHat(f.magnitude, f.angle)            # Add X component of this force → magnitude * cos(angle)
            Fy += Physics_2D.JHat(f.magnitude, f.angle)            # Add Y component of this force → magnitude * sin(angle)

        magnitude = math.sqrt(Fx**2 + Fy**2)                       # Calculate net magnitude from summed components → sqrt(Fx² + Fy²)
        angle = Physics_2D.VectorAngle2D(Fx, Fy)                   # Calculate net angle from summed components → atan2(Fy, Fx)

        return Force2D(Fx, Fy, angle, magnitude)                    # Return a new Force2D representing the net force → complete Σf

    # Formula: a = F_net / m
    # Returns scalar net acceleration — derived from object mass and net force magnitude
    def NetAcceleration(self):
        net = self.NetForce()                                       # Get the net force acting on the object
        return Acceleration(net.magnitude, self.mass)               # Divide net force by object mass → complete a = F/m

    # Formula: p = m * v
    # Returns momentum of the object using its current velocity
    def NetMomentum(self):
        return Momentum(self.mass, self.velocity)                   # Multiply object mass by current velocity → complete p = mv

    # Formula: KE = ½ * m * v²
    # Returns kinetic energy of the object using its current velocity
    def NetKineticEnergy(self):
        return KineticEnergy(self.mass, self.velocity)              # Calculate ½mv² using object mass and current velocity → complete KE

    # Formula: PE = m * g * h
    # Returns gravitational potential energy using object mass and current height
    def NetPotentialEnergy(self):
        return PotentialEnergy(self.mass, self.height, self.g)      # Calculate mgh using object mass, height, and stored gravity → complete PE

    # Formula: ME = KE + PE
    # Returns total mechanical energy — sum of kinetic and potential energy
    def NetMechanicalEnergy(self):
        return MechanicalEnergy(self.mass, self.velocity, self.height, self.g)  # Sum KE and PE using object mass, velocity, height, gravity → complete ME

    # Formula: v = v + a * t
    # Updates the object's velocity based on net acceleration over a time step
    # Call this after setting up forces to advance the object's state forward in time
    def UpdateVelocity(self, time):
        a = self.NetAcceleration()                                  # Get current net acceleration → a = F_net / m
        self.velocity += a * time                                   # Add acceleration * time to velocity → complete v = v + at

    # Formula: J = F * t
    # Returns impulse delivered to the object by the net force over a time interval
    def NetImpulse(self, time):
        net = self.NetForce()                                       # Get the net force acting on the object
        return Impulse(net.magnitude, time)                         # Multiply net force by time → complete J = Ft

    # Formula: ΣF = 0
    # Returns True if the object is currently in static equilibrium — net force is zero and velocity is zero
    def IsStaticEquilibrium(self, tolerance = 1e-9):
        net = self.NetForce()                                       # Get the net force acting on the object
        force_zero    = net.magnitude < tolerance                   # Check if net force magnitude is effectively zero
        velocity_zero = abs(self.velocity) < tolerance              # Check if velocity is effectively zero — must be still
        return force_zero and velocity_zero                         # Both must be true for static equilibrium

    # Formula: ΣF = 0, v ≠ 0
    # Returns True if the object is in dynamic equilibrium — net force is zero but object is still moving
    def IsDynamicEquilibrium(self, tolerance = 1e-9):
        net = self.NetForce()                                       # Get the net force acting on the object
        force_zero = net.magnitude < tolerance                      # Check if net force magnitude is effectively zero
        is_moving  = abs(self.velocity) > tolerance                 # Check that object has nonzero velocity
        return force_zero and is_moving                             # Forces balanced AND moving → dynamic equilibrium

# ============================================================
# FORCES 3D
# ============================================================

# Represents a single 3D force vector
# Stores x, y, z, angle, phi, and magnitude only — mass lives on the object not the force
class Force3D:
    x = 0
    y = 0
    z = 0
    angle = 0
    phi = 0
    magnitude = 0

    def __init__(self, x, y, z, angle = 0, phi = 0, magnitude = 0):
        self.x = x
        self.y = y
        self.z = z

        if magnitude == 0:                                                  # If magnitude not provided...
            self.magnitude = math.sqrt(x**2 + y**2 + z**2)                 # Derive magnitude from components → sqrt(x² + y² + z²)
        else:
            self.magnitude = magnitude                                      # Use provided magnitude directly

        if angle == 0:                                                      # If angle not provided...
            self.angle, self.phi = Physics_3D.VectorAngle3D(x, y, z)       # Derive both angles from components → atan2 for theta and phi
        else:
            self.angle = angle                                              # Use provided azimuth angle directly
            self.phi = phi                                                  # Use provided elevation angle directly

# Represents a physical object with mass that has forces acting on it in 3D
# Mass lives here — on the object — not on individual forces
# Normal force is automatically derived from mass and gravity on creation
# All derived quantities (acceleration, momentum, energy) come from mass + net force
class Forces3D:
    def __init__(self, mass, g = 9.8):
        self.forces   = []                                                  # Initialize empty list to store Force3D objects
        self.mass     = mass                                                # Store object mass — this is the single mass all forces act upon
        self.g        = g                                                   # Store gravity — used for normal force and potential energy (default 9.8 m/s²)
        self.velocity = 0                                                   # Initialize velocity — updated via UpdateVelocity after forces are applied
        self.height   = 0                                                   # Initialize height — used for potential energy calculations
        self.normal   = NormalForce(mass, g)                                # Derive normal force automatically → Fn = mg (flat surface default)

    # Formula: Fn = m * g * cos(angle)
    # Recalculates normal force for an inclined surface — call this when the object is on a slope
    def SetIncline(self, angle, isDegrees = True):
        self.normal = NormalForceIncline(self.mass, angle, self.g, isDegrees)  # Update normal force for slope → Fn = mg*cos(θ)

    # Formula: Fg = m * g  (downward — negative Y)
    # Adds gravity as a downward force on the object — call this once after creating the object
    # Gravity points in the negative Y direction in 3D → (0, -mg, 0)
    def ApplyGravity(self):
        fg    = self.mass * self.g                                          # Calculate gravitational force magnitude → Fg = mg
        force = Force3D(0, -fg, 0)                                          # Create downward force — negative Y is down in 3D
        self.forces.append(force)                                           # Add gravity to the force list like any other force

    def AddForce(self, x, y, z, angle = 0, phi = 0, magnitude = 0):
        phForce = Force3D(x, y, z, angle, phi, magnitude)                  # Create a new Force3D object from provided values
        self.forces.append(phForce)                                         # Add the new force to the forces list

    # Formula: Fx_net = Σ(f.magnitude * cos(f.angle))
    #          Fy_net = Σ(f.magnitude * sin(f.angle))
    #          Fz_net = Σ(f.magnitude * sin(f.phi) * cos(f.angle))
    #          magnitude_net = sqrt(Fx_net² + Fy_net² + Fz_net²)
    #          angle_net, phi_net = atan2(Fy_net, Fx_net), atan2(Fz_net, sqrt(Fx²+Fy²))
    # Returns a Force3D representing the single combined result of all forces
    def NetForce(self):
        Fx = 0  # Initialize net X force accumulator
        Fy = 0  # Initialize net Y force accumulator
        Fz = 0  # Initialize net Z force accumulator

        for f in self.forces:                                               # Loop through every force in the list
            Fx += Physics_3D.IHat(f.magnitude, f.angle)                    # Add X component of this force → magnitude * cos(angle)
            Fy += Physics_3D.JHat(f.magnitude, f.angle)                    # Add Y component of this force → magnitude * sin(angle)
            Fz += Physics_3D.KHat(f.magnitude, f.angle, f.phi)             # Add Z component of this force → magnitude * sin(phi) * cos(angle)

        magnitude = math.sqrt(Fx**2 + Fy**2 + Fz**2)                      # Calculate net magnitude from summed components → sqrt(Fx² + Fy² + Fz²)
        angle, phi = Physics_3D.VectorAngle3D(Fx, Fy, Fz)                  # Calculate net angles from summed components → theta and phi

        return Force3D(Fx, Fy, Fz, angle, phi, magnitude)                  # Return a new Force3D representing the net force → complete Σf

    # Formula: a = F_net / m
    # Returns scalar net acceleration — derived from object mass and net force magnitude
    def NetAcceleration(self):
        net = self.NetForce()                                               # Get the net force acting on the object
        return Acceleration(net.magnitude, self.mass)                       # Divide net force by object mass → complete a = F/m

    # Formula: p = m * v
    # Returns momentum of the object using its current velocity
    def NetMomentum(self):
        return Momentum(self.mass, self.velocity)                           # Multiply object mass by current velocity → complete p = mv

    # Formula: KE = ½ * m * v²
    # Returns kinetic energy of the object using its current velocity
    def NetKineticEnergy(self):
        return KineticEnergy(self.mass, self.velocity)                      # Calculate ½mv² using object mass and current velocity → complete KE

    # Formula: PE = m * g * h
    # Returns gravitational potential energy using object mass and current height
    def NetPotentialEnergy(self):
        return PotentialEnergy(self.mass, self.height, self.g)              # Calculate mgh using object mass, height, and stored gravity → complete PE

    # Formula: ME = KE + PE
    # Returns total mechanical energy — sum of kinetic and potential energy
    def NetMechanicalEnergy(self):
        return MechanicalEnergy(self.mass, self.velocity, self.height, self.g)  # Sum KE and PE using object mass, velocity, height, gravity → complete ME

    # Formula: v = v + a * t
    # Updates the object's velocity based on net acceleration over a time step
    # Call this after setting up forces to advance the object's state forward in time
    def UpdateVelocity(self, time):
        a = self.NetAcceleration()                                          # Get current net acceleration → a = F_net / m
        self.velocity += a * time                                           # Add acceleration * time to velocity → complete v = v + at

    # Formula: J = F * t
    # Returns impulse delivered to the object by the net force over a time interval
    def NetImpulse(self, time):
        net = self.NetForce()                                               # Get the net force acting on the object
        return Impulse(net.magnitude, time)                                 # Multiply net force by time → complete J = Ft

    # Formula: ΣF = 0
    # Returns True if the object is currently in static equilibrium — net force is zero and velocity is zero
    def IsStaticEquilibrium(self, tolerance = 1e-9):
        net = self.NetForce()                                               # Get the net force acting on the object
        force_zero    = net.magnitude < tolerance                           # Check if net force magnitude is effectively zero
        velocity_zero = abs(self.velocity) < tolerance                     # Check if velocity is effectively zero — must be still
        return force_zero and velocity_zero                                 # Both must be true for static equilibrium

    # Formula: ΣF = 0, v ≠ 0
    # Returns True if the object is in dynamic equilibrium — net force is zero but object is still moving
    def IsDynamicEquilibrium(self, tolerance = 1e-9):
        net = self.NetForce()                                               # Get the net force acting on the object
        force_zero = net.magnitude < tolerance                              # Check if net force magnitude is effectively zero
        is_moving  = abs(self.velocity) > tolerance                        # Check that object has nonzero velocity
        return force_zero and is_moving                                     # Forces balanced AND moving → dynamic equilibrium