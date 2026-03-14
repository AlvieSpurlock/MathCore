"""
MathCore UI  —  Tkinter front-end for the MathCore engine.
Replaces the console DebugUI while using its calculation logic.

Architecture
────────────
  FunctionRegistry   — maps every section / function to a field spec + handler
  MathCoreApp        — root Tk window, owns the two main panels
  NavPanel           — left sidebar: collapsible tree of all 20 disciplines
  WorkPanel          — right area: dynamic form + scrollable output
  CalcPopup          — the layered "ripcord" calculator (? key anywhere)
  StepView           — optional step-by-step breakdown drawer
  WordParser         — optional NL problem sentence parser

Run with:  python MathCoreUI.py
"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont
import tkinter.messagebox as messagebox
import math
import sys
import os
import re
import textwrap
import traceback
from functools import partial
from Config.MathCodeEngine  import MathCodeEngine
from Config.MathCodeMonitor import ArtMonitor, ArtStatusBadge

# ── MathCore imports (adjust path if running outside the project root) ────────
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

def _try_import(alias, module_path):
    try:
        import importlib
        return importlib.import_module(module_path)
    except ImportError:
        return None

# Physics
Physics_1D       = _try_import('Physics_1D',       'MathTypes.Physics.Physics_1D')
Physics_2D       = _try_import('Physics_2D',       'MathTypes.Physics.Physics_2D')
Physics_3D       = _try_import('Physics_3D',       'MathTypes.Physics.Physics_3D')
Forces           = _try_import('Forces',            'MathTypes.Physics.Forces')
PEnergy          = _try_import('PEnergy',           'MathTypes.Physics.Physics_Energy')
PSprings         = _try_import('PSprings',          'MathTypes.Physics.Physics_Springs')
PMomentum        = _try_import('PMomentum',         'MathTypes.Physics.Physics_Momentum')
PCoM             = _try_import('PCoM',              'MathTypes.Physics.Physics_CenterOfMass')
PCollisions      = _try_import('PCollisions',       'MathTypes.Physics.Physics_Collisions')
# Math
BasicMath        = _try_import('BasicMath',         'MathTypes.Basic.BasicMath')
Algebra          = _try_import('Algebra',           'MathTypes.Basic.Algebra')
Geometry         = _try_import('Geometry',          'MathTypes.Basic.Geometry')
Trig             = _try_import('Trig',              'MathTypes.Basic.Trigonometry')
Calc             = _try_import('Calc',              'MathTypes.Advanced.Calculus')
Diff             = _try_import('Diff',              'MathTypes.Advanced.Differential')
Stat             = _try_import('Stat',              'MathTypes.Advanced.Statistics')
Prob             = _try_import('Prob',              'MathTypes.Advanced.Probability')
Comb             = _try_import('Comb',              'MathTypes.Advanced.Combinatorics')
Discrete         = _try_import('Discrete',          'MathTypes.Advanced.DiscreteMath')
LinAlg           = _try_import('LinAlg',            'MathTypes.Advanced.LinearAlgebra')
DiffGeo          = _try_import('DiffGeo',           'MathTypes.Advanced.DifferentialGeometry')
AbsAlg           = _try_import('AbsAlg',            'MathTypes.Advanced.AbstractAlgebra')
Topo             = _try_import('Topo',              'MathTypes.Advanced.Topology')
AlgGeo           = _try_import('AlgGeo',            'MathTypes.Advanced.AlgebraicGeometry')

# ══════════════════════════════════════════════════════════════════════════════
# THEME  —  Cyberpunk / Terminal aesthetic
# ══════════════════════════════════════════════════════════════════════════════

C = {
    'bg':          '#080b0f',   # deep space black
    'bg2':         '#0d1117',   # card background
    'bg3':         '#111820',   # input background
    'panel':       '#0a0e14',   # nav panel
    'border':      '#1a2535',   # subtle border
    'border_hi':   '#00ff9f',   # neon green accent border
    'accent':      '#00ff9f',   # primary neon green
    'accent2':     '#00d4ff',   # cyan
    'accent3':     '#ff006e',   # hot pink
    'accent4':     '#ffe600',   # yellow
    'text':        '#c9d1d9',   # main text
    'text_dim':    '#6e7681',   # dimmed text
    'text_bright': '#f0f6fc',   # headings
    'text_code':   '#79c0ff',   # code / numbers
    'result':      '#00ff9f',   # result value
    'error':       '#ff4444',   # errors
    'warn':        '#ffe600',   # warnings
    'step_bg':     '#0d1f0d',   # step-by-step box
    'nav_sel':     '#112233',   # selected nav item
    'nav_hover':   '#0d1a2a',   # hovered nav item
    'btn':         '#0f2a1f',   # button bg
    'btn_hover':   '#1a4030',   # button hover
    'btn_text':    '#00ff9f',   # button text
    'tag_key':     '#ff79c6',   # field label accent
}

FONTS = {
    'mono':    ('Consolas', 11),
    'mono_sm': ('Consolas', 9),
    'mono_lg': ('Consolas', 13, 'bold'),
    'ui':      ('Segoe UI', 10),
    'ui_sm':   ('Segoe UI', 9),
    'ui_lg':   ('Segoe UI', 12, 'bold'),
    'heading': ('Segoe UI', 14, 'bold'),
    'nav':     ('Consolas', 10),
    'nav_sec': ('Consolas', 9, 'bold'),
    'result':  ('Consolas', 12, 'bold'),
    'title':   ('Consolas', 16, 'bold'),
}

# ══════════════════════════════════════════════════════════════════════════════
# FUNCTION REGISTRY
# ══════════════════════════════════════════════════════════════════════════════
# Each entry:
#   name       — display name
#   fields     — list of {'id', 'label', 'type': float/int/str/expr/list, 'default': ''}
#   fn         — callable(field_values_dict) → result_str or dict{label:value}
#   steps_fn   — optional callable(field_values_dict) → list of (label, formula, value) tuples
#   word_fn    — optional callable(sentence_str) → field_values_dict or None

def _f(id_, label, type_='float', default='', hint=''):
    return {'id': id_, 'label': label, 'type': type_, 'default': default, 'hint': hint}

def _fmt(val, unit='', decimals=6):
    if isinstance(val, bool):   return str(val)
    if isinstance(val, int):    return f'{val} {unit}'.strip()
    if isinstance(val, float):  return f'{val:.{decimals}f} {unit}'.strip()
    return f'{val} {unit}'.strip()

def _dict_result(**kw):
    return '\n'.join(f'{k} = {_fmt(v)}' for k, v in kw.items())

def _safe(fn):
    """Wrap a registry function so exceptions become error strings."""
    def wrapper(fv):
        try:
            return fn(fv)
        except Exception as e:
            raise RuntimeError(str(e))
    return wrapper

# ── Build the full registry ───────────────────────────────────────────────────
REGISTRY = {}   # { 'SectionName': [ {name, fields, fn, steps_fn, word_fn}, ... ] }

# ─────────────── 1. Basic Math ────────────────────────────────────────────────
if BasicMath:
    REGISTRY['Basic Math'] = [
        {
            'name': 'Add two numbers',
            'fields': [_f('a','a'), _f('b','b')],
            'fn': _safe(lambda fv: f'a + b = {_fmt(BasicMath.add(fv["a"],fv["b"]))}'),
        },
        {
            'name': 'Subtract  (a − b)',
            'fields': [_f('a','a'), _f('b','b')],
            'fn': _safe(lambda fv: f'a − b = {_fmt(BasicMath.sub(fv["a"],fv["b"]))}'),
        },
        {
            'name': 'Multiply  (a × b)',
            'fields': [_f('a','a'), _f('b','b')],
            'fn': _safe(lambda fv: f'a × b = {_fmt(BasicMath.multi(fv["a"],fv["b"]))}'),
        },
        {
            'name': 'Divide  (a ÷ b)',
            'fields': [_f('a','a'), _f('b','b (divisor)')],
            'fn': _safe(lambda fv: f'a ÷ b = {_fmt(BasicMath.div(fv["a"],fv["b"]))}'),
        },
        {
            'name': 'Modulo  (a mod b)',
            'fields': [_f('a','a','int'), _f('b','b','int')],
            'fn': _safe(lambda fv: f'a mod b = {BasicMath.mod(int(fv["a"]),int(fv["b"]))}'),
        },
    ]

# ─────────────── 2. Physics — 1D Kinematics ───────────────────────────────────
if Physics_1D:
    REGISTRY['Physics 1D'] = [
        {
            'name': 'Distance  |x₂ − x₁|',
            'fields': [_f('x1','x₁ (m)'), _f('x2','x₂ (m)')],
            'fn': _safe(lambda fv: f'|x₂−x₁| = {_fmt(Physics_1D.GetDistance(fv["x1"],fv["x2"]))} m'),
            'steps_fn': lambda fv: [
                ('Formula','Δx = |x₂ − x₁|',''),
                ('Substitute',f'|{fv["x2"]} − {fv["x1"]}|',''),
                ('Result','',f'{_fmt(Physics_1D.GetDistance(fv["x1"],fv["x2"]))} m'),
            ],
        },
        {
            'name': 'Velocity  v = Δx/Δt',
            'fields': [_f('d','Δx distance (m)'), _f('t','Δt time (s)')],
            'fn': _safe(lambda fv: f'v = {_fmt(Physics_1D.Velocity(fv["d"],fv["t"]))} m/s'),
        },
        {
            'name': 'Final velocity  v = v₀ + at',
            'fields': [_f('v0','v₀ (m/s)'), _f('a','a (m/s²)'), _f('t','t (s)')],
            'fn': _safe(lambda fv: f'v = {_fmt(fv["v0"] + fv["a"]*fv["t"])} m/s'),
            'steps_fn': lambda fv: [
                ('Formula','v = v₀ + a·t',''),
                ('Substitute',f'{fv["v0"]} + {fv["a"]}·{fv["t"]}',''),
                ('Result','',f'{_fmt(fv["v0"]+fv["a"]*fv["t"])} m/s'),
            ],
        },
        {
            'name': 'Acceleration  a = Δv/Δt',
            'fields': [_f('v0','v₀ (m/s)'), _f('v','v_f (m/s)'), _f('t','Δt (s)')],
            'fn': _safe(lambda fv: f'a = {_fmt(Physics_1D.Acceleration(fv["v0"],fv["v"],fv["t"]))} m/s²'),
        },
        {
            'name': 'Displacement  Δx = v₀t + ½at²',
            'fields': [_f('v0','v₀ (m/s)'), _f('a','a (m/s²)'), _f('t','t (s)')],
            'fn': _safe(lambda fv: f'Δx = {_fmt(Physics_1D.GetDisplacement(fv["a"],fv["t"],fv["v0"]))} m'),
        },
        {
            'name': 'Stopping time  t = v₀/a',
            'fields': [_f('v0','v₀ (m/s)'), _f('decel','deceleration magnitude (m/s²)')],
            'fn': _safe(lambda fv: f't_stop = {_fmt(Physics_1D.StoppingTime(fv["v0"],fv["decel"]))} s'),
        },
        {
            'name': 'Stopping distance',
            'fields': [_f('v0','v₀ (m/s)'), _f('decel','deceleration (m/s²)')],
            'fn': _safe(lambda fv: f'd_stop = {_fmt(Physics_1D.StoppingDistance(fv["v0"],fv["decel"]))} m'),
        },
        {
            'name': 'Free fall — impact velocity',
            'fields': [_f('h','Height h (m)'), _f('g','g (m/s²)','float','9.8')],
            'fn': _safe(lambda fv: f'v_impact = {_fmt(Physics_1D.ImpactVelocity(fv["h"],fv["g"],0))} m/s'),
        },
        {
            'name': 'Max height from launch',
            'fields': [_f('v0','v₀ upward (m/s)'), _f('g','g (m/s²)','float','9.8')],
            'fn': _safe(lambda fv: f'h_max = {_fmt(Physics_1D.MaxHeightFromLaunch(fv["v0"],fv["g"]))} m'),
        },
    ]

# ─────────────── 3. Physics — Energy ──────────────────────────────────────────
if PEnergy:
    REGISTRY['Physics — Energy'] = [
        {
            'name': 'Kinetic energy  KE = ½mv²',
            'fields': [_f('m','Mass m (kg)'), _f('v','Velocity v (m/s)')],
            'fn': _safe(lambda fv: f'KE = {_fmt(PEnergy.KineticEnergy(fv["m"],fv["v"]))} J'),
            'steps_fn': lambda fv: [
                ('Formula','KE = ½ m v²',''),
                ('Substitute',f'½ × {fv["m"]} × {fv["v"]}²',''),
                ('Result','',f'{_fmt(PEnergy.KineticEnergy(fv["m"],fv["v"]))} J'),
            ],
            'word_fn': lambda s: _parse_ke(s),
        },
        {
            'name': 'Velocity from KE',
            'fields': [_f('ke','KE (J)'), _f('m','Mass m (kg)')],
            'fn': _safe(lambda fv: f'v = {_fmt(PEnergy.VelocityFromKE(fv["ke"],fv["m"]))} m/s'),
        },
        {
            'name': 'Gravitational PE  GPE = mgh',
            'fields': [_f('m','Mass m (kg)'), _f('h','Height h (m)'), _f('g','g (m/s²)','float','9.8')],
            'fn': _safe(lambda fv: f'GPE = {_fmt(PEnergy.GravitationalPE(fv["m"],fv["h"],fv["g"]))} J'),
            'steps_fn': lambda fv: [
                ('Formula','GPE = m·g·h',''),
                ('Substitute',f'{fv["m"]} × {fv["g"]} × {fv["h"]}',''),
                ('Result','',f'{_fmt(PEnergy.GravitationalPE(fv["m"],fv["h"],fv["g"]))} J'),
            ],
        },
        {
            'name': 'Work  W = F·d·cos θ',
            'fields': [_f('F','Force F (N)'), _f('d','Distance d (m)'), _f('theta','Angle θ (deg)','float','0')],
            'fn': _safe(lambda fv: f'W = {_fmt(PEnergy.Work(fv["F"],fv["d"],fv["theta"]))} J'),
        },
        {
            'name': 'Work-Energy Theorem  W = ΔKE',
            'fields': [_f('m','Mass m (kg)'), _f('vi','v_initial (m/s)'), _f('vf','v_final (m/s)')],
            'fn': _safe(lambda fv: f'W_net = ΔKE = {_fmt(PEnergy.WorkEnergyTheorem(fv["m"],fv["vi"],fv["vf"]))} J'),
        },
        {
            'name': 'Average power  P = W/Δt',
            'fields': [_f('W','Work W (J)'), _f('t','Time Δt (s)')],
            'fn': _safe(lambda fv: f'P = {_fmt(PEnergy.PowerAvg(fv["W"],fv["t"]))} W'),
        },
        {
            'name': 'Power from force  P = F·v·cos θ',
            'fields': [_f('F','F (N)'), _f('v','v (m/s)'), _f('theta','θ (deg)','float','0')],
            'fn': _safe(lambda fv: f'P = {_fmt(PEnergy.PowerFromForce(fv["F"],fv["v"],fv["theta"]))} W'),
        },
        {
            'name': 'Conservation — final velocity',
            'fields': [_f('vi','v_i (m/s)'), _f('hi','h_i (m)'), _f('hf','h_f (m)')],
            'fn': _safe(lambda fv: f'v_f = {_fmt(PEnergy.FinalVelocityConservation(fv["vi"],fv["hi"],fv["hf"]))} m/s'),
        },
        {
            'name': 'Energy breakdown at a point',
            'fields': [_f('m','m (kg)'), _f('v','v (m/s)'), _f('h','h (m)'),
                       _f('k','Spring k (0=none)','float','0'), _f('x','Spring x (0=none)','float','0')],
            'fn': _safe(lambda fv: '\n'.join(f'{k}: {v:.4f} J'
                         for k,v in PEnergy.EnergyBreakdown(fv['m'],fv['v'],fv['h'],fv['k'],fv['x'],0).items())),
        },
        {
            'name': 'Inductor energy  U_L = ½LI²',
            'fields': [_f('L','Inductance L (H)'), _f('I','Current I (A)')],
            'fn': _safe(lambda fv: f'U_L = {_fmt(PEnergy.InductorEnergy(fv["L"],fv["I"]))} J'),
        },
    ]

def _parse_ke(sentence):
    """Word parser for KE problems: extracts mass and velocity."""
    ms = re.findall(r'(\d+\.?\d*)\s*kg', sentence, re.I)
    vs = re.findall(r'(\d+\.?\d*)\s*m/?s', sentence, re.I)
    if ms and vs:
        return {'m': float(ms[0]), 'v': float(vs[0])}
    return None

# ─────────────── 4. Physics — Springs ─────────────────────────────────────────
if PSprings:
    REGISTRY['Physics — Springs'] = [
        {
            'name': "Hooke's Law  F = kx",
            'fields': [_f('k','Spring constant k (N/m)'), _f('x','Displacement x (m)')],
            'fn': _safe(lambda fv: f'F_spring = {_fmt(PSprings.SpringForce(fv["k"],fv["x"]))} N'),
            'steps_fn': lambda fv: [
                ('Formula','F = −k·x',''),
                ('Substitute',f'−{fv["k"]} × {fv["x"]}',''),
                ('Result','',f'{_fmt(PSprings.SpringForce(fv["k"],fv["x"]))} N (restoring)'),
            ],
        },
        {
            'name': 'Spring PE  = ½kx²',
            'fields': [_f('k','k (N/m)'), _f('x','x (m)')],
            'fn': _safe(lambda fv: f'PE = {_fmt(PSprings.SpringPE(fv["k"],fv["x"]))} J'),
        },
        {
            'name': 'SHM position  x(t)',
            'fields': [_f('A','Amplitude A (m)'), _f('w','ω (rad/s)'),
                       _f('t','t (s)'), _f('phi','Phase φ (rad)','float','0')],
            'fn': _safe(lambda fv: f'x(t) = {_fmt(PSprings.SHM_Position(fv["A"],fv["w"],fv["t"],fv["phi"]))} m'),
        },
        {
            'name': 'SHM velocity  v(t)',
            'fields': [_f('A','A (m)'), _f('w','ω (rad/s)'),
                       _f('t','t (s)'), _f('phi','φ (rad)','float','0')],
            'fn': _safe(lambda fv: f'v(t) = {_fmt(PSprings.SHM_Velocity(fv["A"],fv["w"],fv["t"],fv["phi"]))} m/s'),
        },
        {
            'name': 'Angular frequency  ω = √(k/m)',
            'fields': [_f('k','k (N/m)'), _f('m','m (kg)')],
            'fn': _safe(lambda fv: f'ω = {_fmt(PSprings.AngularFrequency(fv["k"],fv["m"]))} rad/s'),
        },
        {
            'name': 'Period  T = 2π√(m/k)',
            'fields': [_f('m','m (kg)'), _f('k','k (N/m)')],
            'fn': _safe(lambda fv: f'T = {_fmt(PSprings.Period(fv["m"],fv["k"]))} s'),
        },
        {
            'name': 'Total SHM energy  E = ½kA²',
            'fields': [_f('k','k (N/m)'), _f('A','Amplitude A (m)')],
            'fn': _safe(lambda fv: f'E = {_fmt(PSprings.SHM_TotalEnergy(fv["k"],fv["A"]))} J'),
        },
        {
            'name': 'Equilibrium stretch  x_eq = mg/k',
            'fields': [_f('m','m (kg)'), _f('k','k (N/m)')],
            'fn': _safe(lambda fv: f'x_eq = {_fmt(PSprings.EquilibriumStretch(fv["m"],fv["k"]))} m'),
        },
        {
            'name': 'Series spring constant',
            'fields': [_f('k1','k₁ (N/m)'), _f('k2','k₂ (N/m)')],
            'fn': _safe(lambda fv: f'k_series = {_fmt(PSprings.SpringConstantSeries(fv["k1"],fv["k2"]))} N/m'),
        },
        {
            'name': 'Parallel spring constant',
            'fields': [_f('k1','k₁ (N/m)'), _f('k2','k₂ (N/m)')],
            'fn': _safe(lambda fv: f'k_parallel = {_fmt(PSprings.SpringConstantParallel(fv["k1"],fv["k2"]))} N/m'),
        },
    ]

# ─────────────── 5. Physics — Momentum ────────────────────────────────────────
if PMomentum:
    REGISTRY['Physics — Momentum'] = [
        {
            'name': 'Momentum  p = mv',
            'fields': [_f('m','m (kg)'), _f('v','v (m/s)')],
            'fn': _safe(lambda fv: f'p = {_fmt(PMomentum.Momentum(fv["m"],fv["v"]))} kg·m/s'),
        },
        {
            'name': 'Impulse  J = F·Δt',
            'fields': [_f('F','Force F (N)'), _f('dt','Δt (s)')],
            'fn': _safe(lambda fv: f'J = {_fmt(PMomentum.Impulse(fv["F"],fv["dt"]))} N·s'),
        },
        {
            'name': 'Perfectly inelastic v_f',
            'fields': [_f('m1','m₁ (kg)'), _f('v1i','v₁ᵢ (m/s)'),
                       _f('m2','m₂ (kg)'), _f('v2i','v₂ᵢ (m/s)','float','0')],
            'fn': _safe(lambda fv: f'v_f = {_fmt(PMomentum.InelasticFinalVelocity(fv["m1"],fv["v1i"],fv["m2"],fv["v2i"]))} m/s'),
        },
        {
            'name': 'Reduced mass  μ = m₁m₂/(m₁+m₂)',
            'fields': [_f('m1','m₁ (kg)'), _f('m2','m₂ (kg)')],
            'fn': _safe(lambda fv: f'μ = {_fmt(PMomentum.ReducedMass(fv["m1"],fv["m2"]))} kg'),
        },
        {
            'name': 'CoM velocity  1D',
            'fields': [_f('m1','m₁ (kg)'), _f('v1','v₁ (m/s)'),
                       _f('m2','m₂ (kg)'), _f('v2','v₂ (m/s)')],
            'fn': _safe(lambda fv: f'v_cm = {_fmt(PMomentum.CenterOfMassVelocity([fv["m1"],fv["m2"]],[fv["v1"],fv["v2"]]))} m/s'),
        },
        {
            'name': 'Rocket Δv  (Tsiolkovsky)',
            'fields': [_f('vex','Exhaust speed v_ex (m/s)'), _f('mi','m_i (kg)'), _f('mf','m_f (kg)')],
            'fn': _safe(lambda fv: f'Δv = {_fmt(PMomentum.RocketDeltaV(fv["vex"],fv["mi"],fv["mf"]))} m/s'),
        },
        {
            'name': 'Angular momentum  L = Iω',
            'fields': [_f('I','Moment of inertia I (kg·m²)'), _f('w','ω (rad/s)')],
            'fn': _safe(lambda fv: f'L = {_fmt(PMomentum.AngularMomentumFromI(fv["I"],fv["w"]))} kg·m²/s'),
        },
        {
            'name': 'Final angular velocity  ω₂ = I₁ω₁/I₂',
            'fields': [_f('I1','I₁ (kg·m²)'), _f('w1','ω₁ (rad/s)'), _f('I2','I₂ (kg·m²)')],
            'fn': _safe(lambda fv: f'ω₂ = {_fmt(PMomentum.FinalAngularVelocity(fv["I1"],fv["w1"],fv["I2"]))} rad/s'),
        },
    ]

# ─────────────── 6. Physics — Center of Mass ──────────────────────────────────
if PCoM:
    REGISTRY['Physics — Center of Mass'] = [
        {
            'name': 'CoM 1D  (2 particles)',
            'fields': [_f('m1','m₁ (kg)'), _f('x1','x₁ (m)'),
                       _f('m2','m₂ (kg)'), _f('x2','x₂ (m)')],
            'fn': _safe(lambda fv: f'x_cm = {_fmt(PCoM.SplitCoM1D(fv["m1"],fv["x1"],fv["m2"],fv["x2"]))} m'),
            'steps_fn': lambda fv: [
                ('Formula','x_cm = (m₁x₁ + m₂x₂) / (m₁+m₂)',''),
                ('Numerator',f'{fv["m1"]}×{fv["x1"]} + {fv["m2"]}×{fv["x2"]}',
                 f'{fv["m1"]*fv["x1"]+fv["m2"]*fv["x2"]}'),
                ('Denominator',f'{fv["m1"]} + {fv["m2"]}', f'{fv["m1"]+fv["m2"]}'),
                ('Result','',f'{_fmt(PCoM.SplitCoM1D(fv["m1"],fv["x1"],fv["m2"],fv["x2"]))} m'),
            ],
            'word_fn': lambda s: _parse_com_1d(s),
        },
        {
            'name': 'CoM velocity  v_cm = Σmv/M',
            'fields': [_f('m1','m₁ (kg)'), _f('v1','v₁ (m/s)'),
                       _f('m2','m₂ (kg)'), _f('v2','v₂ (m/s)')],
            'fn': _safe(lambda fv: f'v_cm = {_fmt(PCoM.CoMVelocity1D([fv["m1"],fv["m2"]],[fv["v1"],fv["v2"]]))} m/s'),
        },
        {
            'name': 'After explosion — find v₂',
            'fields': [_f('M','Total mass M (kg)'), _f('vcm','v_cm before (m/s)','float','0'),
                       _f('m1','m₁ (kg)'), _f('v1','v₁ after (m/s)')],
            'fn': _safe(lambda fv: '\n'.join([
                f'v₂ = {_fmt(PCoM.CoMAfterExplosion1D(fv["M"],fv["vcm"],fv["m1"],fv["v1"])[0])} m/s',
                f'm₂ = {_fmt(PCoM.CoMAfterExplosion1D(fv["M"],fv["vcm"],fv["m1"],fv["v1"])[1])} kg',
            ])),
        },
        {
            'name': 'Solid semicircle CoM  y = 4r/3π',
            'fields': [_f('r','Radius r (m)'), _f('y0','Base y₀ (m)','float','0')],
            'fn': _safe(lambda fv: f'y_cm = {_fmt(PCoM.CoMSemicircle(fv["r"],fv["y0"])[1])} m'),
        },
        {
            'name': 'Solid cone CoM  z = h/4',
            'fields': [_f('h','Height h (m)'), _f('z0','Base z₀ (m)','float','0')],
            'fn': _safe(lambda fv: f'z_cm = {_fmt(PCoM.CoMSolidCone(fv["h"],fv["z0"]))} m'),
        },
        {
            'name': 'Solid hemisphere  z = 3r/8',
            'fields': [_f('r','Radius r (m)'), _f('z0','Base z₀ (m)','float','0')],
            'fn': _safe(lambda fv: f'z_cm = {_fmt(PCoM.CoMSolidHemisphere(fv["r"],fv["z0"]))} m'),
        },
        {
            'name': 'Triangle centroid',
            'fields': [_f('x1','v₁x'), _f('y1','v₁y'), _f('x2','v₂x'), _f('y2','v₂y'),
                       _f('x3','v₃x'), _f('y3','v₃y')],
            'fn': _safe(lambda fv: f'Centroid = ({_fmt(PCoM.CoMOfTriangle2D((fv["x1"],fv["y1"]),(fv["x2"],fv["y2"]),(fv["x3"],fv["y3"]))[0])}, {_fmt(PCoM.CoMOfTriangle2D((fv["x1"],fv["y1"]),(fv["x2"],fv["y2"]),(fv["x3"],fv["y3"]))[1])}) m'),
        },
        {
            'name': 'Parallel axis theorem  I = I_cm + md²',
            'fields': [_f('Icm','I_cm (kg·m²)'), _f('m','m (kg)'), _f('d','d (m)')],
            'fn': _safe(lambda fv: f'I = {_fmt(PCoM.ParallelAxisTheorem(fv["Icm"],fv["m"],fv["d"]))} kg·m²'),
        },
        {
            'name': 'Reduced mass  μ',
            'fields': [_f('m1','m₁ (kg)'), _f('m2','m₂ (kg)')],
            'fn': _safe(lambda fv: f'μ = {_fmt(PCoM.ReducedMass(fv["m1"],fv["m2"]))} kg'),
        },
        {
            'name': 'KE in CoM frame',
            'fields': [_f('m1','m₁ (kg)'), _f('v1','v₁ (m/s)'),
                       _f('m2','m₂ (kg)'), _f('v2','v₂ (m/s)')],
            'fn': _safe(lambda fv: '\n'.join([
                f'KE_lab = {_fmt(PCoM.KineticEnergyCoMFrame1D([fv["m1"],fv["m2"]],[fv["v1"],fv["v2"]])[1])} J',
                f'KE_cm  = {_fmt(PCoM.KineticEnergyCoMFrame1D([fv["m1"],fv["m2"]],[fv["v1"],fv["v2"]])[0])} J',
            ])),
        },
    ]

def _parse_com_1d(sentence):
    pairs = []
    pA = re.findall(r'(\d+\.?\d*)\s*kg\s*at\s*(?:position\s+|x\s*=\s*)?(-?\d+\.?\d*)', sentence, re.I)
    if pA: pairs = [(float(m), float(x)) for m, x in pA]
    if not pairs:
        ms = re.findall(r'mass\s+(\d+\.?\d*)', sentence, re.I)
        xs = re.findall(r'position\s+(-?\d+\.?\d*)', sentence, re.I)
        if ms and xs and len(ms) == len(xs):
            pairs = [(float(m), float(x)) for m, x in zip(ms, xs)]
    if len(pairs) == 2:
        return {'m1': pairs[0][0], 'x1': pairs[0][1], 'm2': pairs[1][0], 'x2': pairs[1][1]}
    return None

# ─────────────── 7. Algebra ───────────────────────────────────────────────────
if Algebra:
    REGISTRY['Algebra'] = [
        {
            'name': 'Linear  y = mx + b',
            'fields': [_f('m','Slope m'), _f('x','x value'), _f('b','Y-intercept b')],
            'fn': _safe(lambda fv: f'y = {_fmt(Algebra.Linear(fv["m"],fv["x"],fv["b"]))}'),
        },
        {
            'name': 'Quadratic roots  ax² + bx + c',
            'fields': [_f('a','a'), _f('b','b'), _f('c','c')],
            'fn': _safe(lambda fv: f'roots: {Algebra.QuadraticRoots(fv["a"],fv["b"],fv["c"])}'),
        },
        {
            'name': 'Discriminant  b² − 4ac',
            'fields': [_f('a','a'), _f('b','b'), _f('c','c')],
            'fn': _safe(lambda fv: f'Δ = {_fmt(Algebra.Discriminant(fv["a"],fv["b"],fv["c"]))}'),
        },
        {
            'name': 'Logarithm  log_b(x)',
            'fields': [_f('x','x (must be > 0)'), _f('base','Base b')],
            'fn': _safe(lambda fv: f'log_{fv["base"]}({fv["x"]}) = {_fmt(Algebra.LogBase(fv["x"],fv["base"]))}'),
        },
        {
            'name': 'Natural log  ln(x)',
            'fields': [_f('x','x (must be > 0)')],
            'fn': _safe(lambda fv: f'ln({fv["x"]}) = {_fmt(Algebra.NaturalLog(fv["x"]))}'),
        },
        {
            'name': 'Arithmetic sequence — nth term',
            'fields': [_f('a1','First term a₁'), _f('d','Common diff d'), _f('n','n','int')],
            'fn': _safe(lambda fv: f'a_{int(fv["n"])} = {_fmt(Algebra.ArithmeticTerm(fv["a1"],fv["d"],int(fv["n"])))}'),
        },
        {
            'name': 'Geometric sequence — nth term',
            'fields': [_f('a1','First term a₁'), _f('r','Common ratio r'), _f('n','n','int')],
            'fn': _safe(lambda fv: f'a_{int(fv["n"])} = {_fmt(Algebra.GeometricTerm(fv["a1"],fv["r"],int(fv["n"])))}'),
        },
        {
            'name': 'GCD  (Euclidean)',
            'fields': [_f('a','a','int'), _f('b','b','int')],
            'fn': _safe(lambda fv: f'gcd({int(fv["a"])}, {int(fv["b"])}) = {Algebra.GCD(int(fv["a"]),int(fv["b"]))}'),
        },
        {
            'name': 'Percentage change  (old→new)',
            'fields': [_f('old','Old value'), _f('new','New value')],
            'fn': _safe(lambda fv: f'Δ% = {_fmt(Algebra.PercentageChange(fv["old"],fv["new"]))}%'),
        },
    ]

# ─────────────── 8. Geometry ──────────────────────────────────────────────────
if Geometry:
    REGISTRY['Geometry'] = [
        {
            'name': 'Distance 2D',
            'fields': [_f('x1','x₁'), _f('y1','y₁'), _f('x2','x₂'), _f('y2','y₂')],
            'fn': _safe(lambda fv: f'd = {_fmt(Geometry.Distance2D(fv["x1"],fv["y1"],fv["x2"],fv["y2"]))} units'),
        },
        {
            'name': 'Hypotenuse  c = √(a²+b²)',
            'fields': [_f('a','Leg a'), _f('b','Leg b')],
            'fn': _safe(lambda fv: f'c = {_fmt(Geometry.Hypotenuse(fv["a"],fv["b"]))} units'),
        },
        {
            'name': 'Circle  area & circumference',
            'fields': [_f('r','Radius r')],
            'fn': _safe(lambda fv: f'Area = {_fmt(Geometry.CircleArea(fv["r"]))}\nCircumference = {_fmt(Geometry.CircleCircumference(fv["r"]))}'),
        },
        {
            'name': 'Triangle area  (base × height)',
            'fields': [_f('base','Base'), _f('h','Height')],
            'fn': _safe(lambda fv: f'A = {_fmt(Geometry.TriangleArea(fv["base"],fv["h"]))} sq units'),
        },
        {
            'name': 'Rectangle  area & perimeter',
            'fields': [_f('l','Length'), _f('w','Width')],
            'fn': _safe(lambda fv: f'Area = {_fmt(Geometry.RectangleArea(fv["l"],fv["w"]))}\nPerimeter = {_fmt(Geometry.RectanglePerimeter(fv["l"],fv["w"]))}'),
        },
        {
            'name': 'Sphere  area & volume',
            'fields': [_f('r','Radius r')],
            'fn': _safe(lambda fv: f'Surface area = {_fmt(Geometry.SphereSurfaceArea(fv["r"]))}\nVolume = {_fmt(Geometry.SphereVolume(fv["r"]))}'),
        },
        {
            'name': 'Cylinder  area & volume',
            'fields': [_f('r','Radius r'), _f('h','Height h')],
            'fn': _safe(lambda fv: f'Surface area = {_fmt(Geometry.CylinderSurfaceArea(fv["r"],fv["h"]))}\nVolume = {_fmt(Geometry.CylinderVolume(fv["r"],fv["h"]))}'),
        },
        {
            'name': 'Law of Cosines — find side c',
            'fields': [_f('a','Side a'), _f('b','Side b'), _f('C','Angle C (deg)')],
            'fn': _safe(lambda fv: f'c = {_fmt(Geometry.LawOfCosinesSide(fv["a"],fv["b"],fv["C"]))} units'),
        },
    ]

# ─────────────── 9. Trigonometry ──────────────────────────────────────────────
if Trig:
    REGISTRY['Trigonometry'] = [
        {
            'name': 'sin / cos / tan',
            'fields': [_f('theta','Angle θ (degrees)')],
            'fn': _safe(lambda fv: f'sin = {_fmt(Trig.Sin(fv["theta"]))}\ncos = {_fmt(Trig.Cos(fv["theta"]))}\ntan = {_fmt(Trig.Tan(fv["theta"]))}'),
        },
        {
            'name': 'arcsin / arccos / arctan',
            'fields': [_f('x','x value  (sin/cos: −1 to 1)')],
            'fn': _safe(lambda fv: f'arcsin = {_fmt(Trig.Asin(fv["x"]))}°\narccos = {_fmt(Trig.Acos(fv["x"]))}°\narctan = {_fmt(Trig.Atan(fv["x"]))}°'),
        },
        {
            'name': 'sin(A+B)  and  cos(A+B)',
            'fields': [_f('A','A (degrees)'), _f('B','B (degrees)')],
            'fn': _safe(lambda fv: f'sin(A+B) = {_fmt(Trig.SinSum(fv["A"],fv["B"]))}\ncos(A+B) = {_fmt(Trig.CosSum(fv["A"],fv["B"]))}'),
        },
        {
            'name': 'Double angle  sin(2θ)  cos(2θ)',
            'fields': [_f('theta','θ (degrees)')],
            'fn': _safe(lambda fv: f'sin(2θ) = {_fmt(Trig.Sin2x(fv["theta"]))}\ncos(2θ) = {_fmt(Trig.Cos2x(fv["theta"]))}'),
        },
        {
            'name': 'Sine wave  A·sin(Bt+C)+D',
            'fields': [_f('A','Amplitude A'), _f('B','Frequency B'),
                       _f('t','t (s)'), _f('C','Phase C','float','0'), _f('D','Shift D','float','0')],
            'fn': _safe(lambda fv: f'f(t) = {_fmt(Trig.SineWave(fv["t"],fv["A"],fv["B"],fv["C"],fv["D"]))}'),
        },
        {
            'name': 'Polar ↔ Cartesian',
            'fields': [_f('r','r (magnitude)'), _f('theta','θ (degrees)')],
            'fn': _safe(lambda fv: f'x = {_fmt(Trig.PolarToCartesian(fv["r"],fv["theta"])[0])}\ny = {_fmt(Trig.PolarToCartesian(fv["r"],fv["theta"])[1])}'),
        },
    ]

# ─────────────── 10. Statistics ───────────────────────────────────────────────
if Stat:
    REGISTRY['Statistics'] = [
        {
            'name': 'Mean, Median, Mode',
            'fields': [_f('data','Data values (space-separated)','list')],
            'fn': _safe(lambda fv: f'Mean   = {_fmt(Stat.Mean(fv["data"]))}\nMedian = {_fmt(Stat.Median(fv["data"]))}\nMode   = {Stat.Mode(fv["data"])}'),
        },
        {
            'name': 'Standard deviation & variance',
            'fields': [_f('data','Data values (space-separated)','list')],
            'fn': _safe(lambda fv: f'Std Dev  = {_fmt(Stat.StandardDeviation(fv["data"]))}\nVariance = {_fmt(Stat.Variance(fv["data"]))}'),
        },
        {
            'name': 'Z-score  z = (x−μ)/σ',
            'fields': [_f('x','x value'), _f('mu','Mean μ'), _f('sigma','Std dev σ')],
            'fn': _safe(lambda fv: f'z = {_fmt(Stat.ZScore(fv["x"],fv["mu"],fv["sigma"]))}'),
        },
        {
            'name': 'Normal CDF  P(X ≤ x)',
            'fields': [_f('x','x value'), _f('mu','μ','float','0'), _f('sigma','σ','float','1')],
            'fn': _safe(lambda fv: f'P(X ≤ {fv["x"]}) = {_fmt(Stat.NormalCDF(fv["x"],fv["mu"],fv["sigma"]))}'),
        },
        {
            'name': 'Pearson correlation  r',
            'fields': [_f('x','X values (space-sep)','list'), _f('y','Y values (space-sep)','list')],
            'fn': _safe(lambda fv: f'r = {_fmt(Stat.PearsonCorrelation(fv["x"],fv["y"]))}'),
        },
        {
            'name': 'Linear regression  y = mx + b',
            'fields': [_f('x','X values (space-sep)','list'), _f('y','Y values (space-sep)','list')],
            'fn': _safe(lambda fv: f'slope = {_fmt(Stat.LinearRegression(fv["x"],fv["y"])[0])}\nintercept = {_fmt(Stat.LinearRegression(fv["x"],fv["y"])[1])}'),
        },
        {
            'name': 'Quartiles  Q1 / Q2 / Q3',
            'fields': [_f('data','Data values (space-separated)','list')],
            'fn': _safe(lambda fv: f'Q1 = {_fmt(Stat.Quartiles(fv["data"])[0])}\nQ2 = {_fmt(Stat.Quartiles(fv["data"])[1])}\nQ3 = {_fmt(Stat.Quartiles(fv["data"])[2])}'),
        },
    ]

# ─────────────── 11. Combinatorics ────────────────────────────────────────────
if Comb:
    REGISTRY['Combinatorics'] = [
        {
            'name': 'Factorial  n!',
            'fields': [_f('n','n','int')],
            'fn': _safe(lambda fv: f'{int(fv["n"])}! = {Comb.Factorial(int(fv["n"]))}'),
        },
        {
            'name': 'Permutations  nPr',
            'fields': [_f('n','n','int'), _f('r','r','int')],
            'fn': _safe(lambda fv: f'P({int(fv["n"])},{int(fv["r"])}) = {Comb.Permutations(int(fv["n"]),int(fv["r"]))}'),
        },
        {
            'name': 'Combinations  nCr',
            'fields': [_f('n','n','int'), _f('r','r','int')],
            'fn': _safe(lambda fv: f'C({int(fv["n"])},{int(fv["r"])}) = {Comb.Combinations(int(fv["n"]),int(fv["r"]))}'),
        },
        {
            'name': 'Fibonacci  F(n)',
            'fields': [_f('n','n (0-indexed)','int')],
            'fn': _safe(lambda fv: f'F({int(fv["n"])}) = {Comb.Fibonacci(int(fv["n"]))}'),
        },
        {
            'name': 'Catalan number  C(n)',
            'fields': [_f('n','n','int')],
            'fn': _safe(lambda fv: f'C({int(fv["n"])}) = {Comb.CatalanNumber(int(fv["n"]))}'),
        },
        {
            'name': 'Bell number  B(n)',
            'fields': [_f('n','n','int')],
            'fn': _safe(lambda fv: f'B({int(fv["n"])}) = {Comb.BellNumber(int(fv["n"]))}'),
        },
        {
            'name': 'Lattice paths  C(m+n, m)',
            'fields': [_f('m','m (steps right)','int'), _f('n','n (steps up)','int')],
            'fn': _safe(lambda fv: f'Paths = C({int(fv["m"])+int(fv["n"])},{int(fv["m"])}) = {Comb.LatticePaths(int(fv["m"]),int(fv["n"]))}'),
        },
    ]

# ─────────────── 12. Calculus ─────────────────────────────────────────────────
if Calc:
    REGISTRY['Calculus'] = [
        {
            'name': "Derivative  f'(x)  at a point",
            'fields': [_f('expr','f(x) expression  (use x)','expr'), _f('x','x value')],
            'fn': _safe(lambda fv: f"f'({fv['x']}) = {_fmt(Calc.Derivative(lambda x: eval(fv['expr'],{'x':x,'math':math}), fv['x']))}"),
        },
        {
            'name': 'Definite integral  ∫ᵃᵇ f(x) dx',
            'fields': [_f('expr','f(x)  (use x)','expr'), _f('a','Lower bound a'), _f('b','Upper bound b')],
            'fn': _safe(lambda fv: f"∫ = {_fmt(Calc.DefiniteIntegral(lambda x: eval(fv['expr'],{'x':x,'math':math}), fv['a'], fv['b']))}"),
        },
        {
            'name': 'Limit  lim f(x) as x→a',
            'fields': [_f('expr','f(x)  (use x)','expr'), _f('a','Approach point a')],
            'fn': _safe(lambda fv: f"lim = {_fmt(Calc.Limit(lambda x: eval(fv['expr'],{'x':x,'math':math}), fv['a']))}"),
        },
        {
            'name': 'Arc length  ∫ √(1+f\'²) dx',
            'fields': [_f('expr','f(x)  (use x)','expr'), _f('a','a'), _f('b','b')],
            'fn': _safe(lambda fv: f"L = {_fmt(Calc.ArcLength(lambda x: eval(fv['expr'],{'x':x,'math':math}), fv['a'], fv['b']))}"),
        },
        {
            'name': 'Taylor series  at center a',
            'fields': [_f('expr','f(x)  (use x)','expr'), _f('a','Center a'), _f('x','Evaluate at x'), _f('n','Terms n','int','10')],
            'fn': _safe(lambda fv: f"Taylor ≈ {_fmt(Calc.TaylorSeries(lambda x: eval(fv['expr'],{'x':x,'math':math}), fv['a'], fv['x'], int(fv['n'])))}"),
        },
    ]

# ─────────────── 13. Linear Algebra ───────────────────────────────────────────
if LinAlg:
    REGISTRY['Linear Algebra'] = [
        {'name': 'Dot product  a · b',
         'fields': [_f('a','Vector a (space-sep)','list'), _f('b','Vector b (space-sep)','list')],
         'fn': _safe(lambda fv: f'a·b = {_fmt(LinAlg.DotProduct(fv["a"],fv["b"]))}')},
        {'name': 'Vector magnitude  |v|',
         'fields': [_f('v','Vector (space-sep)','list')],
         'fn': _safe(lambda fv: f'|v| = {_fmt(LinAlg.VectorMagnitude(fv["v"]))}')},
        {'name': 'Angle between vectors',
         'fields': [_f('a','Vector a (space-sep)','list'), _f('b','Vector b (space-sep)','list')],
         'fn': _safe(lambda fv: f'θ = {_fmt(LinAlg.AngleBetween(fv["a"],fv["b"]))}°')},
        {'name': 'Cross product  a × b  (3D)',
         'fields': [_f('a','Vector a (3 components)','list'), _f('b','Vector b (3 components)','list')],
         'fn': _safe(lambda fv: f'a×b = {LinAlg.CrossProduct(fv["a"],fv["b"])}')},
        {'name': 'Vector normalize',
         'fields': [_f('v','Vector (space-sep)','list')],
         'fn': _safe(lambda fv: f'û = {[round(x,6) for x in LinAlg.VectorNormalize(fv["v"])]}')},
        {'name': 'Vector projection  (a onto b)',
         'fields': [_f('a','Vector a (space-sep)','list'), _f('b','Vector b (space-sep)','list')],
         'fn': _safe(lambda fv: f'proj = {[round(x,6) for x in LinAlg.VectorProjection(fv["a"],fv["b"])]}')},
        {'name': 'Matrix multiply  A×B  (2×2)',
         'fields': [_f('a1','A row 1 (space-sep)','list'), _f('a2','A row 2 (space-sep)','list'),
                    _f('b1','B row 1 (space-sep)','list'), _f('b2','B row 2 (space-sep)','list')],
         'fn': _safe(lambda fv: '\n'.join(str(r) for r in LinAlg.MatrixMultiply([fv["a1"],fv["a2"]],[fv["b1"],fv["b2"]])))},
        {'name': '2×2 Determinant',
         'fields': [_f('r1','Row 1 (space-sep 2 values)','list'), _f('r2','Row 2 (space-sep 2 values)','list')],
         'fn': _safe(lambda fv: f'det = {_fmt(LinAlg.Determinant([fv["r1"],fv["r2"]]))}')},
        {'name': '2×2 Matrix inverse',
         'fields': [_f('r1','Row 1 (space-sep 2 values)','list'), _f('r2','Row 2 (space-sep 2 values)','list')],
         'fn': _safe(lambda fv: '\n'.join(str(r) for r in LinAlg.MatrixInverse([fv["r1"],fv["r2"]])))},
        {'name': 'Trace',
         'fields': [_f('r1','Row 1 (space-sep)','list'), _f('r2','Row 2 (space-sep)','list')],
         'fn': _safe(lambda fv: f'tr = {_fmt(LinAlg.Trace([fv["r1"],fv["r2"]]))}')},
        {'name': 'Transpose  (2×2)',
         'fields': [_f('r1','Row 1 (space-sep)','list'), _f('r2','Row 2 (space-sep)','list')],
         'fn': _safe(lambda fv: '\n'.join(str(r) for r in LinAlg.Transpose([fv["r1"],fv["r2"]])))},
        {'name': 'Eigenvalues  (2×2)',
         'fields': [_f('r1','Row 1 (space-sep 2 values)','list'), _f('r2','Row 2 (space-sep 2 values)','list')],
         'fn': _safe(lambda fv: f'λ = {LinAlg.Eigenvalues2x2([fv["r1"],fv["r2"]])}')},
        {'name': 'Solve linear system  Ax=b  (2×2)',
         'fields': [_f('r1','A row 1 (space-sep)','list'), _f('r2','A row 2 (space-sep)','list'),
                    _f('b','b vector (space-sep)','list')],
         'fn': _safe(lambda fv: f'x = {[round(x,6) for x in LinAlg.SolveLinearSystem([fv["r1"],fv["r2"]],fv["b"])]}')},
        {'name': 'Rank  (2×2)',
         'fields': [_f('r1','Row 1 (space-sep)','list'), _f('r2','Row 2 (space-sep)','list')],
         'fn': _safe(lambda fv: f'rank = {LinAlg.Rank([fv["r1"],fv["r2"]])}')},
        {'name': 'Gram-Schmidt orthogonalise',
         'fields': [_f('v1','Vector 1 (space-sep)','list'), _f('v2','Vector 2 (space-sep)','list')],
         'fn': _safe(lambda fv: '\n'.join(f'u{i+1} = {[round(x,6) for x in v]}' for i,v in enumerate(LinAlg.GramSchmidt([fv["v1"],fv["v2"]]))))},
        {'name': 'Scalar triple product  a·(b×c)',
         'fields': [_f('a','a (3 values)','list'), _f('b','b (3 values)','list'), _f('c','c (3 values)','list')],
         'fn': _safe(lambda fv: f'a·(b×c) = {_fmt(LinAlg.ScalarTripleProduct(fv["a"],fv["b"],fv["c"]))}')},
        {'name': 'Cauchy-Schwarz inequality',
         'fields': [_f('a','Vector a (space-sep)','list'), _f('b','Vector b (space-sep)','list')],
         'fn': _safe(lambda fv: f'{LinAlg.CauchySchwarz(fv["a"],fv["b"])}')},
    ]

if Diff:
    REGISTRY['Differentiation'] = [
        {'name': "Derivative of polynomial  (at x)",
         'fields': [_f('coeffs','Coefficients high→low (space-sep)','list'), _f('x','x value')],
         'fn': _safe(lambda fv: f"p'(x) = {_fmt(Diff.DiffPolynomialAt(fv['coeffs'], fv['x']))}")},
        {'name': "Nth derivative of polynomial",
         'fields': [_f('coeffs','Coefficients high→low (space-sep)','list'), _f('n','n','int')],
         'fn': _safe(lambda fv: f"p^({int(fv['n'])}) coeffs = {Diff.DiffPolynomialNth(fv['coeffs'], int(fv['n']))}")},
        {'name': "Product rule  (f·g)'",
         'fields': [_f('fx','f(x) expression','expr'), _f('gx','g(x) expression','expr'), _f('x','x value')],
         'fn': _safe(lambda fv: f"(fg)' = {_fmt(Diff.ProductRule(lambda x: eval(fv['fx'],{'x':x,'math':math}), lambda x: eval(fv['gx'],{'x':x,'math':math}), fv['x']))}")},
        {'name': "Quotient rule  (f/g)'",
         'fields': [_f('fx','f(x) expression','expr'), _f('gx','g(x) expression','expr'), _f('x','x value')],
         'fn': _safe(lambda fv: f"(f/g)' = {_fmt(Diff.QuotientRule(lambda x: eval(fv['fx'],{'x':x,'math':math}), lambda x: eval(fv['gx'],{'x':x,'math':math}), fv['x']))}")},
        {'name': "Chain rule  f(g(x))'",
         'fields': [_f('fx','f(u) expression (use u)','expr'), _f('gx','g(x) expression (use x)','expr'), _f('x','x value')],
         'fn': _safe(lambda fv: f"(f∘g)' = {_fmt(Diff.ChainRule(lambda u: eval(fv['fx'],{'u':u,'math':math}), lambda x: eval(fv['gx'],{'x':x,'math':math}), fv['x']))}")},
        {'name': "Newton's method  root near x₀",
         'fields': [_f('expr','f(x) expression','expr'), _f('x0','Starting x₀')],
         'fn': _safe(lambda fv: f"root ≈ {_fmt(Diff.NewtonsMethod(lambda x: eval(fv['expr'],{'x':x,'math':math}), fv['x0']))}")},
        {'name': "Critical points",
         'fields': [_f('expr','f(x) expression','expr'), _f('a','Search from a'), _f('b','Search to b')],
         'fn': _safe(lambda fv: f"critical pts = {Diff.FindCriticalPoints(lambda x: eval(fv['expr'],{'x':x,'math':math}), fv['a'], fv['b'])}")},
        {'name': "Classify critical points",
         'fields': [_f('expr','f(x) expression','expr'), _f('a','From a'), _f('b','To b')],
         'fn': _safe(lambda fv: f"{Diff.ClassifyCriticalPoints(lambda x: eval(fv['expr'],{'x':x,'math':math}), fv['a'], fv['b'])}")},
        {'name': "Linearization  L(x)",
         'fields': [_f('expr','f(x) expression','expr'), _f('a','Center a'), _f('x','Evaluate at x')],
         'fn': _safe(lambda fv: f"L({fv['x']}) = {_fmt(Diff.Linearization(lambda x: eval(fv['expr'],{'x':x,'math':math}), fv['a'], fv['x']))}")},
        {'name': "Implicit derivative  dy/dx",
         'fields': [_f('fxy','F(x,y) expression (use x,y)','expr'), _f('x','x value'), _f('y','y value')],
         'fn': _safe(lambda fv: f"dy/dx = {_fmt(Diff.ImplicitDerivative(lambda x,y: eval(fv['fxy'],{'x':x,'y':y,'math':math}), fv['x'], fv['y']))}")},
        {'name': "L'Hôpital's rule",
         'fields': [_f('fx','f(x) expression','expr'), _f('gx','g(x) expression','expr'), _f('a','Limit point a')],
         'fn': _safe(lambda fv: f"lim f/g = {_fmt(Diff.LHopital(lambda x: eval(fv['fx'],{'x':x,'math':math}), lambda x: eval(fv['gx'],{'x':x,'math':math}), fv['a']))}")},
        {'name': "Related rate  dy/dt",
         'fields': [_f('expr','y = f(x) expression','expr'), _f('x','x value'), _f('dxdt','dx/dt')],
         'fn': _safe(lambda fv: f"dy/dt = {_fmt(Diff.RelatedRate(lambda x: eval(fv['expr'],{'x':x,'math':math}), fv['x'], fv['dxdt']))}")},
        {'name': "diff sin(x)", 'fields': [_f('x','x (degrees)')],
         'fn': _safe(lambda fv: f"d/dx sin = {_fmt(Diff.DiffSin(fv['x']))}")},
        {'name': "diff cos(x)", 'fields': [_f('x','x (degrees)')],
         'fn': _safe(lambda fv: f"d/dx cos = {_fmt(Diff.DiffCos(fv['x']))}")},
        {'name': "diff eˣ", 'fields': [_f('x','x value')],
         'fn': _safe(lambda fv: f"d/dx eˣ = {_fmt(Diff.DiffExp(fv['x']))}")},
        {'name': "diff ln(x)", 'fields': [_f('x','x value  (x > 0)')],
         'fn': _safe(lambda fv: f"d/dx ln = {_fmt(Diff.DiffLn(fv['x']))}")},
    ]

if Prob:
    REGISTRY['Probability'] = [
        {'name': 'Classical probability',
         'fields': [_f('fav','Favourable','int'), _f('tot','Total','int')],
         'fn': _safe(lambda fv: f'P = {_fmt(Prob.ClassicalProbability(int(fv["fav"]),int(fv["tot"])))}')},
        {'name': "Complement  P(A')",
         'fields': [_f('p','P(A)')],
         'fn': _safe(lambda fv: f"P(A') = {_fmt(Prob.Complement(fv['p']))}")},
        {'name': 'Union  P(A∪B)',
         'fields': [_f('pa','P(A)'), _f('pb','P(B)'), _f('pab','P(A∩B)')],
         'fn': _safe(lambda fv: f'P(A∪B) = {_fmt(Prob.UnionProbability(fv["pa"],fv["pb"],fv["pab"]))}')},
        {'name': 'Conditional  P(A|B)',
         'fields': [_f('pab','P(A∩B)'), _f('pb','P(B)')],
         'fn': _safe(lambda fv: f'P(A|B) = {_fmt(Prob.ConditionalProbability(fv["pab"],fv["pb"]))}')},
        {'name': 'Bayes theorem',
         'fields': [_f('pab','P(B|A)'), _f('pa','P(A)'), _f('pb','P(B)')],
         'fn': _safe(lambda fv: f'P(A|B) = {_fmt(Prob.Bayes(fv["pab"],fv["pa"],fv["pb"]))}')},
        {'name': 'Binomial PMF  P(X=k)',
         'fields': [_f('n','n','int'), _f('k','k','int'), _f('p','P(success)')],
         'fn': _safe(lambda fv: f'P(X={int(fv["k"])}) = {_fmt(Prob.BinomialPMF(int(fv["n"]),int(fv["k"]),fv["p"]))}')},
        {'name': 'Poisson PMF  P(X=k)',
         'fields': [_f('lam','λ'), _f('k','k','int')],
         'fn': _safe(lambda fv: f'P(X={int(fv["k"])}) = {_fmt(Prob.PoissonPMF(fv["lam"],int(fv["k"])))}')},
        {'name': 'Normal CDF  P(X≤x)',
         'fields': [_f('x','x'), _f('mu','μ','float','0'), _f('sigma','σ','float','1')],
         'fn': _safe(lambda fv: f'P = {_fmt(Prob.NormalCDF(fv["x"],fv["mu"],fv["sigma"]))}')},
        {'name': 'Normal P(a≤X≤b)',
         'fields': [_f('a','a'), _f('b','b'), _f('mu','μ','float','0'), _f('sigma','σ','float','1')],
         'fn': _safe(lambda fv: f'P = {_fmt(Prob.NormalBetween(fv["a"],fv["b"],fv["mu"],fv["sigma"]))}')},
        {'name': 'Expected value  E[X]',
         'fields': [_f('x','x values (space-sep)','list'), _f('p','probabilities (space-sep)','list')],
         'fn': _safe(lambda fv: f'E[X] = {_fmt(Prob.ExpectedValue(fv["x"],fv["p"]))}')},
        {'name': 'Variance  Var[X]',
         'fields': [_f('x','x values (space-sep)','list'), _f('p','probabilities (space-sep)','list')],
         'fn': _safe(lambda fv: f'Var[X] = {_fmt(Prob.Variance(fv["x"],fv["p"]))}')},
        {'name': 'Shannon entropy',
         'fields': [_f('p','probabilities (space-sep)','list')],
         'fn': _safe(lambda fv: f'H = {_fmt(Prob.ShannonEntropy(fv["p"]))} bits')},
        {'name': 'Geometric PMF  P(X=k)',
         'fields': [_f('p','P(success)'), _f('k','k','int')],
         'fn': _safe(lambda fv: f'P(X={int(fv["k"])}) = {_fmt(Prob.GeometricPMF(fv["p"],int(fv["k"])))}')},
        {'name': 'Total probability',
         'fields': [_f('pb_a','P(B|Aᵢ) values (space-sep)','list'), _f('pa','P(Aᵢ) values (space-sep)','list')],
         'fn': _safe(lambda fv: f'P(B) = {_fmt(Prob.TotalProbability(fv["pb_a"],fv["pa"]))}')},
    ]

if Discrete:
    REGISTRY['Discrete Math'] = [
        {'name': 'Is prime', 'fields': [_f('n','n','int')],
         'fn': _safe(lambda fv: f'{int(fv["n"])} is prime: {Discrete.IsPrime(int(fv["n"]))}')},
        {'name': 'Prime factorization', 'fields': [_f('n','n','int')],
         'fn': _safe(lambda fv: f'factors = {Discrete.PrimeFactorization(int(fv["n"]))}')},
        {'name': 'GCD', 'fields': [_f('a','a','int'), _f('b','b','int')],
         'fn': _safe(lambda fv: f'gcd = {Discrete.GCD(int(fv["a"]),int(fv["b"]))}')},
        {'name': 'LCM', 'fields': [_f('a','a','int'), _f('b','b','int')],
         'fn': _safe(lambda fv: f'lcm = {Discrete.LCM(int(fv["a"]),int(fv["b"]))}')},
        {'name': 'Extended GCD  (Bézout)', 'fields': [_f('a','a','int'), _f('b','b','int')],
         'fn': _safe(lambda fv: f'{Discrete.ExtendedGCD(int(fv["a"]),int(fv["b"]))}')},
        {'name': "Euler's totient  φ(n)", 'fields': [_f('n','n','int')],
         'fn': _safe(lambda fv: f'φ({int(fv["n"])}) = {Discrete.EulersTotient(int(fv["n"]))}')},
        {'name': 'Modular inverse  a⁻¹ mod m', 'fields': [_f('a','a','int'), _f('m','m','int')],
         'fn': _safe(lambda fv: f'a⁻¹ = {Discrete.ModularInverse(int(fv["a"]),int(fv["m"]))}')},
        {'name': 'Modular power  aⁿ mod m',
         'fields': [_f('a','a','int'), _f('n','n','int'), _f('m','m','int')],
         'fn': _safe(lambda fv: f'= {Discrete.ModularPower(int(fv["a"]),int(fv["n"]),int(fv["m"]))}')},
        {'name': 'Arithmetic series sum',
         'fields': [_f('a1','a₁'), _f('d','d'), _f('n','n','int')],
         'fn': _safe(lambda fv: f'S = {_fmt(Discrete.ArithmeticSum(fv["a1"],fv["d"],int(fv["n"])))}')},
        {'name': 'Geometric series sum',
         'fields': [_f('a1','a₁'), _f('r','r'), _f('n','n','int')],
         'fn': _safe(lambda fv: f'S = {_fmt(Discrete.GeometricSum(fv["a1"],fv["r"],int(fv["n"])))}')},
        {'name': 'Set union  A∪B',
         'fields': [_f('a','Set A (space-sep)','list'), _f('b','Set B (space-sep)','list')],
         'fn': _safe(lambda fv: f'A∪B = {sorted(Discrete.SetUnion(set(fv["a"]),set(fv["b"])))}')},
        {'name': 'Set intersection  A∩B',
         'fields': [_f('a','Set A (space-sep)','list'), _f('b','Set B (space-sep)','list')],
         'fn': _safe(lambda fv: f'A∩B = {sorted(Discrete.SetIntersection(set(fv["a"]),set(fv["b"])))}')},
        {'name': 'Primes up to N', 'fields': [_f('n','N','int')],
         'fn': _safe(lambda fv: f'primes = {Discrete.Primes(int(fv["n"]))}')},
    ]

if DiffGeo:
    REGISTRY['Differential Geometry'] = [
        {'name': 'Curvature  κ(t)',
         'fields': [_f('x','x(t) (use t)','expr'), _f('y','y(t) (use t)','expr'), _f('t','t value')],
         'fn': _safe(lambda fv: f'κ = {_fmt(DiffGeo.Curvature(lambda t: eval(fv["x"],{"t":t,"math":math}), lambda t: eval(fv["y"],{"t":t,"math":math}), fv["t"]))}')},
        {'name': 'Torsion  τ(t)',
         'fields': [_f('x','x(t)','expr'), _f('y','y(t)','expr'), _f('z','z(t)','expr'), _f('t','t value')],
         'fn': _safe(lambda fv: f'τ = {_fmt(DiffGeo.Torsion(lambda t: eval(fv["x"],{"t":t,"math":math}), lambda t: eval(fv["y"],{"t":t,"math":math}), lambda t: eval(fv["z"],{"t":t,"math":math}), fv["t"]))}')},
        {'name': 'Arc length  (parametric)',
         'fields': [_f('x','x(t)','expr'), _f('y','y(t)','expr'), _f('a','t from'), _f('b','t to')],
         'fn': _safe(lambda fv: f'L = {_fmt(DiffGeo.ArcLength(lambda t: eval(fv["x"],{"t":t,"math":math}), lambda t: eval(fv["y"],{"t":t,"math":math}), fv["a"], fv["b"]))}')},
        {'name': 'Unit tangent  T(t)',
         'fields': [_f('x','x(t)','expr'), _f('y','y(t)','expr'), _f('t','t value')],
         'fn': _safe(lambda fv: f'T = {[round(v,6) for v in DiffGeo.UnitTangent(lambda t: eval(fv["x"],{"t":t,"math":math}), lambda t: eval(fv["y"],{"t":t,"math":math}), fv["t"])]}')},
        {'name': 'Unit normal  N(t)',
         'fields': [_f('x','x(t)','expr'), _f('y','y(t)','expr'), _f('t','t value')],
         'fn': _safe(lambda fv: f'N = {[round(v,6) for v in DiffGeo.UnitNormal(lambda t: eval(fv["x"],{"t":t,"math":math}), lambda t: eval(fv["y"],{"t":t,"math":math}), fv["t"])]}')},
        {'name': 'Radius of curvature',
         'fields': [_f('x','x(t)','expr'), _f('y','y(t)','expr'), _f('t','t value')],
         'fn': _safe(lambda fv: f'R = {_fmt(DiffGeo.RadiusOfCurvature(lambda t: eval(fv["x"],{"t":t,"math":math}), lambda t: eval(fv["y"],{"t":t,"math":math}), fv["t"]))}')},
        {'name': 'Gaussian curvature  K',
         'fields': [_f('expr','z=f(x,y) (use x,y)','expr'), _f('x','x value'), _f('y','y value')],
         'fn': _safe(lambda fv: f'K = {_fmt(DiffGeo.GaussianCurvature(lambda x,y: eval(fv["expr"],{"x":x,"y":y,"math":math}), fv["x"], fv["y"]))}')},
        {'name': 'Mean curvature  H',
         'fields': [_f('expr','z=f(x,y) (use x,y)','expr'), _f('x','x value'), _f('y','y value')],
         'fn': _safe(lambda fv: f'H = {_fmt(DiffGeo.MeanCurvature(lambda x,y: eval(fv["expr"],{"x":x,"y":y,"math":math}), fv["x"], fv["y"]))}')},
        {'name': 'Surface normal',
         'fields': [_f('expr','z=f(x,y)','expr'), _f('x','x value'), _f('y','y value')],
         'fn': _safe(lambda fv: f'N = {[round(v,6) for v in DiffGeo.SurfaceNormal(lambda x,y: eval(fv["expr"],{"x":x,"y":y,"math":math}), fv["x"], fv["y"])]}')},
        {'name': 'Frenet-Serret frame',
         'fields': [_f('x','x(t)','expr'), _f('y','y(t)','expr'), _f('z','z(t)','expr'), _f('t','t value')],
         'fn': _safe(lambda fv: '\n'.join(f'{k}: {[round(v,4) for v in vec]}' for k,vec in zip(['T','N','B'],DiffGeo.FrenetSerretFrame(lambda t: eval(fv["x"],{"t":t,"math":math}), lambda t: eval(fv["y"],{"t":t,"math":math}), lambda t: eval(fv["z"],{"t":t,"math":math}), fv["t"]))))},
    ]

if AbsAlg:
    REGISTRY['Abstract Algebra'] = [
        {'name': 'Cyclic group ℤₙ', 'fields': [_f('n','n','int')],
         'fn': _safe(lambda fv: f'ℤ{int(fv["n"])} = {AbsAlg.CyclicGroupZn(int(fv["n"]))}')},
        {'name': 'Cayley table  (ℤₙ)', 'fields': [_f('n','n','int')],
         'fn': _safe(lambda fv: '\n'.join(str(row) for row in AbsAlg.CayleyTable(int(fv["n"]))))},
        {'name': 'Element order  in ℤₙ', 'fields': [_f('a','a','int'), _f('n','n','int')],
         'fn': _safe(lambda fv: f'ord({int(fv["a"])}) = {AbsAlg.ElementOrder(int(fv["a"]),int(fv["n"]))}')},
        {'name': 'Cyclic subgroup  ⟨a⟩ in ℤₙ', 'fields': [_f('a','a','int'), _f('n','n','int')],
         'fn': _safe(lambda fv: f'⟨{int(fv["a"])}⟩ = {AbsAlg.CyclicSubgroup(int(fv["a"]),int(fv["n"]))}')},
        {'name': "Lagrange's theorem", 'fields': [_f('G','|G|','int'), _f('H','|H|','int')],
         'fn': _safe(lambda fv: f'{AbsAlg.LagrangesTheorem(int(fv["G"]),int(fv["H"]))}')},
        {'name': 'Left coset  aH',
         'fields': [_f('a','a','int'), _f('H','H elements (space-sep)','list'), _f('n','mod n','int')],
         'fn': _safe(lambda fv: f'aH = {AbsAlg.LeftCoset(int(fv["a"]),[int(x) for x in fv["H"]],int(fv["n"]))}')},
        {'name': 'Is subgroup  H≤G  (ℤₙ)',
         'fields': [_f('H','H elements (space-sep)','list'), _f('n','n','int')],
         'fn': _safe(lambda fv: f'H≤G: {AbsAlg.IsSubgroup([int(x) for x in fv["H"]],int(fv["n"]))}')},
        {'name': 'Is normal subgroup',
         'fields': [_f('H','H elements (space-sep)','list'), _f('n','n','int')],
         'fn': _safe(lambda fv: f'H◁G: {AbsAlg.IsNormalSubgroup([int(x) for x in fv["H"]],int(fv["n"]))}')},
        {'name': 'Permutation cycle decomposition',
         'fields': [_f('perm','Permutation (space-sep 0-indexed)','list')],
         'fn': _safe(lambda fv: f'cycles = {AbsAlg.CycleDecomposition([int(x) for x in fv["perm"]])}')},
        {'name': 'Is abelian  (ℤₙ)', 'fields': [_f('n','n','int')],
         'fn': _safe(lambda fv: f'Abelian: {AbsAlg.IsAbelian(int(fv["n"]))}')},
    ]

if Topo:
    REGISTRY['Topology'] = [
        {'name': 'Interior of a set',
         'fields': [_f('pts','Set points (space-sep)','list'), _f('space','Space points (space-sep)','list')],
         'fn': _safe(lambda fv: f'int = {Topo.Interior(fv["pts"], fv["space"])}')},
        {'name': 'Closure of a set',
         'fields': [_f('pts','Set points (space-sep)','list'), _f('space','Space points (space-sep)','list')],
         'fn': _safe(lambda fv: f'cl = {Topo.Closure(fv["pts"], fv["space"])}')},
        {'name': 'Boundary of a set',
         'fields': [_f('pts','Set points (space-sep)','list'), _f('space','Space points (space-sep)','list')],
         'fn': _safe(lambda fv: f'∂S = {Topo.Boundary(fv["pts"], fv["space"])}')},
        {'name': 'Is connected', 'fields': [_f('pts','Points (space-sep)','list')],
         'fn': _safe(lambda fv: f'Connected: {Topo.IsConnected(fv["pts"])}')},
        {'name': 'Is compact subset', 'fields': [_f('pts','Subset points (space-sep)','list')],
         'fn': _safe(lambda fv: f'Compact: {Topo.IsCompactSubset(fv["pts"])}')},
        {'name': 'Hausdorff distance  d(A,B)',
         'fields': [_f('a','Set A (space-sep)','list'), _f('b','Set B (space-sep)','list')],
         'fn': _safe(lambda fv: f'd_H = {_fmt(Topo.HausdorffDistance(fv["a"],fv["b"]))}')},
        {'name': 'Euler characteristic  χ=V−E+F',
         'fields': [_f('V','Vertices V','int'), _f('E','Edges E','int'), _f('F','Faces F','int')],
         'fn': _safe(lambda fv: f'χ = {int(fv["V"])-int(fv["E"])+int(fv["F"])}')},
        {'name': 'Betti numbers',
         'fields': [_f('V','Vertices','int'), _f('E','Edges','int'), _f('F','Faces','int')],
         'fn': _safe(lambda fv: f'β = {Topo.BettiNumbers(int(fv["V"]),int(fv["E"]),int(fv["F"]))}')},
        {'name': 'Is dense', 'fields': [_f('pts','Subset (space-sep)','list'), _f('space','Space (space-sep)','list')],
         'fn': _safe(lambda fv: f'Dense: {Topo.IsDense(fv["pts"],fv["space"])}')},
    ]

if AlgGeo:
    REGISTRY['Algebraic Geometry'] = [
        {'name': 'Classify conic  ax²+bxy+cy²+dx+ey+f',
         'fields': [_f('a','a'), _f('b','b'), _f('c','c'), _f('d','d'), _f('e','e'), _f('f','f')],
         'fn': _safe(lambda fv: f'{AlgGeo.ClassifyConic(fv["a"],fv["b"],fv["c"],fv["d"],fv["e"],fv["f"])}')},
        {'name': 'Discriminant of polynomial',
         'fields': [_f('coeffs','Coefficients (space-sep high→low)','list')],
         'fn': _safe(lambda fv: f'Δ = {_fmt(AlgGeo.Discriminant([int(x) for x in fv["coeffs"]]))}')},
        {'name': 'Resultant of two polynomials',
         'fields': [_f('p','Poly p (space-sep)','list'), _f('q','Poly q (space-sep)','list')],
         'fn': _safe(lambda fv: f'Res = {_fmt(AlgGeo.Resultant([int(x) for x in fv["p"]],[int(x) for x in fv["q"]]))}')},
        {'name': 'J-invariant  y²=x³+ax+b',
         'fields': [_f('a','a'), _f('b','b')],
         'fn': _safe(lambda fv: f'j = {_fmt(AlgGeo.JInvariant(fv["a"],fv["b"]))}')},
        {'name': 'Elliptic curve discriminant',
         'fields': [_f('a','a'), _f('b','b')],
         'fn': _safe(lambda fv: f'Δ = {_fmt(AlgGeo.EllipticCurveDiscriminant(fv["a"],fv["b"]))}')},
        {'name': 'Points on elliptic curve over F_p',
         'fields': [_f('a','a','int'), _f('b','b','int'), _f('p','prime p','int')],
         'fn': _safe(lambda fv: f'points = {AlgGeo.EllipticCurvePoints_Fp(int(fv["a"]),int(fv["b"]),int(fv["p"]))}')},
        {'name': 'Bezout number',
         'fields': [_f('d1','Degree d₁','int'), _f('d2','Degree d₂','int')],
         'fn': _safe(lambda fv: f'|V₁∩V₂| ≤ {AlgGeo.BezoutNumber(int(fv["d1"]),int(fv["d2"]))}')},
        {'name': 'Affine variety  V(f)  1D',
         'fields': [_f('coeffs','f(x) coefficients (space-sep)','list')],
         'fn': _safe(lambda fv: f'roots = {[round(r,6) for r in AlgGeo.AffineVariety1D([int(x) for x in fv["coeffs"]])]}')},
        {'name': 'Plane curve genus  g=(d−1)(d−2)/2',
         'fields': [_f('d','Degree d','int')],
         'fn': _safe(lambda fv: f'g = {AlgGeo.PlaneCurveGenus(int(fv["d"]))}')},
        {'name': 'Is smooth point',
         'fields': [_f('px','∂F/∂x (use x,y)','expr'), _f('py','∂F/∂y (use x,y)','expr'),
                    _f('x','x value'), _f('y','y value')],
         'fn': _safe(lambda fv: f'Smooth: {AlgGeo.IsSmoothPoint(lambda x,y: eval(fv["px"],{"x":x,"y":y,"math":math}), lambda x,y: eval(fv["py"],{"x":x,"y":y,"math":math}), fv["x"], fv["y"])}')},
    ]


# Navigation tree definition — ORDER matters (matches DebugUI menu)
NAV_TREE = [
    ('Basic Math',                 REGISTRY.get('Basic Math',[])),
    ('Physics', [
        ('1D Kinematics',          REGISTRY.get('Physics 1D',[])),
        ('Energy & Work',          REGISTRY.get('Physics — Energy',[])),
        ('Springs & SHM',          REGISTRY.get('Physics — Springs',[])),
        ('Momentum & Impulse',     REGISTRY.get('Physics — Momentum',[])),
        ('Center of Mass',         REGISTRY.get('Physics — Center of Mass',[])),
    ]),
    ('Algebra',                    REGISTRY.get('Algebra',[])),
    ('Geometry',                   REGISTRY.get('Geometry',[])),
    ('Trigonometry',               REGISTRY.get('Trigonometry',[])),
    ('Calculus',                   REGISTRY.get('Calculus',[])),
    ('Differentiation',            REGISTRY.get('Differentiation',[])),
    ('Statistics',                 REGISTRY.get('Statistics',[])),
    ('Probability',                REGISTRY.get('Probability',[])),
    ('Combinatorics',              REGISTRY.get('Combinatorics',[])),
    ('Discrete Math',              REGISTRY.get('Discrete Math',[])),
    ('Linear Algebra',             REGISTRY.get('Linear Algebra',[])),
    ('Differential Geometry',      REGISTRY.get('Differential Geometry',[])),
    ('Abstract Algebra',           REGISTRY.get('Abstract Algebra',[])),
    ('Topology',                   REGISTRY.get('Topology',[])),
    ('Algebraic Geometry',         REGISTRY.get('Algebraic Geometry',[])),
]

# ══════════════════════════════════════════════════════════════════════════════
# LAYERED CALCULATOR POPUP
# ══════════════════════════════════════════════════════════════════════════════

class CalcPopup(tk.Toplevel):
    """Inline ripcord calculator — press ? in any field to open."""
    HIST = []

    def __init__(self, parent, target_var):
        super().__init__(parent)
        self.target_var = target_var
        self.title('⊕  Quick Calculator')
        self.configure(bg=C['bg'])
        self.resizable(False, False)
        self._build()
        self.grab_set()

    def _build(self):
        pad = {'padx': 12, 'pady': 6}
        title = tk.Label(self, text='⊕  Quick Calculator',
                         font=FONTS['mono_lg'], fg=C['accent'], bg=C['bg'])
        title.pack(**pad, anchor='w')
        sub = tk.Label(self, text='Result will fill the field you typed ? in.',
                       font=FONTS['ui_sm'], fg=C['text_dim'], bg=C['bg'])
        sub.pack(padx=12, anchor='w')
        tk.Frame(self, height=1, bg=C['border']).pack(fill='x', padx=12, pady=4)

        # Expression entry
        expr_frame = tk.Frame(self, bg=C['bg'])
        expr_frame.pack(fill='x', padx=12, pady=4)
        tk.Label(expr_frame, text='Expression:', font=FONTS['mono'],
                 fg=C['text_dim'], bg=C['bg']).pack(anchor='w')
        self.expr_var = tk.StringVar()
        expr_entry = tk.Entry(expr_frame, textvariable=self.expr_var,
                              font=FONTS['mono'], bg=C['bg3'], fg=C['accent'],
                              insertbackground=C['accent'], relief='flat',
                              highlightthickness=1, highlightcolor=C['accent'],
                              highlightbackground=C['border'], width=38)
        expr_entry.pack(fill='x', ipady=6)
        expr_entry.bind('<Return>', lambda e: self._evaluate())
        expr_entry.focus_set()

        hint = tk.Label(expr_frame,
                        text='Use: sqrt, pi, sin, cos, tan, log, exp, abs  |  Examples: 3**2 + 4**2',
                        font=FONTS['mono_sm'], fg=C['text_dim'], bg=C['bg'])
        hint.pack(anchor='w', pady=(2,0))

        # Shortcut buttons — row 1: physics formulas
        btn_frame = tk.Frame(self, bg=C['bg'])
        btn_frame.pack(fill='x', padx=12, pady=(6,2))
        shortcuts = [
            ('½mv²',    self._ke),
            ('mgh',     self._gpe),
            ('F·d·cosθ',self._work),
            ('√x',      self._sqrt),
            ('a²+b²',   self._pyth),
        ]
        for label, cmd in shortcuts:
            b = tk.Button(btn_frame, text=label, command=cmd,
                          font=FONTS['mono_sm'], bg=C['btn'], fg=C['btn_text'],
                          activebackground=C['btn_hover'], activeforeground=C['accent'],
                          relief='flat', padx=8, pady=4, cursor='hand2')
            b.pack(side='left', padx=2)

        # Shortcut buttons — row 2: unit conversions
        conv_frame = tk.Frame(self, bg=C['bg'])
        conv_frame.pack(fill='x', padx=12, pady=(0,4))
        tk.Label(conv_frame, text='convert:', font=FONTS['mono_sm'],
                 fg=C['text_dim'], bg=C['bg']).pack(side='left', padx=(0,4))
        conv_shortcuts = [
            ('m↔cm',  self._conv_m_cm),
            ('kg↔g',  self._conv_kg_g),
            ('J↔kJ',  self._conv_j_kj),
            ('°↔rad', self._conv_deg_rad),
            ('mph↔m/s',self._conv_mph_ms),
        ]
        for label, cmd in conv_shortcuts:
            b = tk.Button(conv_frame, text=label, command=cmd,
                          font=FONTS['mono_sm'], bg=C['bg3'], fg=C['accent2'],
                          activebackground=C['btn_hover'], activeforeground=C['accent2'],
                          relief='flat', padx=6, pady=3, cursor='hand2')
            b.pack(side='left', padx=2)

        # History
        if self.HIST:
            tk.Label(self, text='Previous results:', font=FONTS['ui_sm'],
                     fg=C['text_dim'], bg=C['bg']).pack(anchor='w', padx=12, pady=(4,0))
            for label, val in self.HIST[-4:]:
                row = tk.Frame(self, bg=C['bg'])
                row.pack(fill='x', padx=16, pady=1)
                tk.Label(row, text=f'{label}  = {val:.6g}', font=FONTS['mono_sm'],
                         fg=C['text_code'], bg=C['bg']).pack(side='left')
                tk.Button(row, text='use ↑', font=FONTS['mono_sm'],
                          bg=C['btn'], fg=C['btn_text'], relief='flat', padx=4,
                          cursor='hand2',
                          command=partial(self._use, val)).pack(side='right')

        # Result display
        self.result_var = tk.StringVar(value='')
        tk.Label(self, textvariable=self.result_var, font=FONTS['result'],
                 fg=C['result'], bg=C['bg']).pack(padx=12, pady=4, anchor='w')

        # Buttons
        btn_row = tk.Frame(self, bg=C['bg'])
        btn_row.pack(fill='x', padx=12, pady=8)
        tk.Button(btn_row, text='Calculate', command=self._evaluate,
                  font=FONTS['mono'], bg=C['btn'], fg=C['btn_text'],
                  activebackground=C['btn_hover'], relief='flat',
                  padx=16, pady=6, cursor='hand2').pack(side='left')
        tk.Button(btn_row, text='Use Result', command=self._use_result,
                  font=FONTS['mono'], bg=C['accent'], fg=C['bg'],
                  activebackground='#00cc80', relief='flat',
                  padx=16, pady=6, cursor='hand2').pack(side='left', padx=8)
        tk.Button(btn_row, text='Cancel', command=self.destroy,
                  font=FONTS['mono'], bg=C['bg2'], fg=C['text_dim'],
                  relief='flat', padx=12, pady=6, cursor='hand2').pack(side='right')

        self._result_value = None

    def _safe_eval(self, expr):
        safe_globals = {
            'sqrt': math.sqrt, 'pi': math.pi, 'sin': math.sin, 'cos': math.cos,
            'tan': math.tan, 'log': math.log, 'exp': math.exp, 'abs': abs,
            'round': round, 'pow': pow, '__builtins__': {},
        }
        return float(eval(expr, safe_globals))

    def _evaluate(self):
        expr = self.expr_var.get().strip()
        if not expr:
            return
        try:
            result = self._safe_eval(expr)
            self._result_value = result
            self.result_var.set(f'= {result:.8g}')
            CalcPopup.HIST.append((expr, result))
        except Exception as e:
            self.result_var.set(f'Error: {e}')

    def _use_result(self):
        if self._result_value is not None:
            self.target_var.set(str(self._result_value))
            self.destroy()

    def _use(self, val):
        self.target_var.set(str(val))
        self.destroy()

    def _ke(self):
        w = tk.Toplevel(self); w.configure(bg=C['bg']); w.title('KE = ½mv²')
        mv = tk.StringVar(); vv = tk.StringVar()
        for lbl, var in [('m (kg):', mv), ('v (m/s):', vv)]:
            r = tk.Frame(w, bg=C['bg']); r.pack(padx=12, pady=4)
            tk.Label(r, text=lbl, font=FONTS['mono'], fg=C['text'], bg=C['bg']).pack(side='left')
            tk.Entry(r, textvariable=var, font=FONTS['mono'], bg=C['bg3'],
                     fg=C['accent'], width=12, relief='flat').pack(side='left', padx=4)
        def go():
            try:
                r = 0.5*float(mv.get())*float(vv.get())**2
                self.expr_var.set(f'0.5*{mv.get()}*{vv.get()}**2')
                self._result_value = r; self.result_var.set(f'= {r:.8g} J')
                w.destroy()
            except Exception as e: messagebox.showerror('Error', str(e), parent=w)
        tk.Button(w, text='Calculate', command=go, font=FONTS['mono'],
                  bg=C['btn'], fg=C['btn_text'], relief='flat', padx=8, pady=4).pack(pady=8)

    def _gpe(self):
        w = tk.Toplevel(self); w.configure(bg=C['bg']); w.title('GPE = mgh')
        mv=tk.StringVar(); gv=tk.StringVar(value='9.8'); hv=tk.StringVar()
        for lbl, var in [('m (kg):',mv),('g (m/s²):',gv),('h (m):',hv)]:
            r=tk.Frame(w,bg=C['bg']); r.pack(padx=12,pady=4)
            tk.Label(r,text=lbl,font=FONTS['mono'],fg=C['text'],bg=C['bg']).pack(side='left')
            tk.Entry(r,textvariable=var,font=FONTS['mono'],bg=C['bg3'],fg=C['accent'],width=10,relief='flat').pack(side='left',padx=4)
        def go():
            try:
                r=float(mv.get())*float(gv.get())*float(hv.get())
                self.expr_var.set(f'{mv.get()}*{gv.get()}*{hv.get()}')
                self._result_value=r; self.result_var.set(f'= {r:.8g} J'); w.destroy()
            except Exception as e: messagebox.showerror('Error',str(e),parent=w)
        tk.Button(w,text='Calculate',command=go,font=FONTS['mono'],bg=C['btn'],fg=C['btn_text'],relief='flat',padx=8,pady=4).pack(pady=8)

    def _sqrt(self):
        w=tk.Toplevel(self); w.configure(bg=C['bg']); w.title('√x')
        xv=tk.StringVar()
        r=tk.Frame(w,bg=C['bg']); r.pack(padx=12,pady=8)
        tk.Label(r,text='x:',font=FONTS['mono'],fg=C['text'],bg=C['bg']).pack(side='left')
        tk.Entry(r,textvariable=xv,font=FONTS['mono'],bg=C['bg3'],fg=C['accent'],width=14,relief='flat').pack(side='left',padx=4)
        def go():
            try:
                res=math.sqrt(float(xv.get()))
                self.expr_var.set(f'sqrt({xv.get()})')
                self._result_value=res; self.result_var.set(f'= {res:.8g}'); w.destroy()
            except Exception as e: messagebox.showerror('Error',str(e),parent=w)
        tk.Button(w,text='Calculate',command=go,font=FONTS['mono'],bg=C['btn'],fg=C['btn_text'],relief='flat',padx=8,pady=4).pack(pady=8)

    def _pyth(self):
        w=tk.Toplevel(self); w.configure(bg=C['bg']); w.title('c = √(a²+b²)')
        av=tk.StringVar(); bv=tk.StringVar()
        for lbl,var in [('a:',av),('b:',bv)]:
            r=tk.Frame(w,bg=C['bg']); r.pack(padx=12,pady=4)
            tk.Label(r,text=lbl,font=FONTS['mono'],fg=C['text'],bg=C['bg']).pack(side='left')
            tk.Entry(r,textvariable=var,font=FONTS['mono'],bg=C['bg3'],fg=C['accent'],width=12,relief='flat').pack(side='left',padx=4)
        def go():
            try:
                res=math.sqrt(float(av.get())**2+float(bv.get())**2)
                self.expr_var.set(f'sqrt({av.get()}**2+{bv.get()}**2)')
                self._result_value=res; self.result_var.set(f'= {res:.8g}'); w.destroy()
            except Exception as e: messagebox.showerror('Error',str(e),parent=w)
        tk.Button(w,text='Calculate',command=go,font=FONTS['mono'],bg=C['btn'],fg=C['btn_text'],relief='flat',padx=8,pady=4).pack(pady=8)

    def _work(self):
        """W = F · d · cos(θ)"""
        w=tk.Toplevel(self); w.configure(bg=C['bg']); w.title('W = F·d·cos θ')
        Fv=tk.StringVar(); dv=tk.StringVar(); tv=tk.StringVar(value='0')
        for lbl,var,hint in [('F (N):',Fv,''),('d (m):',dv,''),('θ (deg):',tv,'0 = parallel')]:
            r=tk.Frame(w,bg=C['bg']); r.pack(padx=12,pady=4)
            tk.Label(r,text=lbl,font=FONTS['mono'],fg=C['text'],bg=C['bg'],width=8).pack(side='left')
            tk.Entry(r,textvariable=var,font=FONTS['mono'],bg=C['bg3'],fg=C['accent'],width=12,relief='flat').pack(side='left',padx=4)
            if hint:
                tk.Label(r,text=hint,font=FONTS['mono_sm'],fg=C['text_dim'],bg=C['bg']).pack(side='left')
        def go():
            try:
                res=float(Fv.get())*float(dv.get())*math.cos(math.radians(float(tv.get())))
                self.expr_var.set(f'{Fv.get()}*{dv.get()}*cos({tv.get()}°)')
                self._result_value=res; self.result_var.set(f'= {res:.8g} J')
                CalcPopup.HIST.append((f'W=F·d·cosθ', res))
                w.destroy()
            except Exception as e: messagebox.showerror('Error',str(e),parent=w)
        tk.Button(w,text='Calculate',command=go,font=FONTS['mono'],bg=C['btn'],fg=C['btn_text'],relief='flat',padx=8,pady=4).pack(pady=8)

    # ── Unit conversions ──────────────────────────────────────────────────────

    def _conv_window(self, title, conversions):
        """
        Generic unit conversion window.
        conversions: list of (label, formula_fn, unit_out)
        """
        w=tk.Toplevel(self); w.configure(bg=C['bg']); w.title(title)
        tk.Label(w,text=title,font=FONTS['mono_lg'],fg=C['accent2'],bg=C['bg'],pady=6).pack()
        tk.Frame(w,height=1,bg=C['border']).pack(fill='x',padx=8)
        xv=tk.StringVar()
        row=tk.Frame(w,bg=C['bg']); row.pack(padx=12,pady=8)
        tk.Label(row,text='Value:',font=FONTS['mono'],fg=C['text'],bg=C['bg']).pack(side='left')
        e=tk.Entry(row,textvariable=xv,font=FONTS['mono'],bg=C['bg3'],fg=C['accent'],
                   width=14,relief='flat',insertbackground=C['accent'])
        e.pack(side='left',padx=6,ipady=4)
        e.focus_set()
        # Result labels
        result_vars = []
        for label, _, unit in conversions:
            r=tk.Frame(w,bg=C['bg']); r.pack(fill='x',padx=16,pady=2)
            tk.Label(r,text=f'{label}:',font=FONTS['mono_sm'],fg=C['text_dim'],
                     bg=C['bg'],width=14,anchor='e').pack(side='left')
            rv=tk.StringVar(value='—')
            result_vars.append(rv)
            lbl=tk.Label(r,textvariable=rv,font=FONTS['mono'],fg=C['result'],bg=C['bg'])
            lbl.pack(side='left',padx=6)
            use_btn=tk.Button(r,text='use',font=FONTS['mono_sm'],bg=C['btn'],fg=C['btn_text'],
                              relief='flat',padx=4,cursor='hand2',
                              command=partial(self._use_conv, rv, w))
            use_btn.pack(side='right',padx=4)
        def calc(*args):
            try:
                val=float(xv.get())
                for i,(label,fn,unit) in enumerate(conversions):
                    res=fn(val)
                    result_vars[i].set(f'{res:.8g} {unit}')
            except Exception:
                for rv in result_vars: rv.set('—')
        xv.trace_add('write', calc)
        e.bind('<Return>', calc)
        tk.Button(w,text='Close',command=w.destroy,font=FONTS['mono'],
                  bg=C['bg2'],fg=C['text_dim'],relief='flat',padx=12,pady=4).pack(pady=8)

    def _use_conv(self, result_var, window):
        """Extract numeric part from a conversion result and fill target field."""
        raw = result_var.get().split()[0]
        try:
            val = float(raw)
            self._result_value = val
            self.target_var.set(str(val))
            self.result_var.set(f'= {val:.8g}')
            CalcPopup.HIST.append(('unit conv', val))
            window.destroy()
        except Exception:
            pass

    def _conv_m_cm(self):
        self._conv_window('Length — m / cm / mm / km', [
            ('→ cm',  lambda x: x * 100,       'cm'),
            ('→ mm',  lambda x: x * 1000,      'mm'),
            ('→ km',  lambda x: x / 1000,      'km'),
            ('→ in',  lambda x: x * 39.3701,   'in'),
            ('→ ft',  lambda x: x * 3.28084,   'ft'),
            ('cm → m',lambda x: x / 100,       'm'),
        ])

    def _conv_kg_g(self):
        self._conv_window('Mass — kg / g / lb / oz', [
            ('→ g',   lambda x: x * 1000,      'g'),
            ('→ mg',  lambda x: x * 1e6,       'mg'),
            ('→ lb',  lambda x: x * 2.20462,   'lb'),
            ('→ oz',  lambda x: x * 35.274,    'oz'),
            ('g → kg',lambda x: x / 1000,      'kg'),
        ])

    def _conv_j_kj(self):
        self._conv_window('Energy — J / kJ / cal / eV', [
            ('→ kJ',  lambda x: x / 1000,      'kJ'),
            ('→ cal', lambda x: x / 4.184,     'cal'),
            ('→ kcal',lambda x: x / 4184,      'kcal'),
            ('→ eV',  lambda x: x / 1.602e-19, 'eV'),
            ('kJ → J',lambda x: x * 1000,      'J'),
        ])

    def _conv_deg_rad(self):
        self._conv_window('Angle — degrees / radians', [
            ('deg → rad', lambda x: x * math.pi / 180, 'rad'),
            ('rad → deg', lambda x: x * 180 / math.pi, '°'),
            ('→ grad',    lambda x: x * 400 / 360,     'grad'),
            ('→ turns',   lambda x: x / 360,           'turns'),
        ])

    def _conv_mph_ms(self):
        self._conv_window('Speed — m/s / km/h / mph', [
            ('m/s → km/h', lambda x: x * 3.6,        'km/h'),
            ('m/s → mph',  lambda x: x * 2.23694,    'mph'),
            ('m/s → knots',lambda x: x * 1.94384,    'kn'),
            ('mph → m/s',  lambda x: x / 2.23694,    'm/s'),
            ('km/h → m/s', lambda x: x / 3.6,        'm/s'),
        ])


# ══════════════════════════════════════════════════════════════════════════════
# WORK PANEL  (right side — dynamic form + output)
# ══════════════════════════════════════════════════════════════════════════════

class WorkPanel(tk.Frame):
    def __init__(self, master, step_var, word_var, art_engine=None):
        super().__init__(master, bg=C['bg'])
        self.step_var = step_var
        self.word_var = word_var
        self._art_engine = art_engine   # set at construction — never None after fix
        self._current_fn = None
        self._field_vars = {}
        self._build()

    def _build(self):
        # Header bar
        hdr = tk.Frame(self, bg=C['bg2'], height=48)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)
        self.fn_title = tk.Label(hdr, text='← Select a function from the sidebar',
                                 font=FONTS['mono_lg'], fg=C['accent2'], bg=C['bg2'],
                                 anchor='w', padx=16)
        self.fn_title.pack(side='left', fill='y')
        self.section_label = tk.Label(hdr, text='', font=FONTS['ui_sm'],
                                      fg=C['text_dim'], bg=C['bg2'], padx=8)
        self.section_label.pack(side='right', fill='y')

        # Divider
        tk.Frame(self, height=1, bg=C['border_hi']).pack(fill='x')

        # Scrollable body
        body = tk.Frame(self, bg=C['bg'])
        body.pack(fill='both', expand=True)

        # Left: form
        self.form_frame = tk.Frame(body, bg=C['bg'], width=380)
        self.form_frame.pack(side='left', fill='y', padx=0)
        self.form_frame.pack_propagate(False)
        tk.Frame(body, width=1, bg=C['border']).pack(side='left', fill='y')

        # Right: output
        out_frame = tk.Frame(body, bg=C['bg'])
        out_frame.pack(side='left', fill='both', expand=True)
        out_hdr = tk.Frame(out_frame, bg=C['bg2'])
        out_hdr.pack(fill='x')
        tk.Label(out_hdr, text='  OUTPUT', font=FONTS['nav_sec'],
                 fg=C['text_dim'], bg=C['bg2']).pack(side='left', pady=6)
        clear_btn = tk.Button(out_hdr, text='clear', font=FONTS['mono_sm'],
                              bg=C['bg2'], fg=C['text_dim'], relief='flat',
                              cursor='hand2', command=self._clear_output)
        clear_btn.pack(side='right', padx=8)
        tk.Frame(out_frame, height=1, bg=C['border']).pack(fill='x')
        self.output_text = tk.Text(out_frame, bg=C['bg'], fg=C['text'],
                                   font=FONTS['mono'], relief='flat',
                                   insertbackground=C['accent'], wrap='word',
                                   state='disabled', padx=16, pady=12)
        out_scroll = tk.Scrollbar(out_frame, command=self.output_text.yview,
                                  bg=C['bg'], troughcolor=C['bg2'])
        self.output_text.configure(yscrollcommand=out_scroll.set)
        out_scroll.pack(side='right', fill='y')
        self.output_text.pack(fill='both', expand=True)

        # Output text tags
        self.output_text.tag_configure('result',  foreground=C['result'],  font=FONTS['result'])
        self.output_text.tag_configure('label',   foreground=C['accent2'], font=FONTS['mono'])
        self.output_text.tag_configure('step',    foreground=C['text_dim'],font=FONTS['mono_sm'])
        self.output_text.tag_configure('sep',     foreground=C['border'],  font=FONTS['mono_sm'])
        self.output_text.tag_configure('error',   foreground=C['error'],   font=FONTS['mono'])
        self.output_text.tag_configure('formula', foreground=C['accent4'], font=FONTS['mono_sm'])
        self.output_text.tag_configure('dim',     foreground=C['text_dim'],font=FONTS['mono_sm'])
        self.output_text.tag_configure('parsed',  foreground=C['accent3'], font=FONTS['mono_sm'])

    def load_function(self, section_name, fn_spec):
        """Populate the form for the given function spec."""
        self._current_fn = fn_spec
        self._field_vars = {}
        for w in self.form_frame.winfo_children():
            w.destroy()

        self.fn_title.configure(text=fn_spec['name'])
        self.section_label.configure(text=section_name)

        fields = fn_spec.get('fields', [])
        if not fields:
            lbl = tk.Label(self.form_frame, text='No inputs required.\nPress Calculate to run.',
                           font=FONTS['mono_sm'], fg=C['text_dim'], bg=C['bg'],
                           justify='left', padx=20, pady=20)
            lbl.pack(anchor='nw', padx=16, pady=16)
        else:
            lbl_hdr = tk.Label(self.form_frame, text='  INPUTS', font=FONTS['nav_sec'],
                               fg=C['text_dim'], bg=C['bg2'])
            lbl_hdr.pack(fill='x', pady=(0,1))
            tk.Frame(self.form_frame, height=1, bg=C['border']).pack(fill='x')
            scroll_canvas = tk.Canvas(self.form_frame, bg=C['bg'], highlightthickness=0)
            scrollbar = tk.Scrollbar(self.form_frame, orient='vertical',
                                     command=scroll_canvas.yview)
            scroll_canvas.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side='right', fill='y')
            scroll_canvas.pack(side='left', fill='both', expand=True)
            inner = tk.Frame(scroll_canvas, bg=C['bg'])
            win_id = scroll_canvas.create_window((0,0), window=inner, anchor='nw')
            inner.bind('<Configure>',
                       lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox('all')))
            scroll_canvas.bind('<Configure>',
                               lambda e: scroll_canvas.itemconfig(win_id, width=e.width))

            for field in fields:
                self._make_field(inner, field)

        # Word mode section
        if fn_spec.get('word_fn'):
            wp = tk.Frame(self.form_frame, bg=C['step_bg'])
            wp.pack(fill='x', padx=0, pady=8)
            tk.Frame(wp, height=1, bg=C['accent3']).pack(fill='x')
            word_row = tk.Frame(wp, bg=C['step_bg'])
            word_row.pack(fill='x', padx=12, pady=6)
            tk.Label(word_row, text='📝 Word Problem:', font=FONTS['mono_sm'],
                     fg=C['accent3'], bg=C['step_bg']).pack(anchor='w')
            self.word_var_entry = tk.StringVar()
            we = tk.Entry(word_row, textvariable=self.word_var_entry,
                          font=FONTS['mono_sm'], bg=C['bg3'], fg=C['accent3'],
                          insertbackground=C['accent3'], relief='flat',
                          highlightthickness=1, highlightcolor=C['accent3'],
                          highlightbackground=C['border'])
            we.pack(fill='x', ipady=4, pady=2)
            tk.Button(word_row, text='Parse & Fill Fields', command=self._parse_word,
                      font=FONTS['mono_sm'], bg=C['bg2'], fg=C['accent3'],
                      relief='flat', padx=8, pady=3, cursor='hand2').pack(anchor='w', pady=2)
            tk.Frame(wp, height=1, bg=C['border']).pack(fill='x')
        else:
            self.word_var_entry = None

        # Calculate button
        tk.Frame(self.form_frame, height=8, bg=C['bg']).pack()
        calc_btn = tk.Button(self.form_frame, text='▶  Calculate',
                             font=FONTS['mono_lg'], bg=C['accent'], fg=C['bg'],
                             activebackground='#00cc80', activeforeground=C['bg'],
                             relief='flat', padx=20, pady=10, cursor='hand2',
                             command=self._calculate)
        calc_btn.pack(padx=16, fill='x')
        self.form_frame.bind_all('<Return>', lambda e: self._calculate())

    def _make_field(self, parent, field):
        container = tk.Frame(parent, bg=C['bg'])
        container.pack(fill='x', padx=16, pady=6)

        lbl_row = tk.Frame(container, bg=C['bg'])
        lbl_row.pack(fill='x')
        tk.Label(lbl_row, text=field['label'], font=FONTS['mono'],
                 fg=C['tag_key'], bg=C['bg'], anchor='w').pack(side='left')
        if field.get('hint'):
            tk.Label(lbl_row, text=f'  ({field["hint"]})', font=FONTS['mono_sm'],
                     fg=C['text_dim'], bg=C['bg']).pack(side='left')

        var = tk.StringVar(value=str(field.get('default', '')))
        self._field_vars[field['id']] = (var, field['type'])

        entry = tk.Entry(container, textvariable=var,
                         font=FONTS['mono'], bg=C['bg3'], fg=C['accent'],
                         insertbackground=C['accent'], relief='flat',
                         highlightthickness=1, highlightcolor=C['border_hi'],
                         highlightbackground=C['border'],
                         width=30)
        entry.pack(fill='x', ipady=6)

        # ? binding for ripcord
        entry.bind('<Key-question>', lambda e, v=var: (
            CalcPopup(self.winfo_toplevel(), v), 'break'))

        # Hint for list type
        if field['type'] == 'list':
            tk.Label(container, text='(space-separated values)',
                     font=FONTS['mono_sm'], fg=C['text_dim'], bg=C['bg']).pack(anchor='w')
        elif field['type'] == 'expr':
            tk.Label(container, text='(Python expression, use x, math.sin etc.)',
                     font=FONTS['mono_sm'], fg=C['text_dim'], bg=C['bg']).pack(anchor='w')

    def _parse_values(self):
        """Convert all field vars to their typed values."""
        result = {}
        for fid, (var, typ) in self._field_vars.items():
            raw = var.get().strip()
            if not raw:
                raise ValueError(f'Field "{fid}" is empty.')
            if typ == 'float':
                result[fid] = float(raw)
            elif typ == 'int':
                result[fid] = int(float(raw))
            elif typ == 'list':
                result[fid] = [float(x) for x in re.split(r'[\s,]+', raw) if x]
            elif typ == 'expr':
                result[fid] = raw        # raw expression string
            elif typ == 'str':
                result[fid] = raw
            else:
                result[fid] = float(raw)
        return result

    def _parse_word(self):
        if not (self._current_fn and self._current_fn.get('word_fn') and self.word_var_entry):
            return
        sentence = self.word_var_entry.get().strip()
        if not sentence:
            return
        parsed = self._current_fn['word_fn'](sentence)
        if parsed is None:
            self._append_output('Could not parse that sentence.\n', 'error')
            return
        self._append_output(f'✓  Parsed:  {parsed}\n', 'parsed')
        for fid, val in parsed.items():
            if fid in self._field_vars:
                self._field_vars[fid][0].set(str(val))

    def _calculate(self):
        if self._current_fn is None:
            return
        try:
            fv = self._parse_values()
        except ValueError as e:
            self._append_output(f'\n✗  Input error: {e}\n', 'error')
            return

        self._append_sep()
        self._append_output(f'▶  {self._current_fn["name"]}\n', 'label')

        # Show field values used
        for fid, (var, _) in self._field_vars.items():
            self._append_output(f'   {fid} = {var.get()}\n', 'dim')

        # Steps
        if self.step_var.get() and self._current_fn.get('steps_fn'):
            try:
                steps = self._current_fn['steps_fn'](fv)
                self._append_output('\nStep-by-step:\n', 'label')
                for label, formula, value in steps:
                    if formula:
                        self._append_output(f'  {label}:  {formula}\n', 'formula')
                    if value:
                        self._append_output(f'       →  {value}\n', 'step')
            except Exception as e:
                self._append_output(f'  (steps unavailable: {e})\n', 'dim')

        # Result
        try:
            result = self._current_fn['fn'](fv)
            self._append_output(f'\n{result}\n', 'result')
            # ── Feed MathCode art engine ──────────────────────────────────────
            self._feed_art(result, self.section_label.cget('text'),
                           self._current_fn['name'], fv)
        except RuntimeError as e:
            self._append_output(f'\n✗  Error: {e}\n', 'error')
        except Exception as e:
            self._append_output(f'\n✗  Error: {e}\n', 'error')

    def _append_output(self, text, tag=''):
        self.output_text.configure(state='normal')
        if tag:
            self.output_text.insert('end', text, tag)
        else:
            self.output_text.insert('end', text)
        self.output_text.configure(state='disabled')
        self.output_text.see('end')

    def _feed_art(self, result_text: str, domain: str, fn_name: str,
                  inputs: dict = None):
        """
        Parse the first numeric value from result_text and seed the art engine.

        Now passes the full input dict (field values from the calculator UI)
        alongside the result so _extract_math_params can use them to modulate
        composition geometry — focal offset, size bias, angle bias etc.
        Different inputs to the same function produce visually distinct pieces.
        """
        import re as _re
        engine  = getattr(self, '_art_engine', None)
        monitor = getattr(self, '_art_monitor', None)
        if engine is None:
            return
        # Randomize style if the monitor checkbox is on
        if monitor is not None:
            try:
                if monitor._rand_style_var.get():
                    monitor._randomize_profile()
            except Exception:
                pass
        # Extract first number from the result string
        nums = _re.findall(r'-?\d+\.?\d*(?:[eE][+-]?\d+)?', str(result_text))
        if nums:
            try:
                value = float(nums[0])
                engine.feed(value, domain=domain, fn_name=fn_name,
                            inputs=inputs or {})
            except Exception:
                pass

    def _append_sep(self):
        self._append_output('─' * 50 + '\n', 'sep')

    def _clear_output(self):
        self.output_text.configure(state='normal')
        self.output_text.delete('1.0', 'end')
        self.output_text.configure(state='disabled')


# ══════════════════════════════════════════════════════════════════════════════
# NAV PANEL  (left sidebar)
# ══════════════════════════════════════════════════════════════════════════════

class NavPanel(tk.Frame):
    def __init__(self, master, on_select, width=260):
        super().__init__(master, bg=C['panel'], width=width)
        self.pack_propagate(False)
        self.on_select = on_select
        self._items = {}       # item_id → (section_name, fn_spec)
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=C['panel'])
        hdr.pack(fill='x', pady=(0,0))
        tk.Label(hdr, text='  MATHCORE', font=FONTS['title'],
                 fg=C['accent'], bg=C['panel'], anchor='w',
                 pady=12).pack(fill='x')
        tk.Frame(self, height=1, bg=C['border_hi']).pack(fill='x')

        search_frame = tk.Frame(self, bg=C['panel'])
        search_frame.pack(fill='x', padx=8, pady=6)
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self._filter)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                font=FONTS['mono_sm'], bg=C['bg3'], fg=C['text'],
                                insertbackground=C['accent'], relief='flat',
                                highlightthickness=1, highlightcolor=C['accent'],
                                highlightbackground=C['border'])
        search_entry.pack(fill='x', ipady=4)
        tk.Label(search_frame, text='  search functions…', font=FONTS['mono_sm'],
                 fg=C['text_dim'], bg=C['panel']).place(in_=search_entry, x=4, y=4)
        search_entry.bind('<FocusIn>', lambda e: search_entry.delete(0,'end'))

        tk.Frame(self, height=1, bg=C['border']).pack(fill='x')

        # Treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Nav.Treeview',
                         background=C['panel'],
                         foreground=C['text'],
                         fieldbackground=C['panel'],
                         borderwidth=0,
                         font=FONTS['nav'],
                         rowheight=22)
        style.configure('Nav.Treeview.Heading', background=C['panel'],
                         foreground=C['text_dim'], font=FONTS['nav'])
        style.map('Nav.Treeview',
                  background=[('selected', C['nav_sel'])],
                  foreground=[('selected', C['accent'])])

        tree_frame = tk.Frame(self, bg=C['panel'])
        tree_frame.pack(fill='both', expand=True)
        self.tree = ttk.Treeview(tree_frame, style='Nav.Treeview',
                                  show='tree', selectmode='browse')
        tree_scroll = tk.Scrollbar(tree_frame, orient='vertical',
                                   command=self.tree.yview,
                                   bg=C['panel'], troughcolor=C['panel'])
        self.tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side='right', fill='y')
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)
        self.tree.tag_configure('section', foreground=C['accent2'], font=FONTS['nav_sec'])
        self.tree.tag_configure('subsect', foreground=C['accent'],  font=FONTS['nav_sec'])
        self.tree.tag_configure('fn',      foreground=C['text'])
        self.tree.tag_configure('missing', foreground=C['text_dim'])

        self._populate_tree(NAV_TREE)

    def _populate_tree(self, tree_def):
        self.tree.delete(*self.tree.get_children())
        self._items.clear()
        for entry in tree_def:
            name, content = entry
            if isinstance(content, list) and content and isinstance(content[0], tuple):
                # Nested group (e.g., Physics with sub-sections)
                parent = self.tree.insert('', 'end', text=f'  {name}',
                                          tags=('section',), open=False)
                for sub_name, fns in content:
                    if isinstance(fns, list) and fns and isinstance(fns[0], dict):
                        sub = self.tree.insert(parent, 'end', text=f'    {sub_name}',
                                               tags=('subsect',), open=False)
                        for fn_spec in fns:
                            tag = 'fn' if fn_spec.get('fields') is not None else 'missing'
                            iid = self.tree.insert(sub, 'end',
                                                   text=f'      {fn_spec["name"]}',
                                                   tags=(tag,))
                            self._items[iid] = (f'{name} / {sub_name}', fn_spec)
            else:
                # Flat section
                parent = self.tree.insert('', 'end', text=f'  {name}',
                                          tags=('section',), open=False)
                fns = content if isinstance(content, list) else []
                for fn_spec in fns:
                    if not isinstance(fn_spec, dict):
                        continue
                    tag = 'fn' if fn_spec.get('fn') else 'missing'
                    iid = self.tree.insert(parent, 'end',
                                           text=f'    {fn_spec["name"]}',
                                           tags=(tag,))
                    self._items[iid] = (name, fn_spec)

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        if iid in self._items:
            section, fn_spec = self._items[iid]
            self.on_select(section, fn_spec)

    def _filter(self, *args):
        query = self.search_var.get().strip().lower()
        if not query:
            self._populate_tree(NAV_TREE)
            return
        # Rebuild showing only matching functions
        self.tree.delete(*self.tree.get_children())
        self._items.clear()
        for section, fn_spec in self._all_fns():
            if query in fn_spec['name'].lower() or query in section.lower():
                iid = self.tree.insert('', 'end', text=f'  {fn_spec["name"]}',
                                       tags=('fn',))
                self.tree.insert(iid, 'end', text=f'    [{section}]',
                                  tags=('missing',))
                self._items[iid] = (section, fn_spec)

    def _all_fns(self):
        """Yield (section_name, fn_spec) for every leaf function."""
        for entry in NAV_TREE:
            name, content = entry
            if isinstance(content, list) and content and isinstance(content[0], tuple):
                for sub_name, fns in content:
                    if isinstance(fns, list):
                        for fn_spec in fns:
                            if isinstance(fn_spec, dict):
                                yield f'{name} / {sub_name}', fn_spec
            else:
                for fn_spec in (content if isinstance(content, list) else []):
                    if isinstance(fn_spec, dict):
                        yield name, fn_spec


# ══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

class MathCoreApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('MathCore')
        self.geometry('1200x760')
        self.minsize(900, 600)
        self.configure(bg=C['bg'])
        self._set_icon()
        self.step_var = tk.BooleanVar(value=False)
        self.word_var = tk.BooleanVar(value=False)
        # ── MathCode art engine ────────────────────────────────────────────
        self._art_engine  = MathCodeEngine()
        self._art_engine.start()
        self._art_monitor = None   # created lazily after mainloop starts
        self._build()
        # Defer monitor creation so Tk is fully initialised
        self.after(200, self._init_art_monitor)

    def _set_icon(self):
        try:
            icon = tk.PhotoImage(width=32, height=32)
            # Draw a simple neon M
            for x in range(32):
                for y in range(32):
                    icon.put('#080b0f', (x, y))
            for y in range(4, 28):
                icon.put('#00ff9f', (6, y))
                icon.put('#00ff9f', (26, y))
            for d in range(10):
                icon.put('#00ff9f', (6+d, 4+d))
                icon.put('#00ff9f', (26-d, 4+d))
            self.iconphoto(True, icon)
        except Exception:
            pass

    def _build(self):
        # ── Top bar ──────────────────────────────────────────────────────────
        self._topbar = tk.Frame(self, bg=C['bg2'], height=36)
        self._topbar.pack(fill='x', side='top')
        self._topbar.pack_propagate(False)

        tk.Label(self._topbar, text='MathCore', font=('Consolas', 11, 'bold'),
                 fg=C['accent'], bg=C['bg2'], padx=14).pack(side='left', fill='y')
        tk.Frame(self._topbar, width=1, bg=C['border']).pack(side='left', fill='y', pady=6)

        # Mode toggles
        def _make_toggle(parent, text, var, color):
            frame = tk.Frame(parent, bg=C['bg2'])
            frame.pack(side='left', padx=2, fill='y')
            def _toggle():
                var.set(not var.get())
                lbl.configure(fg=color if var.get() else C['text_dim'])
                indicator.configure(bg=color if var.get() else C['border'])
            btn = tk.Button(frame, text=text, font=FONTS['mono_sm'],
                            bg=C['bg2'], fg=C['text_dim'], relief='flat',
                            activebackground=C['bg2'], cursor='hand2',
                            command=_toggle, padx=8)
            btn.pack(side='left', fill='y')
            lbl = btn
            indicator = tk.Frame(frame, width=6, height=6, bg=C['border'])
            indicator.pack(side='left', fill='y', pady=15, padx=2)
            return frame

        _make_toggle(self._topbar, '≡ Steps', self.step_var, C['accent4'])
        _make_toggle(self._topbar, '📝 Word Mode', self.word_var, C['accent3'])

        # Right side: shortcuts
        tk.Button(self._topbar, text='?  Quick Calc', font=FONTS['mono_sm'],
                  bg=C['bg2'], fg=C['accent2'], relief='flat',
                  cursor='hand2', padx=10,
                  command=self._open_calc_free).pack(side='right', fill='y')
        tk.Frame(self._topbar, width=1, bg=C['border']).pack(side='right', fill='y', pady=6)
        tk.Label(self._topbar, text='type ? in any field to open inline',
                 font=FONTS['mono_sm'], fg=C['text_dim'],
                 bg=C['bg2'], padx=10).pack(side='right', fill='y')

        tk.Frame(self, height=1, bg=C['border_hi']).pack(fill='x')

        # ── Main body ─────────────────────────────────────────────────────────
        body = tk.Frame(self, bg=C['bg'])
        body.pack(fill='both', expand=True)

        # Pass engine directly — no deferred injection needed
        self.work_panel = WorkPanel(body, self.step_var, self.word_var,
                                    art_engine=self._art_engine)
        self.work_panel.pack(side='right', fill='both', expand=True)
        tk.Frame(body, width=1, bg=C['border_hi']).pack(side='right', fill='y')
        self.nav = NavPanel(body, self._on_function_select)
        self.nav.pack(side='left', fill='y')

        # ── Status bar ────────────────────────────────────────────────────────
        status = tk.Frame(self, bg=C['bg2'], height=22)
        status.pack(fill='x', side='bottom')
        status.pack_propagate(False)
        modules_ok = sum(1 for m in [Physics_1D, PEnergy, PSprings, PMomentum, PCoM,
                                      BasicMath, Algebra, Geometry, Trig, Calc,
                                      Stat, Comb, LinAlg] if m is not None)
        tk.Label(status, text=f'  {modules_ok} modules loaded  |  type ? in any field for the layered calculator',
                 font=FONTS['mono_sm'], fg=C['text_dim'], bg=C['bg2']).pack(side='left', fill='y')
        tk.Label(status, text='MathCore UI  ',
                 font=FONTS['mono_sm'], fg=C['border'], bg=C['bg2']).pack(side='right', fill='y')

    def _on_function_select(self, section_name, fn_spec):
        self.work_panel.load_function(section_name, fn_spec)

    def _open_calc_free(self):
        dummy = tk.StringVar()
        CalcPopup(self, dummy)

    def _init_art_monitor(self):
        self._art_monitor = ArtMonitor(self, self._art_engine)
        self._art_badge = ArtStatusBadge(
            self._topbar,
            self._art_monitor,
            self._art_engine,
        )
        self._art_badge.pack(side='right', fill='y')

    def _on_function_select(self, section_name, fn_spec):
        self.work_panel.load_function(section_name, fn_spec)


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    app = MathCoreApp()
    app.mainloop()