import logging
import os
import time
from typing import Any, List

from stock_portfolio.models.stock_model import UserStocks
from stock_portfolio.utils.logger import configure_logger
from stock_portfolio.utils.random_utils import get_random

logger = logging.getLogger(__name__)
configure_logger(logger)


TTL = os.getenv("TTL", 60)  # Default TTL is 60 seconds


class UserListModel:
    """
    A class to manage the battle between two users.

    Attributes:
        users (List[dict[str, Any]]): The list of users in the battle.
        users (dict[int, int]): A dictionary to store TTL for each user.
        meals_cache (dict[int, dict[str, Any]]): A dictionary to cache meal data by ID.
    """

    def __init__(self):
        """Initializes the BattleManager with an empty list of users and TTL."""
        self.users: List[int] = []  # List of active users
        self.users_ttls: dict[int, int] = {}  # Dictionary to store TTL for each combatant
        self.user_stocks_cache: dict[int, dict[str, Any]] = {}  # Cache of meal data by ID

    def clear_users(self):
        """
        Clears the list of users.
        """
        logger.info("Clearing the users list.")
        self.users.clear()

    def get_users(self) -> List[dict[str, Any]]:
        """
        Retrieves the current list of combatants for a battle.

        Returns:
            List[dict[str, Any]]: A list of dicts representing combatants.
        """
        logger.info("Retrieving current list of users.")
        return self.users

    def prep_users(self, user_data: dict[str, Any]):
        """
        Prepares a combatant by adding it to the combatants list for an upcoming battle.

        Args:
            combatant_data (dict[str, Any]): A dict containing the combatant details.

        Raises:
            ValueError: If the combatants list already has two combatants (battle is full).
        """
        if len(self.users) >= 2:
            logger.error("Attempted to add user '%s' but users list is full", user_data["stock"])
            raise ValueError("users list is full, cannot add more users.")

        # Log the addition of the combatant
        logger.info("Adding user '%s' to users list", user_data["stock"])

        id = user_data["id"]
        self.users.append(id)
        self.user_stocks_cache[id] = user_data
        self.users_ttls[id] = time.time() + TTL

        # Log the current state of combatants
        logger.info("Current users list: %s", [self.user_stocks_cache[user]["stock"] for user in self.users])