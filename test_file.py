def bad_function() -> None:
    """Example function to demonstrate code review functionality.

    Returns:
        None: This function returns None
    """
    X_VALUE = 1
    Y_VALUE = 2
    Z = X_VALUE + Y_VALUE  # Changed to uppercase for constant
    return Z


def unused_function() -> None:
    """Example of an unused function.

    This function exists to test the unused code detection.
    """
    pass
