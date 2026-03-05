from MathTypes.Basic import BasicMath  # Import BasicMath for basic arithmetic operations
from Config import Checks, RNG         # Import Checks and RNG from Config

# ============================================================
# DISTANCE AND TIME UTILITY FUNCTIONS
# ============================================================

# Formula: d = loc2 - loc1
# Returns the distance between two locations
def GetDistance(loc1, loc2):
    return BasicMath.sub(loc1, loc2)  # Subtract loc1 from loc2 → complete distance d



# Formula: t = t2 - t1
# Returns the elapsed time between two timestamps
def GetTime(t1, t2):
    return BasicMath.sub(t1, t2)  # Subtract t1 from t2 → complete time t

# ============================================================
# VELOCITY FUNCTIONS
# ============================================================

# Formula: v = d / t
# Returns velocity — distance divided by time
# Derives distance or time from locations/timestamps if not provided
def Velocity(distance, time, loc1 = 0, loc2 = 0, t1 = 0, t2 = 0):
    if distance == 0:                       # If distance not provided...
        distance = GetDistance(loc1, loc2)  # Calculate distance from locations → loc2 - loc1

    if time == 0:                           # If time not provided...
        time = GetTime(t1, t2)              # Calculate time from timestamps → t2 - t1

    return distance / time                  # Divide distance by time → complete v = d/t



# Formula: v = v0 + a*t
# Returns final velocity — initial velocity plus acceleration multiplied by time
# Derives distance, time, or initial velocity if not provided
def FinalVelocity(a, distance, time, v0, loc1 = 0, loc2 = 0, t1 = 0, t2 = 0):
    if distance == 0:                       # If distance not provided...
        distance = GetDistance(loc1, loc2)  # Calculate distance from locations → loc2 - loc1

    if time == 0:                           # If time not provided...
        time = GetTime(t1, t2)              # Calculate time from timestamps → t2 - t1

    if v0 == 0:                             # If initial velocity not provided...
        v0 = Velocity(distance, time, loc1, loc2, t1, t2)  # Calculate initial velocity → d / t

    return (a * time) + v0                  # Multiply acceleration by time then add initial velocity → complete v = v0 + a*t



# Formula: v² = v0² + 2*a*(x - x0)
# Returns final velocity squared — used when time is unknown but position is known
# Derives distance, time, initial velocity, initial position, or position if not provided
def FinalVelocitySquared(ca, distance, time, v0, x, x0, loc1 = 0, loc2 = 0, t1 = 0, t2 = 0):
    if distance == 0:                       # If distance not provided...
        distance = GetDistance(loc1, loc2)  # Calculate distance from locations → loc2 - loc1

    if time == 0:                           # If time not provided...
        time = GetTime(t1, t2)              # Calculate time from timestamps → t2 - t1

    if v0 == 0:                             # If initial velocity not provided...
        v0 = Velocity(distance, time, loc1, loc2, t1, t2)  # Calculate initial velocity → d / t

    if x0 == 0:                             # If initial position not provided...
        x0 = GetPosition(ca, time, v0, 0, distance, loc1, loc2, t1, t2)  # Calculate initial position using x0 = 0 as starting reference

    if x == 0:                              # If current position not provided...
        x = GetPosition(ca, time, v0, x0, distance, loc1, loc2, t1, t2)  # Calculate current position from initial position

    return (v0 ** 2) + 2 * ca * (x - x0)   # Square initial velocity, add 2 * acceleration * displacement → complete v² = v0² + 2a(x-x0)

# ============================================================
# ACCELERATION FUNCTIONS
# ============================================================

# Formula: a = (v2 - v1) / t
# Returns average acceleration — change in velocity divided by time
# Derives distances, time, or velocities from locations/timestamps if not provided
def Acceleration(v1, v2, time = 1, d1 = 1, d2 = 1, loc1 = 0, loc2 = 0, loc3 = 0, loc4 = 0, t1 = 0, t2 = 0):
    if d1 == 0:                             # If initial distance not provided...
        d1 = GetDistance(loc1, loc2)        # Calculate initial distance → loc2 - loc1

    if d2 == 0:                             # If final distance not provided...
        d2 = GetDistance(loc3, loc4)        # Calculate final distance → loc4 - loc3

    if time == 0:                           # If time not provided...
        time = GetTime(t1, t2)              # Calculate time from timestamps → t2 - t1
  
    if v1 == 0:                             # If initial velocity not provided...
        v1 = Velocity(d1, time, loc1, loc2, t1, t2)   # Calculate initial velocity → d1 / time

    if v2 == 0:                             # If final velocity not provided...
        v2 = Velocity(d2, time, loc3, loc4, t1, t2)   # Calculate final velocity → d2 / time

    vd = v2 - v1                            # Subtract initial velocity from final velocity → velocity difference

    return vd / time                        # Divide velocity difference by time → complete a = (v2-v1)/t



# Formula: a = (v2 - v1) / t  (called over a very small time interval)
# Returns instantaneous acceleration — same formula as Acceleration
# The distinction between average and instantaneous is in how small the time interval passed in is
def InstantAcceleration(v1, v2, time, d1 = 1, d2 = 1, loc1 = 0, loc2 = 0, loc3 = 0, loc4 = 0, t1 = 0, t2 = 0):
    if d1 == 0:                             # If initial distance not provided...
        d1 = GetDistance(loc1, loc2)        # Calculate initial distance → loc2 - loc1

    if d2 == 0:                             # If final distance not provided...
        d2 = GetDistance(loc3, loc4)        # Calculate final distance → loc4 - loc3

    if time == 0:                           # If time not provided...
        time = GetTime(t1, t2)              # Calculate time from timestamps → t2 - t1
  
    if v1 == 0:                             # If initial velocity not provided...
        v1 = Velocity(d1, time, loc1, loc2, t1, t2)   # Calculate initial velocity → d1 / time

    if v2 == 0:                             # If final velocity not provided...
        v2 = Velocity(d2, time, loc3, loc4, t1, t2)   # Calculate final velocity → d2 / time

    vd = v2 - v1                            # Subtract initial velocity from final velocity → velocity difference

    return vd / time                        # Divide velocity difference by time → complete a = (v2-v1)/t



# Formula: a = (v2 - v1) / t  (acceleration is assumed constant throughout)
# Returns constant acceleration — same formula but used when acceleration does not change over time
# Verification of constancy is the caller's responsibility
def ConstantAcceleration(v1, v2, time, d1 = 1, d2 = 1, loc1 = 0, loc2 = 0, loc3 = 0, loc4 = 0, t1 = 0, t2 = 0):
    if d1 == 0:                             # If initial distance not provided...
        d1 = GetDistance(loc1, loc2)        # Calculate initial distance → loc2 - loc1

    if d2 == 0:                             # If final distance not provided...
        d2 = GetDistance(loc3, loc4)        # Calculate final distance → loc4 - loc3

    if time == 0:                           # If time not provided...
        time = GetTime(t1, t2)              # Calculate time from timestamps → t2 - t1
  
    if v1 == 0:                             # If initial velocity not provided...
        v1 = Velocity(d1, time, loc1, loc2, t1, t2)   # Calculate initial velocity → d1 / time

    if v2 == 0:                             # If final velocity not provided...
        v2 = Velocity(d2, time, loc3, loc4, t1, t2)   # Calculate final velocity → d2 / time

    vd = v2 - v1                            # Subtract initial velocity from final velocity → velocity difference

    return vd / time                        # Divide velocity difference by time → complete a = (v2-v1)/t

# ============================================================
# DISPLACEMENT AND POSITION FUNCTIONS
# ============================================================

# Formula: Δx = v0*t + ½*a*t²
# Returns displacement — how far the object has moved from its starting point
# Derives distance, time, initial velocity, or acceleration if not provided
def GetDisplacement(a, time, v0, distance = 1, loc1 = 0, loc2 = 0, t1 = 0, t2 = 0):
    if distance == 0:                       # If distance not provided...
        distance = GetDistance(loc1, loc2)  # Calculate distance from locations → loc2 - loc1

    if time == 0:                           # If time not provided...
        time = GetTime(t1, t2)              # Calculate time from timestamps → t2 - t1

    if v0 == 0:                             # If initial velocity not provided...
        v0 = Velocity(distance, time, loc1, loc2, t1, t2)  # Calculate initial velocity → d / t

    if a == 0:                              # If acceleration not provided...
        a = Acceleration(v0, 0, time, distance, 0, loc1, loc2, 0, 0, t1, t2)  # Calculate acceleration from v0 to rest
    
    return (0.5 * a * time ** 2) + (v0 * time)  # Calculate ½at² then add v0*t → complete Δx = v0*t + ½at²



# Formula: x = x0 + v0*t + ½*a*t²
# Returns absolute position — displacement added onto the initial position
# Derives distance, time, initial velocity, or constant acceleration if not provided
def GetPosition(ca, time, v0, x0, distance = 1, loc1 = 0, loc2 = 0, t1 = 0, t2 = 0):
    if distance == 0:                       # If distance not provided...
        distance = GetDistance(loc1, loc2)  # Calculate distance from locations → loc2 - loc1

    if time == 0:                           # If time not provided...
        time = GetTime(t1, t2)              # Calculate time from timestamps → t2 - t1

    if v0 == 0:                             # If initial velocity not provided...
        v0 = Velocity(distance, time, loc1, loc2, t1, t2)  # Calculate initial velocity → d / t

    if ca == 0:                             # If constant acceleration not provided...
        ca = ConstantAcceleration(v0, 0, time, distance, 0, loc1, loc2, 0, 0, t1, t2)  # Calculate constant acceleration from v0 to rest
    
    return (0.5 * ca * time ** 2) + (v0 * time) + x0  # Calculate ½at² + v0*t then add initial position → complete x = x0 + v0*t + ½at²

# ============================================================
# FREE FALL FUNCTIONS
# ============================================================

# Formula: h = h0 + v0*t - ½*g*t²
# Returns height of a falling object at time t
# g is negated because gravity acts downward opposing positive height
# Pass different g values for other planets e.g. Moon = 1.62, Mars = 3.72
# Derives distance, time, or initial velocity if not provided
def FreeFallPosition(g, time, v0, h0, distance = 1, loc1 = 0, loc2 = 0, t1 = 0, t2 = 0):
    if distance == 0:                       # If distance not provided...
        distance = GetDistance(loc1, loc2)  # Calculate distance from locations → loc2 - loc1

    if time == 0:                           # If time not provided...
        time = GetTime(t1, t2)              # Calculate time from timestamps → t2 - t1

    if v0 == 0:                             # If initial velocity not provided...
        v0 = Velocity(distance, time, loc1, loc2, t1, t2)  # Calculate initial velocity → d / t
    
    return 0.5 * (-g) * (time ** 2) + (v0 * time) + h0  # Negate g for downward gravity, calculate ½(-g)t² + v0*t + h0 → complete h = h0 + v0*t - ½gt²