import math  # Import math for sqrt, pi, sin, cos, tan, asin, acos, atan2

# ============================================================
# POINTS AND DISTANCE
# ============================================================

# Formula: d = sqrt((x2-x1)² + (y2-y1)²)
# Returns the straight-line distance between two 2D points
def Distance2D(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)     # Sum squared differences then take root → complete d = sqrt(Δx² + Δy²)

# Formula: d = sqrt((x2-x1)² + (y2-y1)² + (z2-z1)²)
# Returns the straight-line distance between two 3D points
def Distance3D(x1, y1, z1, x2, y2, z2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)  # Sum all three squared differences then take root → complete d = sqrt(Δx²+Δy²+Δz²)

# Formula: midpoint = ((x1+x2)/2, (y1+y2)/2)
# Returns the midpoint between two 2D points as a tuple
def Midpoint2D(x1, y1, x2, y2):
    return ((x1 + x2) / 2, (y1 + y2) / 2)                 # Average each coordinate → complete midpoint = ((x1+x2)/2, (y1+y2)/2)

# Formula: midpoint = ((x1+x2)/2, (y1+y2)/2, (z1+z2)/2)
# Returns the midpoint between two 3D points as a tuple
def Midpoint3D(x1, y1, z1, x2, y2, z2):
    return ((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2) # Average each coordinate → complete 3D midpoint

# Formula: Manhattan distance = |x2-x1| + |y2-y1|
# Returns the Manhattan (taxicab) distance — sum of absolute differences along each axis
def ManhattanDistance(x1, y1, x2, y2):
    return abs(x2 - x1) + abs(y2 - y1)                     # Sum absolute differences along each axis → complete |Δx| + |Δy|

# ============================================================
# ANGLES
# ============================================================

# Formula: degrees = radians * (180 / π)
# Returns an angle converted from radians to degrees
def ToDegrees(radians):
    return math.degrees(radians)                            # Apply standard radian to degree conversion → complete degrees = rad * 180/π

# Formula: radians = degrees * (π / 180)
# Returns an angle converted from degrees to radians
def ToRadians(degrees):
    return math.radians(degrees)                            # Apply standard degree to radian conversion → complete radians = deg * π/180

# Formula: supplementary = 180 - angle
# Returns the supplement of an angle in degrees — the angle that adds to 180°
def SupplementaryAngle(degrees):
    return 180 - degrees                                    # Subtract from 180 → complete supplement = 180 - θ

# Formula: complementary = 90 - angle
# Returns the complement of an angle in degrees — the angle that adds to 90°
def ComplementaryAngle(degrees):
    return 90 - degrees                                     # Subtract from 90 → complete complement = 90 - θ

# Formula: checks if three angles sum to 180
# Returns True if the three angles could form a valid triangle
def IsValidTriangleAngles(a, b, c, tolerance = 1e-9):
    return abs(a + b + c - 180) < tolerance                 # Check if angles sum to 180 within tolerance → True if valid triangle

# ============================================================
# TRIANGLES
# ============================================================

# Formula: A = ½ * base * height
# Returns the area of a triangle given base and height
def TriangleArea(base, height):
    return 0.5 * base * height                              # Multiply ½ by base and height → complete A = ½bh

# Formula: Heron's formula — A = sqrt(s(s-a)(s-b)(s-c))  where s = (a+b+c)/2
# Returns the area of a triangle given all three side lengths
def TriangleAreaHeron(a, b, c):
    s = (a + b + c) / 2                                     # Calculate semi-perimeter → s = (a+b+c)/2
    return math.sqrt(s * (s - a) * (s - b) * (s - c))      # Apply Heron's formula → complete A = sqrt(s(s-a)(s-b)(s-c))

# Formula: P = a + b + c
# Returns the perimeter of a triangle — sum of all three sides
def TrianglePerimeter(a, b, c):
    return a + b + c                                        # Sum all three sides → complete P = a + b + c

# Formula: c = sqrt(a² + b²)
# Returns the hypotenuse of a right triangle given the two legs
def Hypotenuse(a, b):
    return math.sqrt(a ** 2 + b ** 2)                       # Sum squares of both legs then take root → complete c = sqrt(a²+b²)

# Formula: a = sqrt(c² - b²)
# Returns one leg of a right triangle given the hypotenuse and the other leg
# Returns 0 if c < b to avoid a negative under the square root
def TriangleLeg(c, b):
    if c < b:                                               # Guard — hypotenuse must be longer than any leg
        return 0                                            # Return 0 safely — invalid triangle
    return math.sqrt(c ** 2 - b ** 2)                       # Subtract b² from c² then take root → complete a = sqrt(c²-b²)

# Formula: checks if a² + b² == c²
# Returns True if the three sides form a valid right triangle
def IsPythagorean(a, b, c, tolerance = 1e-9):
    sides = sorted([a, b, c])                               # Sort so the largest side is treated as hypotenuse
    return abs(sides[0] ** 2 + sides[1] ** 2 - sides[2] ** 2) < tolerance  # Check if a²+b²=c² within tolerance

# Formula: Law of Cosines — c² = a² + b² - 2ab*cos(C)
# Returns the length of the third side given two sides and the included angle in degrees
def LawOfCosinesSide(a, b, angle_C_degrees):
    C = math.radians(angle_C_degrees)                       # Convert angle to radians for trig functions
    return math.sqrt(a ** 2 + b ** 2 - 2 * a * b * math.cos(C))  # Apply law of cosines → complete c = sqrt(a²+b²-2ab*cos(C))

# Formula: Law of Cosines — C = acos((a² + b² - c²) / 2ab)
# Returns the angle in degrees opposite side c given all three side lengths
# Returns 0 if a or b is zero to avoid division by zero
def LawOfCosinesAngle(a, b, c):
    if a == 0 or b == 0:                                    # Guard against division by zero — sides cannot be zero
        return 0                                            # Return 0 safely
    cos_C = (a ** 2 + b ** 2 - c ** 2) / (2 * a * b)      # Compute cosine of angle C → (a²+b²-c²)/2ab
    cos_C = max(-1, min(1, cos_C))                          # Clamp to [-1, 1] to avoid floating point domain errors in acos
    return math.degrees(math.acos(cos_C))                   # Take inverse cosine and convert to degrees → complete C = acos(...)

# Formula: Law of Sines — a/sin(A) = b/sin(B)
# Returns side b given side a, angle A, and angle B (all angles in degrees)
# Returns 0 if sin(A) is zero to avoid division by zero
def LawOfSinesSide(a, angle_A_degrees, angle_B_degrees):
    sin_A = math.sin(math.radians(angle_A_degrees))         # Convert A to radians and take sine
    if sin_A == 0:                                          # Guard against division by zero
        return 0                                            # Return 0 safely
    sin_B = math.sin(math.radians(angle_B_degrees))         # Convert B to radians and take sine
    return (a * sin_B) / sin_A                              # Multiply a by sin(B) then divide by sin(A) → complete b = a*sin(B)/sin(A)

# Formula: Law of Sines — A = asin(a * sin(B) / b)
# Returns angle A in degrees given side a, side b, and angle B in degrees
# Returns 0 if b is zero to avoid division by zero
def LawOfSinesAngle(a, b, angle_B_degrees):
    if b == 0:                                              # Guard against division by zero
        return 0                                            # Return 0 safely
    sin_B = math.sin(math.radians(angle_B_degrees))         # Convert B to radians and take sine
    ratio = a * sin_B / b                                   # Calculate sin(A) → a*sin(B)/b
    ratio = max(-1, min(1, ratio))                          # Clamp to [-1, 1] to avoid domain errors in asin
    return math.degrees(math.asin(ratio))                   # Take inverse sine and convert to degrees → complete A = asin(...)

# ============================================================
# QUADRILATERALS
# ============================================================

# Formula: A = length * width
# Returns the area of a rectangle
def RectangleArea(length, width):
    return length * width                                   # Multiply length by width → complete A = l*w

# Formula: P = 2 * (length + width)
# Returns the perimeter of a rectangle
def RectanglePerimeter(length, width):
    return 2 * (length + width)                             # Double the sum of both dimensions → complete P = 2(l+w)

# Formula: A = side²
# Returns the area of a square
def SquareArea(side):
    return side ** 2                                        # Square the side length → complete A = s²

# Formula: P = 4 * side
# Returns the perimeter of a square
def SquarePerimeter(side):
    return 4 * side                                         # Multiply side by 4 → complete P = 4s

# Formula: d = side * sqrt(2)
# Returns the diagonal of a square
def SquareDiagonal(side):
    return side * math.sqrt(2)                              # Multiply side by sqrt(2) → complete d = s*sqrt(2)

# Formula: A = base * height
# Returns the area of a parallelogram
def ParallelogramArea(base, height):
    return base * height                                    # Multiply base by perpendicular height → complete A = bh

# Formula: A = ½ * (b1 + b2) * height
# Returns the area of a trapezoid given both parallel bases and the height
def TrapezoidArea(b1, b2, height):
    return 0.5 * (b1 + b2) * height                        # Average the bases then multiply by height → complete A = ½(b1+b2)*h

# Formula: A = ½ * d1 * d2
# Returns the area of a rhombus given its two diagonals
def RhombusArea(d1, d2):
    return 0.5 * d1 * d2                                    # Multiply diagonals and halve → complete A = ½*d1*d2

# ============================================================
# CIRCLES
# ============================================================

# Formula: A = π * r²
# Returns the area of a circle
def CircleArea(r):
    return math.pi * r ** 2                                 # Multiply π by radius squared → complete A = πr²

# Formula: C = 2 * π * r
# Returns the circumference of a circle
def CircleCircumference(r):
    return 2 * math.pi * r                                  # Multiply 2π by radius → complete C = 2πr

# Formula: d = 2 * r
# Returns the diameter of a circle given its radius
def CircleDiameter(r):
    return 2 * r                                            # Double the radius → complete d = 2r

# Formula: r = d / 2
# Returns the radius of a circle given its diameter
def CircleRadius(d):
    return d / 2                                            # Halve the diameter → complete r = d/2

# Formula: arc_length = r * θ  (θ in radians)
# Returns the length of a circular arc given radius and central angle in degrees
def ArcLength(r, angle_degrees):
    angle_radians = math.radians(angle_degrees)             # Convert central angle to radians
    return r * angle_radians                                # Multiply radius by angle in radians → complete arc = rθ

# Formula: sector_area = ½ * r² * θ  (θ in radians)
# Returns the area of a circular sector (pie slice) given radius and central angle in degrees
def SectorArea(r, angle_degrees):
    angle_radians = math.radians(angle_degrees)             # Convert central angle to radians
    return 0.5 * r ** 2 * angle_radians                    # Multiply ½r² by angle in radians → complete A = ½r²θ

# Formula: chord_length = 2 * r * sin(θ/2)  (θ in radians)
# Returns the length of a chord given the radius and the central angle it subtends in degrees
def ChordLength(r, angle_degrees):
    angle_radians = math.radians(angle_degrees)             # Convert angle to radians
    return 2 * r * math.sin(angle_radians / 2)             # Multiply 2r by sin of half the angle → complete chord = 2r*sin(θ/2)

# ============================================================
# POLYGONS
# ============================================================

# Formula: sum of interior angles = (n - 2) * 180
# Returns the sum of all interior angles of a polygon with n sides
def PolygonInteriorAngleSum(n):
    return (n - 2) * 180                                    # Multiply (n-2) by 180 → complete sum = (n-2)*180

# Formula: interior angle = (n - 2) * 180 / n
# Returns each interior angle of a regular polygon with n sides
# Returns 0 if n is zero to avoid division by zero
def RegularPolygonInteriorAngle(n):
    if n == 0:                                              # Guard against division by zero
        return 0                                            # Return 0 safely
    return (n - 2) * 180 / n                                # Divide interior angle sum by number of sides → complete angle = (n-2)*180/n

# Formula: exterior angle = 360 / n
# Returns each exterior angle of a regular polygon with n sides
# Returns 0 if n is zero to avoid division by zero
def RegularPolygonExteriorAngle(n):
    if n == 0:                                              # Guard against division by zero
        return 0                                            # Return 0 safely
    return 360 / n                                          # Divide full rotation by number of sides → complete exterior = 360/n

# Formula: A = (n * s²) / (4 * tan(π/n))
# Returns the area of a regular polygon with n sides each of length s
# Returns 0 if n is zero to avoid division by zero
def RegularPolygonArea(n, s):
    if n == 0:                                              # Guard against division by zero
        return 0                                            # Return 0 safely
    return (n * s ** 2) / (4 * math.tan(math.pi / n))      # Apply regular polygon area formula → complete A = ns²/(4*tan(π/n))

# Formula: P = n * s
# Returns the perimeter of a regular polygon with n sides each of length s
def RegularPolygonPerimeter(n, s):
    return n * s                                            # Multiply number of sides by side length → complete P = n*s

# Formula: diagonals = n * (n - 3) / 2
# Returns the number of diagonals in a polygon with n sides
def PolygonDiagonals(n):
    return n * (n - 3) // 2                                 # Apply diagonal count formula → complete diagonals = n(n-3)/2

# ============================================================
# 3D SOLIDS — SURFACE AREA
# ============================================================

# Formula: SA = 2(lw + lh + wh)
# Returns the surface area of a rectangular prism (box)
def BoxSurfaceArea(l, w, h):
    return 2 * (l * w + l * h + w * h)                     # Sum all three face pairs and double → complete SA = 2(lw+lh+wh)

# Formula: SA = 6 * s²
# Returns the surface area of a cube
def CubeSurfaceArea(s):
    return 6 * s ** 2                                       # Multiply 6 faces by side squared → complete SA = 6s²

# Formula: SA = 2πr² + 2πrh
# Returns the surface area of a cylinder given radius and height
def CylinderSurfaceArea(r, h):
    return 2 * math.pi * r ** 2 + 2 * math.pi * r * h      # Sum top/bottom circles and lateral surface → complete SA = 2πr²+2πrh

# Formula: SA = πr² + πrl  where l = slant height = sqrt(r² + h²)
# Returns the surface area of a cone given radius and height
def ConeSurfaceArea(r, h):
    l = math.sqrt(r ** 2 + h ** 2)                         # Calculate slant height → l = sqrt(r²+h²)
    return math.pi * r ** 2 + math.pi * r * l              # Sum base circle and lateral surface → complete SA = πr²+πrl

# Formula: SA = 4πr²
# Returns the surface area of a sphere
def SphereSurfaceArea(r):
    return 4 * math.pi * r ** 2                             # Multiply 4π by radius squared → complete SA = 4πr²

# ============================================================
# 3D SOLIDS — VOLUME
# ============================================================

# Formula: V = l * w * h
# Returns the volume of a rectangular prism (box)
def BoxVolume(l, w, h):
    return l * w * h                                        # Multiply all three dimensions → complete V = lwh

# Formula: V = s³
# Returns the volume of a cube
def CubeVolume(s):
    return s ** 3                                           # Cube the side length → complete V = s³

# Formula: V = π * r² * h
# Returns the volume of a cylinder
def CylinderVolume(r, h):
    return math.pi * r ** 2 * h                             # Multiply base area by height → complete V = πr²h

# Formula: V = ⅓ * π * r² * h
# Returns the volume of a cone
def ConeVolume(r, h):
    return (1 / 3) * math.pi * r ** 2 * h                  # Multiply cylinder volume by ⅓ → complete V = ⅓πr²h

# Formula: V = (4/3) * π * r³
# Returns the volume of a sphere
def SphereVolume(r):
    return (4 / 3) * math.pi * r ** 3                       # Multiply 4/3π by radius cubed → complete V = (4/3)πr³

# Formula: V = ⅓ * base_area * height
# Returns the volume of a pyramid given base area and height
def PyramidVolume(base_area, h):
    return (1 / 3) * base_area * h                          # Multiply base area by height then take ⅓ → complete V = ⅓Bh

# ============================================================
# COORDINATE GEOMETRY
# ============================================================

# Formula: checks if point (px, py) lies on the line y = mx + b
# Returns True if the point satisfies the line equation within tolerance
def IsOnLine(m, b, px, py, tolerance = 1e-9):
    return abs(m * px + b - py) < tolerance                 # Evaluate line at px and compare to py → True if on line

# Formula: perpendicular slope = -1 / m
# Returns the slope of a line perpendicular to one with slope m
# Returns 0 if m is zero to avoid division by zero (horizontal line → perpendicular is vertical)
def PerpendicularSlope(m):
    if m == 0:                                              # Guard — perpendicular to a horizontal line is a vertical line
        return 0                                            # Return 0 — vertical lines have undefined slope represented as 0 here
    return -1 / m                                           # Negate the reciprocal → complete m_perp = -1/m

# Formula: parallel lines have equal slopes
# Returns True if two lines are parallel — same slope, different intercept
def AreParallel(m1, b1, m2, b2, tolerance = 1e-9):
    slopes_equal     = abs(m1 - m2) < tolerance             # Check if slopes are effectively equal
    intercepts_equal = abs(b1 - b2) < tolerance             # Check if intercepts are also equal (would be same line)
    return slopes_equal and not intercepts_equal            # Parallel means same slope but different intercept

# Formula: perpendicular lines have slopes that are negative reciprocals — m1 * m2 = -1
# Returns True if two lines are perpendicular
def ArePerpendicular(m1, m2, tolerance = 1e-9):
    return abs(m1 * m2 + 1) < tolerance                     # Check if product of slopes equals -1 → complete m1*m2 = -1

# Formula: point-slope form — y - y1 = m(x - x1)  →  y = m*x + (y1 - m*x1)
# Returns the y-intercept b of a line given slope m and a point (x1, y1) it passes through
def LineFromPointSlope(m, x1, y1):
    return y1 - m * x1                                      # Rearrange point-slope form to get b → complete b = y1 - m*x1

# Formula: checks if three points are collinear — area of triangle formed = 0
# Returns True if three 2D points lie on the same straight line
def AreCollinear(x1, y1, x2, y2, x3, y3, tolerance = 1e-9):
    area = abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))  # Compute twice the triangle area using the cross product formula
    return area < tolerance                                 # Zero area means points are collinear → True if on same line
