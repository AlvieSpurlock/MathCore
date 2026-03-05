from Config import Debug  # Import Debug to access all debug UI functions

print("[====]Math Types[====]")  # Print header to identify the debug menu
print()                          # Print blank line for readability

print("(1) [==={Basic Math}===]")  # Option 1 — run BasicMathDebug
print("(2) [==={Physics 1D}===]")  # Option 2 — run Physics1DDebug
print("(3) [==={Physics 2D}===]")  # Option 3 — run Physics2DDebug
print("(4) [==={Physics 3D}===]")  # Option 4 — run Physics3DDebug
print("(5) [==={Forces 2D}===]")  # Option 3 — run Physics2DDebug
print("(6) [==={Forces 3D}===]")  # Option 4 — run Physics3DDebug
print()                          # Print blank line for readability

MathType = int(input("Which Math Type?"))  # Read the user's menu selection as an integer

match MathType:  # Switch on the user's choice — each case launches one debug UI
    case 1:
        Debug.BasicMathDebug()   # Launch Basic Math debug UI — tests add, sub, multi, div, IsEven, mod, rand
    case 2:
        Debug.Physics1DDebug()   # Launch Physics 1D debug UI — tests kinematics functions
    case 3:
        Debug.Physics2DDebug()   # Launch Physics 2D debug UI — tests 2D vector and projectile functions
    case 4:
        Debug.Physics3DDebug()   # Launch Physics 3D debug UI — tests 3D vector and projectile functions
    case 5:
        Debug.Forces2DDebug()    # Launch Forces 2D debug UI — builds a 2D object, adds forces, queries net force and energy
    case 6:
        Debug.Forces3DDebug()    # Launch Forces 3D debug UI — builds a 3D object, adds forces, queries net force and energy
    case _:
        print("Unknown")         # Notify user that their input did not match any option