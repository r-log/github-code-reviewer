from typing import List, Dict, Optional


def bad_function(x: int = 1) -> None:
    """Short doc."""
    return None


def good_function(data: List[str], config: Optional[Dict] = None) -> List[str]:
    """Example of a well-documented function.

    This function demonstrates proper code style, documentation,
    and type hints usage.

    Args:
        data: List of strings to process
        config: Optional configuration dictionary

    Returns:
        List[str]: Processed data
    """
    MULTIPLIER = 2  # Proper constant naming
    result = []  # Initialize list properly

    for item in data:
        processed = item * MULTIPLIER
        result.append(processed)

    return result


class BadClassName:  # Should be PascalCase
    def __init__(self):
        self.badVariable = 123  # Should be snake_case

    def badMethod():  # Missing self parameter
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


# Test various issues
def test_issues():
    # Magic numbers
    x = 42
    y = 123

    # Bad spacing
    z = x+y

    # Nested loops with complexity
    for i in range(10):
        for j in range(10):
            if i > 5:
                if j > 5:
                    print(i + j)

    # Exception handling
    try:
        x = 1/0
    except:  # Bare except
        pass

    # Unused imports and variables
    unused_var = 100

    return None
