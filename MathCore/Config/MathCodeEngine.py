"""
MathCode Art Engine
═══════════════════
Deterministic generative art seeded by MathCore calculation results.
Runs in a background thread — never blocks the calculator.

Public API
──────────
  engine = MathCodeEngine()
  engine.feed(result_value, domain='Physics', fn_name='Kinetic Energy')
  engine.start()          # launch background thread
  engine.stop()

  engine.latest           # most recent ArtPiece or None
  engine.history          # list of last 32 ArtPieces
  engine.on_new_piece     # assign a callable(ArtPiece) for UI notification

ArtPiece fields
───────────────
  seed, domain, fn_name
  strokes           list of stroke dicts
  image             PIL.Image or None
  tk_photo          ImageTk.PhotoImage or None (set by UI layer)
  metadata          dict
  rarity            str
  complexity        int
  price             float
  timestamp         str
"""

import math
import random
import time
import threading
import queue
import json
import os
import uuid
from dataclasses import dataclass, field
from typing import Optional, Callable, List, Dict, Any, Tuple

# ── Optional PIL (graceful fallback to pure-tkinter rendering) ────────────────
try:
    from PIL import Image, ImageDraw, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
# GENERATION PROFILE  —  tune colors, strokes, and style per session
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class GenerationProfile:
    """
    Controls the visual character of every piece generated this session.

    Fields
    ──────
    name            — label shown in the monitor and exported metadata

    palette         — list of (hex_color, weight, alpha_min, alpha_max) tuples.
                      The profile provides AVAILABLE COLORS ONLY.
                      Which colors are used and in what proportions is determined
                      entirely by the mathematical result and inputs via
                      _extract_math_params() → _build_color_weights().
                      Profile weights are accepted for compatibility but ignored —
                      only the hex color and alpha range (alpha_min, alpha_max) matter.
                      Short form (hex,) or (hex, weight) accepted.  Alpha defaults (120,255).

    stroke_weights  — dict of stroke_type -> weight.  Unmentioned types get weight 0.

    n_strokes       — how many strokes per piece

    thickness_range — (min, max) line thickness in pixels

    size_range      — (min, max) stroke size in canvas units

    angle_ranges    — dict of stroke_type -> (min_deg, max_deg).
                      Controls the direction range each stroke type draws in.
                      e.g. {"line": (45, 135)} forces lines to draw diagonally only.
                      Special key "*" sets a global default for all strokes.
                      None = full 0-360 for every stroke type.

    freq_range      — (min, max) frequency multiplier for wave/spiral/curve strokes

    bg_color        — background hex color

    randomize_each  — if True, jitter palette weights slightly each piece
    """
    name:            str                 = "Default"
    palette:         List[tuple]         = None
    stroke_weights:  Dict[str, float]    = None
    n_strokes:       int                 = 200
    thickness_range: Tuple[int, int]     = (1, 4)
    size_range:      Tuple[int, int]     = (10, 60)
    angle_ranges:    Dict[str, tuple]    = None
    freq_range:      Tuple[float, float] = (0.5, 6.0)
    bg_color:        str                 = "#080b0f"
    randomize_each:  bool                = False

    def effective_palette(self, domain: str) -> List[tuple]:
        """Return normalized palette — always (color, alpha_min, alpha_max).
        Weights are stripped. Color selection is driven by math, not profile weights."""
        raw = self.palette if self.palette else DOMAIN_PALETTES.get(domain, DOMAIN_PALETTES["default"])
        result = []
        for entry in raw:
            if len(entry) == 1:
                # (hex,) — no weight, no alpha
                result.append((entry[0], 120, 255))
            elif len(entry) == 2:
                # (hex, weight) — weight ignored, default alpha
                result.append((entry[0], 120, 255))
            elif len(entry) == 3:
                # (hex, weight, alpha_min) — weight ignored
                result.append((entry[0], entry[2], 255))
            else:
                # (hex, weight, alpha_min, alpha_max) — weight ignored
                result.append((entry[0], entry[2], entry[3]))
        return result

    def effective_strokes(self, domain: str) -> List[tuple]:
        """Return this profile's stroke list, falling back to domain default."""
        if self.stroke_weights:
            return list(self.stroke_weights.items())
        return STROKE_STYLES.get(domain, STROKE_STYLES["default"])

    def angle_for(self, stroke: str, rng) -> float:
        """Pick an angle for the given stroke type, respecting angle_ranges."""
        if not self.angle_ranges:
            return rng.uniform(0, 360)
        rng_pair = (self.angle_ranges.get(stroke)
                    or self.angle_ranges.get("*")
                    or (0, 360))
        lo, hi = rng_pair
        if lo <= hi:
            return rng.uniform(lo, hi)
        # Wrap-around range e.g. (350, 10) means near-north
        span1, span2 = 360 - lo, hi
        if rng.random() < span1 / (span1 + span2):
            return rng.uniform(lo, 360)
        else:
            return rng.uniform(0, hi)

    def jitter(self, rng) -> "GenerationProfile":
        """Return a copy with palette weights/alphas slightly shuffled."""
        if not self.randomize_each:
            return self
        new_palette = []
        for entry in self.effective_palette("default"):
            c, amin, amax = entry
            # Jitter alpha ranges slightly — this is the only thing profiles
            # still control per-stroke. Colors are selected by math.
            new_amin = max(0,   min(255, amin + rng.randint(-15, 15)))
            new_amax = max(new_amin + 10, min(255, amax + rng.randint(-15, 15)))
            new_palette.append((c, new_amin, new_amax))
        import copy
        p = copy.copy(self)
        p.palette = new_palette
        return p

# ── Built-in presets ──────────────────────────────────────────────────────────

PROFILES: Dict[str, GenerationProfile] = {

    'default': GenerationProfile(
        name            = 'Default',
        n_strokes       = 160,
        size_range      = (8, 55),
        thickness_range = (1, 4),
    ),

    'neon_city': GenerationProfile(
        name    = 'Neon City',
        palette = [('#00FF9F',1.4),('#00D4FF',1.2),('#FF006E',0.9),
                   ('#FFE600',0.5),('#7B61FF',0.4)],
        stroke_weights  = {'line':1.4,'vector':1.2,'orbit':0.8,
                           'arc':0.6,'dot':0.3},
        # No grid strokes — clean geometric lines only
        n_strokes       = 140,
        size_range      = (12, 70),    # medium strokes — readable at any scale
        thickness_range = (1, 3),      # thin lines = crisp neon feel
        bg_color        = '#050810',
    ),

    'deep_space': GenerationProfile(
        name    = 'Deep Space',
        palette = [('#7B61FF',1.4),('#00D4FF',0.8),('#FFFFFF',0.5),
                   ('#FF006E',0.2),('#00FF9F',0.1)],
        stroke_weights  = {'orbit':1.6,'spiral':1.4,'dot':1.2,
                           'arc':0.6,'radial':0.4},
        # Dominated by orbits and spirals — circular, spacial feel
        n_strokes       = 200,
        size_range      = (20, 90),    # large circular strokes = cosmic scale
        thickness_range = (1, 3),
        bg_color        = '#02020a',
    ),

    'solar_flare': GenerationProfile(
        name    = 'Solar Flare',
        palette = [('#FFE600',1.6),('#FF7700',1.2),('#FF006E',0.8),
                   ('#FFFFFF',0.3),('#FF3300',0.2)],
        stroke_weights  = {'wave':1.6,'radial':1.2,'curve':1.0,
                           'arc':0.5,'spiral':0.4},
        # Waves and radials — directional energy, heat
        n_strokes       = 180,
        size_range      = (15, 80),
        thickness_range = (2, 5),      # thicker strokes = more visual heat
        freq_range      = (1.5, 4.0),  # higher frequency = denser waves
        bg_color        = '#0a0400',
    ),

    'ice_grid': GenerationProfile(
        name    = 'Ice Grid',
        palette = [('#00D4FF',1.6),('#FFFFFF',1.0),('#7B61FF',0.5),
                   ('#aaddff',0.4)],
        stroke_weights  = {'lattice':1.6,'polygon':1.2,'line':0.8,
                           'vector':0.5,'dot':0.2},
        # Lattice and polygon dominant — geometric, crystalline
        # Note: no 'grid' stroke type here — the grid is a stroke element,
        # not the background grid that was removed. Ice Grid's identity
        # comes from lattice patterns and polygon shapes, not background lines.
        n_strokes       = 120,
        size_range      = (10, 50),
        thickness_range = (1, 2),      # very thin — crystalline, precise
        bg_color        = '#020810',
    ),

    'organic': GenerationProfile(
        name    = 'Organic',
        palette = [('#00FF9F',1.2),('#FFE600',0.9),('#FF7700',0.6),
                   ('#FFFFFF',0.3),('#00D4FF',0.2)],
        stroke_weights  = {'tree':1.6,'curve':1.4,'wave':0.8,
                           'spiral':0.5,'scatter':0.4},
        # Tree and curve dominant — branching, flowing, biological
        n_strokes       = 160,
        size_range      = (20, 80),    # larger — branches need space
        thickness_range = (1, 4),
        freq_range      = (0.5, 2.0),  # lower freq = gentler curves
        bg_color        = '#030a04',
    ),

    'monochrome': GenerationProfile(
        name    = 'Monochrome',
        palette = [('#FFFFFF',1.8),('#bbbbbb',1.0),('#666666',0.5),
                   ('#333333',0.2)],
        stroke_weights  = {'line':1.2,'arc':1.0,'spiral':0.8,
                           'vector':0.6,'dot':0.4},
        # Clean structural strokes — no noise types, no lattice/grid
        # Monochrome works by shape and composition, not colour
        n_strokes       = 130,
        size_range      = (10, 65),
        thickness_range = (1, 4),
        bg_color        = '#000000',
    ),

    'chaos': GenerationProfile(
        name            = 'Chaos',
        palette         = [('#00FF9F',1.0),('#00D4FF',1.0),('#FF006E',1.0),
                           ('#FFE600',1.0),('#7B61FF',1.0),('#FF7700',1.0),
                           ('#FFFFFF',0.6)],
        stroke_weights  = {s: 1.0 for s in
                           ['line','arc','dot','orbit','spiral','wave',
                            'vector','polygon','scatter','curve','radial','tree']},
        # Chaos uses all stroke types equally — no lattice/grid which would
        # look like structure rather than chaos
        n_strokes       = 280,
        size_range      = (5, 90),     # extreme range = true chaos
        thickness_range = (1, 6),
        randomize_each  = True,
        bg_color        = '#080b0f',
    ),
}

# Active profile — swap this at any time to change the session style
ACTIVE_PROFILE: GenerationProfile = PROFILES['default']


def set_profile(name_or_profile) -> GenerationProfile:
    """
    Set the active generation profile for this session.

    Usage:
        set_profile('neon_city')
        set_profile(PROFILES['deep_space'])
        set_profile(GenerationProfile(name='Custom', palette=[('#FF0000',1.0)]))
    """
    global ACTIVE_PROFILE
    if isinstance(name_or_profile, str):
        if name_or_profile not in PROFILES:
            raise ValueError(f'Unknown profile "{name_or_profile}". '
                             f'Available: {list(PROFILES.keys())}')
        ACTIVE_PROFILE = PROFILES[name_or_profile]
    elif isinstance(name_or_profile, GenerationProfile):
        ACTIVE_PROFILE = name_or_profile
    else:
        raise TypeError('Pass a profile name string or a GenerationProfile instance.')
    log.info(f'Generation profile set to: {ACTIVE_PROFILE.name}') if 'log' in dir() else None
    return ACTIVE_PROFILE


def register_profile(profile: GenerationProfile) -> None:
    """Add a custom profile to the PROFILES registry under its name."""
    PROFILES[profile.name] = profile
    log.info(f'Custom profile registered: {profile.name}') if 'log' in dir() else None


# ══════════════════════════════════════════════════════════════════════════════
# COLOUR PALETTES  —  one per math domain
# ══════════════════════════════════════════════════════════════════════════════

DOMAIN_PALETTES: Dict[str, List[tuple]] = {
    'Physics — Energy':     [('#00FF9F',1.2),('#00D4FF',0.8),('#FFE600',0.6),('#FF006E',0.3),('#FFFFFF',0.2)],
    'Physics — Springs':    [('#00D4FF',1.2),('#7B61FF',0.8),('#00FF9F',0.5),('#FFE600',0.3),('#FFFFFF',0.1)],
    'Physics — Momentum':   [('#FF006E',1.2),('#FF7700',0.9),('#FFE600',0.6),('#FFFFFF',0.2)],
    'Physics — Center of Mass': [('#7B61FF',1.2),('#00D4FF',0.8),('#00FF9F',0.5),('#FF006E',0.2)],
    'Physics 1D':           [('#00FF9F',1.0),('#00D4FF',0.8),('#FFE600',0.5),('#FF006E',0.3)],
    'Algebra':              [('#FFE600',1.2),('#FF7700',0.8),('#FF006E',0.5),('#FFFFFF',0.2)],
    'Geometry':             [('#7B61FF',1.2),('#00D4FF',0.8),('#FFE600',0.4),('#FFFFFF',0.2)],
    'Trigonometry':         [('#00FF9F',1.0),('#7B61FF',0.9),('#00D4FF',0.6),('#FF006E',0.3)],
    'Calculus':             [('#FFE600',0.9),('#FF7700',0.8),('#00FF9F',0.6),('#FF006E',0.4)],
    'Statistics':           [('#00D4FF',1.2),('#7B61FF',0.7),('#FFE600',0.5),('#FF006E',0.2)],
    'Linear Algebra':       [('#7B61FF',1.4),('#00D4FF',0.8),('#FFFFFF',0.5),('#FFE600',0.2)],
    'Combinatorics':        [('#FF7700',1.2),('#FFE600',0.8),('#FF006E',0.5),('#FFFFFF',0.2)],
    'Basic Math':           [('#FFFFFF',1.0),('#00FF9F',0.8),('#FFE600',0.6),('#FF006E',0.3)],
    'default':              [('#00FF9F',1.0),('#00D4FF',0.8),('#FFE600',0.6),('#FF006E',0.4),('#7B61FF',0.3)],
}

STROKE_STYLES: Dict[str, List[tuple]] = {
    'Physics — Energy':     [('orbit',1.4),('spiral',1.0),('arc',0.8),('line',0.4),('dot',0.2)],
    'Physics — Springs':    [('wave',1.4),('spiral',0.8),('arc',0.8),('line',0.4)],
    'Physics — Momentum':   [('vector',1.4),('line',1.0),('arc',0.6),('dot',0.3)],
    'Physics — Center of Mass': [('orbit',1.2),('radial',1.0),('arc',0.8),('dot',0.4)],
    'Physics 1D':           [('line',1.4),('vector',1.0),('arc',0.5),('dot',0.2)],
    'Algebra':              [('lattice',1.2),('line',0.9),('arc',0.6),('dot',0.3)],
    'Geometry':             [('polygon',1.4),('arc',1.0),('line',0.6),('dot',0.2)],
    'Trigonometry':         [('wave',1.4),('spiral',0.8),('arc',0.8),('orbit',0.5)],
    'Calculus':             [('curve',1.4),('spiral',1.0),('arc',0.6),('dot',0.3)],
    'Statistics':           [('scatter',1.4),('line',0.8),('arc',0.5),('dot',0.8)],
    'Linear Algebra':       [('grid',1.4),('vector',1.0),('line',0.6),('dot',0.2)],
    'Combinatorics':        [('tree',1.2),('lattice',0.8),('dot',0.8),('arc',0.4)],
    'default':              [('line',0.6),('arc',0.5),('spiral',0.4),('dot',0.3),('orbit',0.3)],
}

# ══════════════════════════════════════════════════════════════════════════════
# DETERMINER LOGIC ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def split_seed(seed: int, n: int = 8) -> List[int]:
    """RNG Splitter — deterministic sub-seeds from a master seed."""
    rng = random.Random(seed)
    return [rng.randint(0, 10**9) for _ in range(n)]

def weighted_choice(rng: random.Random, options: List[tuple]) -> Any:
    """Weight Engine — pick a value according to weights."""
    total  = sum(w for _, w in options)
    target = rng.uniform(0, total)
    acc    = 0.0
    for value, weight in options:
        acc += weight
        if acc >= target:
            return value
    return options[-1][0]  # fallback to last

def resolve_fallback(rule: dict) -> dict:
    """Fallback Resolver — guarantee a valid, complete rule."""
    if not rule.get('stroke'):   rule['stroke']    = 'line'
    if not rule.get('color'):    rule['color']     = '#00FF9F'
    if not rule.get('thickness'):rule['thickness'] = 2
    if not rule.get('alpha'):    rule['alpha']     = 200
    if not rule.get('size'):     rule['size']      = 20
    return rule


# ══════════════════════════════════════════════════════════════════════════════
# MATH-DRIVEN VISUAL PARAMETER EXTRACTION
# ══════════════════════════════════════════════════════════════════════════════
#
# This is the core of what makes MathCode different from random generative art.
# The calculation result and inputs drive specific visual parameters.
# The profile drives color and opacity mood.
# They are independent layers — neither overrides the other.
#
# FUNCTION CLASS → STROKE FAMILY
# ─────────────────────────────────────────────────────────────────────────────
# Functions are classified by their mathematical character.
# Each class has a primary stroke vocabulary that expresses that character visually.
#
#   PERIODIC   sin, cos, tan, sinh, cosh, Amplitude, Frequency...
#     → wave, spiral, orbit   (periodicity, cycles, rotation)
#
#   DIFFERENTIAL  derivative, gradient, tangent, slope, Jacobian...
#     → vector, radial, line  (direction, rate, flow)
#
#   ALGEBRAIC   polynomial, quadratic, root, factor, solve...
#     → lattice, polygon, arc (structure, roots, symmetric forms)
#
#   PROBABILISTIC  normal, gaussian, entropy, bayesian, probability...
#     → scatter, dot, curve   (distribution, spread, density)
#
#   GEOMETRIC   area, perimeter, volume, distance, golden...
#     → polygon, arc, orbit   (shape, boundary, proportion)
#
#   COMBINATORIAL  permutation, combination, factorial, paths...
#     → tree, radial, lattice (branching, counting, structure)
#
#   DYNAMIC    velocity, acceleration, momentum, force, kinetic...
#     → vector, wave, line    (direction, energy, motion)
#
#   TOPOLOGICAL  manifold, euler, genus, homotopy, knot...
#     → orbit, curve, spiral  (continuity, loops, deformation)
#
#   STATISTICAL   mean, variance, regression, correlation, distribution...
#     → scatter, arc, dot     (data, spread, relationship)
#
#   RECURSIVE   fibonacci, catalan, recurrence, power, iteration...
#     → tree, spiral, orbit   (self-similarity, growth, iteration)
#
# RESULT VALUE → VISUAL PARAMETERS
# ─────────────────────────────────────────────────────────────────────────────
# The numeric result modulates visual parameters within the profile's ranges:
#
#   Normalized result r = (result - domain_min) / (domain_max - domain_min)
#   clamped to [0, 1].  domain_min/max estimated from function class.
#
#   r → frequency multiplier:    low r = slow waves, high r = fast/dense
#   r → size bias:               low r = small tight strokes, high r = large expansive
#   r → rotation bias:           r maps to a preferred angle family
#   r → color weight shift:      r shifts which palette color dominates
#   r → focal spread:            low r = tight composition, high r = expansive
#
# INPUT VALUES → COMPOSITION
# ─────────────────────────────────────────────────────────────────────────────
# The function inputs (not just their hash) drive composition geometry:
#
#   Number of inputs → layer count (more inputs = more compositional complexity)
#   First input magnitude → focal point offset from centre
#   Second input magnitude → stroke density gradient direction
#   Input ratio (a/b) → golden ratio proximity affects balance
#
# ══════════════════════════════════════════════════════════════════════════════

# Function name → mathematical class
_FN_CLASS_MAP: Dict[str, str] = {}

def _classify_function(fn_name: str) -> str:
    """
    Classify a function name into its mathematical character class.
    This determines which stroke family the piece uses as its primary vocabulary.
    Case-insensitive keyword matching — covers all 1,321 registered functions.
    """
    fn = fn_name.lower()

    # Periodic / oscillatory
    if any(k in fn for k in ('sin','cos','tan','sinh','cosh','tanh',
                               'frequency','amplitude','period','harmonic',
                               'oscillat','resonan','wave','sinusoid',
                               'circular','angular')):
        return 'periodic'

    # Differential / gradient
    if any(k in fn for k in ('deriv','gradient','tangent','slope','jacobian',
                               'hessian','partial','differential','critical',
                               'inflect','newton','chain','quotient')):
        return 'differential'

    # Probabilistic / statistical spread
    if any(k in fn for k in ('probab','entropy','bayesian','stochast','random',
                               'likelihood','posterior','prior','markov',
                               'shannon','mutual','conditional')):
        return 'probabilistic'

    # Statistical / distributional
    if any(k in fn for k in ('mean','median','variance','std','deviation',
                               'normal','gaussian','distribution','regression',
                               'correlation','scatter','histogram','quantile',
                               'zscore','percentile')):
        return 'statistical'

    # Geometric / spatial
    if any(k in fn for k in ('area','perim','volume','surface','distance',
                               'golden','fibonacci','ratio','angle','triangle',
                               'circle','sphere','polygon','hypotenuse',
                               'diagonal','bisect')):
        return 'geometric'

    # Combinatorial / counting
    if any(k in fn for k in ('permut','combin','factorial','catalan','stirling',
                               'bell','partition','lattice','path','spanning',
                               'chromat','eulerian','hamilton')):
        return 'combinatorial'

    # Dynamic / kinematic / forces
    if any(k in fn for k in ('velocit','accelerat','momentum','force','kinetic',
                               'energy','power','work','impulse','inertia',
                               'torque','spring','friction','tension','gravity',
                               'centripet','collision','restitut')):
        return 'dynamic'

    # Topological / manifold
    if any(k in fn for k in ('topolog','manifold','euler','genus','homotopy',
                               'homology','cohomology','knot','betti',
                               'hausdorff','compact','homeomorph')):
        return 'topological'

    # Algebraic / structural
    if any(k in fn for k in ('polynomi','quadrat','cubic','root','factor',
                               'eigenval','eigenvec','determinant','rank',
                               'matrix','linear','solve','system','basis',
                               'null','span','orthog')):
        return 'algebraic'

    # Recursive / self-similar
    if any(k in fn for k in ('fibonacci','recurr','iter','fractal','power',
                               'exponent','logarithm','sequence')):
        return 'recursive'

    return 'algebraic'   # default fallback


# Mathematical class → primary stroke vocabulary
# Profile stroke_weights BLEND with these rather than replacing them.
_CLASS_STROKES: Dict[str, List[tuple]] = {
    'periodic':      [('wave',2.0),('spiral',1.2),('orbit',0.8),('arc',0.5)],
    'differential':  [('vector',2.0),('radial',1.2),('line',1.0),('arc',0.4)],
    'probabilistic': [('scatter',2.0),('dot',1.4),('orbit',0.6),('arc',0.4)],
    'statistical':   [('scatter',1.6),('arc',1.0),('dot',1.2),('curve',0.6)],
    'geometric':     [('polygon',2.0),('arc',1.2),('orbit',0.8),('line',0.5)],
    'combinatorial': [('tree',2.0),('radial',1.2),('lattice',0.8),('dot',0.5)],
    'dynamic':       [('vector',1.6),('wave',1.4),('line',1.0),('arc',0.4)],
    'topological':   [('orbit',1.8),('curve',1.4),('spiral',1.0),('arc',0.5)],
    'algebraic':     [('lattice',1.6),('polygon',1.2),('arc',0.8),('line',0.5)],
    'recursive':     [('tree',1.8),('spiral',1.4),('orbit',0.8),('dot',0.4)],
}


def _extract_math_params(result_seed: int, fn_name: str,
                          inputs: dict = None) -> dict:
    """
    Convert a mathematical result and inputs into visual parameters.

    Returns a dict that render_art_pil uses to modulate generation.
    These parameters sit BETWEEN the profile (which sets mood/color)
    and the random seed (which sets specific positions).

    The profile says: "use neon colors, thin strokes, these opacity ranges"
    The math params say: "make the waves fast, bias composition upward, spread wide"
    The seed says: "place this specific stroke at these exact coordinates"

    All three layers combine — the same function with the same profile
    and different seeds produces clearly related but distinct pieces.
    The same seed with a different function produces clearly different work.

    Parameters returned:
        fn_class        str   — mathematical character class
        stroke_family   list  — [(stroke_type, weight)] from class
        freq_mult       float — frequency multiplier [0.5, 3.0]
                                low = slow/sparse waves, high = rapid/dense
        size_bias       float — size scaling bias [0.6, 1.8]
                                low = tight/small strokes, high = large/expansive
        angle_bias      float — preferred angle in degrees [0, 360]
                                strokes biased toward this direction
        angle_spread    float — how tightly strokes cluster around angle_bias
                                low = highly directional, high = omnidirectional
        focal_spread    float — composition focal spread [0.08, 0.45]
                                low = tight cluster, high = loose/scattered
        focal_offset_x  float — focal point x-offset [−0.25, 0.25] of canvas
        focal_offset_y  float — focal point y-offset [−0.25, 0.25] of canvas
        color_shift     int   — index shift in palette [0, len(palette)-1]
                                0 = normal palette order, higher = shifted
        layer_weight    float — relative weight of math vs profile strokes [0.3, 0.9]
                                how strongly math class dominates over profile style
    """
    fn_class     = _classify_function(fn_name)
    stroke_family= _CLASS_STROKES.get(fn_class, _CLASS_STROKES['algebraic'])

    # Normalize result_seed to [0, 1] for parameter mapping
    # result_seed is the first integer extracted from the calculation result
    r = (result_seed % 100000) / 100000.0   # 0.0 → 1.0, stable across any magnitude

    # ── Frequency ─────────────────────────────────────────────────────────────
    # Periodic functions: result value maps directly to visual frequency
    # A high-frequency sine output (many cycles) → dense fast waves
    # A low-frequency output → slow undulating composition
    if fn_class == 'periodic':
        freq_mult = 0.5 + r * 2.5           # 0.5–3.0 — full range
    elif fn_class in ('dynamic', 'differential'):
        freq_mult = 0.8 + r * 1.2           # 0.8–2.0 — moderate variation
    else:
        freq_mult = 0.7 + r * 0.8           # 0.7–1.5 — subtle

    # ── Size bias ─────────────────────────────────────────────────────────────
    # Large result values → expansive strokes filling the canvas
    # Small result values → tight, concentrated strokes
    # Probabilistic functions: spread = uncertainty = wide size range
    if fn_class == 'probabilistic':
        size_bias = 0.6 + r * 1.2           # varies widely
    elif fn_class == 'combinatorial':
        size_bias = 0.7 + (1.0 - r) * 0.8  # small r = many items = denser
    elif fn_class == 'topological':
        size_bias = 0.9 + r * 0.6           # topological = continuous = medium-large
    else:
        size_bias = 0.7 + r * 0.8           # 0.7–1.5

    # ── Angle bias ────────────────────────────────────────────────────────────
    # Maps result value to a preferred compass direction.
    # This makes the piece feel "directed" by the math — a momentum
    # calculation pointing right vs left depending on the sign of velocity.
    angle_bias   = r * 360.0

    # Angle spread: how tightly strokes cluster around the bias direction
    # Differential functions are highly directional (gradient has a direction)
    # Probabilistic functions are omnidirectional (probability has no direction)
    if fn_class == 'differential':
        angle_spread = 30 + r * 40          # 30–70° spread — very directional
    elif fn_class in ('probabilistic', 'statistical'):
        angle_spread = 180.0                # no directional preference
    elif fn_class == 'periodic':
        angle_spread = 60 + r * 60         # 60–120° — moderate directionality
    else:
        angle_spread = 90 + r * 90         # 90–180°

    # ── Focal spread ──────────────────────────────────────────────────────────
    # How tightly the composition clusters vs spreads across the canvas.
    # Topological = continuous, connected = tight
    # Statistical = distributed = spread
    if fn_class in ('topological', 'recursive'):
        focal_spread = 0.10 + r * 0.15     # 0.10–0.25 — tight, self-referential
    elif fn_class in ('probabilistic', 'statistical'):
        focal_spread = 0.25 + r * 0.20     # 0.25–0.45 — wide distribution
    elif fn_class == 'geometric':
        focal_spread = 0.15 + r * 0.15     # 0.15–0.30 — moderate, proportional
    else:
        focal_spread = 0.12 + r * 0.25     # 0.12–0.37

    # ── Focal offset ──────────────────────────────────────────────────────────
    # The composition focal point sits at a result-derived offset from centre.
    # This means two different results produce different compositional balance.
    # Inputs modulate this — first two input values set x/y offset direction.
    if inputs:
        vals = [float(v) for v in inputs.values()
                if isinstance(v, (int, float))][:2]
        if len(vals) >= 2:
            a, b = vals[0], vals[1]
            mag  = max(abs(a), abs(b), 1e-9)
            focal_offset_x = (a / mag) * 0.18 * r
            focal_offset_y = (b / mag) * 0.18 * r
        elif len(vals) == 1:
            focal_offset_x = 0.10 * r * (1 if vals[0] >= 0 else -1)
            focal_offset_y = 0.08 * (r - 0.5)
        else:
            focal_offset_x = focal_offset_y = 0.0
    else:
        # No input data — derive from result
        focal_offset_x = 0.15 * math.cos(math.radians(angle_bias))
        focal_offset_y = 0.15 * math.sin(math.radians(angle_bias))

    # ── Color selection — math drives which colors are used ─────────────────
    # Profile provides the color menu. Math decides what to order.
    #
    # primary_color_r: float [0,1] — which palette slot is the dominant color.
    #   Derived from result value. Same function with different result → different
    #   dominant color drawn from the profile's available colors.
    #
    # secondary_color_r: float [0,1] — secondary color slot.
    #   Derived from the first input value (or result if no inputs).
    #   The relationship between primary and secondary colors changes per calculation.
    #
    # color_distribution: how colors are weighted across strokes.
    #   Each function class has a characteristic distribution pattern:
    #
    #   focused     → one dominant color, others barely present
    #                 (geometric: a shape has one identity)
    #   dual        → two colors roughly equal, rest suppressed
    #                 (differential: gradient has two sides)
    #   spread      → all colors roughly equal weight
    #                 (probabilistic: probability is uniform)
    #   oscillating → colors alternate in a cycle driven by result frequency
    #                 (periodic: color cycles like the function itself)
    #   gradient    → smooth falloff from primary toward edges of palette
    #                 (topological: continuity, no hard edges)
    #   cascade     → exponentially weighted from primary
    #                 (recursive: self-similar dominance)
    #
    # dominant_strength: float [1.5, 6.0] — how much stronger the primary is.
    #   Low = subtle color preference. High = one color dominates strongly.
    #
    # alpha_scale: float [0.6, 1.0] — scales all alpha ranges.
    #   Result-driven: large results = more opaque strokes.
    #   Lets the math control visual weight/presence of strokes.

    primary_color_r   = r                    # [0,1] — maps to palette index

    if inputs:
        vals = [float(v) for v in inputs.values() if isinstance(v, (int, float))]
        if vals:
            # First input value → secondary color, normalized to [0,1]
            v0 = vals[0]
            secondary_color_r = (abs(v0) % 100) / 100.0
        else:
            secondary_color_r = (1.0 - r)    # complement of primary
    else:
        secondary_color_r = (r + 0.5) % 1.0  # opposite side of palette

    # Function class → color distribution pattern
    _color_dist_map = {
        'periodic':      'oscillating',   # cycles like the function
        'differential':  'dual',          # gradient = two directions
        'probabilistic': 'spread',        # uncertainty = no preference
        'statistical':   'spread',        # data = all colors present
        'geometric':     'focused',       # shape = one identity
        'combinatorial': 'cascade',       # counting = exponential weight
        'dynamic':       'dual',          # energy = primary + accent
        'topological':   'gradient',      # continuity = smooth falloff
        'algebraic':     'focused',       # structure = single dominant
        'recursive':     'cascade',       # self-similar = exponential
    }
    color_distribution = _color_dist_map.get(fn_class, 'focused')

    # Dominant strength — how much the primary color overpowers the rest
    if fn_class in ('geometric', 'algebraic'):
        dominant_strength = 4.0 + r * 2.0    # 4–6: very focused
    elif fn_class in ('probabilistic', 'statistical'):
        dominant_strength = 1.2 + r * 0.6    # 1.2–1.8: nearly uniform
    elif fn_class == 'periodic':
        dominant_strength = 2.0 + r * 1.5    # 2–3.5: moderate oscillation
    else:
        dominant_strength = 2.5 + r * 1.5    # 2.5–4: moderate dominance

    # Alpha scale — result value controls overall opacity/presence
    alpha_scale = 0.6 + r * 0.4              # 0.6–1.0

    # ── Layer weight ─────────────────────────────────────────────────────────
    # How strongly the math class stroke vocabulary dominates over profile strokes.
    # Recursive and topological classes are strongly math-character-driven.
    # Algebraic and statistical blend more with the profile.
    if fn_class in ('recursive', 'topological', 'periodic'):
        layer_weight = 0.75
    elif fn_class in ('probabilistic', 'statistical'):
        layer_weight = 0.50
    else:
        layer_weight = 0.60

    return {
        'fn_class':       fn_class,
        'stroke_family':  stroke_family,
        'freq_mult':      freq_mult,
        'size_bias':      size_bias,
        'angle_bias':     angle_bias,
        'angle_spread':   angle_spread,
        'focal_spread':   focal_spread,
        'focal_offset_x': focal_offset_x,
        'focal_offset_y': focal_offset_y,
        'primary_color_r':    primary_color_r,
        'secondary_color_r':  secondary_color_r,
        'color_distribution': color_distribution,
        'dominant_strength':  dominant_strength,
        'alpha_scale':        alpha_scale,
        'layer_weight':       layer_weight,
    }


def _blend_strokes(math_strokes: list, profile_strokes: list,
                   layer_weight: float) -> list:
    """
    Blend math class stroke vocabulary with profile stroke weights.

    math_strokes:    [(type, weight)] from function class
    profile_strokes: [(type, weight)] from active profile
    layer_weight:    0.0 = pure profile, 1.0 = pure math class

    Result: a merged list where both contribute proportionally.
    Math class types are boosted, profile-only types are present but secondary.
    This means:
      - A periodic function always has more wave strokes than a geometric one
      - But the neon_city profile makes them thin and electric
      - And the organic profile makes them thick and flowing
    """
    math_dict    = dict(math_strokes)
    profile_dict = dict(profile_strokes)
    all_types    = set(math_dict) | set(profile_dict)

    blended = []
    for stroke_type in all_types:
        math_w    = math_dict.get(stroke_type, 0.0)
        profile_w = profile_dict.get(stroke_type, 0.0)
        w = math_w * layer_weight + profile_w * (1.0 - layer_weight)
        if w > 0:
            blended.append((stroke_type, w))

    return blended


def _build_color_weights(palette: list, mp: dict) -> list:
    """
    Build per-color weights from math parameters.

    palette: [(hex, alpha_min, alpha_max), ...] — from effective_palette()
    mp:      math params from _extract_math_params()

    Returns: [weight_float, ...] — one weight per palette entry, same order.
    The caller uses these weights in weighted_choice() instead of the
    profile's original weights, which are discarded.

    Distribution patterns:
      focused     — one color at dominant_strength, others at 1.0
      dual        — primary at dominant_strength, secondary at dominant_strength×0.6
      spread      — all equal (1.0)
      oscillating — cosine wave across palette indexed by primary_color_r
      gradient    — linear falloff from primary index outward
      cascade     — exponential decay from primary index
    """
    n = len(palette)
    if n == 0:
        return []

    primary_r   = mp.get('primary_color_r',   0.0)
    secondary_r = mp.get('secondary_color_r', 0.5)
    dist        = mp.get('color_distribution', 'focused')
    strength    = mp.get('dominant_strength',  3.0)

    primary_idx   = int(primary_r   * n) % n
    secondary_idx = int(secondary_r * n) % n

    weights = [1.0] * n

    if dist == 'focused':
        weights[primary_idx] = strength

    elif dist == 'dual':
        weights[primary_idx]   = strength * 0.65
        weights[secondary_idx] = strength * 0.45

    elif dist == 'spread':
        # All colors equally weighted — pure uniform
        pass

    elif dist == 'oscillating':
        # Cosine wave through palette, phase set by primary_color_r
        # A periodic function with r=0.2 gets a different color cycle than r=0.8
        phase = primary_r * 2 * math.pi
        for i in range(n):
            theta = 2 * math.pi * i / n + phase
            weights[i] = max(0.1, 1.0 + (strength - 1.0) * 0.5 * (1 + math.cos(theta)))

    elif dist == 'gradient':
        # Smooth falloff from primary index — continuous, no hard edge
        for i in range(n):
            dist_from_primary = min(abs(i - primary_idx),
                                    n - abs(i - primary_idx))  # wrap-around
            weights[i] = max(0.1, strength - (strength - 1.0) * dist_from_primary / (n / 2))

    elif dist == 'cascade':
        # Exponential decay from primary — each step away is much weaker
        # Recursive/combinatorial: like factorial, each level is a fraction
        decay = 0.35
        for i in range(n):
            dist_from_primary = min(abs(i - primary_idx),
                                    n - abs(i - primary_idx))
            weights[i] = strength * (decay ** dist_from_primary)
            weights[i] = max(0.05, weights[i])

    return weights


def generate_rule(master_seed: int, index: int, domain: str = 'default',
                  profile: GenerationProfile = None,
                  math_params: dict = None) -> dict:
    """
    Full Determiner Logic pipeline.
    Seed → RNG Splitter → Weight Engine → Fallback Resolver → Stroke Rule

    math_params (from _extract_math_params) modulates the output:
        - stroke_family blended with profile stroke_weights
        - freq_mult scales frequency within profile's freq_range
        - size_bias scales size within profile's size_range
        - angle_bias + angle_spread constrain angle selection
        - color_shift rotates which palette color is dominant

    Without math_params: behavior is identical to original.
    With math_params: same profile + different function = different strokes.
    """
    prof = profile or ACTIVE_PROFILE
    sub  = split_seed(master_seed ^ (index * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFF)
    rng  = random.Random(sub[0])

    prof = prof.jitter(rng)

    palette = prof.effective_palette(domain)   # (color, weight, alpha_min, alpha_max)

    # ── Stroke selection: blend math class with profile ───────────────────────
    if math_params:
        profile_strokes = prof.effective_strokes(domain)
        blended_strokes = _blend_strokes(
            math_params['stroke_family'],
            profile_strokes,
            math_params['layer_weight'],
        )
        stroke = weighted_choice(rng, blended_strokes)
    else:
        styles = prof.effective_strokes(domain)
        stroke = weighted_choice(rng, styles)

    # ── Color selection: math drives which color is used ────────────────────
    # Profile = available color menu.  Math = what gets ordered from it.
    #
    # _build_color_weights() produces per-slot weights derived entirely from
    # result value, inputs, and function class. Same profile + different
    # function → different color distribution from the same palette.
    #
    # Without math_params: uniform weights — any palette color equally likely.
    if math_params:
        color_weights = _build_color_weights(palette, math_params)
        color_pairs   = [(palette[i][0], color_weights[i]) for i in range(len(palette))]
        color_entry   = weighted_choice(rng, color_pairs)
        alpha_min, alpha_max = 120, 255
        for hex_c, amin, amax in palette:
            if hex_c == color_entry:
                alpha_min, alpha_max = amin, amax
                break
        # alpha_scale: result value modulates overall opacity/presence
        a_sc = math_params.get('alpha_scale', 1.0)
        alpha_min = int(alpha_min * a_sc)
        alpha_max = int(alpha_max * a_sc)
    else:
        # No math context — uniform color distribution
        color_entry = rng.choice([c for c, _, _ in palette])
        alpha_min, alpha_max = 120, 255
        for hex_c, amin, amax in palette:
            if hex_c == color_entry:
                alpha_min, alpha_max = amin, amax
                break

    alpha_max = max(alpha_min + 1, alpha_max)
    alpha = rng.randint(alpha_min, alpha_max)
    t_min, t_max = prof.thickness_range
    s_min, s_max = prof.size_range
    f_min, f_max = prof.freq_range

    thickness = rng.randint(t_min, t_max)

    # ── Size: apply size_bias from math params ────────────────────────────────
    if math_params:
        sb    = math_params['size_bias']
        bias_min = int(s_min * sb)
        bias_max = int(s_max * sb)
        size  = rng.randint(max(2, bias_min), max(3, bias_max))
    else:
        size = rng.randint(s_min, s_max)

    # ── Angle: apply angle_bias + spread from math params ────────────────────
    if math_params:
        bias   = math_params['angle_bias']
        spread = math_params['angle_spread']
        # Draw angle from Gaussian around bias, clipped to spread
        raw = rng.gauss(bias, spread)
        angle = raw % 360
    else:
        angle = prof.angle_for(stroke, rng)

    # ── Frequency: apply freq_mult from math params ───────────────────────────
    if math_params:
        fm   = math_params['freq_mult']
        freq = rng.uniform(f_min * fm, f_max * fm)
        freq = max(0.1, freq)
    else:
        freq = rng.uniform(f_min, f_max)

    rule = {
        'stroke':    stroke,
        'color':     color_entry,
        'thickness': thickness,
        'alpha':     alpha,
        'size':      size,
        'angle':     angle,
        'freq':      freq,
    }
    return resolve_fallback(rule)

# ══════════════════════════════════════════════════════════════════════════════
# PRICING STRATEGY MODULE
# ══════════════════════════════════════════════════════════════════════════════

RARE_COLORS = {'#FF006E', '#7B61FF', '#FFFFFF'}
ULTRA_RARE_STROKES = {'spiral', 'orbit', 'tree', 'wave'}

# ── Rarity distribution targets ───────────────────────────────────────────────
# Common 50% | Uncommon 25% | Rare 15% | Ultra Rare 8% | Legendary 2%
_RARITY_THRESHOLDS = [
    (0.02,  'Legendary'),
    (0.10,  'Ultra Rare'),
    (0.25,  'Rare'),
    (0.50,  'Uncommon'),
    (1.00,  'Common'),
]

def score_complexity(strokes: list) -> int:
    """
    Complexity score 1–100.
    Based on structural diversity, not raw stroke count, so it
    produces a meaningful spread rather than a flat ~416 every time.
    """
    if not strokes: return 1
    n = len(strokes)

    # How many distinct stroke types and colors are used?
    unique_types  = len(set(s['stroke'] for s in strokes))   # max ~14
    unique_colors = len(set(s['color']  for s in strokes))   # max ~5

    # Average size and thickness variation — higher variance = more complex
    sizes      = [s['size']      for s in strokes]
    thicknesses= [s['thickness'] for s in strokes]
    avg_size   = sum(sizes) / n
    var_size   = sum((x - avg_size)**2 for x in sizes) / n
    avg_thick  = sum(thicknesses) / n
    var_thick  = sum((x - avg_thick)**2 for x in thicknesses) / n

    # Presence of structurally complex stroke types
    complex_present = sum(1 for s in strokes if s['stroke'] in
                          {'spiral','orbit','tree','wave','curve','radial'})
    complex_frac    = complex_present / n  # 0.0–1.0

    # Composite — each term contributes to a 0–100 range
    type_score    = min(30, unique_types  * 3)       # 0–30  (10 types = 30)
    color_score   = min(20, unique_colors * 4)       # 0–20  (5 colors = 20)
    var_score     = min(20, (var_size / 400) * 20)   # 0–20
    thick_score   = min(10, (var_thick / 2) * 10)    # 0–10
    complex_score = min(20, complex_frac * 40)       # 0–20

    return max(1, round(type_score + color_score + var_score + thick_score + complex_score))

def detect_rarity(strokes: list, seed: int = None) -> str:
    """
    Rarity determined primarily by a seed-based probability roll so the
    distribution is statistically correct across many pieces:
      Common 50% | Uncommon 25% | Rare 15% | Ultra Rare 8% | Legendary 2%

    The roll is then optionally bumped UP one tier if the piece has genuine
    structural complexity (diverse stroke types + at least one rare type present).
    Seed-based so the same input always produces the same rarity.
    """
    if not strokes: return 'Common'

    # Primary: weighted probability roll from seed
    rng  = random.Random((seed or 0) ^ 0xDEADBEEF)
    roll = rng.random()

    base_rarity = 'Common'
    for threshold, tier in _RARITY_THRESHOLDS:
        if roll < threshold:
            base_rarity = tier
            break

    # Secondary: structural bonus — can bump up one tier only
    # Requires genuinely diverse and rare-type-heavy artwork
    unique_types   = len(set(s['stroke'] for s in strokes))
    rare_type_count = sum(1 for s in strokes if s['stroke'] in ULTRA_RARE_STROKES)
    rare_type_frac  = rare_type_count / len(strokes)
    # Only bump if 7+ distinct stroke types AND rare types make up 20%+ of strokes
    eligible_bump  = unique_types >= 7 and rare_type_frac >= 0.20

    if eligible_bump:
        tiers = ['Common', 'Uncommon', 'Rare', 'Ultra Rare', 'Legendary']
        idx   = tiers.index(base_rarity)
        if idx < 4:
            base_rarity = tiers[idx + 1]

    return base_rarity

def calculate_price(complexity: int, rarity: str) -> float:
    """
    Internal MathCoin (ℳ) price — 1–100 range.
    complexity is now 1–100, so base = complexity / 10 → 0.1–10 ℳ,
    then multiplied by rarity tier.
    """
    base        = complexity / 10.0          # 0.1–10.0
    multipliers = {
        'Common':     1.0,    # 0.1 – 10.0 ℳ
        'Uncommon':   2.0,    # 0.2 – 20.0 ℳ
        'Rare':       4.0,    # 0.4 – 40.0 ℳ
        'Ultra Rare': 7.0,    # 0.7 – 70.0 ℳ
        'Legendary':  12.0,   # 1.2 – 120.0 ℳ  (only ~2% of pieces)
    }
    return round(base * multipliers.get(rarity, 1.0), 2)

RARITY_COLOR = {
    'Common':     '#6e7681',
    'Uncommon':   '#00FF9F',
    'Rare':       '#00D4FF',
    'Ultra Rare': '#7B61FF',
    'Legendary':  '#FFE600',
}

# ── Session export directory ──────────────────────────────────────────────────
# Anchored to the directory containing MathCodeEngine.py — never relative to cwd.
# Format:  <script_dir>/mathcode_art/{short_id}_{YYYY-MM-DD}_{HH-MM-SS}
_SESSION_ID   = uuid.uuid4().hex[:8].upper()
_SESSION_TIME = time.strftime('%Y-%m-%d_%H-%M-%S')
_SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
SESSION_DIR   = os.path.join(
    _SCRIPT_DIR,
    'mathcode_art',
    f'{_SESSION_ID}_{_SESSION_TIME}'
)

# ══════════════════════════════════════════════════════════════════════════════
# CANVAS RENDERER
# ══════════════════════════════════════════════════════════════════════════════

SIZE = 3000  # output resolution — 3000×3000 = print-quality at 300dpi up to 10×10"
             # For 18×24" prints at 300dpi set to 5400. For fast preview use 512.
             # Change via:  import MathCodeEngine; MathCodeEngine.SIZE = 512
             # or set MATHCODE_SIZE env var before import.
import os as _os
_env_size = _os.getenv('MATHCODE_SIZE')
if _env_size and _env_size.isdigit():
    SIZE = int(_env_size)

def _hex_to_rgb(hex_color: str, alpha: int = 255) -> tuple:
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return (r, g, b, alpha)

def _draw_stroke_pil(draw, rule: dict, cx: float, cy: float) -> None:
    """Render a single stroke rule onto a PIL ImageDraw context."""
    import PIL.ImageDraw  # ensure import
    color = _hex_to_rgb(rule['color'], rule['alpha'])
    s     = rule['size']
    t     = rule['thickness']
    a     = rule['angle']
    f     = rule['freq']

    kind = rule['stroke']
    x, y = int(cx), int(cy)

    if kind == 'line':
        rad = math.radians(a)
        x2  = int(x + s * math.cos(rad))
        y2  = int(y + s * math.sin(rad))
        draw.line([(x,y),(x2,y2)], fill=color, width=t)

    elif kind == 'arc':
        r = s // 2
        draw.arc([x-r, y-r, x+r, y+r], start=int(a), end=int(a+180), fill=color, width=t)

    elif kind == 'dot':
        r = max(2, s // 6)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color)

    elif kind == 'orbit':
        for k in range(0, 360, 30):
            rad_k = math.radians(k)
            xi = int(x + s * math.cos(rad_k))
            yi = int(y + s * math.sin(rad_k))
            draw.ellipse([xi-2, yi-2, xi+2, yi+2], fill=color)
        draw.ellipse([x-s, y-s, x+s, y+s], outline=color, width=max(1, t-1))

    elif kind == 'spiral':
        pts = []
        for k in range(60):
            r_k   = k * s / 60
            rad_k = math.radians(k * f * 6)
            pts.append((int(x + r_k*math.cos(rad_k)), int(y + r_k*math.sin(rad_k))))
        if len(pts) > 1:
            draw.line(pts, fill=color, width=t)

    elif kind == 'wave':
        pts = []
        for k in range(-s, s+1, 2):
            wave_y = int(y + (s//3) * math.sin(math.radians(k * f * 10 + a)))
            pts.append((x + k, wave_y))
        if len(pts) > 1:
            draw.line(pts, fill=color, width=t)

    elif kind == 'vector':
        rad   = math.radians(a)
        x2, y2 = int(x + s*math.cos(rad)), int(y + s*math.sin(rad))
        draw.line([(x,y),(x2,y2)], fill=color, width=t)
        # arrowhead
        for da in (30, -30):
            rad2 = math.radians(a + 180 + da)
            ax  = int(x2 + 8*math.cos(rad2))
            ay  = int(y2 + 8*math.sin(rad2))
            draw.line([(x2,y2),(ax,ay)], fill=color, width=t)

    elif kind == 'lattice':
        spacing = max(4, s // 4)
        for dx in range(-s, s+1, spacing):
            draw.line([(x+dx, y-s),(x+dx, y+s)], fill=color, width=max(1,t-1))
        for dy in range(-s, s+1, spacing):
            draw.line([(x-s, y+dy),(x+s, y+dy)], fill=color, width=max(1,t-1))

    elif kind == 'grid':
        r = s
        draw.rectangle([x-r, y-r, x+r, y+r], outline=color, width=t)
        draw.line([(x-r,y),(x+r,y)], fill=color, width=t)
        draw.line([(x,y-r),(x,y+r)], fill=color, width=t)

    elif kind == 'polygon':
        sides = max(3, int(f * 2 + 3))
        pts2  = []
        for k in range(sides):
            rad_k = math.radians(k * 360 / sides + a)
            pts2.append((int(x + s*math.cos(rad_k)), int(y + s*math.sin(rad_k))))
        draw.polygon(pts2, outline=color)

    elif kind == 'scatter':
        for k in range(8):
            rng2 = random.Random(x * 31 + y * 17 + k)
            sx = x + rng2.randint(-s, s)
            sy = y + rng2.randint(-s, s)
            r  = rng2.randint(1, 4)
            draw.ellipse([sx-r, sy-r, sx+r, sy+r], fill=color)

    elif kind == 'curve':
        pts = []
        for k in range(0, 361, 10):
            rad_k = math.radians(k)
            rx_k  = s * math.cos(rad_k)
            ry_k  = (s//2) * math.sin(2*rad_k + math.radians(a))
            pts.append((int(x+rx_k), int(y+ry_k)))
        if len(pts) > 1:
            draw.line(pts, fill=color, width=t)

    elif kind == 'radial':
        spokes = 12
        for k in range(spokes):
            rad_k = math.radians(k * 360 / spokes + a)
            x2r   = int(x + s*math.cos(rad_k))
            y2r   = int(y + s*math.sin(rad_k))
            draw.line([(x,y),(x2r,y2r)], fill=color, width=t)

    elif kind == 'tree':
        def _branch(d, bx, by, ba, bl):
            if bl < 3 or d > 5: return
            rad_b = math.radians(ba)
            ex    = int(bx + bl * math.cos(rad_b))
            ey    = int(by + bl * math.sin(rad_b))
            draw.line([(bx,by),(ex,ey)], fill=color, width=max(1, d))
            _branch(d+1, ex, ey, ba-25, bl*0.7)
            _branch(d+1, ex, ey, ba+25, bl*0.7)
        _branch(1, x, y, a-90, s)


def render_art_pil(master_seed: int, domain: str, n_strokes: int = None,
                   fn_name: str = '', inputs: dict = None,
                   result_seed: int = None) -> tuple:
    """
    Render a full PIL artwork.

    fn_name and inputs are now used to derive visual parameters so that
    different mathematical functions produce structurally different art,
    not just different random seeds of the same visual language.

    See _extract_math_params() for the full mapping.
    """
    prof = ACTIVE_PROFILE
    if n_strokes is None:
        scale     = SIZE / 512
        n_strokes = max(80, int(prof.n_strokes * scale * 0.6))

    S = SIZE / 512

    # ── Extract math-driven parameters ───────────────────────────────────────
    seed_for_math = result_seed if result_seed is not None else master_seed
    mp = _extract_math_params(seed_for_math, fn_name, inputs) if fn_name else None

    # Parse background color
    try:
        bh = prof.bg_color.lstrip('#')
        bg = (int(bh[0:2],16), int(bh[2:4],16), int(bh[4:6],16), 255)
    except Exception:
        bg = (8, 11, 15, 255)

    img  = Image.new('RGBA', (SIZE, SIZE), bg)
    draw = ImageDraw.Draw(img, 'RGBA')
    rng  = random.Random(master_seed)

    # ── Compositional focal point ─────────────────────────────────────────────
    # Base offset from seed
    cx_canvas = SIZE // 2
    cy_canvas = SIZE // 2

    if mp:
        # Math-derived focal offset: result value determines where the
        # composition "leans" — a force pointing right shifts the focal
        # point right, a negative value shifts it left
        focal_x = int(cx_canvas + mp['focal_offset_x'] * SIZE)
        focal_y = int(cy_canvas + mp['focal_offset_y'] * SIZE)
        # Small additional seed-based jitter so same function + different
        # seeds still produces varied compositions
        focal_x += int(rng.gauss(0, SIZE * 0.05))
        focal_y += int(rng.gauss(0, SIZE * 0.05))
        focal_spread = mp['focal_spread']
    else:
        focal_x = cx_canvas + int(rng.gauss(0, SIZE * 0.08))
        focal_y = cy_canvas + int(rng.gauss(0, SIZE * 0.08))
        focal_spread = 0.20

    # ── Composition layers ────────────────────────────────────────────────────
    anchor_count  = max(1, int(n_strokes * 0.20))
    mid_count     = max(1, int(n_strokes * 0.50))
    scatter_count = n_strokes - anchor_count - mid_count

    strokes = []
    stroke_idx = 0

    def _place(layer: str) -> tuple:
        if layer == 'anchor':
            r = SIZE * focal_spread * 0.6
            return (focal_x + int(rng.gauss(0, r)),
                    focal_y + int(rng.gauss(0, r)))
        elif layer == 'mid':
            r = SIZE * focal_spread * 1.5
            return (focal_x + int(rng.gauss(0, r)),
                    focal_y + int(rng.gauss(0, r)))
        else:
            return (int(rng.gauss(cx_canvas, SIZE * 0.38)),
                    int(rng.gauss(cy_canvas, SIZE * 0.38)))

    def _scaled(rule: dict) -> dict:
        r = dict(rule)
        r['size']      = max(int(r['size']      * S), int(S))
        r['thickness'] = max(int(r['thickness'] * S), int(S * 0.8))
        return r

    for layer, count in [('anchor', anchor_count),
                          ('mid',    mid_count),
                          ('scatter',scatter_count)]:
        for _ in range(count):
            rule = generate_rule(master_seed, stroke_idx, domain, prof,
                                 math_params=mp)
            # Size modulation by layer (independent of math params)
            s_min, s_max = prof.size_range
            if layer == 'anchor':
                rule['size'] = rng.randint((s_min + s_max)//2, s_max)
            elif layer == 'scatter':
                rule['size'] = rng.randint(s_min, (s_min + s_max)//2)

            rule = _scaled(rule)
            pcx, pcy = _place(layer)
            pcx = max(0, min(SIZE-1, pcx))
            pcy = max(0, min(SIZE-1, pcy))
            _draw_stroke_pil(draw, rule, pcx, pcy)
            strokes.append(rule)
            stroke_idx += 1

    # Vignette
    vignette = Image.new('RGBA', (SIZE, SIZE), (0,0,0,0))
    vdraw    = ImageDraw.Draw(vignette, 'RGBA')
    for r_vign in range(SIZE//2, 0, -max(1, SIZE//60)):
        alpha_v = int(60 * (1 - r_vign/(SIZE//2))**3)
        vdraw.ellipse(
            [SIZE//2-r_vign, SIZE//2-r_vign,
             SIZE//2+r_vign, SIZE//2+r_vign],
            outline=bg[:3]+(alpha_v,), width=max(1, SIZE//300)
        )
    img = Image.alpha_composite(img, vignette)
    return img.convert('RGB'), strokes
    """
    Render a full PIL artwork at production resolution.

    CHANGES FROM ORIGINAL:
    ── Grid removed ──────────────────────────────────────────────────────────
        The subtle background grid has been removed entirely. At 512px it
        read as texture. At 3000px+ it reads as graph paper and looks
        unfinished on prints. Background is now a pure solid color with an
        optional very faint radial vignette only.

    ── Resolution-aware stroke scaling ───────────────────────────────────────
        Stroke sizes and thicknesses were absolute pixel values calibrated
        for 512px. At 3000px every stroke was microscopic — thin scratches
        on a large canvas. All sizes and thicknesses now scale proportionally
        with the canvas: scale = SIZE / 512. A stroke that was 30px at 512px
        becomes 175px at 3000px — the same visual weight at any resolution.

    ── Compositional gravity ─────────────────────────────────────────────────
        Original placement: pure random scatter across the entire canvas.
        Result: even density everywhere — no focal point, no visual hierarchy.

        New placement: three-layer composition model.

        Layer 1 — anchor (20% of strokes):
            Placed near the canvas centre (±15% of canvas size).
            These are the large, defining strokes that give the piece
            its identity. They use the full size_range maximum.

        Layer 2 — mid-field (50% of strokes):
            Placed within ±35% of canvas centre, biased slightly off-centre
            via a rng-seeded offset. Medium sizes. These are the strokes that
            fill out the composition and create visual complexity.

        Layer 3 — scatter (30% of strokes):
            Placed anywhere on the canvas. Small sizes. These provide the
            texture and breathing room that prevents the composition from
            looking too centred or mechanical.

        The result is a piece with a readable focal region and organic
        falloff toward the edges — how a human artist would compose a canvas.

    ── Stroke count scaled with resolution ───────────────────────────────────
        200 strokes at 512px created dense, busy output.
        200 strokes at 3000px would look like a few scattered marks.
        Default n_strokes is now drawn from the profile and scaled:
            effective_strokes = profile.n_strokes × (SIZE / 512) × 0.6
        The 0.6 factor prevents over-density — scaled strokes are physically
        larger, so fewer of them fills the canvas appropriately.

    Returns (Image, list_of_strokes).
    """
    prof = ACTIVE_PROFILE
    if n_strokes is None:
        # Scale stroke count with resolution, but not linearly —
        # larger strokes fill more space so we need fewer of them
        scale     = SIZE / 512
        n_strokes = max(80, int(prof.n_strokes * scale * 0.6))

    # Scale factor for converting 512px-calibrated sizes to current SIZE
    S = SIZE / 512  # e.g. 5.86 at 3000px

    # Parse background color
    try:
        bh = prof.bg_color.lstrip('#')
        bg = (int(bh[0:2],16), int(bh[2:4],16), int(bh[4:6],16), 255)
    except Exception:
        bg = (8, 11, 15, 255)

    img  = Image.new('RGBA', (SIZE, SIZE), bg)
    draw = ImageDraw.Draw(img, 'RGBA')
    rng  = random.Random(master_seed)

    # No grid — removed entirely

    # Compositional gravity: define placement regions
    cx_canvas = SIZE // 2
    cy_canvas = SIZE // 2

    # Slight compositional offset per seed — varies per piece, not mechanical
    offset_x = int(rng.gauss(0, SIZE * 0.08))
    offset_y = int(rng.gauss(0, SIZE * 0.08))
    focal_x  = cx_canvas + offset_x
    focal_y  = cy_canvas + offset_y

    anchor_count  = max(1, int(n_strokes * 0.20))  # Layer 1 — centre-heavy
    mid_count     = max(1, int(n_strokes * 0.50))  # Layer 2 — mid-field
    scatter_count = n_strokes - anchor_count - mid_count  # Layer 3 — full canvas

    strokes = []
    stroke_idx = 0

    def _place_stroke(layer: str) -> tuple:
        """Return (cx, cy) for a stroke based on compositional layer."""
        if layer == 'anchor':
            # Tight cluster around focal point
            radius = SIZE * 0.15
            return (
                focal_x + int(rng.gauss(0, radius)),
                focal_y + int(rng.gauss(0, radius)),
            )
        elif layer == 'mid':
            # Wider spread, still biased toward focal
            radius = SIZE * 0.35
            return (
                focal_x + int(rng.gauss(0, radius)),
                focal_y + int(rng.gauss(0, radius)),
            )
        else:
            # Full canvas scatter — with slight centre pull
            return (
                int(rng.gauss(cx_canvas, SIZE * 0.38)),
                int(rng.gauss(cy_canvas, SIZE * 0.38)),
            )

    def _scaled_rule(rule: dict) -> dict:
        """Scale stroke size and thickness from 512px baseline to current SIZE."""
        r = dict(rule)
        r['size']      = max(int(r['size']      * S), int(S))
        r['thickness'] = max(int(r['thickness'] * S), int(S * 0.8))
        return r

    for layer, count in [('anchor', anchor_count),
                          ('mid',    mid_count),
                          ('scatter',scatter_count)]:
        for _ in range(count):
            rule = generate_rule(master_seed, stroke_idx, domain, prof)
            # Anchor layer: prefer large strokes — use upper half of size range
            if layer == 'anchor':
                s_min, s_max = prof.size_range
                rule['size'] = rng.randint((s_min + s_max)//2, s_max)
            # Scatter layer: prefer small strokes
            elif layer == 'scatter':
                s_min, s_max = prof.size_range
                rule['size'] = rng.randint(s_min, (s_min + s_max)//2)

            rule = _scaled_rule(rule)
            pcx, pcy = _place_stroke(layer)
            # Clamp to canvas bounds
            pcx = max(0, min(SIZE-1, pcx))
            pcy = max(0, min(SIZE-1, pcy))
            _draw_stroke_pil(draw, rule, pcx, pcy)
            strokes.append(rule)
            stroke_idx += 1

    # Subtle vignette — darkens edges slightly, no grid
    vignette = Image.new('RGBA', (SIZE, SIZE), (0,0,0,0))
    vdraw    = ImageDraw.Draw(vignette, 'RGBA')
    for r_vign in range(SIZE//2, 0, -max(1, SIZE//60)):
        alpha_v = int(60 * (1 - r_vign/(SIZE//2))**3)
        vdraw.ellipse(
            [SIZE//2-r_vign, SIZE//2-r_vign,
             SIZE//2+r_vign, SIZE//2+r_vign],
            outline=bg[:3]+(alpha_v,), width=max(1, SIZE//300)
        )
    img = Image.alpha_composite(img, vignette)

    final = img.convert('RGB')
    return final, strokes


def render_art_simple(master_seed: int, domain: str, n_strokes: int = None) -> tuple:
    """
    Lightweight renderer for when PIL is unavailable.
    Returns (None, list_of_strokes_with_positions).
    Positions are scaled to current SIZE.
    """
    prof = ACTIVE_PROFILE
    S    = SIZE / 512
    if n_strokes is None:
        n_strokes = min(int(prof.n_strokes * S * 0.6), 300)
    rng     = random.Random(master_seed)
    strokes = []
    cx_canvas = SIZE // 2
    cy_canvas = SIZE // 2
    for i in range(n_strokes):
        rule = generate_rule(master_seed, i, domain, prof)
        rule['size']      = max(int(rule['size']      * S), int(S))
        rule['thickness'] = max(int(rule['thickness'] * S), int(S * 0.8))
        # Simple weighted placement — centre bias
        rule['cx'] = int(rng.gauss(cx_canvas, SIZE * 0.30))
        rule['cy'] = int(rng.gauss(cy_canvas, SIZE * 0.30))
        strokes.append(rule)
    return None, strokes


# ══════════════════════════════════════════════════════════════════════════════
# ArtPiece dataclass
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class ArtPiece:
    seed:       int
    domain:     str
    fn_name:    str
    strokes:    List[dict] = field(default_factory=list)
    image:      Any        = None   # PIL.Image or None
    tk_photo:   Any        = None   # set by UI layer
    rarity:     str        = 'Common'
    complexity: int        = 0
    price:      float      = 0.0
    timestamp:  str        = ''
    metadata:   dict       = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({
            'seed':       self.seed,
            'domain':     self.domain,
            'fn_name':    self.fn_name,
            'rarity':     self.rarity,
            'complexity': self.complexity,
            'price':      self.price,
            'timestamp':  self.timestamp,
            'stroke_count': len(self.strokes),
            'colors_used': list(set(s['color'] for s in self.strokes)),
        }, indent=2)

    def save_png(self, directory: str = None) -> Optional[str]:
        if self.image is None:
            return None
        if directory is None:
            directory = SESSION_DIR
        os.makedirs(directory, exist_ok=True)
        # Sanitize domain name for Windows — strip ALL non-ASCII and illegal chars
        safe_domain = ''.join(
            c if (c.isalnum() or c in '_-') else '_'
            for c in self.domain.encode('ascii', 'ignore').decode('ascii')
        ).strip('_') or 'Unknown'
        filename  = f'{self.rarity}_{self.seed}_{safe_domain}.png'
        path      = os.path.join(directory, filename)
        self.image.save(path)
        json_path = path.replace('.png', '.json')
        with open(json_path, 'w') as f:
            f.write(self.to_json())
        return path


# ══════════════════════════════════════════════════════════════════════════════
# BACKGROUND ENGINE
# ══════════════════════════════════════════════════════════════════════════════

class MathCodeEngine:
    """
    Background art-generation engine.
    Feed it calculation results; it produces ArtPieces in a daemon thread.
    """
    HISTORY_MAX = 32

    def __init__(self):
        self._queue:    queue.Queue = queue.Queue(maxsize=64)
        self._thread:   Optional[threading.Thread] = None
        self._running:  bool = False
        self._lock:     threading.Lock = threading.Lock()

        self.latest:    Optional[ArtPiece] = None
        self.history:   List[ArtPiece]     = []
        self.on_new_piece: Optional[Callable] = None   # callback(ArtPiece)

        # Stack mode — accumulate strokes from multiple calculations on one canvas
        self.stack_mode:   bool              = False
        self._stack_piece: Optional[ArtPiece] = None   # the canvas being built up

        # Stats
        self.total_generated: int   = 0
        self.total_legendary: int   = 0

    # ── Public API ────────────────────────────────────────────────────────────

    def start(self):
        """Launch the background generation thread."""
        if self._running:
            return
        self._running = True
        self._thread  = threading.Thread(target=self._worker, daemon=True, name='MathCode')
        self._thread.start()

    def stop(self):
        """Signal the worker to exit."""
        self._running = False
        self._queue.put(None)  # sentinel

    def clear_stack(self):
        """Discard the current stacked canvas so the next calculation starts fresh."""
        with self._lock:
            self._stack_piece = None

    def feed(self, result_value, domain: str = 'default',
             fn_name: str = '', inputs: dict = None):
        """
        Push a new calculation result into the generation queue.
        result_value — numeric result (int or float) that seeds the art.
        inputs       — dict of {param_name: value} from the calculation,
                       used to modulate composition geometry (focal offset etc).
        fn_name      — function name used to classify mathematical character.
        """
        try:
            seed = self._value_to_seed(result_value)
            self._queue.put_nowait({
                'seed':         seed,
                'domain':       domain,
                'fn_name':      fn_name,
                'inputs':       inputs or {},
                'result_seed':  seed,
            })
        except queue.Full:
            pass  # drop if overloaded — never block the calculator

    def current_status(self) -> dict:
        """Summary dict for the UI status bar."""
        with self._lock:
            return {
                'running':    self._running,
                'queue_depth':self._queue.qsize(),
                'generated':  self.total_generated,
                'legendary':  self.total_legendary,
                'latest_rarity': self.latest.rarity if self.latest else '—',
                'latest_price':  self.latest.price  if self.latest else 0.0,
            }

    # ── Worker ────────────────────────────────────────────────────────────────

    def _worker(self):
        while self._running:
            try:
                job = self._queue.get(timeout=2.0)
            except queue.Empty:
                continue
            if job is None:   # stop sentinel
                break
            try:
                if self.stack_mode:
                    piece = self._generate_stacked(job['seed'], job['domain'], job['fn_name'])
                else:
                    piece = self._generate(
                        job['seed'], job['domain'], job['fn_name'],
                        inputs      = job.get('inputs', {}),
                        result_seed = job.get('result_seed', job['seed']),
                    )
                with self._lock:
                    self.latest = piece
                    self.history.append(piece)
                    if len(self.history) > self.HISTORY_MAX:
                        self.history.pop(0)
                    self.total_generated += 1
                    if piece.rarity == 'Legendary':
                        self.total_legendary += 1
                # Notify UI (must be thread-safe — caller uses after())
                if self.on_new_piece:
                    self.on_new_piece(piece)
            except Exception:
                pass  # never crash the calculator over art

    def _generate(self, seed: int, domain: str, fn_name: str,
                  inputs: dict = None, result_seed: int = None) -> ArtPiece:
        """
        Core generation pipeline.
        fn_name and inputs now flow through to the renderer so the
        mathematical character of the function drives visual parameters.
        result_seed (the actual numeric result) modulates frequency, size,
        angle, and composition independently from the RNG seed.
        """
        if PIL_AVAILABLE:
            image, strokes = render_art_pil(
                seed, domain,
                fn_name     = fn_name,
                inputs      = inputs or {},
                result_seed = result_seed if result_seed is not None else seed,
            )
        else:
            image, strokes = render_art_simple(seed, domain, fn_name=fn_name)

        rarity     = detect_rarity(strokes, seed=seed)
        complexity = score_complexity(strokes)
        price      = calculate_price(complexity, rarity)
        fn_class   = _classify_function(fn_name)

        piece = ArtPiece(
            seed       = seed,
            domain     = domain,
            fn_name    = fn_name,
            strokes    = strokes,
            image      = image,
            rarity     = rarity,
            complexity = complexity,
            price      = price,
            timestamp  = time.strftime('%H:%M:%S'),
            metadata   = {
                'seed':         seed,
                'domain':       domain,
                'fn_name':      fn_name,
                'fn_class':     fn_class,
                'inputs':       inputs or {},
                'result_seed':  result_seed if result_seed is not None else seed,
                'rarity':       rarity,
                'complexity':   complexity,
                'price':        price,
                'stroke_count': len(strokes),
                'colors':       list(set(s['color'] for s in strokes)),
                'stroke_types': list(set(s['stroke'] for s in strokes)),
                'profile':      ACTIVE_PROFILE.name,
            },
        )
        return piece

    def _generate_stacked(self, seed: int, domain: str, fn_name: str) -> ArtPiece:
        """
        Stack mode: paint new strokes on top of the existing canvas.
        The _stack_piece accumulates every calculation until clear_stack() is called.
        Rarity/complexity/price are re-evaluated against the FULL combined stroke list.
        """
        # Generate the new layer's strokes (fewer strokes per layer so it doesn't
        # get overwhelmed — uses a fraction of the normal count)
        prof       = ACTIVE_PROFILE
        n_layer    = max(40, prof.n_strokes // 4)   # ~25% strokes per layer

        if PIL_AVAILABLE:
            new_image, new_strokes = render_art_pil(seed, domain, n_layer)
        else:
            new_image, new_strokes = render_art_simple(seed, domain, n_layer)

        with self._lock:
            base = self._stack_piece

        if base is None:
            # First calculation in this stack — start with a full-weight render
            # so the canvas isn't sparse, then accumulate from here
            if PIL_AVAILABLE:
                base_image, base_strokes = render_art_pil(seed, domain, prof.n_strokes)
            else:
                base_image, base_strokes = render_art_simple(seed, domain, prof.n_strokes)
            all_strokes = base_strokes
            combined_image = base_image
            layer_index = 1
            # Collect fn names for combined label
            fn_names = [fn_name]
        else:
            all_strokes  = base.strokes + new_strokes
            layer_index  = base.metadata.get('stack_layers', 1) + 1
            fn_names     = base.metadata.get('fn_names', [base.fn_name]) + [fn_name]

            # Composite the new layer onto the existing PIL image
            if PIL_AVAILABLE and base.image is not None and new_image is not None:
                try:
                    from PIL import Image as _Img
                    combined_image = base.image.copy().convert('RGBA')
                    overlay = new_image.convert('RGBA')
                    # Blend new layer at reduced opacity so base remains visible
                    r, g, b, a = overlay.split()
                    a = a.point(lambda x: int(x * 0.65))   # 65% opacity per layer
                    overlay.putalpha(a)
                    combined_image.paste(overlay, (0, 0), overlay)
                    combined_image = combined_image.convert('RGB')
                except Exception:
                    combined_image = new_image
            else:
                combined_image = new_image

        # Re-score against the full accumulated stroke list
        combined_seed = seed ^ (layer_index * 0xABCD1234) & 0x7FFFFFFF
        rarity     = detect_rarity(all_strokes, seed=combined_seed)
        complexity = score_complexity(all_strokes)
        price      = calculate_price(complexity, rarity)

        piece = ArtPiece(
            seed       = seed,
            domain     = domain,
            fn_name    = ' + '.join(fn_names[-3:]),   # show last 3 layers in name
            strokes    = all_strokes,
            image      = combined_image,
            rarity     = rarity,
            complexity = complexity,
            price      = price,
            timestamp  = time.strftime('%H:%M:%S'),
            metadata   = {
                'seed': seed, 'domain': domain,
                'fn_name': ' + '.join(fn_names[-3:]),
                'fn_names': fn_names,
                'rarity': rarity, 'complexity': complexity, 'price': price,
                'stroke_count': len(all_strokes),
                'stack_layers': layer_index,
                'colors': list(set(s['color'] for s in all_strokes)),
                'stroke_types': list(set(s['stroke'] for s in all_strokes)),
                'profile': ACTIVE_PROFILE.name,
                'stacked': True,
            },
        )

        with self._lock:
            self._stack_piece = piece

        return piece

    @staticmethod
    def _value_to_seed(value) -> int:
        """Convert any numeric result to a stable integer seed."""
        try:
            f   = float(value) if not isinstance(value, (int, float)) else float(value)
            if math.isnan(f) or math.isinf(f):
                return abs(hash(str(value))) & 0x7FFFFFFF
            # Encode sign + mantissa + exponent into an integer
            mantissa, exp = math.frexp(abs(f))
            encoded = int(mantissa * (2**31)) ^ (exp * 1234567) ^ (1 if f < 0 else 0)
            return abs(encoded) & 0x7FFFFFFF
        except Exception:
            return abs(hash(str(value))) & 0x7FFFFFFF


# ══════════════════════════════════════════════════════════════════════════════
# TKINTER CANVAS RENDERER  (fallback — no PIL required)
# ══════════════════════════════════════════════════════════════════════════════

def draw_piece_on_canvas(canvas, piece: ArtPiece, w: int, h: int) -> None:
    """
    Render an ArtPiece directly onto a tkinter Canvas widget.
    Used when PIL is unavailable or as the live-preview renderer.
    """
    import tkinter as tk
    scale_x = w / SIZE
    scale_y = h / SIZE

    canvas.delete('art')

    # Background grid
    for gx in range(0, w, 16):
        canvas.create_line(gx, 0, gx, h, fill='#0d1520', tags='art')
    for gy in range(0, h, 16):
        canvas.create_line(0, gy, w, gy, fill='#0d1520', tags='art')

    def sc(x, y):  # scale to canvas
        return x * scale_x, y * scale_y

    for rule in piece.strokes:
        cx = rule.get('cx', SIZE//2)
        cy = rule.get('cy', SIZE//2)
        col = rule['color']
        s   = rule['size']
        t   = max(1, rule['thickness'])
        a   = rule['angle']
        f   = rule['freq']
        kind = rule['stroke']

        # All coordinates scaled
        x, y = sc(cx, cy)
        rs   = s * min(scale_x, scale_y)

        try:
            if kind == 'line':
                rad = math.radians(a)
                x2, y2 = x + rs*math.cos(rad), y + rs*math.sin(rad)
                canvas.create_line(x, y, x2, y2, fill=col, width=t, tags='art')

            elif kind == 'arc':
                r = rs / 2
                canvas.create_arc(x-r, y-r, x+r, y+r,
                                  start=a, extent=180, style='arc',
                                  outline=col, width=t, tags='art')

            elif kind == 'dot':
                r = max(2, rs/4)
                canvas.create_oval(x-r, y-r, x+r, y+r, fill=col, outline='', tags='art')

            elif kind == 'orbit':
                canvas.create_oval(x-rs, y-rs, x+rs, y+rs,
                                   outline=col, width=t, tags='art')
                for k in range(0, 360, 45):
                    rad_k = math.radians(k)
                    xi, yi = x+rs*math.cos(rad_k), y+rs*math.sin(rad_k)
                    canvas.create_oval(xi-2, yi-2, xi+2, yi+2,
                                       fill=col, outline='', tags='art')

            elif kind == 'spiral':
                pts = []
                for k in range(0, 60, 2):
                    r_k   = k * rs / 60
                    rad_k = math.radians(k * f * 6)
                    pts.extend([x+r_k*math.cos(rad_k), y+r_k*math.sin(rad_k)])
                if len(pts) >= 4:
                    canvas.create_line(pts, fill=col, width=t, smooth=True, tags='art')

            elif kind == 'wave':
                pts = []
                for k in range(-int(rs), int(rs)+1, 3):
                    wy = y + (rs/3)*math.sin(math.radians(k*f*10+a))
                    pts.extend([x+k, wy])
                if len(pts) >= 4:
                    canvas.create_line(pts, fill=col, width=t, smooth=True, tags='art')

            elif kind == 'vector':
                rad  = math.radians(a)
                x2, y2 = x+rs*math.cos(rad), y+rs*math.sin(rad)
                canvas.create_line(x, y, x2, y2, fill=col, width=t,
                                   arrow='last', arrowshape=(8,10,4), tags='art')

            elif kind == 'polygon':
                sides = max(3, int(f*2+3))
                pts   = []
                for k in range(sides):
                    rad_k = math.radians(k*360/sides+a)
                    pts.extend([x+rs*math.cos(rad_k), y+rs*math.sin(rad_k)])
                canvas.create_polygon(pts, outline=col, fill='', width=t, tags='art')

            elif kind in ('lattice', 'grid'):
                canvas.create_rectangle(x-rs, y-rs, x+rs, y+rs,
                                        outline=col, width=t, tags='art')
                canvas.create_line(x-rs, y, x+rs, y, fill=col, width=t, tags='art')
                canvas.create_line(x, y-rs, x, y+rs, fill=col, width=t, tags='art')

            elif kind == 'scatter':
                rng2 = random.Random(int(cx*31+cy*17))
                for _ in range(6):
                    sx, sy = x+rng2.randint(-int(rs), int(rs)), y+rng2.randint(-int(rs), int(rs))
                    r = rng2.randint(1, 4)
                    canvas.create_oval(sx-r, sy-r, sx+r, sy+r, fill=col, outline='', tags='art')

            elif kind == 'curve':
                pts = []
                for k in range(0, 361, 15):
                    rad_k = math.radians(k)
                    rx_k  = rs*math.cos(rad_k)
                    ry_k  = (rs/2)*math.sin(2*rad_k+math.radians(a))
                    pts.extend([x+rx_k, y+ry_k])
                if len(pts) >= 4:
                    canvas.create_line(pts, fill=col, width=t, smooth=True, tags='art')

            elif kind == 'radial':
                for k in range(12):
                    rad_k = math.radians(k*30+a)
                    canvas.create_line(x, y, x+rs*math.cos(rad_k), y+rs*math.sin(rad_k),
                                       fill=col, width=t, tags='art')

            elif kind == 'tree':
                def _btk(d, bx, by, ba, bl):
                    if bl < 3 or d > 4: return
                    rad_b = math.radians(ba)
                    ex, ey = bx+bl*math.cos(rad_b), by+bl*math.sin(rad_b)
                    canvas.create_line(bx, by, ex, ey, fill=col, width=max(1,d), tags='art')
                    _btk(d+1, ex, ey, ba-25, bl*0.65)
                    _btk(d+1, ex, ey, ba+25, bl*0.65)
                _btk(1, x, y, a-90, rs)

        except Exception:
            pass  # never crash on a render error