# ============================================================
# CHECK FUNCTIONS
# ============================================================

# Formula: var % 2 == 0
# Returns True if var is even, False if var is odd
# Uses modulo to check if there is no remainder when divided by 2
def IsEven(var):
    return var % 2 == 0  # Divide var by 2 and check if remainder is zero → True if even, False if odd