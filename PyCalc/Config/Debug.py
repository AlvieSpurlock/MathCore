from MathTypes.Basic import BasicMath                      # Import BasicMath for arithmetic operations
from MathTypes.Physics import Physics_1D                   # Import Physics_1D for 1D kinematics functions
from MathTypes.Physics import Physics_2D                   # Import Physics_2D for 2D vector and projectile functions
from MathTypes.Physics import Physics_3D                   # Import Physics_3D for 3D vector and projectile functions
from MathTypes.Physics.Forces import Force2D, Forces2D     # Import Force2D and Forces2D for 2D force objects and systems
from MathTypes.Physics.Forces import Force3D, Forces3D     # Import Force3D and Forces3D for 3D force objects and systems
from MathTypes.Physics.Forces import Force, Acceleration   # Import F=ma utility functions
from MathTypes.Physics.Forces import Mass, FrictionForce   # Import mass derivation and friction
from MathTypes.Physics.Forces import NormalForce           # Import normal force utility
from MathTypes.Physics.Forces import TerminalVelocity, DragForce, IsAtTerminalVelocity  # Import terminal velocity utilities
from Config import Checks, RNG                             # Import Checks for validation and RNG for random number generation

# ============================================================
# BASIC MATH DEBUG UI
# ============================================================

# Helper — collects as many numbers as the user wants and returns them as a list
# Used by add, subtract, multiply, and divide to support unlimited variables
def CollectVariables():
    variables = []                                              # Start with an empty list of variables

    while True:                                                 # Loop until the user confirms and exits
        print()

        if variables:                                           # If there are variables to show, list them numbered
            print("  Variables so far:")
            for i, v in enumerate(variables):                  # Loop through each variable with its index
                print(f"    {i + 1}.  {v}")                    # Print each one numbered starting at 1
        else:
            print("  Variables so far: none yet")              # No variables added yet

        print()
        print("  (1)  Add a variable")
        print("  (2)  Remove a variable")
        print("  (3)  Confirm and calculate")
        print()

        action = int(input("  Enter a number to choose: "))    # Read the user's action choice

        match action:
            case 1:
                val = float(input("  Enter a value: "))        # Prompt for a new number to add to the list
                variables.append(val)                          # Add it to the variable list
                print(f"  Added {val}. You now have {len(variables)} variable(s).")

            case 2:
                if not variables:                              # Nothing to remove if the list is empty
                    print()
                    print("  There are no variables to remove yet.")
                else:
                    print()
                    print("  Which variable would you like to remove?")
                    print()
                    for i, v in enumerate(variables):          # List all current variables numbered for selection
                        print(f"    {i + 1}.  {v}")
                    print()

                    pick = int(input("  Enter the number of the variable to remove: "))  # Read the user's selection

                    if pick < 1 or pick > len(variables):      # Validate the selection is within range
                        print()
                        print(f"  That number isn't on the list. Please enter a number between 1 and {len(variables)}.")
                    else:
                        selected = variables[pick - 1]         # Get the value at the chosen position (convert 1-based to 0-based)
                        print()
                        print(f"  You selected: {selected}")
                        print()
                        print("  (1)  Yes — remove it")
                        print("  (2)  No — go back")
                        print()

                        confirm = int(input("  Enter a number to choose: "))  # Read the confirmation choice

                        if confirm == 1:                       # Only remove if the user confirmed
                            variables.pop(pick - 1)            # Remove the variable at the chosen index
                            print(f"  Removed {selected}. You now have {len(variables)} variable(s).")
                        else:
                            print("  Cancelled. Nothing was removed.")  # User backed out — leave list unchanged

            case 3:
                if len(variables) < 2:                         # Need at least two numbers to perform an operation
                    print()
                    print("  You need at least 2 variables to calculate. Please add more.")
                else:
                    return variables                           # Return the confirmed list to the caller

            case _:
                print()
                print("  That wasn't a valid option. Try again.")  # Notify user that their input did not match any option

# Console debug interface for testing a single BasicMath, Checks, or RNG function
# Prints a numbered menu, prompts the user to pick a function, then runs only that function
def BasicMathDebug():
    print()
    print("  Basic Math  ")
    print("  Pick a function to test:")
    print()
    print("  (1)  Add numbers together")
    print("  (2)  Subtract numbers in sequence")
    print("  (3)  Multiply numbers together")
    print("  (4)  Divide numbers in sequence")
    print("  (5)  Check if a number is even")
    print("  (6)  Get the remainder (modulo)")
    print("  (7)  Generate a random integer")
    print()

    choice = int(input("  Enter a number to choose: "))  # Read the user's menu selection as an integer

    match choice:
        case 1:
            print()
            print("  Add — enter as many numbers as you want.")
            variables = CollectVariables()                              # Collect unlimited variables from the user
            result = variables[0]                                       # Start with the first value
            for v in variables[1:]:                                     # Loop through every remaining value
                result = BasicMath.add(result, v)                      # Add each one to the running total → result = result + v
            print(f"\n  Adding: {' + '.join(str(v) for v in variables)}")  # Show the full expression
        case 2:
            print()
            print("  Subtract — enter as many numbers as you want. Each is subtracted from the previous.")
            variables = CollectVariables()                              # Collect unlimited variables from the user
            result = variables[0]                                       # Start with the first value
            for v in variables[1:]:                                     # Loop through every remaining value
                result = BasicMath.sub(result, v)                      # Subtract each one from the running total → result = result - v
            print(f"\n  Subtracting: {' - '.join(str(v) for v in variables)}")  # Show the full expression
        case 3:
            print()
            print("  Multiply — enter as many numbers as you want.")
            variables = CollectVariables()                              # Collect unlimited variables from the user
            result = variables[0]                                       # Start with the first value
            for v in variables[1:]:                                     # Loop through every remaining value
                result = BasicMath.multi(result, v)                    # Multiply each one into the running total → result = result * v
            print(f"\n  Multiplying: {' × '.join(str(v) for v in variables)}")  # Show the full expression
        case 4:
            print()
            print("  Divide — enter as many numbers as you want. Each divides the previous result.")
            variables = CollectVariables()                              # Collect unlimited variables from the user
            result = variables[0]                                       # Start with the first value
            for v in variables[1:]:                                     # Guard is inside BasicMath.div already
                result = BasicMath.div(result, v)                      # Divide running total by each value → result = result / v
            print(f"\n  Dividing: {' ÷ '.join(str(v) for v in variables)}")  # Show the full expression
        case 5:
            result = Checks.IsEven(int(input("  Enter a number to check: ")))                                                     # Prompt for one integer and check if even → result = True or False
        case 6:
            result = BasicMath.mod(int(input("  First number: ")), int(input("  Divide by (get remainder): ")))                   # Prompt for two integers and get remainder → result = base % var
        case 7:
            result = RNG.rand(int(input("  Minimum value: ")), int(input("  Maximum value: ")))                                   # Prompt for min and max and generate random integer → result = randint(mi, ma)
        case _:
            print()
            print("  That wasn't a valid option. Please enter a number from the menu.")  # Notify user that their input did not match any option
            return                                                                        # Exit early — no result to print

    print()
    print(f"  Result: {result}")  # Print the result of the chosen function
    print()

# ============================================================
# PHYSICS 1D DEBUG UI
# ============================================================

# Console debug interface for testing a single Physics_1D kinematics function
# Prints a numbered menu, prompts the user to pick a function, then runs only that function
def Physics1DDebug():
    print()
    print("  Physics 1D  ")
    print("  Pick a function to test:")
    print()
    print("  (1)  Distance between two points")
    print("  (2)  Elapsed time between two moments")
    print("  (3)  Velocity from distance and time")
    print("  (4)  Final velocity after acceleration")
    print("  (5)  Acceleration from two velocities")
    print("  (6)  Instantaneous acceleration")
    print("  (7)  Constant acceleration")
    print("  (8)  Displacement over time")
    print("  (9)  Position after moving")
    print()

    choice = int(input("  Enter a number to choose: "))  # Read the user's menu selection as an integer

    match choice:  # Switch on the user's choice — each case runs one function
        case 1:
            result = Physics_1D.GetDistance(float(input("  Starting position: ")), float(input("  Ending position: ")))                                                                                                    # Prompt for two locations and get distance → result = loc2 - loc1
        case 2:
            result = Physics_1D.GetTime(float(input("  Start time (s): ")), float(input("  End time (s): ")))                                                                                                              # Prompt for two timestamps and get elapsed time → result = t2 - t1
        case 3:
            result = Physics_1D.Velocity(float(input("  Distance traveled: ")), float(input("  Time taken (s): ")))                                                                                                        # Prompt for distance and time and get velocity → result = d / t
        case 4:
            result = Physics_1D.FinalVelocity(float(input("  Acceleration (m/s²): ")), float(input("  Distance (m): ")), float(input("  Time (s): ")), float(input("  Starting velocity (m/s): ")))                      # Prompt for a, d, t, v0 and get final velocity → result = v0 + a*t
        case 5:
            result = Physics_1D.Acceleration(float(input("  Starting velocity (m/s): ")), float(input("  Ending velocity (m/s): ")), float(input("  Time (s): ")))                                                        # Prompt for v1, v2, t and get acceleration → result = (v2-v1) / t
        case 6:
            result = Physics_1D.InstantAcceleration(float(input("  Starting velocity (m/s): ")), float(input("  Ending velocity (m/s): ")), float(input("  Time (s): ")))                                                 # Prompt for v1, v2, t and get instantaneous acceleration → result = (v2-v1) / t
        case 7:
            result = Physics_1D.ConstantAcceleration(float(input("  Starting velocity (m/s): ")), float(input("  Ending velocity (m/s): ")), float(input("  Time (s): ")))                                                # Prompt for v1, v2, t and get constant acceleration → result = (v2-v1) / t
        case 8:
            result = Physics_1D.GetDisplacement(float(input("  Acceleration (m/s²): ")), float(input("  Time (s): ")), float(input("  Starting velocity (m/s): ")))                                                       # Prompt for a, t, v0 and get displacement → result = v0*t + ½at²
        case 9:
            result = Physics_1D.GetPosition(float(input("  Acceleration (m/s²): ")), float(input("  Time (s): ")), float(input("  Starting velocity (m/s): ")), float(input("  Starting position (m): ")))               # Prompt for a, t, v0, x0 and get position → result = x0 + v0*t + ½at²
        case _:
            print()
            print("  That wasn't a valid option. Please enter a number from the menu.")  # Notify user that their input did not match any option
            return                                                                        # Exit early — no result to print

    print()
    print(f"  Result: {result}")  # Print the result of the chosen function
    print()

# ============================================================
# PHYSICS 2D DEBUG UI
# ============================================================

# Console debug interface for testing a single Physics_2D vector or projectile function
# Prints a numbered menu, prompts the user to pick a function, then runs only that function
def Physics2DDebug():
    print()
    print("  Physics 2D  ")
    print("  Pick a function to test:")
    print()
    print("  (1)   X component of a vector (IHat)")
    print("  (2)   Y component of a vector (JHat)")
    print("  (3)   Both X and Y components (IJ)")
    print("  (4)   Total length of a vector (Magnitude)")
    print("  (5)   Add two vectors together")
    print("  (6)   Subtract one vector from another")
    print("  (7)   Dot product of two vectors")
    print("  (8)   Cross product of two vectors")
    print("  (9)   Multiply a vector by a scalar")
    print("  (10)  Divide a vector by a scalar")
    print("  (11)  Normalize a vector (make it length 1)")
    print("  (12)  Project one vector onto another")
    print("  (13)  2D position from X and Y")
    print("  (14)  Projectile velocity at a given time")
    print("  (15)  Projectile position at a given time")
    print("  (16)  How far a projectile travels (range)")
    print("  (17)  How high a projectile gets (max height)")
    print("  (18)  Full projectile path (with air resistance)")
    print("  (19)  Full projectile path (no air resistance)")
    print()

    choice = int(input("  Enter a number to choose: "))  # Read the user's menu selection as an integer

    match choice:  # Switch on the user's choice — each case runs one function
        case 1:
            result = Physics_2D.IHat(float(input("  Total speed / magnitude: ")), float(input("  Angle (degrees): ")))                                                                                                                                     # Prompt for magnitude and angle and get X component → result = a * cos(angle)
        case 2:
            result = Physics_2D.JHat(float(input("  Total speed / magnitude: ")), float(input("  Angle (degrees): ")))                                                                                                                                     # Prompt for magnitude and angle and get Y component → result = a * sin(angle)
        case 3:
            result = Physics_2D.IJ(float(input("  Total speed / magnitude: ")), float(input("  Angle (degrees): ")))                                                                                                                                       # Prompt for magnitude and angle and get both components → result = (i, j)
        case 4:
            result = Physics_2D.VectorMagnitude(float(input("  Total speed / magnitude: ")), float(input("  Angle (degrees): ")))                                                                                                                          # Prompt for magnitude and angle and get scalar magnitude → result = sqrt(ax² + ay²)
        case 5:
            result = Physics_2D.AddVectors(float(input("  Vector A — magnitude: ")), float(input("  Vector A — angle (degrees): ")), float(input("  Vector B — magnitude: ")), float(input("  Vector B — angle (degrees): ")))                            # Prompt for two vectors and add them → result = (ax+bx, ay+by)
        case 6:
            result = Physics_2D.SubtractVectors(float(input("  Vector A — magnitude: ")), float(input("  Vector A — angle (degrees): ")), float(input("  Vector B — magnitude: ")), float(input("  Vector B — angle (degrees): ")))                       # Prompt for two vectors and subtract them → result = (ax-bx, ay-by)
        case 7:
            result = Physics_2D.DotProduct(float(input("  Vector A — magnitude: ")), float(input("  Vector A — angle (degrees): ")), float(input("  Vector B — magnitude: ")), float(input("  Vector B — angle (degrees): ")))                            # Prompt for two vectors and get dot product → result = (ax*bx) + (ay*by)
        case 8:
            result = Physics_2D.CrossProduct(float(input("  Vector A — magnitude: ")), float(input("  Vector A — angle (degrees): ")), float(input("  Vector B — magnitude: ")), float(input("  Vector B — angle (degrees): ")))                          # Prompt for two vectors and get scalar cross product → result = (ax*by) - (ay*bx)
        case 9:
            result = Physics_2D.ScalarMultiply(float(input("  Scalar value: ")), float(input("  Vector magnitude: ")), float(input("  Vector angle (degrees): ")))                                                                                        # Prompt for scalar and vector and multiply → result = (ax*c, ay*c)
        case 10:
            result = Physics_2D.ScalarDivide(float(input("  Scalar value: ")), float(input("  Vector magnitude: ")), float(input("  Vector angle (degrees): ")))                                                                                          # Prompt for scalar and vector and divide → result = (ax/c, ay/c)
        case 11:
            result = Physics_2D.NormalizeVector(float(input("  Vector magnitude: ")), float(input("  Vector angle (degrees): ")))                                                                                                                          # Prompt for magnitude and angle and get unit vector → result = (ax/||a||, ay/||a||)
        case 12:
            result = Physics_2D.VectorProjection(float(input("  Vector A — magnitude: ")), float(input("  Vector A — angle (degrees): ")), float(input("  Vector B — magnitude: ")), float(input("  Vector B — angle (degrees): ")))                      # Prompt for two vectors and get scalar projection of a onto b → result = (a⃗ · b⃗) / ||b⃗||
        case 13:
            result = Physics_2D.Position2D(float(input("  X position: ")), float(input("  Y position: ")))                                                                                                                                                # Prompt for x and y and get 2D position vector → result = (rx, ry)
        case 14:
            result = Physics_2D.ProjectileVelocity(float(input("  Launch speed (m/s): ")), float(input("  Launch angle (degrees): ")), float(input("  Time in flight (s): ")), float(input("  Mass of object (kg): ")))                                   # Prompt for a, angle, t, mass and get velocity at time t → result = (vx, vy)
        case 15:
            result = Physics_2D.ProjectilePosition(float(input("  Launch speed (m/s): ")), float(input("  Launch angle (degrees): ")), float(input("  Time in flight (s): ")), float(input("  Mass of object (kg): ")))                                   # Prompt for a, angle, t, mass and get position at time t → result = (x, y)
        case 16:
            result = Physics_2D.ProjectileRange(float(input("  Launch speed (m/s): ")), float(input("  Launch angle (degrees): ")), float(input("  Total flight time (s): ")), float(input("  Mass of object (kg): ")))                                   # Prompt for a, angle, t, mass and get horizontal range → result = x
        case 17:
            result = Physics_2D.ProjectileMaxHeight(float(input("  Launch speed (m/s): ")), float(input("  Launch angle (degrees): ")), float(input("  Mass of object (kg): ")))                                                                          # Prompt for a, angle, mass and get peak height → result = y at t_max
        case 18:
            result = Physics_2D.ProjectilePath(float(input("  Launch speed (m/s): ")), float(input("  Launch angle (degrees): ")), float(input("  Total flight time (s): ")), float(input("  Mass of object (kg): ")), int(input("  Number of steps: "))) # Prompt for a, angle, total_time, mass, steps and get full path → result = [(x,y), ...]
        case 19:
            result = Physics_2D.ProjectilePathNoAR(float(input("  Launch speed (m/s): ")), float(input("  Launch angle (degrees): ")), float(input("  Total flight time (s): ")), int(input("  Number of steps: ")))                                      # Prompt for a, angle, total_time, steps and get path without drag → result = [(x,y), ...]
        case _:
            print()
            print("  That wasn't a valid option. Please enter a number from the menu.")  # Notify user that their input did not match any option
            return                                                                        # Exit early — no result to print

    print()
    print(f"  Result: {result}")  # Print the result of the chosen function
    print()

# ============================================================
# PHYSICS 3D DEBUG UI
# ============================================================

# Console debug interface for testing a single Physics_3D vector or projectile function
# Prints a numbered menu, prompts the user to pick a function, then runs only that function
def Physics3DDebug():
    print()
    print("  Physics 3D  ")
    print("  Pick a function to test:")
    print()
    print("  (1)   X component of a vector (IHat)")
    print("  (2)   Y component of a vector (JHat)")
    print("  (3)   Z component of a vector (KHat)")
    print("  (4)   All three components (IJK)")
    print("  (5)   Total length of a vector (Magnitude)")
    print("  (6)   Add two vectors together")
    print("  (7)   Subtract one vector from another")
    print("  (8)   Dot product of two vectors")
    print("  (9)   Cross product of two vectors")
    print("  (10)  Multiply a vector by a scalar")
    print("  (11)  Divide a vector by a scalar")
    print("  (12)  Normalize a vector (make it length 1)")
    print("  (13)  Project one vector onto another")
    print("  (14)  3D position from X, Y, and Z")
    print("  (15)  Projectile velocity at a given time")
    print("  (16)  Projectile position at a given time")
    print("  (17)  How far a projectile travels (range)")
    print("  (18)  How high a projectile gets (max height)")
    print("  (19)  Drag force on a moving object")
    print("  (20)  Full projectile path (with air resistance)")
    print("  (21)  Full projectile path (no air resistance)")
    print()

    choice = int(input("  Enter a number to choose: "))  # Read the user's menu selection as an integer

    match choice:  # Switch on the user's choice — each case runs one function
        case 1:
            result = Physics_3D.IHat(float(input("  Total speed / magnitude: ")), float(input("  Angle (degrees): ")))                                                                                                                                                                               # Prompt for magnitude and angle and get X component → result = a * cos(angle)
        case 2:
            result = Physics_3D.JHat(float(input("  Total speed / magnitude: ")), float(input("  Angle (degrees): ")))                                                                                                                                                                               # Prompt for magnitude and angle and get Y component → result = a * sin(angle)
        case 3:
            result = Physics_3D.KHat(float(input("  Total speed / magnitude: ")), float(input("  Angle (degrees): ")), float(input("  Phi — elevation angle (degrees): ")))                                                                                                                         # Prompt for magnitude, angle, phi and get Z component → result = a * sin(phi) * cos(angle)
        case 4:
            result = Physics_3D.IJK(float(input("  Total speed / magnitude: ")), float(input("  Angle (degrees): ")), float(input("  Phi — elevation angle (degrees): ")))                                                                                                                          # Prompt for magnitude, angle, phi and get all three components → result = (i, j, k)
        case 5:
            result = Physics_3D.VectorMagnitude(float(input("  Total speed / magnitude: ")), float(input("  Angle (degrees): ")), float(input("  Phi — elevation angle (degrees): ")))                                                                                                              # Prompt for magnitude, angle, phi and get scalar magnitude → result = sqrt(ax² + ay² + az²)
        case 6:
            result = Physics_3D.AddVectors(float(input("  Vector A — magnitude: ")), float(input("  Vector A — angle (degrees): ")), float(input("  Vector B — magnitude: ")), float(input("  Vector B — angle (degrees): ")), float(input("  Vector A — phi (degrees): ")), float(input("  Vector B — phi (degrees): ")))        # Prompt for two vectors and add them → result = (ax+bx, ay+by, az+bz)
        case 7:
            result = Physics_3D.SubtractVectors(float(input("  Vector A — magnitude: ")), float(input("  Vector A — angle (degrees): ")), float(input("  Vector B — magnitude: ")), float(input("  Vector B — angle (degrees): ")), float(input("  Vector A — phi (degrees): ")), float(input("  Vector B — phi (degrees): ")))   # Prompt for two vectors and subtract them → result = (ax-bx, ay-by, az-bz)
        case 8:
            result = Physics_3D.DotProduct(float(input("  Vector A — magnitude: ")), float(input("  Vector A — angle (degrees): ")), float(input("  Vector B — magnitude: ")), float(input("  Vector B — angle (degrees): ")), float(input("  Vector A — phi (degrees): ")), float(input("  Vector B — phi (degrees): ")))        # Prompt for two vectors and get dot product → result = (ax*bx) + (ay*by) + (az*bz)
        case 9:
            result = Physics_3D.CrossProduct(float(input("  Vector A — magnitude: ")), float(input("  Vector A — angle (degrees): ")), float(input("  Vector B — magnitude: ")), float(input("  Vector B — angle (degrees): ")), float(input("  Vector A — phi (degrees): ")), float(input("  Vector B — phi (degrees): ")))      # Prompt for two vectors and get perpendicular vector → result = (rx, ry, rz)
        case 10:
            result = Physics_3D.ScalarMultiply(float(input("  Scalar value: ")), float(input("  Vector magnitude: ")), float(input("  Vector angle (degrees): ")), float(input("  Vector phi (degrees): ")))                                                                                        # Prompt for scalar and vector and multiply → result = (ax*c, ay*c, az*c)
        case 11:
            result = Physics_3D.ScalarDivide(float(input("  Scalar value: ")), float(input("  Vector magnitude: ")), float(input("  Vector angle (degrees): ")), float(input("  Vector phi (degrees): ")))                                                                                          # Prompt for scalar and vector and divide → result = (ax/c, ay/c, az/c)
        case 12:
            result = Physics_3D.NormalizeVector(float(input("  Vector magnitude: ")), float(input("  Vector angle (degrees): ")), float(input("  Vector phi (degrees): ")))                                                                                                                         # Prompt for magnitude, angle, phi and get unit vector → result = (ax/||a||, ay/||a||, az/||a||)
        case 13:
            result = Physics_3D.VectorProjection(float(input("  Vector A — magnitude: ")), float(input("  Vector A — angle (degrees): ")), float(input("  Vector B — magnitude: ")), float(input("  Vector B — angle (degrees): ")), float(input("  Vector A — phi (degrees): ")), float(input("  Vector B — phi (degrees): ")))  # Prompt for two vectors and get scalar projection of a onto b → result = (a⃗ · b⃗) / ||b⃗||
        case 14:
            result = Physics_3D.Position3D(float(input("  X position: ")), float(input("  Y position: ")), float(input("  Z position: ")))                                                                                                                                                          # Prompt for x, y, z and get 3D position vector → result = (rx, ry, rz)
        case 15:
            result = Physics_3D.ProjectileVelocity(float(input("  Launch speed (m/s): ")), float(input("  Launch angle (degrees): ")), float(input("  Time in flight (s): ")), float(input("  Mass of object (kg): ")))                                                                             # Prompt for a, angle, t, mass and get velocity at time t → result = (vx, vy)
        case 16:
            result = Physics_3D.ProjectilePosition(float(input("  Launch speed (m/s): ")), float(input("  Launch angle (degrees): ")), float(input("  Time in flight (s): ")), float(input("  Mass of object (kg): ")))                                                                             # Prompt for a, angle, t, mass and get position at time t → result = (x, y)
        case 17:
            result = Physics_3D.ProjectileRange(float(input("  Launch speed (m/s): ")), float(input("  Launch angle (degrees): ")), float(input("  Total flight time (s): ")), float(input("  Mass of object (kg): ")))                                                                             # Prompt for a, angle, t, mass and get horizontal range → result = x
        case 18:
            result = Physics_3D.ProjectileMaxHeight(float(input("  Launch speed (m/s): ")), float(input("  Launch angle (degrees): ")), float(input("  Mass of object (kg): ")))                                                                                                                    # Prompt for a, angle, mass and get peak height → result = y at t_max
        case 19:
            result = Physics_3D.DragForce(float(input("  Mass of object (kg): ")), float(input("  Horizontal velocity vx (m/s): ")), float(input("  Vertical velocity vy (m/s): ")))                                                                                                               # Prompt for mass, vx, vy and get drag force components → result = (fx, fy)
        case 20:
            result = Physics_3D.ProjectilePath(float(input("  Launch speed (m/s): ")), float(input("  Launch angle (degrees): ")), float(input("  Total flight time (s): ")), float(input("  Mass of object (kg): ")), int(input("  Number of steps: ")))                                          # Prompt for a, angle, total_time, mass, steps and get full path → result = [(x,y), ...]
        case 21:
            result = Physics_3D.ProjectilePathNoAR(float(input("  Launch speed (m/s): ")), float(input("  Launch angle (degrees): ")), float(input("  Total flight time (s): ")), int(input("  Number of steps: ")))                                                                                # Prompt for a, angle, total_time, steps and get path without drag → result = [(x,y), ...]
        case _:
            print()
            print("  That wasn't a valid option. Please enter a number from the menu.")  # Notify user that their input did not match any option
            return                                                                        # Exit early — no result to print

    print()
    print(f"  Result: {result}")  # Print the result of the chosen function
    print()

# ============================================================
# FORCES 2D DEBUG UI
# ============================================================

# Console debug interface for building a Forces2D object, adding Force2D objects to it, and querying results
# Walks through three steps: create the object → add forces → query the system
def Forces2DDebug():
    print()
    print("  Forces 2D  ")
    print("  This will walk you through three steps:")
    print("  Step 1 — describe your object")
    print("  Step 2 — add as many forces as you need")
    print("  Step 3 — ask a question about the system")
    print()

    # ---- Step 1: Create the physics object ----
    print("  --- Step 1: Your Object ---")
    print("  Enter the properties of the object the forces are acting on.")
    print()
    mass     = float(input("  Mass of the object (kg): "))                        # Prompt for the mass of the object — mass belongs to the object not the forces
    g        = float(input("  Gravity (m/s², press Enter for 9.8): ") or "9.8")  # Prompt for gravity — allows non-Earth scenarios
    velocity = float(input("  Current velocity (m/s): "))                         # Prompt for the current velocity — used for momentum and energy calculations
    height   = float(input("  Current height above ground (m): "))                # Prompt for the current height — used for potential energy calculations

    obj          = Forces2D(mass, g)  # Create the physics object with mass and gravity → normal force derived automatically
    obj.velocity = velocity           # Set the object's current velocity → stored on object for KE and momentum
    obj.height   = height             # Set the object's current height → stored on object for PE

    print()
    print(f"  Object ready — {mass} kg, gravity {obj.g} m/s², normal force {obj.normal:.3f} N")
    print()

    # ---- Optional incline setup ----
    print("  Is the object on an inclined surface?")
    print("  (1)  Yes — set the incline angle")
    print("  (2)  No — flat surface (normal force already set)")
    print()

    incline_choice = int(input("  Enter a number to choose: "))  # Read the incline choice

    if incline_choice == 1:                                              # If the user wants an inclined surface...
        angle = float(input("  Incline angle (degrees): "))             # Prompt for the slope angle
        obj.SetIncline(angle)                                            # Recalculate normal force for the slope → Fn = mg*cos(θ)
        print()
        print(f"  Incline set to {angle}° — normal force updated to {obj.normal:.3f} N")
    print()

    # ---- Step 2: Build and add Force2D objects ----
    print("  --- Step 2: Add Forces ---")
    print("  Add one force at a time. Choose how you want to describe each force.")
    print()

    # ---- Optional gravity setup ----
    print("  Should gravity act on this object as a downward force?")
    print("  (1)  Yes — add gravity to the force list  (Fg = mg downward)")
    print("  (2)  No — I will manage forces manually")
    print()

    gravity_choice = int(input("  Enter a number to choose: "))  # Read the gravity choice

    if gravity_choice == 1:                                              # If the user wants gravity applied...
        obj.ApplyGravity()                                               # Add downward force Fg = mg → inserted into force list
        force_count = 1                                                  # Count gravity as the first force
        print()
        print(f"  Gravity applied — {obj.mass * obj.g:.3f} N downward added to force list.")
    else:
        force_count = 0     # No gravity force — start counter at zero
    print()

    adding = True       # Flag to keep the force-adding loop running
    while adding:       # Loop until the user decides to stop adding forces
        print(f"  Force #{force_count + 1} — how would you like to enter it?")
        print("  (1)  By X and Y components  (e.g. 10N right, 5N up)")
        print("  (2)  By total strength and direction  (e.g. 20N at 45 degrees)")
        print("  (3)  I'm done adding forces")
        print()

        force_choice = int(input("  Enter a number to choose: "))  # Read the force input method choice

        match force_choice:  # Switch on how the user wants to define this force
            case 1:
                x     = float(input("  Force in the X direction (N, negative = left): "))    # Prompt for X component of the force in Newtons
                y     = float(input("  Force in the Y direction (N, negative = down): "))    # Prompt for Y component of the force in Newtons
                force = Force2D(x, y)                                                         # Create Force2D from components — magnitude and angle derived automatically
                obj.forces.append(force)                                                      # Add the constructed Force2D to the object's force list
                force_count += 1                                                              # Increment the force counter
                print()
                print(f"  Added! Strength = {force.magnitude:.3f} N, Direction = {force.angle:.1f} degrees")
                print()
            case 2:
                magnitude = float(input("  Total force strength (N): "))                     # Prompt for magnitude of the force in Newtons
                angle     = float(input("  Direction of force (degrees, 0 = right): "))      # Prompt for direction angle of the force in degrees
                force     = Force2D(0, 0, angle, magnitude)                                  # Create Force2D from magnitude and angle — x and y derived automatically
                obj.forces.append(force)                                                      # Add the constructed Force2D to the object's force list
                force_count += 1                                                              # Increment the force counter
                print()
                print(f"  Added! {magnitude} N at {angle} degrees")
                print()
            case 3:
                adding = False  # Exit the adding loop — user is done adding forces
            case _:
                print()
                print("  That wasn't a valid option. Try again.")  # Notify user that their input did not match any option
                print()

    print(f"  {force_count} force(s) loaded. Ready to calculate.")
    print()

    # ---- Step 3: Query the system ----
    print("  --- Step 3: What do you want to know? ---")
    print()
    print("  (1)   Net force on the object")
    print("  (2)   Acceleration caused by the net force")
    print("  (3)   Momentum of the object")
    print("  (4)   Kinetic energy  (energy from motion)")
    print("  (5)   Potential energy  (energy from height)")
    print("  (6)   Total mechanical energy  (KE + PE)")
    print("  (7)   Impulse delivered over a time interval")
    print("  (8)   Update the object's velocity over a time step")
    print("  (9)   Normal force")
    print("  (10)  Is the object in static equilibrium?  (ΣF = 0, v = 0)")
    print("  (11)  Is the object in dynamic equilibrium?  (ΣF = 0, v ≠ 0)")
    print("  (12)  Terminal velocity of this object")
    print("  (13)  Drag force at current velocity")
    print("  (14)  Has the object reached terminal velocity?")
    print()

    query = int(input("  Enter a number to choose: "))  # Read the query choice

    match query:  # Switch on the user's query — each case calls one method on the object
        case 1:
            net = obj.NetForce()                         # Calculate net force → sum all forces into single resultant Force2D
            print()
            print(f"  Net Force:")
            print(f"    X component    : {net.x:.3f} N")
            print(f"    Y component    : {net.y:.3f} N")
            print(f"    Total strength : {net.magnitude:.3f} N")
            print(f"    Direction      : {net.angle:.1f} degrees")
        case 2:
            result = obj.NetAcceleration()               # Calculate a = F_net / m using object mass
            print()
            print(f"  Net Acceleration: {result:.3f} m/s²")
        case 3:
            result = obj.NetMomentum()                   # Calculate p = mv using object mass and current velocity
            print()
            print(f"  Momentum: {result:.3f} kg·m/s")
        case 4:
            result = obj.NetKineticEnergy()              # Calculate KE = ½mv² using object mass and current velocity
            print()
            print(f"  Kinetic Energy: {result:.3f} J")
        case 5:
            result = obj.NetPotentialEnergy()            # Calculate PE = mgh using object mass, height, and stored gravity
            print()
            print(f"  Potential Energy: {result:.3f} J")
        case 6:
            result = obj.NetMechanicalEnergy()           # Calculate ME = KE + PE using object mass, velocity, height, and gravity
            print()
            print(f"  Total Mechanical Energy: {result:.3f} J")
        case 7:
            print()
            time   = float(input("  Over how many seconds? "))   # Prompt for time interval to apply impulse over
            result = obj.NetImpulse(time)                        # Calculate J = F_net * t
            print()
            print(f"  Impulse over {time}s: {result:.3f} N·s")
        case 8:
            print()
            time = float(input("  Advance by how many seconds? "))  # Prompt for time step to advance velocity by
            obj.UpdateVelocity(time)                                 # Advance velocity → v = v + at using net acceleration
            print()
            print(f"  Velocity is now: {obj.velocity:.3f} m/s")
        case 9:
            print()
            print(f"  Normal Force: {obj.normal:.3f} N")          # Print the stored normal force — Fn = mg or mg*cos(θ) on incline
        case 10:
            result = obj.IsStaticEquilibrium()           # Check ΣF = 0 and v = 0 → True if fully at rest with no net force
            print()
            if result:
                print("  Yes — the object is in static equilibrium. Net force is zero and it is not moving.")
            else:
                net = obj.NetForce()
                print(f"  No — net force is {net.magnitude:.3f} N, velocity is {obj.velocity:.3f} m/s.")
        case 11:
            result = obj.IsDynamicEquilibrium()          # Check ΣF = 0 and v ≠ 0 → True if moving at constant velocity
            print()
            if result:
                print("  Yes — the object is in dynamic equilibrium. Net force is zero and it is moving at constant velocity.")
            else:
                net = obj.NetForce()
                print(f"  No — net force is {net.magnitude:.3f} N, velocity is {obj.velocity:.3f} m/s.")
        case 12:
            print()
            area             = float(input("  Cross-sectional area of the object (m²): "))       # Prompt for area — affects how much drag acts on the object
            drag_coefficient = float(input("  Drag coefficient (e.g. 0.47 for a sphere): "))     # Prompt for Cd — dimensionless shape factor
            fluid_density    = float(input("  Fluid density (kg/m³, press Enter for 1.225): ") or "1.225")  # Prompt for fluid density — default is air at sea level
            result = TerminalVelocity(obj.mass, area, drag_coefficient, fluid_density, obj.g)    # Calculate v_t = sqrt(2mg / ρACd)
            print()
            print(f"  Terminal Velocity: {result:.3f} m/s")
        case 13:
            print()
            area             = float(input("  Cross-sectional area of the object (m²): "))       # Prompt for area
            drag_coefficient = float(input("  Drag coefficient (e.g. 0.47 for a sphere): "))     # Prompt for Cd
            fluid_density    = float(input("  Fluid density (kg/m³, press Enter for 1.225): ") or "1.225")  # Prompt for fluid density
            result = DragForce(obj.velocity, area, drag_coefficient, fluid_density)              # Calculate Fd = ½ρv²ACd at current velocity
            print()
            print(f"  Drag Force at {obj.velocity:.3f} m/s: {result:.3f} N")
        case 14:
            print()
            area             = float(input("  Cross-sectional area of the object (m²): "))       # Prompt for area
            drag_coefficient = float(input("  Drag coefficient (e.g. 0.47 for a sphere): "))     # Prompt for Cd
            fluid_density    = float(input("  Fluid density (kg/m³, press Enter for 1.225): ") or "1.225")  # Prompt for fluid density
            result = IsAtTerminalVelocity(obj.velocity, obj.mass, area, drag_coefficient, fluid_density, obj.g)  # Check if v ≈ v_t within 1%
            vt     = TerminalVelocity(obj.mass, area, drag_coefficient, fluid_density, obj.g)    # Also show the terminal velocity for reference
            print()
            if result:
                print(f"  Yes — the object is at terminal velocity ({vt:.3f} m/s).")
            else:
                print(f"  No — current velocity is {obj.velocity:.3f} m/s, terminal velocity is {vt:.3f} m/s.")
        case _:
            print()
            print("  That wasn't a valid option. Please enter a number from the menu.")  # Notify user that their input did not match any option

    print()

# ============================================================
# FORCES 3D DEBUG UI
# ============================================================

# Console debug interface for building a Forces3D object, adding Force3D objects to it, and querying results
# Walks through three steps: create the object → add forces → query the system
def Forces3DDebug():
    print()
    print("  Forces 3D  ")
    print("  This will walk you through three steps:")
    print("  Step 1 — describe your object")
    print("  Step 2 — add as many forces as you need")
    print("  Step 3 — ask a question about the system")
    print()

    # ---- Step 1: Create the physics object ----
    print("  --- Step 1: Your Object ---")
    print("  Enter the properties of the object the forces are acting on.")
    print()
    mass     = float(input("  Mass of the object (kg): "))                        # Prompt for the mass of the object — mass belongs to the object not the forces
    g        = float(input("  Gravity (m/s², press Enter for 9.8): ") or "9.8")  # Prompt for gravity — allows non-Earth scenarios
    velocity = float(input("  Current velocity (m/s): "))                         # Prompt for the current velocity — used for momentum and energy calculations
    height   = float(input("  Current height above ground (m): "))                # Prompt for the current height — used for potential energy calculations

    obj          = Forces3D(mass, g)  # Create the physics object with mass and gravity → normal force derived automatically
    obj.velocity = velocity           # Set the object's current velocity → stored on object for KE and momentum
    obj.height   = height             # Set the object's current height → stored on object for PE

    print()
    print(f"  Object ready — {mass} kg, gravity {obj.g} m/s², normal force {obj.normal:.3f} N")
    print()

    # ---- Optional incline setup ----
    print("  Is the object on an inclined surface?")
    print("  (1)  Yes — set the incline angle")
    print("  (2)  No — flat surface (normal force already set)")
    print()

    incline_choice = int(input("  Enter a number to choose: "))  # Read the incline choice

    if incline_choice == 1:                                              # If the user wants an inclined surface...
        angle = float(input("  Incline angle (degrees): "))             # Prompt for the slope angle
        obj.SetIncline(angle)                                            # Recalculate normal force for the slope → Fn = mg*cos(θ)
        print()
        print(f"  Incline set to {angle}° — normal force updated to {obj.normal:.3f} N")
    print()

    # ---- Step 2: Build and add Force3D objects ----
    print("  --- Step 2: Add Forces ---")
    print("  Add one force at a time. Choose how you want to describe each force.")
    print()

    # ---- Optional gravity setup ----
    print("  Should gravity act on this object as a downward force?")
    print("  (1)  Yes — add gravity to the force list  (Fg = mg downward)")
    print("  (2)  No — I will manage forces manually")
    print()

    gravity_choice = int(input("  Enter a number to choose: "))  # Read the gravity choice

    if gravity_choice == 1:                                              # If the user wants gravity applied...
        obj.ApplyGravity()                                               # Add downward force Fg = mg → inserted into force list
        force_count = 1                                                  # Count gravity as the first force
        print()
        print(f"  Gravity applied — {obj.mass * obj.g:.3f} N downward added to force list.")
    else:
        force_count = 0     # No gravity force — start counter at zero
    print()

    adding = True       # Flag to keep the force-adding loop running
    while adding:       # Loop until the user decides to stop adding forces
        print(f"  Force #{force_count + 1} — how would you like to enter it?")
        print("  (1)  By X, Y, and Z components")
        print("  (2)  By total strength, horizontal direction, and vertical angle")
        print("  (3)  I'm done adding forces")
        print()

        force_choice = int(input("  Enter a number to choose: "))  # Read the force input method choice

        match force_choice:  # Switch on how the user wants to define this force
            case 1:
                x     = float(input("  Force in the X direction (N): "))                                    # Prompt for X component of the force in Newtons
                y     = float(input("  Force in the Y direction (N): "))                                    # Prompt for Y component of the force in Newtons
                z     = float(input("  Force in the Z direction (N): "))                                    # Prompt for Z component of the force in Newtons
                force = Force3D(x, y, z)                                                                    # Create Force3D from components — magnitude, angle, phi derived automatically
                obj.forces.append(force)                                                                    # Add the constructed Force3D to the object's force list
                force_count += 1                                                                            # Increment the force counter
                print()
                print(f"  Added! Strength = {force.magnitude:.3f} N, Angle = {force.angle:.1f}°, Phi = {force.phi:.1f}°")
                print()
            case 2:
                magnitude = float(input("  Total force strength (N): "))                                    # Prompt for magnitude of the force in Newtons
                angle     = float(input("  Horizontal direction (degrees, 0 = forward): "))                 # Prompt for azimuth angle of the force in degrees
                phi       = float(input("  Vertical angle (degrees, 0 = flat, 90 = straight up): "))        # Prompt for elevation angle of the force in degrees
                force     = Force3D(0, 0, 0, angle, phi, magnitude)                                         # Create Force3D from magnitude and angles — components derived automatically
                obj.forces.append(force)                                                                    # Add the constructed Force3D to the object's force list
                force_count += 1                                                                            # Increment the force counter
                print()
                print(f"  Added! {magnitude} N at {angle} degrees horizontal, {phi} degrees vertical")
                print()
            case 3:
                adding = False  # Exit the adding loop — user is done adding forces
            case _:
                print()
                print("  That wasn't a valid option. Try again.")  # Notify user that their input did not match any option
                print()

    print(f"  {force_count} force(s) loaded. Ready to calculate.")
    print()

    # ---- Step 3: Query the system ----
    print("  --- Step 3: What do you want to know? ---")
    print()
    print("  (1)   Net force on the object")
    print("  (2)   Acceleration caused by the net force")
    print("  (3)   Momentum of the object")
    print("  (4)   Kinetic energy  (energy from motion)")
    print("  (5)   Potential energy  (energy from height)")
    print("  (6)   Total mechanical energy  (KE + PE)")
    print("  (7)   Impulse delivered over a time interval")
    print("  (8)   Update the object's velocity over a time step")
    print("  (9)   Normal force")
    print("  (10)  Is the object in static equilibrium?  (ΣF = 0, v = 0)")
    print("  (11)  Is the object in dynamic equilibrium?  (ΣF = 0, v ≠ 0)")
    print("  (12)  Terminal velocity of this object")
    print("  (13)  Drag force at current velocity")
    print("  (14)  Has the object reached terminal velocity?")
    print()

    query = int(input("  Enter a number to choose: "))  # Read the query choice

    match query:  # Switch on the user's query — each case calls one method on the object
        case 1:
            net = obj.NetForce()                         # Calculate net force → sum all forces into single resultant Force3D
            print()
            print(f"  Net Force:")
            print(f"    X component    : {net.x:.3f} N")
            print(f"    Y component    : {net.y:.3f} N")
            print(f"    Z component    : {net.z:.3f} N")
            print(f"    Total strength : {net.magnitude:.3f} N")
            print(f"    Horizontal dir : {net.angle:.1f} degrees")
            print(f"    Vertical angle : {net.phi:.1f} degrees")
        case 2:
            result = obj.NetAcceleration()               # Calculate a = F_net / m using object mass
            print()
            print(f"  Net Acceleration: {result:.3f} m/s²")
        case 3:
            result = obj.NetMomentum()                   # Calculate p = mv using object mass and current velocity
            print()
            print(f"  Momentum: {result:.3f} kg·m/s")
        case 4:
            result = obj.NetKineticEnergy()              # Calculate KE = ½mv² using object mass and current velocity
            print()
            print(f"  Kinetic Energy: {result:.3f} J")
        case 5:
            result = obj.NetPotentialEnergy()            # Calculate PE = mgh using object mass, height, and stored gravity
            print()
            print(f"  Potential Energy: {result:.3f} J")
        case 6:
            result = obj.NetMechanicalEnergy()           # Calculate ME = KE + PE using object mass, velocity, height, and gravity
            print()
            print(f"  Total Mechanical Energy: {result:.3f} J")
        case 7:
            print()
            time   = float(input("  Over how many seconds? "))   # Prompt for time interval to apply impulse over
            result = obj.NetImpulse(time)                        # Calculate J = F_net * t
            print()
            print(f"  Impulse over {time}s: {result:.3f} N·s")
        case 8:
            print()
            time = float(input("  Advance by how many seconds? "))  # Prompt for time step to advance velocity by
            obj.UpdateVelocity(time)                                 # Advance velocity → v = v + at using net acceleration
            print()
            print(f"  Velocity is now: {obj.velocity:.3f} m/s")
        case 9:
            print()
            print(f"  Normal Force: {obj.normal:.3f} N")          # Print the stored normal force — Fn = mg or mg*cos(θ) on incline
        case 10:
            result = obj.IsStaticEquilibrium()           # Check ΣF = 0 and v = 0 → True if fully at rest with no net force
            print()
            if result:
                print("  Yes — the object is in static equilibrium. Net force is zero and it is not moving.")
            else:
                net = obj.NetForce()
                print(f"  No — net force is {net.magnitude:.3f} N, velocity is {obj.velocity:.3f} m/s.")
        case 11:
            result = obj.IsDynamicEquilibrium()          # Check ΣF = 0 and v ≠ 0 → True if moving at constant velocity
            print()
            if result:
                print("  Yes — the object is in dynamic equilibrium. Net force is zero and it is moving at constant velocity.")
            else:
                net = obj.NetForce()
                print(f"  No — net force is {net.magnitude:.3f} N, velocity is {obj.velocity:.3f} m/s.")
        case 12:
            print()
            area             = float(input("  Cross-sectional area of the object (m²): "))       # Prompt for area — affects how much drag acts on the object
            drag_coefficient = float(input("  Drag coefficient (e.g. 0.47 for a sphere): "))     # Prompt for Cd — dimensionless shape factor
            fluid_density    = float(input("  Fluid density (kg/m³, press Enter for 1.225): ") or "1.225")  # Prompt for fluid density — default is air at sea level
            result = TerminalVelocity(obj.mass, area, drag_coefficient, fluid_density, obj.g)    # Calculate v_t = sqrt(2mg / ρACd)
            print()
            print(f"  Terminal Velocity: {result:.3f} m/s")
        case 13:
            print()
            area             = float(input("  Cross-sectional area of the object (m²): "))       # Prompt for area
            drag_coefficient = float(input("  Drag coefficient (e.g. 0.47 for a sphere): "))     # Prompt for Cd
            fluid_density    = float(input("  Fluid density (kg/m³, press Enter for 1.225): ") or "1.225")  # Prompt for fluid density
            result = DragForce(obj.velocity, area, drag_coefficient, fluid_density)              # Calculate Fd = ½ρv²ACd at current velocity
            print()
            print(f"  Drag Force at {obj.velocity:.3f} m/s: {result:.3f} N")
        case 14:
            print()
            area             = float(input("  Cross-sectional area of the object (m²): "))       # Prompt for area
            drag_coefficient = float(input("  Drag coefficient (e.g. 0.47 for a sphere): "))     # Prompt for Cd
            fluid_density    = float(input("  Fluid density (kg/m³, press Enter for 1.225): ") or "1.225")  # Prompt for fluid density
            result = IsAtTerminalVelocity(obj.velocity, obj.mass, area, drag_coefficient, fluid_density, obj.g)  # Check if v ≈ v_t within 1%
            vt     = TerminalVelocity(obj.mass, area, drag_coefficient, fluid_density, obj.g)    # Also show the terminal velocity for reference
            print()
            if result:
                print(f"  Yes — the object is at terminal velocity ({vt:.3f} m/s).")
            else:
                print(f"  No — current velocity is {obj.velocity:.3f} m/s, terminal velocity is {vt:.3f} m/s.")
        case _:
            print()
            print("  That wasn't a valid option. Please enter a number from the menu.")  # Notify user that their input did not match any option

    print()