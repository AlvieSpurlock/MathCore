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
import Config                                              # Validation and RNG


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

def CollectVariables():
    """Collects an unlimited list of numbers from the user. Used by add/sub/mul/div."""
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
        action = int(input('  Enter a number to choose: '))
        match action:
            case 1:
                val = float(input('  Enter a value: '))
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
                    pick = int(input('  Enter the number of the variable to remove: '))
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
                        confirm = int(input('  Enter a number to choose: '))
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
        print()
        _ExitBar('Exit MathCore Debug')
        print()
        MathType = _menu_int('  Choose a math type: ')
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
        sec = int(input('  Select a section: '))
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
            choice = int(input('  Select a function: '))
            if choice == 0: break
            result = None
            if sec == 1:
                match choice:
                    case 1:
                        print()
                        print('  Add — enter as many numbers as you want.')
                        variables = CollectVariables()
                        result = variables[0]
                        for v in variables[1:]:
                            result = BasicMath.add(result, v)
                        print(f"\n  Adding: {" + ".join(str(v) for v in variables)}")
                    case 2:
                        print()
                        print('  Subtract — each is subtracted from the previous.')
                        variables = CollectVariables()
                        result = variables[0]
                        for v in variables[1:]:
                            result = BasicMath.sub(result, v)
                        print(f"\n  Subtracting: {" - ".join(str(v) for v in variables)}")
                    case 3:
                        print()
                        print('  Multiply — enter as many numbers as you want.')
                        variables = CollectVariables()
                        result = variables[0]
                        for v in variables[1:]:
                            result = BasicMath.multi(result, v)
                        print(f"\n  Multiplying: {" × ".join(str(v) for v in variables)}")
                    case 4:
                        print()
                        print('  Divide — each divides the previous result.')
                        variables = CollectVariables()
                        result = variables[0]
                        for v in variables[1:]:
                            result = BasicMath.div(result, v)
                        print(f"\n  Dividing: {" ÷ ".join(str(v) for v in variables)}")
                    case _:
                        print('\n  That was not a valid option.')
                        continue
            elif sec == 2:
                match choice:
                    case 1:
                        result = Config.Checks.IsEven(int(input('  Enter a number to check: ')))
                    case 2:
                        result = BasicMath.mod(int(input('  First number: ')), int(input('  Divide by (get remainder): ')))
                    case 3:
                        result = Config.RNG.rand(int(input('  Minimum value: ')), int(input('  Maximum value: ')))
                    case _:
                        print('\n  That was not a valid option.')
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
        _SectionHeader('Physics', 'Choose a sub-module')
        print('  (1)  Kinematics 1D')
        print('  (2)  Kinematics 2D')
        print('  (3)  Kinematics 3D')
        print('  (4)  Forces 2D')
        print('  (5)  Forces 3D')
        print()
        _ExitBar('Return to main menu')
        print()
        choice = _menu_int('  Choose: ')
        if choice == 0: return
        match choice:
            case 1: Physics1DDebug()
            case 2: Physics2DDebug()
            case 3: Physics3DDebug()
            case 4: Forces2DDebug()
            case 5: Forces3DDebug()
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
        sec = int(input('  Select a section: '))
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
            choice = int(input('  Select a function: '))
            if choice == 0: break
            result = None
            if sec == 1:
                match choice:
                    case 1:
                        result = Physics_1D.GetDistance(
                            float(input('  Starting position (m): ')),
                            float(input('  Ending position (m): '))
                        )
                    case 2:
                        result = Physics_1D.GetTime(
                            float(input('  Start time (s): ')),
                            float(input('  End time (s): '))
                        )
                    case 3:
                        result = Physics_1D.Velocity(
                            float(input('  Distance traveled (m): ')),
                            float(input('  Time taken (s): '))
                        )
                    case 4:
                        result = Physics_1D.FinalVelocity(
                            float(input('  Acceleration (m/s²): ')),
                            float(input('  Distance (m): ')),
                            float(input('  Time (s): ')),
                            float(input('  Starting velocity (m/s): '))
                        )
                    case 5:
                        result = Physics_1D.Acceleration(
                            float(input('  Starting velocity (m/s): ')),
                            float(input('  Ending velocity (m/s): ')),
                            float(input('  Time (s): '))
                        )
                    case 6:
                        result = Physics_1D.InstantAcceleration(
                            float(input('  Starting velocity (m/s): ')),
                            float(input('  Ending velocity (m/s): ')),
                            float(input('  Time interval (s) — use a very small value for instantaneous: '))
                        )
                    case 7:
                        result = Physics_1D.ConstantAcceleration(
                            float(input('  Starting velocity (m/s): ')),
                            float(input('  Ending velocity (m/s): ')),
                            float(input('  Time (s): '))
                        )
                    case 8:
                        result = Physics_1D.GetDisplacement(
                            float(input('  Acceleration (m/s²): ')),
                            float(input('  Time (s): ')),
                            float(input('  Starting velocity (m/s — enter 0 if starting from rest): '))
                        )
                    case 9:
                        result = Physics_1D.GetPosition(
                            float(input('  Acceleration (m/s²): ')),
                            float(input('  Time (s): ')),
                            float(input('  Starting velocity (m/s — enter 0 if starting from rest): ')),
                            float(input('  Starting position (m — enter 0 if at the origin): '))
                        )
                    case _:
                        print('\n  That was not a valid option.')
                        continue
            elif sec == 2:
                match choice:
                    case 1:
                        result = Physics_1D.SolveForTime(
                            float(input('  Distance to travel (m): ')),
                            float(input('  Constant speed (m/s): '))
                        )
                        print(f"\n  Time to travel that distance: {result:.4f} s")
                        print()
                        continue
                    case 2:
                        result = Physics_1D.SolveForDistance(
                            float(input('  Speed (m/s): ')),
                            float(input('  Time (s): '))
                        )
                        print(f"\n  Distance traveled: {result:.4f} m")
                        print()
                        continue
                    case 3:
                        v_base  = float(input('  Base speed (m/s): '))
                        delta_v = float(input('  Speed difference (m/s — negative to go slower): '))
                        result  = Physics_1D.SpeedWithDelta(v_base, delta_v)
                        print(f"\n  New speed: {result:.4f} m/s")
                        print()
                        continue
                    case 4:
                        distance = float(input('  Distance of the course (m): '))
                        v_base   = float(input('  Baseline speed to beat (m/s): '))
                        delta_v  = float(input('  Amount faster than the baseline (m/s): '))
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
                        v_now = float(input('  Current velocity (m/s): '))
                        a     = float(input('  Constant acceleration (m/s²): '))
                        dt    = float(input('  How many seconds AFTER this moment: '))
                        result = Physics_1D.VelocityAfter(v_now, a, dt)
                        print(f"\n  Velocity {dt} s later: {result:.4f} m/s")
                        print()
                        continue
                    case 2:
                        v_now = float(input('  Current velocity (m/s): '))
                        a     = float(input('  Constant acceleration (m/s²): '))
                        dt    = float(input('  How many seconds BEFORE this moment: '))
                        result = Physics_1D.VelocityBefore(v_now, a, dt)
                        print(f"\n  Velocity {dt} s earlier: {result:.4f} m/s")
                        print()
                        continue
                    case 3:
                        v_initial = float(input('  Earlier velocity (m/s): '))
                        v_final   = float(input('  Later velocity (m/s): '))
                        a         = float(input('  Constant acceleration (m/s²): '))
                        result    = Physics_1D.TimeBetweenVelocities(v_initial, v_final, a)
                        print(f"\n  Time between those velocities: {result:.4f} s")
                        print()
                        continue
                    case 4:
                        v_ref    = float(input('  Known velocity at reference time (m/s): '))
                        t_ref    = float(input('  Reference time (s): '))
                        a        = float(input('  Constant acceleration (m/s²): '))
                        t_target = float(input('  Target time to find velocity at (s): '))
                        result   = Physics_1D.VelocityAtTime(v_ref, t_ref, a, t_target)
                        direction = 'earlier' if t_target < t_ref else 'later'
                        print(f"\n  Velocity at t = {t_target} s ({direction}): {result:.4f} m/s")
                        print()
                        continue
                    case 5:
                        x_now = float(input('  Current position (m — 0 for relative): '))
                        v_now = float(input('  Current velocity (m/s): '))
                        a     = float(input('  Constant acceleration (m/s²): '))
                        dt    = float(input('  How many seconds BEFORE this moment: '))
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
                        v0    = float(input('  Initial speed (m/s): '))
                        decel = float(input('  Deceleration magnitude (m/s² — positive): '))
                        result = Physics_1D.StoppingTime(v0, decel)
                        print(f"\n  Time to stop: {result:.4f} s")
                        print()
                        continue
                    case 2:
                        v0    = float(input('  Initial speed (m/s): '))
                        decel = float(input('  Deceleration magnitude (m/s² — positive): '))
                        result = Physics_1D.StoppingDistance(v0, decel)
                        print(f"\n  Distance traveled while stopping: {result:.4f} m")
                        print()
                        continue
                    case 3:
                        v0    = float(input('  Initial speed at start of braking (m/s): '))
                        decel = float(input('  Deceleration magnitude (m/s² — positive): '))
                        t     = float(input('  Time after braking began (s): '))
                        result = Physics_1D.VelocityWhileStopping(v0, decel, t)
                        print(f"\n  Velocity at t = {t} s during braking: {result:.4f} m/s")
                        if result == 0:
                            print('  (Object has already stopped by this time)')
                        print()
                        continue
                    case 4:
                        v0    = float(input('  Initial speed at start of braking (m/s): '))
                        decel = float(input('  Deceleration magnitude (m/s² — positive): '))
                        t     = float(input('  Time after braking began (s): '))
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
                        v_final = float(input('  Impact velocity (m/s): '))
                        g       = float(input('  Gravity (m/s², Enter = 9.8): ') or '9.8')
                        v0      = float(input('  Initial vertical velocity (0 if dropped): ') or '0')
                        result  = Physics_1D.HeightFromFinalVelocity(v_final, float(g), float(v0))
                        print(f"\n  Height fallen from: {result:.4f} m")
                        print()
                        continue
                    case 2:
                        v_final = float(input('  Impact velocity (m/s): '))
                        g       = float(input('  Gravity (m/s², Enter = 9.8): ') or '9.8')
                        v0      = float(input('  Initial vertical velocity (0 if dropped): ') or '0')
                        result  = Physics_1D.FreeFallTime(v_final, float(g), float(v0))
                        print(f"\n  Time spent falling: {result:.4f} s")
                        print()
                        continue
                    case 3:
                        h  = float(input('  Height of the fall (m): '))
                        g  = float(input('  Gravity (m/s², Enter = 9.8): ') or '9.8')
                        v0 = float(input('  Initial vertical velocity (0 if dropped): ') or '0')
                        result = Physics_1D.ImpactVelocity(h, float(g), float(v0))
                        print(f"\n  Impact velocity: {result:.4f} m/s")
                        print()
                        continue
                    case 4:
                        h  = float(input('  Height of the fall (m): '))
                        g  = float(input('  Gravity (m/s², Enter = 9.8): ') or '9.8')
                        v0 = float(input('  Initial downward velocity (0 if dropped from rest): ') or '0')
                        result = Physics_1D.FreeFallTimeFromHeight(h, float(g), float(v0))
                        print(f"\n  Time to reach the ground: {result:.4f} s")
                        print()
                        continue
                    case 5:
                        v0 = float(input('  Initial upward launch speed (m/s): '))
                        g  = float(input('  Gravity (m/s², Enter = 9.8): ') or '9.8')
                        result = Physics_1D.MaxHeightFromLaunch(v0, float(g))
                        print(f"\n  Maximum height reached: {result:.4f} m")
                        print()
                        continue
                    case 6:
                        v0 = float(input('  Initial upward launch speed (m/s): '))
                        g  = float(input('  Gravity (m/s², Enter = 9.8): ') or '9.8')
                        result = Physics_1D.TimeToMaxHeight(v0, float(g))
                        print(f"\n  Time to reach peak: {result:.4f} s")
                        print()
                        continue
                    case _:
                        print('\n  That was not a valid option.')
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
            mode = int(input('  Choose: '))
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
            sec = int(input('  Select a section: '))
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
                choice = int(input('  Select a function: '))
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
                        vals['speed'] = float(input('  Launch speed (m/s): '))
                        vals['angle'] = float(input('  Launch angle above horizontal (degrees): '))
                        vals['vx0']   = vals['speed'] * math.cos(math.radians(vals['angle']))
                        vals['vy0']   = vals['speed'] * math.sin(math.radians(vals['angle']))
                    else:
                        vals['vx0']   = float(input('  Horizontal speed vx (m/s): '))
                        vals['vy0']   = float(input('  Vertical speed vy (m/s, positive = up): '))
                        vals['speed'] = math.sqrt(vals['vx0']**2 + vals['vy0']**2)
                        vals['angle'] = math.degrees(math.atan2(vals['vy0'], vals['vx0']))
                    vals['mode'] = mode
                    if need_time:
                        vals['time'] = float(input('  Time (s): '))
                    if need_y0:
                        raw = input('  Launch height y0 (Enter = 0): ').strip()
                        vals['y0'] = float(raw) if raw else 0.0
                    if need_mass:
                        vals['mass'] = float(input('  Mass (kg): '))
                    if need_steps:
                        vals['steps'] = int(input('  Number of steps (Enter = 100): ') or '100')
                    return vals

                result = None
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
                if result is not None:
                    print()
                    print(f'  Result: {result}')
                print()

            elif sec == 2:
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
                h  = float(input('  Launch height above ground (m): '))
                if choice in (2, 4, 5):
                    vx = float(input('  Horizontal launch speed (m/s): '))
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
                    mass = float(input('  Mass (kg): '))
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
                        weight = float(input('  Object weight  (N, positive = downward): '))
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
                        mass = float(input('  Mass (kg): '))
                        mu   = float(input('  Coefficient of kinetic friction (μk): '))
                        F    = float(input('  Applied horizontal force (N): '))
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
                        mass  = float(input('  Mass (kg): '))
                        mu    = float(input('  Coefficient of kinetic friction (μk): '))
                        F     = float(input('  Applied force magnitude (N): '))
                        theta = float(input('  Angle below horizontal (degrees): '))
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
                        mass  = float(input('  Mass (kg): '))
                        theta = float(input('  Incline angle (degrees): '))
                        N     = Forces.NormalForceIncline(mass, theta)
                        T     = Forces.FrictionForceIncline(mass, theta)
                        print()
                        print(f'  Normal force  N = mg·cosθ : {N:.4f} N  (perpendicular to slope)')
                        print(f'  Parallel comp T = mg·sinθ : {T:.4f} N  (down the slope / tension needed)')
                    case 4:
                        # Minimum force to overcome static friction
                        mass = float(input('  Mass (kg): '))
                        mu_s = float(input('  Coefficient of static friction (μs): '))
                        N       = Forces.NormalForce(mass)
                        F_min   = Forces.FrictionForce(mu_s, N)
                        print()
                        print(f'  Normal force   N     : {N:.4f} N  (= mg)')
                        print(f'  Min force to move    : {F_min:.4f} N  (= μs × N)')
                        print(f'  Any force > {F_min:.4f} N will start motion')
                    case 5:
                        # Final speed after distance — flat surface
                        mass = float(input('  Mass (kg): '))
                        mu   = float(input('  Coefficient of kinetic friction (μk): '))
                        F    = float(input('  Applied horizontal force (N): '))
                        d    = float(input('  Distance (m): '))
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
                        mass = float(input('  Mass (kg): '))
                        T, W, F_net = Forces.TensionHanging(mass)
                        print()
                        print(f'  Object weight  W     : {W:.4f} N  ↓')
                        print(f'  Rope tension   T     : {T:.4f} N  ↑  (equals weight — at rest)')
                        print(f'  Net force on object  : {F_net:.4f} N  (zero — equilibrium)')
                    case 2:
                        mass = float(input('  Mass (kg): '))
                        a    = float(input('  Acceleration (m/s²)  [positive=up, negative=down]: '))
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
                        mass  = float(input('  Mass (kg): '))
                        theta = float(input('  Angle from vertical (degrees): '))
                        T, T_x, T_y, W = Forces.TensionAtAngle(mass, theta)
                        print()
                        print(f'  Object weight  W     : {W:.4f} N  ↓')
                        print(f'  Rope tension   T     : {T:.4f} N  (magnitude along rope)')
                        print(f'  Horizontal component : {T_x:.4f} N  →  (T·sinθ)')
                        print(f'  Vertical component   : {T_y:.4f} N  ↑  (T·cosθ = W)')
                    case 4:
                        m1 = float(input('  Mass 1 (kg): '))
                        m2 = float(input('  Mass 2 (kg): '))
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
                        m1 = float(input('  Mass 1 (kg): '))
                        m2 = float(input('  Mass 2 (kg): '))
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
                        mass = float(input('  Mass (kg): '))
                        v    = float(input('  Speed (m/s): '))
                        r    = float(input('  Radius (m): '))
                        Fc   = Forces.CentripetalForce(mass, v, r)
                        ac   = Forces.CentripetalAcceleration(v, r)
                        T    = Forces.CircularPeriod(r, v)
                        print()
                        print(f'  Centripetal force   Fc : {Fc:.4f} N  (= mv²/r, directed inward)')
                        print(f'  Centripetal accel   ac : {ac:.4f} m/s²')
                        print(f'  Period               T : {T:.4f} s  (time for one full circle)')
                    case 2:
                        mu = float(input('  Coefficient of friction (μ): '))
                        r  = float(input('  Radius (m): '))
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
                        v = float(input('  Speed (m/s): '))
                        r = float(input('  Radius (m): '))
                        ac = Forces.CentripetalAcceleration(v, r)
                        print()
                        print(f'  Centripetal acceleration : {ac:.4f} m/s²  (ac = v²/r, directed inward)')
                    case 4:
                        r = float(input('  Radius (m): '))
                        v = float(input('  Speed (m/s): '))
                        T = Forces.CircularPeriod(r, v)
                        print()
                        print(f'  Period  T = 2πr/v : {T:.4f} s  (time for one complete revolution)')
                    case 5:
                        r = float(input('  Radius (m): '))
                        v = float(input('  Speed (m/s): '))
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
                        m1 = float(input('  Mass 1 (kg): '))
                        m2 = float(input('  Mass 2 (kg): '))
                        r  = float(input('  Distance between centres (m): '))
                        F  = Forces.GravitationalForce(m1, m2, r)
                        print()
                        print(f'  Gravitational force : {F:.4e} N  (F = G·m1·m2/r²)')
                        print(f'  Acts equally on both bodies — attractive, along the line joining them')
                    case 2:
                        M = float(input('  Mass of large body (kg): '))
                        r = float(input('  Distance from centre (m): '))
                        g = Forces.GravitationalFieldStrength(M, r)
                        print()
                        print(f'  Field strength : {g:.4e} m/s²  (g = G·M/r²)')
                        print(f'  This is also the free-fall acceleration at that distance')
                    case 3:
                        M        = float(input('  Mass of large body (kg): '))
                        g_target = float(input('  Target field strength (m/s²): '))
                        r = Forces.GravitationalFieldRadius(M, g_target)
                        print()
                        print(f'  Distance from centre : {r:.4e} m  (r = sqrt(G·M/g))')
                    case 4:
                        M = float(input('  Mass of large body (kg): '))
                        r = float(input('  Orbital radius — centre to orbit (m): '))
                        v = Forces.OrbitalSpeed(M, r)
                        T = Forces.OrbitalPeriod(M, r)
                        print()
                        print(f'  Orbital speed  v : {v:.4e} m/s  (v = sqrt(G·M/r))')
                        print(f'  Orbital period T : {T:.4e} s   (T = 2π·sqrt(r³/GM))')
                    case 5:
                        M = float(input('  Mass of large body (kg): '))
                        r = float(input('  Orbital radius — centre to orbit (m): '))
                        T = Forces.OrbitalPeriod(M, r)
                        v = Forces.OrbitalSpeed(M, r)
                        print()
                        print(f'  Orbital period T : {T:.4e} s   (T = 2π·sqrt(r³/GM))')
                        print(f'  Orbital speed  v : {v:.4e} m/s  (v = sqrt(G·M/r))')
                    case 6:
                        m1 = float(input('  Mass 1 (kg): '))
                        m2 = float(input('  Mass 2 (kg): '))
                        r  = float(input('  Distance between centres (m): '))
                        U  = Forces.GravitationalPotentialEnergy(m1, m2, r)
                        print()
                        print(f'  Gravitational PE : {U:.4e} J  (U = −G·m1·m2/r)')
                        print(f'  Negative — energy needed to separate the bodies to infinity')
                    case 7:
                        M = float(input('  Mass of large body (kg): '))
                        r = float(input('  Distance from centre (m): '))
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
            mode = int(input('  Choose: '))
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
            sec = int(input('  Select a section: '))
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
                choice = int(input('  Select a function: '))
            except ValueError:
                continue
            if choice == 0:
                break

            if sec == 1:
                result = None
                match choice:
                    case 1:
                        result = Physics_3D.ProjectileVelocity(
                            float(input('  Launch speed (m/s): ')), float(input('  Launch angle (degrees): ')),
                            float(input('  Time in flight (s): ')), float(input('  Mass (kg): ')))
                    case 2:
                        result = Physics_3D.ProjectilePosition(
                            float(input('  Launch speed (m/s): ')), float(input('  Launch angle (degrees): ')),
                            float(input('  Time in flight (s): ')), float(input('  Mass (kg): ')))
                    case 3:
                        result = Physics_3D.ProjectileRange(
                            float(input('  Launch speed (m/s): ')), float(input('  Launch angle (degrees): ')),
                            float(input('  Total flight time (s): ')), float(input('  Mass (kg): ')))
                    case 4:
                        result = Physics_3D.ProjectileMaxHeight(
                            float(input('  Launch speed (m/s): ')), float(input('  Launch angle (degrees): ')),
                            float(input('  Mass (kg): ')))
                    case 5:
                        result = Physics_3D.DragForce(
                            float(input('  Mass (kg): ')), float(input('  vx (m/s): ')), float(input('  vy (m/s): ')))
                    case 6:
                        result = Physics_3D.ProjectilePath(
                            float(input('  Launch speed (m/s): ')), float(input('  Launch angle (degrees): ')),
                            float(input('  Total flight time (s): ')), float(input('  Mass (kg): ')),
                            int(input('  Number of steps: ')))
                    case 7:
                        result = Physics_3D.ProjectilePathNoAR(
                            float(input('  Launch speed (m/s): ')), float(input('  Launch angle (degrees): ')),
                            float(input('  Total flight time (s): ')), int(input('  Number of steps: ')))
                    case _:
                        print('\n  That was not a valid option.')
                        continue
                if result is not None:
                    print()
                    print(f'  Result: {result}')
                print()

            elif sec == 2:
                # Displacement & position — all component form
                print()
                match choice:
                    case 1:
                        print('  Enter the INITIAL position vector  (r_i):')
                        rix = float(input('    r_ix  (i): '))
                        riy = float(input('    r_iy  (j): '))
                        riz = float(input('    r_iz  (k): '))
                        print('  Enter the FINAL position vector  (r_f):')
                        rfx = float(input('    r_fx  (i): '))
                        rfy = float(input('    r_fy  (j): '))
                        rfz = float(input('    r_fz  (k): '))
                        drx, dry, drz = Physics_3D.DisplacementXYZ(rix, riy, riz, rfx, rfy, rfz)
                        print(f'\n  Δr⃗  =  r⃗_f − r⃗_i  =  {drx:.4f}i  +  {dry:.4f}j  +  {drz:.4f}k')
                        print(f'  |Δr⃗|  =  {Physics_3D.MagnitudeXYZ(drx, dry, drz):.4f} m')
                    case 2:
                        print('  Enter the INITIAL position vector  (r_i):')
                        rix = float(input('    r_ix  (i): '))
                        riy = float(input('    r_iy  (j): '))
                        riz = float(input('    r_iz  (k): '))
                        print('  Enter the DISPLACEMENT vector  (Δr):')
                        drx = float(input('    Δrx  (i): '))
                        dry = float(input('    Δry  (j): '))
                        drz = float(input('    Δrz  (k): '))
                        rfx, rfy, rfz = Physics_3D.FinalPositionXYZ(rix, riy, riz, drx, dry, drz)
                        print(f'\n  r⃗_f  =  r⃗_i + Δr⃗  =  {rfx:.4f}i  +  {rfy:.4f}j  +  {rfz:.4f}k')
                    case 3:
                        print('  Enter the FINAL position vector  (r_f):')
                        rfx = float(input('    r_fx  (i): '))
                        rfy = float(input('    r_fy  (j): '))
                        rfz = float(input('    r_fz  (k): '))
                        print('  Enter the DISPLACEMENT vector  (Δr):')
                        drx = float(input('    Δrx  (i): '))
                        dry = float(input('    Δry  (j): '))
                        drz = float(input('    Δrz  (k): '))
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
                    mass = float(input('  Mass (kg): '))
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
    mass     = float(input('  Mass of the object (kg): '))
    g        = float(input('  Gravity (m/s², Enter = 9.8): ') or '9.8')
    velocity = float(input('  Current velocity (m/s): '))
    height   = float(input('  Current height above ground (m): '))
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
    if int(input('  Enter a number to choose: ')) == 1:
        angle = float(input('  Incline angle (degrees): '))
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
    if int(input('  Enter a number to choose: ')) == 1:
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
        fc = int(input('  Enter a number to choose: '))
        match fc:
            case 1:
                x     = float(input('  Force X (N, negative = left): '))
                y     = float(input('  Force Y (N, negative = down): '))
                force = Forces.Force2D(x, y)
                obj.forces.append(force)
                force_count += 1
                print()
                print(f"  Added — {force.magnitude:.3f} N at {force.angle:.1f}°")
                print()
            case 2:
                magnitude = float(input('  Total strength (N): '))
                angle     = float(input('  Direction (degrees, 0 = right): '))
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
        sec = int(input('  Select a section: '))
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
            query = int(input('  Select a query: '))
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
                        time   = float(input('  Over how many seconds? '))
                        result = obj.NetImpulse(time)
                        print()
                        print(f"  Impulse over {time}s: {result:.3f} N·s")
                    case 6:
                        print()
                        time = float(input('  Advance by how many seconds? '))
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
                area             = float(input('  Cross-sectional area (m²): '))
                drag_coefficient = float(input('  Drag coefficient (e.g. 0.47 for a sphere): '))
                fluid_density    = float(input('  Fluid density (kg/m³, Enter = 1.225): ') or '1.225')
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
    mass     = float(input('  Mass of the object (kg): '))
    g        = float(input('  Gravity (m/s², Enter = 9.8): ') or '9.8')
    velocity = float(input('  Current velocity (m/s): '))
    height   = float(input('  Current height above ground (m): '))
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
    if int(input('  Enter a number to choose: ')) == 1:
        angle = float(input('  Incline angle (degrees): '))
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
    if int(input('  Enter a number to choose: ')) == 1:
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
        fc = int(input('  Enter a number to choose: '))
        match fc:
            case 1:
                x     = float(input('  Force X (N): '))
                y     = float(input('  Force Y (N): '))
                z     = float(input('  Force Z (N): '))
                force = Forces.Force3D(x, y, z)
                obj.forces.append(force)
                force_count += 1
                print()
                print(f"  Added — {force.magnitude:.3f} N, angle {force.angle:.1f}°, phi {force.phi:.1f}°")
                print()
            case 2:
                magnitude = float(input('  Total strength (N): '))
                angle     = float(input('  Horizontal direction (degrees, 0 = forward): '))
                phi       = float(input('  Vertical angle (degrees, 0 = flat, 90 = up): '))
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
        sec = int(input('  Select a section: '))
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
            query = int(input('  Select a query: '))
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
                        time   = float(input('  Over how many seconds? '))
                        result = obj.NetImpulse(time)
                        print()
                        print(f"  Impulse over {time}s: {result:.3f} N·s")
                    case 6:
                        print()
                        time = float(input('  Advance by how many seconds? '))
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
                area             = float(input('  Cross-sectional area (m²): '))
                drag_coefficient = float(input('  Drag coefficient (e.g. 0.47 for a sphere): '))
                fluid_density    = float(input('  Fluid density (kg/m³, Enter = 1.225): ') or '1.225')
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
        sec = int(input('  Select a section: '))
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
            choice = int(input('  Select a function: '))
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
        'Vectors 2D',
        'Vectors 3D',
    ]
    while True:
        _SectionHeader('Geometry', 'Choose a section')
        for i, s in enumerate(SECTIONS, 1):
            print(f"  ({i})  {s}")
        print()
        _ExitBar('Return to main menu')
        print()
        sec = int(input('  Select a section: '))
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
                _p('Pure 2D vector operations — direction and magnitude in the x-y plane.')
                print()
                print('  (1)   X component  (IHat)')
                print('  (2)   Y component  (JHat)')
                print('  (3)   Both X and Y components')
                print('  (4)   Magnitude')
                print('  (5)   Normalize  (unit vector)')
                print('  (6)   Project a onto b')
                print('  (7)   Add  a + b')
                print('  (8)   Subtract  a - b')
                print('  (9)   Dot product  a · b  (scalar)')
                print('  (10)  Cross product  a × b  (Z scalar)')
                print('  (11)  Scale a by scalar')
                print('  (12)  Divide a by scalar')
            elif sec == 10:
                _p('Pure 3D vector operations — direction and magnitude in x-y-z space.')
                print()
                print('  (1)   X component  (IHat)')
                print('  (2)   Y component  (JHat)')
                print('  (3)   Z component  (KHat)')
                print('  (4)   All three components  (IJK)')
                print('  (5)   Magnitude')
                print('  (6)   Normalize  (unit vector)')
                print('  (7)   Project a onto b')
                print('  (8)   Add  a + b')
                print('  (9)   Subtract  a - b')
                print('  (10)  Dot product  a · b  (scalar)')
                print('  (11)  Cross product  a × b  (vector)')
                print('  (12)  Scale a by scalar')
                print('  (13)  Divide a by scalar')
                print('  (14)  Scalar triple product  a · (b × c)')
                print('  (15)  Dot with sum            a · (b + c)')
                print('  (16)  Dot with difference     a · (b - c)')
                print('  (17)  Cross with sum          a × (b + c)')
            print()
            _ExitBar('Return to sections')
            print()
            choice = int(input('  Select a function: '))
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
                # Vectors 2D — pure geometric operations
                def _v2(prompt='a'):
                    raw = input(f'  Vector {prompt} — enter x and y separated by space: ').strip().split()
                    return float(raw[0]), float(raw[1])
                def _polar(x, y):
                    mag   = math.sqrt(x**2 + y**2)
                    angle = math.degrees(math.atan2(y, x)) % 360
                    return mag, angle
                ax, ay = _v2('a')
                mag_a, angle_a = _polar(ax, ay)
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
                    case 7:
                        bx, by = _v2('b')
                        mag_b, angle_b = _polar(bx, by)
                        rx, ry = Physics_2D.AddVectors(mag_a, angle_a, mag_b, angle_b)
                        print(f'\n  a + b  =  {rx:.6f}i  +  {ry:.6f}j')
                    case 8:
                        bx, by = _v2('b')
                        mag_b, angle_b = _polar(bx, by)
                        rx, ry = Physics_2D.SubtractVectors(mag_a, angle_a, mag_b, angle_b)
                        print(f'\n  a - b  =  {rx:.6f}i  +  {ry:.6f}j')
                    case 9:
                        bx, by = _v2('b')
                        mag_b, angle_b = _polar(bx, by)
                        print(f'\n  a · b  =  {Physics_2D.DotProduct(mag_a, angle_a, mag_b, angle_b):.6f}')
                    case 10:
                        bx, by = _v2('b')
                        mag_b, angle_b = _polar(bx, by)
                        print(f'\n  a × b  =  {Physics_2D.CrossProduct(mag_a, angle_a, mag_b, angle_b):.6f}  (Z scalar)')
                    case 11:
                        scalar = float(input('  Scalar: '))
                        rx, ry = Physics_2D.ScalarMultiply(scalar, mag_a, angle_a)
                        print(f'\n  {scalar} × a  =  {rx:.6f}i  +  {ry:.6f}j')
                    case 12:
                        scalar = float(input('  Scalar: '))
                        rx, ry = Physics_2D.ScalarDivide(scalar, mag_a, angle_a)
                        print(f'\n  a / {scalar}  =  {rx:.6f}i  +  {ry:.6f}j')
                    case _:
                        print('\n  That was not a valid option.')
            elif sec == 10:
                # Vectors 3D — pure geometric operations
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
                    case 8:
                        bx, by, bz = _v3('b')
                        rx, ry, rz = Physics_3D.AddVectorsXYZ(ax, ay, az, bx, by, bz)
                        print(f'\n  a + b  =  {rx:.6f}i  +  {ry:.6f}j  +  {rz:.6f}k')
                    case 9:
                        bx, by, bz = _v3('b')
                        rx, ry, rz = Physics_3D.SubtractVectorsXYZ(ax, ay, az, bx, by, bz)
                        print(f'\n  a - b  =  {rx:.6f}i  +  {ry:.6f}j  +  {rz:.6f}k')
                    case 10:
                        bx, by, bz = _v3('b')
                        print(f'\n  a · b  =  {Physics_3D.DotProductXYZ(ax, ay, az, bx, by, bz):.6f}')
                    case 11:
                        bx, by, bz = _v3('b')
                        rx, ry, rz = Physics_3D.CrossProductXYZ(ax, ay, az, bx, by, bz)
                        print(f'\n  a × b  =  {rx:.6f}i  +  {ry:.6f}j  +  {rz:.6f}k')
                    case 12:
                        scalar = float(input('  Scalar: '))
                        rx, ry, rz = Physics_3D.ScalarMultiply(scalar, mag_a, theta_a, phi_a)
                        print(f'\n  {scalar} × a  =  {rx:.6f}i  +  {ry:.6f}j  +  {rz:.6f}k')
                    case 13:
                        scalar = float(input('  Scalar: '))
                        rx, ry, rz = Physics_3D.ScalarDivide(scalar, mag_a, theta_a, phi_a)
                        print(f'\n  a / {scalar}  =  {rx:.6f}i  +  {ry:.6f}j  +  {rz:.6f}k')
                    case 14:
                        bx, by, bz = _v3('b')
                        cx, cy, cz = _v3('c')
                        result = Physics_3D.ScalarTripleProduct(ax, ay, az, bx, by, bz, cx, cy, cz)
                        bxc    = Physics_3D.CrossProductXYZ(bx, by, bz, cx, cy, cz)
                        print(f'\n  b × c  =  {bxc[0]:.4f}i  +  {bxc[1]:.4f}j  +  {bxc[2]:.4f}k')
                        print(f'  a · (b × c)  =  {result:.6f}')
                    case 15:
                        bx, by, bz = _v3('b')
                        cx, cy, cz = _v3('c')
                        result = Physics_3D.DotWithSum(ax, ay, az, bx, by, bz, cx, cy, cz)
                        bpc = Physics_3D.AddVectorsXYZ(bx, by, bz, cx, cy, cz)
                        print(f'\n  b + c  =  {bpc[0]:.4f}i  +  {bpc[1]:.4f}j  +  {bpc[2]:.4f}k')
                        print(f'  a · (b + c)  =  {result:.6f}')
                    case 16:
                        bx, by, bz = _v3('b')
                        cx, cy, cz = _v3('c')
                        result = Physics_3D.DotWithDifference(ax, ay, az, bx, by, bz, cx, cy, cz)
                        bmc = Physics_3D.SubtractVectorsXYZ(bx, by, bz, cx, cy, cz)
                        print(f'\n  b - c  =  {bmc[0]:.4f}i  +  {bmc[1]:.4f}j  +  {bmc[2]:.4f}k')
                        print(f'  a · (b - c)  =  {result:.6f}')
                    case 17:
                        bx, by, bz = _v3('b')
                        cx, cy, cz = _v3('c')
                        bpc = Physics_3D.AddVectorsXYZ(bx, by, bz, cx, cy, cz)
                        rx, ry, rz = Physics_3D.CrossWithSum(ax, ay, az, bx, by, bz, cx, cy, cz)
                        print(f'\n  b + c  =  {bpc[0]:.4f}i  +  {bpc[1]:.4f}j  +  {bpc[2]:.4f}k')
                        print(f'  a × (b + c)  =  {rx:.6f}i  +  {ry:.6f}j  +  {rz:.6f}k')
                    case _:
                        print('\n  That was not a valid option.')
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
        sec = int(input('  Select a section: '))
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
            choice = int(input('  Select a function: '))
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
        sec = int(input('  Select a section: '))
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
            choice = int(input('  Select a function: '))
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