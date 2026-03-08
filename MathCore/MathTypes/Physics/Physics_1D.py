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

# ============================================================
# INVERSE SOLVERS — SOLVING FOR TIME, DISTANCE, OR SPEED
# ============================================================

# Formula: t = d / v
# Returns the time it takes to travel a distance at a given constant speed
# This is the inverse of Velocity — solves for t instead of v
# Returns 0 if speed is zero to avoid division by zero
# Example: SolveForTime(200, 30.73) → 6.509 s
def SolveForTime(distance, speed):
    if speed == 0:                                              # Guard against division by zero
        return 0                                                # Return 0 safely — undefined travel time
    return distance / speed                                     # Divide distance by speed → complete t = d/v

# Formula: d = v * t
# Returns the distance traveled at a constant speed over a given time
# This is the inverse of Velocity — solves for d instead of v
# Example: SolveForDistance(30.73, 6.509) → 200 m
def SolveForDistance(speed, time):
    return speed * time                                         # Multiply speed by time → complete d = v*t

# Formula: v_new = v_base + delta_v
# Returns a new speed given a base speed and a signed velocity difference
# Useful when one competitor beats another by a known speed margin
# Positive delta_v means faster — negative means slower
# Example: SpeedWithDelta(30.73, 5.28) → 36.01 m/s  (Whittingham's speed)
def SpeedWithDelta(v_base, delta_v):
    return v_base + delta_v                                     # Add velocity delta to base speed → complete v_new = v_base + Δv

# Formula: t = d / (v_base + delta_v)
# Returns the time through a distance for a competitor who beats a base speed by delta_v
# Combines SpeedWithDelta and SolveForTime in one call
# Returns 0 if the resulting speed is zero to avoid division by zero
# Example: TimeWithSpeedDelta(200, 30.73, 5.28) → 5.554 s  (Whittingham's time)
def TimeWithSpeedDelta(distance, v_base, delta_v):
    new_speed = SpeedWithDelta(v_base, delta_v)                 # Calculate the new speed first → v_base + delta_v
    return SolveForTime(distance, new_speed)                    # Solve for time at the new speed → complete t = d/v_new

# ============================================================
# TEMPORAL VELOCITY SOLVERS — FORWARD AND BACKWARD IN TIME
# ============================================================

# Formula: v_after = v_now + a * dt
# Returns the velocity at a time dt AFTER a known instant
# Standard forward application of constant acceleration
# Example: VelocityAfter(55, 14.3, 2.5) → 90.75 m/s
def VelocityAfter(v_now, a, dt):
    return v_now + a * dt                                       # Add acceleration times time to current velocity → complete v = v₀ + at

# Formula: v_before = v_now - a * dt
# Returns the velocity at a time dt BEFORE a known instant
# Reverses the acceleration — useful when you know current state and want the earlier state
# Example: VelocityBefore(55, 14.3, 2.5) → 19.25 m/s  (rocket 2.5s earlier)
def VelocityBefore(v_now, a, dt):
    return v_now - a * dt                                       # Subtract acceleration times time → complete v_before = v_now - a*dt

# Formula: dt = (v_final - v_initial) / a
# Returns the time elapsed between two known velocities under constant acceleration
# Returns 0 if acceleration is zero to avoid division by zero
# Example: TimeBetweenVelocities(19.25, 55, 14.3) → 2.5 s
def TimeBetweenVelocities(v_initial, v_final, a):
    if a == 0:                                                  # Guard against division by zero
        return 0                                                # Return 0 safely — no acceleration means no change
    return (v_final - v_initial) / a                            # Divide velocity change by acceleration → complete dt = Δv/a

# Formula: v_at_t = v_ref + a * (t_target - t_ref)
# Returns the velocity at any target time given a reference velocity at a known reference time
# Works both forward and backward — sign of (t_target - t_ref) determines direction
# Example: VelocityAtTime(55, 10.0, 14.3, 7.5) → 19.25 m/s  (velocity at t=7.5 when v=55 at t=10)
def VelocityAtTime(v_ref, t_ref, a, t_target):
    dt = t_target - t_ref                                       # Signed time difference — negative means going backward
    return v_ref + a * dt                                       # Apply acceleration over signed dt → complete v = v_ref + a*(t_target - t_ref)

# Formula: x_before = x_now - v_now * dt + ½ * a * dt²
# Returns the position at a time dt BEFORE the current instant
# Works by reversing the kinematic position equation
# Example: PositionBefore(0, 55, 14.3, 2.5) → -116.5625 m  (position 2.5s earlier relative to current)
def PositionBefore(x_now, v_now, a, dt):
    return x_now - v_now * dt + 0.5 * a * dt ** 2              # Subtract displacement traveled in dt → complete x_before

# ============================================================
# DECELERATION SOLVERS — STOPPING FROM A KNOWN SPEED
# ============================================================

# Formula: t_stop = v0 / |a|
# Returns the time it takes for an object to come to a complete stop
# from an initial velocity v0 under a constant deceleration
# Pass deceleration as a positive magnitude — the sign is handled internally
# Returns 0 if deceleration is zero to avoid division by zero
# Example: StoppingTime(24.6, 4.92) → 5.0 s
def StoppingTime(v0, deceleration):
    if deceleration == 0:                                       # Guard against division by zero
        return 0                                                # Return 0 safely — object never stops
    return abs(v0) / abs(deceleration)                          # Divide speed by deceleration magnitude → complete t = v0 / |a|

# Formula: Δx = v0² / (2 * |a|)
# Returns the total distance an object travels before coming to a complete stop
# from an initial velocity v0 under a constant deceleration
# Derived from v² = v0² + 2aΔx with v_final = 0
# Pass deceleration as a positive magnitude — the sign is handled internally
# Returns 0 if deceleration is zero to avoid division by zero
# Example: StoppingDistance(24.6, 4.92) → 61.5 m
def StoppingDistance(v0, deceleration):
    if deceleration == 0:                                       # Guard against division by zero
        return 0                                                # Return 0 safely — object never stops
    return (v0 ** 2) / (2 * abs(deceleration))                  # Square v0 and divide by twice deceleration → complete Δx = v0²/2|a|

# Formula: v_at_t = v0 - |a| * t  (during braking — velocity decreasing toward zero)
# Returns the velocity of a decelerating object at a given time t after braking begins
# Clamps the result to zero — the object does not reverse direction when braking to a stop
# Returns 0 if t is at or beyond the stopping time
# Example: VelocityWhileStopping(24.6, 4.92, 2.0) → 14.76 m/s
def VelocityWhileStopping(v0, deceleration, t):
    v = v0 - abs(deceleration) * t                              # Subtract deceleration times time from initial speed
    return max(v, 0)                                            # Clamp to zero — object stops, does not reverse → complete

# Formula: x = v0*t - ½*|a|*t²  (position during braking from x=0 start)
# Returns the position of a decelerating object at time t measured from where braking began
# Clamps to stopping distance — position does not decrease after the object stops
# Example: PositionWhileStopping(24.6, 4.92, 3.0) → 51.66 m
def PositionWhileStopping(v0, deceleration, t):
    t_stop = StoppingTime(v0, deceleration)                     # Find the time when the object fully stops
    t      = min(t, t_stop)                                     # Clamp time — object stays put after stopping
    return v0 * t - 0.5 * abs(deceleration) * t ** 2           # Apply kinematic position equation → complete x = v0*t - ½|a|t²

# ============================================================
# FREE FALL INVERSE SOLVERS — HEIGHT AND TIME FROM FINAL VELOCITY
# ============================================================

# Formula: h = (v_final² - v0²) / (2 * g)
# Returns the height an object fell from given its impact velocity and initial vertical velocity
# v0 is zero for objects dropped from rest — pass a non-zero v0 for thrown objects
# g defaults to 9.8 m/s² — pass Moon = 1.62, Mars = 3.72 for other planets
# Returns 0 if g is zero to avoid division by zero
# Example: HeightFromFinalVelocity(24, 9.8) → 29.4 m
def HeightFromFinalVelocity(v_final, g = 9.8, v0 = 0):
    if g == 0:                                                  # Guard against division by zero
        return 0                                                # Return 0 safely — undefined without gravity
    return (v_final ** 2 - v0 ** 2) / (2 * g)                  # Rearrange v² = v0² + 2gh → complete h = (v²-v0²)/(2g)

# Formula: t = (v_final - v0) / g
# Returns the duration of free fall given a final impact velocity and initial vertical velocity
# v0 is zero for objects dropped from rest — pass a non-zero v0 for thrown objects
# g defaults to 9.8 m/s² — pass Moon = 1.62, Mars = 3.72 for other planets
# Returns 0 if g is zero to avoid division by zero
# Example: FreeFallTime(24, 9.8) → 2.449 s
def FreeFallTime(v_final, g = 9.8, v0 = 0):
    if g == 0:                                                  # Guard against division by zero
        return 0                                                # Return 0 safely — undefined without gravity
    return (v_final - v0) / g                                   # Divide velocity gained by gravitational rate → complete t = (v-v0)/g

# Formula: v_final = sqrt(v0² + 2*g*h)
# Returns the impact velocity of an object that fell from a given height
# v0 is zero for objects dropped from rest — pass a non-zero v0 for thrown objects
# g defaults to 9.8 m/s²
# Returns 0 if the expression under the square root is negative — physically impossible inputs
# Example: ImpactVelocity(29.4, 9.8) → 24.0 m/s
def ImpactVelocity(h, g = 9.8, v0 = 0):
    under_root = v0 ** 2 + 2 * g * h                           # Compute v0² + 2gh
    if under_root < 0:                                          # Guard against square root of negative — invalid scenario
        return 0                                                # Return 0 safely
    return under_root ** 0.5                                    # Square root → complete v = sqrt(v0² + 2gh)

# Formula: h = v0*t - ½*g*t²  solved for max height where v = 0 → h_max = v0² / (2g)
# Returns the maximum height reached by an object thrown straight upward
# v0 is the initial upward velocity
# g defaults to 9.8 m/s²
# Returns 0 if g is zero to avoid division by zero
# Example: MaxHeightFromLaunch(24, 9.8) → 29.4 m
def MaxHeightFromLaunch(v0, g = 9.8):
    if g == 0:                                                  # Guard against division by zero
        return 0                                                # Return 0 safely
    return (v0 ** 2) / (2 * g)                                  # Square initial speed and divide by 2g → complete h_max = v0²/(2g)

# Formula: t_up = v0 / g
# Returns the time for a vertically launched object to reach its peak (where v = 0)
# g defaults to 9.8 m/s²
# Returns 0 if g is zero to avoid division by zero
# Example: TimeToMaxHeight(24, 9.8) → 2.449 s
def TimeToMaxHeight(v0, g = 9.8):
    if g == 0:                                                  # Guard against division by zero
        return 0                                                # Return 0 safely
    return v0 / g                                               # Divide initial speed by g → complete t = v0/g

# Formula: t = (-v0 + sqrt(v0² + 2*g*h)) / g
# Returns the time for an object to fall a known height under gravity
# Solves the kinematic equation h = v0*t + ½*g*t² for t using the quadratic formula
# v0 is zero for objects dropped from rest — pass a positive v0 for objects thrown downward
# g defaults to 9.8 m/s²
# Returns 0 if g is zero or if the discriminant is negative — physically impossible inputs
# Example: FreeFallTimeFromHeight(86.44, 9.8, 0) → 4.200 s    (package dropped from 86.44 m)
# Example: FreeFallTimeFromHeight(86.44, 9.8, 5) → 3.807 s    (thrown downward at 5 m/s)
def FreeFallTimeFromHeight(h, g = 9.8, v0 = 0):
    if g == 0:                                                  # Guard against division by zero
        return 0                                                # Return 0 safely — undefined without gravity
    discriminant = v0 ** 2 + 2 * g * h                         # Compute the expression under the square root: v0² + 2gh
    if discriminant < 0:                                        # Guard against square root of negative — invalid scenario
        return 0                                                # Return 0 safely
    return (-v0 + discriminant ** 0.5) / g                     # Quadratic formula positive root → t = (-v0 + sqrt(v0²+2gh)) / g