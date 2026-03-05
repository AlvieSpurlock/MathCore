from MathTypes.Basic import BasicMath  # Import BasicMath for Cosine and Sine functions
from Config import Checks, RNG         # Import Checks and RNG from Config
import math                            # Import math for sqrt
from MathTypes.Physics import Physics_1D  # Import Physics_1D for 1D physics fallback calculations

# ============================================================
# VECTOR COMPONENT FUNCTIONS
# ============================================================

# Formula: i = a * cos(angle)
# The horizontal (X) component of a 2D vector using magnitude and angle
def IHat(a, angle, isDegrees = True):
    return a * BasicMath.Cosine(angle, isDegrees)  # Multiply magnitude by cosine of angle → complete i component

# Formula: j = a * sin(angle)
# The vertical (Y) component of a 2D vector using magnitude and angle
def JHat(a, angle, isDegrees = True):
    return a * BasicMath.Sine(angle, isDegrees)  # Multiply magnitude by sine of angle → complete j component

# Formula: a⃗ = a_x*i + a_y*j
# Returns both 2D vector components as a tuple (i, j)
def IJ(a, angle, isDegrees = True):
    i = IHat(a, angle, isDegrees)  # Calculate i (X) component → a * cos(angle)
    j = JHat(a, angle, isDegrees)  # Calculate j (Y) component → a * sin(angle)
    return i, j  # Return both components as a tuple → complete vector a⃗

# Formula: vx = a * cos(angle)
# Horizontal velocity component — identical to IHat but named for velocity context
def VX(a, angle, isDegrees = True):
    return a * BasicMath.Cosine(angle, isDegrees)  # Multiply magnitude by cosine of angle → complete vx

# Formula: vy = a * sin(angle)
# Vertical velocity component — identical to JHat but named for velocity context
def VY(a, angle, isDegrees = True):
    return a * BasicMath.Sine(angle, isDegrees)  # Multiply magnitude by sine of angle → complete vy

# ============================================================
# VECTOR ANGLE FUNCTIONS
# ============================================================

# Formula: tan(θ) = ay / ax
# Returns the tangent of the angle of a 2D vector from its components
# Returns 0 if ax = 0 to avoid division by zero (angle would be 90°)
def TanTheta(a, angle, isDegrees = True):
    ax = IHat(a, angle, isDegrees)  # Calculate horizontal component ax = a * cos(angle)
    ay = JHat(a, angle, isDegrees)  # Calculate vertical component ay = a * sin(angle)
    if ax == 0:   # Guard against division by zero — tan(90°) is undefined
        return 0  # Return 0 safely — cannot divide by zero
    return ay / ax  # Divide ay by ax → complete tan(θ)

# Formula: a⃗ = a_x*i + a_y*j
# Returns the 2D vector components (ax, ay) — alias for IJ with clearer name
def VectorAngle(a, angle, isDegrees = True):
    return IJ(a, angle, isDegrees)  # Delegate to IJ → returns (i, j) tuple

# Formula: θ = atan2(ay, ax)
# Returns the angle of a 2D vector in degrees measured from the positive X axis
def VectorAngle2D(ax, ay):
    return math.degrees(math.atan2(ay, ax))  # atan2 handles all quadrants correctly → complete θ

# ============================================================
# VECTOR MAGNITUDE FUNCTIONS
# ============================================================

# Formula: ||a|| = sqrt(ax² + ay²)
# Returns the scalar magnitude of a 2D vector
def VectorMagnitude(a, angle, isDegrees = True):
    ax = IHat(a, angle, isDegrees)  # Calculate ax = a * cos(angle) → X component
    ay = JHat(a, angle, isDegrees)  # Calculate ay = a * sin(angle) → Y component
    return math.sqrt((ax ** 2) + (ay ** 2))  # Sum squares and take sqrt → complete ||a||

# ============================================================
# VECTOR ARITHMETIC
# ============================================================

# Formula: a⃗ + b⃗ = (ax+bx)i + (ay+by)j
# Adds two 2D vectors by summing their components individually
def AddVectors(a, angle_a, b, angle_b, isDegrees = True):
    ax, ay = IJ(a, angle_a, isDegrees)  # Decompose vector a into components (ax, ay)
    bx, by = IJ(b, angle_b, isDegrees)  # Decompose vector b into components (bx, by)
    rx = ax + bx  # Add X components → (ax+bx)i
    ry = ay + by  # Add Y components → (ay+by)j
    return rx, ry  # Return result vector tuple → complete a⃗ + b⃗

# Formula: a⃗ - b⃗ = (ax-bx)i + (ay-by)j
# Subtracts two 2D vectors by subtracting their components individually
def SubtractVectors(a, angle_a, b, angle_b, isDegrees = True):
    ax, ay = IJ(a, angle_a, isDegrees)  # Decompose vector a into components (ax, ay)
    bx, by = IJ(b, angle_b, isDegrees)  # Decompose vector b into components (bx, by)
    rx = ax - bx  # Subtract X components → (ax-bx)i
    ry = ay - by  # Subtract Y components → (ay-by)j
    return rx, ry  # Return result vector tuple → complete a⃗ - b⃗

# ============================================================
# DOT AND CROSS PRODUCTS
# ============================================================

# Formula: a⃗ · b⃗ = (ax*bx) + (ay*by)
# Returns a SCALAR — multiply matching components and sum them
def DotProduct(a, angle_a, b, angle_b, isDegrees = True):
    ax, ay = IJ(a, angle_a, isDegrees)  # Decompose vector a into components (ax, ay)
    bx, by = IJ(b, angle_b, isDegrees)  # Decompose vector b into components (bx, by)
    return (ax * bx) + (ay * by)  # Multiply matching components and sum → complete a⃗ · b⃗

# Formula: a⃗ × b⃗ = (ax*by) - (ay*bx)
# In 2D cross product returns a SCALAR (the Z component of the 3D cross product)
# Represents the signed area of the parallelogram formed by the two vectors
# Positive = counterclockwise, Negative = clockwise
# NOTE: Not commutative — a × b = -(b × a)
def CrossProduct(a, angle_a, b, angle_b, isDegrees = True):
    ax, ay = IJ(a, angle_a, isDegrees)  # Decompose vector a into components (ax, ay)
    bx, by = IJ(b, angle_b, isDegrees)  # Decompose vector b into components (bx, by)
    return (ax * by) - (ay * bx)  # Calculate scalar cross product → complete a⃗ × b⃗

# Formula: cos(θ) = (a⃗ · b⃗) / (||a|| * ||b||)
# Returns cos(θ) — useful for finding the angle between two 2D vectors
# Returns 0 if either magnitude is zero to avoid division by zero
def DotProductMagnitude(a, angle_a, b, angle_b, isDegrees = True):
    mag_a = VectorMagnitude(a, angle_a, isDegrees)              # Calculate magnitude of vector a → ||a||
    mag_b = VectorMagnitude(b, angle_b, isDegrees)              # Calculate magnitude of vector b → ||b||
    dot = DotProduct(a, angle_a, b, angle_b, isDegrees)         # Calculate dot product → a⃗ · b⃗
    if mag_a == 0 or mag_b == 0:  # Guard against division by zero — zero magnitude vector has no direction
        return 0                   # Return 0 safely — cannot divide by zero magnitude
    return dot / (mag_a * mag_b)  # Divide dot product by product of magnitudes → complete cos(θ)

# Formula: ||a⃗ × b⃗|| = |ax*by - ay*bx|
# Returns the absolute scalar magnitude of the 2D cross product
# Equals the area of the parallelogram formed by the two vectors
def CrossProductMagnitude(a, angle_a, b, angle_b, isDegrees = True):
    cross = CrossProduct(a, angle_a, b, angle_b, isDegrees)  # Calculate scalar cross product
    return abs(cross)  # Take absolute value → complete ||a⃗ × b⃗||

# ============================================================
# SCALAR OPERATIONS
# ============================================================

# Formula: a⃗ × c = (ax*c)i + (ay*c)j
# Multiplies each 2D vector component by a scalar
# Positive scalar = same direction, Negative scalar = opposite direction
def ScalarMultiply(c, a, angle, isDegrees = True):
    ax, ay = IJ(a, angle, isDegrees)  # Decompose vector into components (ax, ay)
    return ax * c, ay * c  # Multiply each component by scalar c → complete a⃗ × c

# Formula: a⃗ / c = (ax/c)i + (ay/c)j
# Divides each 2D vector component by a scalar
# Returns (0, 0) if scalar is zero to avoid division by zero
def ScalarDivide(c, a, angle, isDegrees = True):
    if c == 0:      # Guard against division by zero — cannot divide by zero scalar
        return 0, 0  # Return zero vector safely
    ax, ay = IJ(a, angle, isDegrees)  # Decompose vector into components (ax, ay)
    rx = ax / c  # Divide X component by scalar → (ax/c)i
    ry = ay / c  # Divide Y component by scalar → (ay/c)j
    return rx, ry  # Return scaled vector tuple → complete a⃗ / c

# ============================================================
# ADVANCED VECTOR OPERATIONS
# ============================================================

# Formula: a⃗_unit = a⃗ / ||a⃗|| = (ax/||a||, ay/||a||)
# Returns a unit vector (magnitude = 1) pointing in the same direction
# Returns (0, 0) if magnitude is zero — zero vector has no direction to normalize
def NormalizeVector(a, angle, isDegrees = True):
    ax, ay = IJ(a, angle, isDegrees)          # Decompose vector into components (ax, ay)
    mag = VectorMagnitude(a, angle, isDegrees) # Calculate magnitude ||a|| for normalization
    if mag == 0:    # Guard against division by zero — zero vector cannot be normalized
        return 0, 0  # Return zero vector safely
    return ax / mag, ay / mag  # Divide each component by magnitude → complete unit vector

# Formula: proj_b(a) = (a⃗ · b⃗) / ||b⃗||
# Returns the scalar projection of vector a onto vector b
# Returns 0 if magnitude of b is zero to avoid division by zero
def VectorProjection(a, angle_a, b, angle_b, isDegrees = True):
    dot = DotProduct(a, angle_a, b, angle_b, isDegrees)  # Calculate dot product a⃗ · b⃗
    mag = VectorMagnitude(b, angle_b, isDegrees)          # Calculate magnitude ||b⃗||
    if mag == 0:  # Guard against division by zero — cannot project onto zero vector
        return 0  # Return 0 safely
    return dot / mag  # Divide dot product by magnitude of b → complete projection

# ============================================================
# 2D MOTION FUNCTIONS
# ============================================================

# Formula: r⃗ = rx*i + ry*j
# Returns the 2D position vector
# Derives any missing component from angle if not provided
def Position2D(rx = 0, ry = 0, a = 0, angle = 0, isDegrees = True):
    if rx == 0:                          # If X position not provided...
        rx = IHat(a, angle, isDegrees)   # Derive X position from magnitude and angle → a * cos(angle)
    if ry == 0:                          # If Y position not provided...
        ry = JHat(a, angle, isDegrees)   # Derive Y position from magnitude and angle → a * sin(angle)
    return rx, ry  # Return position vector tuple → complete r⃗

# Formula: v⃗ = (drx/dt)*i + (dry/dt)*j = vx*i + vy*j
# Returns the 2D velocity vector
# Derives any missing velocity or distance from provided locations and time
def Velocity2D(angle, time, vx = 0, vy = 0, dx = 1, dy = 1, loc1 = 0, loc2 = 0, loc3 = 0, loc4 = 0, t1 = 0, t2 = 0, isDegrees = True):
    if dx == 0:                                  # If X distance not provided...
        dx = Physics_1D.GetDistance(loc1, loc2)  # Calculate X distance from X locations → loc2 - loc1
    if dy == 0:                                  # If Y distance not provided...
        dy = Physics_1D.GetDistance(loc3, loc4)  # Calculate Y distance from Y locations → loc4 - loc3
    if time == 0:                                # If time not provided...
        time = Physics_1D.GetTime(t1, t2)        # Calculate time from timestamps → t2 - t1
    if vx == 0:                                  # If X velocity not provided...
        vx = Physics_1D.Velocity(dx, time)       # Calculate X velocity → dx / time
    if vy == 0:                                  # If Y velocity not provided...
        vy = Physics_1D.Velocity(dy, time)       # Calculate Y velocity → dy / time
    rx = IHat(vx, angle, isDegrees)              # Apply angle to X velocity → vx * cos(angle) → vx*i
    ry = JHat(vy, angle, isDegrees)              # Apply angle to Y velocity → vy * sin(angle) → vy*j
    return rx, ry  # Return velocity vector tuple → complete v⃗

# Formula: a⃗ = (dvx/dt)*i + (dvy/dt)*j = ax*i + ay*j
# Returns the 2D acceleration vector
# Uses separate initial (dx1) and final (dx2) distances per axis to avoid equal velocities
def Acceleration2D(angle, time, v1x = 0, v1y = 0, v2x = 0, v2y = 0, dx1 = 1, dy1 = 1, dx2 = 1, dy2 = 1, loc1 = 0, loc2 = 0, loc3 = 0, loc4 = 0, loc5 = 0, loc6 = 0, loc7 = 0, loc8 = 0, t1 = 0, t2 = 0, isDegrees = True):
    if dx1 == 0:                                   # If initial X distance not provided...
        dx1 = Physics_1D.GetDistance(loc1, loc2)   # Calculate initial X distance → loc2 - loc1
    if dy1 == 0:                                   # If initial Y distance not provided...
        dy1 = Physics_1D.GetDistance(loc3, loc4)   # Calculate initial Y distance → loc4 - loc3
    if dx2 == 0:                                   # If final X distance not provided...
        dx2 = Physics_1D.GetDistance(loc5, loc6)   # Calculate final X distance → loc6 - loc5
    if dy2 == 0:                                   # If final Y distance not provided...
        dy2 = Physics_1D.GetDistance(loc7, loc8)   # Calculate final Y distance → loc8 - loc7
    if time == 0:                                  # If time not provided...
        time = Physics_1D.GetTime(t1, t2)          # Calculate time from timestamps → t2 - t1
    if v1x == 0:                                   # If initial X velocity not provided...
        v1x = Physics_1D.Velocity(dx1, time)       # Calculate initial X velocity → dx1 / time
    if v1y == 0:                                   # If initial Y velocity not provided...
        v1y = Physics_1D.Velocity(dy1, time)       # Calculate initial Y velocity → dy1 / time
    if v2x == 0:                                   # If final X velocity not provided...
        v2x = Physics_1D.Velocity(dx2, time)       # Calculate final X velocity → dx2 / time
    if v2y == 0:                                   # If final Y velocity not provided...
        v2y = Physics_1D.Velocity(dy2, time)       # Calculate final Y velocity → dy2 / time
    ax = Physics_1D.Acceleration(v1x, v2x, time)  # Calculate X acceleration → (v2x - v1x) / time → ax complete
    ay = Physics_1D.Acceleration(v1y, v2y, time)  # Calculate Y acceleration → (v2y - v1y) / time → ay complete
    rx = IHat(ax, angle, isDegrees)                # Apply angle to X acceleration → ax * cos(angle) → ax*i
    ry = JHat(ay, angle, isDegrees)                # Apply angle to Y acceleration → ay * sin(angle) → ay*j
    return rx, ry  # Return acceleration vector tuple → complete a⃗

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