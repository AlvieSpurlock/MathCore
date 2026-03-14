from Config import Debug
import subprocess, sys

print("  (1)  Console DebugUI")
print("  (2)  MathCore GUI  (Tkinter)")
choice = input("  Choose: ").strip()

if choice == "2":
    subprocess.run([sys.executable, "MathCoreUI.py"])
else:
    Debug.Debug()