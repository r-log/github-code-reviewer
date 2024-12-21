def badFunction():
    x = 1
    y = 2
    z = x+y  # No spaces around operators
    return z  # Missing type hints


def unused_function():  # This will be flagged as unused
    """This is an unused function."""
    pass
