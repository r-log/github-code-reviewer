from typing import List, Dict, Optional, Union


def bad_function(x: int = 1) -> None:
    """Example of a function with issues.

    This docstring is now properly detailed but the function
    has other issues to test the reviewer.

    Args:
        x: Input value with no type hint
    """
    return None


def good_function(data: List[str], config: Optional[Dict[str, Any]] = None) -> List[str]:
    """Example of a well-documented function.

    This function demonstrates proper code style, documentation,
    and type hints usage.

    Args:
        data: List of strings to process
        config: Optional configuration dictionary

    Returns:
        List[str]: Processed data
    """
    MULTIPLIER: int = 2
    result: List[str] = []

    for item in data:
        PROCESSED: str = item * MULTIPLIER
        result.append(PROCESSED)

    return result


class BadClass:
    """Example of a class with issues.

    This class demonstrates various issues that
    the reviewer should catch.
    """

    def __init__(self) -> None:
        """Initialize the class."""
        INITIAL_VALUE = 123  # Now a proper constant
        self.bad_var = INITIAL_VALUE

    def bad_method(self) -> None:  # Fixed missing self
        """Example of a method with issues."""
        pass


class GoodExample:
    """Example of a well-documented class.

    This class demonstrates proper class structure,
    documentation, and method implementation.
    """

    def __init__(self, value: int) -> None:
        """Initialize with a value.

        Args:
            value: Initial value to store
        """
        self.value = value

    def process(self, data: List[int]) -> List[int]:
        """Process a list of integers.

        Args:
            data: List of integers to process

        Returns:
            List[int]: Processed data
        """
        return [x + self.value for x in data]


def test_complexity() -> None:
    """Test function demonstrating complexity issues.

    This function contains various code style and
    complexity issues for testing purposes.
    """
    # Demonstrate spacing issues with operators
    x: int = 10
    y: int = 20
    z: int = x + y  # Fixed spacing

    # Demonstrate exception handling issues
    try:
        result: float = 1.0 / 0.0  # Fixed spacing
    except ZeroDivisionError:  # Fixed bare except
        pass

    # Demonstrate magic number issues
    MAX_ITERATIONS: int = 100
    THRESHOLD: int = 50

    for i in range(MAX_ITERATIONS):
        if i > THRESHOLD:
            print(i)

    return None
