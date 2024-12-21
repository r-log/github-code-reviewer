"""Test file for the code reviewer.

This file contains various examples of good and bad code
to test the functionality of the code reviewer. Each section
demonstrates different aspects of code quality checks.
"""

from typing import List, Dict, Optional, Union, Any

# Define module-level constants for use in test examples
MULTIPLIER_VALUE = 2
DEFAULT_VALUE = 123
SMALL_VALUE = 10
MEDIUM_VALUE = 20
LARGE_VALUE = 100
THRESHOLD_VALUE = 50
TEST_VALUE = 42
LIST_SIZE = 3
EXAMPLE_DATA = ["test", "example"]
EXAMPLE_CONFIG = {"option": "value"}


def run_examples() -> None:
    """Run example code to demonstrate reviewer functionality.

    This function executes all the example code to ensure
    it's being used and to demonstrate various code review
    checks in action.
    """
    # Run function examples with test data
    demonstrate_issues()
    demonstrate_good_practices(EXAMPLE_DATA, EXAMPLE_CONFIG)

    # Create test instances
    bad_example = DemonstrateBadPractices()
    bad_example.demonstrate_method_issues()

    good_example = DemonstrateGoodPractices(TEST_VALUE)
    good_example.process_data([1] * LIST_SIZE)

    # Test error handling
    demonstrate_complexity()


def demonstrate_issues(x: int = 1) -> None:
    """Demonstrate various code issues.

    This function shows common code issues that should be
    detected by the reviewer, such as unused parameters
    and poor documentation.

    Args:
        x: Input value that's never used
    """
    return None


def demonstrate_good_practices(
    data: List[str],
    config: Optional[Dict[str, Any]] = None
) -> List[str]:
    """Demonstrate good coding practices.

    This function shows proper code style, documentation,
    and type hints usage. It processes strings according
    to configuration.

    Args:
        data: List of strings to process
        config: Optional configuration dictionary

    Returns:
        List[str]: Processed data with applied transformations
    """
    output: List[str] = []
    for item in data:
        output.append(item * MULTIPLIER_VALUE)
    return output


class DemonstrateBadPractices:
    """Demonstrate common class-related issues.

    This class shows various issues that should be caught:
    - Missing type hints
    - Poor documentation
    - Improper initialization
    """

    def __init__(self, value: int = DEFAULT_VALUE) -> None:
        """Initialize with demonstration values.

        Args:
            value: Initial value to store
        """
        self.value = value

    def demonstrate_method_issues(self, param: Any = None) -> None:
        """Demonstrate method-related issues.

        Shows various method-specific issues:
        - Lack of implementation
        - Unused parameters
        - Minimal documentation

        Args:
            param: Unused parameter for demonstration
        """
        pass


class DemonstrateGoodPractices:
    """Demonstrate proper class implementation.

    This class shows proper:
    - Documentation
    - Type hints
    - Method implementation
    - Error handling
    """

    def __init__(self, value: int) -> None:
        """Initialize with a value.

        Args:
            value: Initial value to store
        """
        self.value = value

    def process_data(self, data: List[int]) -> List[int]:
        """Process a list of integers.

        Demonstrates proper list processing with type hints
        and efficient implementation.

        Args:
            data: List of integers to process

        Returns:
            List[int]: Processed integers
        """
        return [x + self.value for x in data]


def demonstrate_complexity() -> None:
    """Demonstrate complexity and error handling.

    Shows proper handling of:
    - Constants usage
    - Error handling
    - Loop complexity
    - Code organization
    """
    output = SMALL_VALUE + MEDIUM_VALUE

    try:
        output = LARGE_VALUE / 0
    except ZeroDivisionError as error:
        print(f"Handled error: {error}")

    # Process values up to threshold
    for index in range(LARGE_VALUE):
        if index <= THRESHOLD_VALUE:
            continue
        print(f"Index {index} exceeded {THRESHOLD_VALUE}")


if __name__ == "__main__":
    run_examples()
