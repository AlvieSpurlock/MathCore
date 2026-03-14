# MathCore

MathCore is a modular mathematical computation library and generative art engine for Python. It provides a clean, readable API covering pure mathematics and physics across 23 domains — and uses those calculations as direct input to a deterministic generative art system that turns every result into a unique, reproducible visual piece.

Every function is documented, guarded against invalid input, and returns clean values ready for use in scripts, simulations, or as the computational backbone of the art engine. No external dependencies are required for the math layer. Pillow is required for the art engine.

---

## Overview

MathCore has two layers that work together.

The **calculation layer** is 23 focused modules covering 1,364 callable functions across pure mathematics and physics. Every function accepts clean numeric inputs and returns a result.

The **art engine** takes that result — along with the function name and the exact input values — and generates a 3000×3000px artwork that is mathematically determined by what was computed. The same calculation always produces the same artwork. Different inputs to the same function produce visually distinct pieces.

---

## Calculation Modules

| Module | Domain | Functions | Sample |
|--------|--------|-----------|--------|
| `Algebra` | Linear, quadratic, polynomial equations | 42 | `Linear`, `Slope`, `SolveLinearForX` |
| `AbstractAlgebra` | Groups, rings, fields, modular arithmetic | 76 | `GroupOrder`, `IsAbelian`, `ModularInverse` |
| `AlgebraicGeometry` | Curves, varieties, projective geometry | 63 | `EllipticCurvePoint`, `BezoutNumber` |
| `Calculus` | Limits, derivatives, integrals, series | 39 | `Limit`, `Derivative`, `RiemannSum` |
| `Combinatorics` | Counting, permutations, graph theory | 55 | `Factorial`, `BinomialCoefficient`, `CatalanNumber` |
| `DifferentialGeometry` | Curvature, geodesics, manifolds | 61 | `GaussianCurvature`, `Geodesic` |
| `Differentiation` | Differentiation rules and applications | 55 | `ChainRule`, `ProductRule`, `CriticalPoints` |
| `DiscreteMath` | Logic, sets, graphs, number theory | 125 | `GCD`, `IsPrime`, `EulerPhi` |
| `Geometry` | Euclidean shapes, distance, area, volume | 58 | `CircleArea`, `TriangleArea`, `GoldenRatio` |
| `LinearAlgebra` | Matrices, vectors, eigenvalues | 91 | `Determinant`, `Eigenvalue`, `Orthogonalize` |
| `Probability` | Distributions, Bayes, entropy | 70 | `NormalDistribution`, `BayesTheorem`, `Entropy` |
| `Statistics` | Descriptive and inferential statistics | 56 | `Mean`, `Variance`, `Regression` |
| `Topology` | Topological spaces, invariants, manifolds | 56 | `EulerCharacteristic`, `IsTopology`, `FundamentalGroup` |
| `Trigonometry` | Circular and hyperbolic functions | 45 | `Sin`, `Cos`, `GoldenAngle` |
| `Forces` | Force systems, energy, momentum, drag | 92 | `NetForce`, `TerminalVelocity`, `DragForce` |
| `Physics_Energy` | Kinetic, potential, mechanical energy | 67 | `KineticEnergy`, `RotationalKE`, `PowerOutput` |
| `Physics_Momentum` | Linear and angular momentum, impulse | 39 | `Momentum`, `Impulse`, `AngularMomentum` |
| `Physics_Springs` | Spring systems, oscillation, resonance | 44 | `SpringForce`, `NaturalFrequency`, `DampingRatio` |
| `Physics_Collisions` | Elastic and inelastic collisions | 22 | `ElasticCollision`, `CoefficientOfRestitution` |
| `Physics_CenterOfMass` | Centre of mass for systems and bodies | 64 | `CenterOfMass`, `MomentOfInertia` |
| `Physics_1D` | 1D kinematics | 30 | `Velocity`, `GetDisplacement`, `FinalVelocity` |
| `Physics_2D` | 2D vectors, projectile motion | 59 | `AddVectors`, `ProjectileRange`, `DotProduct` |
| `Physics_3D` | 3D vectors, projectile motion | 55 | `IJK`, `CrossProduct`, `DragForce` |

---

## Installation and Requirements

```
Python 3.10+      (match/case syntax required)
Pillow            (pip install Pillow — required for art engine only)
```

No other external dependencies.

```python
# Math layer — no dependencies
from MathTypes.Basic import BasicMath
from MathTypes.Physics import Physics_1D, Physics_2D, Physics_3D
from MathTypes.Physics.Forces import Force2D, Forces2D
from MathTypes import Algebra, Calculus, Statistics, Trigonometry
# ... and so on for any module

# Art engine — requires Pillow
from MathCodeEngine import MathCodeEngine
```

---

## The Art Engine

Every calculation feeds a deterministic generative art system. The result value, the function name, and the exact inputs you entered all drive how the artwork looks — not just what seed it uses.

### How the math maps to visuals

**Function class → stroke vocabulary**

Functions are classified by mathematical character. Each class has a primary visual vocabulary:

| Class | Functions | Strokes |
|-------|-----------|---------|
| `periodic` | Sin, Cos, Frequency, Amplitude | wave, spiral, orbit |
| `differential` | Derivative, Gradient, Tangent | vector, radial — highly directional |
| `geometric` | GoldenRatio, Area, CircleArea | polygon, arc, orbit |
| `combinatorial` | Factorial, Permutation, CatalanNumber | tree, radial, lattice |
| `dynamic` | KineticEnergy, Velocity, Force | vector, wave, line |
| `topological` | EulerCharacteristic, Manifold, Knot | orbit, curve, spiral |
| `probabilistic` | Entropy, BayesTheorem, Markov | scatter, dot — omnidirectional |
| `statistical` | NormalDistribution, Variance, Mean | scatter, arc, curve |
| `algebraic` | Eigenvalue, Determinant, Polynomial | lattice, polygon |
| `recursive` | Fibonacci, PowerSeries, Recurrence | tree, spiral |

**Result value → visual parameters**

The numeric result modulates:
- **Frequency** — high result = dense, rapid strokes; low result = slow, expansive
- **Size bias** — large result = strokes fill the canvas; small = tight cluster
- **Angle bias** — result maps to a preferred compass direction, making pieces feel directed by the math
- **Focal spread** — geometric functions cluster tightly; statistical functions spread wide
- **Alpha scale** — large results produce more opaque, heavier strokes

**Input values → composition**

The actual named inputs you entered (not just their hash) drive compositional geometry:
- First input value → focal point x-offset from centre
- Second input value → focal point y-offset from centre
- `KineticEnergy(mass=20, velocity=0.5)` and `KineticEnergy(mass=0.1, velocity=50)` produce the same energy value but different compositions — the mass vs velocity balance shifts the focal point

**Profile → color palette and stroke weight**

Profiles provide the available color menu and stroke thickness/opacity ranges. The math decides what to order from that menu.

**Math → which colors are actually used**

Six color distribution patterns, each driven by function class and result:

| Pattern | Used by | Effect |
|---------|---------|--------|
| `focused` | geometric, algebraic | One color dominates at 4–6× weight |
| `dual` | differential, dynamic | Two colors compete equally |
| `spread` | probabilistic, statistical | All colors uniform — no preference |
| `oscillating` | periodic | Colors cycle in a wave, phase from result |
| `gradient` | topological | Smooth falloff from dominant color |
| `cascade` | combinatorial, recursive | Exponential dropoff like factorial growth |

The same profile applied to a `Sin` function and a `GoldenRatio` function will produce different color distributions even with the same seed — because the math is ordering different things from the same color menu.

### Output

- Default resolution: **3000×3000px** (print-quality — 10×10" at 300dpi)
- Set `MATHCODE_SIZE=512` env var for fast preview renders
- Compositional gravity: 20% anchor strokes near focal point, 50% mid-field, 30% scatter
- All stroke sizes and thicknesses scale proportionally with canvas resolution
- No background grid — clean output at any size

---

## Art Profiles

Eight built-in visual profiles. Each provides a color palette and stroke character. The math drives which colors are used and in what proportion.

| Profile | Palette | Stroke character | Best domains |
|---------|---------|-----------------|--------------|
| `neon_city` | Cyan, green, pink, yellow, purple on near-black | Thin, electric lines | Differential, algebraic |
| `deep_space` | Purple, cyan, white, pink on deep black | Orbital, circular, cosmic | Physics, topological, probabilistic |
| `solar_flare` | Yellow, orange, red, pink, white on dark red-black | Thick directional waves | Dynamic, periodic |
| `ice_grid` | Cyan, white, purple on dark blue | Thin lattice and polygon | Algebraic, geometric |
| `organic` | Green, yellow, orange, white on dark green | Flowing tree branches and curves | Combinatorial, recursive |
| `monochrome` | White greys on black | Clean lines, arcs, spirals | Geometric, differential |
| `chaos` | All seven palette colors equally | All stroke types equally | Any |
| `default` | Multi-color | Balanced mix | Any |

---

## The UI

MathCore includes a full graphical interface and a floating art monitor.

### MathCoreUI

A Tkinter application exposing all 23 modules and 1,364 functions through a searchable sidebar.

- Navigate by module via the left panel
- Enter function inputs in labelled fields
- View step-by-step working where available
- Every calculation immediately triggers an art generation
- Art profile can be changed or randomized at any time
- Results are shown in a scrollable output panel with syntax highlighting

### MathCodeMonitor

A floating, always-on-top art monitor that sits alongside the calculator.

- Displays each new piece at 400px with LANCZOS downscaling from 3000px source
- Thumbnail strip shows history of all pieces generated in the session
- Click any thumbnail to review a past piece with its metadata
- Regen button re-queues the current piece's seed with a new profile — preserves all mathematical composition parameters, only the visual style changes
- Export button saves the full 3000px PNG to the session folder
- Piece metadata includes: seed, domain, function, function class, input values, rarity, complexity, stroke types, and active profile

### Rarity system

Each piece receives a rarity rating based on a seed-derived probability roll, bumped one tier if the piece has genuine structural complexity.

| Tier | Probability | Criteria |
|------|------------|---------|
| Common | 50% | Base roll |
| Uncommon | 25% | Base roll |
| Rare | 15% | Base roll or structural bump |
| Ultra Rare | 8% | Base roll or structural bump |
| Legendary | 2% | Base roll or structural bump |

---

## Usage Examples

```python
# ── Calculation layer ────────────────────────────────────────────────────────

from MathTypes.Basic import BasicMath
BasicMath.add(10, 2, 3, 4)       # 19
BasicMath.div(100, 2, 5)         # 10.0

from MathTypes.Physics import Physics_1D
Physics_1D.GetDisplacement(9.8, 3, 0)    # 44.1

from MathTypes import Statistics
Statistics.Mean(2, 4, 6, 8, 10)          # 6.0
Statistics.NormalDistribution(0, 1, 0)   # 0.3989

from MathTypes import Trigonometry
Trigonometry.Sin(45)                     # 0.7071
Trigonometry.GoldenAngle()              # 137.5077...

from MathTypes import Combinatorics
Combinatorics.Factorial(7)              # 5040
Combinatorics.BinomialCoefficient(10, 3)  # 120

from MathTypes.Physics.Forces import Force2D, Forces2D
obj = Forces2D(5.0, 9.8)
obj.velocity = 3.0
obj.height   = 2.0
obj.ApplyGravity()
obj.forces.append(Force2D(0, 0, 0, 15))
print(obj.NetKineticEnergy())            # J
print(obj.IsStaticEquilibrium())         # False

# ── Art engine — standalone ──────────────────────────────────────────────────

from MathCodeEngine import MathCodeEngine, set_profile

engine = MathCodeEngine()
engine.start()

# Feed a result directly
engine.feed(
    result_value = 160.0,              # KE = 0.5 * 5 * 8² = 160J
    domain       = 'Physics — Energy',
    fn_name      = 'KineticEnergy',
    inputs       = {'mass': 5.0, 'velocity': 8.0},
)

# The engine renders asynchronously — register a callback for new pieces
def on_new_piece(piece):
    print(f'{piece.rarity} | {piece.domain} | seed {piece.seed}')
    piece.save_png()   # saves to mathcode_art/ session folder

engine.on_new_piece = on_new_piece

# Change profile at any time
set_profile('deep_space')

# ── Full UI ──────────────────────────────────────────────────────────────────

from MathCoreUI import MathCoreApp
app = MathCoreApp()
app.mainloop()
```

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
│   ├── Physics_Energy.py
│   ├── Physics_Momentum.py
│   ├── Physics_Springs.py
│   ├── Physics_Collisions.py
│   ├── Physics_CenterOfMass.py
│   ├── Forces/
│   │   ├── Force2D.py
│   │   ├── Force3D.py
│   │   ├── Forces2D.py
│   │   ├── Forces3D.py
│   │   ├── Utilities.py
│   │   └── __init__.py
│   └── __init__.py
├── Algebra.py
├── AbstractAlgebra.py
├── AlgebraicGeometry.py
├── Calculus.py
├── Combinatorics.py
├── DifferentialGeometry.py
├── Differentiation.py
├── DiscreteMath.py
├── Geometry.py
├── LinearAlgebra.py
├── Probability.py
├── Statistics.py
├── Topology.py
├── Trigonometry.py
└── __init__.py
Config/
├── Checks.py
├── RNG.py
└── __init__.py
MathCodeEngine.py       — generative art engine
MathCodeMonitor.py      — floating art monitor (Tkinter)
MathCoreUI.py           — main application UI (Tkinter)
DebugUI.py              — console debug interface for all modules
mathcode_art/           — session output folders (gitignored)
```

---

## Requirements

| Requirement | Purpose |
|-------------|---------|
| Python 3.10+ | match/case syntax throughout |
| Pillow | Art engine rendering (optional — engine falls back to tkinter canvas without it) |

No other dependencies. Install Pillow with `pip install Pillow`.
