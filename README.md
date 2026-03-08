# MathCore

MathCore is a modular mathematical and physics computation library for Python. It provides a clean, readable API covering arithmetic, 1D/2D/3D kinematics, vector operations, projectile motion, and a full force physics system — all without external dependencies.

Every function is documented, guarded against invalid input, and returns clean values ready for use in scripts, simulations, CLI tools, or as a backend engine for larger applications.

---

## Overview

MathCore is organized into focused modules that build on each other by prerequisite:

| Module | What It Covers |
|--------|---------------|
| `BasicMath` | Arithmetic — add, subtract, multiply, divide, modulo, even check, random int |
| `Physics_1D` | 1D kinematics — distance, velocity, acceleration, displacement, position |
| `Physics_2D` | 2D vectors and projectile motion with and without air resistance |
| `Physics_3D` | 3D vectors and projectile motion with and without air resistance |
| `Forces` | Force objects, force systems, energy, momentum, equilibrium, drag, terminal velocity |

---

## Why MathCore?

Python has arithmetic operators, but MathCore solves a different problem: **a reusable, well-structured math and physics backend** that you can import into any project.

MathCore provides:

- Multi-argument arithmetic functions with a consistent API
- Full 2D and 3D vector operation suites
- Projectile motion with realistic drag calculations
- A complete force physics system with object-level properties
- Division-by-zero guards and domain validation throughout
- An interactive Debug UI for every module
- No classes to instantiate for math functions — just clean callable functions
- Force objects (`Force2D`, `Force3D`) and force systems (`Forces2D`, `Forces3D`) where objects are appropriate

---

## Module Reference

### BasicMath

Simple arithmetic functions that accept a starting value and any number of additional values.

```python
from MathTypes.Basic import BasicMath
from Config import Checks, RNG

BasicMath.add(10, 2, 3, 4)    # 19
BasicMath.sub(20, 3, 2)       # 15
BasicMath.multi(2, 3, 4)      # 24
BasicMath.div(100, 2, 5)      # 10.0
BasicMath.mod(17, 5)          # 2
Checks.IsEven(42)             # True
RNG.rand(1, 10)               # Random int between 1 and 10
```

| Function | Description |
|----------|-------------|
| `add(start, *args)` | Adds all values to the starting number |
| `sub(start, *args)` | Subtracts each value from the running total |
| `multi(start, *args)` | Multiplies all values together |
| `div(start, *args)` | Divides running total by each value — guarded against divide by zero |
| `mod(base, var)` | Returns base % var |
| `Checks.IsEven(var)` | Returns True if var is even |
| `RNG.rand(mi, ma)` | Returns a random integer between mi and ma |

---

### Physics_1D

One-dimensional kinematics. All functions operate on scalars along a single axis.

```python
from MathTypes.Physics import Physics_1D

Physics_1D.GetDistance(0, 50)                        # 50.0
Physics_1D.Velocity(100, 5)                          # 20.0  (m/s)
Physics_1D.FinalVelocity(9.8, 10, 2, 0)             # 19.6  (m/s)
Physics_1D.GetDisplacement(9.8, 3, 0)               # 44.1  (m)
```

| Function | Formula | Description |
|----------|---------|-------------|
| `GetDistance(loc1, loc2)` | `loc2 - loc1` | Distance between two positions |
| `GetTime(t1, t2)` | `t2 - t1` | Elapsed time between two moments |
| `Velocity(d, t)` | `d / t` | Speed from distance and time |
| `FinalVelocity(a, d, t, v0)` | `v0 + a*t` | Final speed after accelerating |
| `Acceleration(v1, v2, t)` | `(v2-v1) / t` | Average acceleration |
| `InstantAcceleration(v1, v2, t)` | `(v2-v1) / t` | Instantaneous acceleration |
| `ConstantAcceleration(v1, v2, t)` | `(v2-v1) / t` | Acceleration assumed constant |
| `GetDisplacement(a, t, v0)` | `v0*t + ½at²` | Displacement from rest or initial speed |
| `GetPosition(a, t, v0, x0)` | `x0 + v0*t + ½at²` | Absolute position after motion |

---

### Physics_2D

Two-dimensional vector operations and projectile motion. All vectors are described by magnitude and angle in degrees.

```python
from MathTypes.Physics import Physics_2D

Physics_2D.IHat(50, 30)                              # X component
Physics_2D.IJ(50, 30)                               # (X, Y) tuple
Physics_2D.AddVectors(30, 45, 20, 90)               # Resultant vector tuple
Physics_2D.ProjectileRange(20, 45, 2.04, 0.5)       # Horizontal range
```

**Vector Operations**

| Function | Description |
|----------|-------------|
| `IHat(a, angle)` | X component — `a * cos(angle)` |
| `JHat(a, angle)` | Y component — `a * sin(angle)` |
| `IJ(a, angle)` | Both X and Y components as a tuple |
| `VectorMagnitude(a, angle)` | Scalar magnitude — `sqrt(x²+y²)` |
| `AddVectors(a, aA, b, aB)` | Sum of two vectors as a tuple |
| `SubtractVectors(a, aA, b, aB)` | Difference of two vectors |
| `DotProduct(a, aA, b, aB)` | Scalar dot product — `ax*bx + ay*by` |
| `CrossProduct(a, aA, b, aB)` | Scalar cross product — `ax*by - ay*bx` |
| `ScalarMultiply(c, a, angle)` | Scale vector by a constant |
| `ScalarDivide(c, a, angle)` | Divide vector by a constant |
| `NormalizeVector(a, angle)` | Unit vector — length scaled to 1 |
| `VectorProjection(a, aA, b, aB)` | Scalar projection of a onto b |
| `Position2D(x, y)` | 2D position vector tuple |

**Projectile Motion**

| Function | Description |
|----------|-------------|
| `ProjectileVelocity(speed, angle, t, mass)` | Velocity vector at time t |
| `ProjectilePosition(speed, angle, t, mass)` | Position at time t |
| `ProjectileRange(speed, angle, t, mass)` | Horizontal distance traveled |
| `ProjectileMaxHeight(speed, angle, mass)` | Peak height reached |
| `ProjectilePath(speed, angle, t, mass, steps)` | Full path with air resistance as list of (x,y) |
| `ProjectilePathNoAR(speed, angle, t, steps)` | Full path without drag as list of (x,y) |

---

### Physics_3D

Three-dimensional extension of Physics_2D. Vectors are described by magnitude, horizontal angle (θ), and vertical elevation angle (φ).

```python
from MathTypes.Physics import Physics_3D

Physics_3D.IJK(50, 45, 30)                          # (X, Y, Z) tuple
Physics_3D.CrossProduct(30, 45, 0, 20, 90, 0)       # 3D cross product tuple
Physics_3D.ProjectileMaxHeight(20, 45, 0.5)         # Peak height
```

Includes all vector operations from Physics_2D extended to three dimensions plus:

| Function | Description |
|----------|-------------|
| `KHat(a, angle, phi)` | Z component — `a * sin(phi) * cos(angle)` |
| `IJK(a, angle, phi)` | All three components as a tuple |
| `DragForce(mass, vx, vy)` | Drag force components acting on a moving object |
| `Position3D(x, y, z)` | 3D position vector tuple |

---

### Forces

A complete force physics system built around `Force2D`, `Force3D`, `Forces2D`, and `Forces3D` objects. Supports building multi-force scenarios and querying energy, momentum, equilibrium, and more.

```python
from MathTypes.Physics.Forces import Force2D, Forces2D
from MathTypes.Physics.Forces import Force3D, Forces3D
from MathTypes.Physics.Forces import TerminalVelocity, DragForce, IsAtTerminalVelocity
```

#### Force2D and Force3D — Individual Force Objects

Represent a single force. Constructed either from components or from magnitude and angle.

```python
# From components
f = Force2D(10, 5)              # 10N right, 5N up — magnitude and angle auto-derived

# From magnitude and angle
f = Force2D(0, 0, 45, 20)      # 20N at 45 degrees — components auto-derived
```

| Property | Description |
|----------|-------------|
| `f.x` | X component (N) |
| `f.y` | Y component (N) |
| `f.magnitude` | Total force strength (N) |
| `f.angle` | Direction in degrees |

`Force3D` adds `f.z` and `f.phi` for the vertical elevation angle.

#### Forces2D and Forces3D — Multi-Force Systems

Hold a list of Force objects acting on a single physical object. Mass and gravity are assigned to the object, not the forces.

```python
obj          = Forces2D(mass=5.0, g=9.8)   # Create object with mass and gravity
obj.velocity = 3.0                          # Set current velocity for KE and momentum
obj.height   = 2.0                          # Set current height for PE
obj.forces.append(Force2D(10, 0))           # Apply a 10N rightward force
obj.ApplyGravity()                          # Add Fg = mg downward to the force list
obj.SetIncline(30)                          # Recalculate normal force for a 30° slope
```

**Query Methods**

| Method | Returns |
|--------|---------|
| `NetForce()` | Resultant force as a Force2D or Force3D object |
| `NetAcceleration()` | `a = F_net / mass` in m/s² |
| `NetMomentum()` | `p = mv` in kg·m/s |
| `NetKineticEnergy()` | `KE = ½mv²` in J |
| `NetPotentialEnergy()` | `PE = mgh` in J |
| `NetMechanicalEnergy()` | `ME = KE + PE` in J |
| `NetImpulse(t)` | `J = F_net * t` in N·s |
| `UpdateVelocity(t)` | Advances velocity by `v = v + at` over time t |
| `IsStaticEquilibrium()` | True if ΣF = 0 and v = 0 |
| `IsDynamicEquilibrium()` | True if ΣF = 0 and v ≠ 0 |

**Standalone Force Utilities**

```python
from MathTypes.Physics.Forces import (
    Force, Acceleration, Mass,
    FrictionForce, NormalForce,
    TerminalVelocity, DragForce, IsAtTerminalVelocity
)
```

| Function | Formula | Description |
|----------|---------|-------------|
| `Force(m, a)` | `F = ma` | Net force from mass and acceleration |
| `Acceleration(F, m)` | `a = F/m` | Acceleration from force and mass |
| `Mass(F, a)` | `m = F/a` | Mass from force and acceleration |
| `FrictionForce(mu, Fn)` | `Ff = μ * Fn` | Friction force |
| `NormalForce(m, g)` | `Fn = mg` | Normal force on flat surface |
| `TerminalVelocity(m, A, Cd, rho, g)` | `vt = sqrt(2mg / ρACd)` | Maximum fall speed through a fluid |
| `DragForce(v, A, Cd, rho)` | `Fd = ½ρv²ACd` | Drag at a given velocity |
| `IsAtTerminalVelocity(v, m, A, Cd, rho, g)` | `v ≈ vt` | True if within 1% of terminal velocity |

---

## Debug UI

MathCore includes an interactive console Debug UI for every module. Each function runs a numbered menu, collects inputs, and prints the result.

```python
from DebugUI import (
    BasicMathDebug,
    Physics1DDebug,
    Physics2DDebug,
    Physics3DDebug,
    Forces2DDebug,
    Forces3DDebug
)

BasicMathDebug()    # Interactive arithmetic tester
Physics1DDebug()    # Interactive kinematics tester
Physics2DDebug()    # Interactive 2D vector and projectile tester
Physics3DDebug()    # Interactive 3D vector and projectile tester
Forces2DDebug()     # Step-through 2D force scenario builder
Forces3DDebug()     # Step-through 3D force scenario builder
```

`Forces2DDebug` and `Forces3DDebug` walk through three guided steps:

1. **Describe your object** — mass, gravity, velocity, height, optional incline
2. **Add forces** — by components or by magnitude and angle, with optional gravity
3. **Query the system** — net force, acceleration, energy, momentum, equilibrium, drag

The `CollectVariables()` helper used by BasicMathDebug supports adding, removing, and confirming an unlimited list of numbers before calculating.

---

## File Structure

```
MathTypes/
├── Basic/
│   ├── BasicMath.py
│   └── __init__.py
├── Physics/
│   ├── Physics_1D.py
│   ├── Physics_2D.py
│   ├── Physics_3D.py
│   ├── Forces/
│   │   ├── Force2D.py
│   │   ├── Force3D.py
│   │   ├── Forces2D.py
│   │   ├── Forces3D.py
│   │   ├── Utilities.py
│   │   └── __init__.py
│   └── __init__.py
Config/
├── Checks.py
├── RNG.py
└── __init__.py
DebugUI.py
```

---

## Example Usage

```python
# ---- BasicMath ----
from MathTypes.Basic import BasicMath
print(BasicMath.add(10, 2, 3, 4))       # 19
print(BasicMath.div(100, 2, 5))         # 10.0

# ---- Physics 1D ----
from MathTypes.Physics import Physics_1D
print(Physics_1D.GetDisplacement(9.8, 3, 0))   # 44.1

# ---- Physics 2D ----
from MathTypes.Physics import Physics_2D
print(Physics_2D.IJ(50, 45))           # (35.355, 35.355)
print(Physics_2D.ProjectileRange(20, 45, 2.04, 0.5))

# ---- Forces 2D ----
from MathTypes.Physics.Forces import Force2D, Forces2D

obj = Forces2D(5.0, 9.8)
obj.velocity = 3.0
obj.height   = 2.0
obj.ApplyGravity()
obj.forces.append(Force2D(0, 0, 0, 15))    # 15N rightward
print(obj.NetAcceleration())               # m/s²
print(obj.NetKineticEnergy())              # J
print(obj.IsStaticEquilibrium())           # False
```

---

## Requirements

- Python 3.10+  *(match/case syntax required)*
- No external dependencies

---

## Summary

MathCore is a dependency-free math and physics engine built for readability, correctness, and reuse. It covers arithmetic through full 3D force physics in a consistent, well-guarded API with an interactive Debug UI for every module — ready to import into any Python project.
