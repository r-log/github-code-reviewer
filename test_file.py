from typing import List, Dict, Optional


def bad_function(x=1):
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
    MULTIPLIER = 2
    result = []

    for item in data:
        PROCESSED = item * MULTIPLIER
        result.append(PROCESSED)

    return result


class BadClass:
    def __init__(self):
        self.bad_var = 123

    def bad_method():
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


def test_complexity():
    """Test function demonstrating complexity issues."""
    # Bad spacing
    z = x+y

    # Exception handling
    try:
        result = 1/0
    except:  # Bare except
        pass

    # Magic numbers
    MAX_VALUE = 100
    for i in range(MAX_VALUE):
        if i > 50:
            print(i)

    return None
