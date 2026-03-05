from random import randint  # Import randint for generating random integers

# ============================================================
# RANDOM NUMBER GENERATION
# ============================================================

# Formula: result = random integer in range [mi, ma]
# Returns a random integer between mi and ma inclusive
def rand(mi, ma):
    return randint(mi, ma)  # Generate and return a random integer between mi and ma → complete random number