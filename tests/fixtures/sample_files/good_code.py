"""Module containing examples of good coding practices."""
from typing import List, Optional


class UserManager:
    """Class to manage user operations."""

    def __init__(self, database_url: str):
        """Initialize the user manager.

        Args:
            database_url: Connection string for the database
        """
        self.database_url = database_url
        self.connected = False

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Retrieve user information by ID.

        Args:
            user_id: The unique identifier of the user

        Returns:
            Optional[dict]: User data if found, None otherwise

        Raises:
            ConnectionError: If database connection fails
        """
        if not self.connected:
            raise ConnectionError("Database connection not established")

        # Example of good practices:
        # - Type hints
        # - Proper error handling
        # - Clear variable names
        # - Reasonable function length
        return {"id": user_id, "name": "test_user"}


def calculate_average(numbers: List[float]) -> float:
    """Calculate the average of a list of numbers.

    Args:
        numbers: List of numbers to average

    Returns:
        float: The calculated average

    Raises:
        ValueError: If the input list is empty
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")

    return sum(numbers) / len(numbers)
