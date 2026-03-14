# ============================================================
# IMPORTS
# ============================================================

import re
import math
import textwrap

from MathTypes.Basic import BasicMath                      # Basic arithmetic operations
from MathTypes.Physics import Physics_1D                   # 1D kinematics
from MathTypes.Physics import Physics_2D                   # 2D vectors and projectiles
from MathTypes.Physics import Physics_3D                   # 3D vectors and projectiles
import MathTypes.Physics.Forces as Forces                  # Forces, friction, tension, circular motion
import MathTypes.Basic.Algebra as Algebra                  # Algebra functions
import MathTypes.Basic.Geometry as Geometry                # Geometry functions
import MathTypes.Basic.Trigonometry as Trig                # Trigonometry functions
import MathTypes.Advanced.Calculus as Calc                 # Calculus functions
import MathTypes.Advanced.Differential as Diff             # Differentiation functions
import MathTypes.Advanced.Statistics as Stat               # Statistics functions
import MathTypes.Advanced.Probability as Prob              # Probability functions
import MathTypes.Advanced.Combinatorics as Comb            # Combinatorics functions
import MathTypes.Advanced.DiscreteMath as Discrete          # Discrete Mathematics functions
import Config                                              # Validation and RNG
import MathTypes.Advanced.LinearAlgebra as LinAlg          # Linear Algebra functions
import MathTypes.Advanced.Differential as DiffGeo  # Differential Geometry functions
import MathTypes.Advanced.AbstractAlgebra as AbsAlg        # Abstract Algebra functions
import MathTypes.Advanced.Topology as Topo                 # Topology functions
import MathTypes.Advanced.AlgebraicGeometry as AlgGeo      # Algebraic Geometry functions
import MathTypes.Physics.Physics_Energy as PEnergy         # Energy, work, power, IsWork
import MathTypes.Physics.Physics_Springs as PSprings       # Springs, SHM, Hooke's law
import MathTypes.Physics.Physics_Momentum as PMomentum     # Momentum, impulse, center of mass
import MathTypes.Physics.Physics_CenterOfMass as PCoM    # Center of mass, composite bodies, CoM frame


# ============================================================
# ============================================================
# UI HELPERS
# ============================================================

_BAR_WIDTH  = 40   # Inner width of the exit bar box
_TEXT_WIDTH = 72   # Max characters per printed line (before indent)

# ── Abort signal ────────────────────────────────────────────
class _AskAbort(Exception):
    """Raised by _ask() when the user chooses to cancel a calculation."""
    pass

# ── Safe input with retry logic ─────────────────────────────
def _ask(prompt, cast=float, desc=None):
    """
    Ask for a value up to 3 times.
    On 3 failures offers: cancel  or  retry (with a description of what's needed).
    Raises _AskAbort if the user cancels.
    """
    label = desc or prompt
    for attempt in range(3):
        remaining = 2 - attempt
        try:
            raw = input(f'  {prompt}: ').strip()
            if not raw:
                if remaining:
                    print(f'  ✗  This field cannot be empty.  ({remaining} attempt{"s" if remaining != 1 else ""} left)')
                continue
            # ── Ripcord: ? opens the layered calculator ──────────────────────
            if raw == '?':
                result = _layered_calc()
                if result is not None:
                    try:
                        return cast(result)
                    except (ValueError, TypeError):
                        return cast(str(result))
                continue
            return cast(raw)
        except (ValueError, TypeError):
            if remaining:
                print(f'  ✗  That isn\'t a valid value.  ({remaining} attempt{"s" if remaining != 1 else ""} left)')
    # 3 strikes exhausted
    print()
    print('  ─── 3 invalid attempts ───────────────────────────')
    print('  (1)  Cancel this calculation and go back to the menu')
    print('  (2)  Try entering the value again')
    print()
    opt = input('  Choose: ').strip()
    if opt != '2':
        raise _AskAbort()
    print()
    print(f'  This field needs: {label}')
    print()
    while True:
        try:
            raw = input(f'  {prompt}: ').strip()
            if not raw:
                print('  ✗  Cannot be empty. Please try again.')
                continue
            return cast(raw)
        except (ValueError, TypeError):
            print('  ✗  Still not a valid value. Please try again.')

def _ask_int(prompt, desc=None):
    return _ask(prompt, cast=int, desc=desc)

def _ask_str(prompt):
    """Ask for a non-empty string. Same 3-retry logic."""
    for attempt in range(3):
        remaining = 2 - attempt
        raw = input(f'  {prompt}: ').strip()
        if raw:
            return raw
        if remaining:
            print(f'  ✗  This cannot be empty.  ({remaining} attempt{"s" if remaining != 1 else ""} left)')
    print()
    print('  ─── 3 invalid attempts ───────────────────────────')
    print('  (1)  Cancel this calculation and go back to the menu')
    print('  (2)  Try entering the value again')
    print()
    opt = input('  Choose: ').strip()
    if opt != '2':
        raise _AskAbort()
    while True:
        raw = input(f'  {prompt}: ').strip()
        if raw:
            return raw
        print('  ✗  Cannot be empty. Please try again.')

def _ask_list(prompt='  Enter numbers separated by spaces or commas', cast=float, min_count=1):
    """
    Ask the user for a list of numbers on one line.
    Re-prompts on bad input using the same retry logic.
    """
    for attempt in range(3):
        remaining = 2 - attempt
        raw = input(f'{prompt}: ').strip()
        if not raw:
            if remaining:
                print(f'  ✗  Please enter at least {min_count} value(s).  ({remaining} left)')
            continue
        try:
            parts = re.split(r'[\s,]+', raw)
            values = [cast(p) for p in parts if p]
            if len(values) < min_count:
                if remaining:
                    print(f'  ✗  Need at least {min_count} value(s), got {len(values)}.  ({remaining} left)')
                continue
            return values
        except (ValueError, TypeError):
            if remaining:
                print(f'  ✗  One or more values were not valid numbers.  ({remaining} left)')
    print()
    print('  ─── 3 invalid attempts ───────────────────────────')
    print('  (1)  Cancel and go back')
    print('  (2)  Try again')
    print()
    opt = input('  Choose: ').strip()
    if opt != '2':
        raise _AskAbort()
    while True:
        raw = input(f'{prompt}: ').strip()
        if not raw:
            print(f'  ✗  Please enter at least {min_count} value(s).')
            continue
        try:
            parts = re.split(r'[\s,]+', raw)
            values = [cast(p) for p in parts if p]
            if len(values) < min_count:
                print(f'  ✗  Need at least {min_count} value(s). Got {len(values)}.')
                continue
            return values
        except (ValueError, TypeError):
            print('  ✗  Some values were not valid. Please re-enter.')

# ── Text wrapper ─────────────────────────────────────────────
def _p(text, indent=2):
    """
    Print text wrapped to _TEXT_WIDTH columns with a consistent left indent.
    Handles multi-sentence strings gracefully — no weird mid-word line breaks.
    """
    prefix = ' ' * indent
    for line in textwrap.wrap(text, width=_TEXT_WIDTH, initial_indent=prefix, subsequent_indent=prefix):
        print(line)

# ── Safe section/choice entry (wraps int cast + 0-exit) ─────
def _menu_int(prompt='  Select: '):
    """Read an integer menu choice. Returns -1 on blank/bad input (triggers invalid-option message)."""
    try:
        raw = input(prompt).strip()
        if not raw:
            return -1
        return int(raw)
    except (ValueError, TypeError):
        return -1

def _ExitBar(label='Go back'):
    """Prints a visually distinct (0) prompt that is never confused with numbered choices."""
    inner = f"  (0)  {label}"
    print(f"  ╔{"═" * _BAR_WIDTH}╗")
    print(f"  ║{inner:<{_BAR_WIDTH}}║")
    print(f"  ╚{"═" * _BAR_WIDTH}╝")

def _SectionHeader(title, subtitle=''):
    """Prints a consistent section header box."""
    print()
    print(f"  ╔══════════════════════════════════════════╗")
    print(f"  ║  {title:<40}║")
    if subtitle:
        print(f"  ║  {subtitle:<40}║")
    print(f"  ╚══════════════════════════════════════════╝")
    print()

# ============================================================
# FEATURE TOGGLES  (word problem mode, step display, layered calc)
# ============================================================

_STEP_MODE = False   # When True, all calculations print a step-by-step breakdown
_WORD_MODE = False   # When True, functions offer a word-problem parser entry point

# ── Step-by-step display ─────────────────────────────────────────────────────
def _step(label, formula, substitution, result, unit=''):
    """
    Print a single calculation step in a formatted box.
    Called when _STEP_MODE is True.
      label        — short name of this step (e.g. 'Kinetic Energy')
      formula      — the symbolic formula (e.g. 'KE = ½mv²')
      substitution — values plugged in (e.g. '½ × 2.0 × 3.0²')
      result       — numeric result (e.g. 9.0)
      unit         — physical unit string (e.g. 'J')
    """
    if not _STEP_MODE:
        return
    W = 52
    print(f'  ┌─ {label} {"─"*(W - len(label) - 4)}┐')
    if formula:
        print(f'  │  {formula:<{W-2}}│')
    if substitution:
        print(f'  │  = {substitution:<{W-4}}│')
    res_str = f'{result:.6f} {unit}'.strip() if isinstance(result, float) else str(result)
    print(f'  │  → {res_str:<{W-5}}│')
    print(f'  └{"─"*W}┘')

def _step_result(label, result, unit=''):
    """Short single-line step display — just label and result."""
    _step(label, '', '', result, unit)

def _show_steps(steps):
    """
    Render a list of (label, formula, result) tuples from a StepByStep* function.
    Only does anything when _STEP_MODE is True.
    """
    if not _STEP_MODE:
        return
    W = 52
    print()
    print(f'  ┌─ Step-by-step solution {"─"*(W-24)}┐')
    for label, formula, result in steps:
        if result:
            print(f'  │  {label:<16}  {formula:<20}  = {result:<8}│'.ljust(W+4) + '│' if len(f'  │  {label:<16}  {formula:<20}  = {result}') < W+3 else f'  │  {label}: {formula} = {result}')
        else:
            print(f'  │  {label:<{W-2}}│')
    print(f'  └{"─"*W}┘')
    print()

# ── Layered calculation ripcord ──────────────────────────────────────────────
_CALC_HISTORY = []   # stores results from sub-calculations, most recent last

def _layered_calc():
    """
    Opens a mini inline calculator when the user types ? during _ask().
    Supports: arithmetic, common physics formulas, and previous results.
    Returns the numeric result, or None if the user cancels.
    """
    print()
    print('  ╔══════════════════════════════════════════╗')
    print('  ║  ⊕  Quick Calculator  (ripcord)          ║')
    print('  ║  Result will be returned as your value.  ║')
    print('  ╚══════════════════════════════════════════╝')
    print()
    print('  (1)  Arithmetic expression  (type any math)')
    print('  (2)  Previous results')
    print('  (3)  ½ m v²  (kinetic energy)')
    print('  (4)  m g h   (gravitational PE)')
    print('  (5)  F · d · cos θ  (work)')
    print('  (6)  √ of a number')
    print('  (7)  a² + b²  →  c  (Pythagorean)')
    print('  (8)  Unit conversion  (m↔cm↔mm, kg↔g, J↔kJ)')
    print()
    print('  (0)  Cancel — return to original prompt')
    print()
    try:
        choice = _menu_int('  Choose: ')
    except Exception:
        return None
    if choice == 0:
        return None
    try:
        if choice == 1:
            raw = input('  Expression (use Python syntax, e.g. 3**2 + 4**2): ').strip()
            result = float(eval(raw, {'__builtins__': {}}, {
                'sqrt': math.sqrt, 'pi': math.pi, 'sin': math.sin,
                'cos': math.cos, 'tan': math.tan, 'log': math.log,
                'exp': math.exp, 'abs': abs, 'round': round,
            }))
        elif choice == 2:
            if not _CALC_HISTORY:
                print('  No previous results yet.')
                return None
            print()
            for i, (label, val) in enumerate(_CALC_HISTORY[-5:], 1):
                print(f'    ({i})  {label}  =  {val}')
            print()
            idx = _menu_int('  Pick result (or 0 to cancel): ')
            if idx == 0 or idx < 1 or idx > min(5, len(_CALC_HISTORY)):
                return None
            _, result = _CALC_HISTORY[-5:][idx - 1]
        elif choice == 3:
            m = float(input('  m (kg): '))
            v = float(input('  v (m/s): '))
            result = 0.5 * m * v**2
            print(f'  KE = ½ × {m} × {v}² = {result:.6f} J')
        elif choice == 4:
            m = float(input('  m (kg): ')); g = float(input('  g (m/s², Enter=9.8): ') or '9.8')
            h = float(input('  h (m): '))
            result = m * float(g) * h
            print(f'  GPE = {m} × {g} × {h} = {result:.6f} J')
        elif choice == 5:
            F = float(input('  F (N): ')); d = float(input('  d (m): '))
            th = float(input('  θ (deg, 0 if parallel): ') or '0')
            result = F * d * math.cos(math.radians(float(th)))
            print(f'  W = {F} × {d} × cos({th}°) = {result:.6f} J')
        elif choice == 6:
            x = float(input('  Number: '))
            result = math.sqrt(x)
            print(f'  √{x} = {result:.6f}')
        elif choice == 7:
            a = float(input('  a: ')); b = float(input('  b: '))
            result = math.sqrt(a**2 + b**2)
            print(f'  c = √({a}² + {b}²) = {result:.6f}')
        elif choice == 8:
            print('  (1) m→cm  (2) cm→m  (3) kg→g  (4) g→kg  (5) J→kJ  (6) kJ→J')
            conv = _menu_int('  Choose: ')
            val  = float(input('  Value: '))
            table = {1:(val*100,'cm'), 2:(val/100,'m'), 3:(val*1000,'g'),
                     4:(val/1000,'kg'), 5:(val/1000,'kJ'), 6:(val*1000,'J')}
            result, unit = table.get(conv, (val,'?'))
            print(f'  = {result} {unit}')
        else:
            return None
        _CALC_HISTORY.append((f'calc {len(_CALC_HISTORY)+1}', result))
        print(f'\n  ✓  Using  {result:.6f}  as your value.')
        print()
        return result
    except Exception as e:
        print(f'  ✗  Calculator error: {e}')
        return None

# ── Word problem mode toggle ─────────────────────────────────────────────────
def _toggle_step_mode():
    """Toggle the global step-by-step display on/off."""
    global _STEP_MODE
    _STEP_MODE = not _STEP_MODE
    print(f'\n  Step-by-step display: {"ON ✓" if _STEP_MODE else "OFF"}')

def _toggle_word_mode():
    """Toggle the global word-problem parsing mode on/off."""
    global _WORD_MODE
    _WORD_MODE = not _WORD_MODE
    print(f'\n  Word-problem mode: {"ON ✓" if _WORD_MODE else "OFF"}')

# ============================================================
# COLLECT VARIABLES
# ============================================================

def CollectVariables():
    """
    Collects an unlimited list of numbers from the user.
    Used by add / sub / mul / div.
    Enter (0) at the action menu to cancel and return to function selection.
    Raises _AskAbort on cancel so the caller's except block handles it.
    """
    variables = []
    while True:
        print()
        if variables:
            print('  Variables so far:')
            for i, v in enumerate(variables):
                print(f"    {i + 1}.  {v}")
        else:
            print('  Variables so far: none yet')
        print()
        print('  (1)  Add a variable')
        print('  (2)  Remove a variable')
        print('  (3)  Confirm and calculate')
        print()
        _ExitBar('Cancel and return to function list')
        print()
        action = _menu_int('  Enter a number to choose: ')
        if action == 0:
            raise _AskAbort()                                  # User chose to cancel
        match action:
            case 1:
                val = _ask('  Enter a value: ', cast=float)
                variables.append(val)
                print(f"  Added {val}. You now have {len(variables)} variable(s).")
            case 2:
                if not variables:
                    print()
                    print('  There are no variables to remove yet.')
                else:
                    print()
                    print('  Which variable would you like to remove?')
                    print()
                    for i, v in enumerate(variables):
                        print(f"    {i + 1}.  {v}")
                    print()
                    pick = _ask('  Enter the number of the variable to remove: ', cast=int)
                    if pick < 1 or pick > len(variables):
                        print()
                        print(f"  Please enter a number between 1 and {len(variables)}.")
                    else:
                        selected = variables[pick - 1]
                        print()
                        print(f"  You selected: {selected}")
                        print()
                        print('  (1)  Yes — remove it')
                        print('  (2)  No — go back')
                        print()
                        confirm = _menu_int('  Enter a number to choose: ')
                        if confirm == 1:
                            variables.pop(pick - 1)
                            print(f"  Removed {selected}. You now have {len(variables)} variable(s).")
                        else:
                            print('  Cancelled. Nothing was removed.')
            case 3:
                if len(variables) < 2:
                    print()
                    print('  You need at least 2 variables to calculate. Please add more.')
                else:
                    return variables
            case _:
                print()
                print('  That was not a valid option. Try again.')

# ============================================================
# MAIN DEBUG ENTRY POINT
# ============================================================

def Debug():
    """Main debug menu. Loops until the user exits."""
    while True:
        _SectionHeader('MathCore Debug', 'Choose a math type to test')
        print('  (1)   Basic Math')
        print('  (2)   Physics')
        print('  (3)   Algebra')
        print('  (4)   Geometry')
        print('  (5)   Trigonometry')
        print('  (6)   Calculus')
        print('  (7)   Differentiation')
        print('  (8)   Statistics')
        print('  (9)   Probability')
        print('  (10)  Combinatorics')
        print('  (11)  Discrete Mathematics')
        print('  (12)  Linear Algebra')
        print('  (13)  Differential Geometry')
        print('  (14)  Abstract Algebra')
        print('  (15)  Topology')
        print('  (16)  Algebraic Geometry')
        print('  (17)  Physics — Energy & Work')
        print('  (18)  Physics — Springs & SHM')
        print('  (19)  Physics — Momentum & Impulse')
        print('  (20)  Physics — Center of Mass')
        print()
        print('  (S)  Toggle step-by-step display  ', end='')
        print(f'[{"ON ✓" if _STEP_MODE else "off"}]')
        print('  (W)  Toggle word-problem mode      ', end='')
        print(f'[{"ON ✓" if _WORD_MODE else "off"}]')
        print()
        _ExitBar('Exit MathCore Debug')
        print()
        raw_choice = input('  Choose a math type: ').strip()
        if raw_choice.upper() == 'S': _toggle_step_mode(); continue
        if raw_choice.upper() == 'W': _toggle_word_mode(); continue
        try:
            MathType = int(raw_choice) if raw_choice else -1
        except ValueError:
            MathType = -1
        if MathType == 0:
            print()
            print('  Exiting MathCore Debug.')
            print()
            return
        match MathType:
            case 1:  BasicMathDebug()
            case 2:  PhysicsDebug()
            case 3:  AlgebraDebug()
            case 4:  GeometryDebug()
            case 5:  TrigonometryDebug()
            case 6:  CalculusDebug()
            case 7:  DifferentiationDebug()
            case 8:  StatisticsDebug()
            case 9:  ProbabilityDebug()
            case 10: CombinatoricsDebug()
            case 11: DiscreteMathDebug()
            case 12: LinearAlgebraDebug()
            case 13: DifferentialGeometryDebug()
            case 14: AbstractAlgebraDebug()
            case 15: TopologyDebug()
            case 16: AlgebraicGeometryDebug()
            case 17: PhysicsEnergyDebug()
            case 18: PhysicsSpringsDebug()
            case 19: PhysicsMomentumDebug()
            case 20: CenterOfMassDebug()
            case _:  print('\n  That was not a valid option. Please try again.')

# ============================================================
# BASIC MATH DEBUG
# ============================================================

def BasicMathDebug():
    SECTIONS = [
        'Arithmetic',
        'Number Tools',
    ]
    while True:
        _SectionHeader('Basic Math', 'Choose a section')
        for i, s in enumerate(SECTIONS, 1):
            print(f"  ({i})  {s}")
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section.')
            continue
        while True:
            _SectionHeader('Basic Math', SECTIONS[sec - 1])
            if sec == 1:
                print('  (1)  Add numbers together')
                print('  (2)  Subtract numbers in sequence')
                print('  (3)  Multiply numbers together')
                print('  (4)  Divide numbers in sequence')
            elif sec == 2:
                print('  (1)  Check if a number is even')
                print('  (2)  Get the remainder  (modulo)')
                print('  (3)  Generate a random integer')
            print()
            _ExitBar('Return to sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            if choice < 0:
                print('\n  That was not a valid option.')
                continue
            result = None
            try:
                if sec == 1:
                    match choice:
                        case 1:
                            print()
                            print('  Add — enter as many numbers as you want.')
                            variables = CollectVariables()
                            result = variables[0]
                            for v in variables[1:]:
                                result = BasicMath.add(result, v)
                            print(f"\n  Adding: {' + '.join(str(v) for v in variables)}")
                        case 2:
                            # ── Subtraction with negative-result handling ──────────────────
                            print()
                            print('  Subtract — each value is subtracted from the previous.')
                            print()
                            print('  Allow negative results?')
                            print('  (1)  Yes — allow negatives')
                            print('  (2)  No  — auto-adjust order to stay positive')
                            print()
                            allow_neg = _menu_int('  Choose: ') != 2   # default allow
                            while True:
                                variables = CollectVariables()
                                # Try subtraction in given order
                                result = variables[0]
                                for v in variables[1:]:
                                    result = BasicMath.sub(result, v)
                                expr = ' - '.join(str(v) for v in variables)
                                if result >= 0 or allow_neg:
                                    print(f"\n  Subtracting: {expr}")
                                    break
                                # Result is negative — try sorting descending to keep positive
                                sorted_vars = sorted(variables, reverse=True)
                                sorted_result = sorted_vars[0]
                                for v in sorted_vars[1:]:
                                    sorted_result = BasicMath.sub(sorted_result, v)
                                sorted_expr = ' - '.join(str(v) for v in sorted_vars)
                                if sorted_result >= 0:
                                    print()
                                    print(f"  ℹ  Original order gave a negative result ({result}).")
                                    print(f"  ℹ  Re-ordered to keep the result positive: {sorted_expr} = {sorted_result}")
                                    result = sorted_result
                                    expr   = sorted_expr
                                    variables = sorted_vars
                                    break
                                else:
                                    # Still negative after reorder
                                    print()
                                    print(f"  ✗  The result is still negative ({sorted_result}) even after reordering.")
                                    print()
                                    print('  Would you like to:')
                                    print('  (1)  Allow the negative result')
                                    print('  (2)  Re-enter the numbers')
                                    print()
                                    retry = _menu_int('  Choose: ')
                                    if retry == 1:
                                        allow_neg = True        # Accept it this time
                                        result = sorted_result if sorted_result < result else result
                                        result = variables[0]
                                        for v in variables[1:]:
                                            result = BasicMath.sub(result, v)
                                        break
                                    else:
                                        print()
                                        print('  Starting over — please re-enter your numbers.')
                                        # loop back to CollectVariables
                            print(f"\n  Subtracting: {expr}")
                        case 3:
                            print()
                            print('  Multiply — enter as many numbers as you want.')
                            variables = CollectVariables()
                            result = variables[0]
                            for v in variables[1:]:
                                result = BasicMath.multi(result, v)
                            print(f"\n  Multiplying: {' × '.join(str(v) for v in variables)}")
                        case 4:
                            print()
                            print('  Divide — each divides the previous result.')
                            variables = CollectVariables()
                            result = variables[0]
                            for v in variables[1:]:
                                result = BasicMath.div(result, v)
                            print(f"\n  Dividing: {' ÷ '.join(str(v) for v in variables)}")
                        case _:
                            print('\n  That was not a valid option.')
                            continue
                elif sec == 2:
                    match choice:
                        case 1:
                            result = Config.Checks.IsEven(_ask('  Enter a number to check: ', cast=int))
                        case 2:
                            a = _ask('  First number: ', cast=int)
                            b = _ask('  Divide by (get remainder): ', cast=int)
                            result = BasicMath.mod(a, b)
                        case 3:
                            lo = _ask('  Minimum value: ', cast=int)
                            hi = _ask('  Maximum value: ', cast=int)
                            result = Config.RNG.rand(lo, hi)
                        case _:
                            print('\n  That was not a valid option.')
                            continue
            except _AskAbort:
                print()
                _p('Calculation cancelled. Returning to the function list.')
                print()
                continue
            except (ValueError, TypeError, ZeroDivisionError) as e:
                print(f'\n  Error: {e}  Please try again.')
                print()
                continue
            if result is not None:
                print()
                print(f"  Result: {result}")
                print()

# ============================================================
# PHYSICS 1D DEBUG
# ============================================================

# ============================================================
# PHYSICS DEBUG  (wrapper — routes to 1D / 2D / 3D / Forces)
# ============================================================

def PhysicsDebug():
    while True:
        _SectionHeader('Physics', 'Choose a category')
        print('  (1)  Kinematics')
        print('  (2)  Forces')
        print()
        _ExitBar('Return to main menu')
        print()
        choice = _menu_int('  Choose: ')
        if choice == 0: return
        match choice:
            case 1: KinematicsDebug()
            case 2: ForcesDebug()
            case _: print('\n  That was not a valid option. Please try again.')

# ────────────────────────────────────────────────────────────
# KINEMATICS — dimensional sub-router
# ────────────────────────────────────────────────────────────

def KinematicsDebug():
    while True:
        _SectionHeader('Kinematics', 'Choose a dimension')
        print('  (1)  1D  — motion along a straight line')
        print('  (2)  2D  — planar motion, projectile, forces')
        print('  (3)  3D  — three-dimensional motion')
        print()
        _ExitBar('Return to Physics menu')
        print()
        choice = _menu_int('  Choose: ')
        if choice == 0: return
        match choice:
            case 1: Physics1DDebug()
            case 2: Physics2DDebug()
            case 3: Physics3DDebug()
            case _: print('\n  That was not a valid option. Please try again.')

# ────────────────────────────────────────────────────────────
# FORCES — dimensional sub-router
# ────────────────────────────────────────────────────────────

def ForcesDebug():
    while True:
        _SectionHeader('Forces', 'Choose a dimension')
        print('  (1)  2D  — forces in a plane')
        print('  (2)  3D  — forces in three-dimensional space')
        print()
        _ExitBar('Return to Physics menu')
        print()
        choice = _menu_int('  Choose: ')
        if choice == 0: return
        match choice:
            case 1: Forces2DDebug()
            case 2: Forces3DDebug()
            case _: print('\n  That was not a valid option. Please try again.')

# ============================================================
# PHYSICS 1D DEBUG
# ============================================================

def Physics1DDebug():
    SECTIONS = [
        'Core Kinematics',
        'Inverse Solvers',
        'Temporal Velocity Solvers',
        'Deceleration Solvers',
        'Free Fall Inverse Solvers',
    ]
    while True:
        _SectionHeader('Physics 1D', 'Motion along a straight line')
        for i, s in enumerate(SECTIONS, 1):
            print(f"  ({i})  {s}")
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section.')
            continue
        while True:
            _SectionHeader('Physics 1D', SECTIONS[sec - 1])
            if sec == 1:
                print('  (1)  Distance between two points')
                print('  (2)  Elapsed time between two moments')
                print('  (3)  Velocity from distance and time')
                print('  (4)  Final velocity  v = v₀ + at')
                print('  (5)  Acceleration from two velocities')
                print('  (6)  Instantaneous acceleration')
                print('  (7)  Constant acceleration')
                print('  (8)  Displacement  Δx = v₀t + ½at²')
                print('  (9)  Position  x = x₀ + v₀t + ½at²')
            elif sec == 2:
                print('  (1)  Time to travel a distance at constant speed')
                print('  (2)  Distance traveled at constant speed over time')
                print('  (3)  New speed after adding a velocity difference')
                print('  (4)  Time through a distance when speed beats a baseline')
            elif sec == 3:
                print('  (1)  Velocity AFTER a known instant')
                print('  (2)  Velocity BEFORE a known instant')
                print('  (3)  Time elapsed between two known velocities')
                print('  (4)  Velocity at any target time given a reference')
                print('  (5)  Position BEFORE a known instant')
            elif sec == 4:
                print('  (1)  Time to stop from an initial speed')
                print('  (2)  Distance traveled while stopping')
                print('  (3)  Velocity at a moment during braking')
                print('  (4)  Position at a moment during braking')
            elif sec == 5:
                print('  (1)  Height fallen from — given impact velocity')
                print('  (2)  Time falling — given impact velocity')
                print('  (3)  Impact velocity — given fall height')
                print('  (4)  Time to reach ground — given fall height')
                print('  (5)  Maximum height — given launch speed upward')
                print('  (6)  Time to reach peak — given launch speed upward')
            print()
            _ExitBar('Return to sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            result = None
            try:
                if sec == 1:
                    match choice:
                        case 1:
                            result = Physics_1D.GetDistance(
                                _ask('  Starting position (m): ', cast=float),
                                _ask('  Ending position (m): ', cast=float)
                            )
                        case 2:
                            result = Physics_1D.GetTime(
                                _ask('  Start time (s): ', cast=float),
                                _ask('  End time (s): ', cast=float)
                            )
                        case 3:
                            result = Physics_1D.Velocity(
                                _ask('  Distance traveled (m): ', cast=float),
                                _ask('  Time taken (s): ', cast=float)
                            )
                        case 4:
                            result = Physics_1D.FinalVelocity(
                                _ask('  Acceleration (m/s²): ', cast=float),
                                _ask('  Distance (m): ', cast=float),
                                _ask('  Time (s): ', cast=float),
                                _ask('  Starting velocity (m/s): ', cast=float)
                            )
                        case 5:
                            result = Physics_1D.Acceleration(
                                _ask('  Starting velocity (m/s): ', cast=float),
                                _ask('  Ending velocity (m/s): ', cast=float),
                                _ask('  Time (s): ', cast=float)
                            )
                        case 6:
                            result = Physics_1D.InstantAcceleration(
                                _ask('  Starting velocity (m/s): ', cast=float),
                                _ask('  Ending velocity (m/s): ', cast=float),
                                _ask('  Time interval (s) — use a very small value for instantaneous: ', cast=float)
                            )
                        case 7:
                            result = Physics_1D.ConstantAcceleration(
                                _ask('  Starting velocity (m/s): ', cast=float),
                                _ask('  Ending velocity (m/s): ', cast=float),
                                _ask('  Time (s): ', cast=float)
                            )
                        case 8:
                            result = Physics_1D.GetDisplacement(
                                _ask('  Acceleration (m/s²): ', cast=float),
                                _ask('  Time (s): ', cast=float),
                                _ask('  Starting velocity (m/s — enter 0 if starting from rest): ', cast=float)
                            )
                        case 9:
                            result = Physics_1D.GetPosition(
                                _ask('  Acceleration (m/s²): ', cast=float),
                                _ask('  Time (s): ', cast=float),
                                _ask('  Starting velocity (m/s — enter 0 if starting from rest): ', cast=float),
                                _ask('  Starting position (m — enter 0 if at the origin): ', cast=float)
                            )
                        case _:
                            print('\n  That was not a valid option.')
                            continue
                elif sec == 2:
                    match choice:
                        case 1:
                            result = Physics_1D.SolveForTime(
                                _ask('  Distance to travel (m): ', cast=float),
                                _ask('  Constant speed (m/s): ', cast=float)
                            )
                            print(f"\n  Time to travel that distance: {result:.4f} s")
                            print()
                            continue
                        case 2:
                            result = Physics_1D.SolveForDistance(
                                _ask('  Speed (m/s): ', cast=float),
                                _ask('  Time (s): ', cast=float)
                            )
                            print(f"\n  Distance traveled: {result:.4f} m")
                            print()
                            continue
                        case 3:
                            v_base  = _ask('  Base speed (m/s): ', cast=float)
                            delta_v = _ask('  Speed difference (m/s — negative to go slower): ', cast=float)
                            result  = Physics_1D.SpeedWithDelta(v_base, delta_v)
                            print(f"\n  New speed: {result:.4f} m/s")
                            print()
                            continue
                        case 4:
                            distance = _ask('  Distance of the course (m): ', cast=float)
                            v_base   = _ask('  Baseline speed to beat (m/s): ', cast=float)
                            delta_v  = _ask('  Amount faster than the baseline (m/s): ', cast=float)
                            result   = Physics_1D.TimeWithSpeedDelta(distance, v_base, delta_v)
                            print(f"\n  New speed: {Physics_1D.SpeedWithDelta(v_base, delta_v):.4f} m/s")
                            print(f"  Time through the course: {result:.4f} s")
                            print()
                            continue
                        case _:
                            print('\n  That was not a valid option.')
                            continue
                elif sec == 3:
                    match choice:
                        case 1:
                            v_now = _ask('  Current velocity (m/s): ', cast=float)
                            a     = _ask('  Constant acceleration (m/s²): ', cast=float)
                            dt    = _ask('  How many seconds AFTER this moment: ', cast=float)
                            result = Physics_1D.VelocityAfter(v_now, a, dt)
                            print(f"\n  Velocity {dt} s later: {result:.4f} m/s")
                            print()
                            continue
                        case 2:
                            v_now = _ask('  Current velocity (m/s): ', cast=float)
                            a     = _ask('  Constant acceleration (m/s²): ', cast=float)
                            dt    = _ask('  How many seconds BEFORE this moment: ', cast=float)
                            result = Physics_1D.VelocityBefore(v_now, a, dt)
                            print(f"\n  Velocity {dt} s earlier: {result:.4f} m/s")
                            print()
                            continue
                        case 3:
                            v_initial = _ask('  Earlier velocity (m/s): ', cast=float)
                            v_final   = _ask('  Later velocity (m/s): ', cast=float)
                            a         = _ask('  Constant acceleration (m/s²): ', cast=float)
                            result    = Physics_1D.TimeBetweenVelocities(v_initial, v_final, a)
                            print(f"\n  Time between those velocities: {result:.4f} s")
                            print()
                            continue
                        case 4:
                            v_ref    = _ask('  Known velocity at reference time (m/s): ', cast=float)
                            t_ref    = _ask('  Reference time (s): ', cast=float)
                            a        = _ask('  Constant acceleration (m/s²): ', cast=float)
                            t_target = _ask('  Target time to find velocity at (s): ', cast=float)
                            result   = Physics_1D.VelocityAtTime(v_ref, t_ref, a, t_target)
                            direction = 'earlier' if t_target < t_ref else 'later'
                            print(f"\n  Velocity at t = {t_target} s ({direction}): {result:.4f} m/s")
                            print()
                            continue
                        case 5:
                            x_now = _ask('  Current position (m — 0 for relative): ', cast=float)
                            v_now = _ask('  Current velocity (m/s): ', cast=float)
                            a     = _ask('  Constant acceleration (m/s²): ', cast=float)
                            dt    = _ask('  How many seconds BEFORE this moment: ', cast=float)
                            result = Physics_1D.PositionBefore(x_now, v_now, a, dt)
                            print(f"\n  Position {dt} s earlier: {result:.4f} m")
                            print()
                            continue
                        case _:
                            print('\n  That was not a valid option.')
                            continue
                elif sec == 4:
                    match choice:
                        case 1:
                            v0    = _ask('  Initial speed (m/s): ', cast=float)
                            decel = _ask('  Deceleration magnitude (m/s² — positive): ', cast=float)
                            result = Physics_1D.StoppingTime(v0, decel)
                            print(f"\n  Time to stop: {result:.4f} s")
                            print()
                            continue
                        case 2:
                            v0    = _ask('  Initial speed (m/s): ', cast=float)
                            decel = _ask('  Deceleration magnitude (m/s² — positive): ', cast=float)
                            result = Physics_1D.StoppingDistance(v0, decel)
                            print(f"\n  Distance traveled while stopping: {result:.4f} m")
                            print()
                            continue
                        case 3:
                            v0    = _ask('  Initial speed at start of braking (m/s): ', cast=float)
                            decel = _ask('  Deceleration magnitude (m/s² — positive): ', cast=float)
                            t     = _ask('  Time after braking began (s): ', cast=float)
                            result = Physics_1D.VelocityWhileStopping(v0, decel, t)
                            print(f"\n  Velocity at t = {t} s during braking: {result:.4f} m/s")
                            if result == 0:
                                print('  (Object has already stopped by this time)')
                            print()
                            continue
                        case 4:
                            v0    = _ask('  Initial speed at start of braking (m/s): ', cast=float)
                            decel = _ask('  Deceleration magnitude (m/s² — positive): ', cast=float)
                            t     = _ask('  Time after braking began (s): ', cast=float)
                            result = Physics_1D.PositionWhileStopping(v0, decel, t)
                            t_stop = Physics_1D.StoppingTime(v0, decel)
                            print(f"\n  Position at t = {t} s during braking: {result:.4f} m from braking start")
                            if t >= t_stop:
                                print(f"  (Object stopped at t = {t_stop:.4f} s)")
                            print()
                            continue
                        case _:
                            print('\n  That was not a valid option.')
                            continue
                elif sec == 5:
                    match choice:
                        case 1:
                            v_final = _ask('  Impact velocity (m/s): ', cast=float)
                            g       = _ask('  Gravity (m/s², Enter = 9.8): ', cast=float, default='9.8')
                            v0      = _ask('  Initial vertical velocity (0 if dropped): ', cast=float, default='0')
                            result  = Physics_1D.HeightFromFinalVelocity(v_final, float(g), float(v0))
                            print(f"\n  Height fallen from: {result:.4f} m")
                            print()
                            continue
                        case 2:
                            v_final = _ask('  Impact velocity (m/s): ', cast=float)
                            g       = _ask('  Gravity (m/s², Enter = 9.8): ', cast=float, default='9.8')
                            v0      = _ask('  Initial vertical velocity (0 if dropped): ', cast=float, default='0')
                            result  = Physics_1D.FreeFallTime(v_final, float(g), float(v0))
                            print(f"\n  Time spent falling: {result:.4f} s")
                            print()
                            continue
                        case 3:
                            h  = _ask('  Height of the fall (m): ', cast=float)
                            g  = _ask('  Gravity (m/s², Enter = 9.8): ', cast=float, default='9.8')
                            v0 = _ask('  Initial vertical velocity (0 if dropped): ', cast=float, default='0')
                            result = Physics_1D.ImpactVelocity(h, float(g), float(v0))
                            print(f"\n  Impact velocity: {result:.4f} m/s")
                            print()
                            continue
                        case 4:
                            h  = _ask('  Height of the fall (m): ', cast=float)
                            g  = _ask('  Gravity (m/s², Enter = 9.8): ', cast=float, default='9.8')
                            v0 = _ask('  Initial downward velocity (0 if dropped from rest): ', cast=float, default='0')
                            result = Physics_1D.FreeFallTimeFromHeight(h, float(g), float(v0))
                            print(f"\n  Time to reach the ground: {result:.4f} s")
                            print()
                            continue
                        case 5:
                            v0 = _ask('  Initial upward launch speed (m/s): ', cast=float)
                            g  = _ask('  Gravity (m/s², Enter = 9.8): ', cast=float, default='9.8')
                            result = Physics_1D.MaxHeightFromLaunch(v0, float(g))
                            print(f"\n  Maximum height reached: {result:.4f} m")
                            print()
                            continue
                        case 6:
                            v0 = _ask('  Initial upward launch speed (m/s): ', cast=float)
                            g  = _ask('  Gravity (m/s², Enter = 9.8): ', cast=float, default='9.8')
                            result = Physics_1D.TimeToMaxHeight(v0, float(g))
                            print(f"\n  Time to reach peak: {result:.4f} s")
                            print()
                            continue
                        case _:
                            print('\n  That was not a valid option.')
                            continue
            except _AskAbort:
                print()
                _p('Calculation cancelled. Returning to the function list.')
                print()
                continue
            except (ValueError, TypeError) as e:
                print(f'\n  Invalid input: {e}  Please try again.')
                print()
                continue
            if result is not None:
                print()
                print(f"  Result: {result:.6f}")
                print()

# ============================================================

# ============================================================
# VECTOR STORE HELPERS  (shared by Physics2D and Physics3D)
# ============================================================

def _fmt2d(label, x, y):
    mag   = math.sqrt(x**2 + y**2)
    angle = math.degrees(math.atan2(y, x)) % 360
    return f"    {label:<4}=  {x:.3f}i  +  {y:.3f}j    (|{label}| = {mag:.3f},  θ = {angle:.1f}°)"

def _fmt3d(label, x, y, z):
    mag = math.sqrt(x**2 + y**2 + z**2)
    return f"    {label:<4}=  {x:.3f}i  +  {y:.3f}j  +  {z:.3f}k    (|{label}| = {mag:.3f})"

def _ShowVectors2D(stored):
    if not stored:
        print('  No vectors stored yet.')
    else:
        print('  Stored vectors:')
        for label, (x, y) in stored.items():
            print(_fmt2d(label, x, y))

def _ShowVectors3D(stored):
    if not stored:
        print('  No vectors stored yet.')
    else:
        print('  Stored vectors:')
        for label, (x, y, z) in stored.items():
            print(_fmt3d(label, x, y, z))

def _VectorStore2D(stored, title='Physics 2D'):
    """Vector store manager for 2D. Mutates stored in place. Returns False if user wants to exit entirely."""
    while True:
        _SectionHeader(title, 'Vector Store')
        _ShowVectors2D(stored)
        print()
        print('  (1)  Add a vector')
        print('  (2)  Edit a vector')
        print('  (3)  Remove a vector')
        print('  (4)  Done — go to sections')
        print()
        _ExitBar('Return to main menu')
        print()
        try:
            action = int(input('  Choose: '))
        except ValueError:
            continue
        if action == 0:
            return False
        elif action == 1:
            label = input('  Label (e.g. a, b, v1): ').strip()
            if not label:
                print('\n  Please enter a label.')
                continue
            try:
                x = float(input(f'  {label}x  (i): '))
                y = float(input(f'  {label}y  (j): '))
            except ValueError:
                print('\n  Invalid number.')
                continue
            stored[label] = (x, y)
            print()
            print(_fmt2d(label, x, y))
        elif action == 2:
            if not stored:
                print('\n  No vectors to edit.')
                continue
            _ShowVectors2D(stored)
            label = input('\n  Which label to edit? ').strip()
            if label not in stored:
                print(f'\n  No vector "{label}" found.')
                continue
            try:
                x = float(input(f'  New {label}x (i): '))
                y = float(input(f'  New {label}y (j): '))
            except ValueError:
                print('\n  Invalid number.')
                continue
            stored[label] = (x, y)
            print()
            print(_fmt2d(label, x, y))
        elif action == 3:
            if not stored:
                print('\n  No vectors to remove.')
                continue
            _ShowVectors2D(stored)
            label = input('\n  Which label to remove? ').strip()
            if label not in stored:
                print(f'\n  No vector "{label}" found.')
            else:
                del stored[label]
                print(f'\n  Removed "{label}".')
        elif action == 4:
            return True
        else:
            print('\n  That was not a valid option.')

def _VectorStore3D(stored, title='Physics 3D'):
    """Vector store manager for 3D. Mutates stored in place. Returns False if user wants to exit entirely."""
    while True:
        _SectionHeader(title, 'Vector Store')
        _ShowVectors3D(stored)
        print()
        print('  (1)  Add a vector')
        print('  (2)  Edit a vector')
        print('  (3)  Remove a vector')
        print('  (4)  Done — go to sections')
        print()
        _ExitBar('Return to main menu')
        print()
        try:
            action = int(input('  Choose: '))
        except ValueError:
            continue
        if action == 0:
            return False
        elif action == 1:
            label = input('  Label (e.g. a, b, v1): ').strip()
            if not label:
                print('\n  Please enter a label.')
                continue
            try:
                x = float(input(f'  {label}x  (i): '))
                y = float(input(f'  {label}y  (j): '))
                z = float(input(f'  {label}z  (k): '))
            except ValueError:
                print('\n  Invalid number.')
                continue
            stored[label] = (x, y, z)
            print()
            print(_fmt3d(label, x, y, z))
        elif action == 2:
            if not stored:
                print('\n  No vectors to edit.')
                continue
            _ShowVectors3D(stored)
            label = input('\n  Which label to edit? ').strip()
            if label not in stored:
                print(f'\n  No vector "{label}" found.')
                continue
            try:
                x = float(input(f'  New {label}x (i): '))
                y = float(input(f'  New {label}y (j): '))
                z = float(input(f'  New {label}z (k): '))
            except ValueError:
                print('\n  Invalid number.')
                continue
            stored[label] = (x, y, z)
            print()
            print(_fmt3d(label, x, y, z))
        elif action == 3:
            if not stored:
                print('\n  No vectors to remove.')
                continue
            _ShowVectors3D(stored)
            label = input('\n  Which label to remove? ').strip()
            if label not in stored:
                print(f'\n  No vector "{label}" found.')
            else:
                del stored[label]
                print(f'\n  Removed "{label}".')
        elif action == 4:
            return True
        else:
            print('\n  That was not a valid option.')

def _Pick2D(stored, prompt_label):
    """
    Get a 2D vector (x, y) for an operation.
    Direct mode (stored is None): prompts for x, y.
    Stored mode: shows list, user picks a label or 'new' for a one-time entry.
    """
    if stored is None:
        print(f'  Vector {prompt_label}:')
        x = float(input(f'    x (i): '))
        y = float(input(f'    y (j): '))
        return x, y
    print()
    _ShowVectors2D(stored)
    raw = input(f'\n  Vector {prompt_label} — enter label  (or "new"): ').strip()
    if raw in stored:
        x, y = stored[raw]
        print(f'  Using: {_fmt2d(raw, x, y).strip()}')
        return x, y
    print(f'  Entering values manually for {prompt_label}:')
    x = float(input(f'    x (i): '))
    y = float(input(f'    y (j): '))
    return x, y

def _Pick3D(stored, prompt_label):
    """
    Get a 3D vector (x, y, z) for an operation.
    Direct mode (stored is None): prompts for x, y, z.
    Stored mode: shows list, user picks a label or enters manually.
    """
    if stored is None:
        print(f'  Vector {prompt_label}:')
        x = float(input(f'    x (i): '))
        y = float(input(f'    y (j): '))
        z = float(input(f'    z (k): '))
        return x, y, z
    print()
    _ShowVectors3D(stored)
    raw = input(f'\n  Vector {prompt_label} — enter label  (or "new"): ').strip()
    if raw in stored:
        x, y, z = stored[raw]
        print(f'  Using: {_fmt3d(raw, x, y, z).strip()}')
        return x, y, z
    print(f'  Entering values manually for {prompt_label}:')
    x = float(input(f'    x (i): '))
    y = float(input(f'    y (j): '))
    z = float(input(f'    z (k): '))
    return x, y, z

def _to_polar(x, y):
    """(x, y) → (magnitude, angle_degrees) for Physics_2D function calls."""
    mag   = math.sqrt(x**2 + y**2)
    angle = math.degrees(math.atan2(y, x))
    return mag, angle

def _to_spherical(x, y, z):
    """(x, y, z) → (magnitude, theta_degrees, phi_degrees) for Physics_3D function calls."""
    mag   = math.sqrt(x**2 + y**2 + z**2)
    theta = math.degrees(math.atan2(y, x))
    phi   = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))
    return mag, theta, phi

# ============================================================
# PHYSICS 2D DEBUG
# ============================================================

def Physics2DDebug():
    # ── Input mode selection ────────────────────────────────
    while True:
        _SectionHeader('Physics 2D', 'Choose input mode')
        print('  (1)  Direct — enter values with each calculation')
        print('  (2)  Store vectors — define vectors once, reuse across all sections')
        print()
        _ExitBar('Return to main menu')
        print()
        try:
            mode = _ask('  Choose: ', cast=int)
        except ValueError:
            continue
        if mode == 0:
            return
        if mode in (1, 2):
            break
        print('\n  That was not a valid option.')

    stored = None
    if mode == 2:
        stored = {}
        if not _VectorStore2D(stored):
            return  # user exited from store manager

    # ── Section loop ────────────────────────────────────────
    SECTIONS = [
        'Projectile Motion',
        'Path Resultant',
        'Horizontal Projectile  (fired from height)',
        'Path Kinematics  (displacement, velocity, speed)',
        "Newton's 2nd Law  (F = ma, component form)",
        'Free Body Diagram  (equilibrium, normal force)',
        'Friction  (flat surface, off-axis push, incline)',
        'Tension  (hanging, accelerating, angled, Atwood)',
        'Circular Motion  (centripetal force, max speed, period)',
        'Universal Gravitation  (F = Gm1m2/r², orbital speed, escape velocity)',
    ]
    if stored is not None:
        SECTIONS = SECTIONS + ['Manage Stored Vectors']

    while True:
        _SectionHeader('Physics 2D', 'Choose a section')
        if stored is not None:
            print()
            _ShowVectors2D(stored)
            print()
        for i, s in enumerate(SECTIONS, 1):
            print(f'  ({i})  {s}')
        print()
        _ExitBar('Return to main menu')
        print()
        try:
            sec = _menu_int('  Select a section: ')
        except ValueError:
            continue
        if sec == 0:
            return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section.')
            continue

        # Manage vectors option (stored mode only)
        if stored is not None and sec == len(SECTIONS):
            if not _VectorStore2D(stored):
                return
            continue

        # ── Function loop ────────────────────────────────────
        while True:
            _SectionHeader('Physics 2D', SECTIONS[sec - 1])
            if stored is not None:
                _ShowVectors2D(stored)
                print()
            if sec == 1:
                print('  Each function asks how you want to specify the launch.')
                print('  Input mode (A): speed + angle   |   Input mode (B): vx + vy components')
                print()
                print('  (1)  Velocity at a given time    — vx, vy, and total speed')
                print('  (2)  Position at a given time    — x, y')
                print('  (3)  Max height                  — peak time and height')
                print('  (4)  Total flight time and range — when and where it lands')
                print('  (5)  Full path  (with air resistance)    — requires speed + angle + mass')
                print('  (6)  Full path  (no air resistance)      — list of (x, y) points')
            elif sec == 2:
                print('  (1)  Net X and Y displacement')
                print('  (2)  Straight-line distance from start to end  (magnitude)')
                print('  (3)  Direction from start to end  (angle from East)')
                print('  (4)  Both magnitude and direction')
            elif sec == 1:
                print('  Object fired HORIZONTALLY from a height  (no vertical launch component)')
                print()
                print('  (1)  Time in air')
                print('  (2)  Horizontal range from firing point')
                print('  (3)  Vertical speed at ground impact')
                print('  (4)  Total speed at ground impact')
                print('  (5)  All four results at once')
            elif sec == 2:
                print('  Each segment: distance (m)  +  direction (°)  +  time (s)')
                print('  Convention: 0°=East  90°=North  180°=West  270°=South')
                print()
                print('  (1)  Total displacement  Δr = rx·i + ry·j')
                print('  (2)  Average velocity    v_avg = vx·i + vy·j')
                print('  (3)  Average speed       (scalar — total distance / total time)')
                print('  (4)  All three at once')
            elif sec == 1:
                print("  Enter forces as  Fx  Fy  components  (i / j)")
                print()
                print('  (1)  Net force  F⃗_net = ΣFx·i + ΣFy·j')
                print('  (2)  Acceleration  a⃗ = F⃗_net / m')
                print('  (3)  Acceleration magnitude  |a⃗|')
                print('  (4)  Net force polar  (magnitude + direction)')
            elif sec == 2:
                print('  Equilibrium and normal force on a horizontal surface.')
                print()
                print('  (1)  Normal force  N = W − (sum of upward forces)')
                print('  (2)  Balancing force needed for equilibrium')
                print('  (3)  Full free body summary  (all forces + net)')
            elif sec == 1:
                print('  Friction problems — flat, off-axis push, or incline.')
                print()
                print('  (1)  Flat surface  —  horizontal push  (Ff = μmg,  a = (F−Ff)/m)')
                print('  (2)  Off-axis push  —  force at angle below horizontal  (N = mg + F·sinθ)')
                print('  (3)  Incline  —  normal force and parallel gravity component  (mg·cosθ, mg·sinθ)')
                print('  (4)  Minimum force to move  —  F_min = μs × mg  (overcomes max static friction)')
                print('  (5)  Final speed after distance  —  v = sqrt(u² + 2·a·d)  (flat surface push)')
            elif sec == 2:
                print('  Rope and cord tension problems.')
                print()
                print('  (1)  Hanging at rest          T = mg')
                print('  (2)  Accelerating vertically  T = m(g + a)  [a negative = downward]')
                print('  (3)  Rope at an angle         T = mg / cos(θ)')
                print('  (4)  Atwood machine — tension  T = 2m1m2g / (m1+m2)')
                print('  (5)  Atwood machine — acceleration  a = (m1−m2)g / (m1+m2)')
            elif sec == 1:
                print('  Circular motion — centripetal force, max speed, period, frequency.')
                print()
                print('  (1)  Centripetal force         Fc = mv² / r')
                print('  (2)  Max speed before sliding  v = sqrt(μgr)  [friction as centripetal]')
                print('  (3)  Centripetal acceleration  ac = v² / r')
                print('  (4)  Period                    T = 2πr / v')
                print('  (5)  Frequency                 f = v / (2πr)')
            elif sec == 2:
                print('  Universal Gravitation — F = G·m1·m2 / r²')
                print()
                print('  (1)  Gravitational force         F = G·m1·m2 / r²')
                print('  (2)  Gravitational field strength g = G·M / r²  (free-fall acceleration)')
                print('  (3)  Distance for target field   r = sqrt(G·M / g)')
                print('  (4)  Orbital speed               v = sqrt(G·M / r)')
                print('  (5)  Orbital period              T = 2π·sqrt(r³/GM)')
                print('  (6)  Gravitational potential energy  U = −G·m1·m2 / r')
                print('  (7)  Escape velocity             v_esc = sqrt(2·G·M / r)')
            print()
            _ExitBar('Return to sections')
            print()
            try:
                choice = _menu_int('  Select a function: ')
            except ValueError:
                continue
            if choice == 0:
                break

            if sec == 1:
                # Projectile — unified input mode per function

                def _proj_input(need_mass=False, need_time=False, need_steps=False, need_y0=False):
                    """Ask input mode then collect launch params. Returns dict of values."""
                    print()
                    print('  Input mode:')
                    print('  (A)  Speed + angle')
                    print('  (B)  Horizontal vx  and  vertical vy  components')
                    print()
                    mode = input('  Choose A or B: ').strip().upper()
                    vals = {}
                    if mode == 'A':
                        vals['speed'] = _ask('  Launch speed (m/s): ', cast=float)
                        vals['angle'] = _ask('  Launch angle above horizontal (degrees): ', cast=float)
                        vals['vx0']   = vals['speed'] * math.cos(math.radians(vals['angle']))
                        vals['vy0']   = vals['speed'] * math.sin(math.radians(vals['angle']))
                    else:
                        vals['vx0']   = _ask('  Horizontal speed vx (m/s): ', cast=float)
                        vals['vy0']   = _ask('  Vertical speed vy (m/s, positive = up): ', cast=float)
                        vals['speed'] = math.sqrt(vals['vx0']**2 + vals['vy0']**2)
                        vals['angle'] = math.degrees(math.atan2(vals['vy0'], vals['vx0']))
                    vals['mode'] = mode
                    if need_time:
                        vals['time'] = _ask('  Time (s): ', cast=float)
                    if need_y0:
                        raw = input('  Launch height y0 (Enter = 0): ').strip()
                        vals['y0'] = float(raw) if raw else 0.0
                    if need_mass:
                        vals['mass'] = _ask('  Mass (kg): ', cast=float)
                    if need_steps:
                        vals['steps'] = int(input('  Number of steps (Enter = 100): ') or '100')
                    return vals

                result = None
            try:
                    match choice:
                        case 1:
                            v = _proj_input(need_time=True)
                            vx, vy = Physics_2D.ProjectileVelocityXY(v['vx0'], v['vy0'], v['time'])
                            speed  = Physics_2D.ProjectileSpeedXY(v['vx0'], v['vy0'], v['time'])
                            print()
                            print(f'  Horizontal speed vx : {vx:.4f} m/s  (unchanged — no air resistance)')
                            print(f'  Vertical speed   vy : {vy:.4f} m/s  (vy0 − g·t)')
                            print(f'  Total speed    |v|  : {speed:.4f} m/s')
                            print()
                            continue
                        case 2:
                            v = _proj_input(need_time=True, need_y0=True)
                            raw_x0 = input('  Starting x position (Enter = 0): ').strip()
                            x0 = float(raw_x0) if raw_x0 else 0.0
                            x, y = Physics_2D.ProjectilePositionXY(v['vx0'], v['vy0'], v['time'], x0, v['y0'])
                            print()
                            print(f'  x position : {x:.4f} m')
                            print(f'  y position : {y:.4f} m')
                            print()
                            continue
                        case 3:
                            v = _proj_input(need_y0=True)
                            t_peak, y_max = Physics_2D.ProjectileMaxHeightXY(v['vx0'], v['vy0'], v['y0'])
                            print()
                            if v['vy0'] <= 0:
                                print(f'  No peak — projectile is moving downward or horizontally from the start.')
                                print(f'  Starting height : {v["y0"]:.4f} m')
                            else:
                                print(f'  Time to peak    : {t_peak:.4f} s  (when vy = 0)')
                                print(f'  Maximum height  : {y_max:.4f} m  (y0 + vy0²/2g)')
                            print()
                            continue
                        case 4:
                            v = _proj_input(need_y0=True)
                            t_land = Physics_2D.ProjectileFlightTimeXY(v['vx0'], v['vy0'], v['y0'])
                            x_land = Physics_2D.ProjectileRangeXY(v['vx0'], v['vy0'], v['y0'])
                            print()
                            print(f'  Launch speed    : {v["speed"]:.4f} m/s  at  {v["angle"]:.2f}°')
                            print(f'  vx = {v["vx0"]:.4f} m/s    vy0 = {v["vy0"]:.4f} m/s')
                            print(f'  Total flight time : {t_land:.4f} s')
                            print(f'  Horizontal range  : {x_land:.4f} m')
                            print()
                            continue
                        case 5:
                            # Air resistance — needs mass; uses angle-form functions
                            v = _proj_input(need_mass=True, need_steps=True)
                            raw_t = input('  Total flight time (s): ').strip()
                            t_total = float(raw_t)
                            result = Physics_2D.ProjectilePath(
                                v['speed'], v['angle'], t_total, v['mass'], v['steps'])
                        case 6:
                            v = _proj_input(need_steps=True)
                            raw_t = input('  Total flight time (s): ').strip()
                            t_total = float(raw_t)
                            result = Physics_2D.ProjectilePathNoAR(
                                v['speed'], v['angle'], t_total, v['steps'])
                        case _:
                            print('\n  That was not a valid option.')
                            continue
            except _AskAbort:
                print()
                _p('Calculation cancelled. Returning to the function list.')
                print()
                continue
            except (ValueError, TypeError) as e:
                print(f'\n  Invalid input: {e}  Please try again.')
                print()
                continue
            if result is not None:
                print()
                print(f'  Result: {result}')
                print()
                # Path resultant — in stored mode let user pick vectors as segments
                if stored is not None and stored:
                    print()
                    print('  Build path from stored vectors, or enter segments manually.')
                    print('  Enter labels in order  (e.g.  a b c),  or leave blank for manual entry.')
                    print()
                    _ShowVectors2D(stored)
                    print()
                    raw_labels = input('  Labels: ').strip()
                else:
                    raw_labels = ''

                segments = []
                if raw_labels:
                    for lbl in raw_labels.split():
                        if lbl in stored:
                            x, y = stored[lbl]
                            mag, angle = _to_polar(x, y)
                            segments.append((mag, angle))
                        else:
                            print(f'  "{lbl}" not found — skipped.')
                else:
                    print()
                    print('  Angle convention: 0° = East   90° = North   180° = West   270° = South')
                    print()
                    seg_num = 1
                    while True:
                        print(f'  Segment {seg_num} — leave magnitude blank when done.')
                        raw2 = input(f'    Magnitude (m): ').strip()
                        if not raw2:
                            break
                        magnitude = float(raw2)
                        angle     = float(input(f'    Direction (degrees): '))
                        segments.append((magnitude, angle))
                        seg_num += 1

                if len(segments) < 2:
                    print('\n  Need at least two segments to compute a resultant.')
                    print()
                    continue

                print()
                print(f'  {len(segments)} segments:')
                for i, (m, a) in enumerate(segments, 1):
                    print(f'    Segment {i}: {m:.3f} m at {a:.1f}°')

                match choice:
                    case 1:
                        rx, ry = Physics_2D.PathResultantXY(segments)
                        print(f'\n  Net X: {rx:.4f} m    Net Y: {ry:.4f} m')
                    case 2:
                        mag = Physics_2D.PathResultantMagnitude(segments)
                        print(f'\n  Magnitude: {mag:.4f} m')
                    case 3:
                        ang = Physics_2D.PathResultantAngle(segments)
                        print(f'\n  Direction: {ang:.2f}° from East')
                    case 4:
                        mag, ang = Physics_2D.PathResultant(segments)
                        rx, ry   = Physics_2D.PathResultantXY(segments)
                        print(f'\n  Magnitude  : {mag:.4f} m')
                        print(f'  Direction  : {ang:.2f}° from East')
                        print(f'  X component: {rx:.4f} m')
                        print(f'  Y component: {ry:.4f} m')
                    case _:
                        print('\n  That was not a valid option.')
                        continue
                print()

            elif sec == 1:
                # Horizontal projectile — always direct input
                print()
                h  = _ask('  Launch height above ground (m): ', cast=float)
                if choice in (2, 4, 5):
                    vx = _ask('  Horizontal launch speed (m/s): ', cast=float)
                raw_g = input('  Gravity (m/s²)  [Enter for 9.8]: ').strip()
                g  = float(raw_g) if raw_g else 9.8
                print()
                match choice:
                    case 1:
                        t = Physics_2D.HorizontalProjectileTime(h, g)
                        print(f'  Time in air: {t:.3f} s')
                    case 2:
                        t = Physics_2D.HorizontalProjectileTime(h, g)
                        x = Physics_2D.HorizontalProjectileRange(h, vx, g)
                        print(f'  Time in air  : {t:.3f} s')
                        print(f'  Range        : {x:.2f} m')
                    case 3:
                        vy = Physics_2D.HorizontalProjectileImpactVY(h, g)
                        print(f'  Vertical speed at impact: {vy:.3f} m/s')
                    case 4:
                        spd = Physics_2D.HorizontalProjectileImpactSpeed(h, vx, g)
                        vy  = Physics_2D.HorizontalProjectileImpactVY(h, g)
                        print(f'  vx at impact : {vx:.3f} m/s  (unchanged)')
                        print(f'  vy at impact : {vy:.3f} m/s')
                        print(f'  Total speed  : {spd:.3f} m/s')
                    case 5:
                        t   = Physics_2D.HorizontalProjectileTime(h, g)
                        x   = Physics_2D.HorizontalProjectileRange(h, vx, g)
                        vy  = Physics_2D.HorizontalProjectileImpactVY(h, g)
                        spd = Physics_2D.HorizontalProjectileImpactSpeed(h, vx, g)
                        print(f'  Time in air          : {t:.3f} s')
                        print(f'  Horizontal range     : {x:.2f} m')
                        print(f'  Vertical vy (impact) : {vy:.3f} m/s')
                        print(f'  Total speed (impact) : {spd:.3f} m/s')
                    case _:
                        print('\n  That was not a valid option.')
                        continue
                print()

            elif sec == 2:
                # Path kinematics — collect timed segments then compute
                print()
                print('  Enter each leg of the journey as  distance  direction  time.')
                print('  Leave distance blank when done.')
                print()
                segments = []
                seg_num  = 1
                while True:
                    print(f'  Leg {seg_num} — leave distance blank to finish.')
                    raw = input(f'    Distance (m): ').strip()
                    if not raw:
                        break
                    magnitude = float(raw)
                    angle     = float(input(f'    Direction (°, 0=East 90=North 180=West 270=South): '))
                    time      = float(input(f'    Time (s): '))
                    segments.append((magnitude, angle, time))
                    seg_num  += 1
                if len(segments) < 1:
                    print('\n  Enter at least one segment.')
                    print()
                    continue
                print()
                print(f'  {len(segments)} leg(s) entered:')
                for i, (m, a, t) in enumerate(segments, 1):
                    print(f'    Leg {i}: {m} m at {a}° in {t} s')
                print()
                match choice:
                    case 1:
                        rx, ry = Physics_2D.PathResultantXY([(m, a) for m, a, t in segments])
                        print(f'  Δr  =  {rx:.4f}i  +  {ry:.4f}j  m')
                        print(f'  |Δr| = {(rx**2+ry**2)**0.5:.4f} m')
                    case 2:
                        vx, vy = Physics_2D.AverageVelocity2D(segments)
                        print(f'  v_avg  =  {vx:.4f}i  +  {vy:.4f}j  m/s')
                        print(f'  |v_avg| = {(vx**2+vy**2)**0.5:.4f} m/s')
                    case 3:
                        spd = Physics_2D.AverageSpeed2D(segments)
                        print(f'  Average speed = {spd:.4f} m/s')
                    case 4:
                        rx, ry, vx, vy, spd = Physics_2D.PathKinematics2D(segments)
                        t_total = sum(t for _, _, t in segments)
                        d_total = sum(m for m, _, _ in segments)
                        print(f'  Total distance  : {d_total:.1f} m')
                        print(f'  Total time      : {t_total:.1f} s')
                        print()
                        print(f'  Displacement    : {rx:.4f}i  +  {ry:.4f}j  m')
                        print(f'  |Displacement|  : {(rx**2+ry**2)**0.5:.4f} m')
                        print()
                        print(f'  Avg velocity    : {vx:.4f}i  +  {vy:.4f}j  m/s')
                        print(f'  |Avg velocity|  : {(vx**2+vy**2)**0.5:.4f} m/s')
                        print()
                        print(f'  Avg speed       : {spd:.4f} m/s  (scalar)')
                    case _:
                        print('\n  That was not a valid option.')
                        continue
                print()

            elif sec == 1:
                # Newton's 2nd Law — collect forces then compute
                print()
                print('  Enter each force as  Fx  Fy  components.')
                print('  Leave Fx blank when done.')
                print()
                forces = []
                f_num  = 1
                while True:
                    raw = input(f'  Force {f_num}  Fx (i): ').strip()
                    if not raw:
                        break
                    fx = float(raw)
                    fy = float(input(f'  Force {f_num}  Fy (j): '))
                    forces.append((fx, fy))
                    f_num += 1
                if not forces:
                    print('\n  Enter at least one force.')
                    print()
                    continue
                print()
                print(f'  {len(forces)} force(s) entered:')
                for i, (fx, fy) in enumerate(forces, 1):
                    print(f'    F{i} = {fx}i  +  {fy}j  N')
                print()
                if choice in (2, 3):
                    mass = _ask('  Mass (kg): ', cast=float)
                    print()
                match choice:
                    case 1:
                        fx, fy = Physics_2D.NetForce2D(forces)
                        mag = (fx**2+fy**2)**0.5
                        print(f'  F⃗_net  =  {fx:.4f}i  +  {fy:.4f}j  N')
                        print(f'  |F⃗_net| = {mag:.4f} N')
                    case 2:
                        ax, ay = Physics_2D.Acceleration2DFromForces(forces, mass)
                        print(f'  a⃗  =  {ax:.4f}i  +  {ay:.4f}j  m/s²')
                    case 3:
                        a_mag = Physics_2D.AccelerationMagnitude2D(forces, mass)
                        ax, ay = Physics_2D.Acceleration2DFromForces(forces, mass)
                        print(f'  a⃗      =  {ax:.4f}i  +  {ay:.4f}j  m/s²')
                        print(f'  |a⃗|    =  {a_mag:.4f} m/s²')
                    case 4:
                        mag, angle = Physics_2D.NetForcePolar(forces)
                        fx, fy = Physics_2D.NetForce2D(forces)
                        print(f'  F⃗_net  =  {fx:.4f}i  +  {fy:.4f}j  N')
                        print(f'  |F⃗_net| = {mag:.4f} N  at  {angle:.2f}°')
                    case _:
                        print('\n  That was not a valid option.')
                        continue
                print()

            elif sec == 2:
                # Free body diagram
                print()
                match choice:
                    case 1:
                        weight = _ask('  Object weight  (N, positive = downward): ', cast=float)
                        print('  Enter each upward force magnitude. Leave blank when done.')
                        up_forces = []
                        n = 1
                        while True:
                            raw = input(f'  Upward force {n} (N): ').strip()
                            if not raw:
                                break
                            up_forces.append(float(raw))
                            n += 1
                        N = weight - sum(up_forces)
                        print()
                        print(f'  Weight          : {weight} N  ↓')
                        for i, f in enumerate(up_forces, 1):
                            print(f'  Upward force {i}  : {f} N  ↑')
                        print(f'  Normal force  N : {N:.4f} N  ↑  (surface pushes up)')
                    case 2:
                        print('  Enter all KNOWN forces as  Fx  Fy. Leave Fx blank when done.')
                        forces = []
                        n = 1
                        while True:
                            raw = input(f'  Force {n}  Fx (i): ').strip()
                            if not raw:
                                break
                            fx = float(raw)
                            fy = float(input(f'  Force {n}  Fy (j): '))
                            forces.append((fx, fy))
                            n += 1
                        if not forces:
                            print('\n  Enter at least one force.')
                            print()
                            continue
                        bx, by = Physics_2D.EquilibriumForce2D(forces)
                        mag = (bx**2+by**2)**0.5
                        print()
                        print(f'  Balancing force needed: {bx:.4f}i  +  {by:.4f}j  N')
                        print(f'  Magnitude: {mag:.4f} N')
                    case 3:
                        print('  Enter all forces as  Fx  Fy. Leave Fx blank when done.')
                        forces = []
                        n = 1
                        while True:
                            raw = input(f'  Force {n}  Fx (i): ').strip()
                            if not raw:
                                break
                            fx = float(raw)
                            fy = float(input(f'  Force {n}  Fy (j): '))
                            forces.append((fx, fy))
                            n += 1
                        if not forces:
                            print('\n  Enter at least one force.')
                            print()
                            continue
                        fx_net, fy_net = Physics_2D.NetForce2D(forces)
                        mag, angle = Physics_2D.NetForcePolar(forces)
                        print()
                        print(f'  Forces:')
                        for i, (fx, fy) in enumerate(forces, 1):
                            print(f'    F{i} = {fx}i  +  {fy}j  N')
                        print()
                        print(f'  F⃗_net   = {fx_net:.4f}i  +  {fy_net:.4f}j  N')
                        print(f'  |F⃗_net| = {mag:.4f} N  at  {angle:.2f}°')
                        if abs(mag) < 1e-9:
                            print('  → System is in EQUILIBRIUM')
                    case _:
                        print('\n  That was not a valid option.')
                        continue
                print()

            elif sec == 1:
                # Friction
                print()
                match choice:
                    case 1:
                        # Flat surface, horizontal push
                        mass = _ask('  Mass (kg): ', cast=float)
                        mu   = _ask('  Coefficient of kinetic friction (μk): ', cast=float)
                        F    = _ask('  Applied horizontal force (N): ', cast=float)
                        g    = 9.8
                        N    = Forces.NormalForce(mass, g)
                        Ff   = Forces.FrictionForce(mu, N)
                        a    = Forces.Acceleration(F - Ff, mass)
                        print()
                        print(f'  Normal force   N  : {N:.4f} N')
                        print(f'  Friction force Ff : {Ff:.4f} N')
                        print(f'  Net force  F−Ff   : {F-Ff:.4f} N')
                        print(f'  Acceleration   a  : {a:.4f} m/s²')
                    case 2:
                        # Off-axis push (force angled below horizontal)
                        mass  = _ask('  Mass (kg): ', cast=float)
                        mu    = _ask('  Coefficient of kinetic friction (μk): ', cast=float)
                        F     = _ask('  Applied force magnitude (N): ', cast=float)
                        theta = _ask('  Angle below horizontal (degrees): ', cast=float)
                        N     = Forces.NormalForceOffAxis(mass, F, theta)
                        Ff    = Forces.FrictionForceOffAxis(mass, mu, F, theta)
                        a     = Forces.AccelerationOffAxis(mass, mu, F, theta)
                        Fx    = F * math.cos(math.radians(theta))
                        print()
                        print(f'  Normal force   N  : {N:.4f} N  (mg + F·sinθ)')
                        print(f'  Friction force Ff : {Ff:.4f} N  (μN)')
                        print(f'  Horizontal push   : {Fx:.4f} N  (F·cosθ)')
                        print(f'  Net horiz. force  : {Fx-Ff:.4f} N')
                        print(f'  Acceleration   a  : {a:.4f} m/s²')
                    case 3:
                        # Incline — normal force and tension/parallel gravity
                        mass  = _ask('  Mass (kg): ', cast=float)
                        theta = _ask('  Incline angle (degrees): ', cast=float)
                        N     = Forces.NormalForceIncline(mass, theta)
                        T     = Forces.FrictionForceIncline(mass, theta)
                        print()
                        print(f'  Normal force  N = mg·cosθ : {N:.4f} N  (perpendicular to slope)')
                        print(f'  Parallel comp T = mg·sinθ : {T:.4f} N  (down the slope / tension needed)')
                    case 4:
                        # Minimum force to overcome static friction
                        mass = _ask('  Mass (kg): ', cast=float)
                        mu_s = _ask('  Coefficient of static friction (μs): ', cast=float)
                        N       = Forces.NormalForce(mass)
                        F_min   = Forces.FrictionForce(mu_s, N)
                        print()
                        print(f'  Normal force   N     : {N:.4f} N  (= mg)')
                        print(f'  Min force to move    : {F_min:.4f} N  (= μs × N)')
                        print(f'  Any force > {F_min:.4f} N will start motion')
                    case 5:
                        # Final speed after distance — flat surface
                        mass = _ask('  Mass (kg): ', cast=float)
                        mu   = _ask('  Coefficient of kinetic friction (μk): ', cast=float)
                        F    = _ask('  Applied horizontal force (N): ', cast=float)
                        d    = _ask('  Distance (m): ', cast=float)
                        raw_u = input('  Initial speed (m/s)  [Enter = 0, starting from rest]: ').strip()
                        u    = float(raw_u) if raw_u else 0.0
                        v, a, Ff, N = Forces.FinalSpeedFlatFriction(mass, mu, F, d, u)
                        print()
                        print(f'  Normal force   N  : {N:.4f} N')
                        print(f'  Friction force Ff : {Ff:.4f} N  (= μN)')
                        print(f'  Net force  F−Ff   : {F-Ff:.4f} N')
                        print(f'  Acceleration   a  : {a:.4f} m/s²')
                        print(f'  Initial speed  u  : {u:.4f} m/s')
                        print(f'  Distance       d  : {d:.4f} m')
                        print()
                        if v == 0.0 and a < 0:
                            print(f'  Object decelerates to rest before reaching {d} m')
                        else:
                            print(f'  Final speed    v  : {v:.4f} m/s  (v = sqrt(u² + 2·a·d))')
                    case _:
                        print('\n  That was not a valid option.')
                        continue
                print()

            elif sec == 2:
                # Tension
                print()
                match choice:
                    case 1:
                        mass = _ask('  Mass (kg): ', cast=float)
                        T, W, F_net = Forces.TensionHanging(mass)
                        print()
                        print(f'  Object weight  W     : {W:.4f} N  ↓')
                        print(f'  Rope tension   T     : {T:.4f} N  ↑  (equals weight — at rest)')
                        print(f'  Net force on object  : {F_net:.4f} N  (zero — equilibrium)')
                    case 2:
                        mass = _ask('  Mass (kg): ', cast=float)
                        a    = _ask('  Acceleration (m/s²)  [positive=up, negative=down]: ', cast=float)
                        T, W, F_net = Forces.TensionAccelerating(mass, a)
                        print()
                        print(f'  Object weight  W     : {W:.4f} N  ↓')
                        print(f'  Rope tension   T     : {T:.4f} N  ↑')
                        print(f'  Net force on object  : {F_net:.4f} N  (= ma)')
                        if T > W:
                            print('  → Tension GREATER than weight  (accelerating upward)')
                        elif T < W:
                            print('  → Tension LESS than weight  (accelerating downward)')
                        else:
                            print('  → Tension equals weight  (constant velocity)')
                    case 3:
                        mass  = _ask('  Mass (kg): ', cast=float)
                        theta = _ask('  Angle from vertical (degrees): ', cast=float)
                        T, T_x, T_y, W = Forces.TensionAtAngle(mass, theta)
                        print()
                        print(f'  Object weight  W     : {W:.4f} N  ↓')
                        print(f'  Rope tension   T     : {T:.4f} N  (magnitude along rope)')
                        print(f'  Horizontal component : {T_x:.4f} N  →  (T·sinθ)')
                        print(f'  Vertical component   : {T_y:.4f} N  ↑  (T·cosθ = W)')
                    case 4:
                        m1 = _ask('  Mass 1 (kg): ', cast=float)
                        m2 = _ask('  Mass 2 (kg): ', cast=float)
                        T, W1, W2, a, F_net1, F_net2 = Forces.TensionAtwood(m1, m2)
                        print()
                        print(f'  Mass 1 weight  W1    : {W1:.4f} N  ↓')
                        print(f'  Mass 2 weight  W2    : {W2:.4f} N  ↓')
                        print(f'  Rope tension   T     : {T:.4f} N  (same throughout rope)')
                        print(f'  Net force on m1      : {F_net1:.4f} N  (W1 − T)')
                        print(f'  Net force on m2      : {F_net2:.4f} N  (T − W2)')
                        print(f'  System acceleration  : {a:.4f} m/s²')
                        if a > 0:
                            print('  → m1 accelerates downward, m2 accelerates upward')
                        elif a < 0:
                            print('  → m2 accelerates downward, m1 accelerates upward')
                        else:
                            print('  → System in equilibrium  (equal masses)')
                    case 5:
                        m1 = _ask('  Mass 1 (kg): ', cast=float)
                        m2 = _ask('  Mass 2 (kg): ', cast=float)
                        a, T, W1, W2, F_net1, F_net2 = Forces.AtwoodAcceleration(m1, m2)
                        print()
                        print(f'  Mass 1 weight  W1    : {W1:.4f} N  ↓')
                        print(f'  Mass 2 weight  W2    : {W2:.4f} N  ↓')
                        print(f'  Rope tension   T     : {T:.4f} N  (same throughout rope)')
                        print(f'  Net force on m1      : {F_net1:.4f} N  (W1 − T)')
                        print(f'  Net force on m2      : {F_net2:.4f} N  (T − W2)')
                        print(f'  System acceleration  : {a:.4f} m/s²')
                        if a > 0:
                            print('  → m1 accelerates downward, m2 accelerates upward')
                        elif a < 0:
                            print('  → m2 accelerates downward, m1 accelerates upward')
                        else:
                            print('  → System in equilibrium  (equal masses)')
                    case _:
                        print('\n  That was not a valid option.')
                        continue
                print()

            elif sec == 1:
                # Circular Motion
                print()
                match choice:
                    case 1:
                        mass = _ask('  Mass (kg): ', cast=float)
                        v    = _ask('  Speed (m/s): ', cast=float)
                        r    = _ask('  Radius (m): ', cast=float)
                        Fc   = Forces.CentripetalForce(mass, v, r)
                        ac   = Forces.CentripetalAcceleration(v, r)
                        T    = Forces.CircularPeriod(r, v)
                        print()
                        print(f'  Centripetal force   Fc : {Fc:.4f} N  (= mv²/r, directed inward)')
                        print(f'  Centripetal accel   ac : {ac:.4f} m/s²')
                        print(f'  Period               T : {T:.4f} s  (time for one full circle)')
                    case 2:
                        mu = _ask('  Coefficient of friction (μ): ', cast=float)
                        r  = _ask('  Radius (m): ', cast=float)
                        v_max = Forces.MaxCircularSpeedFromFriction(mu, r)
                        mass  = input('  Mass (kg) [optional — press Enter to skip]: ').strip()
                        print()
                        print(f'  Max speed before sliding : {v_max:.4f} m/s  (v = sqrt(μgr))')
                        print(f'  Note: mass cancels — result is independent of mass')
                        if mass:
                            m  = float(mass)
                            Fc = Forces.CentripetalForce(m, v_max, r)
                            N  = Forces.NormalForce(m)
                            Ff = Forces.FrictionForce(mu, N)
                            print()
                            print(f'  At this speed:')
                            print(f'    Normal force   N  : {N:.4f} N')
                            print(f'    Max friction   Ff : {Ff:.4f} N  (= μN = centripetal force)')
                            print(f'    Centripetal Fc    : {Fc:.4f} N  (confirms Ff = Fc at v_max)')
                    case 3:
                        v = _ask('  Speed (m/s): ', cast=float)
                        r = _ask('  Radius (m): ', cast=float)
                        ac = Forces.CentripetalAcceleration(v, r)
                        print()
                        print(f'  Centripetal acceleration : {ac:.4f} m/s²  (ac = v²/r, directed inward)')
                    case 4:
                        r = _ask('  Radius (m): ', cast=float)
                        v = _ask('  Speed (m/s): ', cast=float)
                        T = Forces.CircularPeriod(r, v)
                        print()
                        print(f'  Period  T = 2πr/v : {T:.4f} s  (time for one complete revolution)')
                    case 5:
                        r = _ask('  Radius (m): ', cast=float)
                        v = _ask('  Speed (m/s): ', cast=float)
                        f = Forces.CircularFrequency(v, r)
                        print()
                        print(f'  Frequency  f = v/(2πr) : {f:.4f} Hz  (revolutions per second)')
                        print(f'  Period     T = 1/f     : {1/f:.4f} s' if f != 0 else '  Period: undefined (v=0)')
                    case _:
                        print('\n  That was not a valid option.')
                        continue
                print()

            elif sec == 2:
                # Universal Gravitation
                print()
                match choice:
                    case 1:
                        m1 = _ask('  Mass 1 (kg): ', cast=float)
                        m2 = _ask('  Mass 2 (kg): ', cast=float)
                        r  = _ask('  Distance between centres (m): ', cast=float)
                        F  = Forces.GravitationalForce(m1, m2, r)
                        print()
                        print(f'  Gravitational force : {F:.4e} N  (F = G·m1·m2/r²)')
                        print(f'  Acts equally on both bodies — attractive, along the line joining them')
                    case 2:
                        M = _ask('  Mass of large body (kg): ', cast=float)
                        r = _ask('  Distance from centre (m): ', cast=float)
                        g = Forces.GravitationalFieldStrength(M, r)
                        print()
                        print(f'  Field strength : {g:.4e} m/s²  (g = G·M/r²)')
                        print(f'  This is also the free-fall acceleration at that distance')
                    case 3:
                        M        = _ask('  Mass of large body (kg): ', cast=float)
                        g_target = _ask('  Target field strength (m/s²): ', cast=float)
                        r = Forces.GravitationalFieldRadius(M, g_target)
                        print()
                        print(f'  Distance from centre : {r:.4e} m  (r = sqrt(G·M/g))')
                    case 4:
                        M = _ask('  Mass of large body (kg): ', cast=float)
                        r = _ask('  Orbital radius — centre to orbit (m): ', cast=float)
                        v = Forces.OrbitalSpeed(M, r)
                        T = Forces.OrbitalPeriod(M, r)
                        print()
                        print(f'  Orbital speed  v : {v:.4e} m/s  (v = sqrt(G·M/r))')
                        print(f'  Orbital period T : {T:.4e} s   (T = 2π·sqrt(r³/GM))')
                    case 5:
                        M = _ask('  Mass of large body (kg): ', cast=float)
                        r = _ask('  Orbital radius — centre to orbit (m): ', cast=float)
                        T = Forces.OrbitalPeriod(M, r)
                        v = Forces.OrbitalSpeed(M, r)
                        print()
                        print(f'  Orbital period T : {T:.4e} s   (T = 2π·sqrt(r³/GM))')
                        print(f'  Orbital speed  v : {v:.4e} m/s  (v = sqrt(G·M/r))')
                    case 6:
                        m1 = _ask('  Mass 1 (kg): ', cast=float)
                        m2 = _ask('  Mass 2 (kg): ', cast=float)
                        r  = _ask('  Distance between centres (m): ', cast=float)
                        U  = Forces.GravitationalPotentialEnergy(m1, m2, r)
                        print()
                        print(f'  Gravitational PE : {U:.4e} J  (U = −G·m1·m2/r)')
                        print(f'  Negative — energy needed to separate the bodies to infinity')
                    case 7:
                        M = _ask('  Mass of large body (kg): ', cast=float)
                        r = _ask('  Distance from centre (m): ', cast=float)
                        v = Forces.EscapeVelocity(M, r)
                        print()
                        print(f'  Escape velocity : {v:.4e} m/s  (v = sqrt(2·G·M/r))')
                        print(f'  Minimum speed needed to escape gravity from this distance')
                    case _:
                        print('\n  That was not a valid option.')
                        continue
                print()

def Physics3DDebug():
    # ── Input mode selection ────────────────────────────────
    while True:
        _SectionHeader('Physics 3D', 'Choose input mode')
        print('  (1)  Direct — enter values with each calculation')
        print('  (2)  Store vectors — define vectors once, reuse across all sections')
        print()
        _ExitBar('Return to main menu')
        print()
        try:
            mode = _ask('  Choose: ', cast=int)
        except ValueError:
            continue
        if mode == 0:
            return
        if mode in (1, 2):
            break
        print('\n  That was not a valid option.')

    stored = None
    if mode == 2:
        stored = {}
        if not _VectorStore3D(stored):
            return

    # ── Section loop ────────────────────────────────────────
    SECTIONS = [
        'Projectile Motion',
        'Displacement & Position',
        "Newton's 2nd Law  (F = ma, component form)",
    ]
    if stored is not None:
        SECTIONS = SECTIONS + ['Manage Stored Vectors']

    while True:
        _SectionHeader('Physics 3D', 'Choose a section')
        if stored is not None:
            print()
            _ShowVectors3D(stored)
            print()
        for i, s in enumerate(SECTIONS, 1):
            print(f'  ({i})  {s}')
        print()
        _ExitBar('Return to main menu')
        print()
        try:
            sec = _menu_int('  Select a section: ')
        except ValueError:
            continue
        if sec == 0:
            return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section.')
            continue

        if stored is not None and sec == len(SECTIONS):
            if not _VectorStore3D(stored):
                return
            continue

        # ── Function loop ────────────────────────────────────
        while True:
            _SectionHeader('Physics 3D', SECTIONS[sec - 1])
            if stored is not None:
                _ShowVectors3D(stored)
                print()
            if sec == 1:
                print('  Note: Projectile inputs are always entered directly.')
                print()
                print('  (1)  Velocity at a given time')
                print('  (2)  Position at a given time')
                print('  (3)  Range')
                print('  (4)  Max height')
                print('  (5)  Drag force')
                print('  (6)  Full path with air resistance')
                print('  (7)  Full path without air resistance')
            elif sec == 2:
                print('  Enter all positions/displacements as  x  y  z  components')
                print()
                print('  (1)  Δr⃗  =  r⃗_f − r⃗_i     Find displacement from two positions')
                print('  (2)  r⃗_f =  r⃗_i + Δr⃗      Find final position')
                print('  (3)  r⃗_i =  r⃗_f − Δr⃗      Find initial position')
            elif sec == 3:
                print("  Enter forces as  Fx  Fy  Fz  components  (i / j / k)")
                print()
                print('  (1)  Net force  F⃗_net = ΣFx·i + ΣFy·j + ΣFz·k')
                print('  (2)  Acceleration  a⃗ = F⃗_net / m')
                print('  (3)  Acceleration magnitude  |a⃗|')
                print('  (4)  Net force spherical  (magnitude + θ + φ)')
            print()
            _ExitBar('Return to sections')
            print()
            try:
                choice = _menu_int('  Select a function: ')
            except ValueError:
                continue
            if choice == 0:
                break

            if sec == 1:
                result = None
            try:
                    match choice:
                        case 1:
                            result = Physics_3D.ProjectileVelocity(
                                _ask('  Launch speed (m/s): ', cast=float), _ask('  Launch angle (degrees): ', cast=float),
                                _ask('  Time in flight (s): ', cast=float), _ask('  Mass (kg): ', cast=float))
                        case 2:
                            result = Physics_3D.ProjectilePosition(
                                _ask('  Launch speed (m/s): ', cast=float), _ask('  Launch angle (degrees): ', cast=float),
                                _ask('  Time in flight (s): ', cast=float), _ask('  Mass (kg): ', cast=float))
                        case 3:
                            result = Physics_3D.ProjectileRange(
                                _ask('  Launch speed (m/s): ', cast=float), _ask('  Launch angle (degrees): ', cast=float),
                                _ask('  Total flight time (s): ', cast=float), _ask('  Mass (kg): ', cast=float))
                        case 4:
                            result = Physics_3D.ProjectileMaxHeight(
                                _ask('  Launch speed (m/s): ', cast=float), _ask('  Launch angle (degrees): ', cast=float),
                                _ask('  Mass (kg): ', cast=float))
                        case 5:
                            result = Physics_3D.DragForce(
                                _ask('  Mass (kg): ', cast=float), _ask('  vx (m/s): ', cast=float), _ask('  vy (m/s): ', cast=float))
                        case 6:
                            result = Physics_3D.ProjectilePath(
                                _ask('  Launch speed (m/s): ', cast=float), _ask('  Launch angle (degrees): ', cast=float),
                                _ask('  Total flight time (s): ', cast=float), _ask('  Mass (kg): ', cast=float),
                                _ask('  Number of steps: ', cast=int))
                        case 7:
                            result = Physics_3D.ProjectilePathNoAR(
                                _ask('  Launch speed (m/s): ', cast=float), _ask('  Launch angle (degrees): ', cast=float),
                                _ask('  Total flight time (s): ', cast=float), _ask('  Number of steps: ', cast=int))
                        case _:
                            print('\n  That was not a valid option.')
                            continue
            except _AskAbort:
                print()
                _p('Calculation cancelled. Returning to the function list.')
                print()
                continue
            except (ValueError, TypeError) as e:
                print(f'\n  Invalid input: {e}  Please try again.')
                print()
                continue
            if result is not None:
                print()
                print(f'  Result: {result}')
                print()
                # Displacement & position — all component form
                print()
                match choice:
                    case 1:
                        print('  Enter the INITIAL position vector  (r_i):')
                        rix = _ask('    r_ix  (i): ', cast=float)
                        riy = _ask('    r_iy  (j): ', cast=float)
                        riz = _ask('    r_iz  (k): ', cast=float)
                        print('  Enter the FINAL position vector  (r_f):')
                        rfx = _ask('    r_fx  (i): ', cast=float)
                        rfy = _ask('    r_fy  (j): ', cast=float)
                        rfz = _ask('    r_fz  (k): ', cast=float)
                        drx, dry, drz = Physics_3D.DisplacementXYZ(rix, riy, riz, rfx, rfy, rfz)
                        print(f'\n  Δr⃗  =  r⃗_f − r⃗_i  =  {drx:.4f}i  +  {dry:.4f}j  +  {drz:.4f}k')
                        print(f'  |Δr⃗|  =  {Physics_3D.MagnitudeXYZ(drx, dry, drz):.4f} m')
                    case 2:
                        print('  Enter the INITIAL position vector  (r_i):')
                        rix = _ask('    r_ix  (i): ', cast=float)
                        riy = _ask('    r_iy  (j): ', cast=float)
                        riz = _ask('    r_iz  (k): ', cast=float)
                        print('  Enter the DISPLACEMENT vector  (Δr):')
                        drx = _ask('    Δrx  (i): ', cast=float)
                        dry = _ask('    Δry  (j): ', cast=float)
                        drz = _ask('    Δrz  (k): ', cast=float)
                        rfx, rfy, rfz = Physics_3D.FinalPositionXYZ(rix, riy, riz, drx, dry, drz)
                        print(f'\n  r⃗_f  =  r⃗_i + Δr⃗  =  {rfx:.4f}i  +  {rfy:.4f}j  +  {rfz:.4f}k')
                    case 3:
                        print('  Enter the FINAL position vector  (r_f):')
                        rfx = _ask('    r_fx  (i): ', cast=float)
                        rfy = _ask('    r_fy  (j): ', cast=float)
                        rfz = _ask('    r_fz  (k): ', cast=float)
                        print('  Enter the DISPLACEMENT vector  (Δr):')
                        drx = _ask('    Δrx  (i): ', cast=float)
                        dry = _ask('    Δry  (j): ', cast=float)
                        drz = _ask('    Δrz  (k): ', cast=float)
                        rix, riy, riz = Physics_3D.InitialPositionXYZ(rfx, rfy, rfz, drx, dry, drz)
                        print(f'\n  r⃗_i  =  r⃗_f − Δr⃗  =  {rix:.4f}i  +  {riy:.4f}j  +  {riz:.4f}k')
                    case _:
                        print('\n  That was not a valid option.')
                        continue
                print()

            elif sec == 3:
                # Newton's 2nd Law — 3D component form
                print()
                print('  Enter each force as  Fx  Fy  Fz  components.')
                print('  Leave Fx blank when done.')
                print()
                forces = []
                f_num  = 1
                while True:
                    raw = input(f'  Force {f_num}  Fx (i): ').strip()
                    if not raw:
                        break
                    fx = float(raw)
                    fy = float(input(f'  Force {f_num}  Fy (j): '))
                    fz = float(input(f'  Force {f_num}  Fz (k): '))
                    forces.append((fx, fy, fz))
                    f_num += 1
                if not forces:
                    print('\n  Enter at least one force.')
                    print()
                    continue
                print()
                print(f'  {len(forces)} force(s) entered:')
                for i, (fx, fy, fz) in enumerate(forces, 1):
                    print(f'    F{i} = {fx}i  +  {fy}j  +  {fz}k  N')
                print()
                if choice in (2, 3):
                    mass = _ask('  Mass (kg): ', cast=float)
                    print()
                match choice:
                    case 1:
                        fx, fy, fz = Physics_3D.NetForce3D(forces)
                        mag = (fx**2+fy**2+fz**2)**0.5
                        print(f'  F⃗_net  =  {fx:.4f}i  +  {fy:.4f}j  +  {fz:.4f}k  N')
                        print(f'  |F⃗_net| = {mag:.4f} N')
                    case 2:
                        ax, ay, az = Physics_3D.Acceleration3DFromForces(forces, mass)
                        print(f'  a⃗  =  {ax:.4f}i  +  {ay:.4f}j  +  {az:.4f}k  m/s²')
                    case 3:
                        a_mag = Physics_3D.AccelerationMagnitude3D(forces, mass)
                        ax, ay, az = Physics_3D.Acceleration3DFromForces(forces, mass)
                        print(f'  a⃗      =  {ax:.4f}i  +  {ay:.4f}j  +  {az:.4f}k  m/s²')
                        print(f'  |a⃗|    =  {a_mag:.4f} m/s²')
                    case 4:
                        mag, theta, phi = Physics_3D.NetForcePolar3D(forces)
                        fx, fy, fz = Physics_3D.NetForce3D(forces)
                        print(f'  F⃗_net  =  {fx:.4f}i  +  {fy:.4f}j  +  {fz:.4f}k  N')
                        print(f'  |F⃗_net| = {mag:.4f} N  |  θ = {theta:.2f}°  |  φ = {phi:.2f}°')
                    case _:
                        print('\n  That was not a valid option.')
                        continue
                print()

# ============================================================
# FORCES 2D DEBUG
# ============================================================

def Forces2DDebug():
    _SectionHeader('Forces 2D', 'Step 1 of 3 — Describe the object')
    print('  Enter the properties of the object the forces will act on.')
    print()
    mass     = _ask('  Mass of the object (kg): ', cast=float)
    g        = _ask('  Gravity (m/s², Enter = 9.8): ', cast=float)
    velocity = _ask('  Current velocity (m/s): ', cast=float)
    height   = _ask('  Current height above ground (m): ', cast=float)
    obj          = Forces.Forces2D(mass, float(g))
    obj.velocity = velocity
    obj.height   = height
    print()
    print(f"  Object ready — {mass} kg, gravity {obj.g} m/s², normal force {obj.normal:.3f} N")
    print()
    print('  Is the object on an inclined surface?')
    print('  (1)  Yes — set the incline angle')
    print('  (2)  No — flat surface')
    print()
    if _ask('  Enter a number to choose: ', cast=int) == 1:
        angle = _ask('  Incline angle (degrees): ', cast=float)
        obj.SetIncline(angle)
        print()
        print(f"  Incline set to {angle}° — normal force updated to {obj.normal:.3f} N")
    print()
    _SectionHeader('Forces 2D', 'Step 2 of 3 — Add Forces')
    print('  Should gravity act on this object as a downward force?')
    print('  (1)  Yes — add Fg = mg downward')
    print('  (2)  No — I will manage forces manually')
    print()
    force_count = 0
    if _ask('  Enter a number to choose: ', cast=int) == 1:
        obj.ApplyGravity()
        force_count = 1
        print()
        print(f"  Gravity applied — {obj.mass * obj.g:.3f} N downward.")
    print()
    adding = True
    while adding:
        print(f"  Force #{force_count + 1} — how would you like to enter it?")
        print('  (1)  By X and Y components')
        print('  (2)  By total strength and direction angle')
        print('  (3)  Done adding forces')
        print()
        fc = _ask('  Enter a number to choose: ', cast=int)
        match fc:
            case 1:
                x     = _ask('  Force X (N, negative = left): ', cast=float)
                y     = _ask('  Force Y (N, negative = down): ', cast=float)
                force = Forces.Force2D(x, y)
                obj.forces.append(force)
                force_count += 1
                print()
                print(f"  Added — {force.magnitude:.3f} N at {force.angle:.1f}°")
                print()
            case 2:
                magnitude = _ask('  Total strength (N): ', cast=float)
                angle     = _ask('  Direction (degrees, 0 = right): ', cast=float)
                force     = Forces.Force2D(0, 0, angle, magnitude)
                obj.forces.append(force)
                force_count += 1
                print()
                print(f"  Added — {magnitude} N at {angle}°")
                print()
            case 3:
                adding = False
            case _:
                print('\n  That was not a valid option.')
                print()
    print(f"  {force_count} force(s) loaded.")
    print()
    QUERY_SECTIONS = [
        'Energy & Momentum',
        'Forces & Equilibrium',
        'Drag & Terminal Velocity',
    ]
    while True:
        _SectionHeader('Forces 2D', 'Step 3 of 3 — Query the System')
        for i, s in enumerate(QUERY_SECTIONS, 1):
            print(f"  ({i})  {s}")
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(QUERY_SECTIONS):
            print('\n  That was not a valid section.')
            continue
        while True:
            _SectionHeader('Forces 2D', QUERY_SECTIONS[sec - 1])
            if sec == 1:
                print('  (1)  Momentum')
                print('  (2)  Kinetic energy')
                print('  (3)  Potential energy')
                print('  (4)  Total mechanical energy  (KE + PE)')
                print('  (5)  Impulse over a time interval')
                print('  (6)  Update velocity over a time step')
            elif sec == 2:
                print('  (1)  Net force on the object')
                print('  (2)  Net acceleration')
                print('  (3)  Normal force')
                print('  (4)  Is the object in static equilibrium?')
                print('  (5)  Is the object in dynamic equilibrium?')
            elif sec == 3:
                print('  (1)  Terminal velocity')
                print('  (2)  Drag force at current velocity')
                print('  (3)  Has the object reached terminal velocity?')
            print()
            _ExitBar('Return to sections')
            print()
            query = _ask('  Select a query: ', cast=int)
            if query == 0: break
            if sec == 1:
                match query:
                    case 1:
                        result = obj.NetMomentum()
                        print()
                        print(f"  Momentum: {result:.3f} kg·m/s")
                    case 2:
                        result = obj.NetKineticEnergy()
                        print()
                        print(f"  Kinetic Energy: {result:.3f} J")
                    case 3:
                        result = obj.NetPotentialEnergy()
                        print()
                        print(f"  Potential Energy: {result:.3f} J")
                    case 4:
                        result = obj.NetMechanicalEnergy()
                        print()
                        print(f"  Total Mechanical Energy: {result:.3f} J")
                    case 5:
                        print()
                        time   = _ask('  Over how many seconds? ', cast=float)
                        result = obj.NetImpulse(time)
                        print()
                        print(f"  Impulse over {time}s: {result:.3f} N·s")
                    case 6:
                        print()
                        time = _ask('  Advance by how many seconds? ', cast=float)
                        obj.UpdateVelocity(time)
                        print()
                        print(f"  Velocity is now: {obj.velocity:.3f} m/s")
                    case _:
                        print('\n  That was not a valid option.')
                        continue
            elif sec == 2:
                match query:
                    case 1:
                        net = obj.NetForce()
                        print()
                        print('  Net Force:')
                        print(f"    X component    : {net.x:.3f} N")
                        print(f"    Y component    : {net.y:.3f} N")
                        print(f"    Total strength : {net.magnitude:.3f} N")
                        print(f"    Direction      : {net.angle:.1f} degrees")
                    case 2:
                        result = obj.NetAcceleration()
                        print()
                        print(f"  Net Acceleration: {result:.3f} m/s²")
                    case 3:
                        print()
                        print(f"  Normal Force: {obj.normal:.3f} N")
                    case 4:
                        result = obj.IsStaticEquilibrium()
                        print()
                        if result:
                            print('  Yes — net force is zero and the object is not moving.')
                        else:
                            net = obj.NetForce()
                            print(f"  No — net force {net.magnitude:.3f} N, velocity {obj.velocity:.3f} m/s.")
                    case 5:
                        result = obj.IsDynamicEquilibrium()
                        print()
                        if result:
                            print('  Yes — net force is zero and the object is moving at constant velocity.')
                        else:
                            net = obj.NetForce()
                            print(f"  No — net force {net.magnitude:.3f} N, velocity {obj.velocity:.3f} m/s.")
                    case _:
                        print('\n  That was not a valid option.')
                        continue
            elif sec == 3:
                area             = _ask('  Cross-sectional area (m²): ', cast=float)
                drag_coefficient = _ask('  Drag coefficient (e.g. 0.47 for a sphere): ', cast=float)
                fluid_density    = _ask('  Fluid density (kg/m³, Enter = 1.225): ', cast=float)
                match query:
                    case 1:
                        result = Forces.TerminalVelocity(obj.mass, area, drag_coefficient, float(fluid_density), obj.g)
                        print()
                        print(f"  Terminal Velocity: {result:.3f} m/s")
                    case 2:
                        result = Forces.DragForce(obj.velocity, area, drag_coefficient, float(fluid_density))
                        print()
                        print(f"  Drag Force at {obj.velocity:.3f} m/s: {result:.3f} N")
                    case 3:
                        result = Forces.IsAtTerminalVelocity(obj.velocity, obj.mass, area, drag_coefficient, float(fluid_density), obj.g)
                        vt     = Forces.TerminalVelocity(obj.mass, area, drag_coefficient, float(fluid_density), obj.g)
                        print()
                        if result:
                            print(f"  Yes — at terminal velocity ({vt:.3f} m/s).")
                        else:
                            print(f"  No — current {obj.velocity:.3f} m/s, terminal {vt:.3f} m/s.")
                    case _:
                        print('\n  That was not a valid option.')
                        continue
            print()

# ============================================================
# FORCES 3D DEBUG
# ============================================================

def Forces3DDebug():
    _SectionHeader('Forces 3D', 'Step 1 of 3 — Describe the object')
    print('  Enter the properties of the object the forces will act on.')
    print()
    mass     = _ask('  Mass of the object (kg): ', cast=float)
    g        = _ask('  Gravity (m/s², Enter = 9.8): ', cast=float)
    velocity = _ask('  Current velocity (m/s): ', cast=float)
    height   = _ask('  Current height above ground (m): ', cast=float)
    obj          = Forces.Forces3D(mass, float(g))
    obj.velocity = velocity
    obj.height   = height
    print()
    print(f"  Object ready — {mass} kg, gravity {obj.g} m/s², normal force {obj.normal:.3f} N")
    print()
    print('  Is the object on an inclined surface?')
    print('  (1)  Yes — set the incline angle')
    print('  (2)  No — flat surface')
    print()
    if _ask('  Enter a number to choose: ', cast=int) == 1:
        angle = _ask('  Incline angle (degrees): ', cast=float)
        obj.SetIncline(angle)
        print()
        print(f"  Incline set to {angle}° — normal force updated to {obj.normal:.3f} N")
    print()
    _SectionHeader('Forces 3D', 'Step 2 of 3 — Add Forces')
    print('  Should gravity act on this object as a downward force?')
    print('  (1)  Yes — add Fg = mg downward')
    print('  (2)  No — I will manage forces manually')
    print()
    force_count = 0
    if _ask('  Enter a number to choose: ', cast=int) == 1:
        obj.ApplyGravity()
        force_count = 1
        print()
        print(f"  Gravity applied — {obj.mass * obj.g:.3f} N downward.")
    print()
    adding = True
    while adding:
        print(f"  Force #{force_count + 1} — how would you like to enter it?")
        print('  (1)  By X, Y, and Z components')
        print('  (2)  By total strength, horizontal angle, vertical angle')
        print('  (3)  Done adding forces')
        print()
        fc = _ask('  Enter a number to choose: ', cast=int)
        match fc:
            case 1:
                x     = _ask('  Force X (N): ', cast=float)
                y     = _ask('  Force Y (N): ', cast=float)
                z     = _ask('  Force Z (N): ', cast=float)
                force = Forces.Force3D(x, y, z)
                obj.forces.append(force)
                force_count += 1
                print()
                print(f"  Added — {force.magnitude:.3f} N, angle {force.angle:.1f}°, phi {force.phi:.1f}°")
                print()
            case 2:
                magnitude = _ask('  Total strength (N): ', cast=float)
                angle     = _ask('  Horizontal direction (degrees, 0 = forward): ', cast=float)
                phi       = _ask('  Vertical angle (degrees, 0 = flat, 90 = up): ', cast=float)
                force     = Forces.Force3D(0, 0, 0, angle, phi, magnitude)
                obj.forces.append(force)
                force_count += 1
                print()
                print(f"  Added — {magnitude} N at {angle}° horizontal, {phi}° vertical")
                print()
            case 3:
                adding = False
            case _:
                print('\n  That was not a valid option.')
                print()
    print(f"  {force_count} force(s) loaded.")
    print()
    QUERY_SECTIONS = [
        'Energy & Momentum',
        'Forces & Equilibrium',
        'Drag & Terminal Velocity',
    ]
    while True:
        _SectionHeader('Forces 3D', 'Step 3 of 3 — Query the System')
        for i, s in enumerate(QUERY_SECTIONS, 1):
            print(f"  ({i})  {s}")
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(QUERY_SECTIONS):
            print('\n  That was not a valid section.')
            continue
        while True:
            _SectionHeader('Forces 3D', QUERY_SECTIONS[sec - 1])
            if sec == 1:
                print('  (1)  Momentum')
                print('  (2)  Kinetic energy')
                print('  (3)  Potential energy')
                print('  (4)  Total mechanical energy  (KE + PE)')
                print('  (5)  Impulse over a time interval')
                print('  (6)  Update velocity over a time step')
            elif sec == 2:
                print('  (1)  Net force on the object')
                print('  (2)  Net acceleration')
                print('  (3)  Normal force')
                print('  (4)  Is the object in static equilibrium?')
                print('  (5)  Is the object in dynamic equilibrium?')
            elif sec == 3:
                print('  (1)  Terminal velocity')
                print('  (2)  Drag force at current velocity')
                print('  (3)  Has the object reached terminal velocity?')
            print()
            _ExitBar('Return to sections')
            print()
            query = _ask('  Select a query: ', cast=int)
            if query == 0: break
            if sec == 1:
                match query:
                    case 1:
                        result = obj.NetMomentum()
                        print()
                        print(f"  Momentum: {result:.3f} kg·m/s")
                    case 2:
                        result = obj.NetKineticEnergy()
                        print()
                        print(f"  Kinetic Energy: {result:.3f} J")
                    case 3:
                        result = obj.NetPotentialEnergy()
                        print()
                        print(f"  Potential Energy: {result:.3f} J")
                    case 4:
                        result = obj.NetMechanicalEnergy()
                        print()
                        print(f"  Total Mechanical Energy: {result:.3f} J")
                    case 5:
                        print()
                        time   = _ask('  Over how many seconds? ', cast=float)
                        result = obj.NetImpulse(time)
                        print()
                        print(f"  Impulse over {time}s: {result:.3f} N·s")
                    case 6:
                        print()
                        time = _ask('  Advance by how many seconds? ', cast=float)
                        obj.UpdateVelocity(time)
                        print()
                        print(f"  Velocity is now: {obj.velocity:.3f} m/s")
                    case _:
                        print('\n  That was not a valid option.')
                        continue
            elif sec == 2:
                match query:
                    case 1:
                        net = obj.NetForce()
                        print()
                        print('  Net Force:')
                        print(f"    X component    : {net.x:.3f} N")
                        print(f"    Y component    : {net.y:.3f} N")
                        print(f"    Z component    : {net.z:.3f} N")
                        print(f"    Total strength : {net.magnitude:.3f} N")
                        print(f"    Horizontal dir : {net.angle:.1f} degrees")
                        print(f"    Vertical angle : {net.phi:.1f} degrees")
                    case 2:
                        result = obj.NetAcceleration()
                        print()
                        print(f"  Net Acceleration: {result:.3f} m/s²")
                    case 3:
                        print()
                        print(f"  Normal Force: {obj.normal:.3f} N")
                    case 4:
                        result = obj.IsStaticEquilibrium()
                        print()
                        if result:
                            print('  Yes — net force is zero and the object is not moving.')
                        else:
                            net = obj.NetForce()
                            print(f"  No — net force {net.magnitude:.3f} N, velocity {obj.velocity:.3f} m/s.")
                    case 5:
                        result = obj.IsDynamicEquilibrium()
                        print()
                        if result:
                            print('  Yes — net force is zero and the object is moving at constant velocity.')
                        else:
                            net = obj.NetForce()
                            print(f"  No — net force {net.magnitude:.3f} N, velocity {obj.velocity:.3f} m/s.")
                    case _:
                        print('\n  That was not a valid option.')
                        continue
            elif sec == 3:
                area             = _ask('  Cross-sectional area (m²): ', cast=float)
                drag_coefficient = _ask('  Drag coefficient (e.g. 0.47 for a sphere): ', cast=float)
                fluid_density    = _ask('  Fluid density (kg/m³, Enter = 1.225): ', cast=float)
                match query:
                    case 1:
                        result = Forces.TerminalVelocity(obj.mass, area, drag_coefficient, float(fluid_density), obj.g)
                        print()
                        print(f"  Terminal Velocity: {result:.3f} m/s")
                    case 2:
                        result = Forces.DragForce(obj.velocity, area, drag_coefficient, float(fluid_density))
                        print()
                        print(f"  Drag Force at {obj.velocity:.3f} m/s: {result:.3f} N")
                    case 3:
                        result = Forces.IsAtTerminalVelocity(obj.velocity, obj.mass, area, drag_coefficient, float(fluid_density), obj.g)
                        vt     = Forces.TerminalVelocity(obj.mass, area, drag_coefficient, float(fluid_density), obj.g)
                        print()
                        if result:
                            print(f"  Yes — at terminal velocity ({vt:.3f} m/s).")
                        else:
                            print(f"  No — current {obj.velocity:.3f} m/s, terminal {vt:.3f} m/s.")
                    case _:
                        print('\n  That was not a valid option.')
                        continue
            print()

# ============================================================
# ALGEBRA DEBUG
# ============================================================

def AlgebraDebug():
    SECTIONS = [
        'Linear Equations',
        'Quadratic Equations',
        'Polynomials',
        'Exponents & Logarithms',
        'Ratios & Proportions',
        'Sequences & Series',
        'Factoring & Number Theory',
        'Systems of Equations',
        'Functions',
    ]
    while True:
        _SectionHeader('Algebra', 'Choose a section')
        for i, s in enumerate(SECTIONS, 1):
            print(f"  ({i})  {s}")
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section.')
            continue
        while True:
            _SectionHeader('Algebra', SECTIONS[sec - 1])
            if sec == 1:
                print('  (1)  y = mx + b  — evaluate a line at x')
                print('  (2)  Slope between two points')
                print('  (3)  Y-intercept from slope and a point')
                print('  (4)  Solve for x  given y  (linear)')
                print('  (5)  Intersection of two lines')
            elif sec == 2:
                print('  (1)  Evaluate quadratic  y = ax² + bx + c')
                print('  (2)  Discriminant  b² - 4ac')
                print('  (3)  Roots of a quadratic')
                print('  (4)  Vertex of a parabola')
            elif sec == 3:
                print('  (1)  Evaluate a polynomial at x')
                print('  (2)  Check if x is a root')
            elif sec == 4:
                print('  (1)  base ^ exponent')
                print('  (2)  Nth root of a value')
                print('  (3)  Logarithm in any base  log_b(x)')
                print('  (4)  Natural logarithm  ln(x)')
                print('  (5)  e^x')
            elif sec == 5:
                print('  (1)  Ratio  a / b')
                print('  (2)  Solve a proportion  a/b = x/d')
                print('  (3)  Percentage  part / whole × 100')
                print('  (4)  Percentage of a value')
                print('  (5)  Percentage change between two values')
            elif sec == 6:
                print('  (1)  Nth term of an arithmetic sequence')
                print('  (2)  Sum of first n arithmetic terms')
                print('  (3)  Nth term of a geometric sequence')
                print('  (4)  Sum of first n geometric terms')
                print('  (5)  Infinite geometric series sum')
            elif sec == 7:
                print('  (1)  GCD of two integers')
                print('  (2)  LCM of two integers')
                print('  (3)  Check if a is divisible by b')
                print('  (4)  Check if n is prime')
                print('  (5)  Prime factors of n')
            elif sec == 8:
                print('  (1)  Solve 2×2 linear system  (Cramers rule)')
                print('  (2)  Solve two lines in slope-intercept form')
            elif sec == 9:
                print('  (1)  Average rate of change of a function')
                print('  (2)  Solve a linear inequality  ax + b < c')
            print()
            _ExitBar('Return to sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            if sec == 1:
                match choice:
                    case 1:
                        m = float(input('  Slope (m): '))
                        x = float(input('  x value: '))
                        b = float(input('  Y-intercept (b): '))
                        print(f"\n  y = {Algebra.Linear(m, x, b):.6f}")
                    case 2:
                        x1, y1 = float(input('  x1: ')), float(input('  y1: '))
                        x2, y2 = float(input('  x2: ')), float(input('  y2: '))
                        print(f"\n  Slope: {Algebra.Slope(x1, y1, x2, y2):.6f}")
                    case 3:
                        m = float(input('  Slope (m): '))
                        x = float(input('  x of the point: '))
                        y = float(input('  y of the point: '))
                        print(f"\n  Y-intercept: {Algebra.YIntercept(m, x, y):.6f}")
                    case 4:
                        m = float(input('  Slope (m): '))
                        b = float(input('  Y-intercept (b): '))
                        y = float(input('  Target y value: '))
                        print(f"\n  x = {Algebra.SolveLinearForX(m, b, y):.6f}")
                    case 5:
                        print('  Line 1:')
                        m1, b1 = float(input('    Slope m1: ')), float(input('    Intercept b1: '))
                        print('  Line 2:')
                        m2, b2 = float(input('    Slope m2: ')), float(input('    Intercept b2: '))
                        x, y   = Algebra.LineIntersectionX(m1, b1, m2, b2), Algebra.LineIntersectionY(m1, b1, m2, b2)
                        print(f"\n  Intersection: x = {x:.6f},  y = {y:.6f}")
                    case _:
                        print('\n  That was not a valid option.')
            elif sec == 2:
                match choice:
                    case 1:
                        a, b, c = float(input('  a: ')), float(input('  b: ')), float(input('  c: '))
                        x       = float(input('  x value: '))
                        print(f"\n  y = {Algebra.Quadratic(a, b, c, x):.6f}")
                    case 2:
                        a, b, c = float(input('  a: ')), float(input('  b: ')), float(input('  c: '))
                        d       = Algebra.Discriminant(a, b, c)
                        nature  = 'two real roots' if d > 0 else ('one real root' if d == 0 else 'two complex roots')
                        print(f"\n  Discriminant: {d:.6f}  →  {nature}")
                    case 3:
                        a, b, c  = float(input('  a: ')), float(input('  b: ')), float(input('  c: '))
                        x1, x2   = Algebra.QuadraticRoots(a, b, c)
                        print(f"\n  Root 1: {x1}")
                        print(f"  Root 2: {x2}")
                    case 4:
                        a, b, c = float(input('  a: ')), float(input('  b: ')), float(input('  c: '))
                        vx, vy  = Algebra.VertexX(a, b), Algebra.VertexY(a, b, c)
                        print(f"\n  Vertex: ({vx:.6f}, {vy:.6f})")
                    case _:
                        print('\n  That was not a valid option.')
            elif sec == 3:
                match choice:
                    case 1:
                        print('  Enter coefficients highest-degree first (blank line to finish).')
                        coefficients = []
                        while True:
                            entry = input('  Coefficient: ')
                            if entry == '': break
                            coefficients.append(float(entry))
                        x = float(input('  x value: '))
                        print(f"\n  p({x}) = {Algebra.EvaluatePolynomial(coefficients, x):.6f}")
                    case 2:
                        print('  Enter coefficients highest-degree first (blank line to finish).')
                        coefficients = []
                        while True:
                            entry = input('  Coefficient: ')
                            if entry == '': break
                            coefficients.append(float(entry))
                        x = float(input('  x value to test: '))
                        result = Algebra.IsRoot(coefficients, x)
                        print(f"\n  Is x = {x} a root?  {'Yes' if result else 'No'}")
                    case _:
                        print('\n  That was not a valid option.')
            elif sec == 4:
                match choice:
                    case 1:
                        base, exp = float(input('  Base: ')), float(input('  Exponent: '))
                        print(f"\n  {base} ^ {exp} = {Algebra.Power(base, exp):.6f}")
                    case 2:
                        value, n = float(input('  Value: ')), float(input('  Root (2 = square, 3 = cube): '))
                        print(f"\n  {n}th root of {value} = {Algebra.NthRoot(value, n):.6f}")
                    case 3:
                        x, base = float(input('  x: ')), float(input('  Base: '))
                        print(f"\n  log_{base}({x}) = {Algebra.LogBase(x, base):.6f}")
                    case 4:
                        x = float(input('  x: '))
                        print(f"\n  ln({x}) = {Algebra.NaturalLog(x):.6f}")
                    case 5:
                        x = float(input('  x: '))
                        print(f"\n  e^{x} = {Algebra.Exponential(x):.6f}")
                    case _:
                        print('\n  That was not a valid option.')
            elif sec == 5:
                match choice:
                    case 1:
                        a, b = float(input('  a: ')), float(input('  b: '))
                        print(f"\n  Ratio a/b = {Algebra.Ratio(a, b):.6f}")
                    case 2:
                        a, b, d = float(input('  a: ')), float(input('  b: ')), float(input('  d: '))
                        print(f"\n  x = {Algebra.SolveProportion(a, b, d):.6f}")
                    case 3:
                        part, whole = float(input('  Part: ')), float(input('  Whole: '))
                        print(f"\n  {part} is {Algebra.Percentage(part, whole):.4f}% of {whole}")
                    case 4:
                        percent, whole = float(input('  Percentage: ')), float(input('  Whole: '))
                        print(f"\n  {percent}% of {whole} = {Algebra.PercentageOf(percent, whole):.6f}")
                    case 5:
                        old, new = float(input('  Old value: ')), float(input('  New value: '))
                        print(f"\n  Percentage change: {Algebra.PercentageChange(old, new):.4f}%")
                    case _:
                        print('\n  That was not a valid option.')
            elif sec == 6:
                match choice:
                    case 1:
                        a1, d, n = float(input('  First term a1: ')), float(input('  Common difference d: ')), int(input('  Which term n: '))
                        print(f"\n  Term {n} = {Algebra.ArithmeticTerm(a1, d, n):.6f}")
                    case 2:
                        a1, d, n = float(input('  First term a1: ')), float(input('  Common difference d: ')), int(input('  Number of terms n: '))
                        print(f"\n  Sum of first {n} terms = {Algebra.ArithmeticSum(a1, d, n):.6f}")
                    case 3:
                        a1, r, n = float(input('  First term a1: ')), float(input('  Common ratio r: ')), int(input('  Which term n: '))
                        print(f"\n  Term {n} = {Algebra.GeometricTerm(a1, r, n):.6f}")
                    case 4:
                        a1, r, n = float(input('  First term a1: ')), float(input('  Common ratio r: ')), int(input('  Number of terms n: '))
                        print(f"\n  Sum of first {n} terms = {Algebra.GeometricSum(a1, r, n):.6f}")
                    case 5:
                        a1, r = float(input('  First term a1: ')), float(input('  Common ratio r (|r| < 1): '))
                        result = Algebra.InfiniteGeometricSum(a1, r)
                        if result == 0 and abs(r) >= 1:
                            print('\n  Series diverges — |r| must be less than 1.')
                        else:
                            print(f"\n  Infinite sum = {result:.6f}")
                    case _:
                        print('\n  That was not a valid option.')
            elif sec == 7:
                match choice:
                    case 1:
                        a, b = int(float(input('  a: '))), int(float(input('  b: ')))
                        print(f"\n  Algebra.GCD({a}, {b}) = {Algebra.GCD(a, b)}")
                    case 2:
                        a, b = int(float(input('  a: '))), int(float(input('  b: ')))
                        print(f"\n  Algebra.LCM({a}, {b}) = {Algebra.LCM(a, b)}")
                    case 3:
                        a, b   = int(float(input('  a: '))), int(float(input('  b: ')))
                        result = Algebra.IsDivisible(a, b)
                        print(f"\n  Is {a} divisible by {b}?  {'Yes' if result else 'No'}")
                    case 4:
                        n      = int(float(input('  n: ')))
                        result = Algebra.IsPrime(n)
                        print(f"\n  Is {n} prime?  {'Yes' if result else 'No'}")
                    case 5:
                        n       = int(float(input('  n: ')))
                        factors = Algebra.PrimeFactors(n)
                        print(f"\n  Prime factors of {n}: {factors}")
                    case _:
                        print('\n  That was not a valid option.')
            elif sec == 8:
                match choice:
                    case 1:
                        print('  Equation 1: a1·x + b1·y = c1')
                        a1, b1, c1 = float(input('    a1: ')), float(input('    b1: ')), float(input('    c1: '))
                        print('  Equation 2: a2·x + b2·y = c2')
                        a2, b2, c2 = float(input('    a2: ')), float(input('    b2: ')), float(input('    c2: '))
                        x, y = Algebra.SolveSystem2x2(a1, b1, c1, a2, b2, c2)
                        if x == 0 and y == 0:
                            print('\n  No unique solution — lines are parallel or identical.')
                        else:
                            print(f"\n  x = {x:.6f},  y = {y:.6f}")
                    case 2:
                        print('  Line 1: y = m1·x + b1')
                        m1, b1 = float(input('    m1: ')), float(input('    b1: '))
                        print('  Line 2: y = m2·x + b2')
                        m2, b2 = float(input('    m2: ')), float(input('    b2: '))
                        x, y   = Algebra.SolveSlopeIntercept(m1, b1, m2, b2)
                        print(f"\n  Intersection: x = {x:.6f},  y = {y:.6f}")
                    case _:
                        print('\n  That was not a valid option.')
            elif sec == 9:
                match choice:
                    case 1:
                        print('  Enter a function using x, e.g. x**2 + 3*x + 1')
                        expr = input('  f(x) = ')
                        f    = lambda x: eval(expr, {'x': x, 'math': math})
                        x1, x2 = float(input('  x1: ')), float(input('  x2: '))
                        print(f"\n  Average rate of change from {x1} to {x2}: {Algebra.AverageRateOfChange(f, x1, x2):.6f}")
                    case 2:
                        print('  Solving: a·x + b < c  (or >, <=, >=)')
                        a      = float(input('  a: '))
                        b      = float(input('  b: '))
                        c      = float(input('  c: '))
                        symbol = input('  Inequality symbol (< > <= >=, Enter = <): ') or '<'
                        boundary, inequality_str = Algebra.SolveLinearInequality(a, b, c, symbol)
                        print(f"\n  Solution: {inequality_str}")
                    case _:
                        print('\n  That was not a valid option.')
            print()

# ============================================================
# GEOMETRY DEBUG
# ============================================================

def GeometryDebug():
    SECTIONS = [
        'Points & Distance',
        'Angles',
        'Triangles',
        'Quadrilaterals',
        'Circles',
        'Polygons',
        '3D Solids',
        'Coordinate Geometry',
        'Vectors  (2D & 3D)',
    ]
    while True:
        _SectionHeader('Geometry', 'Choose a section')
        for i, s in enumerate(SECTIONS, 1):
            print(f"  ({i})  {s}")
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section.')
            continue
        while True:
            _SectionHeader('Geometry', SECTIONS[sec - 1])
            if sec == 1:
                print('  (1)  Distance between two 2D points')
                print('  (2)  Distance between two 3D points')
                print('  (3)  Midpoint between two 2D points')
                print('  (4)  Midpoint between two 3D points')
                print('  (5)  Manhattan distance')
            elif sec == 2:
                print('  (1)  Convert degrees to radians')
                print('  (2)  Convert radians to degrees')
                print('  (3)  Supplementary angle  180 - θ')
                print('  (4)  Complementary angle  90 - θ')
                print('  (5)  Check if three angles form a valid triangle')
            elif sec == 3:
                print('  (1)  Area  (base and height)')
                print('  (2)  Area  (Herons formula — three sides)')
                print('  (3)  Perimeter')
                print('  (4)  Hypotenuse  (Pythagorean theorem)')
                print('  (5)  Missing leg  (Pythagorean theorem)')
                print('  (6)  Check if three sides form a right triangle')
                print('  (7)  Law of Cosines — find missing side')
                print('  (8)  Law of Cosines — find missing angle')
                print('  (9)  Law of Sines — find missing side')
                print('  (10) Law of Sines — find missing angle')
            elif sec == 4:
                print('  (1)  Rectangle area and perimeter')
                print('  (2)  Square area, perimeter, and diagonal')
                print('  (3)  Parallelogram area')
                print('  (4)  Trapezoid area')
                print('  (5)  Rhombus area  (from diagonals)')
            elif sec == 5:
                print('  (1)  Circle area and circumference')
                print('  (2)  Arc length')
                print('  (3)  Sector area')
                print('  (4)  Chord length')
            elif sec == 6:
                print('  (1)  Interior angle sum of a polygon')
                print('  (2)  Interior and exterior angles of a regular polygon')
                print('  (3)  Area of a regular polygon')
                print('  (4)  Number of diagonals')
            elif sec == 7:
                print('  (1)  Box — surface area and volume')
                print('  (2)  Cube — surface area and volume')
                print('  (3)  Cylinder — surface area and volume')
                print('  (4)  Cone — surface area and volume')
                print('  (5)  Sphere — surface area and volume')
                print('  (6)  Pyramid volume')
            elif sec == 8:
                print('  (1)  Check if a point lies on a line')
                print('  (2)  Perpendicular slope')
                print('  (3)  Check if two lines are parallel')
                print('  (4)  Check if two lines are perpendicular')
                print('  (5)  Line equation from a point and slope')
                print('  (6)  Check if three points are collinear')
            elif sec == 9:
                _p('Vector operations in 2D and 3D space — choose a dimension inside.')
                print()
            print()
            _ExitBar('Return to sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            if sec == 1:
                match choice:
                    case 1:
                        x1, y1 = float(input('  x1: ')), float(input('  y1: '))
                        x2, y2 = float(input('  x2: ')), float(input('  y2: '))
                        print(f"\n  Distance: {Geometry.Distance2D(x1, y1, x2, y2):.6f}")
                    case 2:
                        x1,y1,z1 = float(input('  x1: ')),float(input('  y1: ')),float(input('  z1: '))
                        x2,y2,z2 = float(input('  x2: ')),float(input('  y2: ')),float(input('  z2: '))
                        print(f"\n  Distance: {Geometry.Distance3D(x1, y1, z1, x2, y2, z2):.6f}")
                    case 3:
                        x1, y1 = float(input('  x1: ')), float(input('  y1: '))
                        x2, y2 = float(input('  x2: ')), float(input('  y2: '))
                        mx, my = Geometry.Midpoint2D(x1, y1, x2, y2)
                        print(f"\n  Midpoint: ({mx:.6f}, {my:.6f})")
                    case 4:
                        x1,y1,z1 = float(input('  x1: ')),float(input('  y1: ')),float(input('  z1: '))
                        x2,y2,z2 = float(input('  x2: ')),float(input('  y2: ')),float(input('  z2: '))
                        mx,my,mz = Geometry.Midpoint3D(x1,y1,z1,x2,y2,z2)
                        print(f"\n  Midpoint: ({mx:.6f}, {my:.6f}, {mz:.6f})")
                    case 5:
                        x1, y1 = float(input('  x1: ')), float(input('  y1: '))
                        x2, y2 = float(input('  x2: ')), float(input('  y2: '))
                        print(f"\n  Manhattan Distance: {Geometry.ManhattanDistance(x1, y1, x2, y2):.6f}")
                    case _:
                        print('\n  That was not a valid option.')
            elif sec == 2:
                match choice:
                    case 1:
                        deg = float(input('  Degrees: '))

                        print(f"\n  Radians: {Geometry.ToRadians(deg):.6f}")

                    case 2:
                        rad = float(input('  Radians: '))

                        print(f"\n  Degrees: {Geometry.ToDegrees(rad):.6f}")

                    case 3:
                        deg = float(input('  Angle (degrees): '))

                        print(f"\n  Supplementary: {Geometry.SupplementaryAngle(deg):.6f}°")

                    case 4:
                        deg = float(input('  Angle (degrees): '))

                        print(f"\n  Complementary: {Geometry.ComplementaryAngle(deg):.6f}°")

                    case 5:
                        a, b, c = float(input('  Angle A: ')), float(input('  Angle B: ')), float(input('  Angle C: '))
                        result  = Geometry.IsValidTriangleAngles(a, b, c)
                        print(f"\n  Valid triangle?  {'Yes' if result else 'No — angles do not sum to 180°'}")
                    case _:
                        print('\n  That was not a valid option.')
            elif sec == 3:
                match choice:
                    case 1:
                        base, h = float(input('  Base: ')), float(input('  Height: '))

                        print(f"\n  Area: {Geometry.TriangleArea(base, h):.6f}")

                    case 2:
                        a,b,c = float(input('  Side a: ')),float(input('  Side b: ')),float(input('  Side c: '))
                        print(f"\n  Area (Herons): {Geometry.TriangleAreaHeron(a, b, c):.6f}")
                    case 3:
                        a,b,c = float(input('  Side a: ')),float(input('  Side b: ')),float(input('  Side c: '))
                        print(f"\n  Perimeter: {Geometry.TrianglePerimeter(a, b, c):.6f}")
                    case 4:
                        a, b = float(input('  Leg a: ')), float(input('  Leg b: '))

                        print(f"\n  Hypotenuse: {Geometry.Hypotenuse(a, b):.6f}")

                    case 5:
                        c, b = float(input('  Hypotenuse c: ')), float(input('  Known leg b: '))

                        print(f"\n  Missing leg: {Geometry.TriangleLeg(c, b):.6f}")

                    case 6:
                        a,b,c  = float(input('  Side a: ')),float(input('  Side b: ')),float(input('  Side c: '))
                        print(f"\n  Right triangle?  {'Yes' if Geometry.IsPythagorean(a, b, c) else 'No'}")
                    case 7:
                        a, b   = float(input('  Side a: ')), float(input('  Side b: '))
                        angle_C = float(input('  Included angle C (degrees): '))
                        print(f"\n  Missing side c: {Geometry.LawOfCosinesSide(a, b, angle_C):.6f}")
                    case 8:
                        a,b,c = float(input('  Side a: ')),float(input('  Side b: ')),float(input('  Side c: '))
                        print(f"\n  Angle C: {Geometry.LawOfCosinesAngle(a, b, c):.6f}°")
                    case 9:
                        a       = float(input('  Known side a: '))
                        angle_A = float(input('  Angle A opposite a (degrees): '))
                        angle_B = float(input('  Angle B opposite unknown b (degrees): '))
                        print(f"\n  Side b: {Geometry.LawOfSinesSide(a, angle_A, angle_B):.6f}")
                    case 10:
                        a       = float(input('  Side a: '))
                        b       = float(input('  Side b: '))
                        angle_B = float(input('  Angle B opposite b (degrees): '))
                        print(f"\n  Angle A: {Geometry.LawOfSinesAngle(a, b, angle_B):.6f}°")
                    case _:
                        print('\n  That was not a valid option.')
            elif sec == 4:
                match choice:
                    case 1:
                        l, w = float(input('  Length: ')), float(input('  Width: '))
                        print(f"\n  Area: {Geometry.RectangleArea(l, w):.6f}  |  Perimeter: {Geometry.RectanglePerimeter(l, w):.6f}")
                    case 2:
                        s = float(input('  Side length: '))
                        print(f"\n  Area: {Geometry.SquareArea(s):.6f}  |  Perimeter: {Geometry.SquarePerimeter(s):.6f}  |  Diagonal: {Geometry.SquareDiagonal(s):.6f}")
                    case 3:
                        base, h = float(input('  Base: ')), float(input('  Height: '))
                        print(f"\n  Area: {Geometry.ParallelogramArea(base, h):.6f}")
                    case 4:
                        b1, b2, h = float(input('  Base 1: ')), float(input('  Base 2: ')), float(input('  Height: '))
                        print(f"\n  Area: {Geometry.TrapezoidArea(b1, b2, h):.6f}")
                    case 5:
                        d1, d2 = float(input('  Diagonal 1: ')), float(input('  Diagonal 2: '))
                        print(f"\n  Area: {Geometry.RhombusArea(d1, d2):.6f}")
                    case _:
                        print('\n  That was not a valid option.')
            elif sec == 5:
                match choice:
                    case 1:
                        r = float(input('  Radius: '))
                        print(f"\n  Area: {Geometry.CircleArea(r):.6f}  |  Circumference: {Geometry.CircleCircumference(r):.6f}")
                    case 2:
                        r, angle = float(input('  Radius: ')), float(input('  Central angle (degrees): '))
                        print(f"\n  Arc length: {Geometry.ArcLength(r, angle):.6f}")
                    case 3:
                        r, angle = float(input('  Radius: ')), float(input('  Central angle (degrees): '))
                        print(f"\n  Sector area: {Geometry.SectorArea(r, angle):.6f}")
                    case 4:
                        r, angle = float(input('  Radius: ')), float(input('  Central angle (degrees): '))
                        print(f"\n  Chord length: {Geometry.ChordLength(r, angle):.6f}")
                    case _:
                        print('\n  That was not a valid option.')
            elif sec == 6:
                match choice:
                    case 1:
                        n = int(float(input('  Number of sides: ')))
                        print(f"\n  Interior angle sum: {Geometry.PolygonInteriorAngleSum(n):.6f}°")
                    case 2:
                        n = int(float(input('  Number of sides: ')))
                        print(f"\n  Each interior: {Geometry.RegularPolygonInteriorAngle(n):.6f}°  |  Each exterior: {Geometry.RegularPolygonExteriorAngle(n):.6f}°")
                    case 3:
                        n, s = int(float(input('  Number of sides: '))), float(input('  Side length: '))
                        print(f"\n  Area: {Geometry.RegularPolygonArea(n, s):.6f}  |  Perimeter: {Geometry.RegularPolygonPerimeter(n, s):.6f}")
                    case 4:
                        n = int(float(input('  Number of sides: ')))
                        print(f"\n  Number of diagonals: {Geometry.PolygonDiagonals(n)}")
                    case _:
                        print('\n  That was not a valid option.')
            elif sec == 7:
                match choice:
                    case 1:
                        l,w,h = float(input('  Length: ')),float(input('  Width: ')),float(input('  Height: '))
                        print(f"\n  Surface area: {Geometry.BoxSurfaceArea(l, w, h):.6f}  |  Volume: {Geometry.BoxVolume(l, w, h):.6f}")
                    case 2:
                        s = float(input('  Side length: '))
                        print(f"\n  Surface area: {Geometry.CubeSurfaceArea(s):.6f}  |  Volume: {Geometry.CubeVolume(s):.6f}")
                    case 3:
                        r, h = float(input('  Radius: ')), float(input('  Height: '))
                        print(f"\n  Surface area: {Geometry.CylinderSurfaceArea(r, h):.6f}  |  Volume: {Geometry.CylinderVolume(r, h):.6f}")
                    case 4:
                        r, h = float(input('  Radius: ')), float(input('  Height: '))
                        print(f"\n  Surface area: {Geometry.ConeSurfaceArea(r, h):.6f}  |  Volume: {Geometry.ConeVolume(r, h):.6f}")
                    case 5:
                        r = float(input('  Radius: '))
                        print(f"\n  Surface area: {Geometry.SphereSurfaceArea(r):.6f}  |  Volume: {Geometry.SphereVolume(r):.6f}")
                    case 6:
                        ba, h = float(input('  Base area: ')), float(input('  Height: '))
                        print(f"\n  Volume: {Geometry.PyramidVolume(ba, h):.6f}")
                    case _:
                        print('\n  That was not a valid option.')
            elif sec == 8:
                match choice:
                    case 1:
                        m, b   = float(input('  Slope (m): ')), float(input('  Y-intercept (b): '))
                        px, py = float(input('  Point x: ')), float(input('  Point y: '))
                        print(f"\n  On the line?  {'Yes' if Geometry.IsOnLine(m, b, px, py) else 'No'}")
                    case 2:
                        m = float(input('  Slope: '))
                        print(f"\n  Perpendicular slope: {Geometry.PerpendicularSlope(m):.6f}")
                    case 3:
                        m1, b1 = float(input('  Line 1 slope: ')), float(input('  Line 1 intercept: '))
                        m2, b2 = float(input('  Line 2 slope: ')), float(input('  Line 2 intercept: '))
                        print(f"\n  Parallel?  {'Yes' if Geometry.AreParallel(m1, b1, m2, b2) else 'No'}")
                    case 4:
                        m1, m2 = float(input('  Slope 1: ')), float(input('  Slope 2: '))
                        print(f"\n  Perpendicular?  {'Yes' if Geometry.ArePerpendicular(m1, m2) else 'No'}")
                    case 5:
                        m, x1, y1 = float(input('  Slope: ')), float(input('  Point x: ')), float(input('  Point y: '))
                        b = Geometry.LineFromPointSlope(m, x1, y1)
                        print(f"\n  Line: y = {m}x + {b:.6f}")
                    case 6:
                        x1, y1 = float(input('  Point 1 x: ')), float(input('  Point 1 y: '))
                        x2, y2 = float(input('  Point 2 x: ')), float(input('  Point 2 y: '))
                        x3, y3 = float(input('  Point 3 x: ')), float(input('  Point 3 y: '))
                        print(f"\n  Collinear?  {'Yes' if Geometry.AreCollinear(x1,y1,x2,y2,x3,y3) else 'No'}")
                    case _:
                        print('\n  That was not a valid option.')
            elif sec == 9:
                VectorsDebug()
                break
            print()
# ============================================================
# VECTORS DEBUG  (2D & 3D) — sub-router from Geometry
# ============================================================

def VectorsDebug():
    while True:
        _SectionHeader('Vectors', 'Choose a dimension')
        print('  (1)  2D  — operations in the x-y plane')
        print('  (2)  3D  — operations in x-y-z space')
        print()
        _ExitBar('Return to Geometry menu')
        print()
        dim = _menu_int('  Choose: ')
        if dim == 0: return
        if dim == 1:
            _Vectors2DDebug()
        elif dim == 2:
            _Vectors3DDebug()
        else:
            print('\n  That was not a valid option.')

# ────────────────────────────────────────────────────────────

def _Vectors2DDebug():
    SECTIONS = [
        'Components & Magnitude',
        'Vector Operations',
    ]
    while True:
        _SectionHeader('Vectors 2D', 'Choose a section')
        print('  (1)  Components & Magnitude  (IHat, JHat, normalize, project)')
        print('  (2)  Vector Operations        (add, subtract, dot, cross, scale)')
        print()
        _ExitBar('Return to Vectors menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        while True:
            _SectionHeader('Vectors 2D', SECTIONS[sec - 1] if 1 <= sec <= 2 else '')
            if sec == 1:
                print('  (1)   X component  (IHat)')
                print('  (2)   Y component  (JHat)')
                print('  (3)   Both X and Y components')
                print('  (4)   Magnitude')
                print('  (5)   Normalize  (unit vector)')
                print('  (6)   Project a onto b')
            elif sec == 2:
                print('  (1)   Add  a + b')
                print('  (2)   Subtract  a - b')
                print('  (3)   Dot product  a · b  (scalar)')
                print('  (4)   Cross product  a × b  (Z scalar)')
                print('  (5)   Scale a by scalar')
                print('  (6)   Divide a by scalar')
            print()
            _ExitBar('Return to Vectors 2D sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            def _v2(prompt='a'):
                raw = input(f'  Vector {prompt} — enter x and y separated by space: ').strip().split()
                return float(raw[0]), float(raw[1])
            def _polar(x, y):
                mag   = math.sqrt(x**2 + y**2)
                angle = math.degrees(math.atan2(y, x)) % 360
                return mag, angle
            ax, ay = _v2('a')
            mag_a, angle_a = _polar(ax, ay)
            if sec == 1:
                match choice:
                    case 1:
                        print(f'\n  X component  =  {Physics_2D.IHat(mag_a, angle_a):.6f}')
                    case 2:
                        print(f'\n  Y component  =  {Physics_2D.JHat(mag_a, angle_a):.6f}')
                    case 3:
                        ix, jy = Physics_2D.IJ(mag_a, angle_a)
                        print(f'\n  X = {ix:.6f}   Y = {jy:.6f}')
                    case 4:
                        print(f'\n  |a|  =  {Physics_2D.VectorMagnitude(mag_a, angle_a):.6f}')
                    case 5:
                        ux, uy = Physics_2D.NormalizeVector(mag_a, angle_a)
                        print(f'\n  â  =  {ux:.6f}i  +  {uy:.6f}j')
                    case 6:
                        bx, by = _v2('b')
                        mag_b, angle_b = _polar(bx, by)
                        print(f'\n  proj_b(a)  =  {Physics_2D.VectorProjection(mag_a, angle_a, mag_b, angle_b):.6f}')
                    case _:
                        print('\n  That was not a valid option.')
                        continue
            elif sec == 2:
                if choice in (1, 2, 3, 4):
                    bx, by = _v2('b')
                    mag_b, angle_b = _polar(bx, by)
                match choice:
                    case 1:
                        rx, ry = Physics_2D.AddVectors(mag_a, angle_a, mag_b, angle_b)
                        print(f'\n  a + b  =  {rx:.6f}i  +  {ry:.6f}j')
                    case 2:
                        rx, ry = Physics_2D.SubtractVectors(mag_a, angle_a, mag_b, angle_b)
                        print(f'\n  a - b  =  {rx:.6f}i  +  {ry:.6f}j')
                    case 3:
                        print(f'\n  a · b  =  {Physics_2D.DotProduct(mag_a, angle_a, mag_b, angle_b):.6f}')
                    case 4:
                        print(f'\n  a × b  =  {Physics_2D.CrossProduct(mag_a, angle_a, mag_b, angle_b):.6f}  (Z scalar)')
                    case 5:
                        scalar = float(input('  Scalar: '))
                        rx, ry = Physics_2D.ScalarMultiply(scalar, mag_a, angle_a)
                        print(f'\n  {scalar} × a  =  {rx:.6f}i  +  {ry:.6f}j')
                    case 6:
                        scalar = float(input('  Scalar: '))
                        rx, ry = Physics_2D.ScalarDivide(scalar, mag_a, angle_a)
                        print(f'\n  a / {scalar}  =  {rx:.6f}i  +  {ry:.6f}j')
                    case _:
                        print('\n  That was not a valid option.')
                        continue
            print()

# ────────────────────────────────────────────────────────────

def _Vectors3DDebug():
    SECTIONS = [
        'Components & Magnitude',
        'Vector Operations',
        'Compound Operations  (triple products etc.)',
    ]
    while True:
        _SectionHeader('Vectors 3D', 'Choose a section')
        print('  (1)  Components & Magnitude  (IHat/JHat/KHat, normalize, project)')
        print('  (2)  Vector Operations        (add, subtract, dot, cross, scale)')
        print('  (3)  Compound Operations      (scalar triple, dot/cross with sum/diff)')
        print()
        _ExitBar('Return to Vectors menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        while True:
            _SectionHeader('Vectors 3D', SECTIONS[sec - 1] if 1 <= sec <= 3 else '')
            if sec == 1:
                print('  (1)   X component  (IHat)')
                print('  (2)   Y component  (JHat)')
                print('  (3)   Z component  (KHat)')
                print('  (4)   All three components  (IJK)')
                print('  (5)   Magnitude')
                print('  (6)   Normalize  (unit vector)')
                print('  (7)   Project a onto b')
            elif sec == 2:
                print('  (1)   Add  a + b')
                print('  (2)   Subtract  a - b')
                print('  (3)   Dot product  a · b  (scalar)')
                print('  (4)   Cross product  a × b  (vector)')
                print('  (5)   Scale a by scalar')
                print('  (6)   Divide a by scalar')
                print('  (7)   Magnitude of a vector')
                print('  (8)   Normalize  (unit vector)')
            elif sec == 3:
                print('  — Two vectors —')
                print('  (1)   a + b')
                print('  (2)   a - b')
                print('  (3)   a · b  (dot product)')
                print('  (4)   a × b  (cross product)')
                print()
                print('  — Three vectors —')
                print('  (5)   a · (b × c)   scalar triple product')
                print('  (6)   a · (b + c)   dot with sum')
                print('  (7)   a · (b - c)   dot with difference')
                print('  (8)   a × (b + c)   cross with sum')
            print()
            _ExitBar('Return to Vectors 3D sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            def _v3(prompt='a'):
                raw = input(f'  Vector {prompt} — enter x, y, z separated by spaces: ').strip().split()
                return float(raw[0]), float(raw[1]), float(raw[2])
            def _sph(x, y, z):
                mag   = math.sqrt(x**2 + y**2 + z**2)
                theta = math.degrees(math.atan2(y, x)) % 360
                phi   = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))
                return mag, theta, phi
            ax, ay, az = _v3('a')
            mag_a, theta_a, phi_a = _sph(ax, ay, az)
            if sec == 1:
                match choice:
                    case 1:
                        print(f'\n  X component  =  {Physics_3D.IHat(mag_a, theta_a):.6f}')
                    case 2:
                        print(f'\n  Y component  =  {Physics_3D.JHat(mag_a, theta_a):.6f}')
                    case 3:
                        print(f'\n  Z component  =  {Physics_3D.KHat(mag_a, theta_a, phi_a):.6f}')
                    case 4:
                        ix, jy, kz = Physics_3D.IJK(mag_a, theta_a, phi_a)
                        print(f'\n  X = {ix:.6f}   Y = {jy:.6f}   Z = {kz:.6f}')
                    case 5:
                        print(f'\n  |a|  =  {Physics_3D.MagnitudeXYZ(ax, ay, az):.6f}')
                    case 6:
                        ux, uy, uz = Physics_3D.NormalizeXYZ(ax, ay, az)
                        print(f'\n  â  =  {ux:.6f}i  +  {uy:.6f}j  +  {uz:.6f}k')
                    case 7:
                        bx, by, bz = _v3('b')
                        mag_b, theta_b, phi_b = _sph(bx, by, bz)
                        print(f'\n  proj_b(a)  =  {Physics_3D.VectorProjection(mag_a, theta_a, mag_b, theta_b, phi_a, phi_b):.6f}')
                    case _:
                        print('\n  That was not a valid option.')
                        continue
            elif sec == 2:
                if choice in (1, 2, 3, 4):
                    bx, by, bz = _v3('b')
                match choice:
                    case 1:
                        rx, ry, rz = Physics_3D.AddVectorsXYZ(ax, ay, az, bx, by, bz)
                        print(f'\n  a + b  =  {rx:.6f}i  +  {ry:.6f}j  +  {rz:.6f}k')
                    case 2:
                        rx, ry, rz = Physics_3D.SubtractVectorsXYZ(ax, ay, az, bx, by, bz)
                        print(f'\n  a - b  =  {rx:.6f}i  +  {ry:.6f}j  +  {rz:.6f}k')
                    case 3:
                        print(f'\n  a · b  =  {Physics_3D.DotProductXYZ(ax, ay, az, bx, by, bz):.6f}')
                    case 4:
                        rx, ry, rz = Physics_3D.CrossProductXYZ(ax, ay, az, bx, by, bz)
                        print(f'\n  a × b  =  {rx:.6f}i  +  {ry:.6f}j  +  {rz:.6f}k')
                    case 5:
                        scalar = float(input('  Scalar: '))
                        rx, ry, rz = Physics_3D.ScalarMultiply(scalar, mag_a, theta_a, phi_a)
                        print(f'\n  {scalar} × a  =  {rx:.6f}i  +  {ry:.6f}j  +  {rz:.6f}k')
                    case 6:
                        scalar = float(input('  Scalar: '))
                        rx, ry, rz = Physics_3D.ScalarDivide(scalar, mag_a, theta_a, phi_a)
                        print(f'\n  a / {scalar}  =  {rx:.6f}i  +  {ry:.6f}j  +  {rz:.6f}k')
                    case 7:
                        print(f'\n  |a|  =  {Physics_3D.MagnitudeXYZ(ax, ay, az):.6f}')
                    case 8:
                        ux, uy, uz = Physics_3D.NormalizeXYZ(ax, ay, az)
                        print(f'\n  â  =  {ux:.6f}i  +  {uy:.6f}j  +  {uz:.6f}k')
                    case _:
                        print('\n  That was not a valid option.')
                        continue
            elif sec == 3:
                if choice in (1, 2, 3, 4):
                    bx, by, bz = _v3('b')
                elif choice in (5, 6, 7, 8):
                    bx, by, bz = _v3('b')
                    cx, cy, cz = _v3('c')
                else:
                    print('\n  That was not a valid option.')
                    continue
                match choice:
                    case 1:
                        rx, ry, rz = Physics_3D.AddVectorsXYZ(ax, ay, az, bx, by, bz)
                        print(f'\n  a + b  =  {rx:.6f}i  +  {ry:.6f}j  +  {rz:.6f}k')
                    case 2:
                        rx, ry, rz = Physics_3D.SubtractVectorsXYZ(ax, ay, az, bx, by, bz)
                        print(f'\n  a - b  =  {rx:.6f}i  +  {ry:.6f}j  +  {rz:.6f}k')
                    case 3:
                        print(f'\n  a · b  =  {Physics_3D.DotProductXYZ(ax, ay, az, bx, by, bz):.6f}')
                    case 4:
                        rx, ry, rz = Physics_3D.CrossProductXYZ(ax, ay, az, bx, by, bz)
                        print(f'\n  a × b  =  {rx:.6f}i  +  {ry:.6f}j  +  {rz:.6f}k')
                    case 5:
                        result = Physics_3D.ScalarTripleProduct(ax, ay, az, bx, by, bz, cx, cy, cz)
                        bxc    = Physics_3D.CrossProductXYZ(bx, by, bz, cx, cy, cz)
                        print(f'\n  b × c  =  {bxc[0]:.4f}i  +  {bxc[1]:.4f}j  +  {bxc[2]:.4f}k')
                        print(f'  a · (b × c)  =  {result:.6f}')
                    case 6:
                        result = Physics_3D.DotWithSum(ax, ay, az, bx, by, bz, cx, cy, cz)
                        bpc = Physics_3D.AddVectorsXYZ(bx, by, bz, cx, cy, cz)
                        print(f'\n  b + c  =  {bpc[0]:.4f}i  +  {bpc[1]:.4f}j  +  {bpc[2]:.4f}k')
                        print(f'  a · (b + c)  =  {result:.6f}')
                    case 7:
                        result = Physics_3D.DotWithDifference(ax, ay, az, bx, by, bz, cx, cy, cz)
                        bmc = Physics_3D.SubtractVectorsXYZ(bx, by, bz, cx, cy, cz)
                        print(f'\n  b - c  =  {bmc[0]:.4f}i  +  {bmc[1]:.4f}j  +  {bmc[2]:.4f}k')
                        print(f'  a · (b - c)  =  {result:.6f}')
                    case 8:
                        bpc = Physics_3D.AddVectorsXYZ(bx, by, bz, cx, cy, cz)
                        rx, ry, rz = Physics_3D.CrossWithSum(ax, ay, az, bx, by, bz, cx, cy, cz)
                        print(f'\n  b + c  =  {bpc[0]:.4f}i  +  {bpc[1]:.4f}j  +  {bpc[2]:.4f}k')
                        print(f'  a × (b + c)  =  {rx:.6f}i  +  {ry:.6f}j  +  {rz:.6f}k')
                    case _:
                        print('\n  That was not a valid option.')
                        continue
            print()


# ============================================================
# TRIGONOMETRY DEBUG
# ============================================================

def TrigonometryDebug():
    SECTIONS = [
        'Core & Reciprocal Functions',
        'Inverse Functions',
        'Pythagorean Identities',
        'Angle Sum & Difference',
        'Double & Half Angle',
        'Right Triangle Solvers',
        'Hyperbolic Functions',
        'Polar, Cartesian & Waves',
    ]
    while True:
        _SectionHeader('Trigonometry', 'Choose a section')
        for i, s in enumerate(SECTIONS, 1):
            print(f"  ({i})  {s}")
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section.')
            continue
        while True:
            _SectionHeader('Trigonometry', SECTIONS[sec - 1])
            if sec == 1:
                print('  (1)  sin(θ)')
                print('  (2)  cos(θ)')
                print('  (3)  tan(θ)')
                print('  (4)  csc(θ)  =  1/sin(θ)')
                print('  (5)  sec(θ)  =  1/cos(θ)')
                print('  (6)  cot(θ)  =  cos(θ)/sin(θ)')
            elif sec == 2:
                print('  (1)  arcsin(x)  →  angle in degrees')
                print('  (2)  arccos(x)  →  angle in degrees')
                print('  (3)  arctan(x)  →  angle in degrees')
                print('  (4)  atan2(y, x)  →  angle in degrees  (all quadrants)')
            elif sec == 3:
                print('  (1)  Verify sin²(θ) + cos²(θ) = 1')
                print('  (2)  sin²(θ) using power reduction')
                print('  (3)  cos²(θ) using power reduction')
            elif sec == 4:
                print('  (1)  sin(A + B)')
                print('  (2)  sin(A - B)')
                print('  (3)  cos(A + B)')
                print('  (4)  cos(A - B)')
                print('  (5)  tan(A + B)')
                print('  (6)  tan(A - B)')
            elif sec == 5:
                print('  (1)  sin(2θ)')
                print('  (2)  cos(2θ)')
                print('  (3)  tan(2θ)')
                print('  (4)  sin(θ/2)')
                print('  (5)  cos(θ/2)')
                print('  (6)  tan(θ/2)')
            elif sec == 6:
                print('  (1)  Opposite side  (from hypotenuse and angle)')
                print('  (2)  Adjacent side  (from hypotenuse and angle)')
                print('  (3)  Hypotenuse  (from opposite and angle)')
                print('  (4)  Hypotenuse  (from adjacent and angle)')
                print('  (5)  Opposite  (from adjacent and angle)')
                print('  (6)  Adjacent  (from opposite and angle)')
                print('  (7)  Angle  (from opposite and adjacent)')
            elif sec == 7:
                print('  (1)  sinh(x)')
                print('  (2)  cosh(x)')
                print('  (3)  tanh(x)')
                print('  (4)  Verify cosh²(x) - sinh²(x) = 1')
            elif sec == 8:
                print('  (1)  Polar to Cartesian  (r, θ) → (x, y)')
                print('  (2)  Cartesian to Polar  (x, y) → (r, θ)')
                print('  (3)  Sine wave value at x')
                print('  (4)  Cosine wave value at x')
                print('  (5)  Wave period from angular frequency')
                print('  (6)  Wave frequency from period')
                print('  (7)  Phase shift')
            print()
            _ExitBar('Return to sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            if sec == 1:
                match choice:
                    case 1: print(f'\n  sin = {Trig.Sin(float(input("  Angle (degrees): "))):.6f}')
                    case 2: print(f'\n  cos = {Trig.Cos(float(input("  Angle (degrees): "))):.6f}')
                    case 3: print(f'\n  tan = {Trig.Tan(float(input("  Angle (degrees): "))):.6f}')
                    case 4: print(f'\n  csc = {Trig.Csc(float(input("  Angle (degrees): "))):.6f}')
                    case 5: print(f'\n  sec = {Trig.Sec(float(input("  Angle (degrees): "))):.6f}')
                    case 6: print(f'\n  cot = {Trig.Cot(float(input("  Angle (degrees): "))):.6f}')
                    case _: print('\n  That was not a valid option.')
            elif sec == 2:
                match choice:
                    case 1: print(f'\n  arcsin = {Trig.Asin(float(input("  x (−1 to 1): "))):.6f}°')
                    case 2: print(f'\n  arccos = {Trig.Acos(float(input("  x (−1 to 1): "))):.6f}°')
                    case 3: print(f'\n  arctan = {Trig.Atan(float(input("  x: "))):.6f}°')
                    case 4:
                        y, x = float(input('  y: ')), float(input('  x: '))
                        print(f'\n  atan2 = {Trig.Atan2(y, x):.6f}°')
                    case _: print('\n  That was not a valid option.')
            elif sec == 3:
                match choice:
                    case 1:
                        deg = float(input('  Angle (degrees): '))
                        print(f"\n  sin²+cos²=1?  {'Yes' if Trig.PythagoreanIdentity(deg) else 'No'}")
                    case 2: print(f'\n  sin²= {Trig.SinSquared(float(input("  Angle (degrees): "))):.6f}')
                    case 3: print(f'\n  cos²= {Trig.CosSquared(float(input("  Angle (degrees): "))):.6f}')
                    case _: print('\n  That was not a valid option.')
            elif sec == 4:
                match choice:
                    case 1:
                        A, B = float(input('  A (degrees): ')), float(input('  B (degrees): '))
                        print(f'\n  sin(A+B) = {Trig.SinSum(A, B):.6f}')
                    case 2:
                        A, B = float(input('  A (degrees): ')), float(input('  B (degrees): '))
                        print(f'\n  sin(A-B) = {Trig.SinDiff(A, B):.6f}')
                    case 3:
                        A, B = float(input('  A (degrees): ')), float(input('  B (degrees): '))
                        print(f'\n  cos(A+B) = {Trig.CosSum(A, B):.6f}')
                    case 4:
                        A, B = float(input('  A (degrees): ')), float(input('  B (degrees): '))
                        print(f'\n  cos(A-B) = {Trig.CosDiff(A, B):.6f}')
                    case 5:
                        A, B = float(input('  A (degrees): ')), float(input('  B (degrees): '))
                        print(f'\n  tan(A+B) = {Trig.TanSum(A, B):.6f}')
                    case 6:
                        A, B = float(input('  A (degrees): ')), float(input('  B (degrees): '))
                        print(f'\n  tan(A-B) = {Trig.TanDiff(A, B):.6f}')
                    case _: print('\n  That was not a valid option.')
            elif sec == 5:
                match choice:
                    case 1: print(f'\n  sin(2θ) = {Trig.Sin2x(float(input("  Angle (degrees): "))):.6f}')
                    case 2: print(f'\n  cos(2θ) = {Trig.Cos2x(float(input("  Angle (degrees): "))):.6f}')
                    case 3: print(f'\n  tan(2θ) = {Trig.Tan2x(float(input("  Angle (degrees): "))):.6f}')
                    case 4: print(f'\n  sin(θ/2) = {Trig.SinHalf(float(input("  Angle (degrees): "))):.6f}')
                    case 5: print(f'\n  cos(θ/2) = {Trig.CosHalf(float(input("  Angle (degrees): "))):.6f}')
                    case 6: print(f'\n  tan(θ/2) = {Trig.TanHalf(float(input("  Angle (degrees): "))):.6f}')
                    case _: print('\n  That was not a valid option.')
            elif sec == 6:
                match choice:
                    case 1:
                        hyp, deg = float(input('  Hypotenuse: ')), float(input('  Angle (degrees): '))
                        print(f'\n  Opposite = {Trig.OppositeFromHypotenuse(hyp, deg):.6f}')
                    case 2:
                        hyp, deg = float(input('  Hypotenuse: ')), float(input('  Angle (degrees): '))
                        print(f'\n  Adjacent = {Trig.AdjacentFromHypotenuse(hyp, deg):.6f}')
                    case 3:
                        opp, deg = float(input('  Opposite: ')), float(input('  Angle (degrees): '))
                        print(f'\n  Hypotenuse = {Trig.HypotenuseFromOpposite(opp, deg):.6f}')
                    case 4:
                        adj, deg = float(input('  Adjacent: ')), float(input('  Angle (degrees): '))
                        print(f'\n  Hypotenuse = {Trig.HypotenuseFromAdjacent(adj, deg):.6f}')
                    case 5:
                        adj, deg = float(input('  Adjacent: ')), float(input('  Angle (degrees): '))
                        print(f'\n  Opposite = {Trig.OppositeFromAdjacent(adj, deg):.6f}')
                    case 6:
                        opp, deg = float(input('  Opposite: ')), float(input('  Angle (degrees): '))
                        print(f'\n  Adjacent = {Trig.AdjacentFromOpposite(opp, deg):.6f}')
                    case 7:
                        opp, adj = float(input('  Opposite: ')), float(input('  Adjacent: '))
                        print(f'\n  Angle = {Trig.AngleFromSides(opp, adj):.6f}°')
                    case _: print('\n  That was not a valid option.')
            elif sec == 7:
                match choice:
                    case 1: print(f'\n  sinh = {Trig.Sinh(float(input("  x: "))):.6f}')
                    case 2: print(f'\n  cosh = {Trig.Cosh(float(input("  x: "))):.6f}')
                    case 3: print(f'\n  tanh = {Trig.Tanh(float(input("  x: "))):.6f}')
                    case 4:
                        x = float(input('  x: '))
                        print(f"\n  cosh²-sinh²=1?  {'Yes' if Trig.HyperbolicIdentity(x) else 'No'}")
                    case _: print('\n  That was not a valid option.')
            elif sec == 8:
                match choice:
                    case 1:
                        r, deg = float(input('  r: ')), float(input('  θ (degrees): '))
                        x, y   = Trig.PolarToCartesian(r, deg)
                        print(f'\n  Cartesian: ({x:.6f}, {y:.6f})')
                    case 2:
                        x, y      = float(input('  x: ')), float(input('  y: '))
                        r, theta  = Trig.CartesianToPolar(x, y)
                        print(f'\n  Polar: r = {r:.6f},  θ = {theta:.6f}°')
                    case 3:
                        x  = float(input('  x: '))
                        A  = float(input('  Amplitude A: '))
                        B  = float(input('  Frequency B: '))
                        C  = float(input('  Phase shift C (Enter = 0): ') or '0')
                        D  = float(input('  Vertical shift D (Enter = 0): ') or '0')
                        print(f'\n  f({x}) = {Trig.SineWave(x, A, float(B), float(C), float(D)):.6f}')
                    case 4:
                        x  = float(input('  x: '))
                        A  = float(input('  Amplitude A: '))
                        B  = float(input('  Frequency B: '))
                        C  = float(input('  Phase shift C (Enter = 0): ') or '0')
                        D  = float(input('  Vertical shift D (Enter = 0): ') or '0')
                        print(f'\n  f({x}) = {Trig.CosineWave(x, A, float(B), float(C), float(D)):.6f}')
                    case 5: print(f'\n  Period: {Trig.WavePeriod(float(input("  Angular frequency B: "))):.6f}')
                    case 6: print(f'\n  Frequency: {Trig.WaveFrequency(float(input("  Period: "))):.6f}')
                    case 7:
                        C, freq = float(input('  Phase constant C: ')), float(input('  Angular frequency B: '))
                        print(f'\n  Phase shift: {Trig.PhaseShift(C, freq):.6f}')
                    case _: print('\n  That was not a valid option.')
            print()

# ============================================================
# CALCULUS DEBUG
# ============================================================

def CalculusDebug():
    SECTIONS = [
        'Limits',
        'Derivatives',
        'Differentiation Rules',
        'Curve Analysis',
        'Numerical Integration',
        'Series',
        'Multivariable',
        'Arc Length & Area',
    ]
    def get_f():
        print('  Enter a function using x.  Example: x**2 + 3*x  or  math.sin(x)')
        expr = input('  f(x) = ')
        return lambda x: eval(expr, {'x': x, 'math': math})
    def get_fxy():
        print('  Enter a function using x and y.  Example: x**2 + y**2')
        expr = input('  f(x, y) = ')
        return lambda x, y: eval(expr, {'x': x, 'y': y, 'math': math})
    def get_fxyz():
        print('  Enter a function using x, y, and z.  Example: x**2 + y**2 + z**2')
        expr = input('  f(x, y, z) = ')
        return lambda x, y, z: eval(expr, {'x': x, 'y': y, 'z': z, 'math': math})
    while True:
        _SectionHeader('Calculus', 'Choose a section')
        for i, s in enumerate(SECTIONS, 1):
            print(f"  ({i})  {s}")
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section.')
            continue
        while True:
            _SectionHeader('Calculus', SECTIONS[sec - 1])
            if sec == 1:
                print('  (1)  Two-sided limit  lim f(x) as x → a')
                print('  (2)  Left-hand limit  as x → a⁻')
                print('  (3)  Right-hand limit  as x → a⁺')
                print('  (4)  Check if the limit exists at a point')
            elif sec == 2:
                print('  (1)  First derivative  f\u2019(x)  at a point')
                print('  (2)  Second derivative  f\u2019\u2019(x)  at a point')
                print('  (3)  Third derivative  f\u2019\u2019\u2019(x)  at a point')
                print('  (4)  Nth derivative  f^(n)(x)  at a point')
            elif sec == 3:
                print('  (1)  Power rule  d/dx[c·x^n]  at x')
                print('  (2)  Product rule  d/dx[f·g]  at x')
                print('  (3)  Quotient rule  d/dx[f/g]  at x')
                print('  (4)  Chain rule  d/dx[f(g(x))]  at x')
            elif sec == 4:
                print('  (1)  Is a point a critical point?  f\u2019(x) = 0')
                print('  (2)  Second derivative test  (min / max / inconclusive)')
                print('  (3)  Concavity at a point')
                print('  (4)  Is a point an inflection point?')
                print('  (5)  Equation of the tangent line at a point')
                print('  (6)  Equation of the normal line at a point')
            elif sec == 5:
                print('  (1)  Left Riemann sum')
                print('  (2)  Right Riemann sum')
                print('  (3)  Trapezoid rule')
                print('  (4)  Simpsons rule  (most accurate)')
                print('  (5)  Definite integral  ∫a to b f(x)dx')
            elif sec == 6:
                print('  (1)  Taylor series approximation  at center a')
                print('  (2)  Maclaurin series  (centered at 0)')
                print('  (3)  Infinite geometric series sum')
                print('  (4)  Ratio test for convergence')
            elif sec == 7:
                print('  (1)  Partial derivative ∂f/∂x  at (x, y)')
                print('  (2)  Partial derivative ∂f/∂y  at (x, y)')
                print('  (3)  Partial derivative ∂f/∂z  at (x, y, z)')
                print('  (4)  Gradient vector ∇f  at (x, y)')
                print('  (5)  Gradient vector ∇f  at (x, y, z)')
                print('  (6)  Directional derivative  D_u f  at (x, y)')
            elif sec == 8:
                print('  (1)  Arc length of f from a to b')
                print('  (2)  Area under a curve  |∫f(x)dx|')
                print('  (3)  Area between two curves  ∫|f-g|dx')
                print('  (4)  Volume of revolution around x-axis  π∫f²dx')
            print()
            _ExitBar('Return to sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            if sec == 1:
                match choice:
                    case 1:
                        f = get_f()
                        a = float(input('  Approach point a: '))
                        print(f"\n  lim f(x) as x→{a} = {Calc.Limit(f, a):.6f}")
                    case 2:
                        f = get_f()
                        a = float(input('  Approach point a: '))
                        print(f"\n  Left-hand limit as x→{a}⁻ = {Calc.LimitLeft(f, a):.6f}")
                    case 3:
                        f = get_f()
                        a = float(input('  Approach point a: '))
                        print(f"\n  Right-hand limit as x→{a}⁺ = {Calc.LimitRight(f, a):.6f}")
                    case 4:
                        f  = get_f()
                        a  = float(input('  Point a: '))
                        exists = Calc.LimitExists(f, a)
                        left, right = Calc.LimitLeft(f, a), Calc.LimitRight(f, a)
                        print(f"\n  Left: {left:.6f}   Right: {right:.6f}")
                        print(f"  Limit exists?  {'Yes' if exists else 'No — left and right disagree'}")
                    case _: print('\n  That was not a valid option.')
            elif sec == 2:
                match choice:
                    case 1:
                        f, x = get_f(), float(input('  x: '))
                        print(f"\n  f'({x}) = {Calc.Derivative(f, x):.6f}")
                    case 2:
                        f, x = get_f(), float(input('  x: '))
                        print(f"\n  f''({x}) = {Calc.SecondDerivative(f, x):.6f}")
                    case 3:
                        f, x = get_f(), float(input('  x: '))
                        print(f"\n  f'''({x}) = {Calc.ThirdDerivative(f, x):.6f}")
                    case 4:
                        f, x, n = get_f(), float(input('  x: ')), int(input('  Derivative order n: '))
                        print(f"\n  f^({n})({x}) = {Calc.NthDerivative(f, x, n):.6f}")
                    case _: print('\n  That was not a valid option.')
            elif sec == 3:
                match choice:
                    case 1:
                        c, n, x = float(input('  Coefficient c: ')), float(input('  Exponent n: ')), float(input('  x: '))
                        print(f"\n  d/dx[{c}x^{n}] at x={x} = {Calc.PowerRule(c, n, x):.6f}")
                    case 2:
                        print('  Function f:')  ; f = get_f()
                        print('  Function g:')  ; g = get_f()
                        x = float(input('  x: '))
                        print(f"\n  d/dx[f·g] at x={x} = {Calc.ProductRule(f, g, x):.6f}")
                    case 3:
                        print('  Numerator f:')   ; f = get_f()
                        print('  Denominator g:') ; g = get_f()
                        x = float(input('  x: '))
                        print(f"\n  d/dx[f/g] at x={x} = {Calc.QuotientRule(f, g, x):.6f}")
                    case 4:
                        print('  Outer function f:') ; f = get_f()
                        print('  Inner function g:') ; g = get_f()
                        x = float(input('  x: '))
                        print(f"\n  d/dx[f(g(x))] at x={x} = {Calc.ChainRule(f, g, x):.6f}")
                    case _: print('\n  That was not a valid option.')
            elif sec == 4:
                match choice:
                    case 1:
                        f, x = get_f(), float(input('  x: '))
                        result = Calc.IsCriticalPoint(f, x)
                        print(f"\n  f'({x}) = {Calc.Derivative(f, x):.6f}")
                        print(f"  Critical point?  {'Yes' if result else 'No'}")
                    case 2:
                        f, x = get_f(), float(input('  x: '))
                        print(f"\n  f''({x}) = {Calc.SecondDerivative(f, x):.6f}")
                        print(f"  Result: {Calc.SecondDerivativeTest(f, x)}")
                    case 3:
                        f, x = get_f(), float(input('  x: '))
                        print(f"\n  At x = {x}: {Calc.Concavity(f, x)}")
                    case 4:
                        f, x = get_f(), float(input('  x: '))
                        result = Calc.IsInflectionPoint(f, x)
                        print(f"\n  f''({x}) = {Calc.SecondDerivative(f, x):.6f}")
                        print(f"  Inflection point?  {'Yes' if result else 'No'}")
                    case 5:
                        f, x0 = get_f(), float(input('  x₀: '))
                        slope  = Calc.Derivative(f, x0)
                        b      = f(x0) - slope * x0
                        print(f"\n  Tangent line at x={x0}:  y = {slope:.6f}x + {b:.6f}")
                    case 6:
                        f, x0  = get_f(), float(input('  x₀: '))
                        slope  = Calc.Derivative(f, x0)
                        n_slope = 0 if abs(slope) < 1e-9 else -1 / slope
                        b       = f(x0) - n_slope * x0
                        print(f"\n  Normal line at x={x0}:  y = {n_slope:.6f}x + {b:.6f}")
                    case _: print('\n  That was not a valid option.')
            elif sec == 5:
                match choice:
                    case 1:
                        f = get_f()
                        a, b = float(input('  Lower bound a: ')), float(input('  Upper bound b: '))
                        n = int(input('  Subintervals (Enter = 1000): ') or '1000')
                        print(f"\n  Left Riemann ≈ {Calc.RiemannLeft(f, a, b, n):.6f}")
                    case 2:
                        f = get_f()
                        a, b = float(input('  Lower bound a: ')), float(input('  Upper bound b: '))
                        n = int(input('  Subintervals (Enter = 1000): ') or '1000')
                        print(f"\n  Right Riemann ≈ {Calc.RiemannRight(f, a, b, n):.6f}")
                    case 3:
                        f = get_f()
                        a, b = float(input('  Lower bound a: ')), float(input('  Upper bound b: '))
                        n = int(input('  Subintervals (Enter = 1000): ') or '1000')
                        print(f"\n  Trapezoid rule ≈ {Calc.TrapezoidRule(f, a, b, n):.6f}")
                    case 4:
                        f = get_f()
                        a, b = float(input('  Lower bound a: ')), float(input('  Upper bound b: '))
                        n = int(input('  Subintervals (Enter = 1000): ') or '1000')
                        print(f"\n  Simpsons rule ≈ {Calc.SimpsonsRule(f, a, b, n):.6f}")
                    case 5:
                        f = get_f()
                        a, b = float(input('  Lower bound a: ')), float(input('  Upper bound b: '))
                        print(f"\n  ∫f from {a} to {b} = {Calc.DefiniteIntegral(f, a, b):.6f}")
                    case _: print('\n  That was not a valid option.')
            elif sec == 6:
                match choice:
                    case 1:
                        f = get_f()
                        a, x = float(input('  Center a: ')), float(input('  Evaluate at x: '))
                        terms = int(input('  Terms (Enter = 10): ') or '10')
                        print(f"\n  Taylor series ≈ {Calc.TaylorSeries(f, a, x, terms):.6f}")
                    case 2:
                        f = get_f()
                        x = float(input('  Evaluate at x: '))
                        terms = int(input('  Terms (Enter = 10): ') or '10')
                        print(f"\n  Maclaurin series ≈ {Calc.MaclaurinSeries(f, x, terms):.6f}")
                    case 3:
                        a, r = float(input('  First term a: ')), float(input('  Common ratio r (|r| < 1): '))
                        result = Calc.GeometricSeriesSum(a, r)
                        if result == 0 and abs(r) >= 1:
                            print('\n  Series diverges.')
                        else:
                            print(f"\n  Infinite sum = {result:.6f}")
                    case 4:
                        print('  Enter the general term using k.  Example: 1 / k**2')
                        expr   = input('  a(k) = ')
                        f_term = lambda k: eval(expr, {'k': k, 'math': math})
                        print(f"\n  Ratio test: {Calc.RatioTest(f_term)}")
                    case _: print('\n  That was not a valid option.')
            elif sec == 7:
                match choice:
                    case 1:
                        f    = get_fxy()
                        x, y = float(input('  x: ')), float(input('  y: '))
                        print(f"\n  ∂f/∂x at ({x}, {y}) = {Calc.PartialX(f, x, y):.6f}")
                    case 2:
                        f    = get_fxy()
                        x, y = float(input('  x: ')), float(input('  y: '))
                        print(f"\n  ∂f/∂y at ({x}, {y}) = {Calc.PartialY(f, x, y):.6f}")
                    case 3:
                        f       = get_fxyz()
                        x, y, z = float(input('  x: ')), float(input('  y: ')), float(input('  z: '))
                        print(f"\n  ∂f/∂z at ({x},{y},{z}) = {Calc.PartialZ(f, x, y, z):.6f}")
                    case 4:
                        f    = get_fxy()
                        x, y = float(input('  x: ')), float(input('  y: '))
                        gx, gy = Calc.Gradient2D(f, x, y)
                        print(f"\n  ∇f at ({x},{y}) = ({gx:.6f}, {gy:.6f})")
                    case 5:
                        f       = get_fxyz()
                        x, y, z = float(input('  x: ')), float(input('  y: ')), float(input('  z: '))
                        gx, gy, gz = Calc.Gradient3D(f, x, y, z)
                        print(f"\n  ∇f at ({x},{y},{z}) = ({gx:.6f}, {gy:.6f}, {gz:.6f})")
                    case 6:
                        f    = get_fxy()
                        x, y = float(input('  x: ')), float(input('  y: '))
                        ux, uy = float(input('  Direction ux: ')), float(input('  Direction uy: '))
                        print(f"\n  D_u f at ({x},{y}) = {Calc.DirectionalDerivative2D(f, x, y, ux, uy):.6f}")
                    case _: print('\n  That was not a valid option.')
            elif sec == 8:
                match choice:
                    case 1:
                        f = get_f()
                        a, b = float(input('  Lower bound a: ')), float(input('  Upper bound b: '))
                        print(f"\n  Arc length ≈ {Calc.ArcLength(f, a, b):.6f}")
                    case 2:
                        f = get_f()
                        a, b = float(input('  Lower bound a: ')), float(input('  Upper bound b: '))
                        print(f"\n  Area under curve ≈ {Calc.AreaUnderCurve(f, a, b):.6f}")
                    case 3:
                        print('  Upper function f:') ; f = get_f()
                        print('  Lower function g:') ; g = get_f()
                        a, b = float(input('  Lower bound a: ')), float(input('  Upper bound b: '))
                        print(f"\n  Area between curves ≈ {Calc.AreaBetweenCurves(f, g, a, b):.6f}")
                    case 4:
                        f = get_f()
                        a, b = float(input('  Lower bound a: ')), float(input('  Upper bound b: '))
                        print(f"\n  Volume of revolution ≈ {Calc.VolumeOfRevolution(f, a, b):.6f}")
                    case _: print('\n  That was not a valid option.')
            print()

# ============================================================
# DIFFERENTIATION DEBUG
# ============================================================

def DifferentiationDebug():

    def _get_f(label='f(x)'):
        _p(f'Enter {label} as a Python expression using x.  Example:  x**2 + 3*x   or   math.sin(x)')
        expr = _ask_str(f'  {label} = ')
        return lambda x: eval(expr, {'x': x, 'math': math})

    def _get_fxy(label='f(x, y)'):
        _p(f'Enter {label} using x and y.  Example:  x**2 + y**2')
        expr = _ask_str(f'  {label} = ')
        return lambda x, y: eval(expr, {'x': x, 'y': y, 'math': math})

    def _fmt(v, precision=6):
        if isinstance(v, float):
            return f'{v:.{precision}f}'
        return str(v)

    SECTIONS = [
        'Polynomial Derivatives',
        'Differentiation Rules',
        'Common Functions  (trig, exp, log)',
        'Inverse & Hyperbolic Functions',
        'Implicit Differentiation',
        'Root Finding  (Newton\'s Method)',
        'Related Rates',
        'Linearisation & Error Estimation',
        'Advanced  (Jacobian, Hessian, Critical Points)',
    ]

    while True:
        _SectionHeader('Differentiation', 'Choose a section')
        for i, s in enumerate(SECTIONS, 1):
            print(f'  ({i})  {s}')
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section number. Please try again.')
            continue

        while True:
            _SectionHeader('Differentiation', SECTIONS[sec - 1])
            if sec == 1:
                _p('Work with polynomial expressions entered as a list of coefficients  '
                   '(highest power first).  Example: [3, 0, -2] means 3x² − 2.')
                print()
                print('  (1)  Differentiate a single term       d/dx[c·xⁿ]')
                print('  (2)  Differentiate a polynomial        (list of coefficients)')
                print('  (3)  Evaluate a polynomial             f(x) at x')
                print('  (4)  Derivative of polynomial at x     f\'(x) at x')
                print('  (5)  Nth derivative of polynomial      f⁽ⁿ⁾(x)')
                print('  (6)  Integrate a polynomial            ∫p(x)dx  (symbolic)')
            elif sec == 2:
                _p('Each rule works numerically — enter your functions as expressions in x.')
                print()
                print('  (1)  Sum rule          d/dx[f + g]  at x')
                print('  (2)  Difference rule   d/dx[f − g]  at x')
                print('  (3)  Constant multiple d/dx[c·f]    at x')
                print('  (4)  Product rule      d/dx[f·g]    at x')
                print('  (5)  Quotient rule     d/dx[f/g]    at x')
                print('  (6)  Chain rule        d/dx[f(g(x))] at x')
            elif sec == 3:
                print('  (1)  Power function    d/dx[xⁿ]  at x')
                print('  (2)  Natural exp       d/dx[eˣ]  at x')
                print('  (3)  Exp base a        d/dx[aˣ]  at x')
                print('  (4)  Natural log       d/dx[ln x]  at x')
                print('  (5)  Log base a        d/dx[logₐx]  at x')
                print('  (6)  Sin               d/dx[sin x]  at x')
                print('  (7)  Cos               d/dx[cos x]  at x')
                print('  (8)  Tan               d/dx[tan x]  at x')
            elif sec == 4:
                print('  (1)  Arcsin   d/dx[arcsin x]  at x')
                print('  (2)  Arccos   d/dx[arccos x]  at x')
                print('  (3)  Arctan   d/dx[arctan x]  at x')
                print('  (4)  Sinh     d/dx[sinh x]    at x')
                print('  (5)  Cosh     d/dx[cosh x]    at x')
                print('  (6)  Tanh     d/dx[tanh x]    at x')
            elif sec == 5:
                _p('Implicit differentiation works on equations F(x, y) = 0.')
                print()
                print('  (1)  dy/dx    at a point  (first implicit derivative)')
                print('  (2)  d²y/dx²  at a point  (second implicit derivative)')
                print('  (3)  Tangent line  at a point on the curve')
            elif sec == 6:
                _p('Newton\'s Method numerically finds roots of f(x) = 0.  '
                   'Enter a starting estimate close to the root you\'re looking for.')
                print()
                print('  (1)  Find a single root     near a starting point x₀')
                print('  (2)  Find all roots          in an interval [a, b]')
                print('  (3)  Count iterations        to converge from x₀')
            elif sec == 7:
                _p('Related rates — how fast one quantity changes when another does.  '
                   'Enter known rates as numbers.')
                print()
                print('  (1)  General chain rule     dy/dt = (dy/dx)·(dx/dt)')
                print('  (2)  Circle area rate       dA/dt  given r and dr/dt')
                print('  (3)  Sphere volume rate     dV/dt  given r and dr/dt')
                print('  (4)  Cylinder volume rate   dV/dt  given r and dh/dt  (fixed r)')
                print('  (5)  Pythagorean rate       dz/dt  given x, y, dx/dt, dy/dt')
                print('  (6)  Shadow length rate     ds/dt  given geometry and walking speed')
            elif sec == 8:
                _p('Linearisation approximates f(x) near a known point a.  '
                   'Error estimation quantifies how accurate the approximation is.')
                print()
                print('  (1)  Linearisation        L(x) = f(a) + f\'(a)·(x−a)')
                print('  (2)  Differential         dy ≈ f\'(x)·dx')
                print('  (3)  Relative error       dy / y')
                print('  (4)  Percentage error     100 · |dy / y|  %')
            elif sec == 9:
                _p('Advanced tools for multivariable analysis and curve classification.')
                print()
                print('  (1)  Nth derivative          f⁽ⁿ⁾(x)  at a point')
                print('  (2)  Mixed partial           ∂²f/∂x∂y  at (x, y)')
                print('  (3)  Jacobian matrix         of a vector function at a point')
                print('  (4)  Hessian matrix          of f(x, y) at a point')
                print('  (5)  Find critical points    of f in [a, b]')
                print('  (6)  Find inflection points  of f in [a, b]')
                print('  (7)  Classify critical points as min / max / saddle in [a, b]')
            print()
            _ExitBar('Return to sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            print()
            try:
                if sec == 1:
                    match choice:
                        case 1:
                            c = _ask('Coefficient c')
                            n = _ask('Exponent n')
                            new_c, new_n = Diff.DiffPowerTerm(c, n)
                            print(f'\n  d/dx[{c}·x^{n}]  =  {new_c}·x^{new_n}')
                        case 2:
                            _p('Enter coefficients from highest to lowest power, separated by spaces or commas.')
                            _p('Example:  3 0 -2  →  3x² + 0x − 2')
                            coeffs = _ask_list('  Coefficients', cast=float, min_count=1)
                            d = Diff.DiffPolynomial(coeffs)
                            print(f'\n  Original:   {coeffs}')
                            print(f'  Derivative: {d}')
                        case 3:
                            _p('Enter coefficients from highest to lowest power.')
                            coeffs = _ask_list('  Coefficients', cast=float, min_count=1)
                            x = _ask('x value to evaluate at')
                            result = Diff.EvalPoly(coeffs, x)
                            print(f'\n  f({x}) = {_fmt(result)}')
                        case 4:
                            _p('Enter coefficients from highest to lowest power.')
                            coeffs = _ask_list('  Coefficients', cast=float, min_count=1)
                            x = _ask('x value')
                            result = Diff.DiffPolynomialAt(coeffs, x)
                            print(f"\n  f'({x}) = {_fmt(result)}")
                        case 5:
                            _p('Enter coefficients from highest to lowest power.')
                            coeffs = _ask_list('  Coefficients', cast=float, min_count=1)
                            n = _ask_int('Derivative order n  (1 = first, 2 = second, etc.)',
                                         desc='a positive whole number')
                            x = _ask('x value')
                            result = Diff.DiffPolynomialAt(Diff.DiffPolynomialNth(coeffs, n), x) \
                                     if n > 1 else Diff.DiffPolynomialAt(coeffs, x)
                            print(f'\n  f^({n})({x}) = {_fmt(result)}')
                        case 6:
                            _p('Enter coefficients from highest to lowest power.')
                            coeffs = _ask_list('  Coefficients', cast=float, min_count=1)
                            result = Diff.IntegratePolynomial(coeffs)
                            print(f'\n  ∫p(x)dx coefficients: {result}  (+ C)')
                        case _: print('  That was not a valid option.')
                elif sec == 2:
                    match choice:
                        case 1:
                            print('  Function f:') ; f = _get_f('f(x)')
                            print('  Function g:') ; g = _get_f('g(x)')
                            x = _ask('x value')
                            print(f"\n  d/dx[f + g] at x={x}  =  {Diff.SumRule(f, g, x):.6f}")
                        case 2:
                            print('  Function f:') ; f = _get_f('f(x)')
                            print('  Function g:') ; g = _get_f('g(x)')
                            x = _ask('x value')
                            print(f"\n  d/dx[f − g] at x={x}  =  {Diff.DifferenceRule(f, g, x):.6f}")
                        case 3:
                            c = _ask('Constant c')
                            print('  Function f:') ; f = _get_f('f(x)')
                            x = _ask('x value')
                            print(f"\n  d/dx[{c}·f] at x={x}  =  {Diff.ConstantMultipleRule(c, f, x):.6f}")
                        case 4:
                            print('  Function f:') ; f = _get_f('f(x)')
                            print('  Function g:') ; g = _get_f('g(x)')
                            x = _ask('x value')
                            print(f"\n  d/dx[f·g] at x={x}  =  {Diff.ProductRule(f, g, x):.6f}")
                        case 5:
                            print('  Numerator f:')   ; f = _get_f('f(x)')
                            print('  Denominator g:') ; g = _get_f('g(x)')
                            x = _ask('x value')
                            print(f"\n  d/dx[f/g] at x={x}  =  {Diff.QuotientRule(f, g, x):.6f}")
                        case 6:
                            print('  Outer function f:') ; f = _get_f('f(x)')
                            print('  Inner function g:') ; g = _get_f('g(x)')
                            x = _ask('x value')
                            print(f"\n  d/dx[f(g(x))] at x={x}  =  {Diff.ChainRule(f, g, x):.6f}")
                        case _: print('  That was not a valid option.')
                elif sec == 3:
                    match choice:
                        case 1:
                            n = _ask('Exponent n')
                            x = _ask('x value')
                            print(f'\n  d/dx[x^{n}] at x={x}  =  {Diff.DiffPower(n, x):.6f}')
                        case 2:
                            x = _ask('x value')
                            print(f'\n  d/dx[eˣ] at x={x}  =  {Diff.DiffExp(x):.6f}')
                        case 3:
                            a = _ask('Base a  (must be positive, not 1)', desc='a positive number other than 1')
                            x = _ask('x value')
                            print(f'\n  d/dx[{a}ˣ] at x={x}  =  {Diff.DiffExpBase(a, x):.6f}')
                        case 4:
                            x = _ask('x value  (must be > 0)', desc='a positive number')
                            print(f'\n  d/dx[ln x] at x={x}  =  {Diff.DiffLn(x):.6f}')
                        case 5:
                            a = _ask('Log base a  (must be positive, not 1)', desc='a positive number other than 1')
                            x = _ask('x value  (must be > 0)', desc='a positive number')
                            print(f'\n  d/dx[log_{a}(x)] at x={x}  =  {Diff.DiffLog(a, x):.6f}')
                        case 6:
                            x = _ask('x value  (radians)')
                            print(f'\n  d/dx[sin x] at x={x}  =  {Diff.DiffSin(x):.6f}')
                        case 7:
                            x = _ask('x value  (radians)')
                            print(f'\n  d/dx[cos x] at x={x}  =  {Diff.DiffCos(x):.6f}')
                        case 8:
                            x = _ask('x value  (radians, avoid π/2 + nπ)', desc='a number not at a vertical asymptote')
                            print(f'\n  d/dx[tan x] at x={x}  =  {Diff.DiffTan(x):.6f}')
                        case _: print('  That was not a valid option.')
                elif sec == 4:
                    match choice:
                        case 1:
                            x = _ask('x value  (must be between −1 and 1)', desc='a number in [−1, 1]')
                            print(f'\n  d/dx[arcsin x] at x={x}  =  {Diff.DiffArcsin(x):.6f}')
                        case 2:
                            x = _ask('x value  (must be between −1 and 1)', desc='a number in [−1, 1]')
                            print(f'\n  d/dx[arccos x] at x={x}  =  {Diff.DiffArccos(x):.6f}')
                        case 3:
                            x = _ask('x value')
                            print(f'\n  d/dx[arctan x] at x={x}  =  {Diff.DiffArctan(x):.6f}')
                        case 4:
                            x = _ask('x value')
                            print(f'\n  d/dx[sinh x] at x={x}  =  {Diff.DiffSinh(x):.6f}')
                        case 5:
                            x = _ask('x value')
                            print(f'\n  d/dx[cosh x] at x={x}  =  {Diff.DiffCosh(x):.6f}')
                        case 6:
                            x = _ask('x value')
                            print(f'\n  d/dx[tanh x] at x={x}  =  {Diff.DiffTanh(x):.6f}')
                        case _: print('  That was not a valid option.')
                elif sec == 5:
                    _p('Enter F(x, y) as a Python expression.  The equation is assumed to equal 0.  '
                       'Example: x**2 + y**2 - 25  (circle of radius 5)')
                    match choice:
                        case 1:
                            F = _get_fxy('F(x, y)')
                            x = _ask('x value at the point')
                            y = _ask('y value at the point')
                            dy = Diff.ImplicitDerivative(F, x, y)
                            print(f'\n  dy/dx at ({x}, {y})  =  {dy:.6f}')
                        case 2:
                            F = _get_fxy('F(x, y)')
                            x = _ask('x value at the point')
                            y = _ask('y value at the point')
                            d2y = Diff.ImplicitSecondDerivative(F, x, y)
                            print(f'\n  d²y/dx² at ({x}, {y})  =  {d2y:.6f}')
                        case 3:
                            F = _get_fxy('F(x, y)')
                            x = _ask('x value at the point')
                            y = _ask('y value at the point')
                            slope, intercept = Diff.ImplicitTangentLine(F, x, y)
                            print(f'\n  Tangent line at ({x}, {y}):')
                            print(f'    y = {slope:.6f}·x + {intercept:.6f}')
                        case _: print('  That was not a valid option.')
                elif sec == 6:
                    match choice:
                        case 1:
                            f  = _get_f('f(x)')
                            x0 = _ask('Starting estimate x₀  (close to the root)',
                                      desc='a number near the root you want to find')
                            root = Diff.NewtonsMethod(f, x0)
                            print(f'\n  Root found:  x ≈ {root:.10f}')
                            print(f'  Verification:  f({root:.6f}) = {f(root):.2e}')
                        case 2:
                            f = _get_f('f(x)')
                            a = _ask('Left bound a')
                            b = _ask('Right bound b  (must be > a)', desc='a number larger than a')
                            roots = Diff.FindRoots(f, a, b)
                            if not roots:
                                print('\n  No roots found in that interval.')
                            else:
                                print(f'\n  Roots found in [{a}, {b}]:')
                                for i, r in enumerate(roots, 1):
                                    print(f'    {i}.  x ≈ {r:.10f}   (f(x) ≈ {f(r):.2e})')
                        case 3:
                            f  = _get_f('f(x)')
                            x0 = _ask('Starting estimate x₀')
                            count = Diff.NewtonsConvergenceCount(f, x0)
                            print(f'\n  Iterations to converge from x₀={x0}:  {count}')
                        case _: print('  That was not a valid option.')
                elif sec == 7:
                    match choice:
                        case 1:
                            dydx = _ask('dy/dx  (rate of change of y with respect to x)')
                            dxdt = _ask('dx/dt  (rate of change of x with respect to t)')
                            dydt = Diff.RelatedRate(dydx, dxdt)
                            print(f'\n  dy/dt = (dy/dx) · (dx/dt) = {dydx} × {dxdt} = {dydt:.6f}')
                        case 2:
                            r    = _ask('Radius r  (m)', desc='the current radius in metres')
                            drdt = _ask('dr/dt  (rate of change of radius, m/s)')
                            dAdt = Diff.CircleAreaRate(r, drdt)
                            print(f'\n  Circle area rate:')
                            print(f'    r = {r} m,  dr/dt = {drdt} m/s')
                            print(f'    dA/dt = 2πr·(dr/dt) = {dAdt:.6f} m²/s')
                        case 3:
                            r    = _ask('Radius r  (m)')
                            drdt = _ask('dr/dt  (rate of change of radius, m/s)')
                            dVdt = Diff.SphereVolumeRate(r, drdt)
                            print(f'\n  Sphere volume rate:')
                            print(f'    r = {r} m,  dr/dt = {drdt} m/s')
                            print(f'    dV/dt = 4πr²·(dr/dt) = {dVdt:.6f} m³/s')
                        case 4:
                            r    = _ask('Radius r  (m, fixed)')
                            dhdt = _ask('dh/dt  (rate height is changing, m/s)')
                            dVdt = Diff.CylinderVolumeRate(r, dhdt)
                            print(f'\n  Cylinder volume rate:')
                            print(f'    r = {r} m,  dh/dt = {dhdt} m/s')
                            print(f'    dV/dt = πr²·(dh/dt) = {dVdt:.6f} m³/s')
                        case 5:
                            x    = _ask('x  (horizontal distance)')
                            y    = _ask('y  (vertical distance)')
                            dxdt = _ask('dx/dt  (rate x is changing)')
                            dydt = _ask('dy/dt  (rate y is changing)')
                            dzdt = Diff.PythagoreanRate(x, y, dxdt, dydt)
                            print(f'\n  Pythagorean rate:')
                            print(f'    z = sqrt(x² + y²) = {math.sqrt(x**2+y**2):.4f}')
                            print(f'    dz/dt = {dzdt:.6f}')
                        case 6:
                            ph   = _ask('Person height  (m)')
                            lh   = _ask('Light/lamp height  (m, must be > person height)',
                                        desc='a number larger than the person height')
                            x    = _ask('Current distance from base of light  (m)')
                            dxdt = _ask('Walking speed  (m/s, positive = moving away from light)')
                            dsdt = Diff.ShadowLengthRate(ph, lh, x, dxdt)
                            print(f'\n  Shadow length rate:  ds/dt = {dsdt:.6f} m/s')
                        case _: print('  That was not a valid option.')
                elif sec == 8:
                    match choice:
                        case 1:
                            f = _get_f('f(x)')
                            a = _ask('Centre of linearisation a')
                            x = _ask('Approximate f at x')
                            L = Diff.Linearization(f, a, x)
                            print(f'\n  L({x}) ≈ f({a}) + f\'({a})·({x}−{a})')
                            print(f'  Linearised value:  L({x}) = {L:.6f}')
                            print(f'  Actual value:      f({x}) = {f(x):.6f}')
                            print(f'  Error:             {abs(f(x)-L):.6f}')
                        case 2:
                            f  = _get_f('f(x)')
                            x  = _ask('x value')
                            dx = _ask('dx  (small change in x)')
                            dy = Diff.Differential(f, x, dx)
                            print(f'\n  dy = f\'({x}) · {dx}  =  {dy:.6f}')
                        case 3:
                            f  = _get_f('f(x)')
                            x  = _ask('x value')
                            dx = _ask('dx  (measurement error or small change)')
                            re = Diff.RelativeError(f, x, dx)
                            print(f'\n  Relative error  dy/y  =  {re:.6f}')
                        case 4:
                            f  = _get_f('f(x)')
                            x  = _ask('x value')
                            dx = _ask('dx  (measurement error or small change)')
                            pe = Diff.PercentageError(f, x, dx)
                            print(f'\n  Percentage error  =  {pe:.4f} %')
                        case _: print('  That was not a valid option.')
                elif sec == 9:
                    match choice:
                        case 1:
                            f = _get_f('f(x)')
                            n = _ask_int('Derivative order n', desc='a positive whole number')
                            x = _ask('x value')
                            print(f'\n  f^({n})({x})  =  {Diff.NthDerivative(f, x, n):.6f}')
                        case 2:
                            f = _get_fxy('f(x, y)')
                            x = _ask('x value')
                            y = _ask('y value')
                            print(f'\n  ∂²f/∂x∂y at ({x}, {y})  =  {Diff.MixedPartial(f, x, y):.6f}')
                        case 3:
                            _p('Enter each component function of the vector-valued function F as an '
                               'expression in x and y, one per line.')
                            n_comp = _ask_int('Number of component functions', desc='a whole number like 2 or 3')
                            funcs  = []
                            for i in range(n_comp):
                                e = _ask_str(f'  F_{i+1}(x,y) = ')
                                funcs.append(lambda x, y, _e=e: eval(_e, {'x': x, 'y': y, 'math': math}))
                            point = _ask_list('  Evaluation point (x, y)', cast=float, min_count=2)
                            J = Diff.Jacobian(funcs, point[:2])
                            print('\n  Jacobian matrix:')
                            for row in J:
                                print('   ', '  '.join(f'{v:10.6f}' for v in row))
                        case 4:
                            f = _get_fxy('f(x, y)')
                            point = _ask_list('  Evaluation point (x, y)', cast=float, min_count=2)
                            H = Diff.Hessian(f, point[:2])
                            print('\n  Hessian matrix:')
                            for row in H:
                                print('   ', '  '.join(f'{v:10.6f}' for v in row))
                        case 5:
                            f = _get_f('f(x)')
                            a = _ask('Left bound a')
                            b = _ask('Right bound b  (must be > a)', desc='a number larger than a')
                            pts = Diff.FindCriticalPoints(f, a, b)
                            if not pts:
                                print(f'\n  No critical points found in [{a}, {b}].')
                            else:
                                print(f'\n  Critical points in [{a}, {b}]:')
                                for p in pts:
                                    print(f'    x ≈ {p:.6f}   f(x) = {f(p):.6f}')
                        case 6:
                            f = _get_f('f(x)')
                            a = _ask('Left bound a')
                            b = _ask('Right bound b  (must be > a)', desc='a number larger than a')
                            pts = Diff.FindInflectionPoints(f, a, b)
                            if not pts:
                                print(f'\n  No inflection points found in [{a}, {b}].')
                            else:
                                print(f'\n  Inflection points in [{a}, {b}]:')
                                for p in pts:
                                    print(f'    x ≈ {p:.6f}   f(x) = {f(p):.6f}')
                        case 7:
                            f = _get_f('f(x)')
                            a = _ask('Left bound a')
                            b = _ask('Right bound b  (must be > a)', desc='a number larger than a')
                            classified = Diff.ClassifyCriticalPoints(f, a, b)
                            if not classified:
                                print(f'\n  No critical points found in [{a}, {b}].')
                            else:
                                print(f'\n  Critical points in [{a}, {b}]:')
                                for x_val, label in classified:
                                    print(f'    x ≈ {x_val:.6f}   f(x) = {f(x_val):.6f}   →  {label}')
                        case _: print('  That was not a valid option.')
            except _AskAbort:
                print()
                _p('Calculation cancelled. Returning to the function list.')
            print()

# ============================================================
# STATISTICS DEBUG
# ============================================================

def StatisticsDebug():

    def _data(label='dataset'):
        _p(f'Enter the {label} as numbers separated by spaces or commas.')
        return _ask_list('  Values', cast=float, min_count=1)

    def _data2(label1='first dataset', label2='second dataset'):
        _p(f'Enter the {label1}:')
        d1 = _ask_list('  Values', cast=float, min_count=2)
        _p(f'Enter the {label2}:')
        d2 = _ask_list('  Values', cast=float, min_count=2)
        return d1, d2

    SECTIONS = [
        'Central Tendency  (mean, median, mode)',
        'Spread & Variability  (variance, std dev, IQR)',
        'Position & Shape  (percentiles, quartiles, skewness)',
        'Discrete Distributions  (binomial, Poisson)',
        'Continuous Distributions  (normal, exponential, uniform)',
        'Statistical Inference  (confidence intervals, sample size)',
        'Hypothesis Testing  (z-test, t-test, chi-squared)',
        'Correlation & Regression  (Pearson, linear regression)',
    ]

    while True:
        _SectionHeader('Statistics', 'Choose a section')
        for i, s in enumerate(SECTIONS, 1):
            print(f'  ({i})  {s}')
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section number. Please try again.')
            continue

        while True:
            _SectionHeader('Statistics', SECTIONS[sec - 1])
            if sec == 1:
                print('  (1)  Mean             (arithmetic average)')
                print('  (2)  Median           (middle value)')
                print('  (3)  Mode             (most frequent value)')
                print('  (4)  Midrange         (halfway between min and max)')
                print('  (5)  Weighted mean    (each value has a weight)')
                print('  (6)  Geometric mean   (nth root of the product)')
                print('  (7)  Harmonic mean    (reciprocal average)')
            elif sec == 2:
                print('  (1)  Range             (max − min)')
                print('  (2)  Variance          (population or sample)')
                print('  (3)  Standard deviation')
                print('  (4)  Interquartile range  (IQR = Q3 − Q1)')
                print('  (5)  Coefficient of variation  (std dev / mean)')
                print('  (6)  Mean absolute deviation  (MAD)')
            elif sec == 3:
                print('  (1)  Z-score          (how many std devs from the mean)')
                print('  (2)  Value from z-score')
                print('  (3)  Percentile        (value at the p-th percentile)')
                print('  (4)  Quartiles         (Q1, Q2, Q3)')
                print('  (5)  Five-number summary')
                print('  (6)  Skewness          (symmetry of distribution)')
                print('  (7)  Kurtosis          (tail weight)')
            elif sec == 4:
                _p('These distributions model count data.  n = number of trials, '
                   'k = successes, p = probability of success, λ = average rate.')
                print()
                print('  (1)  Binomial PMF      P(X = k)  for n trials')
                print('  (2)  Binomial CDF      P(X ≤ k)  cumulative')
                print('  (3)  Poisson PMF       P(X = k)  given average rate λ')
                print('  (4)  Poisson CDF       P(X ≤ k)  cumulative')
            elif sec == 5:
                _p('These distributions model continuous measurements.  '
                   'μ and σ are mean and standard deviation for the normal distribution.')
                print()
                print('  (1)  Normal PDF        f(x)  — height of the bell curve at x')
                print('  (2)  Normal CDF        P(X ≤ x)  — area under the curve to x')
                print('  (3)  Normal between    P(a ≤ X ≤ b)')
                print('  (4)  Exponential PDF   f(x)  given rate λ')
                print('  (5)  Exponential CDF   P(X ≤ x)  given rate λ')
                print('  (6)  Uniform PDF       f(x)  on interval [a, b]')
                print('  (7)  Uniform CDF       P(X ≤ x)  on interval [a, b]')
            elif sec == 6:
                _p('Inference uses sample data to estimate population parameters.')
                print()
                print('  (1)  Standard error     SE = σ / √n')
                print('  (2)  Margin of error    ME = z · SE')
                print('  (3)  Confidence interval   (mean ± ME)')
                print('  (4)  Required sample size   to achieve a target margin of error')
                print('  (5)  Point estimate         (sample mean as estimate of μ)')
                print('  (6)  Pooled variance        (for two-sample tests)')
            elif sec == 7:
                _p('Hypothesis tests determine whether sample data provides evidence '
                   'against a null hypothesis.')
                print()
                print('  (1)  Z-test statistic    z = (x̄ − μ) / (σ/√n)')
                print('  (2)  One-sample t-test   t from sample data')
                print('  (3)  Two-sample t-test   t comparing two groups')
                print('  (4)  P-value from z      P(Z > |z|)  two-tailed')
                print('  (5)  Reject null?         given z-statistic and significance level')
                print('  (6)  Chi-squared statistic   Σ (O−E)²/E')
            elif sec == 8:
                _p('Correlation and regression measure and model the relationship '
                   'between two variables.')
                print()
                print('  (1)  Pearson correlation    r  (linear relationship strength)')
                print('  (2)  Spearman correlation   ρ  (rank-based, works for non-linear)')
                print('  (3)  Covariance             Cov(X, Y)')
                print('  (4)  Linear regression      slope and intercept of best-fit line')
                print('  (5)  Predict y              using regression line at x')
                print('  (6)  R-squared              how well the line fits the data')
            print()
            _ExitBar('Return to sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            print()
            try:
                if sec == 1:
                    match choice:
                        case 1:
                            data = _data()
                            print(f'\n  Mean  =  {Stat.Mean(data):.6f}')
                        case 2:
                            data = _data()
                            print(f'\n  Median  =  {Stat.Median(data):.6f}')
                        case 3:
                            data = _data()
                            modes = Stat.Mode(data)
                            print(f'\n  Mode(s):  {modes}')
                        case 4:
                            data = _data()
                            print(f'\n  Midrange  =  {Stat.Midrange(data):.6f}')
                        case 5:
                            _p('Enter values and their corresponding weights as two lists.')
                            vals    = _ask_list('  Values',  cast=float, min_count=1)
                            weights = _ask_list('  Weights (same count as values)', cast=float, min_count=len(vals))
                            print(f'\n  Weighted mean  =  {Stat.WeightedMean(vals, weights[:len(vals)]):.6f}')
                        case 6:
                            data = _data()
                            print(f'\n  Geometric mean  =  {Stat.GeometricMean(data):.6f}')
                        case 7:
                            data = _data()
                            print(f'\n  Harmonic mean  =  {Stat.HarmonicMean(data):.6f}')
                        case _: print('  That was not a valid option.')
                elif sec == 2:
                    match choice:
                        case 1:
                            data = _data()
                            print(f'\n  Range  =  max − min  =  {Stat.Range(data):.6f}')
                        case 2:
                            data = _data()
                            pop  = input('  Population variance (p) or sample variance (s)?  [Enter = p]: ').strip().lower()
                            is_pop = (pop != 's')
                            v = Stat.Variance(data, population=is_pop)
                            print(f'\n  {"Population" if is_pop else "Sample"} variance  =  {v:.6f}')
                        case 3:
                            data = _data()
                            pop  = input('  Population (p) or sample (s)?  [Enter = p]: ').strip().lower()
                            is_pop = (pop != 's')
                            sd = Stat.StandardDeviation(data, population=is_pop)
                            print(f'\n  {"Population" if is_pop else "Sample"} std dev  =  {sd:.6f}')
                        case 4:
                            data = _data()
                            print(f'\n  IQR  =  Q3 − Q1  =  {Stat.IQR(data):.6f}')
                        case 5:
                            data = _data()
                            cv = Stat.CoefficientOfVariation(data)
                            print(f'\n  Coefficient of variation  =  {cv:.4f}  ({cv*100:.2f} %)')
                        case 6:
                            data = _data()
                            print(f'\n  Mean absolute deviation  =  {Stat.MeanAbsoluteDeviation(data):.6f}')
                        case _: print('  That was not a valid option.')
                elif sec == 3:
                    match choice:
                        case 1:
                            x   = _ask('Observed value x')
                            mu  = _ask('Population mean μ')
                            sig = _ask('Population std dev σ  (must be > 0)', desc='a positive number')
                            z   = Stat.ZScore(x, mu, sig)
                            print(f'\n  z = (x − μ) / σ = ({x} − {mu}) / {sig} = {z:.4f}')
                            _p(f'This value is {abs(z):.2f} standard deviations '
                               f'{"above" if z >= 0 else "below"} the mean.')
                        case 2:
                            z   = _ask('Z-score')
                            mu  = _ask('Population mean μ')
                            sig = _ask('Population std dev σ  (must be > 0)', desc='a positive number')
                            val = Stat.ZScoreToValue(z, mu, sig)
                            print(f'\n  x = μ + z·σ = {mu} + {z}×{sig} = {val:.6f}')
                        case 3:
                            data = _data()
                            p    = _ask('Percentile p  (0 to 100)', desc='a number between 0 and 100')
                            print(f'\n  {p}th percentile  =  {Stat.Percentile(data, p):.6f}')
                        case 4:
                            data = _data()
                            q1, q2, q3 = Stat.Quartiles(data)
                            print(f'\n  Q1 = {q1:.4f}   Q2 (median) = {q2:.4f}   Q3 = {q3:.4f}')
                            print(f'  IQR = Q3 − Q1 = {q3-q1:.4f}')
                        case 5:
                            data = _data()
                            mn, q1, med, q3, mx = Stat.FiveNumberSummary(data)
                            print(f'\n  Min    =  {mn:.4f}')
                            print(f'  Q1     =  {q1:.4f}')
                            print(f'  Median =  {med:.4f}')
                            print(f'  Q3     =  {q3:.4f}')
                            print(f'  Max    =  {mx:.4f}')
                            print(f'  IQR    =  {q3-q1:.4f}')
                        case 6:
                            data = _data()
                            sk = Stat.Skewness(data)
                            direction = 'right (positive) skew' if sk > 0.1 else 'left (negative) skew' if sk < -0.1 else 'approximately symmetric'
                            print(f'\n  Skewness  =  {sk:.6f}   →  {direction}')
                        case 7:
                            data = _data()
                            ku = Stat.Kurtosis(data)
                            shape = 'heavy tails (leptokurtic)' if ku > 3.1 else 'light tails (platykurtic)' if ku < 2.9 else 'normal-like tails (mesokurtic)'
                            print(f'\n  Kurtosis  =  {ku:.6f}   →  {shape}')
                        case _: print('  That was not a valid option.')
                elif sec == 4:
                    match choice:
                        case 1:
                            n = _ask_int('n  (number of trials)', desc='a positive whole number')
                            k = _ask_int('k  (number of successes, 0 to n)', desc='a whole number from 0 to n')
                            p = _ask('p  (probability of success, 0 to 1)', desc='a number between 0 and 1')
                            pmf = Stat.BinomialPMF(n, k, p)
                            print(f'\n  P(X = {k})  =  C({n},{k}) · {p}^{k} · {1-p:.4f}^{n-k}  =  {pmf:.6f}')
                        case 2:
                            n = _ask_int('n  (number of trials)', desc='a positive whole number')
                            k = _ask_int('k  (at most this many successes)', desc='a whole number from 0 to n')
                            p = _ask('p  (probability of success)', desc='a number between 0 and 1')
                            cdf = Stat.BinomialCDF(n, k, p)
                            print(f'\n  P(X ≤ {k})  =  {cdf:.6f}')
                        case 3:
                            lam = _ask('λ  (expected number of events)', desc='a positive number')
                            k   = _ask_int('k  (number of events to find probability for)', desc='a whole number ≥ 0')
                            pmf = Stat.PoissonPMF(lam, k)
                            print(f'\n  P(X = {k} | λ={lam})  =  {pmf:.6f}')
                        case 4:
                            lam = _ask('λ  (expected number of events)', desc='a positive number')
                            k   = _ask_int('k  (at most this many events)', desc='a whole number ≥ 0')
                            cdf = Stat.PoissonCDF(lam, k)
                            print(f'\n  P(X ≤ {k} | λ={lam})  =  {cdf:.6f}')
                        case _: print('  That was not a valid option.')
                elif sec == 5:
                    match choice:
                        case 1:
                            x   = _ask('x value')
                            mu  = _ask('Mean μ  [Enter 0 for standard normal]') if input('  Use non-standard parameters? (y/n) [n]: ').strip().lower() == 'y' else 0.0
                            sig = _ask('Std dev σ  (must be > 0)', desc='a positive number') if mu != 0 else 1.0
                            print(f'\n  Normal PDF  f({x})  =  {Stat.NormalPDF(x, mu, sig):.6f}')
                        case 2:
                            x   = _ask('x value')
                            custom = input('  Use non-standard parameters? (y/n) [n]: ').strip().lower() == 'y'
                            mu  = _ask('Mean μ') if custom else 0.0
                            sig = _ask('Std dev σ  (must be > 0)', desc='a positive number') if custom else 1.0
                            p   = Stat.NormalCDF(x, mu, sig)
                            print(f'\n  P(X ≤ {x})  =  {p:.6f}   ({p*100:.2f}%)')
                        case 3:
                            a   = _ask('Lower bound a')
                            b   = _ask('Upper bound b  (must be > a)', desc='a number larger than a')
                            custom = input('  Use non-standard parameters? (y/n) [n]: ').strip().lower() == 'y'
                            mu  = _ask('Mean μ') if custom else 0.0
                            sig = _ask('Std dev σ  (must be > 0)', desc='a positive number') if custom else 1.0
                            p   = Stat.NormalProbBetween(a, b, mu, sig)
                            print(f'\n  P({a} ≤ X ≤ {b})  =  {p:.6f}   ({p*100:.2f}%)')
                        case 4:
                            lam = _ask('Rate λ  (must be > 0)', desc='a positive number')
                            x   = _ask('x value  (must be ≥ 0)', desc='a non-negative number')
                            print(f'\n  Exponential PDF  f({x} | λ={lam})  =  {Stat.ExponentialPDF(lam, x):.6f}')
                        case 5:
                            lam = _ask('Rate λ  (must be > 0)', desc='a positive number')
                            x   = _ask('x value  (must be ≥ 0)', desc='a non-negative number')
                            p   = Stat.ExponentialCDF(lam, x)
                            print(f'\n  P(X ≤ {x} | λ={lam})  =  {p:.6f}   ({p*100:.2f}%)')
                        case 6:
                            a = _ask('Lower bound a')
                            b = _ask('Upper bound b  (must be > a)', desc='a number larger than a')
                            x = _ask('x value')
                            print(f'\n  Uniform PDF  f({x} | a={a}, b={b})  =  {Stat.UniformPDF(x, a, b):.6f}')
                        case 7:
                            a = _ask('Lower bound a')
                            b = _ask('Upper bound b  (must be > a)', desc='a number larger than a')
                            x = _ask('x value')
                            p = Stat.UniformCDF(x, a, b)
                            print(f'\n  P(X ≤ {x} | a={a}, b={b})  =  {p:.6f}   ({p*100:.2f}%)')
                        case _: print('  That was not a valid option.')
                elif sec == 6:
                    match choice:
                        case 1:
                            sig = _ask('Population std dev σ', desc='a positive number')
                            n   = _ask_int('Sample size n', desc='a positive whole number')
                            se  = Stat.StandardError(sig, n)
                            print(f'\n  Standard error  SE = σ/√n = {sig}/√{n} = {se:.6f}')
                        case 2:
                            z   = _ask('z-score for confidence level  (e.g. 1.96 for 95%)',
                                       desc='a positive number like 1.645 or 1.96 or 2.576')
                            sig = _ask('Population std dev σ')
                            n   = _ask_int('Sample size n', desc='a positive whole number')
                            me  = Stat.MarginOfError(z, sig, n)
                            print(f'\n  Margin of error  ME = z·σ/√n = {z}×{sig}/√{n} = {me:.6f}')
                        case 3:
                            mean = _ask('Sample mean x̄')
                            z    = _ask('z-score for confidence level  (e.g. 1.96 for 95%)')
                            sig  = _ask('Population std dev σ')
                            n    = _ask_int('Sample size n')
                            lo, hi = Stat.ConfidenceInterval(mean, z, sig, n)
                            me   = Stat.MarginOfError(z, sig, n)
                            print(f'\n  Confidence interval:  ({lo:.4f},  {hi:.4f})')
                            print(f'  =  {mean} ± {me:.4f}')
                        case 4:
                            z   = _ask('z-score for confidence level')
                            sig = _ask('Population std dev σ')
                            E   = _ask('Desired margin of error E  (must be > 0)', desc='a positive number')
                            n   = Stat.RequiredSampleSize(z, sig, E)
                            print(f'\n  Required sample size  n ≥ {n}  (rounded up)')
                        case 5:
                            data = _data()
                            pe   = Stat.PointEstimate(data)
                            print(f'\n  Point estimate (sample mean)  =  {pe:.6f}')
                        case 6:
                            d1, d2 = _data2()
                            pv     = Stat.PooledVariance(d1, d2)
                            print(f'\n  Pooled variance  =  {pv:.6f}')
                        case _: print('  That was not a valid option.')
                elif sec == 7:
                    match choice:
                        case 1:
                            xbar = _ask('Sample mean x̄')
                            mu   = _ask('Hypothesised population mean μ₀')
                            sig  = _ask('Population std dev σ  (must be > 0)', desc='a positive number')
                            n    = _ask_int('Sample size n', desc='a positive whole number')
                            z    = Stat.ZTestStatistic(xbar, mu, sig, n)
                            print(f'\n  z = (x̄ − μ₀) / (σ/√n) = ({xbar} − {mu}) / ({sig}/√{n}) = {z:.4f}')
                        case 2:
                            data = _data('sample (raw data)')
                            mu0  = _ask('Hypothesised mean μ₀')
                            t    = Stat.TTestStatistic(data, mu0)
                            print(f'\n  t-statistic  =  {t:.4f}   (df = {len(data)-1})')
                        case 3:
                            d1, d2 = _data2('first group', 'second group')
                            t, df  = Stat.TwoSampleTTest(d1, d2)
                            print(f'\n  Two-sample t  =  {t:.4f}   (df ≈ {df:.1f})')
                        case 4:
                            z = _ask('z-statistic')
                            p = Stat.PValueFromZ(z)
                            print(f'\n  Two-tailed p-value  =  {p:.6f}   ({p*100:.3f}%)')
                            print(f'  {"Reject H₀ at α=0.05" if p < 0.05 else "Do not reject H₀ at α=0.05"}')
                        case 5:
                            z     = _ask('z-statistic')
                            alpha = _ask('Significance level α  (e.g. 0.05)',
                                         desc='a small positive number like 0.01, 0.05, or 0.10')
                            rej   = Stat.RejectNull(z, alpha)
                            print(f'\n  At α = {alpha}:  {"Reject H₀ — result is statistically significant" if rej else "Fail to reject H₀ — result is not significant"}')
                        case 6:
                            _p('Enter observed counts then expected counts as two separate lists.')
                            obs = _ask_list('  Observed counts', cast=float, min_count=2)
                            exp = _ask_list('  Expected counts (same length as observed)', cast=float, min_count=len(obs))
                            chi = Stat.ChiSquaredStatistic(obs, exp[:len(obs)])
                            print(f'\n  χ² = Σ(O−E)²/E  =  {chi:.6f}')
                        case _: print('  That was not a valid option.')
                elif sec == 8:
                    match choice:
                        case 1:
                            d1, d2 = _data2('x values', 'y values')
                            r = Stat.PearsonCorrelation(d1, d2)
                            strength = 'strong' if abs(r) > 0.7 else 'moderate' if abs(r) > 0.4 else 'weak'
                            direction = 'positive' if r > 0 else 'negative'
                            print(f'\n  Pearson r  =  {r:.6f}')
                            _p(f'Interpretation: {strength} {direction} linear relationship.')
                        case 2:
                            d1, d2 = _data2('x values', 'y values')
                            rho = Stat.SpearmanCorrelation(d1, d2)
                            print(f'\n  Spearman ρ  =  {rho:.6f}')
                        case 3:
                            d1, d2 = _data2('x values', 'y values')
                            cov = Stat.Covariance(d1, d2)
                            print(f'\n  Covariance  Cov(X, Y)  =  {cov:.6f}')
                        case 4:
                            d1, d2 = _data2('x values', 'y values')
                            slope, intercept = Stat.LinearRegression(d1, d2)
                            print(f'\n  Best-fit line:  y = {slope:.6f}·x + {intercept:.6f}')
                        case 5:
                            d1, d2 = _data2('x values (for fitting)', 'y values (for fitting)')
                            slope, intercept = Stat.LinearRegression(d1, d2)
                            xp = _ask('x value to predict y at')
                            yp = Stat.Predict(xp, slope, intercept)
                            print(f'\n  ŷ at x={xp}  =  {yp:.6f}')
                        case 6:
                            d1, d2 = _data2('x values', 'y values')
                            r2 = Stat.RSquared(d1, d2)
                            print(f'\n  R²  =  {r2:.6f}   ({r2*100:.2f}% of variance explained)')
                        case _: print('  That was not a valid option.')
            except _AskAbort:
                print()
                _p('Calculation cancelled. Returning to the function list.')
            print()

# ============================================================
# PROBABILITY DEBUG
# ============================================================

def ProbabilityDebug():

    def _data(label='values'):
        _p(f'Enter the {label} as numbers separated by spaces or commas.')
        return _ask_list('  Values', cast=float, min_count=1)

    SECTIONS = [
        'Basic Probability',
        'Conditional & Multiplication Rules',
        'Bayes\'s Theorem',
        'Counting & Odds',
        'Random Variables  (expected value, variance)',
        'Discrete Distributions  (binomial, Poisson, geometric, hypergeometric)',
        'Continuous Distributions  (normal, exponential, uniform)',
        'Central Limit Theorem',
        'Markov Chains',
        'Simulations',
        'Information Theory  (entropy, KL divergence)',
    ]

    while True:
        _SectionHeader('Probability', 'Choose a section')
        for i, s in enumerate(SECTIONS, 1):
            print(f'  ({i:>2})  {s}')
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section number. Please try again.')
            continue

        while True:
            _SectionHeader('Probability', SECTIONS[sec - 1])
            if sec == 1:
                print('  (1)  Classical probability   favourable / total outcomes')
                print('  (2)  Complement              P(not A) = 1 − P(A)')
                print('  (3)  Union                  P(A or B) = P(A)+P(B)−P(A∩B)')
                print('  (4)  Intersection           P(A and B) from union/add rule')
                print('  (5)  Mutually exclusive union  P(A or B) = P(A)+P(B)')
                print('  (6)  Independent intersection  P(A and B) = P(A)·P(B)')
            elif sec == 2:
                print('  (1)  Are events mutually exclusive?    P(A∩B) = 0?')
                print('  (2)  Are events independent?           P(A∩B) = P(A)·P(B)?')
                print('  (3)  Conditional probability           P(A|B) = P(A∩B)/P(B)')
                print('  (4)  Multiplication rule               P(A∩B) = P(A|B)·P(B)')
            elif sec == 3:
                _p('Bayes\'s theorem updates a prior probability given new evidence.')
                print()
                print('  (1)  Bayes\'s theorem          P(A|B) from P(B|A), P(A), P(B)')
                print('  (2)  Total probability rule   P(B) = Σ P(B|Aᵢ)·P(Aᵢ)')
                print('  (3)  Full Bayes partition     all posterior probabilities P(Aᵢ|B)')
            elif sec == 4:
                print('  (1)  Permutations              nPr = n! / (n−r)!')
                print('  (2)  Combinations              nCr = n! / (r!·(n−r)!)')
                print('  (3)  Circular permutations     (n−1)!')
                print('  (4)  Permutations with repetition  nʳ')
                print('  (5)  Combinations with repetition  C(n+r−1, r)')
                print('  (6)  Multinomial                n! / (n₁!·n₂!···nₖ!)')
                print('  (7)  Odds in favour             p / (1−p)')
                print('  (8)  Odds to probability        odds / (1+odds)')
            elif sec == 5:
                _p('Enter values and their probabilities as two lists of the same length.  '
                   'Probabilities should sum to 1.')
                print()
                print('  (1)  Expected value           E(X) = Σ xᵢ·P(xᵢ)')
                print('  (2)  Variance                 Var(X) = E(X²) − [E(X)]²')
                print('  (3)  Standard deviation       σ = √Var(X)')
                print('  (4)  Linear transform E       E(aX+b) = a·E(X)+b')
                print('  (5)  Linear transform Var     Var(aX+b) = a²·Var(X)')
                print('  (6)  Sum of two RVs  E        E(X+Y) = E(X)+E(Y)')
                print('  (7)  Sum of two RVs  Var      Var(X+Y) = Var(X)+Var(Y)  (if independent)')
            elif sec == 6:
                print('  (1)  Binomial PMF              P(X=k) for n trials')
                print('  (2)  Binomial mean and variance')
                print('  (3)  Poisson PMF               P(X=k | λ)')
                print('  (4)  Poisson mean and variance  (both equal λ)')
                print('  (5)  Geometric PMF             P(X=k)  (k trials until first success)')
                print('  (6)  Geometric mean and variance')
                print('  (7)  Negative binomial PMF     P(X=k)  (k trials for r successes)')
                print('  (8)  Hypergeometric PMF        P(X=k)  (sampling without replacement)')
                print('  (9)  Hypergeometric mean')
            elif sec == 7:
                print('  (1)  Normal PDF               f(x)')
                print('  (2)  Normal CDF               P(X ≤ x)')
                print('  (3)  Normal between           P(a ≤ X ≤ b)')
                print('  (4)  Inverse normal CDF       x such that P(X ≤ x) = p')
                print('  (5)  Exponential PDF          f(x | λ)')
                print('  (6)  Exponential CDF          P(X ≤ x | λ)')
                print('  (7)  Exponential mean         E(X) = 1/λ')
                print('  (8)  Uniform PDF              f(x | a, b)')
                print('  (9)  Uniform CDF              P(X ≤ x | a, b)')
                print('  (10) Uniform mean and variance')
            elif sec == 8:
                _p('The Central Limit Theorem states that the sample mean approaches '
                   'a normal distribution as sample size grows, regardless of the original distribution.')
                print()
                print('  (1)  Sampling distribution mean   μ_x̄ = μ')
                print('  (2)  Sampling std dev             σ_x̄ = σ/√n')
                print('  (3)  CLT z-score                  z = (x̄ − μ) / (σ/√n)')
                print('  (4)  P(X̄ ≤ value)')
                print('  (5)  P(a ≤ X̄ ≤ b)')
            elif sec == 9:
                _p('Markov chains model systems that transition between states '
                   'based only on the current state.')
                print()
                print('  (1)  Next state vector         after one transition')
                print('  (2)  State after k steps')
                print('  (3)  Stationary distribution   long-run state probabilities')
            elif sec == 10:
                _p('These tools simulate random experiments numerically.')
                print()
                print('  (1)  Simulate Bernoulli trials     n flips with probability p')
                print('  (2)  Simulated proportion          from n Bernoulli trials')
                print('  (3)  Empirical probability         from simulation')
                print('  (4)  Simulated expected value      from random variable and distribution')
            elif sec == 11:
                _p('Information theory measures uncertainty and information content.')
                print()
                print('  (1)  Shannon entropy    H = −Σ pᵢ·log₂(pᵢ)  (bits)')
                print('  (2)  Natural entropy    H = −Σ pᵢ·ln(pᵢ)    (nats)')
                print('  (3)  Maximum entropy    for n equally likely outcomes')
                print('  (4)  Self-information   I(x) = −log₂(p)')
                print('  (5)  KL divergence      D_KL(P ∥ Q)  =  Σ pᵢ·log(pᵢ/qᵢ)')
            print()
            _ExitBar('Return to sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            print()
            try:
                if sec == 1:
                    match choice:
                        case 1:
                            fav   = _ask_int('Favourable outcomes', desc='a whole number ≥ 0')
                            total = _ask_int('Total outcomes  (must be > 0)', desc='a positive whole number')
                            p     = Prob.ClassicalProbability(fav, total)
                            print(f'\n  P  =  {fav}/{total}  =  {p:.6f}   ({p*100:.2f}%)')
                        case 2:
                            pa = _ask('P(A)  — probability of event A  (0 to 1)', desc='a number between 0 and 1')
                            print(f'\n  P(not A)  =  1 − {pa}  =  {Prob.Complement(pa):.6f}')
                        case 3:
                            pa  = _ask('P(A)', desc='a number between 0 and 1')
                            pb  = _ask('P(B)', desc='a number between 0 and 1')
                            pab = _ask('P(A and B)', desc='a number between 0 and 1')
                            print(f'\n  P(A or B)  =  P(A)+P(B)−P(A∩B)  =  {Prob.UnionProbability(pa,pb,pab):.6f}')
                        case 4:
                            pa     = _ask('P(A)')
                            pb     = _ask('P(B)')
                            pa_or_b = _ask('P(A or B)')
                            print(f'\n  P(A and B)  =  P(A)+P(B)−P(A or B)  =  {Prob.IntersectionProbability(pa,pb,pa_or_b):.6f}')
                        case 5:
                            pa = _ask('P(A)')
                            pb = _ask('P(B)')
                            print(f'\n  P(A or B)  =  P(A)+P(B)  =  {Prob.MutuallyExclusiveUnion(pa,pb):.6f}')
                            _p('Note: this formula only applies when A and B cannot both occur.')
                        case 6:
                            pa = _ask('P(A)')
                            pb = _ask('P(B)')
                            print(f'\n  P(A and B)  =  P(A)·P(B)  =  {Prob.IndependentIntersection(pa,pb):.6f}')
                            _p('Note: this formula only applies when A and B are independent events.')
                        case _: print('  That was not a valid option.')
                elif sec == 2:
                    match choice:
                        case 1:
                            pab = _ask('P(A and B)', desc='a number between 0 and 1')
                            me  = Prob.AreMutuallyExclusive(pab)
                            print(f'\n  Mutually exclusive?  {"Yes — they cannot both occur" if me else "No — they can occur together"}')
                        case 2:
                            pa  = _ask('P(A)')
                            pb  = _ask('P(B)')
                            pab = _ask('P(A and B)')
                            ind = Prob.AreIndependent(pa, pb, pab)
                            print(f'\n  Independent?  {"Yes — knowledge of one does not affect the other" if ind else "No — the events influence each other"}')
                        case 3:
                            pab = _ask('P(A and B)')
                            pb  = _ask('P(B)  (must be > 0)', desc='a positive number')
                            print(f'\n  P(A | B)  =  P(A∩B)/P(B)  =  {Prob.ConditionalProbability(pab,pb):.6f}')
                        case 4:
                            pa_b = _ask('P(A | B)  — probability of A given B')
                            pb   = _ask('P(B)')
                            print(f'\n  P(A and B)  =  P(A|B)·P(B)  =  {Prob.MultiplicationRule(pa_b,pb):.6f}')
                        case _: print('  That was not a valid option.')
                elif sec == 3:
                    match choice:
                        case 1:
                            pb_a = _ask('P(B | A)  — likelihood')
                            pa   = _ask('P(A)  — prior probability of A')
                            pb   = _ask('P(B)  — total probability of B  (must be > 0)', desc='a positive number')
                            post = Prob.Bayes(pb_a, pa, pb)
                            print(f'\n  P(A | B)  =  P(B|A)·P(A) / P(B)  =  {post:.6f}')
                        case 2:
                            n     = _ask_int('Number of hypotheses (Aᵢ)', desc='a positive whole number')
                            priors = _ask_list(f'  P(Aᵢ) — {n} prior probabilities', cast=float, min_count=n)
                            likelihoods = _ask_list(f'  P(B|Aᵢ) — {n} likelihoods', cast=float, min_count=n)
                            pb   = Prob.TotalProbability(likelihoods[:n], priors[:n])
                            print(f'\n  P(B)  =  Σ P(B|Aᵢ)·P(Aᵢ)  =  {pb:.6f}')
                        case 3:
                            n     = _ask_int('Number of hypotheses (Aᵢ)', desc='a positive whole number')
                            priors = _ask_list(f'  P(Aᵢ) — {n} prior probabilities', cast=float, min_count=n)
                            likelihoods = _ask_list(f'  P(B|Aᵢ) — {n} likelihoods', cast=float, min_count=n)
                            posts = Prob.BayesPartition(likelihoods[:n], priors[:n])
                            print(f'\n  Posterior probabilities P(Aᵢ | B):')
                            for i, p in enumerate(posts, 1):
                                print(f'    A{i}:  {p:.6f}   ({p*100:.2f}%)')
                        case _: print('  That was not a valid option.')
                elif sec == 4:
                    match choice:
                        case 1:
                            n = _ask_int('n  (total items)')
                            r = _ask_int('r  (items chosen, order matters)')
                            print(f'\n  P({n},{r})  =  n!/(n−r)!  =  {Prob.Permutations(n,r)}')
                        case 2:
                            n = _ask_int('n  (total items)')
                            r = _ask_int('r  (items chosen, order does not matter)')
                            print(f'\n  C({n},{r})  =  n!/(r!·(n−r)!)  =  {Prob.Combinations(n,r)}')
                        case 3:
                            n = _ask_int('n  (items arranged in a circle)')
                            print(f'\n  Circular permutations  =  (n−1)!  =  {Prob.CircularPermutations(n)}')
                        case 4:
                            n = _ask_int('n  (types of items)')
                            r = _ask_int('r  (length of sequence)')
                            print(f'\n  Permutations with repetition  =  n^r  =  {Prob.PermutationsWithRepetition(n,r)}')
                        case 5:
                            n = _ask_int('n  (types of items)')
                            r = _ask_int('r  (items to choose, repetition allowed)')
                            print(f'\n  Combinations with repetition  =  C(n+r−1,r)  =  {Prob.CombinationsWithRepetition(n,r)}')
                        case 6:
                            n      = _ask_int('n  (total items to arrange)')
                            k      = _ask_int('Number of groups k')
                            groups = _ask_list(f'  Sizes of the {k} groups (must sum to {n})', cast=int, min_count=k)
                            print(f'\n  Multinomial  =  n!/(n₁!·…·nₖ!)  =  {Prob.Multinomial(n, groups[:k])}')
                        case 7:
                            p = _ask('Probability of success p  (0 to 1)', desc='a number between 0 and 1')
                            odds_for, odds_against = Prob.OddsInFavor(p)
                            print(f'\n  Odds in favour:  {odds_for:.4f} : {odds_against:.4f}')
                        case 8:
                            odds = _ask('Odds in favour  (e.g. enter 3 for 3:1 odds)')
                            p    = Prob.OddsToProb(odds)
                            print(f'\n  Probability  =  {odds} / (1+{odds})  =  {p:.6f}')
                        case _: print('  That was not a valid option.')
                elif sec == 5:
                    def _vp():
                        vals  = _ask_list('  Outcome values', cast=float, min_count=2)
                        probs = _ask_list(f'  Probabilities (must sum to 1, {len(vals)} values)', cast=float, min_count=len(vals))
                        return vals, probs[:len(vals)]
                    match choice:
                        case 1:
                            vals, probs = _vp()
                            ev = Prob.ExpectedValue(vals, probs)
                            print(f'\n  E(X)  =  {ev:.6f}')
                        case 2:
                            vals, probs = _vp()
                            v = Prob.Variance(vals, probs)
                            print(f'\n  Var(X)  =  E(X²) − [E(X)]²  =  {v:.6f}')
                        case 3:
                            vals, probs = _vp()
                            sd = Prob.StandardDeviation(vals, probs)
                            print(f'\n  σ(X)  =  √Var(X)  =  {sd:.6f}')
                        case 4:
                            a   = _ask('Constant a  (scale factor)')
                            ex  = _ask('E(X)  — expected value of X')
                            b   = _ask('Constant b  (shift)')
                            print(f'\n  E({a}X+{b})  =  {a}·E(X)+{b}  =  {Prob.LinearTransformExpected(a,ex,b):.6f}')
                        case 5:
                            a   = _ask('Constant a  (scale factor)')
                            var = _ask('Var(X)  — variance of X')
                            print(f'\n  Var({a}X+b)  =  {a}²·Var(X)  =  {Prob.LinearTransformVariance(a,var):.6f}')
                        case 6:
                            ex = _ask('E(X)')
                            ey = _ask('E(Y)')
                            print(f'\n  E(X+Y)  =  E(X)+E(Y)  =  {Prob.SumExpected(ex,ey):.6f}')
                        case 7:
                            vx = _ask('Var(X)')
                            vy = _ask('Var(Y)')
                            print(f'\n  Var(X+Y)  =  Var(X)+Var(Y)  =  {Prob.SumVariance(vx,vy):.6f}')
                            _p('Note: this formula only applies when X and Y are independent.')
                        case _: print('  That was not a valid option.')
                elif sec == 6:
                    match choice:
                        case 1:
                            n = _ask_int('n  (number of trials)')
                            k = _ask_int('k  (number of successes)')
                            p = _ask('p  (probability of success on each trial)', desc='a number between 0 and 1')
                            print(f'\n  P(X={k} | n={n}, p={p})  =  {Prob.BinomialPMF(n,k,p):.6f}')
                        case 2:
                            n = _ask_int('n  (number of trials)')
                            p = _ask('p  (probability of success)', desc='a number between 0 and 1')
                            mu  = Prob.BinomialMean(n, p)
                            var = Prob.BinomialVariance(n, p)
                            print(f'\n  Mean      E(X) = np    = {mu:.4f}')
                            print(f'  Variance  Var(X) = np(1−p) = {var:.4f}')
                            print(f'  Std dev   σ = √Var    = {var**0.5:.4f}')
                        case 3:
                            lam = _ask('λ  (expected number of events)', desc='a positive number')
                            k   = _ask_int('k  (specific count)', desc='a whole number ≥ 0')
                            print(f'\n  P(X={k} | λ={lam})  =  {Prob.PoissonPMF(lam,k):.6f}')
                        case 4:
                            lam = _ask('λ  (expected number of events)', desc='a positive number')
                            mu, var = Prob.PoissonMeanVariance(lam)
                            print(f'\n  Mean  =  Variance  =  λ  =  {mu:.4f}')
                        case 5:
                            p = _ask('p  (probability of success on each trial)', desc='a number between 0 and 1')
                            k = _ask_int('k  (trial number of the first success)', desc='a positive whole number')
                            print(f'\n  P(X={k} | p={p})  =  (1−p)^(k−1)·p  =  {Prob.GeometricPMF(p,k):.6f}')
                        case 6:
                            p   = _ask('p  (probability of success)', desc='a number between 0 and 1')
                            mu  = Prob.GeometricMean(p)
                            var = Prob.GeometricVariance(p)
                            print(f'\n  Mean  E(X)  = 1/p         = {mu:.4f}')
                            print(f'  Var   Var(X) = (1−p)/p²   = {var:.4f}')
                        case 7:
                            r = _ask_int('r  (number of successes needed)')
                            k = _ask_int('k  (total trials, must be ≥ r)', desc='a whole number ≥ r')
                            p = _ask('p  (probability of success per trial)', desc='a number between 0 and 1')
                            print(f'\n  P(X={k} | r={r}, p={p})  =  {Prob.NegativeBinomialPMF(r,k,p):.6f}')
                        case 8:
                            N = _ask_int('N  (population size)')
                            K = _ask_int('K  (number of successes in population)')
                            n = _ask_int('n  (sample size drawn)')
                            k = _ask_int('k  (successes in sample)')
                            print(f'\n  P(X={k})  =  {Prob.HypergeometricPMF(N,K,n,k):.6f}')
                        case 9:
                            N = _ask_int('N  (population size)')
                            K = _ask_int('K  (successes in population)')
                            n = _ask_int('n  (sample size)')
                            mu = Prob.HypergeometricMean(N, K, n)
                            print(f'\n  Hypergeometric mean  E(X)  =  n·K/N  =  {mu:.4f}')
                        case _: print('  That was not a valid option.')
                elif sec == 7:
                    def _normal_params():
                        custom = input('  Use non-standard parameters? (y/n) [n]: ').strip().lower() == 'y'
                        if custom:
                            mu  = _ask('Mean μ')
                            sig = _ask('Std dev σ  (must be > 0)', desc='a positive number')
                        else:
                            mu, sig = 0.0, 1.0
                        return mu, sig
                    match choice:
                        case 1:
                            x       = _ask('x value')
                            mu, sig = _normal_params()
                            print(f'\n  Normal PDF  f({x})  =  {Prob.NormalPDF(x,mu,sig):.6f}')
                        case 2:
                            x       = _ask('x value')
                            mu, sig = _normal_params()
                            p       = Prob.NormalCDF(x, mu, sig)
                            print(f'\n  P(X ≤ {x})  =  {p:.6f}   ({p*100:.2f}%)')
                        case 3:
                            a       = _ask('Lower bound a')
                            b       = _ask('Upper bound b  (must be > a)', desc='a number larger than a')
                            mu, sig = _normal_params()
                            p       = Prob.NormalBetween(a, b, mu, sig)
                            print(f'\n  P({a} ≤ X ≤ {b})  =  {p:.6f}   ({p*100:.2f}%)')
                        case 4:
                            p       = _ask('Target probability p  (0 to 1)', desc='a number between 0 and 1')
                            mu, sig = _normal_params()
                            x       = Prob.InverseNormalCDF(p)
                            x_adj   = mu + sig * x
                            print(f'\n  x such that P(Z ≤ x) = {p}  →  x = {x:.6f}')
                            if mu != 0 or sig != 1:
                                print(f'  Adjusted for μ={mu}, σ={sig}:  x = {x_adj:.6f}')
                        case 5:
                            lam = _ask('Rate λ  (must be > 0)', desc='a positive number')
                            x   = _ask('x value  (must be ≥ 0)', desc='a non-negative number')
                            print(f'\n  Exp PDF  f({x} | λ={lam})  =  {Prob.ExponentialPDF(lam,x):.6f}')
                        case 6:
                            lam = _ask('Rate λ  (must be > 0)', desc='a positive number')
                            x   = _ask('x value  (must be ≥ 0)', desc='a non-negative number')
                            p   = Prob.ExponentialCDF(lam, x)
                            print(f'\n  P(X ≤ {x} | λ={lam})  =  {p:.6f}   ({p*100:.2f}%)')
                        case 7:
                            lam  = _ask('Rate λ  (must be > 0)', desc='a positive number')
                            mean = Prob.ExponentialMean(lam)
                            print(f'\n  E(X)  =  1/λ  =  1/{lam}  =  {mean:.6f}')
                        case 8:
                            a = _ask('Lower bound a')
                            b = _ask('Upper bound b  (must be > a)', desc='a number larger than a')
                            x = _ask('x value')
                            print(f'\n  Uniform PDF  f({x} | [{a},{b}])  =  {Prob.UniformPDF(x,a,b):.6f}')
                        case 9:
                            a = _ask('Lower bound a')
                            b = _ask('Upper bound b  (must be > a)', desc='a number larger than a')
                            x = _ask('x value')
                            p = Prob.UniformCDF(x, a, b)
                            print(f'\n  P(X ≤ {x} | [{a},{b}])  =  {p:.6f}   ({p*100:.2f}%)')
                        case 10:
                            a   = _ask('Lower bound a')
                            b   = _ask('Upper bound b  (must be > a)', desc='a number larger than a')
                            mu  = Prob.UniformMean(a, b)
                            var = Prob.UniformVariance(a, b)
                            print(f'\n  Mean      E(X)  = (a+b)/2    = {mu:.4f}')
                            print(f'  Variance  Var(X) = (b−a)²/12  = {var:.4f}')
                        case _: print('  That was not a valid option.')
                elif sec == 8:
                    match choice:
                        case 1:
                            mu  = _ask('Population mean μ')
                            print(f'\n  Sampling distribution mean  μ_x̄  =  μ  =  {Prob.SamplingDistributionMean(mu):.6f}')
                        case 2:
                            sig = _ask('Population std dev σ  (must be > 0)', desc='a positive number')
                            n   = _ask_int('Sample size n', desc='a positive whole number')
                            se  = Prob.SamplingDistributionStdDev(sig, n)
                            print(f'\n  σ_x̄  =  σ/√n  =  {sig}/√{n}  =  {se:.6f}')
                        case 3:
                            xbar = _ask('Sample mean x̄')
                            mu   = _ask('Population mean μ')
                            sig  = _ask('Population std dev σ')
                            n    = _ask_int('Sample size n')
                            z    = Prob.CLTZScore(xbar, mu, sig, n)
                            print(f'\n  z = (x̄−μ) / (σ/√n) = {z:.4f}')
                        case 4:
                            val = _ask('Sample mean value to find P(X̄ ≤ value)')
                            mu  = _ask('Population mean μ')
                            sig = _ask('Population std dev σ')
                            n   = _ask_int('Sample size n')
                            p   = Prob.CLTProbabilityBelow(val, mu, sig, n)
                            print(f'\n  P(X̄ ≤ {val})  =  {p:.6f}   ({p*100:.2f}%)')
                        case 5:
                            a   = _ask('Lower bound a')
                            b   = _ask('Upper bound b  (must be > a)', desc='a number larger than a')
                            mu  = _ask('Population mean μ')
                            sig = _ask('Population std dev σ')
                            n   = _ask_int('Sample size n')
                            p   = Prob.CLTProbabilityBetween(a, b, mu, sig, n)
                            print(f'\n  P({a} ≤ X̄ ≤ {b})  =  {p:.6f}   ({p*100:.2f}%)')
                        case _: print('  That was not a valid option.')
                elif sec == 9:
                    def _matrix():
                        n = _ask_int('Number of states', desc='a positive whole number')
                        _p(f'Enter the {n}×{n} transition matrix row by row  '
                           f'(each row sums to 1, {n} values per row).')
                        rows = []
                        for i in range(n):
                            row = _ask_list(f'  Row {i+1}', cast=float, min_count=n)
                            rows.append(row[:n])
                        return n, rows
                    match choice:
                        case 1:
                            _p('Enter the current state vector (probabilities for each state, must sum to 1):')
                            sv = _ask_list('  State vector', cast=float, min_count=2)
                            n, tm = _matrix()
                            nxt = Prob.MarkovNextState(sv[:n], tm)
                            print(f'\n  State after 1 step:')
                            for i, p in enumerate(nxt):
                                print(f'    State {i+1}:  {p:.6f}')
                        case 2:
                            _p('Enter the current state vector:')
                            sv = _ask_list('  State vector', cast=float, min_count=2)
                            n, tm = _matrix()
                            k   = _ask_int('Number of steps k', desc='a positive whole number')
                            res = Prob.MarkovAfterSteps(sv[:n], tm, k)
                            print(f'\n  State after {k} steps:')
                            for i, p in enumerate(res):
                                print(f'    State {i+1}:  {p:.6f}')
                        case 3:
                            _p('Enter the initial state vector:')
                            sv = _ask_list('  State vector', cast=float, min_count=2)
                            n, tm = _matrix()
                            stat = Prob.StationaryDistribution(sv[:n], tm)
                            print(f'\n  Stationary distribution:')
                            for i, p in enumerate(stat):
                                print(f'    State {i+1}:  {p:.6f}   ({p*100:.2f}%)')
                        case _: print('  That was not a valid option.')
                elif sec == 10:
                    match choice:
                        case 1:
                            n    = _ask_int('n  (number of trials)', desc='a positive whole number')
                            p    = _ask('p  (probability of success)', desc='a number between 0 and 1')
                            seed = _ask_int('Random seed  [Enter 42]') if input('  Custom seed? (y/n) [n]: ').strip().lower() == 'y' else 42
                            results = Prob.SimulateBernoulli(n, p, seed)
                            successes = sum(results)
                            print(f'\n  Trials: {n}   Successes: {successes}   Failures: {n-successes}')
                            print(f'  Simulated proportion: {successes/n:.4f}   Expected: {p:.4f}')
                        case 2:
                            n    = _ask_int('n  (number of trials)')
                            p    = _ask('p  (probability of success)', desc='a number between 0 and 1')
                            prop = Prob.SimulateBernoulliProportion(n, p)
                            print(f'\n  Simulated proportion  =  {prop:.6f}   (expected: {p:.4f})')
                        case 3:
                            n    = _ask_int('n  (number of trials)')
                            p    = _ask('p  (true probability)', desc='a number between 0 and 1')
                            ep   = Prob.EmpiricalProbability(n, p)
                            print(f'\n  Empirical probability  =  {ep:.6f}   (theoretical: {p:.4f})')
                        case 4:
                            vals  = _ask_list('  Outcome values', cast=float, min_count=2)
                            probs = _ask_list(f'  Probabilities ({len(vals)} values, must sum to 1)', cast=float, min_count=len(vals))
                            n     = _ask_int('Number of simulation trials', desc='a large positive whole number like 10000')
                            ev    = Prob.SimulatedExpectedValue(vals, probs[:len(vals)], n)
                            theo  = Prob.ExpectedValue(vals, probs[:len(vals)])
                            print(f'\n  Simulated E(X)  =  {ev:.6f}')
                            print(f'  Theoretical E(X)  =  {theo:.6f}')
                        case _: print('  That was not a valid option.')
                elif sec == 11:
                    def _probs():
                        _p('Enter probabilities (should sum to 1).')
                        return _ask_list('  Probabilities', cast=float, min_count=2)
                    match choice:
                        case 1:
                            ps = _probs()
                            h  = Prob.ShannonEntropy(ps)
                            print(f'\n  Shannon entropy  H  =  {h:.6f} bits')
                            print(f'  Maximum possible (uniform): {Prob.MaxEntropy(len(ps)):.6f} bits')
                        case 2:
                            ps = _probs()
                            print(f'\n  Natural entropy  H  =  {Prob.NaturalEntropy(ps):.6f} nats')
                        case 3:
                            n = _ask_int('n  (number of equally likely outcomes)', desc='a positive whole number')
                            print(f'\n  Max entropy for {n} outcomes  =  {Prob.MaxEntropy(n):.6f} bits  (= log₂ {n})')
                        case 4:
                            p = _ask('Probability of the event  (0 to 1)', desc='a number between 0 and 1')
                            print(f'\n  Self-information  I  =  −log₂(p)  =  {Prob.SelfInformation(p):.6f} bits')
                        case 5:
                            _p('KL divergence D_KL(P ∥ Q) measures how distribution P differs from Q.  '
                               'Enter both distributions as probability lists of the same length.')
                            ps = _ask_list('  Distribution P', cast=float, min_count=2)
                            qs = _ask_list(f'  Distribution Q  ({len(ps)} values)', cast=float, min_count=len(ps))
                            kl = Prob.KLDivergence(ps, qs[:len(ps)])
                            print(f'\n  D_KL(P ∥ Q)  =  {kl:.6f} nats')
                            _p('A value of 0 means the distributions are identical.  '
                               'Larger values indicate greater divergence.')
                        case _: print('  That was not a valid option.')
            except _AskAbort:
                print()
                _p('Calculation cancelled. Returning to the function list.')
            print()

# ============================================================
# COMBINATORICS DEBUG
# ============================================================

def CombinatoricsDebug():

    SECTIONS = [
        'Factorials & Falling/Rising Powers',
        'Permutations',
        'Combinations',
        'Pascal\'s Triangle & Identities',
        'Binomial & Multinomial Theorem',
        'Partition Numbers  (Stirling, Bell, Catalan)',
        'Integer Sequences  (Fibonacci, triangular, polygonal)',
        'Paths & Counting Problems',
        'Graph Theory Counting',
        'Generating Functions & Recurrences',
    ]

    while True:
        _SectionHeader('Combinatorics', 'Choose a section')
        for i, s in enumerate(SECTIONS, 1):
            print(f'  ({i:>2})  {s}')
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section number. Please try again.')
            continue

        while True:
            _SectionHeader('Combinatorics', SECTIONS[sec - 1])
            if sec == 1:
                print('  (1)  Factorial          n!')
                print('  (2)  Double factorial   n!!  (every other factor)')
                print('  (3)  Subfactorial       !n  (derangement count)')
                print('  (4)  Falling factorial  x⁽ⁿ⁾ = x·(x−1)···(x−n+1)')
                print('  (5)  Rising factorial   x⁽ⁿ⁾ = x·(x+1)···(x+n−1)  (Pochhammer symbol)')
                print('  (6)  Primorial          n#  (product of primes ≤ n)')
            elif sec == 2:
                print('  (1)  Permutations                   nPr = n!/(n−r)!')
                print('  (2)  Permutations with repetition   nʳ')
                print('  (3)  Multiset permutations          n!/(n₁!·n₂!···)')
                print('  (4)  Circular permutations          (n−1)!')
                print('  (5)  Necklace permutations          (n−1)!/2  (no flip distinction)')
                print('  (6)  Derangements                   !n  (no fixed points)')
                print('  (7)  Derangement probability        P(no fixed points)')
            elif sec == 3:
                print('  (1)  Combinations          nCr = n!/(r!·(n−r)!)')
                print('  (2)  Combinations with repetition  C(n+r−1, r)')
                print('  (3)  Combination symmetry  C(n,r) = C(n, n−r)  — verify')
            elif sec == 4:
                _p('Pascal\'s triangle identities and row structure.')
                print()
                print('  (1)  Pascal\'s identity     C(n,r) = C(n−1,r−1) + C(n−1,r)')
                print('  (2)  Sum of a row           Σ C(n,k) = 2ⁿ')
                print('  (3)  Vandermonde identity   Σ C(m,k)·C(n,r−k) = C(m+n,r)')
                print('  (4)  Pascal\'s row           list all C(n,k) for k=0…n')
                print('  (5)  Pascal\'s triangle      print first n rows')
                print('  (6)  Pascal\'s element       C(n,k) at a specific position')
                print('  (7)  Fibonacci from diagonal  sum of diagonal entries')
                print('  (8)  Hockey stick identity  Σ C(i,r) for i=r to n = C(n+1,r+1)')
            elif sec == 5:
                print('  (1)  Binomial expansion     (x+y)ⁿ — list all terms')
                print('  (2)  Specific binomial term  the k-th term of (x+y)ⁿ')
                print('  (3)  Binomial expansion value  numerical result of (x+y)ⁿ')
                print('  (4)  Multinomial coefficient  n!/(n₁!·n₂!···nₖ!)')
                print('  (5)  Specific multinomial term  with given powers and values')
            elif sec == 6:
                _p('Partition numbers count ways to divide n objects into groups.')
                print()
                print('  (1)  Stirling number (2nd kind)   S(n,k)  — partitions into k non-empty subsets')
                print('  (2)  Stirling number (1st kind)   s(n,k)  — signed, cycle counting')
                print('  (3)  Bell number                  B(n)    — total set partitions')
                print('  (4)  Catalan number               C(n)    — many structural counting problems')
            elif sec == 7:
                _p('Integer sequences that arise frequently in combinatorics.')
                print()
                print('  (1)  nth Fibonacci number')
                print('  (2)  Triangular number      n(n+1)/2')
                print('  (3)  Pentagonal number      n(3n−1)/2')
                print('  (4)  Hexagonal number       n(2n−1)')
                print('  (5)  Fibonacci sequence     first n terms')
                print('  (6)  Tribonacci sequence    first n terms')
            elif sec == 8:
                print('  (1)  Lattice paths          C(m+n, m)  — grid paths from (0,0) to (m,n)')
                print('  (2)  Dyck paths             Catalan(n)  — valid bracket sequences of length 2n')
                print('  (3)  Number of subsets      2ⁿ  — all subsets of an n-element set')
                print('  (4)  Non-empty subsets      2ⁿ − 1')
                print('  (5)  Inclusion-exclusion    |A ∪ B ∪ C|')
                print('  (6)  Surjective functions   onto functions from n to k  (Stirling-based)')
                print('  (7)  Total functions        kⁿ  — all functions from n to k')
                print('  (8)  Injective functions    one-to-one functions from n to k  (k ≥ n)')
            elif sec == 9:
                _p('Counting structures on complete graphs.')
                print()
                print('  (1)  Labelled graphs        2^C(n,2)  — all graphs on n labelled vertices')
                print('  (2)  Spanning trees         nⁿ⁻²  (Cayley\'s formula)')
                print('  (3)  Complete graph edges   n(n−1)/2')
                print('  (4)  Chromatic polynomial value   for complete graph Kₙ with q colours')
                print('  (5)  Simple paths in Kₙ    of length k')
            elif sec == 10:
                _p('Generating functions encode sequences.  '
                   'Convolution finds coefficients of a product of two generating functions.')
                print()
                print('  (1)  OGF coefficients       first n coefficients from a sequence formula')
                print('  (2)  Convolve two sequences  coefficient product')
                print('  (3)  Linear recurrence       compute the nth term from initial values')
            print()
            _ExitBar('Return to sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            print()
            try:
                if sec == 1:
                    match choice:
                        case 1:
                            n = _ask_int('n  (must be a non-negative whole number)', desc='a whole number ≥ 0')
                            print(f'\n  {n}!  =  {Comb.Factorial(n)}')
                        case 2:
                            n = _ask_int('n  (must be a non-negative whole number)', desc='a whole number ≥ 0')
                            print(f'\n  {n}!!  =  {Comb.DoubleFactorial(n)}')
                        case 3:
                            n = _ask_int('n  (must be a non-negative whole number)', desc='a whole number ≥ 0')
                            d = Comb.Subfactorial(n)
                            p = Comb.DerangementProbability(n) if n > 0 else 0
                            print(f'\n  !{n}  =  {d}  (number of derangements of {n} items)')
                            print(f'  Probability that a random permutation is a derangement:  {p:.6f}')
                        case 4:
                            x = _ask('x  (starting value)')
                            n = _ask_int('n  (number of factors)', desc='a non-negative whole number')
                            print(f'\n  Falling factorial  ({x})⁽{n}⁾  =  {Comb.FallingFactorial(x,n):.4f}')
                        case 5:
                            x = _ask('x  (starting value)')
                            n = _ask_int('n  (number of factors)', desc='a non-negative whole number')
                            print(f'\n  Rising factorial  ({x})⁽{n}⁾  =  {Comb.RisingFactorial(x,n):.4f}')
                        case 6:
                            n = _ask_int('n  (finds product of all primes ≤ n)', desc='a positive whole number')
                            print(f'\n  {n}#  =  {Comb.Primorial(n)}')
                        case _: print('  That was not a valid option.')
                elif sec == 2:
                    match choice:
                        case 1:
                            n = _ask_int('n  (total items)')
                            r = _ask_int('r  (items to arrange, 0 ≤ r ≤ n)', desc='a whole number from 0 to n')
                            print(f'\n  P({n},{r})  =  n!/(n−r)!  =  {Comb.Permutations(n,r)}')
                        case 2:
                            n = _ask_int('n  (types of items, with replacement)')
                            r = _ask_int('r  (length of arrangement)')
                            print(f'\n  {n}^{r}  =  {Comb.PermutationsWithRepetition(n,r)}')
                        case 3:
                            n      = _ask_int('n  (total items to arrange)')
                            k      = _ask_int('Number of groups k')
                            groups = _ask_list(f'  Group sizes (must sum to {n}, {k} values)', cast=int, min_count=k)
                            print(f'\n  n!/( {" · ".join(str(g)+"!" for g in groups[:k])} )  =  {Comb.MultisetPermutations(n, groups[:k])}')
                        case 4:
                            n = _ask_int('n  (people/objects in a circle)')
                            print(f'\n  Circular perms  =  ({n}−1)!  =  {Comb.CircularPermutations(n)}')
                        case 5:
                            n = _ask_int('n  (beads on a necklace)')
                            print(f'\n  Necklace perms  =  ({n}−1)!/2  =  {Comb.NecklacePermutations(n)}')
                        case 6:
                            n = _ask_int('n  (number of items, must be ≥ 0)', desc='a non-negative whole number')
                            print(f'\n  Derangements  !{n}  =  {Comb.Derangements(n)}')
                        case 7:
                            n = _ask_int('n  (number of items, must be ≥ 1)', desc='a positive whole number')
                            p = Comb.DerangementProbability(n)
                            print(f'\n  P(no fixed points)  ≈  {p:.6f}   ({p*100:.2f}%)')
                            _p('As n increases this approaches 1/e ≈ 36.79%.')
                        case _: print('  That was not a valid option.')
                elif sec == 3:
                    match choice:
                        case 1:
                            n = _ask_int('n  (total items)')
                            r = _ask_int('r  (items chosen, order does not matter)')
                            print(f'\n  C({n},{r})  =  {Comb.Combinations(n,r)}')
                        case 2:
                            n = _ask_int('n  (types of items)')
                            r = _ask_int('r  (items to choose, repetition allowed)')
                            print(f'\n  C({n}+{r}−1,{r})  =  {Comb.CombinationsWithRepetition(n,r)}')
                        case 3:
                            n = _ask_int('n')
                            r = _ask_int('r')
                            a = Comb.Combinations(n, r)
                            b = Comb.Combinations(n, n - r)
                            print(f'\n  C({n},{r})  =  {a}')
                            print(f'  C({n},{n-r})  =  {b}')
                            print(f'  {"Equal — symmetry confirmed ✓" if a == b else "Not equal — check your values"}')
                        case _: print('  That was not a valid option.')
                elif sec == 4:
                    match choice:
                        case 1:
                            n = _ask_int('n')
                            r = _ask_int('r  (must be ≥ 1 and ≤ n)', desc='a whole number from 1 to n')
                            a = Comb.PascalsIdentity(n, r)
                            print(f'\n  C({n},{r})  =  C({n-1},{r-1}) + C({n-1},{r})  =  {Comb.Combinations(n-1,r-1)} + {Comb.Combinations(n-1,r)}  =  {a}')
                        case 2:
                            n = _ask_int('n  (row index, 0-based)')
                            s = Comb.SumOfCombinations(n)
                            print(f'\n  Σ C({n},k) for k=0…{n}  =  2^{n}  =  {s}')
                        case 3:
                            m = _ask_int('m')
                            n = _ask_int('n')
                            r = _ask_int('r')
                            v = Comb.VandermondeIdentity(m, n, r)
                            print(f'\n  Σ C({m},k)·C({n},{r}−k) for k=0…{r}  =  C({m}+{n},{r})  =  {v}')
                        case 4:
                            n = _ask_int('n  (row number, 0-based)')
                            row = Comb.PascalRow(n)
                            print(f'\n  Row {n}:  {row}')
                            print(f'  Sum = {sum(row)}  =  2^{n}')
                        case 5:
                            n = _ask_int('n  (number of rows to print)', desc='a positive whole number ≤ 15 recommended')
                            tri = Comb.PascalTriangle(n)
                            print(f'\n  Pascal\'s Triangle (first {n} rows):')
                            for i, row in enumerate(tri):
                                print(f'  {" " * (n-i)}{" ".join(str(v) for v in row)}')
                        case 6:
                            n = _ask_int('n  (row, 0-based)')
                            k = _ask_int('k  (column, 0-based, must be ≤ n)', desc='a whole number from 0 to n')
                            print(f'\n  C({n},{k})  =  {Comb.PascalElement(n,k)}')
                        case 7:
                            n = _ask_int('n  (which Fibonacci via diagonal)', desc='a positive whole number')
                            fib = Comb.PascalDiagonalFibonacci(n)
                            print(f'\n  Fibonacci from diagonal {n}:  {fib}')
                        case 8:
                            n = _ask_int('n  (upper limit)')
                            r = _ask_int('r  (starting row, r ≤ n)', desc='a whole number ≤ n')
                            hs = Comb.HockeyStickIdentity(n, r)
                            print(f'\n  Σ C(i,{r}) for i={r}…{n}  =  C({n+1},{r+1})  =  {hs}')
                        case _: print('  That was not a valid option.')
                elif sec == 5:
                    match choice:
                        case 1:
                            n = _ask_int('n  (exponent in (x+y)ⁿ)')
                            x = _ask('x value  (Enter 1 for symbolic-style output)')
                            y = _ask('y value  (Enter 1 for symbolic-style output)')
                            terms = Comb.BinomialExpansion(n, x, y)
                            print(f'\n  ({x}+{y})^{n} — terms:')
                            for k, t in enumerate(terms):
                                print(f'    k={k}:  C({n},{k})·x^{n-k}·y^{k}  =  {t}')
                        case 2:
                            n = _ask_int('n  (exponent)')
                            k = _ask_int('k  (term index, 0-based, 0 ≤ k ≤ n)')
                            x = _ask('x value')
                            y = _ask('y value')
                            t = Comb.BinomialTerm(n, k, x, y)
                            print(f'\n  Term k={k} of ({x}+{y})^{n}  =  C({n},{k})·{x}^{n-k}·{y}^{k}  =  {t}')
                        case 3:
                            n = _ask_int('n  (exponent)')
                            x = _ask('x value')
                            y = _ask('y value')
                            v = Comb.BinomialExpansionValue(n, x, y)
                            print(f'\n  ({x}+{y})^{n}  =  {v}')
                        case 4:
                            n      = _ask_int('n  (total items)')
                            k      = _ask_int('Number of groups k')
                            groups = _ask_list(f'  Group sizes ({k} values, must sum to {n})', cast=int, min_count=k)
                            mc     = Comb.MultinomialCoefficient(n, groups[:k])
                            print(f'\n  n!/({" · ".join(str(g)+"!" for g in groups[:k])})  =  {mc}')
                        case 5:
                            n      = _ask_int('n  (total degree)')
                            k      = _ask_int('Number of variables k')
                            powers = _ask_list(f'  Powers for each variable ({k} values, must sum to n)', cast=int, min_count=k)
                            values = _ask_list(f'  Values for each variable ({k} values)', cast=float, min_count=k)
                            t      = Comb.MultinomialTerm(n, powers[:k], values[:k])
                            print(f'\n  Multinomial term  =  {t}')
                        case _: print('  That was not a valid option.')
                elif sec == 6:
                    match choice:
                        case 1:
                            n = _ask_int('n  (objects to partition)', desc='a non-negative whole number')
                            k = _ask_int('k  (number of non-empty subsets)', desc='a whole number from 1 to n')
                            print(f'\n  S({n},{k})  =  {Comb.StirlingSecond(n,k)}')
                            _p(f'This is the number of ways to partition {n} labelled objects into {k} non-empty, unlabelled subsets.')
                        case 2:
                            n = _ask_int('n')
                            k = _ask_int('k')
                            print(f'\n  s({n},{k})  =  {Comb.StirlingFirst(n,k)}  (signed Stirling first kind)')
                        case 3:
                            n = _ask_int('n  (number of elements in the set)', desc='a non-negative whole number')
                            b = Comb.BellNumber(n)
                            print(f'\n  Bell number  B({n})  =  {b}')
                            _p(f'There are {b} ways to partition a set of {n} elements into non-empty subsets.')
                        case 4:
                            n = _ask_int('n', desc='a non-negative whole number')
                            c = Comb.CatalanNumber(n)
                            print(f'\n  Catalan number  C({n})  =  {c}')
                            _p(f'Counts many things: balanced bracket sequences of length {2*n}, '
                               f'binary trees with {n+1} leaves, polygon triangulations, and more.')
                        case _: print('  That was not a valid option.')
                elif sec == 7:
                    match choice:
                        case 1:
                            n = _ask_int('n  (which Fibonacci number, 0-indexed)', desc='a non-negative whole number')
                            print(f'\n  F({n})  =  {Comb.Fibonacci(n)}')
                        case 2:
                            n = _ask_int('n')
                            print(f'\n  Triangular number  T({n})  =  n(n+1)/2  =  {Comb.TriangularNumber(n)}')
                        case 3:
                            n = _ask_int('n')
                            print(f'\n  Pentagonal number  P({n})  =  n(3n−1)/2  =  {Comb.PentagonalNumber(n)}')
                        case 4:
                            n = _ask_int('n')
                            print(f'\n  Hexagonal number  H({n})  =  n(2n−1)  =  {Comb.HexagonalNumber(n)}')
                        case 5:
                            n = _ask_int('n  (number of terms to generate)', desc='a positive whole number')
                            seq = Comb.FibonacciSequence(n)
                            print(f'\n  First {n} Fibonacci numbers:')
                            print(f'  {seq}')
                        case 6:
                            n = _ask_int('n  (number of terms to generate)', desc='a positive whole number')
                            seq = Comb.TribonacciSequence(n)
                            print(f'\n  First {n} Tribonacci numbers:')
                            print(f'  {seq}')
                        case _: print('  That was not a valid option.')
                elif sec == 8:
                    match choice:
                        case 1:
                            m = _ask_int('m  (steps right)', desc='a non-negative whole number')
                            n = _ask_int('n  (steps up)', desc='a non-negative whole number')
                            print(f'\n  Lattice paths from (0,0) to ({m},{n})  =  C({m}+{n},{m})  =  {Comb.LatticePaths(m,n)}')
                        case 2:
                            n = _ask_int('n  (pairs of brackets)', desc='a non-negative whole number')
                            print(f'\n  Dyck paths  =  Catalan({n})  =  {Comb.DyckPaths(n)}')
                            _p(f'This is the number of valid sequences of {n} opening and {n} closing brackets.')
                        case 3:
                            n = _ask_int('n  (set size)', desc='a non-negative whole number')
                            print(f'\n  Subsets of an {n}-element set  =  2^{n}  =  {Comb.NumberOfSubsets(n)}')
                        case 4:
                            n = _ask_int('n  (set size)', desc='a positive whole number')
                            print(f'\n  Non-empty subsets  =  2^{n} − 1  =  {Comb.NumberOfNonEmptySubsets(n)}')
                        case 5:
                            _p('Enter the sizes of sets A, B, C (use 0 for any set you don\'t need).')
                            a = _ask_int('|A|  (size of set A)', desc='a non-negative whole number')
                            b = _ask_int('|B|  (size of set B)', desc='a non-negative whole number')
                            c = _ask_int('|C|  (size of set C, enter 0 if only 2 sets)', desc='0 or a positive whole number')
                            ab = _ask_int('|A ∩ B|', desc='a non-negative whole number')
                            ac = _ask_int('|A ∩ C|  (enter 0 if only 2 sets)', desc='0 or a positive whole number') if c else 0
                            bc = _ask_int('|B ∩ C|  (enter 0 if only 2 sets)', desc='0 or a positive whole number') if c else 0
                            abc = _ask_int('|A ∩ B ∩ C|  (enter 0 if only 2 sets)', desc='0 or a positive whole number') if c else 0
                            result = Comb.InclusionExclusion([a,b,c], ab+ac+bc, abc) if c else a+b-ab
                            print(f'\n  |A ∪ B {"∪ C" if c else ""}|  =  {result}')
                        case 6:
                            n = _ask_int('n  (domain size)')
                            k = _ask_int('k  (codomain size, must be ≤ n for surjections)', desc='a whole number ≤ n')
                            print(f'\n  Surjective functions from {n} to {k}  =  {Comb.SurjectiveFunctions(n,k)}')
                        case 7:
                            n = _ask_int('n  (domain size)')
                            k = _ask_int('k  (codomain size)')
                            print(f'\n  Total functions from {n} to {k}  =  {k}^{n}  =  {Comb.TotalFunctions(n,k)}')
                        case 8:
                            n = _ask_int('n  (domain size)')
                            k = _ask_int('k  (codomain size, must be ≥ n)', desc='a whole number ≥ n')
                            print(f'\n  Injective (one-to-one) functions from {n} to {k}  =  {Comb.InjectiveFunctions(n,k)}')
                        case _: print('  That was not a valid option.')
                elif sec == 9:
                    match choice:
                        case 1:
                            n = _ask_int('n  (number of labelled vertices)', desc='a positive whole number')
                            print(f'\n  Labelled graphs on {n} vertices  =  2^C({n},2)  =  {Comb.LabeledGraphs(n)}')
                        case 2:
                            n = _ask_int('n  (number of labelled vertices)', desc='a positive whole number')
                            print(f'\n  Spanning trees of K_{n}  =  {n}^({n}−2)  =  {Comb.SpanningTrees(n)}')
                        case 3:
                            n = _ask_int('n  (number of vertices)', desc='a positive whole number')
                            print(f'\n  Edges in K_{n}  =  n(n−1)/2  =  {Comb.CompleteGraphEdges(n)}')
                        case 4:
                            n = _ask_int('n  (number of vertices)')
                            q = _ask_int('q  (number of available colours)')
                            print(f'\n  Chromatic polynomial P(K_{n}, {q})  =  {Comb.CompleteGraphColorings(n,q)}')
                        case 5:
                            n = _ask_int('n  (vertices in K_n)')
                            k = _ask_int('k  (path length in edges)')
                            print(f'\n  Simple paths of length {k} in K_{n}  =  {Comb.SimplePathsInComplete(n,k)}')
                        case _: print('  That was not a valid option.')
                elif sec == 10:
                    match choice:
                        case 1:
                            n   = _ask_int('Number of coefficients to generate', desc='a positive whole number')
                            _p('Enter the general term formula using k.  Example:  1/(k+1)  or  math.factorial(k)')
                            expr = _ask_str('  a(k) = ')
                            fn   = lambda k: eval(expr, {'k': k, 'math': math})
                            coeffs = Comb.OGFCoefficients(fn, n)
                            print(f'\n  First {n} coefficients:')
                            print(f'  {[round(c, 6) if isinstance(c, float) else c for c in coeffs]}')
                        case 2:
                            _p('Enter two sequences as space-separated numbers.  '
                               'Their convolution gives the coefficients of the product of their generating functions.')
                            a = _ask_list('  Sequence A', cast=float, min_count=2)
                            b = _ask_list('  Sequence B', cast=float, min_count=2)
                            c = Comb.ConvolveSequences(a, b)
                            print(f'\n  Convolution A★B:')
                            print(f'  {[round(v, 6) if isinstance(v, float) else v for v in c]}')
                        case 3:
                            _p('A linear recurrence computes aₙ from previous terms.  '
                               'Example: Fibonacci has initial values [0,1] and coefficients [1,1]  '
                               '(meaning aₙ = 1·aₙ₋₁ + 1·aₙ₋₂).')
                            k      = _ask_int('Order k  (how many previous terms)', desc='a positive whole number')
                            inits  = _ask_list(f'  Initial values (first {k} terms)', cast=float, min_count=k)
                            coeffs = _ask_list(f'  Recurrence coefficients ({k} values)', cast=float, min_count=k)
                            n      = _ask_int('Compute term number n  (0-indexed)')
                            val    = Comb.LinearRecurrence(inits[:k], coeffs[:k], n)
                            print(f'\n  a({n})  =  {val}')
                        case _: print('  That was not a valid option.')
            except _AskAbort:
                print()
                _p('Calculation cancelled. Returning to the function list.')
            print()

# ============================================================
# DISCRETE MATHEMATICS DEBUG
# ============================================================

def DiscreteMathDebug():
    SECTIONS = [
        'Propositional Logic',
        'Predicate Logic',
        'Set Theory',
        'Relations',
        'Functions',
        'Number Theory',
        'Sequences & Recurrences',
        'Graph Theory',
        'Trees',
        'Boolean Algebra',
    ]
    while True:
        _SectionHeader('Discrete Mathematics', 'Choose a section')
        for i, s in enumerate(SECTIONS, 1):
            print(f'  ({i:>2})  {s}')
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section.')
            continue
        while True:
            _SectionHeader('Discrete Mathematics', SECTIONS[sec - 1])
            if sec == 1:
                _p('Two-valued truth functions.  Enter 1 = True, 0 = False.')
                print()
                print('  (1)   AND           p ∧ q')
                print('  (2)   OR            p ∨ q')
                print('  (3)   NOT           ¬p')
                print('  (4)   IMPLIES       p → q')
                print('  (5)   BICONDITIONAL p ↔ q')
                print('  (6)   NAND          ¬(p ∧ q)')
                print('  (7)   NOR           ¬(p ∨ q)')
                print('  (8)   XOR           p ⊕ q')
                print('  (9)   XNOR          ¬(p ⊕ q)')
                print('  (10)  De Morgan — NOR   ¬(p∨q) = ¬p∧¬q')
                print('  (11)  De Morgan — NAND  ¬(p∧q) = ¬p∨¬q')
                print('  (12)  Truth table  (up to 4 variables, built-in formulas)')
                print('  (13)  Is tautology / contradiction / satisfiable?')
                print('  (14)  Logical equivalence check')
            elif sec == 2:
                _p('Predicates over a finite domain.  Enter domain as space-separated values.')
                print()
                print('  (1)   Universal quantifier    ∀x P(x)')
                print('  (2)   Existential quantifier  ∃x P(x)')
                print('  (3)   Unique existential      ∃!x P(x)')
                print('  (4)   Predicate extension     {x | P(x)}')
                print('  (5)   Counterexample for ∀x P(x)')
            elif sec == 3:
                _p('Enter sets as space-separated values, e.g.  1 2 3 4')
                print()
                print('  (1)   Union             A ∪ B')
                print('  (2)   Intersection      A ∩ B')
                print('  (3)   Difference        A \\ B')
                print('  (4)   Symmetric diff    A △ B')
                print('  (5)   Complement        Aᶜ  (needs universal set U)')
                print('  (6)   Subset check      A ⊆ B')
                print('  (7)   Proper subset     A ⊂ B')
                print('  (8)   Power set         𝒫(A)  (max |A|=10)')
                print('  (9)   Cartesian product A × B')
                print('  (10)  Cardinality       |A|')
                print('  (11)  Disjoint check    A ∩ B = ∅')
            elif sec == 4:
                _p('Enter a relation as space-separated pairs  a,b  e.g.  1,1 1,2 2,1')
                _p('Enter the domain as space-separated values.')
                print()
                print('  (1)   Is reflexive')
                print('  (2)   Is irreflexive')
                print('  (3)   Is symmetric')
                print('  (4)   Is antisymmetric')
                print('  (5)   Is asymmetric')
                print('  (6)   Is transitive')
                print('  (7)   Is equivalence relation  (ref + sym + trans)')
                print('  (8)   Is partial order          (ref + anti + trans)')
                print('  (9)   Is total order            (partial order + totality)')
                print('  (10)  Equivalence classes')
                print('  (11)  Transitive closure  (Warshall)')
                print('  (12)  Reflexive closure')
                print('  (13)  Symmetric closure')
                print('  (14)  Relation composition  R ∘ S')
            elif sec == 5:
                _p('Enter function as  input:output  pairs, e.g.  1:a 2:b 3:c')
                _p('Enter domain and codomain as space-separated values.')
                print()
                print('  (1)   Is injective    (one-to-one)')
                print('  (2)   Is surjective   (onto)')
                print('  (3)   Is bijective    (one-to-one correspondence)')
                print('  (4)   Function image  (set of outputs)')
                print('  (5)   Preimage of a value')
                print('  (6)   Inverse function  (if bijective)')
                print('  (7)   Composition  f ∘ g')
                print('  (8)   Count: total functions    mⁿ')
                print('  (9)   Count: injections         P(m,n)')
                print('  (10)  Count: bijections         n!')
            elif sec == 6:
                print('  (1)   Is divisible            a | b')
                print('  (2)   GCD                     Euclidean algorithm')
                print('  (3)   LCM')
                print('  (4)   Extended GCD            Bézout coefficients  ax + by = gcd')
                print('  (5)   Is prime')
                print('  (6)   Prime factorization')
                print('  (7)   Primes up to n          Sieve of Eratosthenes')
                print('  (8)   Euler\'s totient         φ(n)')
                print('  (9)   Divisor count           d(n)')
                print('  (10)  Divisor sum             σ(n)')
                print('  (11)  Is perfect number')
                print('  (12)  Modular arithmetic      a + b, a − b, a · b  (mod m)')
                print('  (13)  Modular power           aⁿ mod m')
                print('  (14)  Modular inverse         x s.t. ax ≡ 1 (mod m)')
                print('  (15)  Is congruent            a ≡ b (mod m)')
                print('  (16)  Linear congruence       solve ax ≡ b (mod m)')
                print('  (17)  Chinese Remainder Theorem')
                print('  (18)  Fermat\'s Little Theorem  aᵖ⁻¹ ≡ 1 (mod p)')
                print('  (19)  Wilson\'s Theorem        (p−1)! ≡ −1 (mod p)')
            elif sec == 7:
                print('  (1)   Arithmetic: nth term    a + (n−1)d')
                print('  (2)   Arithmetic: sum         n/2 · (2a + (n−1)d)')
                print('  (3)   Geometric: nth term     a · rⁿ⁻¹')
                print('  (4)   Geometric: sum          a(rⁿ−1)/(r−1)')
                print('  (5)   Infinite geometric sum  a/(1−r)  for |r| < 1')
                print('  (6)   Linear recurrence       nth term  aₙ = c₁aₙ₋₁ + c₂aₙ₋₂ + …')
                print('  (7)   Detect arithmetic sequence')
                print('  (8)   Detect geometric sequence')
            elif sec == 8:
                _p('Graphs as adjacency dicts.  Enter edges as  u,v  pairs, one per line, blank to finish.')
                print()
                print('  (1)   Vertex degree')
                print('  (2)   Degree sequence')
                print('  (3)   Edge count')
                print('  (4)   Is Eulerian       (Euler circuit — all even degrees)')
                print('  (5)   Is semi-Eulerian  (Euler path — exactly 2 odd degrees)')
                print('  (6)   Is connected')
                print('  (7)   Is complete')
                print('  (8)   Is bipartite')
                print('  (9)   BFS traversal')
                print('  (10)  DFS traversal')
                print('  (11)  Shortest path      Dijkstra (weighted)')
                print('  (12)  Minimum spanning tree  Kruskal (weighted)')
                print('  (13)  Greedy colouring   vertex → colour assignment')
                print('  (14)  Chromatic number bound')
            elif sec == 9:
                _p('Trees use adjacency dicts.  Rooted trees also need a root and children dict.')
                print()
                print('  (1)   Is tree         (connected + n−1 edges)')
                print('  (2)   Tree height     (longest root-to-leaf path)')
                print('  (3)   Leaf nodes')
                print('  (4)   Preorder traversal')
                print('  (5)   Postorder traversal')
                print('  (6)   Inorder traversal  (binary trees)')
                print('  (7)   Number of labeled trees  Cayley: nⁿ⁻²')
                print('  (8)   Prüfer sequence  (from edge list)')
                print('  (9)   Prüfer to tree   (reconstruct edges)')
            elif sec == 10:
                _p('Boolean values: 1 = True, 0 = False.')
                print()
                print('  (1)   AND   a ∧ b')
                print('  (2)   OR    a ∨ b')
                print('  (3)   NOT   ¬a')
                print('  (4)   NAND  ¬(a ∧ b)')
                print('  (5)   NOR   ¬(a ∨ b)')
                print('  (6)   XOR   a ⊕ b')
                print('  (7)   XNOR  a ↔ b')
                print('  (8)   IMPLIES  a → b')
                print('  (9)   DNF  (from minterm list)')
                print('  (10)  CNF  (from maxterm list)')
                print('  (11)  Quine-McCluskey  (basic prime implicants)')
            print()
            _ExitBar('Return to sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            print()
            try:
                # ── Helpers ──────────────────────────────────────────────────
                def _ask_set(prompt='  Set (space-separated values): '):
                    raw = input(prompt).strip().split()
                    try:
                        return [int(x) for x in raw]
                    except ValueError:
                        return raw

                def _ask_relation(prompt='  Pairs a,b separated by spaces: '):
                    raw = input(prompt).strip().split()
                    pairs = set()
                    for item in raw:
                        a, b = item.split(',')
                        try:
                            pairs.add((int(a), int(b)))
                        except ValueError:
                            pairs.add((a.strip(), b.strip()))
                    return pairs

                def _ask_graph(weighted=False):
                    print('  Enter edges as  u,v  (or  u,v,weight  for weighted). Blank line to finish.')
                    adj = {}
                    while True:
                        line = input('  Edge: ').strip()
                        if not line:
                            break
                        parts = line.replace(',', ' ').split()
                        u, v = parts[0], parts[1]
                        try: u = int(u)
                        except: pass
                        try: v = int(v)
                        except: pass
                        if weighted and len(parts) >= 3:
                            w = float(parts[2])
                            adj.setdefault(u, []).append((v, w))
                            adj.setdefault(v, []).append((u, w))
                        else:
                            adj.setdefault(u, []).append(v)
                            adj.setdefault(v, []).append(u)
                    return adj

                def _ask_children():
                    print('  Enter children as  parent:child1,child2  per line. Blank to finish.')
                    children = {}
                    nodes    = set()
                    while True:
                        line = input('  Node: ').strip()
                        if not line:
                            break
                        parent, kids = line.split(':')
                        parent = parent.strip()
                        try: parent = int(parent)
                        except: pass
                        kid_list = []
                        for k in kids.split(','):
                            k = k.strip()
                            try: k = int(k)
                            except: pass
                            kid_list.append(k)
                            nodes.add(k)
                        nodes.add(parent)
                        children[parent] = kid_list
                    for n in nodes:
                        if n not in children:
                            children[n] = []
                    return children, nodes

                # ── Section 1: Propositional Logic ───────────────────────────
                if sec == 1:
                    if choice in (1, 2, 4, 5, 6, 7, 8, 9, 10, 11):
                        p = bool(int(input('  p (1=True, 0=False): ')))
                        q = bool(int(input('  q (1=True, 0=False): ')))
                    elif choice == 3:
                        p = bool(int(input('  p (1=True, 0=False): ')))
                    match choice:
                        case 1:  print(f'\n  p ∧ q  =  {int(Discrete.LogicalAnd(p,q))}')
                        case 2:  print(f'\n  p ∨ q  =  {int(Discrete.LogicalOr(p,q))}')
                        case 3:  print(f'\n  ¬p  =  {int(Discrete.LogicalNot(p))}')
                        case 4:  print(f'\n  p → q  =  {int(Discrete.LogicalImplies(p,q))}')
                        case 5:  print(f'\n  p ↔ q  =  {int(Discrete.LogicalBiconditional(p,q))}')
                        case 6:  print(f'\n  p ↑ q  (NAND)  =  {int(Discrete.LogicalNand(p,q))}')
                        case 7:  print(f'\n  p ↓ q  (NOR)   =  {int(Discrete.LogicalNor(p,q))}')
                        case 8:  print(f'\n  p ⊕ q  (XOR)   =  {int(Discrete.LogicalXor(p,q))}')
                        case 9:  print(f'\n  XNOR(p,q)       =  {int(Discrete.LogicalXnor(p,q))}')
                        case 10:
                            nor, dm, match_ = Discrete.DeMorgansNor(p, q)
                            print(f'\n  ¬(p∨q)   =  {int(nor)}')
                            print(f'  ¬p ∧ ¬q  =  {int(dm)}')
                            print(f'  Match    :  {"Yes ✓" if match_ else "No ✗"}')
                        case 11:
                            nand, dm, match_ = Discrete.DeMorgansNand(p, q)
                            print(f'\n  ¬(p∧q)   =  {int(nand)}')
                            print(f'  ¬p ∨ ¬q  =  {int(dm)}')
                            print(f'  Match    :  {"Yes ✓" if match_ else "No ✗"}')
                        case 12:
                            print()
                            print('  Choose a formula:')
                            print('  (A) p ∧ q       (B) p ∨ q       (C) p → q')
                            print('  (D) p ↔ q       (E) ¬p ∧ q      (F) (p∨q) ∧ ¬(p∧q)')
                            fkey = input('  Formula: ').strip().upper()
                            formulas = {
                                'A': (lambda p, q: Discrete.LogicalAnd(p, q),   2),
                                'B': (lambda p, q: Discrete.LogicalOr(p, q),    2),
                                'C': (lambda p, q: Discrete.LogicalImplies(p,q),2),
                                'D': (lambda p, q: Discrete.LogicalBiconditional(p,q), 2),
                                'E': (lambda p, q: (not p) and q, 2),
                                'F': (lambda p, q: Discrete.LogicalXor(p, q),   2),
                            }
                            if fkey not in formulas:
                                print('\n  Invalid choice.')
                            else:
                                fn, nv = formulas[fkey]
                                table  = Discrete.TruthTable(fn, nv)
                                vars_  = ['p', 'q'][:nv]
                                header = '  ' + '  '.join(f'{v}' for v in vars_) + '   Result'
                                print(f'\n{header}')
                                print('  ' + '─' * (len(header) - 2))
                                for assignment, result in table:
                                    row = '  ' + '  '.join(f'{int(v)}' for v in assignment) + f'     {int(result)}'
                                    print(row)
                        case 13:
                            print()
                            print('  Choose a formula (same list as above): ', end='')
                            fkey = input().strip().upper()
                            formulas = {
                                'A': (lambda p, q: Discrete.LogicalAnd(p, q), 2),
                                'B': (lambda p, q: Discrete.LogicalOr(p, q),  2),
                                'C': (lambda p, q: Discrete.LogicalImplies(p, q), 2),
                                'D': (lambda p, q: Discrete.LogicalBiconditional(p, q), 2),
                                'E': (lambda p, q: (not p) and q, 2),
                                'F': (lambda p, q: Discrete.LogicalXor(p, q), 2),
                            }
                            if fkey not in formulas:
                                print('\n  Invalid choice.')
                            else:
                                fn, nv = formulas[fkey]
                                print(f'\n  Tautology      :  {"Yes" if Discrete.IsTautology(fn, nv) else "No"}')
                                print(f'  Contradiction  :  {"Yes" if Discrete.IsContradiction(fn, nv) else "No"}')
                                print(f'  Satisfiable    :  {"Yes" if Discrete.IsSatisfiable(fn, nv) else "No"}')
                        case 14:
                            print('  Compare two formulas (A–F from list above).')
                            f1k = input('  Formula 1: ').strip().upper()
                            f2k = input('  Formula 2: ').strip().upper()
                            formulas = {
                                'A': lambda p, q: Discrete.LogicalAnd(p, q),
                                'B': lambda p, q: Discrete.LogicalOr(p, q),
                                'C': lambda p, q: Discrete.LogicalImplies(p, q),
                                'D': lambda p, q: Discrete.LogicalBiconditional(p, q),
                                'E': lambda p, q: (not p) and q,
                                'F': lambda p, q: Discrete.LogicalXor(p, q),
                            }
                            if f1k not in formulas or f2k not in formulas:
                                print('\n  Invalid choice.')
                            else:
                                eq = Discrete.AreLogicallyEquivalent(formulas[f1k], formulas[f2k], 2)
                                print(f'\n  Logically equivalent:  {"Yes ✓" if eq else "No ✗"}')
                        case _: print('  That was not a valid option.')

                # ── Section 2: Predicate Logic ────────────────────────────────
                elif sec == 2:
                    if choice != 8:
                        dom_raw = input('  Domain (space-separated): ').strip().split()
                        try:    domain = [int(x) for x in dom_raw]
                        except: domain = dom_raw
                        pred_expr = input('  Predicate expression (Python, use x): ').strip()
                        pred_fn = eval(f'lambda x: {pred_expr}')
                    match choice:
                        case 1:
                            result = Discrete.UniversalQuantifier(pred_fn, domain)
                            print(f'\n  ∀x P(x)  =  {"True" if result else "False"}')
                        case 2:
                            result = Discrete.ExistentialQuantifier(pred_fn, domain)
                            print(f'\n  ∃x P(x)  =  {"True" if result else "False"}')
                        case 3:
                            result = Discrete.UniqueExistential(pred_fn, domain)
                            print(f'\n  ∃!x P(x)  =  {"True" if result else "False"}')
                        case 4:
                            ext = Discrete.PredicateExtension(pred_fn, domain)
                            print(f'\n  {{x | P(x)}}  =  {{{", ".join(str(x) for x in ext)}}}')
                        case 5:
                            cex = Discrete.UniversalCounterexample(pred_fn, domain)
                            if cex is None:
                                print('\n  No counterexample — ∀x P(x) holds on this domain.')
                            else:
                                print(f'\n  Counterexample:  x = {cex}  (P({cex}) is False)')
                        case _: print('  That was not a valid option.')

                # ── Section 3: Set Theory ──────────────────────────────────────
                elif sec == 3:
                    if choice in (1,2,3,4,6,7,9,11):
                        A = _ask_set('  Set A: ')
                        B = _ask_set('  Set B: ')
                    elif choice in (5,):
                        A = _ask_set('  Set A: ')
                        U = _ask_set('  Universal set U: ')
                    elif choice in (8,10):
                        A = _ask_set('  Set A: ')
                    match choice:
                        case 1:  print(f'\n  A ∪ B  =  {sorted(Discrete.SetUnion(A,B))}')
                        case 2:  print(f'\n  A ∩ B  =  {sorted(Discrete.SetIntersection(A,B))}')
                        case 3:  print(f'\n  A \\ B  =  {sorted(Discrete.SetDifference(A,B))}')
                        case 4:  print(f'\n  A △ B  =  {sorted(Discrete.SymmetricDifference(A,B))}')
                        case 5:  print(f'\n  Aᶜ     =  {sorted(Discrete.SetComplement(A,U))}')
                        case 6:  print(f'\n  A ⊆ B  :  {"Yes" if Discrete.IsSubset(A,B) else "No"}')
                        case 7:  print(f'\n  A ⊂ B  :  {"Yes" if Discrete.IsProperSubset(A,B) else "No"}')
                        case 8:
                            ps = Discrete.PowerSet(A)
                            print(f'\n  |𝒫(A)|  =  {len(ps)}  (= 2^{len(set(A))})')
                            print(f'  𝒫(A)   =  {{')
                            for s in sorted(ps, key=lambda x: (len(x), sorted(x))):
                                print(f'             {{{", ".join(str(x) for x in sorted(s))}}}' if s else '             ∅')
                            print('           }')
                        case 9:
                            cp = Discrete.CartesianProduct(A, B)
                            print(f'\n  A × B  ({len(cp)} pairs):')
                            for pair in cp:
                                print(f'    {pair}')
                        case 10: print(f'\n  |A|  =  {Discrete.Cardinality(A)}')
                        case 11: print(f'\n  Disjoint:  {"Yes" if Discrete.AreDisjoint(A,B) else "No"}')
                        case _:  print('  That was not a valid option.')

                # ── Section 4: Relations ──────────────────────────────────────
                elif sec == 4:
                    dom = _ask_set('  Domain (space-separated): ')
                    if choice != 14:
                        rel = _ask_relation('  Relation pairs (a,b ...): ')
                    match choice:
                        case 1:  print(f'\n  Reflexive     :  {"Yes" if Discrete.IsReflexive(rel, dom) else "No"}')
                        case 2:  print(f'\n  Irreflexive   :  {"Yes" if Discrete.IsIrreflexive(rel, dom) else "No"}')
                        case 3:  print(f'\n  Symmetric     :  {"Yes" if Discrete.IsSymmetric(rel, dom) else "No"}')
                        case 4:  print(f'\n  Antisymmetric :  {"Yes" if Discrete.IsAntisymmetric(rel, dom) else "No"}')
                        case 5:  print(f'\n  Asymmetric    :  {"Yes" if Discrete.IsAsymmetric(rel, dom) else "No"}')
                        case 6:  print(f'\n  Transitive    :  {"Yes" if Discrete.IsTransitive(rel, dom) else "No"}')
                        case 7:
                            result, ref, sym, tran = Discrete.IsEquivalenceRelation(rel, dom)
                            print(f'\n  Reflexive: {"✓" if ref else "✗"}   Symmetric: {"✓" if sym else "✗"}   Transitive: {"✓" if tran else "✗"}')
                            print(f'  Equivalence relation: {"Yes ✓" if result else "No ✗"}')
                        case 8:
                            result, ref, anti, tran = Discrete.IsPartialOrder(rel, dom)
                            print(f'\n  Reflexive: {"✓" if ref else "✗"}   Antisymmetric: {"✓" if anti else "✗"}   Transitive: {"✓" if tran else "✗"}')
                            print(f'  Partial order: {"Yes ✓" if result else "No ✗"}')
                        case 9:
                            result, ref, anti, tran, total = Discrete.IsTotalOrder(rel, dom)
                            print(f'\n  Reflexive: {"✓" if ref else "✗"}   Antisymmetric: {"✓" if anti else "✗"}   Transitive: {"✓" if tran else "✗"}   Total: {"✓" if total else "✗"}')
                            print(f'  Total order: {"Yes ✓" if result else "No ✗"}')
                        case 10:
                            classes = Discrete.EquivalenceClasses(rel, dom)
                            print(f'\n  Equivalence classes ({len(classes)}):')
                            for i, cls in enumerate(sorted(classes, key=lambda c: sorted(c)[0]), 1):
                                print(f'    [{i}]  {{{", ".join(str(x) for x in sorted(cls))}}}')
                        case 11:
                            tc = Discrete.TransitiveClosure(rel, dom)
                            print(f'\n  Transitive closure  ({len(tc)} pairs):')
                            for pair in sorted(tc):
                                print(f'    {pair}')
                        case 12:
                            rc = Discrete.ReflexiveClosure(rel, dom)
                            print(f'\n  Reflexive closure  ({len(rc)} pairs):')
                            for pair in sorted(rc):
                                print(f'    {pair}')
                        case 13:
                            sc = Discrete.SymmetricClosure(rel)
                            print(f'\n  Symmetric closure  ({len(sc)} pairs):')
                            for pair in sorted(sc):
                                print(f'    {pair}')
                        case 14:
                            print('  Enter relation R (pairs a,b):')
                            R = _ask_relation()
                            print('  Enter relation S (pairs a,b):')
                            S = _ask_relation()
                            comp = Discrete.RelationComposition(R, S)
                            print(f'\n  R ∘ S  ({len(comp)} pairs):')
                            for pair in sorted(comp):
                                print(f'    {pair}')
                        case _: print('  That was not a valid option.')

                # ── Section 5: Functions ──────────────────────────────────────
                elif sec == 5:
                    if choice not in (8, 9, 10):
                        fn_raw = input('  Function as  input:output  pairs: ').strip().split()
                        fn_dict = {}
                        for pair in fn_raw:
                            k, v = pair.split(':')
                            try: k = int(k)
                            except: pass
                            try: v = int(v)
                            except: pass
                            fn_dict[k] = v
                        dom = _ask_set('  Domain: ')
                        cod = _ask_set('  Codomain: ')
                    match choice:
                        case 1:  print(f'\n  Injective  :  {"Yes" if Discrete.IsInjective(fn_dict, dom, cod) else "No"}')
                        case 2:  print(f'\n  Surjective :  {"Yes" if Discrete.IsSurjective(fn_dict, dom, cod) else "No"}')
                        case 3:  print(f'\n  Bijective  :  {"Yes" if Discrete.IsBijective(fn_dict, dom, cod) else "No"}')
                        case 4:
                            img = Discrete.FunctionImage(fn_dict, dom)
                            print(f'\n  Image  =  {{{", ".join(str(x) for x in sorted(img))}}}')
                        case 5:
                            y_raw = input('  Value y: ').strip()
                            try: y_val = int(y_raw)
                            except: y_val = y_raw
                            pre = Discrete.FunctionPreimage(fn_dict, y_val, dom)
                            print(f'\n  f⁻¹({y_val})  =  {{{", ".join(str(x) for x in sorted(pre))}}}')
                        case 6:
                            inv = Discrete.FunctionInverse(fn_dict, dom, cod)
                            if inv is None:
                                print('\n  No inverse — function is not bijective.')
                            else:
                                print(f'\n  f⁻¹  =  {inv}')
                        case 7:
                            print('  Enter f as  input:output  pairs: ', end='')
                            f_raw = input().strip().split()
                            f_dict = {}
                            for pair in f_raw:
                                k, v = pair.split(':')
                                try: k = int(k)
                                except: pass
                                try: v = int(v)
                                except: pass
                                f_dict[k] = v
                            comp = Discrete.FunctionComposition(f_dict, fn_dict, dom)
                            print(f'\n  (f ∘ g)  =  {comp}')
                        case 8:
                            n = _ask_int('n  (size of domain)')
                            m = _ask_int('m  (size of codomain)')
                            print(f'\n  Total functions  (mⁿ)  =  {Discrete.NumberOfFunctions(n,m)}')
                        case 9:
                            n = _ask_int('n  (domain size)')
                            m = _ask_int('m  (codomain size, m ≥ n for injections)')
                            print(f'\n  Injections  P({m},{n})  =  {Discrete.NumberOfInjections(n,m)}')
                        case 10:
                            n = _ask_int('n  (set size — bijections = n!)')
                            print(f'\n  Bijections  =  {n}!  =  {Discrete.NumberOfBijections(n)}')
                        case _: print('  That was not a valid option.')

                # ── Section 6: Number Theory ──────────────────────────────────
                elif sec == 6:
                    match choice:
                        case 1:
                            b = _ask_int('b  (dividend)')
                            a = _ask_int('a  (divisor)')
                            print(f'\n  {a} | {b}  :  {"Yes" if Discrete.IsDivisible(b,a) else "No"}')
                        case 2:
                            a = _ask_int('a'); b = _ask_int('b')
                            print(f'\n  gcd({a},{b})  =  {Discrete.GCD(a,b)}')
                        case 3:
                            a = _ask_int('a'); b = _ask_int('b')
                            print(f'\n  lcm({a},{b})  =  {Discrete.LCM(a,b)}')
                        case 4:
                            a = _ask_int('a'); b = _ask_int('b')
                            g, x, y = Discrete.ExtendedGCD(a, b)
                            print(f'\n  gcd({a},{b})  =  {g}')
                            print(f'  {a}·({x}) + {b}·({y})  =  {g}  ✓')
                        case 5:
                            n = _ask_int('n')
                            print(f'\n  {n} is {"prime" if Discrete.IsPrime(n) else "not prime"}')
                        case 6:
                            n = _ask_int('n')
                            factors = Discrete.PrimeFactorization(n)
                            parts   = ' · '.join(f'{p}^{e}' if e > 1 else str(p) for p, e in factors)
                            print(f'\n  {n}  =  {parts if parts else "1"}')
                        case 7:
                            n = _ask_int('n')
                            primes = Discrete.Primes(n)
                            print(f'\n  Primes ≤ {n}  ({len(primes)} total):')
                            print('  ' + ', '.join(str(p) for p in primes))
                        case 8:
                            n = _ask_int('n')
                            print(f'\n  φ({n})  =  {Discrete.EulersTotient(n)}')
                        case 9:
                            n = _ask_int('n')
                            print(f'\n  d({n})  =  {Discrete.DivisorCount(n)}')
                        case 10:
                            n = _ask_int('n')
                            print(f'\n  σ({n})  =  {Discrete.DivisorSum(n)}')
                        case 11:
                            n = _ask_int('n')
                            print(f'\n  {n} is {"a perfect number" if Discrete.IsPerfect(n) else "not a perfect number"}')
                        case 12:
                            a = _ask_int('a'); b = _ask_int('b'); m = _ask_int('m  (modulus)')
                            print(f'\n  ({a} + {b}) mod {m}  =  {Discrete.ModularAdd(a,b,m)}')
                            print(f'  ({a} − {b}) mod {m}  =  {Discrete.ModularSubtract(a,b,m)}')
                            print(f'  ({a} × {b}) mod {m}  =  {Discrete.ModularMultiply(a,b,m)}')
                        case 13:
                            base = _ask_int('base'); exp = _ask_int('exponent'); mod = _ask_int('modulus')
                            print(f'\n  {base}^{exp} mod {mod}  =  {Discrete.ModularPower(base,exp,mod)}')
                        case 14:
                            a = _ask_int('a'); m = _ask_int('m  (modulus)')
                            inv = Discrete.ModularInverse(a, m)
                            if inv is None:
                                print(f'\n  No inverse — gcd({a},{m}) ≠ 1')
                            else:
                                print(f'\n  {a}⁻¹ mod {m}  =  {inv}   ({a} × {inv} mod {m} = {(a*inv)%m})')
                        case 15:
                            a = _ask_int('a'); b = _ask_int('b'); m = _ask_int('m')
                            print(f'\n  {a} ≡ {b} (mod {m})  :  {"Yes" if Discrete.IsCongruent(a,b,m) else "No"}')
                        case 16:
                            a = _ask_int('a'); b = _ask_int('b'); m = _ask_int('m')
                            sols = Discrete.LinearCongruence(a, b, m)
                            if not sols:
                                print(f'\n  No solution — gcd({a},{m}) does not divide {b}')
                            else:
                                print(f'\n  Solutions to {a}x ≡ {b} (mod {m}):')
                                for x in sols:
                                    print(f'    x ≡ {x} (mod {m})')
                        case 17:
                            print('  Enter residues (space-separated): ', end='')
                            remainders = [int(x) for x in input().strip().split()]
                            print('  Enter moduli   (space-separated): ', end='')
                            moduli = [int(x) for x in input().strip().split()]
                            sol = Discrete.ChineseRemainderTheorem(remainders, moduli)
                            M = 1
                            for m in moduli: M *= m
                            if sol is None:
                                print('\n  No solution — moduli must be pairwise coprime.')
                            else:
                                print(f'\n  x  ≡  {sol}  (mod {M})')
                        case 18:
                            a = _ask_int('a'); p = _ask_int('p  (prime)')
                            lhs, rhs, holds = Discrete.FermatsLittleTheorem(a, p)
                            if lhs is None:
                                print('\n  p must be prime.')
                            else:
                                print(f'\n  {a}^({p}−1) mod {p}  =  {lhs}')
                                print(f'  Fermat\'s Little Theorem holds:  {"Yes ✓" if holds else "No ✗"}')
                        case 19:
                            p = _ask_int('p')
                            lhs, rhs, holds = Discrete.WilsonsTheorem(p)
                            if lhs is None:
                                print('\n  p must be ≥ 2.')
                            else:
                                print(f'\n  ({p}−1)! mod {p}  =  {lhs}')
                                print(f'  Wilson\'s Theorem holds:  {"Yes ✓" if holds else "No ✗"}')
                                print(f'  {p} is {"prime" if holds else "not prime"} (by Wilson\'s Theorem)')
                        case _: print('  That was not a valid option.')

                # ── Section 7: Sequences & Recurrences ───────────────────────
                elif sec == 7:
                    match choice:
                        case 1:
                            a = _ask('a  (first term)'); d = _ask('d  (common difference)'); n = _ask_int('n  (term, 1-indexed)')
                            print(f'\n  a_{n}  =  {Discrete.ArithmeticTerm(a,d,n):.6f}')
                        case 2:
                            a = _ask('a  (first term)'); d = _ask('d  (common difference)'); n = _ask_int('n  (number of terms)')
                            print(f'\n  S_{n}  =  {Discrete.ArithmeticSum(a,d,n):.6f}')
                        case 3:
                            a = _ask('a  (first term)'); r = _ask('r  (common ratio)'); n = _ask_int('n  (term, 1-indexed)')
                            print(f'\n  a_{n}  =  {Discrete.GeometricTerm(a,r,n):.6f}')
                        case 4:
                            a = _ask('a  (first term)'); r = _ask('r  (common ratio)'); n = _ask_int('n  (number of terms)')
                            print(f'\n  S_{n}  =  {Discrete.GeometricSum(a,r,n):.6f}')
                        case 5:
                            a = _ask('a  (first term)'); r = _ask('r  (ratio, |r| < 1)')
                            result = Discrete.InfiniteGeometricSum(a, r)
                            if result is None:
                                print('\n  Series diverges — |r| must be less than 1.')
                            else:
                                print(f'\n  S∞  =  {result:.6f}')
                        case 6:
                            print('  Initial values (space-separated, a₀ first): ', end='')
                            init = [float(x) for x in input().strip().split()]
                            print('  Coefficients  (c₁ c₂ ..., space-separated): ', end='')
                            coeffs = [float(x) for x in input().strip().split()]
                            n = _ask_int('n  (0-indexed term to compute)')
                            val = Discrete.LinearRecurrenceNthTerm(init, coeffs, n)
                            print(f'\n  a_{n}  =  {val:.6f}')
                        case 7:
                            print('  Sequence (space-separated): ', end='')
                            seq = [float(x) for x in input().strip().split()]
                            is_arith, d = Discrete.IsArithmetic(seq)
                            print(f'\n  Arithmetic:  {"Yes" if is_arith else "No"}' + (f'   d = {d}' if is_arith else ''))
                        case 8:
                            print('  Sequence (space-separated): ', end='')
                            seq = [float(x) for x in input().strip().split()]
                            is_geo, r = Discrete.IsGeometric(seq)
                            print(f'\n  Geometric:  {"Yes" if is_geo else "No"}' + (f'   r = {r:.4f}' if is_geo else ''))
                        case _: print('  That was not a valid option.')

                # ── Section 8: Graph Theory ───────────────────────────────────
                elif sec == 8:
                    if choice in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14):
                        adj = _ask_graph(weighted=False)
                    elif choice in (11, 12):
                        adj = _ask_graph(weighted=True)
                    match choice:
                        case 1:
                            v_raw = input('  Vertex: ').strip()
                            try: v = int(v_raw)
                            except: v = v_raw
                            print(f'\n  deg({v})  =  {Discrete.VertexDegree(adj, v)}')
                        case 2:
                            ds = Discrete.DegreeSequence(adj)
                            print(f'\n  Degree sequence:  {ds}')
                        case 3:
                            print(f'\n  Edges:  {Discrete.EdgeCount(adj)}')
                        case 4:
                            print(f'\n  Eulerian (Euler circuit):  {"Yes" if Discrete.IsEulerian(adj) else "No"}')
                        case 5:
                            print(f'\n  Semi-Eulerian (Euler path):  {"Yes" if Discrete.IsSemiEulerian(adj) else "No"}')
                        case 6:
                            print(f'\n  Connected:  {"Yes" if Discrete.IsConnected(adj) else "No"}')
                        case 7:
                            print(f'\n  Complete:  {"Yes" if Discrete.IsComplete(adj) else "No"}')
                        case 8:
                            bip, A, B = Discrete.IsBipartite(adj)
                            print(f'\n  Bipartite:  {"Yes" if bip else "No"}')
                            if bip:
                                print(f'  Part A:  {sorted(A)}')
                                print(f'  Part B:  {sorted(B)}')
                        case 9:
                            v_raw = input('  Start vertex: ').strip()
                            try: v = int(v_raw)
                            except: v = v_raw
                            print(f'\n  BFS order:  {Discrete.BFS(adj, v)}')
                        case 10:
                            v_raw = input('  Start vertex: ').strip()
                            try: v = int(v_raw)
                            except: v = v_raw
                            print(f'\n  DFS order:  {Discrete.DFS(adj, v)}')
                        case 11:
                            s_raw = input('  Start vertex: ').strip()
                            e_raw = input('  End vertex: ').strip()
                            try: s = int(s_raw)
                            except: s = s_raw
                            try: e = int(e_raw)
                            except: e = e_raw
                            dist, path = Discrete.ShortestPath(adj, s, e)
                            if not path:
                                print(f'\n  No path from {s} to {e}.')
                            else:
                                print(f'\n  Distance:  {dist}')
                                print(f'  Path:      {" → ".join(str(v) for v in path)}')
                        case 12:
                            edges    = [(w, u, v) for u, neighbors in adj.items() for v, w in neighbors if u < v]
                            vertices = set(adj.keys())
                            weight, mst = Discrete.MinimumSpanningTree(edges, vertices)
                            print(f'\n  MST total weight:  {weight}')
                            print(f'  MST edges:')
                            for u, v, w in mst:
                                print(f'    {u} — {v}  (weight {w})')
                        case 13:
                            coloring = Discrete.GreedyColoring(adj)
                            print('\n  Vertex colouring:')
                            for v, c in sorted(coloring.items()):
                                print(f'    vertex {v}  →  colour {c}')
                        case 14:
                            print(f'\n  Chromatic number bound:  {Discrete.ChromaticNumberBound(adj)}')
                        case _: print('  That was not a valid option.')

                # ── Section 9: Trees ──────────────────────────────────────────
                elif sec == 9:
                    if choice in (1,):
                        adj = _ask_graph(weighted=False)
                    elif choice in (2, 3, 4, 5, 6):
                        print('  Enter children as  parent:child1,child2  per line. Blank to finish.')
                        children, nodes = _ask_children()
                        root_raw = input('  Root node: ').strip()
                        try: root = int(root_raw)
                        except: root = root_raw
                    elif choice == 7:
                        pass  # just needs n
                    elif choice in (8,):
                        print('  Enter edges as  u,v  pairs (space-separated): ', end='')
                        raw = input().strip().split()
                        edges_tree = []
                        for pair in raw:
                            a, b = pair.split(',')
                            try: a = int(a)
                            except: pass
                            try: b = int(b)
                            except: pass
                            edges_tree.append((a, b))
                        n_tree = _ask_int('n  (number of vertices, labeled 1 to n)')
                    elif choice == 9:
                        print('  Enter Prüfer sequence (space-separated): ', end='')
                        prufer = [int(x) for x in input().strip().split()]
                    match choice:
                        case 1:
                            print(f'\n  Is tree:  {"Yes" if Discrete.IsTree(adj) else "No"}')
                        case 2:
                            h = Discrete.TreeHeight(children, root)
                            print(f'\n  Height:  {h}')
                        case 3:
                            leaves = Discrete.TreeLeaves(children, nodes)
                            print(f'\n  Leaves:  {sorted(leaves)}')
                        case 4:
                            order = Discrete.PreorderTraversal(children, root)
                            print(f'\n  Preorder:  {order}')
                        case 5:
                            order = Discrete.PostorderTraversal(children, root)
                            print(f'\n  Postorder:  {order}')
                        case 6:
                            order = Discrete.InorderTraversal(children, root)
                            print(f'\n  Inorder:  {order}')
                        case 7:
                            n = _ask_int('n  (number of labeled vertices)')
                            print(f'\n  Labeled trees on {n} vertices  (nⁿ⁻²):  {Discrete.NumberOfLabeledTrees(n)}')
                        case 8:
                            seq = Discrete.PruferSequence(edges_tree, n_tree)
                            print(f'\n  Prüfer sequence:  {seq}')
                        case 9:
                            edges_out = Discrete.PruferToTree(prufer)
                            print(f'\n  Reconstructed edges:')
                            for u, v in edges_out:
                                print(f'    {u} — {v}')
                        case _: print('  That was not a valid option.')

                # ── Section 10: Boolean Algebra ───────────────────────────────
                elif sec == 10:
                    if choice in (1,2,4,5,6,7,8):
                        a = bool(int(input('  a (1=True, 0=False): ')))
                        b = bool(int(input('  b (1=True, 0=False): ')))
                    elif choice == 3:
                        a = bool(int(input('  a (1=True, 0=False): ')))
                    match choice:
                        case 1:  print(f'\n  a ∧ b  =  {Discrete.BoolAnd(a,b)}')
                        case 2:  print(f'\n  a ∨ b  =  {Discrete.BoolOr(a,b)}')
                        case 3:  print(f'\n  ¬a     =  {Discrete.BoolNot(a)}')
                        case 4:  print(f'\n  NAND   =  {Discrete.BoolNand(a,b)}')
                        case 5:  print(f'\n  NOR    =  {Discrete.BoolNor(a,b)}')
                        case 6:  print(f'\n  XOR    =  {Discrete.BoolXor(a,b)}')
                        case 7:  print(f'\n  XNOR   =  {Discrete.BoolXnor(a,b)}')
                        case 8:  print(f'\n  a → b  =  {Discrete.BoolImplies(a,b)}')
                        case 9:
                            n = _ask_int('n_vars  (number of variables)')
                            print('  Minterms (row numbers where output=1, space-sep): ', end='')
                            minterms = [int(x) for x in input().strip().split()]
                            table = [(a, i in minterms) for i, a in enumerate(
                                __import__('itertools').product([False,True], repeat=n))]
                            print(f'\n  DNF:  {Discrete.ToDNF(table)}')
                        case 10:
                            n = _ask_int('n_vars  (number of variables)')
                            print('  Maxterms (row numbers where output=0, space-sep): ', end='')
                            maxterms = [int(x) for x in input().strip().split()]
                            table = [(a, i not in maxterms) for i, a in enumerate(
                                __import__('itertools').product([False,True], repeat=n))]
                            print(f'\n  CNF:  {Discrete.ToCNF(table)}')
                        case 11:
                            n = _ask_int('n_vars')
                            print('  Minterms (space-sep): ', end='')
                            minterms = [int(x) for x in input().strip().split()]
                            pis = Discrete.QuineMcCluskey(minterms, n)
                            print(f'\n  Prime implicants ({len(pis)} found):')
                            for term, mask, covered in sorted(pis, key=lambda x: sorted(x[2])):
                                print(f'    term={bin(term)}  mask={bin(mask)}  covers={sorted(covered)}')
                        case _: print('  That was not a valid option.')

            except _AskAbort:
                print()
                _p('Calculation cancelled. Returning to the function list.')
            except Exception as e:
                print(f'\n  Error: {e}')
            print()

# ============================================================
# LINEAR ALGEBRA DEBUG
# ============================================================

def LinearAlgebraDebug():
    SECTIONS = [
        'Vectors', 'Matrix Operations', 'Matrix Properties',
        'Determinants', 'Matrix Inverse', 'Linear Systems',
        'Eigenvalues', 'Vector Spaces', 'Orthogonality', 'Decompositions',
    ]
    def _vec():
        return [float(x) for x in _ask('  Vector components (space-sep): ', cast=str).split()]
    def _mat():
        r = _ask('  Rows: ', cast=int)
        c = _ask('  Cols: ', cast=int)
        return [[float(x) for x in _ask(f'  Row {i+1} (space-sep): ', cast=str).split()] for i in range(r)]
    def _sq():
        n = _ask('  Size n (n×n): ', cast=int)
        return [[float(x) for x in _ask(f'  Row {i+1} (space-sep): ', cast=str).split()] for i in range(n)]
    while True:
        _SectionHeader('Linear Algebra', 'Choose a section')
        for i, s in enumerate(SECTIONS, 1):
            print(f'  ({i:>2})  {s}')
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section.')
            continue
        while True:
            _SectionHeader('Linear Algebra', SECTIONS[sec - 1])
            if sec == 1:
                print('  (1)  Add  (2)  Subtract  (3)  Scale  (4)  Dot product')
                print('  (5)  Cross product  (6)  Magnitude  (7)  Normalize')
                print('  (8)  Angle between vectors  (9)  Are orthogonal?')
            elif sec == 2:
                print('  (1)  Add  (2)  Subtract  (3)  Scalar multiply')
                print('  (4)  Matrix × matrix  (5)  Matrix × vector')
                print('  (6)  Transpose  (7)  Trace')
            elif sec == 3:
                print('  (1)  Is square?  (2)  Is symmetric?  (3)  Is diagonal?')
                print('  (4)  Is identity?  (5)  Is upper triangular?')
                print('  (6)  Is lower triangular?  (7)  Is orthogonal?  (8)  Rank')
            elif sec == 4:
                print('  (1)  Determinant  (2)  Cofactor matrix  (3)  Adjugate')
            elif sec == 5:
                print('  (1)  Inverse  (2)  Is invertible?  (3)  Pseudoinverse')
            elif sec == 6:
                print('  (1)  Solve Ax=b  (2)  RREF  (3)  Null space  (4)  Column space basis')
            elif sec == 7:
                print('  (1)  Eigenvalues (2×2)  (2)  Characteristic polynomial  (3)  Is diagonalizable?')
            elif sec == 8:
                print('  (1)  Is v in span?  (2)  Linearly independent?  (3)  Is basis?  (4)  Dimension')
            elif sec == 9:
                print('  (1)  Gram-Schmidt  (2)  Project v onto u  (3)  Project onto subspace  (4)  Orthogonal?')
            elif sec == 10:
                print('  (1)  LU decomposition  (2)  QR decomposition  (3)  Cholesky  (4)  Singular values')
            print()
            _ExitBar('Return to sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            if choice < 0:
                print('\n  That was not a valid option.')
                continue
            try:
                if sec == 1:
                    a = _vec()
                    match choice:
                        case 1:
                            b = _vec()
                            print(f'\n  Result: {LinAlg.VectorAdd(a, b)}')
                        case 2:
                            b = _vec()
                            print(f'\n  Result: {LinAlg.VectorSub(a, b)}')
                        case 3:
                            k = _ask('  Scalar: ', cast=float)
                            print(f'\n  Result: {LinAlg.VectorScale(k, a)}')
                        case 4:
                            b = _vec()
                            print(f'\n  Dot product: {LinAlg.DotProduct(a, b):.6f}')
                        case 5:
                            b = _vec()
                            print(f'\n  Cross product: {LinAlg.CrossProduct(a, b)}')
                        case 6:
                            print(f'\n  Magnitude: {LinAlg.VectorMagnitude(a):.6f}')
                        case 7:
                            print(f'\n  Unit vector: {LinAlg.VectorNormalize(a)}')
                        case 8:
                            b = _vec()
                            print(f'\n  Angle: {LinAlg.AngleBetweenVectors(a, b):.4f}°')
                        case 9:
                            b = _vec()
                            print(f'\n  Orthogonal: {LinAlg.AreOrthogonal(a, b)}')
                        case _:
                            print('\n  That was not a valid option.')
                            continue
                elif sec == 2:
                    match choice:
                        case 1:
                            A = _mat(); B = _mat()
                            r = LinAlg.MatrixAdd(A, B)
                            print('\n  Result:')
                            for row in r: print(f'    {row}')
                        case 2:
                            A = _mat(); B = _mat()
                            r = LinAlg.MatrixSub(A, B)
                            print('\n  Result:')
                            for row in r: print(f'    {row}')
                        case 3:
                            k = _ask('  Scalar: ', cast=float); A = _mat()
                            r = LinAlg.MatrixScale(k, A)
                            print('\n  Result:')
                            for row in r: print(f'    {row}')
                        case 4:
                            A = _mat(); B = _mat()
                            r = LinAlg.MatrixMul(A, B)
                            print('\n  Result:')
                            for row in r: print(f'    {row}')
                        case 5:
                            A = _mat(); v = _vec()
                            print(f'\n  Result: {LinAlg.MatrixVectorMul(A, v)}')
                        case 6:
                            A = _mat()
                            r = LinAlg.Transpose(A)
                            print('\n  Transpose:')
                            for row in r: print(f'    {row}')
                        case 7:
                            A = _sq()
                            print(f'\n  Trace: {LinAlg.Trace(A):.6f}')
                        case _:
                            print('\n  That was not a valid option.')
                            continue
                elif sec == 3:
                    A = _sq()
                    match choice:
                        case 1: print(f'\n  Is square: {LinAlg.IsSquare(A)}')
                        case 2: print(f'\n  Is symmetric: {LinAlg.IsSymmetric(A)}')
                        case 3: print(f'\n  Is diagonal: {LinAlg.IsDiagonal(A)}')
                        case 4: print(f'\n  Is identity: {LinAlg.IsIdentity(A)}')
                        case 5: print(f'\n  Is upper triangular: {LinAlg.IsUpperTriangular(A)}')
                        case 6: print(f'\n  Is lower triangular: {LinAlg.IsLowerTriangular(A)}')
                        case 7: print(f'\n  Is orthogonal: {LinAlg.IsOrthogonal(A)}')
                        case 8: print(f'\n  Rank: {LinAlg.Rank(A)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 4:
                    A = _sq()
                    match choice:
                        case 1:
                            print(f'\n  Determinant: {LinAlg.Determinant(A):.6f}')
                        case 2:
                            r = LinAlg.CofactorMatrix(A)
                            print('\n  Cofactor matrix:')
                            for row in r: print(f'    {row}')
                        case 3:
                            r = LinAlg.Adjugate(A)
                            print('\n  Adjugate:')
                            for row in r: print(f'    {row}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 5:
                    A = _sq()
                    match choice:
                        case 1:
                            r = LinAlg.MatrixInverse(A)
                            if r is None:
                                print('\n  Matrix is not invertible.')
                            else:
                                print('\n  Inverse:')
                                for row in r: print(f'    {[round(x,6) for x in row]}')
                        case 2:
                            print(f'\n  Is invertible: {LinAlg.IsInvertible(A)}')
                        case 3:
                            r = LinAlg.Pseudoinverse(A)
                            print('\n  Pseudoinverse:')
                            for row in r: print(f'    {[round(x,6) for x in row]}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 6:
                    match choice:
                        case 1:
                            A = _mat(); b = _vec()
                            r = LinAlg.GaussianElimination(A, b)
                            print(f'\n  Solution x: {r}')
                        case 2:
                            A = _mat()
                            r = LinAlg.RREF(A)
                            print('\n  RREF:')
                            for row in r: print(f'    {row}')
                        case 3:
                            A = _mat()
                            r = LinAlg.NullSpace(A)
                            print('\n  Null space basis:')
                            for v in r: print(f'    {v}')
                        case 4:
                            A = _mat()
                            r = LinAlg.ColumnSpaceBasis(A)
                            print('\n  Column space basis:')
                            for v in r: print(f'    {v}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 7:
                    A = _sq()
                    match choice:
                        case 1:
                            print(f'\n  Eigenvalues: {LinAlg.Eigenvalues2x2(A)}')
                        case 2:
                            print(f'\n  Char. polynomial: {LinAlg.CharacteristicPolynomial(A)}')
                        case 3:
                            print(f'\n  Is diagonalizable: {LinAlg.IsDiagonalizable(A)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 8:
                    match choice:
                        case 1:
                            v = _vec()
                            print('  Span vectors (blank line to finish):')
                            S = []
                            while True:
                                raw = input('  > ').strip()
                                if not raw: break
                                S.append([float(x) for x in raw.split()])
                            print(f'\n  In span: {LinAlg.IsInSpan(v, S)}')
                        case 2:
                            print('  Vectors (blank line to finish):')
                            S = []
                            while True:
                                raw = input('  > ').strip()
                                if not raw: break
                                S.append([float(x) for x in raw.split()])
                            print(f'\n  Linearly independent: {LinAlg.AreLinearlyIndependent(S)}')
                        case 3:
                            n = _ask('  Space dimension: ', cast=int)
                            print('  Basis vectors (blank line to finish):')
                            S = []
                            while True:
                                raw = input('  > ').strip()
                                if not raw: break
                                S.append([float(x) for x in raw.split()])
                            print(f'\n  Is basis: {LinAlg.IsBasis(S, n)}')
                        case 4:
                            A = _mat()
                            print(f'\n  Dimension (rank): {LinAlg.Rank(A)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 9:
                    match choice:
                        case 1:
                            print('  Vectors for Gram-Schmidt (blank line to finish):')
                            S = []
                            while True:
                                raw = input('  > ').strip()
                                if not raw: break
                                S.append([float(x) for x in raw.split()])
                            r = LinAlg.GramSchmidt(S)
                            print('\n  Orthonormal basis:')
                            for v in r: print(f'    {[round(x, 6) for x in v]}')
                        case 2:
                            v = _vec(); u = _vec()
                            print(f'\n  proj_u(v) = {[round(x,6) for x in LinAlg.VectorProjection(v, u)]}')
                        case 3:
                            v = _vec()
                            print('  Subspace basis vectors (blank line to finish):')
                            S = []
                            while True:
                                raw = input('  > ').strip()
                                if not raw: break
                                S.append([float(x) for x in raw.split()])
                            r = LinAlg.ProjectOntoSubspace(v, S)
                            print(f'\n  Projection: {[round(x,6) for x in r]}')
                        case 4:
                            a = _vec(); b = _vec()
                            print(f'\n  Orthogonal: {LinAlg.AreOrthogonal(a, b)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 10:
                    A = _sq()
                    match choice:
                        case 1:
                            L, U = LinAlg.LUDecomposition(A)
                            print('\n  L:')
                            for row in L: print(f'    {[round(x,6) for x in row]}')
                            print('  U:')
                            for row in U: print(f'    {[round(x,6) for x in row]}')
                        case 2:
                            Q, R = LinAlg.QRDecomposition(A)
                            print('\n  Q:')
                            for row in Q: print(f'    {[round(x,6) for x in row]}')
                            print('  R:')
                            for row in R: print(f'    {[round(x,6) for x in row]}')
                        case 3:
                            r = LinAlg.CholeskyDecomposition(A)
                            if r is None:
                                print('\n  Matrix is not positive definite.')
                            else:
                                print('\n  Cholesky L:')
                                for row in r: print(f'    {[round(x,6) for x in row]}')
                        case 4:
                            sv = LinAlg.SingularValues(A)
                            print(f'\n  Singular values: {[round(s,6) for s in sv]}')
                        case _: print('\n  That was not a valid option.'); continue
            except _AskAbort:
                print()
                _p('Calculation cancelled. Returning to the function list.')
                print()
                continue
            except Exception as e:
                print(f'\n  Error: {e}')
                print()
                continue
            print()

# ============================================================
# DIFFERENTIAL GEOMETRY DEBUG
# ============================================================

def DifferentialGeometryDebug():
    import math as _m
    SECTIONS = [
        'Curves in ℝ³', 'Frenet-Serret Frame', 'Parametric Surfaces',
        'First Fundamental Form', 'Second Fundamental Form', 'Surface Curvature',
        'Christoffel Symbols', 'Geodesics', 'Differential Forms', 'Special Surfaces',
    ]
    _CURVES = {
        '1': ('Helix  (cos t, sin t, t)',    lambda t: [_m.cos(t), _m.sin(t), t]),
        '2': ('Circle (cos t, sin t, 0)',    lambda t: [_m.cos(t), _m.sin(t), 0.0]),
        '3': ('Parabola (t, t², 0)',         lambda t: [t, t * t, 0.0]),
    }
    _SURFS = {
        '1': ('Unit sphere',        lambda u, v: [_m.sin(u)*_m.cos(v), _m.sin(u)*_m.sin(v), _m.cos(u)]),
        '2': ('Torus  R=2 a=1',     lambda u, v: [(2+_m.cos(v))*_m.cos(u), (2+_m.cos(v))*_m.sin(u), _m.sin(v)]),
        '3': ('Paraboloid z=u²+v²', lambda u, v: [u, v, u*u + v*v]),
        '4': ('Saddle  z=u²-v²',    lambda u, v: [u, v, u*u - v*v]),
    }
    def _curve():
        for k, (n, _) in _CURVES.items(): print(f'    ({k})  {n}')
        return _CURVES.get(_ask('  Curve (1-3): ', cast=str).strip(), _CURVES['1'])[1]
    def _surf():
        for k, (n, _) in _SURFS.items(): print(f'    ({k})  {n}')
        return _SURFS.get(_ask('  Surface (1-4): ', cast=str).strip(), _SURFS['1'])[1]
    while True:
        _SectionHeader('Differential Geometry', 'Choose a section')
        for i, s in enumerate(SECTIONS, 1):
            print(f'  ({i:>2})  {s}')
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section.')
            continue
        while True:
            _SectionHeader('Differential Geometry', SECTIONS[sec - 1])
            if sec == 1:
                print('  (1)  Tangent vector γ\'(t)    (2)  Speed ‖γ\'(t)‖')
                print('  (3)  Acceleration γ\'\'(t)    (4)  Curvature κ(t)')
                print('  (5)  Radius of curvature    (6)  Torsion τ(t)')
                print('  (7)  Arc length ∫ₐᵇ ‖γ\'‖ dt')
            elif sec == 2:
                print('  (1)  Frenet-Serret frame (T, N, B)')
                print('  (2)  Osculating plane')
                print('  (3)  Osculating circle')
                print('  (4)  Total curvature and torsion over [a, b]')
            elif sec == 3:
                print('  (1)  Tangent vectors r_u, r_v    (2)  Surface normal N')
                print('  (3)  Unit normal n̂              (4)  Area element ‖r_u × r_v‖')
                print('  (5)  Surface area ∫∫ dA')
            elif sec == 4:
                print('  (1)  E, F, G     (2)  Metric tensor')
                print('  (3)  ds²         (4)  Angle between coordinate curves')
                print('  (5)  √(EG - F²)')
            elif sec == 5:
                print('  (1)  L, M, N     (2)  Normal curvature κ_n')
                print('  (3)  Shape operator matrix')
            elif sec == 6:
                print('  (1)  Gaussian curvature K    (2)  Mean curvature H')
                print('  (3)  Principal curvatures    (4)  Classify surface point')
                print('  (5)  Total Gaussian curvature ∫∫ K dA')
            elif sec == 7:
                print('  (1)  Christoffel symbols Γᵏᵢⱼ at (u, v)')
            elif sec == 8:
                print('  (1)  Geodesic path    (2)  Geodesic length')
            elif sec == 9:
                print('  (1)  Exterior derivative of 0-form  df')
                print('  (2)  Exterior derivative of 1-form  dω')
                print('  (3)  Line integral ∫_C ω')
                print('  (4)  Wedge product α ∧ β')
            elif sec == 10:
                print('  (1)  Sphere    (2)  Torus    (3)  Cylinder')
                print('  (4)  Paraboloid    (5)  Saddle    (6)  Gauss-Bonnet check')
            print()
            _ExitBar('Return to sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            if choice < 0:
                print('\n  That was not a valid option.')
                continue
            try:
                if sec == 1:
                    curve = _curve()
                    t = _ask('  Parameter t: ', cast=float)
                    match choice:
                        case 1:
                            print(f'\n  γ\'(t) = {[round(x,6) for x in DiffGeo.CurveTangentVector(curve, t)]}')
                        case 2:
                            print(f'\n  Speed = {DiffGeo.CurveSpeed(curve, t):.6f}')
                        case 3:
                            print(f'\n  γ\'\'(t) = {[round(x,6) for x in DiffGeo.CurveAcceleration(curve, t)]}')
                        case 4:
                            print(f'\n  κ(t) = {DiffGeo.Curvature(curve, t):.6f}')
                        case 5:
                            print(f'\n  ρ(t) = {DiffGeo.RadiusOfCurvature(curve, t):.6f}')
                        case 6:
                            print(f'\n  τ(t) = {DiffGeo.Torsion(curve, t):.6f}')
                        case 7:
                            a = _ask('  Lower bound a: ', cast=float)
                            b = _ask('  Upper bound b: ', cast=float)
                            print(f'\n  Arc length = {DiffGeo.ArcLength(curve, a, b):.6f}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 2:
                    curve = _curve()
                    t = _ask('  Parameter t: ', cast=float)
                    match choice:
                        case 1:
                            T, N, B = DiffGeo.FrenetSerretFrame(curve, t)
                            print(f'\n  T = {[round(x,6) for x in T]}')
                            print(f'  N = {[round(x,6) for x in N]}')
                            print(f'  B = {[round(x,6) for x in B]}')
                        case 2:
                            B, pt = DiffGeo.OsculatingPlane(curve, t)
                            print(f'\n  Normal (B) = {[round(x,6) for x in B]}')
                            print(f'  Base point = {[round(x,6) for x in pt]}')
                        case 3:
                            center, rho = DiffGeo.OsculatingCircle(curve, t)
                            if center is None:
                                print('\n  Straight segment — no osculating circle.')
                            else:
                                print(f'\n  Center = {[round(x,6) for x in center]}')
                                print(f'  Radius = {rho:.6f}')
                        case 4:
                            a = _ask('  a: ', cast=float)
                            b = _ask('  b: ', cast=float)
                            tk, tt = DiffGeo.TotalCurvatureAndTorsion(curve, a, b)
                            print(f'\n  ∫κ ds = {tk:.6f}   ∫τ ds = {tt:.6f}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 3:
                    S = _surf()
                    u = _ask('  u: ', cast=float)
                    v = _ask('  v: ', cast=float)
                    match choice:
                        case 1:
                            ru, rv = DiffGeo.SurfaceTangentVectors(S, u, v)
                            print(f'\n  r_u = {[round(x,6) for x in ru]}')
                            print(f'  r_v = {[round(x,6) for x in rv]}')
                        case 2:
                            print(f'\n  N = {[round(x,6) for x in DiffGeo.SurfaceNormal(S, u, v)]}')
                        case 3:
                            print(f'\n  n̂ = {[round(x,6) for x in DiffGeo.UnitNormal(S, u, v)]}')
                        case 4:
                            print(f'\n  dA = {DiffGeo.AreaElement(S, u, v):.6f}')
                        case 5:
                            u0 = _ask('  u0: ', cast=float); u1 = _ask('  u1: ', cast=float)
                            v0 = _ask('  v0: ', cast=float); v1 = _ask('  v1: ', cast=float)
                            print(f'\n  Surface area = {DiffGeo.SurfaceArea(S, u0, u1, v0, v1):.6f}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 4:
                    S = _surf()
                    u = _ask('  u: ', cast=float)
                    v = _ask('  v: ', cast=float)
                    match choice:
                        case 1:
                            E, F, G = DiffGeo.FirstFundamentalForm(S, u, v)
                            print(f'\n  E={E:.6f}  F={F:.6f}  G={G:.6f}')
                        case 2:
                            mt = DiffGeo.MetricTensor(S, u, v)
                            print(f'\n  g = {[[round(x,6) for x in row] for row in mt]}')
                        case 3:
                            du = _ask('  du: ', cast=float); dv = _ask('  dv: ', cast=float)
                            print(f'\n  ds² = {DiffGeo.ArcLengthElement(S, u, v, du, dv):.6f}')
                        case 4:
                            print(f'\n  Angle = {DiffGeo.AngleBetweenCoordinateCurves(S, u, v):.4f}°')
                        case 5:
                            print(f'\n  √(EG-F²) = {DiffGeo.MetricDeterminant(S, u, v):.6f}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 5:
                    S = _surf()
                    u = _ask('  u: ', cast=float)
                    v = _ask('  v: ', cast=float)
                    match choice:
                        case 1:
                            L, M, N = DiffGeo.SecondFundamentalForm(S, u, v)
                            print(f'\n  L={L:.6f}  M={M:.6f}  N={N:.6f}')
                        case 2:
                            du = _ask('  du: ', cast=float); dv = _ask('  dv: ', cast=float)
                            print(f'\n  κ_n = {DiffGeo.NormalCurvature(S, u, v, du, dv):.6f}')
                        case 3:
                            sm = DiffGeo.ShapeOperator(S, u, v)
                            print(f'\n  Shape operator = {[[round(x,6) for x in row] for row in sm]}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 6:
                    S = _surf()
                    u = _ask('  u: ', cast=float)
                    v = _ask('  v: ', cast=float)
                    match choice:
                        case 1: print(f'\n  K = {DiffGeo.GaussianCurvature(S, u, v):.6f}')
                        case 2: print(f'\n  H = {DiffGeo.MeanCurvature(S, u, v):.6f}')
                        case 3:
                            k1, k2 = DiffGeo.PrincipalCurvatures(S, u, v)
                            print(f'\n  κ₁ = {k1:.6f}   κ₂ = {k2:.6f}')
                        case 4:
                            print(f'\n  Point type: {DiffGeo.ClassifySurfacePoint(S, u, v)}')
                        case 5:
                            u0=_ask('  u0: ',cast=float); u1=_ask('  u1: ',cast=float)
                            v0=_ask('  v0: ',cast=float); v1=_ask('  v1: ',cast=float)
                            print(f'\n  ∫∫ K dA = {DiffGeo.TotalGaussianCurvature(S, u0, u1, v0, v1):.6f}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 7:
                    S = _surf()
                    u = _ask('  u: ', cast=float)
                    v = _ask('  v: ', cast=float)
                    G3 = DiffGeo.ChristoffelSymbols(S, u, v)
                    print('\n  Non-zero Γᵏᵢⱼ:')
                    found = False
                    for k in range(2):
                        for i in range(2):
                            for j in range(2):
                                val = G3[k][i][j]
                                if abs(val) > 1e-6:
                                    print(f'    Γ[{k}][{i}][{j}] = {val:.6f}')
                                    found = True
                    if not found:
                        print('    (all zero at this point)')
                elif sec == 8:
                    S = _surf()
                    match choice:
                        case 1:
                            u0=_ask('  u0: ',cast=float); v0=_ask('  v0: ',cast=float)
                            du=_ask('  Initial du/ds: ',cast=float); dv=_ask('  Initial dv/ds: ',cast=float)
                            s_max=_ask('  s_max (arc length to trace): ',cast=float)
                            path = DiffGeo.GeodesicPath(S, u0, v0, du, dv, s_max)
                            step = max(1, len(path) // 8)
                            print(f'\n  Geodesic ({len(path)} points):')
                            for i in range(0, len(path), step):
                                print(f'    (u,v) = ({path[i][0]:.4f}, {path[i][1]:.4f})')
                        case 2:
                            u0=_ask('  u0: ',cast=float); v0=_ask('  v0: ',cast=float)
                            du=_ask('  du/ds: ',cast=float); dv=_ask('  dv/ds: ',cast=float)
                            s_max=_ask('  s_max: ',cast=float)
                            path = DiffGeo.GeodesicPath(S, u0, v0, du, dv, s_max)
                            print(f'\n  Geodesic length = {DiffGeo.GeodesicLength(S, path):.6f}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 9:
                    match choice:
                        case 1:
                            x=_ask('  x: ',cast=float); y=_ask('  y: ',cast=float); z=_ask('  z: ',cast=float)
                            r = DiffGeo.ExteriorDerivative0Form(lambda a,b,c: a**2+b**2+c**2, x, y, z)
                            print(f'\n  df (for f=x²+y²+z²) = {[round(c,6) for c in r]}')
                        case 2:
                            x=_ask('  x: ',cast=float); y=_ask('  y: ',cast=float); z=_ask('  z: ',cast=float)
                            r = DiffGeo.ExteriorDerivative1Form(
                                lambda a,b,c: b, lambda a,b,c: 0.0, lambda a,b,c: 0.0, x, y, z)
                            print(f'\n  d(y dx) = {[round(c,6) for c in r]}')
                        case 3:
                            curve = _curve()
                            a=_ask('  a: ',cast=float); b=_ask('  b: ',cast=float)
                            r = DiffGeo.LineIntegralOf1Form(
                                lambda a,b,c: b, lambda a,b,c: 0.0, lambda a,b,c: 0.0, curve, a, b)
                            print(f'\n  ∫_C(y dx) = {r:.6f}')
                        case 4:
                            alpha = [_ask(f'  α[{i}]: ', cast=float) for i in range(3)]
                            beta  = [_ask(f'  β[{i}]: ', cast=float) for i in range(3)]
                            print(f'\n  α ∧ β = {[round(c,6) for c in DiffGeo.WedgeProduct1Forms(alpha, beta)]}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 10:
                    match choice:
                        case 1:
                            r = _ask('  Radius r: ', cast=float)
                            _, K, H, area = DiffGeo.Sphere(r)
                            print(f'\n  K={K:.6f}  H={H:.6f}  Area={area:.6f}')
                        case 2:
                            R = _ask('  Major radius R: ', cast=float)
                            a = _ask('  Tube radius a: ', cast=float)
                            _, Kf, Hf, area = DiffGeo.Torus(R, a)
                            u = _ask('  θ: ', cast=float); v = _ask('  φ: ', cast=float)
                            print(f'\n  Area={area:.6f}  K(θ,φ)={Kf(u,v):.6f}  H(θ,φ)={Hf(u,v):.6f}')
                        case 3:
                            r = _ask('  Radius r: ', cast=float)
                            _, K, H = DiffGeo.Cylinder(r)
                            print(f'\n  K={K:.6f}  H={H:.6f}')
                        case 4:
                            _, Kf, Hf = DiffGeo.Paraboloid()
                            u=_ask('  u: ',cast=float); v=_ask('  v: ',cast=float)
                            print(f'\n  K={Kf(u,v):.6f}  H={Hf(u,v):.6f}')
                        case 5:
                            _, Kf, Hf = DiffGeo.Saddle()
                            u=_ask('  u: ',cast=float); v=_ask('  v: ',cast=float)
                            print(f'\n  K={Kf(u,v):.6f}  H={Hf(u,v):.6f}')
                        case 6:
                            total_k = _ask('  ∫∫ K dA: ', cast=float)
                            chi_f, chi_i = DiffGeo.GaussBonnetCheck(total_k)
                            print(f'\n  χ = {chi_f:.6f}  (nearest integer: {chi_i})')
                        case _: print('\n  That was not a valid option.'); continue
            except _AskAbort:
                print()
                _p('Calculation cancelled. Returning to the function list.')
                print()
                continue
            except Exception as e:
                print(f'\n  Error: {e}')
                print()
                continue
            print()

# ============================================================
# ABSTRACT ALGEBRA DEBUG
# ============================================================

def AbstractAlgebraDebug():
    SECTIONS = [
        'Groups', 'Subgroups & Cosets', 'Normal Subgroups & Quotients',
        'Homomorphisms', 'Permutation Groups', 'Rings',
        'Ideals', 'Fields', 'Polynomial Rings mod p', 'Group Actions & Burnside',
    ]
    def _Zn():
        return AbsAlg.CyclicGroupZn(_ask('  n for ℤₙ: ', cast=int))
    def _poly(lbl='f'):
        raw = _ask(f'  Poly {lbl} coefficients (ascending degree, space-sep): ', cast=str)
        return [float(x) for x in raw.split()]
    def _perm():
        raw = _ask('  Permutation image values (e.g. "2 3 1" for σ(1)=2,σ(2)=3,σ(3)=1): ', cast=str)
        vals = [int(x) for x in raw.split()]
        return {i+1: vals[i] for i in range(len(vals))}
    while True:
        _SectionHeader('Abstract Algebra', 'Choose a section')
        for i, s in enumerate(SECTIONS, 1):
            print(f'  ({i:>2})  {s}')
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section.')
            continue
        while True:
            _SectionHeader('Abstract Algebra', SECTIONS[sec - 1])
            if sec == 1:
                print('  (1)  Is group?  (2)  Is abelian?  (3)  |G|')
                print('  (4)  Element order ord(g)  (5)  Cyclic subgroup ⟨g⟩')
                print('  (6)  Generators of ℤₙ  (7)  Cayley table')
            elif sec == 2:
                print('  (1)  Is subgroup?  (2)  Left coset aH  (3)  Right coset Ha')
                print('  (4)  All left cosets  (5)  Lagrange\'s theorem  (6)  Center Z(G)')
            elif sec == 3:
                print('  (1)  Is normal subgroup?  (2)  Quotient group G/N')
                print('  (3)  Commutator [a,b]  (4)  Commutator subgroup [G,G]')
            elif sec == 4:
                print('  (1)  Is homomorphism?  (2)  Kernel  (3)  Image')
                print('  (4)  First Isomorphism Theorem')
            elif sec == 5:
                print('  (1)  Symmetric group Sₙ  (2)  Alternating group Aₙ')
                print('  (3)  Cycle decomposition  (4)  Cycle type  (5)  ord(σ)')
                print('  (6)  Sign ±1  (7)  Compose σ∘τ  (8)  Inverse σ⁻¹')
            elif sec == 6:
                print('  (1)  Is ring?  (2)  Is commutative?  (3)  Unity')
                print('  (4)  Zero divisors  (5)  Characteristic  (6)  Integral domain?')
            elif sec == 7:
                print('  (1)  Is ideal?  (2)  Principal ideal ⟨a⟩')
                print('  (3)  Is prime ideal?  (4)  Is maximal ideal?')
            elif sec == 8:
                print('  (1)  Is field?  (2)  Multiplicative inverse a⁻¹ mod p')
                print('  (3)  Field characteristic  (4)  Prime subfield')
            elif sec == 9:
                print('  (1)  f+g  (2)  f·g  (3)  f÷g  (4)  gcd(f,g)')
                print('  (5)  f(a) mod p  (6)  Roots of f in 𝔽ₚ  (7)  Is f irreducible?')
            elif sec == 10:
                print('  (1)  Orbit of x  (2)  Stabilizer of x  (3)  Orbit-Stabilizer')
                print('  (4)  All orbits  (5)  Burnside\'s lemma (necklace)')
                print('  (6)  Conjugacy class  (7)  All conjugacy classes  (8)  Class equation')
            print()
            _ExitBar('Return to sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            if choice < 0:
                print('\n  That was not a valid option.')
                continue
            try:
                if sec == 1:
                    elems, op = _Zn()
                    ident = AbsAlg._find_identity(elems, op)
                    match choice:
                        case 1:
                            is_g, cl, as_, id_, inv = AbsAlg.IsGroup(elems, op)
                            print(f'\n  Is group: {is_g}  identity={id_}  closed={cl}  assoc={as_}  inverses={inv}')
                        case 2: print(f'\n  Is abelian: {AbsAlg.IsAbelian(elems, op)}')
                        case 3: print(f'\n  |G| = {AbsAlg.GroupOrder(elems)}')
                        case 4:
                            g = _ask('  Element g: ', cast=int)
                            print(f'\n  ord({g}) = {AbsAlg.ElementOrder(g, op, ident)}')
                        case 5:
                            g = _ask('  Generator g: ', cast=int)
                            print(f'\n  ⟨{g}⟩ = {AbsAlg.CyclicSubgroup(g, op, ident)}')
                        case 6:
                            print(f'\n  Generators: {AbsAlg.Generators(elems, op, ident)}')
                        case 7:
                            tbl = AbsAlg.CayleyTable(elems, op)
                            print(f'\n  Cayley table (elements: {elems}):')
                            for row in tbl: print(f'    {row}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 2:
                    elems, op = _Zn()
                    ident = AbsAlg._find_identity(elems, op)
                    H = [int(x) for x in _ask('  Subgroup H elements (space-sep): ', cast=str).split()]
                    match choice:
                        case 1: print(f'\n  Is subgroup: {AbsAlg.IsSubgroup(H, elems, op, ident)}')
                        case 2:
                            a = _ask('  a: ', cast=int)
                            print(f'\n  aH = {AbsAlg.LeftCoset(a, H, op)}')
                        case 3:
                            a = _ask('  a: ', cast=int)
                            print(f'\n  Ha = {AbsAlg.RightCoset(H, a, op)}')
                        case 4:
                            print('\n  All left cosets:')
                            for c in AbsAlg.AllLeftCosets(elems, H, op): print(f'    {c}')
                        case 5:
                            idx, div = AbsAlg.LagrangesTheorem(elems, H)
                            print(f'\n  [G:H] = {idx}   |H| divides |G|: {div}')
                        case 6:
                            print(f'\n  Z(G) = {AbsAlg.Center(elems, op)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 3:
                    elems, op = _Zn()
                    ident = AbsAlg._find_identity(elems, op)
                    N = [int(x) for x in _ask('  Normal subgroup N elements (space-sep): ', cast=str).split()]
                    match choice:
                        case 1:
                            print(f'\n  Is normal: {AbsAlg.IsNormalSubgroup(N, elems, op, ident)}')
                        case 2:
                            cosets, cop = AbsAlg.QuotientGroup(elems, N, op, ident)
                            if cosets is None:
                                print('\n  N is not a normal subgroup — quotient undefined.')
                            else:
                                print(f'\n  G/N has {len(cosets)} cosets:')
                                for c in cosets: print(f'    {c}')
                        case 3:
                            a = _ask('  a: ', cast=int); b = _ask('  b: ', cast=int)
                            pairs = AbsAlg._inverses_map(elems, op, ident)
                            print(f'\n  [a,b] = {AbsAlg.Commutator(a, b, op, pairs)}')
                        case 4:
                            print(f'\n  [G,G] = {AbsAlg.CommutatorSubgroup(elems, op, ident)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 4:
                    n = _ask('  n (source ℤₙ): ', cast=int)
                    m = _ask('  m (target ℤₘ): ', cast=int)
                    eG, opG = AbsAlg.CyclicGroupZn(n)
                    eH, opH = AbsAlg.CyclicGroupZn(m)
                    phi = {x: x % m for x in eG}
                    id_H = AbsAlg._find_identity(eH, opH)
                    match choice:
                        case 1:
                            print(f'\n  Is homomorphism (x mod {m}): {AbsAlg.IsHomomorphism(eG, eH, phi, opG, opH)}')
                        case 2:
                            print(f'\n  ker(φ) = {sorted(AbsAlg.Kernel(phi, id_H))}')
                        case 3:
                            print(f'\n  im(φ) = {sorted(AbsAlg.Image(phi))}')
                        case 4:
                            ker, img, idx = AbsAlg.FirstIsomorphismTheorem(eG, phi, opG, id_H)
                            print(f'\n  ker={sorted(ker)}   im={sorted(img)}   |G/ker|={idx}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 5:
                    n = _ask('  n for Sₙ (≤5 recommended): ', cast=int)
                    match choice:
                        case 1:
                            S = AbsAlg.SymmetricGroup(n)
                            print(f'\n  |S{n}| = {len(S)}  (first 6):')
                            for s in S[:6]: print(f'    {dict(s)}')
                        case 2:
                            A = AbsAlg.AlternatingGroup(n)
                            print(f'\n  |A{n}| = {len(A)}  (first 6):')
                            for s in A[:6]: print(f'    {dict(s)}')
                        case 3:
                            sigma = _perm()
                            print(f'\n  Cycles: {AbsAlg.CycleDecomposition(sigma)}')
                        case 4:
                            sigma = _perm()
                            print(f'\n  Cycle type: {AbsAlg.CycleType(sigma)}')
                        case 5:
                            sigma = _perm()
                            print(f'\n  ord(σ) = {AbsAlg.PermOrder(sigma)}')
                        case 6:
                            sigma = _perm()
                            print(f'\n  sgn(σ) = {AbsAlg.PermSign(sigma)}')
                        case 7:
                            sigma = _perm(); tau = _perm()
                            print(f'\n  σ∘τ = {dict(AbsAlg.PermCompose(sigma, tau))}')
                        case 8:
                            sigma = _perm()
                            print(f'\n  σ⁻¹ = {dict(AbsAlg.PermInverse(sigma))}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 6:
                    elems, add, mul = AbsAlg.RingZn(_ask('  n for ℤₙ: ', cast=int))
                    match choice:
                        case 1:
                            is_r, ao, ma, di = AbsAlg.IsRing(elems, add, mul)
                            print(f'\n  Is ring: {is_r}  (add_ok={ao}, mul_assoc={ma}, distrib={di})')
                        case 2: print(f'\n  Commutative: {AbsAlg.IsCommutativeRing(elems, mul)}')
                        case 3: print(f'\n  Unity: {AbsAlg.RingUnity(elems, mul)}')
                        case 4: print(f'\n  Zero divisors: {AbsAlg.ZeroDivisors(elems, add, mul)}')
                        case 5:
                            unity = AbsAlg.RingUnity(elems, mul)
                            print(f'\n  char(R) = {AbsAlg.RingCharacteristic(elems, add, unity)}')
                        case 6: print(f'\n  Integral domain: {AbsAlg.IsIntegralDomain(elems, add, mul)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 7:
                    n = _ask('  n for ℤₙ: ', cast=int)
                    elems, add, mul = AbsAlg.RingZn(n)
                    zero = AbsAlg._find_identity(elems, add)
                    I = [int(x) for x in _ask('  Ideal I elements (space-sep): ', cast=str).split()]
                    match choice:
                        case 1: print(f'\n  Is ideal: {AbsAlg.IsIdeal(I, elems, add, mul, zero)}')
                        case 2:
                            a = _ask('  Generator a: ', cast=int)
                            print(f'\n  ⟨{a}⟩ = {AbsAlg.PrincipalIdeal(a, elems, mul)}')
                        case 3: print(f'\n  Is prime ideal: {AbsAlg.IsPrimeIdeal(I, elems, mul)}')
                        case 4: print(f'\n  Is maximal ideal: {AbsAlg.IsMaximalIdeal(I, elems, add, mul, zero)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 8:
                    p = _ask('  Prime p: ', cast=int)
                    fe, fa, fm = AbsAlg.PrimeField(p)
                    match choice:
                        case 1:
                            is_f, *_ = AbsAlg.IsField(fe, fa, fm)
                            print(f'\n  𝔽_{p} is field: {is_f}')
                        case 2:
                            a = _ask('  a: ', cast=int)
                            print(f'\n  {a}⁻¹ mod {p} = {AbsAlg.FieldInverse(a, p)}')
                        case 3: print(f'\n  char(𝔽_{p}) = {AbsAlg.FieldCharacteristic(fe, fa, fm)}')
                        case 4: print(f'\n  Prime subfield: {AbsAlg.PrimeSubfield(fe, fa, fm)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 9:
                    p = _ask('  Prime p: ', cast=int)
                    f = _poly('f'); g = _poly('g')
                    match choice:
                        case 1: print(f'\n  f+g = {AbsAlg.PolyAdd(f, g, p)}')
                        case 2: print(f'\n  f·g = {AbsAlg.PolyMul(f, g, p)}')
                        case 3:
                            q, r = AbsAlg.PolyDivMod(f, g, p)
                            print(f'\n  q = {q}   r = {r}')
                        case 4: print(f'\n  gcd(f,g) = {AbsAlg.PolyGCD(f, g, p)}')
                        case 5:
                            a = _ask('  a: ', cast=int)
                            print(f'\n  f({a}) mod {p} = {AbsAlg.PolyEval(f, a, p)}')
                        case 6: print(f'\n  Roots of f in 𝔽_{p}: {AbsAlg.PolyRoots(f, p)}')
                        case 7: print(f'\n  Irreducible over 𝔽_{p}: {AbsAlg.IsIrreducible(f, p)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 10:
                    match choice:
                        case 1 | 2 | 3 | 4:
                            elems, op = _Zn()
                            ident = AbsAlg._find_identity(elems, op)
                            x = _ask('  Element x: ', cast=int)
                            act = lambda g, xv: op(g, xv)
                            if choice == 1:
                                print(f'\n  Orbit({x}) = {AbsAlg.Orbit(x, elems, act)}')
                            elif choice == 2:
                                print(f'\n  Stabilizer({x}) = {AbsAlg.Stabilizer(x, elems, act)}')
                            elif choice == 3:
                                o, s, pr, G = AbsAlg.OrbitStabilizerTheorem(x, elems, act)
                                print(f'\n  |Orb|={o}  |Stab|={s}  product={pr}  |G|={G}')
                            elif choice == 4:
                                print('\n  All orbits:')
                                for orb in AbsAlg.AllOrbits(elems, elems, act):
                                    print(f'    {orb}')
                        case 5:
                            k = _ask('  Bead colors k: ', cast=int)
                            nb = _ask('  Number of beads n: ', cast=int)
                            import itertools as _it
                            X = list(_it.product(range(k), repeat=nb))
                            G = list(range(nb))
                            def _ra(r, c):
                                c = list(c)
                                for _ in range(r): c = [c[-1]] + c[:-1]
                                return tuple(c)
                            n_orb, _ = AbsAlg.BurnsideLemma(X, G, _ra)
                            print(f'\n  Distinct necklaces ({k} colors, {nb} beads): {n_orb}')
                        case 6 | 7 | 8:
                            n = _ask('  n for Sₙ: ', cast=int)
                            S = AbsAlg.SymmetricGroup(n)
                            sid = AbsAlg.PermIdentity(n)
                            if choice == 6:
                                g = _perm()
                                pairs = AbsAlg._inverses_map(S, AbsAlg.PermCompose, sid)
                                cls = AbsAlg.ConjugacyClass(g, S, AbsAlg.PermCompose, pairs)
                                print(f'\n  Conjugacy class size: {len(cls)}')
                            elif choice == 7:
                                cc = AbsAlg.AllConjugacyClasses(S, AbsAlg.PermCompose, sid)
                                print(f'\n  {len(cc)} conjugacy classes in S{n}:')
                                for i, c in enumerate(cc, 1): print(f'    Class {i}: size {len(c)}')
                            elif choice == 8:
                                n_ord, nc, sizes = AbsAlg.ClassEquation(S, AbsAlg.PermCompose, sid)
                                print(f'\n  |S{n}|={n_ord}   |Z(S{n})|={nc}   class sizes={sorted(sizes)}')
                        case _: print('\n  That was not a valid option.'); continue
            except _AskAbort:
                print()
                _p('Calculation cancelled. Returning to the function list.')
                print()
                continue
            except Exception as e:
                print(f'\n  Error: {e}')
                print()
                continue
            print()


# ============================================================
# TOPOLOGY DEBUG
# ============================================================

def TopologyDebug():
    SECTIONS = [
        'Topological Spaces', 'Bases & Subbases', 'Continuity & Homeomorphisms',
        'Separation Axioms', 'Compactness', 'Connectedness',
        'Metric Topology', 'Simplicial Complexes', 'Homotopy Basics', 'Product & Quotient Topologies',
    ]
    def _pts_oss():
        pts = [int(x) for x in _ask('  Points (space-sep integers, e.g. "1 2 3"): ', cast=str).split()]
        print('  Open sets — one per line (space-sep elements), blank line to finish:')
        oss = []
        while True:
            raw = input('  > ').strip()
            if not raw: break
            oss.append(frozenset(int(x) for x in raw.split()))
        return pts, oss
    def _simplices():
        print('  Simplices — one per line (space-sep vertices), blank line to finish:')
        simps = []
        while True:
            raw = input('  > ').strip()
            if not raw: break
            simps.append(frozenset(int(x) for x in raw.split()))
        return simps
    while True:
        _SectionHeader('Topology', 'Choose a section')
        for i, s in enumerate(SECTIONS, 1):
            print(f'  ({i:>2})  {s}')
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section.')
            continue
        while True:
            _SectionHeader('Topology', SECTIONS[sec - 1])
            if sec == 1:
                print('  (1)  Verify topology  (2)  Discrete topology  (3)  Indiscrete topology')
                print('  (4)  Interior of A    (5)  Closure of A       (6)  Boundary of A')
                print('  (7)  Is A dense?      (8)  List closed sets')
            elif sec == 2:
                print('  (1)  Is a collection a base?')
                print('  (2)  Topology generated by a subbasis')
                print('  (3)  Neighbourhoods of a point')
            elif sec == 3:
                print('  (1)  Is a function continuous?')
                print('  (2)  Is a function a homeomorphism?')
            elif sec == 4:
                print('  (1)  Separation axiom tier  (T0–T4)')
                print('  (2)  Is T0?  (3)  Is T1?  (4)  Is T2 (Hausdorff)?')
                print('  (5)  Is T3 (Regular)?  (6)  Is T4 (Normal)?')
            elif sec == 5:
                print('  (1)  Is compact?  (2)  Is subset compact?')
            elif sec == 6:
                print('  (1)  Is connected?  (2)  Is path-connected?')
                print('  (3)  Connected components  (4)  Is locally connected?  (5)  π₀(X)')
            elif sec == 7:
                print('  (1)  Open ball B(x,r)  (2)  Diameter of a set')
                print('  (3)  Distance d(x,A)   (4)  Hausdorff distance')
                print('  (5)  Is Cauchy sequence?')
            elif sec == 8:
                print('  (1)  Is simplicial complex?  (2)  f-vector')
                print('  (3)  Euler characteristic χ  (4)  Betti numbers β₀, β₁, β₂')
                print('  (5)  Complex dimension       (6)  Star of a vertex')
                print('  (7)  Link of a vertex')
            elif sec == 9:
                print('  (1)  Is graph simply connected?')
                print('  (2)  π₀  — number of path components')
            elif sec == 10:
                print('  (1)  Product topology  (2)  Subspace topology  (3)  Full topology profile')
            print()
            _ExitBar('Return to sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            if choice < 0:
                print('\n  That was not a valid option.')
                continue
            try:
                if sec == 1:
                    pts, oss = _pts_oss()
                    match choice:
                        case 1:
                            is_t, emp, whole, uc, ic = Topo.IsTopology(pts, oss)
                            print(f'\n  Valid topology: {is_t}')
                            print(f'  ∅ ∈ τ: {emp}   X ∈ τ: {whole}   ∪-closed: {uc}   ∩-closed: {ic}')
                        case 2:
                            _, d_oss = Topo.DiscreteTopology(pts)
                            print(f'\n  Discrete topology: {len(d_oss)} open sets')
                        case 3:
                            _, i_oss = Topo.IndiscreteTopology(pts)
                            print(f'\n  Indiscrete topology: {[set(u) for u in i_oss]}')
                        case 4:
                            A = [int(x) for x in _ask('  Subset A (space-sep): ', cast=str).split()]
                            print(f'\n  int(A) = {set(Topo.Interior(A, oss))}')
                        case 5:
                            A = [int(x) for x in _ask('  Subset A (space-sep): ', cast=str).split()]
                            print(f'\n  cl(A) = {set(Topo.Closure(A, pts, oss))}')
                        case 6:
                            A = [int(x) for x in _ask('  Subset A (space-sep): ', cast=str).split()]
                            print(f'\n  ∂A = {set(Topo.Boundary(A, pts, oss))}')
                        case 7:
                            A = [int(x) for x in _ask('  Subset A (space-sep): ', cast=str).split()]
                            print(f'\n  Dense: {Topo.IsDense(A, pts, oss)}')
                        case 8:
                            closed = Topo.ClosedSets(pts, oss)
                            print(f'\n  {len(closed)} closed sets:')
                            for c in closed: print(f'    {set(c)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 2:
                    pts, oss = _pts_oss()
                    match choice:
                        case 1:
                            print('  Enter base sets (blank to finish):')
                            base = []
                            while True:
                                raw = input('  > ').strip()
                                if not raw: break
                                base.append(frozenset(int(x) for x in raw.split()))
                            print(f'\n  Is base for this topology: {Topo.IsBase(base, oss)}')
                        case 2:
                            print('  Enter subbasis sets (blank to finish):')
                            sub = []
                            while True:
                                raw = input('  > ').strip()
                                if not raw: break
                                sub.append(frozenset(int(x) for x in raw.split()))
                            _, gen_oss = Topo.TopologyFromSubbasis(pts, sub)
                            print(f'\n  Generated topology: {len(gen_oss)} open sets')
                        case 3:
                            x = _ask('  Point x: ', cast=int)
                            nbhds = Topo.Neighbourhoods(x, oss)
                            print(f'\n  Neighbourhoods of {x}:')
                            for n in nbhds: print(f'    {set(n)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 3:
                    print('  Domain topology:'); pts_X, oss_X = _pts_oss()
                    print('  Codomain topology:'); pts_Y, oss_Y = _pts_oss()
                    raw = _ask('  f as "x:f(x)" pairs (space-sep, e.g. "1:2 2:3"): ', cast=str)
                    f = {int(p.split(':')[0]): int(p.split(':')[1]) for p in raw.split()}
                    match choice:
                        case 1: print(f'\n  Continuous: {Topo.IsContinuous(f, oss_X, oss_Y)}')
                        case 2: print(f'\n  Homeomorphism: {Topo.IsHomeomorphism(f, pts_X, oss_X, pts_Y, oss_Y)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 4:
                    pts, oss = _pts_oss()
                    match choice:
                        case 1: print(f'\n  Separation: {Topo.SeparationAxiom(pts, oss)}')
                        case 2: print(f'\n  T0: {Topo.IsT0(pts, oss)}')
                        case 3: print(f'\n  T1: {Topo.IsT1(pts, oss)}')
                        case 4: print(f'\n  T2 (Hausdorff): {Topo.IsHausdorff(pts, oss)}')
                        case 5: print(f'\n  T3 (Regular): {Topo.IsRegular(pts, oss)}')
                        case 6: print(f'\n  T4 (Normal): {Topo.IsNormal(pts, oss)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 5:
                    pts, oss = _pts_oss()
                    match choice:
                        case 1: print(f'\n  Compact: {Topo.IsCompact(pts, oss)}')
                        case 2:
                            A = [int(x) for x in _ask('  Subset A: ', cast=str).split()]
                            print(f'\n  A compact: {Topo.IsCompactSubset(A, pts, oss)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 6:
                    pts, oss = _pts_oss()
                    match choice:
                        case 1: print(f'\n  Connected: {Topo.IsConnected(pts, oss)}')
                        case 2: print(f'\n  Path-connected: {Topo.IsPathConnected(pts, oss)}')
                        case 3:
                            comps = Topo.ConnectedComponents(pts, oss)
                            print(f'\n  {len(comps)} component(s):')
                            for c in comps: print(f'    {set(c)}')
                        case 4: print(f'\n  Locally connected: {Topo.IsLocallyConnected(pts, oss)}')
                        case 5: print(f'\n  π₀(X) = {Topo.Pi0(pts, oss)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 7:
                    raw = _ask('  Points (numeric, space-sep): ', cast=str)
                    pts_m = [float(x) for x in raw.split()]
                    dist = lambda a, b: abs(a - b)
                    match choice:
                        case 1:
                            x = _ask('  Center x: ', cast=float); r = _ask('  Radius r: ', cast=float)
                            print(f'\n  B({x},{r}) = {sorted(Topo.OpenBall(x, r, pts_m, dist))}')
                        case 2:
                            A = [float(x) for x in _ask('  Subset A: ', cast=str).split()]
                            print(f'\n  diam(A) = {Topo.Diameter(A, dist):.6f}')
                        case 3:
                            x = _ask('  Point x: ', cast=float)
                            A = [float(v) for v in _ask('  Set A: ', cast=str).split()]
                            print(f'\n  d({x},A) = {Topo.DistanceToSet(x, A, dist):.6f}')
                        case 4:
                            A = [float(x) for x in _ask('  Set A: ', cast=str).split()]
                            B = [float(x) for x in _ask('  Set B: ', cast=str).split()]
                            print(f'\n  d_H(A,B) = {Topo.HausdorffDistance(A, B, dist):.6f}')
                        case 5:
                            seq = [float(x) for x in _ask('  Sequence: ', cast=str).split()]
                            tol = _ask('  ε: ', cast=float)
                            print(f'\n  Cauchy: {Topo.IsCauchySequence(seq, dist, tol)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 8:
                    simps = _simplices()
                    match choice:
                        case 1: print(f'\n  Simplicial complex: {Topo.IsSimplicialComplex(simps)}')
                        case 2:
                            fv = Topo.FVector(simps)
                            print(f'\n  f-vector: {fv}')
                        case 3: print(f'\n  χ = {Topo.EulerCharacteristic(simps)}')
                        case 4:
                            b = Topo.BettiNumbers(simps)
                            print(f'\n  β₀={b["beta0"]}  β₁={b["beta1"]}  β₂={b["beta2"]}  χ={b["chi"]}')
                        case 5: print(f'\n  dim(Δ) = {Topo.ComplexDimension(simps)}')
                        case 6:
                            v = _ask('  Vertex v: ', cast=int)
                            print(f'\n  Star({v}):')
                            for s in Topo.Star(v, simps): print(f'    {set(s)}')
                        case 7:
                            v = _ask('  Vertex v: ', cast=int)
                            print(f'\n  Link({v}):')
                            for s in Topo.Link(v, simps): print(f'    {set(s)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 9:
                    pts, oss = _pts_oss()
                    match choice:
                        case 1:
                            raw = _ask('  Adjacency as "v:nbrs" (e.g. "1:2,3 2:1 3:1"): ', cast=str)
                            adj = {}
                            for token in raw.split():
                                v, ns = token.split(':')
                                adj[int(v)] = set(int(x) for x in ns.split(',') if x)
                            print(f'\n  Simply connected: {Topo.IsSimplyConnected(adj)}')
                        case 2:
                            print(f'\n  π₀(X) = {Topo.Pi0(pts, oss)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 10:
                    match choice:
                        case 1:
                            print('  Space X:'); pts_X, oss_X = _pts_oss()
                            print('  Space Y:'); pts_Y, oss_Y = _pts_oss()
                            pp, po = Topo.ProductTopology(pts_X, oss_X, pts_Y, oss_Y)
                            print(f'\n  Product space: {len(pp)} points, {len(po)} open sets')
                        case 2:
                            pts, oss = _pts_oss()
                            A = [int(x) for x in _ask('  Subspace A: ', cast=str).split()]
                            _, sub_oss = Topo.SubspaceTopology(A, oss)
                            print(f'\n  Subspace topology: {len(sub_oss)} open sets')
                            for u in sub_oss: print(f'    {set(u)}')
                        case 3:
                            pts, oss = _pts_oss()
                            profile = Topo.TopologyProfile(pts, oss)
                            print()
                            for k, v in profile.items():
                                print(f'  {k}: {v}')
                        case _: print('\n  That was not a valid option.'); continue
            except _AskAbort:
                print()
                _p('Calculation cancelled. Returning to the function list.')
                print()
                continue
            except Exception as e:
                print(f'\n  Error: {e}')
                print()
                continue
            print()


# ============================================================
# ALGEBRAIC GEOMETRY DEBUG
# ============================================================

def AlgebraicGeometryDebug():
    SECTIONS = [
        'Affine Varieties', 'Polynomial Operations', 'Ideals & Radicals',
        'Curves in ℝ²', 'Projective Geometry', 'Elliptic Curves',
        'Singularities', 'Intersection Theory', 'Hilbert & Dimension', 'Common Curves',
    ]
    def _p1(lbl='f'):
        raw = _ask(f'  Poly {lbl} (ascending degree coefficients, space-sep): ', cast=str)
        return [float(x) for x in raw.split()]
    def _p2(lbl='f'):
        print(f'  {lbl}(x,y): enter "i j coeff" lines (blank to finish):')
        poly = {}
        while True:
            raw = input('  > ').strip()
            if not raw: break
            i, j, c = raw.split()
            poly[(int(i), int(j))] = float(c)
        return poly
    while True:
        _SectionHeader('Algebraic Geometry', 'Choose a section')
        for i, s in enumerate(SECTIONS, 1):
            print(f'  ({i:>2})  {s}')
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section.')
            continue
        while True:
            _SectionHeader('Algebraic Geometry', SECTIONS[sec - 1])
            if sec == 1:
                print('  (1)  Real roots V(f)  (2)  Variety of ideal V(I)  (3)  Is point on variety?')
            elif sec == 2:
                print('  (1)  f+g  (2)  f·g  (3)  f÷g  (4)  gcd  (5)  lcm')
                print('  (6)  f(a)  (7)  f\'  (8)  deg  (9)  Square-free?  (10) Monic')
            elif sec == 3:
                print('  (1)  Resultant  (2)  Discriminant  (3)  Radical √⟨f⟩')
            elif sec == 4:
                print('  (1)  Tangent line to implicit curve  (2)  Root multiplicity')
                print('  (3)  Is smooth point?  (4)  Is singular point?')
                print('  (5)  Genus g=(d-1)(d-2)/2  (6)  Bezout number d₁·d₂')
            elif sec == 5:
                print('  (1)  Cross-ratio of 4 points  (2)  Projective equivalence')
                print('  (3)  Classify conic')
            elif sec == 6:
                print('  (1)  Δ = -16(4a³+27b²)  (2)  j-invariant  (3)  Is point on curve?')
                print('  (4)  Negate point  (5)  Add P+Q  (6)  Scalar [n]P')
                print('  (7)  Point order  (8)  All points over 𝔽ₚ  (9)  Hasse interval')
            elif sec == 7:
                print('  (1)  Singular locus  (2)  Is node?  (3)  Is cusp?  (4)  Delta-invariant')
            elif sec == 8:
                print('  (1)  Intersection multiplicity  (2)  Geometric genus')
            elif sec == 9:
                print('  (1)  H(d) Hilbert function  (2)  Hilbert polynomial')
                print('  (3)  Krull dimension  (4)  Variety degree')
            elif sec == 10:
                print('  (1)  Conic  (2)  Elliptic curve poly  (3)  Nodal cubic')
                print('  (4)  Cuspidal cubic  (5)  Fermat curve xⁿ+yⁿ=1')
            print()
            _ExitBar('Return to sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            if choice < 0:
                print('\n  That was not a valid option.')
                continue
            try:
                if sec == 1:
                    match choice:
                        case 1:
                            f = _p1()
                            print(f'\n  V(f) = {AlgGeo.AffineVariety1D(f)}')
                        case 2:
                            n = _ask('  Number of polynomials: ', cast=int)
                            polys = [_p1(f'f{i+1}') for i in range(n)]
                            print(f'\n  V(I) = {AlgGeo.AffineVarietyOfIdeal(polys)}')
                        case 3:
                            f = _p1(); p = _ask('  Point p: ', cast=float)
                            print(f'\n  {p} ∈ V(f): {AlgGeo.IsOnVariety(p, f)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 2:
                    if choice <= 5:
                        f = _p1('f'); g = _p1('g')
                        match choice:
                            case 1: print(f'\n  f+g = {AlgGeo.PolyAdd(f, g)}')
                            case 2: print(f'\n  f·g = {AlgGeo.PolyMul(f, g)}')
                            case 3:
                                q, r = AlgGeo.PolyDivMod(f, g)
                                print(f'\n  q = {q}\n  r = {r}')
                            case 4: print(f'\n  gcd = {AlgGeo.PolyGCD(f, g)}')
                            case 5: print(f'\n  lcm = {AlgGeo.PolyLCM(f, g)}')
                    else:
                        f = _p1()
                        match choice:
                            case 6:
                                a = _ask('  a: ', cast=float)
                                print(f'\n  f({a}) = {AlgGeo.PolyEval(f, a):.6f}')
                            case 7: print(f'\n  f\' = {AlgGeo.PolynomialDerivative(f)}')
                            case 8: print(f'\n  deg(f) = {AlgGeo.PolyDegree(f)}')
                            case 9: print(f'\n  Square-free: {AlgGeo.IsSquareFree(f)}')
                            case 10: print(f'\n  Monic: {AlgGeo.MakeMonic(f)}')
                            case _: print('\n  That was not a valid option.'); continue
                elif sec == 3:
                    f = _p1('f'); g = _p1('g')
                    match choice:
                        case 1: print(f'\n  Res(f,g) = {AlgGeo.Resultant(f, g):.6f}')
                        case 2: print(f'\n  Δ(f) = {AlgGeo.Discriminant(f):.6f}')
                        case 3: print(f'\n  √⟨f⟩ = {AlgGeo.RadicalOfPrincipalIdeal(f)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 4:
                    match choice:
                        case 1:
                            f = _p2('f')
                            x0 = _ask('  x₀: ', cast=float); y0 = _ask('  y₀: ', cast=float)
                            fx, fy, c = AlgGeo.TangentLineImplicit(f, x0, y0)
                            print(f'\n  Tangent: {fx:.4f}·x + {fy:.4f}·y = {c:.4f}')
                        case 2:
                            f = _p1(); x0 = _ask('  x₀: ', cast=float)
                            print(f'\n  Multiplicity at {x0}: {AlgGeo.RootMultiplicity(f, x0)}')
                        case 3:
                            f = _p2(); x = _ask('  x: ', cast=float); y = _ask('  y: ', cast=float)
                            print(f'\n  Smooth: {AlgGeo.IsSmoothPoint(f, x, y)}')
                        case 4:
                            f = _p2(); x = _ask('  x: ', cast=float); y = _ask('  y: ', cast=float)
                            print(f'\n  Singular: {AlgGeo.IsSingularPoint(f, x, y)}')
                        case 5:
                            d = _ask('  Degree d: ', cast=int)
                            print(f'\n  Genus = (d-1)(d-2)/2 = {AlgGeo.PlaneCurveGenus(d)}')
                        case 6:
                            d1 = _ask('  d₁: ', cast=int); d2 = _ask('  d₂: ', cast=int)
                            print(f'\n  Bezout number = {AlgGeo.BezoutNumber(d1, d2)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 5:
                    match choice:
                        case 1:
                            vals = [_ask(f'  λ{i+1}: ', cast=float) for i in range(4)]
                            print(f'\n  Cross-ratio = {AlgGeo.CrossRatio(*vals):.6f}')
                        case 2:
                            p1 = tuple(_ask(f'  P1[{c}]: ', cast=float) for c in 'xyz')
                            p2 = tuple(_ask(f'  P2[{c}]: ', cast=float) for c in 'xyz')
                            print(f'\n  Projectively equivalent: {AlgGeo.ProjectiveEquivalent(p1, p2)}')
                        case 3:
                            a = _ask('  a (x²): ', cast=float)
                            b = _ask('  b (xy): ', cast=float)
                            c = _ask('  c (y²): ', cast=float)
                            print(f'\n  Conic type: {AlgGeo.ClassifyConic(a, b, c)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 6:
                    a = _ask('  a: ', cast=float); b = _ask('  b: ', cast=float)
                    match choice:
                        case 1: print(f'\n  Δ = {AlgGeo.EllipticCurveDiscriminant(a, b):.6f}')
                        case 2: print(f'\n  j = {AlgGeo.JInvariant(a, b):.6f}')
                        case 3:
                            x = _ask('  x: ', cast=float); y = _ask('  y: ', cast=float)
                            print(f'\n  On curve: {AlgGeo.IsOnEllipticCurve((x, y), a, b)}')
                        case 4:
                            x = _ask('  x: ', cast=float); y = _ask('  y: ', cast=float)
                            print(f'\n  -P = {AlgGeo.EllipticNeg((x, y))}')
                        case 5:
                            x1=_ask('  P x: ',cast=float); y1=_ask('  P y: ',cast=float)
                            x2=_ask('  Q x: ',cast=float); y2=_ask('  Q y: ',cast=float)
                            print(f'\n  P+Q = {AlgGeo.EllipticAdd((x1,y1),(x2,y2),a,b)}')
                        case 6:
                            n = _ask('  n: ', cast=int)
                            x = _ask('  P x: ', cast=float); y = _ask('  P y: ', cast=float)
                            print(f'\n  [{n}]P = {AlgGeo.EllipticMul(n,(x,y),a,b)}')
                        case 7:
                            x = _ask('  x: ', cast=float); y = _ask('  y: ', cast=float)
                            print(f'\n  ord(P) = {AlgGeo.EllipticPointOrder((x,y),a,b)}')
                        case 8:
                            p = _ask('  Prime p: ', cast=int)
                            pts_e = AlgGeo.EllipticCurvePoints_Fp(int(a), int(b), p)
                            print(f'\n  Points on E(𝔽_{p}): {len(pts_e)}')
                            for pt in pts_e[:12]: print(f'    {pt}')
                            if len(pts_e) > 12: print(f'    ... ({len(pts_e)-12} more)')
                        case 9:
                            p = _ask('  Prime p: ', cast=int)
                            lo, hi = AlgGeo.HasseInterval(p)
                            print(f'\n  #E(𝔽_{p}) ∈ [{lo}, {hi}]')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 7:
                    f = _p2('f')
                    match choice:
                        case 1:
                            sing = AlgGeo.SingularLocus(f)
                            print(f'\n  Singular locus: {sing}')
                        case 2:
                            x=_ask('  x₀: ',cast=float); y=_ask('  y₀: ',cast=float)
                            print(f'\n  Node: {AlgGeo.IsNodeSingularity(f, x, y)}')
                        case 3:
                            x=_ask('  x₀: ',cast=float); y=_ask('  y₀: ',cast=float)
                            print(f'\n  Cusp: {AlgGeo.IsCuspSingularity(f, x, y)}')
                        case 4:
                            stype = _ask('  Type (node/cusp/tacnode/triple_point): ', cast=str).strip()
                            print(f'\n  δ({stype}) = {AlgGeo.DeltaInvariant(stype)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 8:
                    f = _p2('f'); g = _p2('g')
                    match choice:
                        case 1:
                            x=_ask('  x₀: ',cast=float); y=_ask('  y₀: ',cast=float)
                            print(f'\n  Intersection mult ≈ {AlgGeo.IntersectionMultiplicity(f, g, x, y)}')
                        case 2:
                            d = _ask('  Curve degree d: ', cast=int)
                            ds = _ask('  Sum of δ-invariants: ', cast=int)
                            print(f'\n  Geometric genus = {AlgGeo.GeometricGenus(d, ds)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 9:
                    d = _ask('  Variety degree: ', cast=int)
                    match choice:
                        case 1:
                            deg_d = _ask('  d for H(d): ', cast=int)
                            print(f'\n  H({deg_d}) = {AlgGeo.HilbertFunction(d, deg_d)}')
                        case 2:
                            coeffs = AlgGeo.HilbertPolynomial(d)
                            print(f'\n  Hilbert polynomial coefficients: {coeffs}')
                        case 3:
                            n = _ask('  n variables: ', cast=int)
                            k = _ask('  k generators: ', cast=int)
                            print(f'\n  Krull dim = {AlgGeo.KrullDimension(n, k)}')
                        case 4:
                            print(f'\n  deg(V) = {AlgGeo.VarietyDegree(d)}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 10:
                    match choice:
                        case 1:
                            a=_ask('  a (x²): ',cast=float); b=_ask('  b (xy): ',cast=float)
                            c=_ask('  c (y²): ',cast=float); d=_ask('  d (x): ',cast=float)
                            e=_ask('  e (y): ',cast=float); f_c=_ask('  f (const): ',cast=float)
                            poly = AlgGeo.ConicPoly(a,b,c,d,e,f_c)
                            print(f'\n  Conic: {poly}   Type: {AlgGeo.ClassifyConic(a,b,c)}')
                        case 2:
                            a=_ask('  a: ',cast=float); b=_ask('  b: ',cast=float)
                            print(f'\n  y²-x³-{a}x-{b}=0: {AlgGeo.EllipticCurvePoly(a,b)}')
                        case 3:
                            print(f'\n  Nodal cubic y²=x²(x+1): {AlgGeo.NodalCubic()}')
                        case 4:
                            print(f'\n  Cuspidal cubic y²=x³: {AlgGeo.CuspidalCubic()}')
                        case 5:
                            n = _ask('  n: ', cast=int)
                            print(f'\n  Fermat x^{n}+y^{n}=1: {AlgGeo.FermatCurve(n)}')
                        case _: print('\n  That was not a valid option.'); continue
            except _AskAbort:
                print()
                _p('Calculation cancelled. Returning to the function list.')
                print()
                continue
            except Exception as e:
                print(f'\n  Error: {e}')
                print()
                continue
            print()

# ============================================================
# PHYSICS ENERGY DEBUG
# ============================================================

def PhysicsEnergyDebug():
    SECTIONS = [
        'Kinetic Energy', 'Gravitational PE', 'Conservation of Energy',
        'Work & Work-Energy Theorem', 'IsWork? — Word Problem Parser',
        'Power', 'Potential ↔ Force', 'Magnetic Field Energy', 'Energy Breakdown',
    ]
    while True:
        _SectionHeader('Physics — Energy & Work', 'Choose a section')
        for i, s in enumerate(SECTIONS, 1):
            print(f'  ({i})  {s}')
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section.')
            continue
        while True:
            _SectionHeader('Physics — Energy', SECTIONS[sec - 1])
            if sec == 1:
                print('  (1)  KE = ½mv²')
                print('  (2)  Velocity from KE')
                print('  (3)  ΔKE between two states')
                print('  (4)  Rotational KE = ½Iω²')
                print('  (5)  Total KE (translational + rotational)')
            elif sec == 2:
                print('  (1)  GPE = mgh')
                print('  (2)  Height from GPE')
                print('  (3)  ΔGPE over height change')
                print('  (4)  Path independence check (3 paths, same Δh)')
            elif sec == 3:
                print('  (1)  Final velocity  (conservation, no friction)')
                print('  (2)  Final height    (conservation)')
                print('  (3)  Max height      (v_f = 0 at peak)')
                print('  (4)  Final velocity with friction')
                print('  (5)  Slide-bottom velocity (starts at rest)')
                print('  (6)  Full energy state at a height')
                print('  (7)  Energy at % of max height (PE/KE split)')
            elif sec == 4:
                print('  (1)  W = F·d·cos θ')
                print('  (2)  Work-energy theorem  W_net = ΔKE')
                print('  (3)  Force from work-energy theorem')
                print('  (4)  Work by gravity  W = mg(h_i − h_f)')
                print('  (5)  Work by spring   W = ½k(x_i² − x_f²)')
            elif sec == 5:
                print('  (1)  Analyse a single problem sentence')
                print('  (2)  Run the four lecture examples')
            elif sec == 6:
                print('  (1)  Average power   P = W / Δt')
                print('  (2)  Power from force  P = F·v·cos θ')
                print('  (3)  Work from power  W = P·Δt')
                print('  (4)  Watts ↔ horsepower')
                print('  (5)  Power efficiency  η = P_out / P_in')
            elif sec == 7:
                print('  (1)  F = −ΔU / Δx')
                print('  (2)  W = −ΔU')
                print('  (3)  ΔU = −W')
            elif sec == 8:
                print('  (1)  Magnetic field energy  U_B = B²V/(2μ₀)')
                print('  (2)  Magnetic energy density  u_B = B²/(2μ₀)')
                print('  (3)  Inductor energy  U_L = ½LI²')
                print('  (4)  Magnetic braking power')
            elif sec == 9:
                print('  (1)  Full energy breakdown at a point')
                print('  (2)  Cannonball energy profile (launch / apex / land)')
            print()
            _ExitBar('Return to sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            if choice < 0:
                print('\n  That was not a valid option.')
                continue
            try:
                if sec == 1:
                    match choice:
                        case 1:
                            m = _ask('  Mass (kg): ', cast=float); v = _ask('  Velocity (m/s): ', cast=float)
                            print(f'\n  KE = {PEnergy.KineticEnergy(m, v):.4f} J')
                        case 2:
                            ke = _ask('  KE (J): ', cast=float); m = _ask('  Mass (kg): ', cast=float)
                            print(f'\n  v = {PEnergy.VelocityFromKE(ke, m):.4f} m/s')
                        case 3:
                            m = _ask('  Mass (kg): ', cast=float)
                            vi = _ask('  v_initial (m/s): ', cast=float); vf = _ask('  v_final (m/s): ', cast=float)
                            print(f'\n  ΔKE = {PEnergy.DeltaKE(m, vi, vf):.4f} J')
                        case 4:
                            I = _ask('  Moment of inertia I (kg·m²): ', cast=float)
                            w = _ask('  ω (rad/s): ', cast=float)
                            print(f'\n  KE_rot = {PEnergy.RotationalKE(I, w):.4f} J')
                        case 5:
                            m=_ask('  Mass (kg): ',cast=float); v=_ask('  v (m/s): ',cast=float)
                            I=_ask('  I (kg·m²): ',cast=float); r=_ask('  Radius (m): ',cast=float)
                            print(f'\n  KE_total = {PEnergy.TotalKERolling(m, v, I, r):.4f} J')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 2:
                    match choice:
                        case 1:
                            m=_ask('  Mass (kg): ',cast=float); h=_ask('  Height (m): ',cast=float)
                            print(f'\n  GPE = {PEnergy.GravitationalPE(m, h):.4f} J')
                        case 2:
                            gpe=_ask('  GPE (J): ',cast=float); m=_ask('  Mass (kg): ',cast=float)
                            print(f'\n  h = {PEnergy.HeightFromGPE(gpe, m):.4f} m')
                        case 3:
                            m=_ask('  Mass (kg): ',cast=float)
                            hi=_ask('  h_i (m): ',cast=float); hf=_ask('  h_f (m): ',cast=float)
                            print(f'\n  ΔGPE = {PEnergy.DeltaGPE(m, hi, hf):.4f} J')
                        case 4:
                            m=_ask('  Mass (kg): ',cast=float); h=_ask('  Height (m): ',cast=float)
                            same, gpe = PEnergy.PathIndependenceCheck(m, h)
                            print(f'\n  All 3 paths give GPE = {gpe:.4f} J  (path-independent: {same})')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 3:
                    match choice:
                        case 1:
                            vi=_ask('  v_i (m/s): ',cast=float)
                            hi=_ask('  h_i (m): ',cast=float); hf=_ask('  h_f (m): ',cast=float)
                            vf = PEnergy.FinalVelocityConservation(vi, hi, hf)
                            print(f'\n  v_f = {vf:.4f} m/s' if vf is not None else '\n  Cannot reach that height.')
                        case 2:
                            vi=_ask('  v_i: ',cast=float); hi=_ask('  h_i: ',cast=float); vf=_ask('  v_f: ',cast=float)
                            print(f'\n  h_f = {PEnergy.FinalHeightConservation(vi, hi, vf):.4f} m')
                        case 3:
                            vi=_ask('  v_i (m/s): ',cast=float); hi=_ask('  h_i (m): ',cast=float)
                            print(f'\n  h_max = {PEnergy.MaxHeightConservation(vi, hi):.4f} m')
                        case 4:
                            m=_ask('  Mass: ',cast=float); vi=_ask('  v_i: ',cast=float)
                            hi=_ask('  h_i: ',cast=float); hf=_ask('  h_f: ',cast=float)
                            ff=_ask('  Friction force (N): ',cast=float); d=_ask('  Distance (m): ',cast=float)
                            print(f'\n  v_f = {PEnergy.FinalVelocityWithFriction(m,vi,hi,hf,ff,d):.4f} m/s')
                        case 5:
                            m=_ask('  Mass: ',cast=float); h_top=_ask('  Height at top (m): ',cast=float)
                            h_bot=_ask('  Height at bottom (m, usually 0): ',cast=float)
                            print(f'\n  v_f = {PEnergy.SlideBottomVelocity(m, h_top, h_bot):.4f} m/s')
                        case 6:
                            m=_ask('  Mass: ',cast=float); v=_ask('  v: ',cast=float); h=_ask('  h: ',cast=float)
                            for k, val in PEnergy.EnergyStateAtHeight(m, v, h).items():
                                print(f'  {k}: {val:.4f}')
                        case 7:
                            me=_ask('  Total ME (J): ',cast=float); frac=_ask('  Height fraction (0–1): ',cast=float)
                            pe, ke = PEnergy.EnergyAtHeightFraction(me, frac)
                            print(f'\n  PE = {pe:.4f} J   KE = {ke:.4f} J')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 4:
                    match choice:
                        case 1:
                            F=_ask('  Force (N): ',cast=float); d=_ask('  Distance (m): ',cast=float)
                            th=_ask('  Angle θ (deg, 0 if parallel): ',cast=float)
                            print(f'\n  W = {PEnergy.Work(F, d, th):.4f} J')
                        case 2:
                            m=_ask('  Mass: ',cast=float); vi=_ask('  v_i: ',cast=float); vf=_ask('  v_f: ',cast=float)
                            print(f'\n  W_net = {PEnergy.WorkEnergyTheorem(m, vi, vf):.4f} J')
                        case 3:
                            m=_ask('  Mass: ',cast=float); vi=_ask('  v_i: ',cast=float)
                            vf=_ask('  v_f: ',cast=float); d=_ask('  Distance: ',cast=float)
                            print(f'\n  F = {PEnergy.ForceFromWorkEnergyTheorem(m,vi,vf,d):.4f} N')
                        case 4:
                            m=_ask('  Mass: ',cast=float); hi=_ask('  h_i: ',cast=float); hf=_ask('  h_f: ',cast=float)
                            print(f'\n  W_gravity = {PEnergy.WorkByGravity(m, hi, hf):.4f} J')
                        case 5:
                            k=_ask('  k (N/m): ',cast=float); xi=_ask('  x_i (m): ',cast=float); xf=_ask('  x_f (m): ',cast=float)
                            print(f'\n  W_spring = {PEnergy.WorkBySpring(k, xi, xf):.4f} J')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 5:
                    match choice:
                        case 1:
                            problem = _ask('  Describe the problem: ', cast=str)
                            r = PEnergy.IsWork(problem)
                            print(f'\n  Is work: {r["is_work"]}')
                            print(f'  Reason:  {r["reason"]}')
                            print(f'  Formula: {r["W_formula"]}')
                        case 2:
                            examples = [
                                'A student pushes against a wall until exhausted.',
                                'A man lifts bricks into the back of a pickup truck.',
                                'A book falls off a table and free falls to the ground.',
                                'A waiter carries a tray above his head across the room at constant speed.',
                            ]
                            print()
                            for prob in examples:
                                r = PEnergy.IsWork(prob)
                                print(f'  {prob}')
                                print(f'  → Is work: {r["is_work"]}  |  {r["reason"]}')
                                print()
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 6:
                    match choice:
                        case 1:
                            W=_ask('  W (J): ',cast=float); t=_ask('  Δt (s): ',cast=float)
                            print(f'\n  P_avg = {PEnergy.PowerAvg(W, t):.4f} W')
                        case 2:
                            F=_ask('  F (N): ',cast=float); v=_ask('  v (m/s): ',cast=float); th=_ask('  θ (deg): ',cast=float)
                            print(f'\n  P = {PEnergy.PowerFromForce(F, v, th):.4f} W')
                        case 3:
                            P=_ask('  P (W): ',cast=float); t=_ask('  Δt (s): ',cast=float)
                            print(f'\n  W = {PEnergy.WorkFromPower(P, t):.4f} J')
                        case 4:
                            val=_ask('  Value: ',cast=float)
                            unit=_ask('  From (W or hp): ',cast=str).strip().lower()
                            if 'hp' in unit:
                                print(f'\n  {val} hp = {PEnergy.HorsepowerToWatts(val):.4f} W')
                            else:
                                print(f'\n  {val} W = {PEnergy.WattsToHorsepower(val):.6f} hp')
                        case 5:
                            po=_ask('  P_out (W): ',cast=float); pi=_ask('  P_in (W): ',cast=float)
                            eta = PEnergy.PowerEfficiency(po, pi)
                            print(f'\n  η = {eta:.4f}  ({eta*100:.2f}%)')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 7:
                    match choice:
                        case 1:
                            dU=_ask('  ΔU (J): ',cast=float); dx=_ask('  Δx (m): ',cast=float)
                            print(f'\n  F = −ΔU/Δx = {PEnergy.ForceFromPotential(dU, dx):.4f} N')
                        case 2:
                            pi=_ask('  U_i (J): ',cast=float); pf=_ask('  U_f (J): ',cast=float)
                            print(f'\n  W = −ΔU = {PEnergy.WorkFromPotentialChange(pi, pf):.4f} J')
                        case 3:
                            W=_ask('  W (J): ',cast=float)
                            print(f'\n  ΔU = −W = {PEnergy.PotentialChangeFromWork(W):.4f} J')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 8:
                    match choice:
                        case 1:
                            B=_ask('  B (T): ',cast=float); V=_ask('  Volume (m³): ',cast=float)
                            print(f'\n  U_B = {PEnergy.MagneticFieldEnergy(B, V):.4f} J')
                        case 2:
                            B=_ask('  B (T): ',cast=float)
                            print(f'\n  u_B = {PEnergy.MagneticEnergyDensity(B):.4f} J/m³')
                        case 3:
                            L=_ask('  L (H): ',cast=float); I=_ask('  I (A): ',cast=float)
                            print(f'\n  U_L = {PEnergy.InductorEnergy(L, I):.4f} J')
                        case 4:
                            B=_ask('  B (T): ',cast=float); L=_ask('  Length (m): ',cast=float)
                            v=_ask('  v (m/s): ',cast=float); R=_ask('  R (Ω): ',cast=float)
                            print(f'\n  P_brake = {PEnergy.MagneticBrakingPower(B, L, v, R):.4f} W')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 9:
                    match choice:
                        case 1:
                            m=_ask('  Mass: ',cast=float); v=_ask('  v: ',cast=float); h=_ask('  h: ',cast=float)
                            k=_ask('  Spring k (0 if none): ',cast=float); x=_ask('  Spring x (0 if none): ',cast=float)
                            th=_ask('  Thermal energy (J, 0 if none): ',cast=float)
                            print()
                            for key, val in PEnergy.EnergyBreakdown(m, v, h, k, x, th).items():
                                print(f'  {key}: {val:.4f} J')
                        case 2:
                            m=_ask('  Mass: ',cast=float)
                            v0x=_ask('  v₀ₓ (m/s): ',cast=float); v0y=_ask('  v₀ᵧ (m/s): ',cast=float)
                            profile = PEnergy.CannonBallEnergyProfile(m, v0x, v0y)
                            print()
                            for phase, data in profile.items():
                                print(f'  {phase.upper()}:')
                                for k, val in data.items(): print(f'    {k}: {val:.4f}')
                        case _: print('\n  That was not a valid option.'); continue
            except _AskAbort:
                print()
                _p('Calculation cancelled. Returning to the function list.')
                print()
                continue
            except Exception as e:
                print(f'\n  Error: {e}')
                print()
                continue
            print()


# ============================================================
# PHYSICS SPRINGS DEBUG
# ============================================================

def PhysicsSpringsDebug():
    SECTIONS = [
        "Hooke's Law", 'Spring Potential Energy',
        'SHM — Position, Velocity, Acceleration', 'Period & Frequency',
        'SHM Energy', 'Spring Forces', 'Spring-Cut & Momentum',
    ]
    while True:
        _SectionHeader('Physics — Springs & SHM', 'Choose a section')
        for i, s in enumerate(SECTIONS, 1):
            print(f'  ({i})  {s}')
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section.')
            continue
        while True:
            _SectionHeader('Physics — Springs', SECTIONS[sec - 1])
            if sec == 1:
                print('  (1)  F = −kx  (2)  F_applied = kx  (3)  x = F/k  (4)  k = F/x')
                print('  (5)  Series k_eff  (6)  Parallel k_eff  (7)  Natural length after stretch')
            elif sec == 2:
                print('  (1)  PE = ½kx²  (2)  x from PE  (3)  Work by spring  (4)  Work against spring')
            elif sec == 3:
                print('  (1)  x(t)  (2)  v(t)  (3)  a(t)  (4)  v_max  (5)  a_max')
                print('  (6)  v at position x  (7)  a = −ω²x')
            elif sec == 4:
                print('  (1)  ω = √(k/m)  (2)  T = 2π√(m/k)  (3)  f = 1/T')
                print('  (4)  Pendulum T  (5)  k from T  (6)  m from T')
            elif sec == 5:
                print('  (1)  E = ½kA²  (2)  KE at x  (3)  PE at x')
                print('  (4)  Amplitude from E  (5)  x where KE = PE')
            elif sec == 6:
                print('  (1)  Equilibrium stretch x_eq = mg/k')
                print('  (2)  Net spring force at x  (3)  Vertical spring breakdown')
            elif sec == 7:
                print('  (1)  Total momentum before cut')
                print('  (2)  v1 after cut given v2  (3)  Full spring-cut analysis')
                print('  (4)  Release from rest  (5)  Release velocities (given one)')
            print()
            _ExitBar('Return to sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            if choice < 0:
                print('\n  That was not a valid option.')
                continue
            try:
                if sec == 1:
                    k = _ask('  Spring constant k (N/m): ', cast=float)
                    match choice:
                        case 1:
                            x = _ask('  Displacement x (m): ', cast=float)
                            print(f'\n  F_spring = {PSprings.SpringForce(k, x):.4f} N')
                        case 2:
                            x = _ask('  Displacement x (m): ', cast=float)
                            print(f'\n  F_applied = {PSprings.AppliedForceToHold(k, x):.4f} N')
                        case 3:
                            F = _ask('  Force (N): ', cast=float)
                            print(f'\n  x = {PSprings.SpringDisplacement(F, k):.4f} m')
                        case 4:
                            F=_ask('  F (N): ',cast=float); x=_ask('  x (m): ',cast=float)
                            print(f'\n  k = {PSprings.SpringConstant(F, x):.4f} N/m')
                        case 5:
                            ks = [float(v) for v in _ask('  k values (space-sep): ', cast=str).split()]
                            print(f'\n  k_series = {PSprings.SpringConstantSeries(*ks):.4f} N/m')
                        case 6:
                            ks = [float(v) for v in _ask('  k values (space-sep): ', cast=str).split()]
                            print(f'\n  k_parallel = {PSprings.SpringConstantParallel(*ks):.4f} N/m')
                        case 7:
                            L0=_ask('  Natural length L₀ (m): ',cast=float); x=_ask('  Displacement (m): ',cast=float)
                            print(f'\n  New length = {PSprings.SpringLength(L0, x):.4f} m')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 2:
                    k = _ask('  k (N/m): ', cast=float)
                    match choice:
                        case 1:
                            x = _ask('  x (m): ', cast=float)
                            print(f'\n  PE = {PSprings.SpringPE(k, x):.4f} J')
                        case 2:
                            pe = _ask('  PE (J): ', cast=float)
                            print(f'\n  x = {PSprings.DisplacementFromPE(pe, k):.4f} m')
                        case 3:
                            xi=_ask('  x_i (m): ',cast=float); xf=_ask('  x_f (m): ',cast=float)
                            print(f'\n  W_by_spring = {PSprings.WorkDoneBySpring(k, xi, xf):.4f} J')
                        case 4:
                            xi=_ask('  x_i (m): ',cast=float); xf=_ask('  x_f (m): ',cast=float)
                            print(f'\n  W_against = {PSprings.WorkDoneAgainstSpring(k, xi, xf):.4f} J')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 3:
                    A=_ask('  Amplitude A (m): ',cast=float); w=_ask('  ω (rad/s): ',cast=float)
                    t=_ask('  Time t (s): ',cast=float); phi=_ask('  Phase φ (rad, 0 if none): ',cast=float)
                    match choice:
                        case 1: print(f'\n  x(t) = {PSprings.SHM_Position(A, w, t, phi):.6f} m')
                        case 2: print(f'\n  v(t) = {PSprings.SHM_Velocity(A, w, t, phi):.6f} m/s')
                        case 3: print(f'\n  a(t) = {PSprings.SHM_Acceleration(A, w, t, phi):.6f} m/s²')
                        case 4: print(f'\n  v_max = {PSprings.SHM_MaxVelocity(A, w):.6f} m/s')
                        case 5: print(f'\n  a_max = {PSprings.SHM_MaxAcceleration(A, w):.6f} m/s²')
                        case 6:
                            x = _ask('  Position x (m): ', cast=float)
                            print(f'\n  v = {PSprings.SHM_VelocityAtPosition(A, w, x):.6f} m/s')
                        case 7:
                            x = _ask('  Position x (m): ', cast=float)
                            print(f'\n  a = {PSprings.SHM_AccelFromPosition(w, x):.6f} m/s²')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 4:
                    match choice:
                        case 1:
                            k=_ask('  k: ',cast=float); m=_ask('  m: ',cast=float)
                            print(f'\n  ω = {PSprings.AngularFrequency(k, m):.6f} rad/s')
                        case 2:
                            m=_ask('  m: ',cast=float); k=_ask('  k: ',cast=float)
                            print(f'\n  T = {PSprings.Period(m, k):.6f} s')
                        case 3:
                            m=_ask('  m: ',cast=float); k=_ask('  k: ',cast=float)
                            print(f'\n  f = {PSprings.Frequency(m, k):.6f} Hz')
                        case 4:
                            L=_ask('  Pendulum length (m): ',cast=float)
                            print(f'\n  T = {PSprings.PendulumPeriod(L):.6f} s')
                        case 5:
                            m=_ask('  m: ',cast=float); T=_ask('  T (s): ',cast=float)
                            print(f'\n  k = {PSprings.SpringConstantFromPeriod(m, T):.4f} N/m')
                        case 6:
                            k=_ask('  k: ',cast=float); T=_ask('  T (s): ',cast=float)
                            print(f'\n  m = {PSprings.MassFromPeriod(k, T):.4f} kg')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 5:
                    k=_ask('  k (N/m): ',cast=float); A=_ask('  Amplitude A (m): ',cast=float)
                    match choice:
                        case 1: print(f'\n  E = {PSprings.SHM_TotalEnergy(k, A):.4f} J')
                        case 2:
                            x=_ask('  x (m): ',cast=float)
                            print(f'\n  KE = {PSprings.SHM_KE_AtPosition(k, A, x):.4f} J')
                        case 3:
                            x=_ask('  x (m): ',cast=float)
                            print(f'\n  PE = {PSprings.SHM_PE_AtPosition(k, x):.4f} J')
                        case 4:
                            E=_ask('  E (J): ',cast=float)
                            print(f'\n  A = {PSprings.AmplitudeFromEnergy(E, k):.4f} m')
                        case 5:
                            print(f'\n  x = ±{PSprings.EquipartitionPosition(A):.4f} m')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 6:
                    k=_ask('  k (N/m): ',cast=float)
                    match choice:
                        case 1:
                            m=_ask('  m (kg): ',cast=float)
                            print(f'\n  x_eq = {PSprings.EquilibriumStretch(m, k):.4f} m')
                        case 2:
                            x=_ask('  x from equilibrium (m): ',cast=float)
                            print(f'\n  F_net = {PSprings.SpringNetForce(k, x):.4f} N')
                        case 3:
                            x=_ask('  Stretch from natural (m): ',cast=float); m=_ask('  m (kg): ',cast=float)
                            for key, val in PSprings.VerticalSpringForces(k, x, m).items():
                                print(f'  {key}: {val:.4f} N')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 7:
                    match choice:
                        case 1:
                            m1=_ask('  m1 (kg): ',cast=float); m2=_ask('  m2 (kg): ',cast=float)
                            v=_ask('  System velocity (m/s): ',cast=float)
                            print(f'\n  p_total = {PSprings.TotalMomentumBefore(m1, m2, v):.4f} kg·m/s')
                        case 2:
                            p=_ask('  p_total: ',cast=float)
                            m1=_ask('  m1: ',cast=float); m2=_ask('  m2: ',cast=float)
                            v2=_ask('  v2_after: ',cast=float)
                            print(f'\n  v1_after = {PSprings.VelocityAfterCut(p, m1, m2, v2):.4f} m/s')
                        case 3:
                            m1=_ask('  m1: ',cast=float); m2=_ask('  m2: ',cast=float)
                            v_sys=_ask('  System v before cut: ',cast=float)
                            v2_after=_ask('  v2 after cut: ',cast=float)
                            for key, val in PSprings.SpringCutFullAnalysis(m1, m2, v_sys, v2_after).items():
                                print(f'  {key}: {val}')
                        case 4:
                            m1=_ask('  m1: ',cast=float); m2=_ask('  m2: ',cast=float)
                            k=_ask('  k (N/m): ',cast=float); comp=_ask('  Compression x (m): ',cast=float)
                            for key, val in PSprings.SpringReleaseWithMomentum(m1, m2, k, comp).items():
                                print(f'  {key}: {val:.4f}')
                        case 5:
                            m1=_ask('  m1: ',cast=float); m2=_ask('  m2: ',cast=float)
                            v1_in=_ask('  v1 (0 if unknown): ',cast=float)
                            v2_in=_ask('  v2 (0 if unknown): ',cast=float)
                            v1, v2 = PSprings.SpringReleaseVelocities(
                                m1, m2,
                                v1=v1_in if v1_in != 0 else None,
                                v2=v2_in if v2_in != 0 else None)
                            print(f'\n  v1 = {v1:.4f} m/s   v2 = {v2:.4f} m/s')
                        case _: print('\n  That was not a valid option.'); continue
            except _AskAbort:
                print()
                _p('Calculation cancelled. Returning to the function list.')
                print()
                continue
            except Exception as e:
                print(f'\n  Error: {e}')
                print()
                continue
            print()


# ============================================================
# PHYSICS MOMENTUM DEBUG
# ============================================================

def PhysicsMomentumDebug():
    SECTIONS = [
        'Momentum', 'Impulse', 'Conservation of Momentum',
        'Center of Mass', "Newton's Laws — Momentum Form",
        'Spring-Cut Analysis', 'Angular Momentum', 'Rocket Propulsion',
    ]
    while True:
        _SectionHeader('Physics — Momentum & Impulse', 'Choose a section')
        for i, s in enumerate(SECTIONS, 1):
            print(f'  ({i})  {s}')
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section.')
            continue
        while True:
            _SectionHeader('Physics — Momentum', SECTIONS[sec - 1])
            if sec == 1:
                print('  (1)  p = mv  (2)  v from p  (3)  Δp  (4)  Total system momentum')
            elif sec == 2:
                print('  (1)  J = FΔt  (2)  J = Δp  (3)  F_avg from J')
                print('  (4)  Impact time from J and F  (5)  F_avg = mΔv/Δt')
            elif sec == 3:
                print('  (1)  Is momentum conserved?  (2)  Find v2f  (3)  Perfectly inelastic v_f')
            elif sec == 4:
                print('  (1)  CM 1D  (2)  CM 2D  (3)  v_cm  (4)  a_cm  (5)  Reduced mass μ')
            elif sec == 5:
                print('  (1)  F = Δp/Δt  (2)  Δp = F·Δt  (3)  Newton 3rd collision forces')
            elif sec == 6:
                print('  (1)  Before-cut state  (2)  After-cut state')
                print('  (3)  Full spring-cut problem  (4)  Cut from rest')
            elif sec == 7:
                print('  (1)  L = mvr sin θ  (2)  L = Iω  (3)  ω₂ = I₁ω₁/I₂  (4)  τ = ΔL/Δt')
            elif sec == 8:
                print('  (1)  Thrust F = v_ex · dm/dt')
                print('  (2)  Rocket Δv  (Tsiolkovsky)  (3)  Propellant mass')
            print()
            _ExitBar('Return to sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            if choice < 0:
                print('\n  That was not a valid option.')
                continue
            try:
                if sec == 1:
                    match choice:
                        case 1:
                            m=_ask('  Mass (kg): ',cast=float); v=_ask('  v (m/s): ',cast=float)
                            print(f'\n  p = {PMomentum.Momentum(m, v):.4f} kg·m/s')
                        case 2:
                            p=_ask('  p (kg·m/s): ',cast=float); m=_ask('  Mass (kg): ',cast=float)
                            print(f'\n  v = {PMomentum.VelocityFromMomentum(p, m):.4f} m/s')
                        case 3:
                            m=_ask('  Mass: ',cast=float); vi=_ask('  v_i: ',cast=float); vf=_ask('  v_f: ',cast=float)
                            print(f'\n  Δp = {PMomentum.DeltaMomentum(m, vi, vf):.4f} kg·m/s')
                        case 4:
                            n=_ask('  Objects: ',cast=int)
                            ms=[_ask(f'  m{i+1}: ',cast=float) for i in range(n)]
                            vs=[_ask(f'  v{i+1}: ',cast=float) for i in range(n)]
                            print(f'\n  p_total = {PMomentum.TotalMomentum(ms, vs):.4f} kg·m/s')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 2:
                    match choice:
                        case 1:
                            F=_ask('  F (N): ',cast=float); dt=_ask('  Δt (s): ',cast=float)
                            print(f'\n  J = {PMomentum.Impulse(F, dt):.4f} N·s')
                        case 2:
                            m=_ask('  m: ',cast=float); vi=_ask('  v_i: ',cast=float); vf=_ask('  v_f: ',cast=float)
                            print(f'\n  J = Δp = {PMomentum.ImpulseFromMomentumChange(m, vi, vf):.4f} N·s')
                        case 3:
                            J=_ask('  J (N·s): ',cast=float); dt=_ask('  Δt (s): ',cast=float)
                            print(f'\n  F_avg = {PMomentum.AverageForceFromImpulse(J, dt):.4f} N')
                        case 4:
                            J=_ask('  J (N·s): ',cast=float); F=_ask('  F (N): ',cast=float)
                            print(f'\n  Δt = {PMomentum.ImpactTime(J, F):.4f} s')
                        case 5:
                            m=_ask('  m: ',cast=float); vi=_ask('  v_i: ',cast=float)
                            vf=_ask('  v_f: ',cast=float); dt=_ask('  Δt: ',cast=float)
                            print(f'\n  F_avg = {PMomentum.AverageForce(m, vi, vf, dt):.4f} N')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 3:
                    match choice:
                        case 1:
                            n=_ask('  Objects: ',cast=int)
                            ms=[_ask(f'  m{i+1}: ',cast=float) for i in range(n)]
                            vi=[_ask(f'  v{i+1}_before: ',cast=float) for i in range(n)]
                            vf=[_ask(f'  v{i+1}_after: ',cast=float) for i in range(n)]
                            pi=PMomentum.SystemMomenta(ms, vi); pf=PMomentum.SystemMomenta(ms, vf)
                            print(f'\n  p_before={sum(pi):.4f}  p_after={sum(pf):.4f}  Conserved: {PMomentum.IsConserved(pi, pf)}')
                        case 2:
                            m1=_ask('  m1: ',cast=float); v1i=_ask('  v1i: ',cast=float)
                            m2=_ask('  m2: ',cast=float); v2i=_ask('  v2i: ',cast=float); v1f=_ask('  v1f: ',cast=float)
                            print(f'\n  v2f = {PMomentum.FindFinalVelocity_2Body(m1, v1i, m2, v2i, v1f):.4f} m/s')
                        case 3:
                            m1=_ask('  m1: ',cast=float); v1i=_ask('  v1i: ',cast=float)
                            m2=_ask('  m2: ',cast=float); v2i=_ask('  v2i (0 if at rest): ',cast=float)
                            print(f'\n  v_f = {PMomentum.InelasticFinalVelocity(m1, v1i, m2, v2i):.4f} m/s')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 4:
                    match choice:
                        case 1:
                            n=_ask('  Objects: ',cast=int)
                            ms=[_ask(f'  m{i+1}: ',cast=float) for i in range(n)]
                            xs=[_ask(f'  x{i+1}: ',cast=float) for i in range(n)]
                            print(f'\n  x_cm = {PMomentum.CenterOfMass1D(ms, xs):.4f} m')
                        case 2:
                            n=_ask('  Objects: ',cast=int)
                            ms=[_ask(f'  m{i+1}: ',cast=float) for i in range(n)]
                            xs=[_ask(f'  x{i+1}: ',cast=float) for i in range(n)]
                            ys=[_ask(f'  y{i+1}: ',cast=float) for i in range(n)]
                            xcm, ycm = PMomentum.CenterOfMass2D(ms, xs, ys)
                            print(f'\n  CM = ({xcm:.4f}, {ycm:.4f}) m')
                        case 3:
                            n=_ask('  Objects: ',cast=int)
                            ms=[_ask(f'  m{i+1}: ',cast=float) for i in range(n)]
                            vs=[_ask(f'  v{i+1}: ',cast=float) for i in range(n)]
                            print(f'\n  v_cm = {PMomentum.CenterOfMassVelocity(ms, vs):.4f} m/s')
                        case 4:
                            F=_ask('  F_ext (N): ',cast=float); M=_ask('  Total mass (kg): ',cast=float)
                            print(f'\n  a_cm = {PMomentum.CenterOfMassAcceleration(F, M):.4f} m/s²')
                        case 5:
                            m1=_ask('  m1: ',cast=float); m2=_ask('  m2: ',cast=float)
                            print(f'\n  μ = {PMomentum.ReducedMass(m1, m2):.4f} kg')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 5:
                    match choice:
                        case 1:
                            dp=_ask('  Δp (kg·m/s): ',cast=float); dt=_ask('  Δt (s): ',cast=float)
                            print(f'\n  F = {PMomentum.NewtonSecondLaw_Momentum(dp, dt):.4f} N')
                        case 2:
                            F=_ask('  F (N): ',cast=float); dt=_ask('  Δt (s): ',cast=float)
                            print(f'\n  Δp = {PMomentum.MomentumChangeFromForce(F, dt):.4f} kg·m/s')
                        case 3:
                            J1=_ask('  Impulse on obj1 (N·s): ',cast=float)
                            j1, j2 = PMomentum.NewtonThirdCollisionForces(J1)
                            print(f'\n  J on obj1 = {j1:.4f} N·s   J on obj2 = {j2:.4f} N·s')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 6:
                    m1=_ask('  m1 (kg): ',cast=float); m2=_ask('  m2 (kg): ',cast=float)
                    match choice:
                        case 1:
                            v=_ask('  System v (m/s): ',cast=float)
                            for key, val in PMomentum.BeforeCutState(m1, m2, v).items():
                                print(f'  {key}: {val:.4f}')
                        case 2:
                            p=_ask('  p_total: ',cast=float); v2=_ask('  v2_after: ',cast=float)
                            for key, val in PMomentum.AfterCutState(m1, m2, p, v2).items():
                                print(f'  {key}: {val}')
                        case 3:
                            v_sys=_ask('  System v before cut: ',cast=float)
                            v2_after=_ask('  v2 after cut: ',cast=float)
                            r = PMomentum.SpringCutProblem(m1, m2, v_sys, v2_after)
                            print('\n  BEFORE:')
                            for k, v in r['before'].items(): print(f'    {k}: {v:.4f}')
                            print('  AFTER:')
                            for k, v in r['after'].items(): print(f'    {k}: {v}')
                            print(f'  Spring KE released: {r["spring_KE_released"]:.4f} J')
                        case 4:
                            v2=_ask('  v2 after cut (m/s): ',cast=float)
                            for key, val in PMomentum.SpringCutFromRest(m1, m2, v2).items():
                                print(f'  {key}: {val:.4f}')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 7:
                    match choice:
                        case 1:
                            m=_ask('  m: ',cast=float); v=_ask('  v: ',cast=float)
                            r=_ask('  r (m): ',cast=float); th=_ask('  θ (deg, 90 if circular): ',cast=float)
                            print(f'\n  L = {PMomentum.AngularMomentum(m, v, r, th):.4f} kg·m²/s')
                        case 2:
                            I=_ask('  I (kg·m²): ',cast=float); w=_ask('  ω (rad/s): ',cast=float)
                            print(f'\n  L = {PMomentum.AngularMomentumFromI(I, w):.4f} kg·m²/s')
                        case 3:
                            I1=_ask('  I1: ',cast=float); w1=_ask('  ω1: ',cast=float); I2=_ask('  I2: ',cast=float)
                            print(f'\n  ω2 = {PMomentum.FinalAngularVelocity(I1, w1, I2):.4f} rad/s')
                        case 4:
                            dL=_ask('  ΔL (kg·m²/s): ',cast=float); dt=_ask('  Δt (s): ',cast=float)
                            print(f'\n  τ = {PMomentum.TorqueFromAngularMomentum(dL, dt):.4f} N·m')
                        case _: print('\n  That was not a valid option.'); continue
                elif sec == 8:
                    match choice:
                        case 1:
                            vex=_ask('  Exhaust speed (m/s): ',cast=float)
                            dmdt=_ask('  Mass flow rate (kg/s): ',cast=float)
                            print(f'\n  Thrust = {PMomentum.RocketThrust(vex, dmdt):.4f} N')
                        case 2:
                            vex=_ask('  v_exhaust (m/s): ',cast=float)
                            mi=_ask('  m_initial (kg): ',cast=float); mf=_ask('  m_final (kg): ',cast=float)
                            print(f'\n  Δv = {PMomentum.RocketDeltaV(vex, mi, mf):.4f} m/s')
                        case 3:
                            dv=_ask('  Δv (m/s): ',cast=float); vex=_ask('  v_exhaust (m/s): ',cast=float)
                            mp=_ask('  Payload mass (kg): ',cast=float)
                            print(f'\n  Propellant = {PMomentum.RocketPropellantMass(dv, vex, mp):.4f} kg')
                        case _: print('\n  That was not a valid option.'); continue
            except _AskAbort:
                print()
                _p('Calculation cancelled. Returning to the function list.')
                print()
                continue
            except Exception as e:
                print(f'\n  Error: {e}')
                print()
                continue
            print()

# ============================================================
# CENTER OF MASS DEBUG
# ============================================================

def CenterOfMassDebug():
    SECTIONS = [
        'Discrete CoM — 1D',
        'Discrete CoM — 2D',
        'Discrete CoM — 3D',
        'Continuous Bodies',
        'Composite Bodies',
        'CoM in Motion (explosion, velocity, trajectory)',
        'Center of Mass Frame',
        'Moment of Inertia & Parallel Axis',
        'Word Problem Solver',
    ]
    # ── Word problem mode entry point ──────────────────────────────────────────
    def _maybe_word_problem_1d():
        """If word mode is on, offer to parse a problem sentence before manual entry."""
        if not _WORD_MODE:
            return None
        print()
        print('  Word-problem mode is ON.')
        print('  Paste a 1D CoM problem sentence and I\'ll extract the values,')
        print('  or press Enter to enter values manually.')
        print()
        raw = input('  Problem: ').strip()
        if not raw:
            return None
        r = PCoM.ParseCoMProblem1D(raw)
        if r is None:
            print('  ✗  Could not parse that sentence. Switching to manual entry.')
            return None
        print(f'\n  ✓  Parsed {len(r["masses"])} particle(s):')
        for i, (m, x) in enumerate(zip(r['masses'], r['positions']), 1):
            print(f'    Particle {i}: m={m} kg  at  x={x} m')
        _show_steps(PCoM.StepByStepCoM1D(r['masses'], r['positions']))
        print(f'\n  x_cm = {r["x_cm"]:.6f} m')
        print()
        return r

    def _maybe_word_problem_2d():
        if not _WORD_MODE:
            return None
        print()
        print('  Word-problem mode is ON.')
        print('  Paste a 2D CoM problem (e.g. "3 kg at (1,2) and 5 kg at (4,6)"),')
        print('  or press Enter to enter values manually.')
        print()
        raw = input('  Problem: ').strip()
        if not raw:
            return None
        r = PCoM.ParseCoMProblem2D(raw)
        if r is None:
            print('  ✗  Could not parse. Switching to manual entry.')
            return None
        print(f'\n  ✓  Parsed {len(r["masses"])} particle(s):')
        for i, (m, p) in enumerate(zip(r['masses'], r['points']), 1):
            print(f'    Particle {i}: m={m} kg  at  ({p[0]}, {p[1]}) m')
        _show_steps(PCoM.StepByStepCoM2D(r['masses'], r['points']))
        print(f'\n  CoM = ({r["x_cm"]:.6f}, {r["y_cm"]:.6f}) m')
        print()
        return r

    def _collect_particles_1d():
        """Gather n masses and positions from the user."""
        n = _ask('  Number of particles: ', cast=int)
        masses = []; positions = []
        for i in range(n):
            print(f'\n  Particle {i+1}:')
            m = _ask(f'    Mass m{i+1} (kg): ', cast=float)
            x = _ask(f'    Position x{i+1} (m): ', cast=float)
            masses.append(m); positions.append(x)
        return masses, positions

    def _collect_particles_2d():
        n = _ask('  Number of particles: ', cast=int)
        masses = []; points = []
        for i in range(n):
            print(f'\n  Particle {i+1}:')
            m = _ask(f'    Mass m{i+1} (kg): ', cast=float)
            x = _ask(f'    x{i+1} (m): ', cast=float)
            y = _ask(f'    y{i+1} (m): ', cast=float)
            masses.append(m); points.append((x, y))
        return masses, points

    def _collect_particles_3d():
        n = _ask('  Number of particles: ', cast=int)
        masses = []; points = []
        for i in range(n):
            print(f'\n  Particle {i+1}:')
            m = _ask(f'    Mass m{i+1} (kg): ', cast=float)
            x = _ask(f'    x{i+1} (m): ', cast=float)
            y = _ask(f'    y{i+1} (m): ', cast=float)
            z = _ask(f'    z{i+1} (m): ', cast=float)
            masses.append(m); points.append((x, y, z))
        return masses, points

    while True:
        _SectionHeader('Physics — Center of Mass', 'Choose a section')
        for i, s in enumerate(SECTIONS, 1):
            print(f'  ({i})  {s}')
        print()
        if _STEP_MODE: print('  [Step-by-step: ON]')
        if _WORD_MODE: print('  [Word-problem mode: ON]')
        print()
        _ExitBar('Return to main menu')
        print()
        sec = _menu_int('  Select a section: ')
        if sec == 0: return
        if sec < 1 or sec > len(SECTIONS):
            print('\n  That was not a valid section.')
            continue

        while True:
            _SectionHeader('Center of Mass', SECTIONS[sec - 1])
            if sec == 1:
                print('  (1)  x_cm = Σmᵢxᵢ / M')
                print('  (2)  Find missing particle position given desired x_cm')
                print('  (3)  CoM measured from a custom reference point')
                print('  (4)  Two-body CoM  (fast form)')
                print('  (5)  Distances of each particle from CoM')
                print('  (6)  Balance / fulcrum point')
            elif sec == 2:
                print('  (1)  (x_cm, y_cm) from n particles')
                print('  (2)  CoM of a triangle  (3 vertices)')
                print('  (3)  CoM of a polygon  (n vertices)')
                print('  (4)  Distances from CoM  (2D)')
                print('  (5)  CoM relative to a reference point  (2D)')
            elif sec == 3:
                print('  (1)  (x_cm, y_cm, z_cm) from n particles')
                print('  (2)  CoM of a tetrahedron  (4 vertices)')
                print('  (3)  Distances from CoM  (3D)')
            elif sec == 4:
                print('  (1)  Uniform rod')
                print('  (2)  Rod with variable linear density λ(x)')
                print('  (3)  Uniform rectangle')
                print('  (4)  Right triangle')
                print('  (5)  Solid semicircle  (y_cm = 4r/3π)')
                print('  (6)  Semicircular arc / wire  (y_cm = 2r/π)')
                print('  (7)  Solid hemisphere  (3r/8)')
                print('  (8)  Hollow hemisphere  (r/2)')
                print('  (9)  Solid cone  (h/4 from base)')
                print('  (10) Quarter-circle')
                print('  (11) Hollow conical shell  (h/3)')
                print('  (12) Solid cylinder')
            elif sec == 5:
                print('  (1)  Composite body  1D  (sum of shapes with their CoM positions)')
                print('  (2)  Composite body  2D')
                print('  (3)  Composite body  3D')
                print('  (4)  Rectangle with circular hole removed')
                print('  (5)  Two sub-bodies  (dumbbell)')
            elif sec == 6:
                print('  (1)  CoM velocity  v_cm = Σmᵢvᵢ / M  (1D)')
                print('  (2)  CoM velocity  (2D)')
                print('  (3)  CoM acceleration  a_cm = F_ext / M')
                print('  (4)  After explosion — find v2  (momentum conserved)')
                print('  (5)  Displacement to keep CoM fixed  (only internal forces)')
                print('  (6)  Verify momentum conservation after explosion')
            elif sec == 7:
                print('  (1)  CoM-frame velocities  (1D)')
                print('  (2)  CoM-frame velocities  (2D)')
                print('  (3)  KE in CoM frame  vs  KE in lab frame')
                print('  (4)  Relative velocity  v_rel = v1 − v2')
                print('  (5)  Reduced mass  μ = m1m2/(m1+m2)')
                print('  (6)  KE of relative motion  ½μ v_rel²')
            elif sec == 8:
                print('  (1)  I = Σmᵢrᵢ²  (point masses)')
                print('  (2)  Parallel axis theorem  I = I_cm + md²')
                print('  (3)  Perpendicular axis theorem  I_z = I_x + I_y')
                print('  (4)  I_cm lookup — common shapes')
                print('  (5)  Composite moment of inertia')
            elif sec == 9:
                print('  Word-problem parser — type or paste a problem in plain English.')
                print()
                print('  (1)  1D CoM word problem')
                print('  (2)  2D CoM word problem')
                print('  (3)  Explosion / split word problem')
            print()
            _ExitBar('Return to sections')
            print()
            choice = _menu_int('  Select a function: ')
            if choice == 0: break
            if choice < 0:
                print('\n  That was not a valid option.')
                continue
            try:
                # ── SECTION 1: Discrete 1D ──────────────────────────────────────
                if sec == 1:
                    match choice:
                        case 1:
                            parsed = _maybe_word_problem_1d()
                            if parsed is None:
                                masses, positions = _collect_particles_1d()
                            else:
                                masses, positions = parsed['masses'], parsed['positions']
                                print()
                                continue
                            _show_steps(PCoM.StepByStepCoM1D(masses, positions))
                            x_cm = PCoM.CoM1D(masses, positions)
                            _step('Center of Mass', 'x_cm = Σmᵢxᵢ / M',
                                  f'{PCoM.MassWeightedSum1D(masses,positions)} / {sum(masses)}',
                                  x_cm, 'm')
                            print(f'\n  x_cm = {x_cm:.6f} m')
                        case 2:
                            print()
                            _p('Given some particles and a total mass, this finds where the'
                               ' unknown particle must be to achieve a target CoM.')
                            masses_k = []; positions_k = []
                            n = _ask('  Known particles: ', cast=int)
                            for i in range(n):
                                masses_k.append(_ask(f'  m{i+1} (kg): ', cast=float))
                                positions_k.append(_ask(f'  x{i+1} (m): ', cast=float))
                            M_total = _ask('  Total system mass M (kg): ', cast=float)
                            x_cm_target = _ask('  Target CoM x_cm (m): ', cast=float)
                            x_unknown = PCoM.MissingMassPosition1D(masses_k, positions_k, M_total, x_cm_target)
                            m_unknown = M_total - sum(masses_k)
                            _step('Missing position', 'x = (M·x_cm − Σmᵢxᵢ) / m_unknown',
                                  f'({M_total}·{x_cm_target} − {PCoM.MassWeightedSum1D(masses_k,positions_k)}) / {m_unknown}',
                                  x_unknown, 'm')
                            print(f'\n  Unknown mass: {m_unknown:.4f} kg')
                            print(f'  Must be at:   {x_unknown:.6f} m')
                        case 3:
                            masses, positions = _collect_particles_1d()
                            ref = _ask('  Reference point x_ref (m): ', cast=float)
                            x_cm_rel = PCoM.CoMFromReference1D(masses, positions, ref)
                            print(f'\n  CoM relative to x={ref}: {x_cm_rel:.6f} m')
                        case 4:
                            m1=_ask('  m1 (kg): ',cast=float); x1=_ask('  x1 (m): ',cast=float)
                            m2=_ask('  m2 (kg): ',cast=float); x2=_ask('  x2 (m): ',cast=float)
                            x_cm = PCoM.SplitCoM1D(m1,x1,m2,x2)
                            _step('Two-body CoM','x_cm = (m1·x1+m2·x2)/(m1+m2)',
                                  f'({m1}·{x1}+{m2}·{x2})/({m1}+{m2})', x_cm, 'm')
                            print(f'\n  x_cm = {x_cm:.6f} m')
                        case 5:
                            masses, positions = _collect_particles_1d()
                            x_cm, dists = PCoM.CoMDistance1D(masses, positions)
                            print(f'\n  x_cm = {x_cm:.6f} m')
                            print('  Distances from CoM:')
                            for i, (m, d) in enumerate(zip(masses, dists), 1):
                                print(f'    Particle {i}  ({m} kg):  Δx = {d:+.6f} m')
                        case 6:
                            masses, positions = _collect_particles_1d()
                            bp = PCoM.BalancePoint1D(masses, positions)
                            print(f'\n  Fulcrum / balance point: x = {bp:.6f} m')
                        case _: print('\n  That was not a valid option.'); continue

                # ── SECTION 2: Discrete 2D ──────────────────────────────────────
                elif sec == 2:
                    match choice:
                        case 1:
                            parsed = _maybe_word_problem_2d()
                            if parsed is None:
                                masses, points = _collect_particles_2d()
                            else:
                                masses, points = parsed['masses'], parsed['points']
                                print(); continue
                            _show_steps(PCoM.StepByStepCoM2D(masses, points))
                            x_cm, y_cm = PCoM.CoM2D(masses, points)
                            _step('CoM 2D','(x_cm,y_cm)=Σmᵢ(xᵢ,yᵢ)/M','',
                                  f'({x_cm:.4f}, {y_cm:.4f})','m')
                            print(f'\n  CoM = ({x_cm:.6f}, {y_cm:.6f}) m')
                        case 2:
                            print('  Vertex 1:'); x1=_ask('    x: ',cast=float); y1=_ask('    y: ',cast=float)
                            print('  Vertex 2:'); x2=_ask('    x: ',cast=float); y2=_ask('    y: ',cast=float)
                            print('  Vertex 3:'); x3=_ask('    x: ',cast=float); y3=_ask('    y: ',cast=float)
                            x_cm,y_cm = PCoM.CoMOfTriangle2D((x1,y1),(x2,y2),(x3,y3))
                            _step('Triangle centroid','= (x1+x2+x3)/3, (y1+y2+y3)/3','',
                                  f'({x_cm:.4f}, {y_cm:.4f})','m')
                            print(f'\n  CoM = ({x_cm:.6f}, {y_cm:.6f}) m')
                        case 3:
                            n = _ask('  Number of vertices: ', cast=int)
                            verts = []
                            for i in range(n):
                                x=_ask(f'  x{i+1}: ',cast=float); y=_ask(f'  y{i+1}: ',cast=float)
                                verts.append((x,y))
                            x_cm,y_cm = PCoM.CoMOfPolygon2D(verts)
                            print(f'\n  Polygon CoM = ({x_cm:.6f}, {y_cm:.6f}) m')
                        case 4:
                            masses, points = _collect_particles_2d()
                            x_cm,y_cm,dists = PCoM.DistanceFromCoM2D(masses, points)
                            print(f'\n  CoM = ({x_cm:.6f}, {y_cm:.6f}) m')
                            print('  Distances from CoM:')
                            for i,(m,d) in enumerate(zip(masses,dists),1):
                                print(f'    Particle {i}  ({m} kg):  r = {d:.6f} m')
                        case 5:
                            masses, points = _collect_particles_2d()
                            rx=_ask('  Reference x: ',cast=float); ry=_ask('  Reference y: ',cast=float)
                            x_cm,y_cm = PCoM.CoMFromReference2D(masses, points, (rx,ry))
                            print(f'\n  CoM from ({rx},{ry}) = ({x_cm:.6f}, {y_cm:.6f}) m')
                        case _: print('\n  That was not a valid option.'); continue

                # ── SECTION 3: Discrete 3D ──────────────────────────────────────
                elif sec == 3:
                    match choice:
                        case 1:
                            masses, points = _collect_particles_3d()
                            x_cm,y_cm,z_cm = PCoM.CoM3D(masses, points)
                            print(f'\n  CoM = ({x_cm:.6f}, {y_cm:.6f}, {z_cm:.6f}) m')
                        case 2:
                            print('  Vertex 1:'); v1=(_ask('    x: ',cast=float),_ask('    y: ',cast=float),_ask('    z: ',cast=float))
                            print('  Vertex 2:'); v2=(_ask('    x: ',cast=float),_ask('    y: ',cast=float),_ask('    z: ',cast=float))
                            print('  Vertex 3:'); v3=(_ask('    x: ',cast=float),_ask('    y: ',cast=float),_ask('    z: ',cast=float))
                            print('  Vertex 4:'); v4=(_ask('    x: ',cast=float),_ask('    y: ',cast=float),_ask('    z: ',cast=float))
                            x_cm,y_cm,z_cm = PCoM.CoMOfTetrahedron3D(v1,v2,v3,v4)
                            print(f'\n  Tetrahedron CoM = ({x_cm:.6f}, {y_cm:.6f}, {z_cm:.6f}) m')
                        case 3:
                            masses, points = _collect_particles_3d()
                            x_cm,y_cm,z_cm,dists = PCoM.DistanceFromCoM3D(masses, points)
                            print(f'\n  CoM = ({x_cm:.6f}, {y_cm:.6f}, {z_cm:.6f}) m')
                            for i,(m,d) in enumerate(zip(masses,dists),1):
                                print(f'    Particle {i}  ({m} kg):  r = {d:.6f} m')
                        case _: print('\n  That was not a valid option.'); continue

                # ── SECTION 4: Continuous Bodies ────────────────────────────────
                elif sec == 4:
                    match choice:
                        case 1:
                            L=_ask('  Length L (m): ',cast=float); x0=_ask('  Start x₀ (m, default 0): ',cast=float)
                            r = PCoM.CoMUniformRod(L, x0)
                            _step('Uniform rod','x_cm = x₀ + L/2',f'{x0} + {L}/2', r, 'm')
                            print(f'\n  x_cm = {r:.6f} m')
                        case 2:
                            a=_ask('  Rod start x=a (m): ',cast=float); b=_ask('  Rod end x=b (m): ',cast=float)
                            print('  Enter density function λ(x) as a Python expression (use x):')
                            expr = input('  λ(x) = ').strip()
                            lam = lambda x, _e=expr: eval(_e, {'x':x,'math':math})
                            r = PCoM.CoMLinearDensityRod(a, b, lam)
                            print(f'\n  x_cm = {r:.6f} m')
                        case 3:
                            W=_ask('  Width W (m): ',cast=float); H=_ask('  Height H (m): ',cast=float)
                            x0=_ask('  Bottom-left x₀ (m): ',cast=float); y0=_ask('  Bottom-left y₀ (m): ',cast=float)
                            x_cm,y_cm = PCoM.CoMUniformRectangle(W,H,x0,y0)
                            _step('Rectangle CoM','(x₀+W/2, y₀+H/2)','', f'({x_cm:.4f}, {y_cm:.4f})','m')
                            print(f'\n  CoM = ({x_cm:.6f}, {y_cm:.6f}) m')
                        case 4:
                            b=_ask('  Base b (m): ',cast=float); h=_ask('  Height h (m): ',cast=float)
                            x0=_ask('  Right-angle x₀: ',cast=float); y0=_ask('  Right-angle y₀: ',cast=float)
                            x_cm,y_cm = PCoM.CoMRightTriangle(b,h,x0,y0)
                            _step('Right triangle','(x₀+b/3, y₀+h/3)','', f'({x_cm:.4f},{y_cm:.4f})','m')
                            print(f'\n  CoM = ({x_cm:.6f}, {y_cm:.6f}) m')
                        case 5:
                            r_val=_ask('  Radius r (m): ',cast=float); y0=_ask('  Base y₀ (m): ',cast=float)
                            _,y_cm = PCoM.CoMSemicircle(r_val, y0)
                            _step('Solid semicircle','y_cm = y₀ + 4r/(3π)',
                                  f'{y0} + 4×{r_val}/(3π)', y_cm, 'm')
                            print(f'\n  y_cm = {y_cm:.6f} m')
                        case 6:
                            r_val=_ask('  Radius r (m): ',cast=float); y0=_ask('  Base y₀ (m): ',cast=float)
                            _,y_cm = PCoM.CoMSemicircularArc(r_val, y0)
                            _step('Semicircular arc','y_cm = y₀ + 2r/π',
                                  f'{y0} + 2×{r_val}/π', y_cm, 'm')
                            print(f'\n  y_cm = {y_cm:.6f} m')
                        case 7:
                            r_val=_ask('  Radius r (m): ',cast=float); z0=_ask('  Base z₀ (m): ',cast=float)
                            z_cm = PCoM.CoMSolidHemisphere(r_val, z0)
                            _step('Solid hemisphere','z_cm = z₀ + 3r/8',
                                  f'{z0} + 3×{r_val}/8', z_cm, 'm')
                            print(f'\n  z_cm = {z_cm:.6f} m')
                        case 8:
                            r_val=_ask('  Radius r (m): ',cast=float); z0=_ask('  Base z₀ (m): ',cast=float)
                            z_cm = PCoM.CoMHollowHemisphere(r_val, z0)
                            _step('Hollow hemisphere','z_cm = z₀ + r/2',
                                  f'{z0} + {r_val}/2', z_cm, 'm')
                            print(f'\n  z_cm = {z_cm:.6f} m')
                        case 9:
                            h=_ask('  Height h (m): ',cast=float); z0=_ask('  Base z₀ (m): ',cast=float)
                            z_cm = PCoM.CoMSolidCone(h, z0)
                            _step('Solid cone','z_cm = z₀ + h/4',
                                  f'{z0} + {h}/4', z_cm, 'm')
                            print(f'\n  z_cm = {z_cm:.6f} m')
                        case 10:
                            r_val=_ask('  Radius r (m): ',cast=float)
                            x_cm,y_cm = PCoM.CoMQuarterCircle(r_val)
                            _step('Quarter-circle','(4r/3π, 4r/3π)','', f'({x_cm:.4f},{y_cm:.4f})','m')
                            print(f'\n  CoM = ({x_cm:.6f}, {y_cm:.6f}) m')
                        case 11:
                            h=_ask('  Height h (m): ',cast=float); z0=_ask('  Base z₀ (m): ',cast=float)
                            z_cm = PCoM.CoMHollowConicalShell(h, z0)
                            _step('Conical shell','z_cm = z₀ + h/3',
                                  f'{z0} + {h}/3', z_cm, 'm')
                            print(f'\n  z_cm = {z_cm:.6f} m')
                        case 12:
                            h=_ask('  Height h (m): ',cast=float); z0=_ask('  Base z₀ (m): ',cast=float)
                            z_cm = PCoM.CoMSolidCylinder(h, z0)
                            print(f'\n  z_cm = {z_cm:.6f} m')
                        case _: print('\n  That was not a valid option.'); continue

                # ── SECTION 5: Composite Bodies ─────────────────────────────────
                elif sec == 5:
                    match choice:
                        case 1:
                            print()
                            _p('Enter each component as (mass, CoM position). Use negative mass for a removed region.')
                            n = _ask('  Number of components: ', cast=int)
                            components = []
                            for i in range(n):
                                m = _ask(f'  Component {i+1} mass (negative to remove): ', cast=float)
                                x = _ask(f'  Component {i+1} CoM x: ', cast=float)
                                components.append((m, x))
                            r = PCoM.CompositeCoM1D(components)
                            print(f'\n  Composite x_cm = {r:.6f} m')
                        case 2:
                            n = _ask('  Number of components: ', cast=int)
                            components = []
                            for i in range(n):
                                m=_ask(f'  Component {i+1} mass: ',cast=float)
                                x=_ask(f'  Component {i+1} CoM x: ',cast=float)
                                y=_ask(f'  Component {i+1} CoM y: ',cast=float)
                                components.append((m, (x, y)))
                            x_cm,y_cm = PCoM.CompositeCoM2D(components)
                            print(f'\n  Composite CoM = ({x_cm:.6f}, {y_cm:.6f}) m')
                        case 3:
                            n = _ask('  Number of components: ', cast=int)
                            components = []
                            for i in range(n):
                                m=_ask(f'  m{i+1}: ',cast=float)
                                x=_ask(f'  x{i+1}: ',cast=float)
                                y=_ask(f'  y{i+1}: ',cast=float)
                                z=_ask(f'  z{i+1}: ',cast=float)
                                components.append((m,(x,y,z)))
                            x_cm,y_cm,z_cm = PCoM.CompositeCoM3D(components)
                            print(f'\n  Composite CoM = ({x_cm:.6f}, {y_cm:.6f}, {z_cm:.6f}) m')
                        case 4:
                            print()
                            _p('Rectangle with a circular hole. Hole is treated as negative mass proportional to its area.')
                            W=_ask('  Rectangle width W (m): ',cast=float); H=_ask('  Rectangle height H (m): ',cast=float)
                            m_rect=_ask('  Total rectangle mass (kg): ',cast=float)
                            r_hole=_ask('  Hole radius (m): ',cast=float)
                            hx=_ask('  Hole centre x (m): ',cast=float); hy=_ask('  Hole centre y (m): ',cast=float)
                            x_cm,y_cm = PCoM.RemoveCircleFromRectangle(W,H,m_rect,r_hole,hx,hy)
                            print(f'\n  CoM after hole = ({x_cm:.6f}, {y_cm:.6f}) m')
                        case 5:
                            m1=_ask('  m1 (kg): ',cast=float); x1=_ask('  x1 (m): ',cast=float)
                            m2=_ask('  m2 (kg): ',cast=float); x2=_ask('  x2 (m): ',cast=float)
                            r = PCoM.TwoHalfSystem(m1,x1,m2,x2)
                            print(f'\n  Dumbbell CoM x = {r:.6f} m')
                        case _: print('\n  That was not a valid option.'); continue

                # ── SECTION 6: CoM in Motion ────────────────────────────────────
                elif sec == 6:
                    match choice:
                        case 1:
                            masses, vels = [], []
                            n = _ask('  Number of particles: ', cast=int)
                            for i in range(n):
                                masses.append(_ask(f'  m{i+1} (kg): ',cast=float))
                                vels.append(_ask(f'  v{i+1} (m/s): ',cast=float))
                            v_cm = PCoM.CoMVelocity1D(masses, vels)
                            _step('CoM velocity','v_cm = Σmᵢvᵢ / M','', v_cm, 'm/s')
                            print(f'\n  v_cm = {v_cm:.6f} m/s')
                        case 2:
                            masses, vels = [], []
                            n = _ask('  Number of particles: ', cast=int)
                            for i in range(n):
                                masses.append(_ask(f'  m{i+1}: ',cast=float))
                                vx=_ask(f'  vx{i+1}: ',cast=float); vy=_ask(f'  vy{i+1}: ',cast=float)
                                vels.append((vx,vy))
                            vx_cm,vy_cm = PCoM.CoMVelocity2D(masses, vels)
                            print(f'\n  v_cm = ({vx_cm:.6f}, {vy_cm:.6f}) m/s')
                        case 3:
                            n = _ask('  Number of particles: ', cast=int)
                            masses=[_ask(f'  m{i+1}: ',cast=float) for i in range(n)]
                            forces=[_ask(f'  F{i+1} (N): ',cast=float) for i in range(n)]
                            a_cm = PCoM.CoMAcceleration(masses, forces)
                            _step('CoM acceleration','a_cm = F_net / M',
                                  f'{sum(forces)} / {sum(masses)}', a_cm, 'm/s²')
                            print(f'\n  a_cm = {a_cm:.6f} m/s²')
                        case 4:
                            print()
                            _p('After an explosion, momentum is conserved so v_cm is unchanged.')
                            M=_ask('  Total initial mass M (kg): ',cast=float)
                            v_cm_before=_ask('  Initial v_cm (m/s): ',cast=float)
                            m1=_ask('  Mass of fragment 1 (kg): ',cast=float)
                            v1=_ask('  Velocity of fragment 1 (m/s): ',cast=float)
                            v2, m2 = PCoM.CoMAfterExplosion1D(M, v_cm_before, m1, v1)
                            _step('Fragment 2 velocity','v2=(M·v_cm − m1·v1)/m2',
                                  f'({M}·{v_cm_before}−{m1}·{v1})/{m2}', v2, 'm/s')
                            print(f'\n  m2 = {m2:.4f} kg')
                            print(f'  v2 = {v2:.6f} m/s')
                        case 5:
                            print()
                            _p('If only internal forces act, CoM stays fixed. Given displacements of all'
                               ' but the last particle, this finds the last displacement needed.')
                            masses, positions = _collect_particles_1d()
                            displacements = []
                            for i in range(len(masses)-1):
                                displacements.append(_ask(f'  Δx of particle {i+1} (m): ',cast=float))
                            delta_last = PCoM.CoMFixedAfterInternalForces(masses, positions, displacements)
                            print(f'\n  Particle {len(masses)} must move: Δx = {delta_last:.6f} m')
                        case 6:
                            n = _ask('  Number of fragments: ', cast=int)
                            masses=[_ask(f'  m{i+1}: ',cast=float) for i in range(n)]
                            vels=[_ask(f'  v{i+1}_after: ',cast=float) for i in range(n)]
                            p_before, p_after, ok = PCoM.ExplosionCoMCheck(masses, vels)
                            print(f'\n  p_after = {p_after:.6f} kg·m/s')
                            print(f'  Momentum conserved (p≈0): {"Yes ✓" if ok else "No ✗"}')
                        case _: print('\n  That was not a valid option.'); continue

                # ── SECTION 7: CoM Frame ────────────────────────────────────────
                elif sec == 7:
                    match choice:
                        case 1:
                            masses, vels = [], []
                            n = _ask('  Particles: ', cast=int)
                            for i in range(n):
                                masses.append(_ask(f'  m{i+1}: ',cast=float))
                                vels.append(_ask(f'  v{i+1}: ',cast=float))
                            v_cm, v_prime = PCoM.CoMFrameVelocities1D(masses, vels)
                            print(f'\n  v_cm = {v_cm:.6f} m/s  (lab frame)')
                            print('  CoM-frame velocities:')
                            for i,(m,vp) in enumerate(zip(masses,v_prime),1):
                                print(f'    m{i}={m} kg:  v\' = {vp:+.6f} m/s')
                        case 2:
                            masses, vels = [], []
                            n = _ask('  Particles: ', cast=int)
                            for i in range(n):
                                masses.append(_ask(f'  m{i+1}: ',cast=float))
                                vx=_ask(f'  vx{i+1}: ',cast=float); vy=_ask(f'  vy{i+1}: ',cast=float)
                                vels.append((vx,vy))
                            (vx_cm,vy_cm), v_prime = PCoM.CoMFrameVelocities2D(masses, vels)
                            print(f'\n  v_cm = ({vx_cm:.4f}, {vy_cm:.4f}) m/s')
                            for i,(m,vp) in enumerate(zip(masses,v_prime),1):
                                print(f'    m{i}: v\' = ({vp[0]:+.4f}, {vp[1]:+.4f}) m/s')
                        case 3:
                            masses, vels = [], []
                            n = _ask('  Particles: ', cast=int)
                            for i in range(n):
                                masses.append(_ask(f'  m{i+1}: ',cast=float))
                                vels.append(_ask(f'  v{i+1}: ',cast=float))
                            ke_cm, ke_lab, v_cm = PCoM.KineticEnergyCoMFrame1D(masses, vels)
                            _step('KE lab','½Σmᵢvᵢ²','', ke_lab, 'J')
                            _step('KE CoM frame','KE_lab − ½M v_cm²',
                                  f'{ke_lab:.4f} − ½×{sum(masses)}×{v_cm:.4f}²', ke_cm, 'J')
                            print(f'\n  v_cm     = {v_cm:.6f} m/s')
                            print(f'  KE (lab) = {ke_lab:.6f} J')
                            print(f'  KE (CoM) = {ke_cm:.6f} J  (available for inelastic processes)')
                        case 4:
                            v1=_ask('  v1 (m/s): ',cast=float); v2=_ask('  v2 (m/s): ',cast=float)
                            v_rel = PCoM.RelativeVelocity1D(v1, v2)
                            _step('Relative velocity','v_rel = v1 − v2',f'{v1} − {v2}', v_rel, 'm/s')
                            print(f'\n  v_rel = {v_rel:.6f} m/s')
                        case 5:
                            m1=_ask('  m1 (kg): ',cast=float); m2=_ask('  m2 (kg): ',cast=float)
                            mu = PCoM.ReducedMass(m1, m2)
                            _step('Reduced mass','μ = m1·m2/(m1+m2)',
                                  f'{m1}·{m2}/({m1}+{m2})', mu, 'kg')
                            print(f'\n  μ = {mu:.6f} kg')
                        case 6:
                            m1=_ask('  m1 (kg): ',cast=float); v1=_ask('  v1 (m/s): ',cast=float)
                            m2=_ask('  m2 (kg): ',cast=float); v2=_ask('  v2 (m/s): ',cast=float)
                            ke_rel = PCoM.RelativeKE1D(m1,v1,m2,v2)
                            _step('Relative KE','½μ v_rel²','', ke_rel, 'J')
                            print(f'\n  KE_rel = {ke_rel:.6f} J')
                        case _: print('\n  That was not a valid option.'); continue

                # ── SECTION 8: Moment of Inertia ────────────────────────────────
                elif sec == 8:
                    match choice:
                        case 1:
                            n = _ask('  Point masses: ', cast=int)
                            masses=[_ask(f'  m{i+1}: ',cast=float) for i in range(n)]
                            rs=[_ask(f'  r{i+1} from axis: ',cast=float) for i in range(n)]
                            I = PCoM.MomentOfInertiaPointMasses(masses, rs)
                            _step('I','I = Σmᵢrᵢ²','', I, 'kg·m²')
                            print(f'\n  I = {I:.6f} kg·m²')
                        case 2:
                            I_cm=_ask('  I_cm (kg·m²): ',cast=float)
                            m=_ask('  Mass m (kg): ',cast=float)
                            d=_ask('  Distance d from CoM to new axis (m): ',cast=float)
                            I = PCoM.ParallelAxisTheorem(I_cm, m, d)
                            _step('Parallel axis','I = I_cm + md²',
                                  f'{I_cm} + {m}×{d}²', I, 'kg·m²')
                            print(f'\n  I = {I:.6f} kg·m²')
                        case 3:
                            Ix=_ask('  I_x (kg·m²): ',cast=float); Iy=_ask('  I_y (kg·m²): ',cast=float)
                            Iz = PCoM.PerpendiculaAxisTheorem(Ix, Iy)
                            _step('Perp. axis','I_z = I_x + I_y',f'{Ix}+{Iy}', Iz, 'kg·m²')
                            print(f'\n  I_z = {Iz:.6f} kg·m²')
                        case 4:
                            print()
                            print('  Shapes:')
                            print('  (1)  Solid sphere  2mr²/5')
                            print('  (2)  Hollow sphere  2mr²/3')
                            print('  (3)  Solid cylinder  mr²/2  (symmetry axis)')
                            print('  (4)  Hollow cylinder  mr²   (symmetry axis)')
                            print('  (5)  Thin rod about centre  mL²/12')
                            print('  (6)  Thin rod about end      mL²/3')
                            print('  (7)  Rectangular plate       m(w²+h²)/12')
                            print()
                            shape = _menu_int('  Shape: ')
                            m = _ask('  Mass m (kg): ', cast=float)
                            if shape in (1,2,3,4):
                                r_val = _ask('  Radius r (m): ', cast=float)
                                fns = {1:PCoM.I_SolidSphere, 2:PCoM.I_HollowSphere,
                                       3:PCoM.I_SolidCylinder, 4:PCoM.I_HollowCylinder}
                                I = fns[shape](m, r_val) if shape in fns else 0
                            elif shape in (5,6):
                                L_val = _ask('  Length L (m): ', cast=float)
                                I = PCoM.I_ThinRod_Center(m,L_val) if shape==5 else PCoM.I_ThinRod_End(m,L_val)
                            elif shape == 7:
                                w=_ask('  Width w: ',cast=float); h=_ask('  Height h: ',cast=float)
                                I = PCoM.I_RectangularPlate(m, w, h)
                            else:
                                print('\n  Invalid shape.'); continue
                            print(f'\n  I_cm = {I:.6f} kg·m²')
                        case 5:
                            print()
                            _p('Enter each component as (I_cm, mass, distance to common axis).')
                            n = _ask('  Components: ', cast=int)
                            comps = []
                            for i in range(n):
                                I_c=_ask(f'  I_cm{i+1}: ',cast=float)
                                m_c=_ask(f'  m{i+1}: ',cast=float)
                                d_c=_ask(f'  d{i+1} (distance to common axis): ',cast=float)
                                comps.append((I_c,m_c,d_c))
                            I_total = PCoM.AxisShiftCombined(comps)
                            print(f'\n  I_total = {I_total:.6f} kg·m²')
                        case _: print('\n  That was not a valid option.'); continue

                # ── SECTION 9: Word Problem Solver ──────────────────────────────
                elif sec == 9:
                    match choice:
                        case 1:
                            print()
                            _p('Type or paste a 1D CoM problem. I will extract masses and positions.')
                            _p('Example: "A 2 kg mass at position 1 m and a 5 kg mass at position 4 m."')
                            print()
                            raw = input('  Problem: ').strip()
                            r = PCoM.ParseCoMProblem1D(raw)
                            if r is None:
                                print('\n  ✗  Could not extract values from that sentence.')
                                print('  Tip: include "N kg at X m" or "m=N x=M" pairs.')
                            else:
                                print(f'\n  ✓  Extracted {len(r["masses"])} particle(s):')
                                for i,(m,x) in enumerate(zip(r['masses'],r['positions']),1):
                                    print(f'    Particle {i}:  m = {m} kg   x = {x} m')
                                print()
                                _show_steps(PCoM.StepByStepCoM1D(r['masses'], r['positions']))
                                print(f'  M_total = {r["M_total"]:.4f} kg')
                                print(f'  Σmᵢxᵢ  = {r["weighted_sum"]:.4f} kg·m')
                                print(f'  x_cm    = {r["x_cm"]:.6f} m')
                        case 2:
                            print()
                            _p('Type or paste a 2D CoM problem.')
                            _p('Example: "3 kg at (1,2) and 5 kg at (4,6)"')
                            print()
                            raw = input('  Problem: ').strip()
                            r = PCoM.ParseCoMProblem2D(raw)
                            if r is None:
                                print('\n  ✗  Could not parse. Try "N kg at (X, Y)" format.')
                            else:
                                print(f'\n  ✓  Extracted {len(r["masses"])} particle(s):')
                                for i,(m,p) in enumerate(zip(r['masses'],r['points']),1):
                                    print(f'    Particle {i}:  m={m} kg  at ({p[0]}, {p[1]}) m')
                                _show_steps(PCoM.StepByStepCoM2D(r['masses'], r['points']))
                                print(f'  CoM = ({r["x_cm"]:.6f}, {r["y_cm"]:.6f}) m')
                        case 3:
                            print()
                            _p('Explosion / split problem.  The CoM velocity is conserved.')
                            _p('Enter the system state before and one fragment\'s velocity after.')
                            M=_ask('  Total mass M (kg): ',cast=float)
                            v_cm=_ask('  v_cm before explosion (m/s): ',cast=float)
                            m1=_ask('  Mass of known fragment m1 (kg): ',cast=float)
                            v1=_ask('  Velocity of m1 after (m/s): ',cast=float)
                            v2, m2 = PCoM.CoMAfterExplosion1D(M, v_cm, m1, v1)
                            print(f'\n  Fragment 2:  m2 = {m2:.4f} kg   v2 = {v2:.6f} m/s')
                            print()
                            print('  Verification:')
                            p_total = m1*v1 + m2*v2
                            p_orig  = M*v_cm
                            print(f'    p_before = {p_orig:.4f} kg·m/s')
                            print(f'    p_after  = {p_total:.4f} kg·m/s')
                            print(f'    Conserved: {"Yes ✓" if abs(p_total-p_orig)<1e-6 else "No ✗"}')
                        case _: print('\n  That was not a valid option.'); continue

            except _AskAbort:
                print()
                _p('Calculation cancelled. Returning to the function list.')
                print()
                continue
            except Exception as e:
                print(f'\n  Error: {e}')
                print()
                continue
            print()