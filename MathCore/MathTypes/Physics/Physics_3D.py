from MathTypes.Basic import BasicMath  # Import BasicMath for Cosine and Sine functions
from Config import Checks, RNG         # Import Checks and RNG from Config
import math                            # Import math for sqrt
from MathTypes.Physics import Physics_1D  # Import Physics_1D for 1D physics fallback calculations

# ============================================================
# VECTOR COMPONENT FUNCTIONS
# ============================================================

# Formula: i = a * cos(angle)
# The horizontal (X) component of a vector using magnitude and angle
def IHat(a, angle, isDegrees = True):
    return a * BasicMath.Cosine(angle, isDegrees)  # Multiply magnitude by cosine of angle → complete i component

# Formula: j = a * sin(angle)
# The vertical (Y) component of a vector using magnitude and angle
def JHat(a, angle, isDegrees = True):
    return a * BasicMath.Sine(angle, isDegrees)  # Multiply magnitude by sine of angle → complete j component

# Formula: k = a * sin(phi) * cos(angle)
# The depth (Z) component of a vector using magnitude and two angles
def KHat(a, angle, phi, isDegrees = True):
    return a * BasicMath.Sine(phi, isDegrees) * BasicMath.Cosine(angle, isDegrees)  # Multiply magnitude by sin(phi) and cos(angle) → complete k component

# Formula: a⃗ = a_x*i + a_y*j + a_z*k
# Returns all three vector components as a tuple (i, j, k)
def IJK(a, angle, phi, isDegrees = True):
    i = IHat(a, angle, isDegrees)              # Calculate i (X) component → a * cos(angle)
    j = JHat(a, angle, isDegrees)              # Calculate j (Y) component → a * sin(angle)
    k = KHat(a, angle, phi, isDegrees)         # Calculate k (Z) component → a * sin(phi) * cos(angle)
    return i, j, k  # Return all three components as a tuple → complete vector a⃗

# Formula: vx = a * cos(angle)
# Horizontal velocity component — identical to IHat but named for velocity context
def VX(a, angle, isDegrees = True):
    return a * BasicMath.Cosine(angle, isDegrees)  # Multiply magnitude by cosine of angle → complete vx

# Formula: vy = a * sin(angle)
# Vertical velocity component — identical to JHat but named for velocity context
def VY(a, angle, isDegrees = True):
    return a * BasicMath.Sine(angle, isDegrees)  # Multiply magnitude by sine of angle → complete vy

# Formula: vz = vy / vx
# Derived Z velocity component — equals tangent of angle
# Returns 0 if either component is zero to avoid division by zero
def VZ(vx, vy):
    if vx == 0 or vy == 0:  # Guard against division by zero — if either component is zero vz must be zero
        return 0             # Return 0 safely — no Z component when either axis is zero
    return vy / vx           # Divide vy by vx → complete vz (equals tan(angle))

# ============================================================
# VECTOR ANGLE FUNCTIONS
# ============================================================

# Formula: tan(θ) = ay / ax
# Returns the tangent of the angle of a vector from its components
# Returns 0 if ax = 0 to avoid division by zero (angle would be 90°)
def TanTheta(a, angle, isDegrees = True):
    ax = IHat(a, angle, isDegrees)  # Calculate horizontal component ax = a * cos(angle)
    ay = JHat(a, angle, isDegrees)  # Calculate vertical component ay = a * sin(angle)
    if ax == 0:   # Guard against division by zero — tan(90°) is undefined
        return 0  # Return 0 safely — cannot divide by zero
    return ay / ax  # Divide ay by ax → complete tan(θ)

# Formula: a⃗ = a_x*i + a_y*j + a_z*k
# Returns the vector components (ax, ay, az) — alias for IJK with clearer name
def VectorAngle(a, angle, phi, isDegrees = True):
    return IJK(a, angle, phi, isDegrees)  # Delegate to IJK → returns (i, j, k) tuple

# ============================================================
# VECTOR MAGNITUDE FUNCTIONS
# ============================================================

# Formula: ||a|| = sqrt(ax² + ay² + az²)
# Returns the scalar magnitude of a 3D vector
def VectorMagnitude(a, angle, phi, isDegrees = True):
    ax = IHat(a, angle, isDegrees)          # Calculate ax = a * cos(angle) → X component
    ay = JHat(a, angle, isDegrees)          # Calculate ay = a * sin(angle) → Y component
    az = KHat(a, angle, phi, isDegrees)     # Calculate az = a * sin(phi) * cos(angle) → Z component
    return math.sqrt((ax ** 2) + (ay ** 2) + (az ** 2))  # Sum squares and take sqrt → complete ||a||

# ============================================================
# VECTOR ARITHMETIC
# ============================================================

# Formula: a⃗ + b⃗ = (ax+bx)i + (ay+by)j + (az+bz)k
# Adds two vectors by summing their components individually
def AddVectors(a, angle_a, b, angle_b, phi_a, phi_b, isDegrees = True):
    ax, ay, az = IJK(a, angle_a, phi_a, isDegrees)  # Decompose vector a into components (ax, ay, az)
    bx, by, bz = IJK(b, angle_b, phi_b, isDegrees)  # Decompose vector b into components (bx, by, bz)
    rx = ax + bx  # Add X components → (ax+bx)i
    ry = ay + by  # Add Y components → (ay+by)j
    rz = az + bz  # Add Z components → (az+bz)k
    return rx, ry, rz  # Return result vector tuple → complete a⃗ + b⃗

# Formula: a⃗ - b⃗ = (ax-bx)i + (ay-by)j + (az-bz)k
# Subtracts two vectors by subtracting their components individually
def SubtractVectors(a, angle_a, b, angle_b, phi_a, phi_b, isDegrees = True):
    ax, ay, az = IJK(a, angle_a, phi_a, isDegrees)  # Decompose vector a into components (ax, ay, az)
    bx, by, bz = IJK(b, angle_b, phi_b, isDegrees)  # Decompose vector b into components (bx, by, bz)
    rx = ax - bx  # Subtract X components → (ax-bx)i
    ry = ay - by  # Subtract Y components → (ay-by)j
    rz = az - bz  # Subtract Z components → (az-bz)k
    return rx, ry, rz  # Return result vector tuple → complete a⃗ - b⃗

# ============================================================
# DOT AND CROSS PRODUCTS
# ============================================================

# Formula: a⃗ · b⃗ = (ax*bx) + (ay*by) + (az*bz)
# Returns a SCALAR — multiply matching components and sum them
def DotProduct(a, angle_a, b, angle_b, phi_a, phi_b, isDegrees = True):
    ax, ay, az = IJK(a, angle_a, phi_a, isDegrees)  # Decompose vector a into components (ax, ay, az)
    bx, by, bz = IJK(b, angle_b, phi_b, isDegrees)  # Decompose vector b into components (bx, by, bz)
    return (ax * bx) + (ay * by) + (az * bz)  # Multiply matching components and sum → complete a⃗ · b⃗

# Formula: a⃗ × b⃗ = (ay*bz - az*by)i + (az*bx - ax*bz)j + (ax*by - ay*bx)k
# Returns a VECTOR perpendicular to both input vectors
# NOTE: Not commutative — a × b ≠ b × a (swapping inputs flips direction)
def CrossProduct(a, angle_a, b, angle_b, phi_a, phi_b, isDegrees = True):
    ax, ay, az = IJK(a, angle_a, phi_a, isDegrees)  # Decompose vector a into components (ax, ay, az)
    bx, by, bz = IJK(b, angle_b, phi_b, isDegrees)  # Decompose vector b into components (bx, by, bz)
    rx = (ay * bz) - (az * by)  # Calculate i component of cross product → (ay*bz - az*by)i
    ry = (az * bx) - (ax * bz)  # Calculate j component of cross product → (az*bx - ax*bz)j
    rz = (ax * by) - (ay * bx)  # Calculate k component of cross product → (ax*by - ay*bx)k
    return rx, ry, rz  # Return perpendicular vector tuple → complete a⃗ × b⃗

# Formula: cos(θ) = (a⃗ · b⃗) / (||a|| * ||b||)
# Returns cos(θ) — useful for finding the angle between two vectors
# Returns 0 if either magnitude is zero to avoid division by zero
def DotProductMagnitude(a, angle_a, b, angle_b, phi_a, phi_b, isDegrees = True):
    mag_a = VectorMagnitude(a, angle_a, phi_a, isDegrees)                       # Calculate magnitude of vector a → ||a||
    mag_b = VectorMagnitude(b, angle_b, phi_b, isDegrees)                       # Calculate magnitude of vector b → ||b||
    dot = DotProduct(a, angle_a, b, angle_b, phi_a, phi_b, isDegrees)           # Calculate dot product → a⃗ · b⃗
    if mag_a == 0 or mag_b == 0:  # Guard against division by zero — zero magnitude vector has no direction
        return 0                   # Return 0 safely — cannot divide by zero magnitude
    return dot / (mag_a * mag_b)  # Divide dot product by product of magnitudes → complete cos(θ)

# Formula: ||a⃗ × b⃗|| = sqrt(rx² + ry² + rz²)
# Returns the scalar magnitude of the cross product
# Equals the area of the parallelogram formed by the two vectors
def CrossProductMagnitude(a, angle_a, b, angle_b, phi_a, phi_b, isDegrees = True):
    rx, ry, rz = CrossProduct(a, angle_a, b, angle_b, phi_a, phi_b, isDegrees)  # Calculate cross product components (rx, ry, rz)
    return math.sqrt((rx ** 2) + (ry ** 2) + (rz ** 2))  # Sum squares and take sqrt → complete ||a⃗ × b⃗||

# ============================================================
# SCALAR OPERATIONS
# ============================================================

# Formula: a⃗ × c = (ax*c)i + (ay*c)j + (az*c)k
# Multiplies each vector component by a scalar
# Positive scalar = same direction, Negative scalar = opposite direction
def ScalarMultiply(c, a, angle, phi, isDegrees = True):
    ax, ay, az = IJK(a, angle, phi, isDegrees)  # Decompose vector into components (ax, ay, az)
    return ax * c, ay * c, az * c  # Multiply each component by scalar c → complete a⃗ × c

# Formula: a⃗ / c = (ax/c)i + (ay/c)j + (az/c)k
# Divides each vector component by a scalar
# Returns (0, 0, 0) if scalar is zero to avoid division by zero
def ScalarDivide(c, a, angle, phi, isDegrees = True):
    if c == 0:          # Guard against division by zero — cannot divide by zero scalar
        return 0, 0, 0  # Return zero vector safely
    ax, ay, az = IJK(a, angle, phi, isDegrees)  # Decompose vector into components (ax, ay, az)
    rx = ax / c  # Divide X component by scalar → (ax/c)i
    ry = ay / c  # Divide Y component by scalar → (ay/c)j
    rz = az / c  # Divide Z component by scalar → (az/c)k
    return rx, ry, rz  # Return scaled vector tuple → complete a⃗ / c

# ============================================================
# ADVANCED VECTOR OPERATIONS
# ============================================================

# Formula: a⃗_unit = a⃗ / ||a⃗|| = (ax/||a||, ay/||a||, az/||a||)
# Returns a unit vector (magnitude = 1) pointing in the same direction
# Returns (0, 0, 0) if magnitude is zero — zero vector has no direction to normalize
def NormalizeVector(a, angle, phi, isDegrees = True):
    ax, ay, az = IJK(a, angle, phi, isDegrees)           # Decompose vector into components (ax, ay, az)
    mag = VectorMagnitude(a, angle, phi, isDegrees)      # Calculate magnitude ||a|| for normalization
    if mag == 0:        # Guard against division by zero — zero vector cannot be normalized
        return 0, 0, 0  # Return zero vector safely
    return ax / mag, ay / mag, az / mag  # Divide each component by magnitude → complete unit vector

# Formula: proj_b(a) = (a⃗ · b⃗) / ||b⃗||
# Returns the scalar projection of vector a onto vector b
# Returns 0 if magnitude of b is zero to avoid division by zero
def VectorProjection(a, angle_a, b, angle_b, phi_a, phi_b, isDegrees = True):
    dot = DotProduct(a, angle_a, b, angle_b, phi_a, phi_b, isDegrees)  # Calculate dot product a⃗ · b⃗
    mag = VectorMagnitude(b, angle_b, phi_b, isDegrees)                 # Calculate magnitude ||b⃗||
    if mag == 0:  # Guard against division by zero — cannot project onto zero vector
        return 0  # Return 0 safely
    return dot / mag  # Divide dot product by magnitude of b → complete projection

# ============================================================
# 3D MOTION FUNCTIONS
# ============================================================

# Formula: r⃗ = rx*i + ry*j + rz*k
# Returns the 3D position vector
# Derives any missing component from angle/phi if not provided
def Position3D(rx = 0, ry = 0, rz = 0, a = 0, angle = 0, phi = 0, isDegrees = True):
    if rx == 0:                              # If X position not provided...
        rx = IHat(a, angle, isDegrees)       # Derive X position from magnitude and angle → a * cos(angle)
    if ry == 0:                              # If Y position not provided...
        ry = JHat(a, angle, isDegrees)       # Derive Y position from magnitude and angle → a * sin(angle)
    if rz == 0:                              # If Z position not provided...
        rz = KHat(a, angle, phi, isDegrees)  # Derive Z position from magnitude and angles → a * sin(phi) * cos(angle)
    return rx, ry, rz  # Return position vector tuple → complete r⃗

# Formula: v⃗ = (drx/dt)*i + (dry/dt)*j + (drz/dt)*k = vx*i + vy*j + vz*k
# Returns the 3D velocity vector
# Derives any missing velocity or distance from provided locations and time
def Velocity3D(angle, phi, time, vx = 0, vy = 0, vz = 0, dx = 1, dy = 1, dz = 1, loc1 = 0, loc2 = 0, loc3 = 0, loc4 = 0, loc5 = 0, loc6 = 0, t1 = 0, t2 = 0, isDegrees = True):
    if dx == 0:                                  # If X distance not provided...
        dx = Physics_1D.GetDistance(loc1, loc2)  # Calculate X distance from X locations → loc2 - loc1
    if dy == 0:                                  # If Y distance not provided...
        dy = Physics_1D.GetDistance(loc3, loc4)  # Calculate Y distance from Y locations → loc4 - loc3
    if dz == 0:                                  # If Z distance not provided...
        dz = Physics_1D.GetDistance(loc5, loc6)  # Calculate Z distance from Z locations → loc6 - loc5
    if time == 0:                                # If time not provided...
        time = Physics_1D.GetTime(t1, t2)        # Calculate time from timestamps → t2 - t1
    if vx == 0:                                  # If X velocity not provided...
        vx = Physics_1D.Velocity(dx, time)       # Calculate X velocity → dx / time
    if vy == 0:                                  # If Y velocity not provided...
        vy = Physics_1D.Velocity(dy, time)       # Calculate Y velocity → dy / time
    if vz == 0:                                  # If Z velocity not provided...
        vz = Physics_1D.Velocity(dz, time)       # Calculate Z velocity → dz / time
    rx = IHat(vx, angle, isDegrees)              # Apply angle to X velocity → vx * cos(angle) → vx*i
    ry = JHat(vy, angle, isDegrees)              # Apply angle to Y velocity → vy * sin(angle) → vy*j
    rz = KHat(vz, angle, phi, isDegrees)         # Apply angles to Z velocity → vz * sin(phi) * cos(angle) → vz*k
    return rx, ry, rz  # Return velocity vector tuple → complete v⃗

# Formula: a⃗ = (dvx/dt)*i + (dvy/dt)*j + (dvz/dt)*k = ax*i + ay*j + az*k
# Returns the 3D acceleration vector
# Uses separate initial (dx1) and final (dx2) distances per axis to avoid equal velocities
def Acceleration3D(angle, phi, time, v1x = 0, v1y = 0, v1z = 0, v2x = 0, v2y = 0, v2z = 0, dx1 = 1, dy1 = 1, dz1 = 1, dx2 = 1, dy2 = 1, dz2 = 1, loc1 = 0, loc2 = 0, loc3 = 0, loc4 = 0, loc5 = 0, loc6 = 0, loc7 = 0, loc8 = 0, loc9 = 0, loc10 = 0, loc11 = 0, loc12 = 0, t1 = 0, t2 = 0, isDegrees = True):
    if dx1 == 0:                                   # If initial X distance not provided...
        dx1 = Physics_1D.GetDistance(loc1, loc2)   # Calculate initial X distance → loc2 - loc1
    if dy1 == 0:                                   # If initial Y distance not provided...
        dy1 = Physics_1D.GetDistance(loc3, loc4)   # Calculate initial Y distance → loc4 - loc3
    if dz1 == 0:                                   # If initial Z distance not provided...
        dz1 = Physics_1D.GetDistance(loc5, loc6)   # Calculate initial Z distance → loc6 - loc5
    if dx2 == 0:                                   # If final X distance not provided...
        dx2 = Physics_1D.GetDistance(loc7, loc8)   # Calculate final X distance → loc8 - loc7
    if dy2 == 0:                                   # If final Y distance not provided...
        dy2 = Physics_1D.GetDistance(loc9, loc10)  # Calculate final Y distance → loc10 - loc9
    if dz2 == 0:                                   # If final Z distance not provided...
        dz2 = Physics_1D.GetDistance(loc11, loc12) # Calculate final Z distance → loc12 - loc11
    if time == 0:                                  # If time not provided...
        time = Physics_1D.GetTime(t1, t2)          # Calculate time from timestamps → t2 - t1
    if v1x == 0:                                   # If initial X velocity not provided...
        v1x = Physics_1D.Velocity(dx1, time)       # Calculate initial X velocity → dx1 / time
    if v1y == 0:                                   # If initial Y velocity not provided...
        v1y = Physics_1D.Velocity(dy1, time)       # Calculate initial Y velocity → dy1 / time
    if v1z == 0:                                   # If initial Z velocity not provided...
        v1z = Physics_1D.Velocity(dz1, time)       # Calculate initial Z velocity → dz1 / time
    if v2x == 0:                                   # If final X velocity not provided...
        v2x = Physics_1D.Velocity(dx2, time)       # Calculate final X velocity → dx2 / time
    if v2y == 0:                                   # If final Y velocity not provided...
        v2y = Physics_1D.Velocity(dy2, time)       # Calculate final Y velocity → dy2 / time
    if v2z == 0:                                   # If final Z velocity not provided...
        v2z = Physics_1D.Velocity(dz2, time)       # Calculate final Z velocity → dz2 / time
    ax = Physics_1D.Acceleration(v1x, v2x, time)  # Calculate X acceleration → (v2x - v1x) / time → ax complete
    ay = Physics_1D.Acceleration(v1y, v2y, time)  # Calculate Y acceleration → (v2y - v1y) / time → ay complete
    az = Physics_1D.Acceleration(v1z, v2z, time)  # Calculate Z acceleration → (v2z - v1z) / time → az complete
    rx = IHat(ax, angle, isDegrees)                # Apply angle to X acceleration → ax * cos(angle) → ax*i
    ry = JHat(ay, angle, isDegrees)                # Apply angle to Y acceleration → ay * sin(angle) → ay*j
    rz = KHat(az, angle, phi, isDegrees)           # Apply angles to Z acceleration → az * sin(phi) * cos(angle) → az*k
    return rx, ry, rz  # Return acceleration vector tuple → complete a⃗

# ============================================================
# PROJECTILE MOTION — BASE FUNCTIONS
# ============================================================

# Formula: F_drag = 0.5 * rho * v² * Cd * A
# fx = -F * (vx / speed),  fy = -F * (vy / speed)
# Returns drag force components (fx, fy) opposing direction of motion
# rho = air density kg/m³ (default 1.225 at sea level)
# drag = drag coefficient (default 0.47 for a sphere)
# area = cross sectional area m²
def DragForce(mass, vx, vy, drag = 0.47, area = 1.0, rho = 1.225):
    speed = math.sqrt((vx ** 2) + (vy ** 2))        # Calculate total speed → sqrt(vx² + vy²)
    force = 0.5 * rho * (speed ** 2) * drag * area  # Calculate drag force magnitude → 0.5 * rho * v² * Cd * A
    if speed == 0:    # Guard against division by zero — no speed means no drag force
        return 0, 0   # Return zero drag safely
    fx = -force * (vx / speed)  # Calculate horizontal drag → opposes X direction of motion
    fy = -force * (vy / speed)  # Calculate vertical drag → opposes Y direction of motion
    return fx, fy  # Return drag force components → complete F_drag

# Formula: ax = Fx / m,  ay = -g + (Fy / m)
# Returns acceleration components (ax, ay) combining gravity and drag
def ProjectileAcceleration(mass, vx, vy, g = 9.8, drag = 0.47, area = 1.0, rho = 1.225):
    fx, fy = DragForce(mass, vx, vy, drag, area, rho)  # Get drag force components (fx, fy)
    ax = fx / mass           # Calculate horizontal acceleration → F = ma rearranged to a = F/m
    ay = (-g) + (fy / mass)  # Calculate vertical acceleration → gravity pulling down plus drag divided by mass
    return ax, ay  # Return acceleration components → complete ax and ay

# ============================================================
# PROJECTILE MOTION — HORIZONTAL
# ============================================================

# Formula: vx(t) = vx0 + ax*t
# Returns horizontal velocity at time t accounting for drag
def ProjectileVelocityX(a, angle, time, mass, g = 9.8, drag = 0.47, area = 1.0, rho = 1.225, isDegrees = True):
    vx = IHat(a, angle, isDegrees)                                      # Get initial horizontal velocity → a * cos(angle)
    vy = JHat(a, angle, isDegrees)                                      # Get initial vertical velocity → needed for drag calculation
    ax, ay = ProjectileAcceleration(mass, vx, vy, g, drag, area, rho)  # Calculate acceleration from drag and gravity
    return vx + (ax * time)  # Add acceleration effect over time → complete vx(t)

# Formula: x(t) = x0 + vx*t + 0.5*ax*t²
# Returns horizontal position at time t
def ProjectilePositionX(a, angle, time, mass, x0 = 0, g = 9.8, drag = 0.47, area = 1.0, rho = 1.225, isDegrees = True):
    vx = IHat(a, angle, isDegrees)                                      # Get initial horizontal velocity → a * cos(angle)
    vy = JHat(a, angle, isDegrees)                                      # Get initial vertical velocity → needed for drag calculation
    ax, ay = ProjectileAcceleration(mass, vx, vy, g, drag, area, rho)  # Calculate acceleration from drag and gravity
    return x0 + (vx * time) + (0.5 * ax * time ** 2)  # Apply kinematic formula → complete x(t)

# Formula: R = x0 + vx*t + 0.5*ax*t²  (x0 = 0)
# Returns horizontal range — horizontal position starting from zero
def ProjectileRange(a, angle, time, mass, g = 9.8, drag = 0.47, area = 1.0, rho = 1.225, isDegrees = True):
    return ProjectilePositionX(a, angle, time, mass, 0, g, drag, area, rho, isDegrees)  # Call ProjectilePositionX with x0 = 0 → complete range R

# Formula: x(t) = x0 + vx*t + 0.5*ax*t²  (stepped per dt)
# Returns list of horizontal X positions over time
# Recalculates drag at every step since velocity changes continuously
def ProjectilePathHorizontal(a, angle, total_time, mass, steps = 100, x0 = 0, g = 9.8, drag = 0.47, area = 1.0, rho = 1.225, isDegrees = True):
    path_x = []                     # Initialize empty list to store X positions
    dt = total_time / steps         # Calculate time per step → divide total time into equal intervals
    vx = IHat(a, angle, isDegrees)  # Get initial horizontal velocity → a * cos(angle)
    vy = JHat(a, angle, isDegrees)  # Get initial vertical velocity → needed for drag calculation
    x = x0                          # Set starting X position
    for i in range(steps):          # Loop through each time step
        ax, ay = ProjectileAcceleration(mass, vx, vy, g, drag, area, rho)  # Recalculate acceleration with current velocity
        x = x + (vx * dt) + (0.5 * ax * dt ** 2)  # Update X position using kinematic formula → x(t+dt)
        vx = vx + (ax * dt)         # Update horizontal velocity → vx changes due to air resistance each step
        vy = vy + (ay * dt)         # Update vertical velocity → needed to keep drag calculation accurate next step
        path_x.append(x)           # Store current X position in path
    return path_x  # Return list of all X positions → complete horizontal path

# ============================================================
# PROJECTILE MOTION — VERTICAL
# ============================================================

# Formula: vy(t) = vy0 + ay*t
# Returns vertical velocity at time t accounting for gravity and drag
def ProjectileVelocityY(a, angle, time, mass, g = 9.8, drag = 0.47, area = 1.0, rho = 1.225, isDegrees = True):
    vx = IHat(a, angle, isDegrees)                                      # Get initial horizontal velocity → needed for drag calculation
    vy = JHat(a, angle, isDegrees)                                      # Get initial vertical velocity → a * sin(angle)
    ax, ay = ProjectileAcceleration(mass, vx, vy, g, drag, area, rho)  # Calculate acceleration from drag and gravity
    return vy + (ay * time)  # Add acceleration effect over time → complete vy(t)

# Formula: y(t) = y0 + vy*t + 0.5*ay*t²
# Returns vertical position at time t
def ProjectilePositionY(a, angle, time, mass, y0 = 0, g = 9.8, drag = 0.47, area = 1.0, rho = 1.225, isDegrees = True):
    vx = IHat(a, angle, isDegrees)                                      # Get initial horizontal velocity → needed for drag calculation
    vy = JHat(a, angle, isDegrees)                                      # Get initial vertical velocity → a * sin(angle)
    ax, ay = ProjectileAcceleration(mass, vx, vy, g, drag, area, rho)  # Calculate acceleration from drag and gravity
    return y0 + (vy * time) + (0.5 * ay * time ** 2)  # Apply kinematic formula → complete y(t)

# Formula: t_max = -vy0 / ay,  h_max = y(t_max)
# Returns the maximum height reached by the projectile
# Step 1: Find time when vertical velocity = 0 (peak of arc)
# Step 2: Calculate Y position at that time
# Returns 0 if ay = 0 — no vertical acceleration means projectile never peaks
def ProjectileMaxHeight(a, angle, mass, g = 9.8, drag = 0.47, area = 1.0, rho = 1.225, isDegrees = True):
    vx = IHat(a, angle, isDegrees)                                      # Get initial horizontal velocity → needed for drag calculation
    vy = JHat(a, angle, isDegrees)                                      # Get initial vertical velocity → a * sin(angle)
    ax, ay = ProjectileAcceleration(mass, vx, vy, g, drag, area, rho)  # Calculate acceleration from drag and gravity
    if ay == 0:   # Guard against division by zero — no vertical acceleration means no peak
        return 0  # Return 0 safely
    t_max = -vy / ay  # Calculate time of peak → solve vy + ay*t = 0 for t → Step 1 complete
    return ProjectilePositionY(a, angle, t_max, mass, 0, g, drag, area, rho, isDegrees)  # Calculate Y at peak time → complete h_max

# Formula: y(t) = y0 + vy*t + 0.5*ay*t²  (stepped per dt)
# Returns list of vertical Y positions over time
# Recalculates drag at every step since velocity changes continuously
# Stops early if projectile hits ground (y < 0)
def ProjectilePathVertical(a, angle, total_time, mass, steps = 100, y0 = 0, g = 9.8, drag = 0.47, area = 1.0, rho = 1.225, isDegrees = True):
    path_y = []                     # Initialize empty list to store Y positions
    dt = total_time / steps         # Calculate time per step → divide total time into equal intervals
    vx = IHat(a, angle, isDegrees)  # Get initial horizontal velocity → needed for drag calculation
    vy = JHat(a, angle, isDegrees)  # Get initial vertical velocity → a * sin(angle)
    y = y0                          # Set starting Y position
    for i in range(steps):          # Loop through each time step
        ax, ay = ProjectileAcceleration(mass, vx, vy, g, drag, area, rho)  # Recalculate acceleration with current velocity
        y = y + (vy * dt) + (0.5 * ay * dt ** 2)  # Update Y position using kinematic formula → y(t+dt)
        vx = vx + (ax * dt)         # Update horizontal velocity → needed to keep drag calculation accurate next step
        vy = vy + (ay * dt)         # Update vertical velocity → vy changes with gravity and drag each step
        path_y.append(y)           # Store current Y position in path
        if y < 0:                   # Check if projectile has hit the ground
            break                   # Stop simulation — projectile has landed
    return path_y  # Return list of all Y positions → complete vertical path

# ============================================================
# PROJECTILE MOTION — COMBINED
# ============================================================

# Formula: vx(t) = vx0 + ax*t,  vy(t) = vy0 + ay*t
# Returns (vx, vy) velocity tuple at time t
def ProjectileVelocity(a, angle, time, mass, g = 9.8, drag = 0.47, area = 1.0, rho = 1.225, isDegrees = True):
    vx_t = ProjectileVelocityX(a, angle, time, mass, g, drag, area, rho, isDegrees)  # Calculate horizontal velocity at time t → vx(t)
    vy_t = ProjectileVelocityY(a, angle, time, mass, g, drag, area, rho, isDegrees)  # Calculate vertical velocity at time t → vy(t)
    return vx_t, vy_t  # Return velocity tuple → complete v⃗(t)

# Formula: x(t) = x0 + vx*t + 0.5*ax*t²,  y(t) = y0 + vy*t + 0.5*ay*t²
# Returns (x, y) position tuple at time t
def ProjectilePosition(a, angle, time, mass, x0 = 0, y0 = 0, g = 9.8, drag = 0.47, area = 1.0, rho = 1.225, isDegrees = True):
    x = ProjectilePositionX(a, angle, time, mass, x0, g, drag, area, rho, isDegrees)  # Calculate horizontal position at time t → x(t)
    y = ProjectilePositionY(a, angle, time, mass, y0, g, drag, area, rho, isDegrees)  # Calculate vertical position at time t → y(t)
    return x, y  # Return position tuple → complete r⃗(t)

# Formula: x(t) and y(t) stepped per dt, combined via zip into (x, y) pairs
# Returns list of (x, y) position tuples tracing the full path with air resistance
# zip pairs horizontal and vertical paths — stops at shortest list (when ground is hit)
def ProjectilePath(a, angle, total_time, mass, steps = 100, x0 = 0, y0 = 0, g = 9.8, drag = 0.47, area = 1.0, rho = 1.225, isDegrees = True):
    path_x = ProjectilePathHorizontal(a, angle, total_time, mass, steps, x0, g, drag, area, rho, isDegrees)  # Get list of all X positions along path
    path_y = ProjectilePathVertical(a, angle, total_time, mass, steps, y0, g, drag, area, rho, isDegrees)    # Get list of all Y positions along path
    return list(zip(path_x, path_y))  # Combine X and Y lists into (x, y) tuples → complete path

# Formula: x(t) = x0 + vx*t,  y(t) = y0 + vy*t + 0.5*(-g)*t²
# Returns list of (x, y) position tuples tracing the full path WITHOUT air resistance
# Uses clean kinematic formula since drag is absent — no step recalculation needed
# Stops when projectile hits ground (y < 0)
def ProjectilePathNoAR(a, angle, total_time, steps = 100, x0 = 0, y0 = 0, g = 9.8, isDegrees = True):
    path = []                       # Initialize empty list to store (x, y) positions
    dt = total_time / steps         # Calculate time per step → divide total time into equal intervals
    vx = IHat(a, angle, isDegrees)  # Get horizontal velocity → a * cos(angle) — stays constant with no drag
    vy = JHat(a, angle, isDegrees)  # Get initial vertical velocity → a * sin(angle)
    for i in range(steps):          # Loop through each time step
        t = i * dt                  # Calculate current time → step number multiplied by step size
        x = x0 + (vx * t)          # Calculate X position → vx is constant since there is no drag
        y = y0 + (vy * t) + (0.5 * (-g) * t ** 2)  # Calculate Y position → gravity pulls down, no drag to oppose it
        path.append((x, y))        # Store (x, y) position tuple in path
        if y < 0:                   # Check if projectile has hit the ground
            break                   # Stop simulation — projectile has landed
    return path  # Return list of all (x, y) positions → complete path without air resistance

# ============================================================
# COMPONENT-FORM 3D VECTOR OPERATIONS
# These functions accept raw (x, y, z) components directly
# instead of magnitude + angle + phi — used when vectors are
# already given in i/j/k notation as in textbook problems
# ============================================================

# Formula: a⃗ + b⃗ = (ax+bx)i + (ay+by)j + (az+bz)k
# Adds two 3D vectors given as raw components
# Example: AddVectorsXYZ(-1, -4, 2, 2, 2, 1) → (1.0, -2.0, 3.0)
def AddVectorsXYZ(ax, ay, az, bx, by, bz):
    return ax + bx, ay + by, az + bz  # Add each component pair → complete a⃗ + b⃗

# Formula: a⃗ - b⃗ = (ax-bx)i + (ay-by)j + (az-bz)k
# Subtracts two 3D vectors given as raw components
# Example: SubtractVectorsXYZ(3, 3, -2, -1, -4, 2) → (4.0, 7.0, -4.0)
def SubtractVectorsXYZ(ax, ay, az, bx, by, bz):
    return ax - bx, ay - by, az - bz  # Subtract each component pair → complete a⃗ - b⃗

# Formula: a⃗ · b⃗ = (ax*bx) + (ay*by) + (az*bz)
# Dot product of two 3D vectors given as raw components — returns a SCALAR
# Example: DotProductXYZ(3, 3, -2, 1, -2, 3) → -9.0
def DotProductXYZ(ax, ay, az, bx, by, bz):
    return (ax * bx) + (ay * by) + (az * bz)  # Multiply matching components and sum → complete a⃗ · b⃗

# Formula: a⃗ × b⃗ = (ay*bz - az*by)i + (az*bx - ax*bz)j + (ax*by - ay*bx)k
# Cross product of two 3D vectors given as raw components — returns a VECTOR
# NOTE: Not commutative — CrossProductXYZ(a,b) = −CrossProductXYZ(b,a)
# Example: CrossProductXYZ(-1, -4, 2, 2, 2, 1) → (-8.0, 5.0, 6.0)
def CrossProductXYZ(ax, ay, az, bx, by, bz):
    rx = (ay * bz) - (az * by)  # i component → ay*bz - az*by
    ry = (az * bx) - (ax * bz)  # j component → az*bx - ax*bz
    rz = (ax * by) - (ay * bx)  # k component → ax*by - ay*bx
    return rx, ry, rz            # Return perpendicular vector → complete a⃗ × b⃗

# Formula: a⃗ · (b⃗ × c⃗)
# Scalar triple product — dot product of a with the cross product of b and c
# Returns a SCALAR representing the signed volume of the parallelepiped formed by a, b, c
# Positive = right-hand orientation, Negative = left-hand orientation, Zero = coplanar vectors
# Example: ScalarTripleProduct(3, 3, -2, -1, -4, 2, 2, 2, 1) → -21.0
def ScalarTripleProduct(ax, ay, az, bx, by, bz, cx, cy, cz):
    cross_x, cross_y, cross_z = CrossProductXYZ(bx, by, bz, cx, cy, cz)  # Step 1: b⃗ × c⃗
    return DotProductXYZ(ax, ay, az, cross_x, cross_y, cross_z)           # Step 2: a⃗ · (b⃗ × c⃗) → complete

# Formula: a⃗ · (b⃗ + c⃗)
# Dot product of a with the sum of b and c
# Equivalent to (a⃗ · b⃗) + (a⃗ · c⃗) by the distributive property — both methods give the same result
# Returns a SCALAR
# Example: DotWithSum(3, 3, -2, -1, -4, 2, 2, 2, 1) → -9.0
def DotWithSum(ax, ay, az, bx, by, bz, cx, cy, cz):
    sum_x, sum_y, sum_z = AddVectorsXYZ(bx, by, bz, cx, cy, cz)  # Step 1: b⃗ + c⃗
    return DotProductXYZ(ax, ay, az, sum_x, sum_y, sum_z)          # Step 2: a⃗ · (b⃗ + c⃗) → complete

# Formula: a⃗ · (b⃗ - c⃗)
# Dot product of a with the difference of b and c
# Returns a SCALAR
# Example: DotWithDifference(3, 3, -2, -1, -4, 2, 2, 2, 1) → -27.0
def DotWithDifference(ax, ay, az, bx, by, bz, cx, cy, cz):
    diff_x, diff_y, diff_z = SubtractVectorsXYZ(bx, by, bz, cx, cy, cz)  # Step 1: b⃗ - c⃗
    return DotProductXYZ(ax, ay, az, diff_x, diff_y, diff_z)               # Step 2: a⃗ · (b⃗ - c⃗) → complete

# Formula: a⃗ × (b⃗ + c⃗)
# Cross product of a with the sum of b and c — returns a VECTOR
# Example: CrossWithSum(-1, -4, 2, 2, 2, 1, 3, 3, -2) → vector result
def CrossWithSum(ax, ay, az, bx, by, bz, cx, cy, cz):
    sum_x, sum_y, sum_z = AddVectorsXYZ(bx, by, bz, cx, cy, cz)  # Step 1: b⃗ + c⃗
    return CrossProductXYZ(ax, ay, az, sum_x, sum_y, sum_z)        # Step 2: a⃗ × (b⃗ + c⃗) → complete

# Formula: ||a⃗|| = sqrt(ax² + ay² + az²)
# Magnitude of a 3D vector given as raw components
# Example: MagnitudeXYZ(3, 3, -2) → 4.690
def MagnitudeXYZ(ax, ay, az):
    return (ax**2 + ay**2 + az**2) ** 0.5  # Sum of squares then square root → complete ||a⃗||

# Formula: a⃗_unit = (ax/||a||, ay/||a||, az/||a||)
# Unit vector from raw components — returns (0, 0, 0) if magnitude is zero
# Example: NormalizeXYZ(3, 3, -2) → (0.640, 0.640, -0.427)
def NormalizeXYZ(ax, ay, az):
    mag = MagnitudeXYZ(ax, ay, az)  # Calculate magnitude
    if mag == 0:                     # Guard against zero-vector
        return 0.0, 0.0, 0.0        # Return zero vector safely
    return ax / mag, ay / mag, az / mag  # Divide each component by magnitude → complete unit vector

# ============================================================
# DISPLACEMENT & POSITION FUNCTIONS (COMPONENT FORM)
# ============================================================

# Formula: Δr⃗ = r⃗_f - r⃗_i
# Returns the displacement vector given initial and final position vectors
# Example: DisplacementXYZ(0, 3, -4, -2, 6, -10) → (2.0, -3.0, 6.0)
def DisplacementXYZ(fix, fiy, fiz, ffx, ffy, ffz):
    return ffx - fix, ffy - fiy, ffz - fiz  # Subtract initial from final → complete Δr⃗

# Formula: r⃗_f = r⃗_i + Δr⃗
# Returns the final position vector given initial position and displacement
# Example: FinalPositionXYZ(-2, 6, -10, 2, -3, 6) → (0.0, 3.0, -4.0)
def FinalPositionXYZ(rix, riy, riz, drx, dry, drz):
    return rix + drx, riy + dry, riz + drz  # Add displacement to initial → complete r⃗_f

# Formula: r⃗_i = r⃗_f - Δr⃗
# Returns the initial position vector given final position and displacement
# This is the inverse of FinalPositionXYZ — used when you know where something ended up
# and how far it moved, but not where it started
# Example: InitialPositionXYZ(0, 3, -4, 2, -3, 6) → (-2.0, 6.0, -10.0)
def InitialPositionXYZ(rfx, rfy, rfz, drx, dry, drz):
    return rfx - drx, rfy - dry, rfz - drz  # Subtract displacement from final → complete r⃗_i

# ============================================================
# NEWTON'S SECOND LAW — COMPONENT FORM (3D)
# Forces accepted as lists of (Fx, Fy, Fz) tuples
# Mirrors the 2D section in Physics_2D — extended to three axes
# ============================================================

# Formula: F⃗_net = Σ F⃗_i = (ΣFx)i + (ΣFy)j + (ΣFz)k
# Returns the net force vector (Fx_net, Fy_net, Fz_net) from any number of 3D force vectors
# Accepts a list of (Fx, Fy, Fz) tuples — one tuple per force
# Example: NetForce3D([(3,4,0),(-3,-4,0)]) → (0.0, 0.0, 0.0)
def NetForce3D(forces):
    fx = sum(f[0] for f in forces)  # Sum all X force components → ΣFx
    fy = sum(f[1] for f in forces)  # Sum all Y force components → ΣFy
    fz = sum(f[2] for f in forces)  # Sum all Z force components → ΣFz
    return fx, fy, fz               # Return net force vector → complete F⃗_net

# Formula: a⃗ = F⃗_net / m = (Fx/m)i + (Fy/m)j + (Fz/m)k
# Returns acceleration vector (ax, ay, az) from net force and mass — Newton's 2nd Law
# Returns (0, 0, 0) if mass is zero to avoid division by zero
# Accepts a list of (Fx, Fy, Fz) force tuples
# Example: Acceleration3DFromForces([(3,4,2),(-3,4,0)], 2.0) → (0.0, 4.0, 1.0)
def Acceleration3DFromForces(forces, mass):
    if mass == 0:           # Guard against division by zero — massless object is non-physical
        return 0.0, 0.0, 0.0
    fx, fy, fz = NetForce3D(forces)           # Calculate net force
    return fx / mass, fy / mass, fz / mass    # Divide by mass → complete a⃗ = F/m

# Formula: |a⃗| = sqrt(ax² + ay² + az²)
# Returns the scalar magnitude of the 3D acceleration from Newton's 2nd Law
# Example: AccelerationMagnitude3D([(3,4,0),(3,-4,0)], 2.0) → 3.0 m/s²
def AccelerationMagnitude3D(forces, mass):
    ax, ay, az = Acceleration3DFromForces(forces, mass)  # Get acceleration components
    return (ax**2 + ay**2 + az**2) ** 0.5                # Pythagorean theorem → complete |a⃗|

# Formula: ΣF⃗ = 0  (object at rest or constant velocity)
# Returns the unknown force (Fx, Fy, Fz) needed to maintain 3D equilibrium
# Accepts a list of (Fx, Fy, Fz) known forces
# Example: EquilibriumForce3D([(3,4,1),(2,-1,0)]) → (-5.0, -3.0, -1.0)
def EquilibriumForce3D(known_forces):
    fx, fy, fz = NetForce3D(known_forces)  # Sum all known forces
    return -fx, -fy, -fz                   # Balancing force is the negative of net → complete equilibrium

# Formula: |F⃗_net| = sqrt(Fx² + Fy² + Fz²),  θ = atan2(Fy, Fx),  φ = atan2(Fz, sqrt(Fx²+Fy²))
# Returns (magnitude, theta_degrees, phi_degrees) of the net force in spherical form
# Example: NetForcePolar3D([(3,4,0),(-3,4,0)]) → (8.0, 90.0, 0.0)
def NetForcePolar3D(forces):
    import math
    fx, fy, fz = NetForce3D(forces)
    mag   = (fx**2 + fy**2 + fz**2) ** 0.5
    theta = math.degrees(math.atan2(fy, fx)) % 360         # Azimuth angle 0–360°
    phi   = math.degrees(math.atan2(fz, (fx**2+fy**2)**0.5))  # Elevation angle −90 to +90°
    return mag, theta, phi