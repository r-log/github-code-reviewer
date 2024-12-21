"""Test file for the code reviewer.

This file contains various examples of good and bad code
to test the functionality of the code reviewer.
"""

from typing import List, Dict, Optional, Union, Any


def bad_function(x: int = 1) -> None:
    """Example of a function with issues.

    This function demonstrates various issues that the code
    reviewer should catch, including:
    - Brief docstrings
    - Missing type hints
    - Unused parameters
    - Magic numbers

    Args:
        x: Input value that's never used
    """
    return None


def good_function(data: List[str], config: Optional[Dict[str, Any]] = None) -> List[str]:
    """Example of a well-documented function.

    This function demonstrates proper code style, documentation,
    and type hints usage. It processes a list of strings according
    to the provided configuration.

    Args:
        data: List of strings to process
        config: Optional configuration dictionary that can modify behavior

    Returns:
        List[str]: Processed data with applied transformations
    """
    # Define constants at the top of the function
    DEFAULT_MULTIPLIER: int = 2

    # Initialize result list with proper typing
    result: List[str] = []

    # Process each item with proper naming and documentation
    for item in data:
        # Apply the multiplication transformation
        transformed: str = item * DEFAULT_MULTIPLIER
        result.append(transformed)

    return result


class BadClass:
    """Example of a class with issues.

    This class demonstrates various issues that the code
    reviewer should catch, including:
    - Missing type hints
    - Poor method documentation
    - Magic numbers
    - Improper initialization
    """

    def __init__(self) -> None:
        """Initialize the class with default values.

        Sets up the initial state of the class with a
        predefined value for demonstration.
        """
        # Define class-level constants
        DEFAULT_VALUE: int = 123
        self.bad_var = DEFAULT_VALUE

    def bad_method(self) -> None:
        """Example of a method with issues.

        This method demonstrates various issues including:
        - Lack of implementation
        - Missing parameters
        - Poor documentation
        """
        pass


class GoodExample:
    """Example of a well-documented class.

    This class demonstrates proper class structure,
    documentation, and method implementation. It serves
    as an example of good coding practices.
    """

    def __init__(self, value: int) -> None:
        """Initialize with a value.

        Args:
            value: Initial value to store for processing
        """
        self.value = value

    def process(self, data: List[int]) -> List[int]:
        """Process a list of integers.

        Applies the stored value to each element in the input list
        using a list comprehension for efficiency.

        Args:
            data: List of integers to process

        Returns:
            List[int]: Each input value incremented by the stored value
        """
        return [x + self.value for x in data]


def test_complexity() -> None:
    """Test function demonstrating complexity issues.

    This function contains various code style and complexity
    issues for testing the code reviewer's ability to detect:
    - Magic numbers
    - Operator spacing
    - Exception handling
    - Code complexity
    """
    # Define constants for all numeric values
    SMALL_VALUE: int = 10
    MEDIUM_VALUE: int = 20
    LARGE_VALUE: int = 100
    THRESHOLD: int = 50

    # Demonstrate proper operator spacing in calculations
    result: int = SMALL_VALUE + MEDIUM_VALUE

    # Demonstrate proper exception handling with specific exceptions
    try:
        # Intentionally cause a division by zero error
        result = LARGE_VALUE / 0
    except ZeroDivisionError as e:
        # Properly handle the specific exception
        print(f"Caught expected error: {e}")

    # Demonstrate proper loop structure with constants
    for i in range(LARGE_VALUE):
        if i > THRESHOLD:
            print(f"Value {i} exceeded threshold")

    return None
