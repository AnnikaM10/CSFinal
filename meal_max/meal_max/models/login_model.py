import logging
import os
import time
from typing import Any, List

from meal_max.meal_max.models.stocks_model import UserStocks
from meal_max.utils.logger import configure_logger
from meal_max.utils.random_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


TTL = os.getenv("TTL", 60)  # Default TTL is 60 seconds


class LoginModel:
    """
    A class to manage the battle between two combatants.

    Attributes:
        combatants (List[dict[str, Any]]): The list of combatants in the battle.
        combatant_ttls (dict[int, int]): A dictionary to store TTL for each combatant.
        meals_cache (dict[int, dict[str, Any]]): A dictionary to cache meal data by ID.
    """

    def __init__(self):
        """Initializes the BattleManager with an empty list of combatants and TTL."""
        self.users: List[int] = []  # List of active combatants
        self.users_ttls: dict[int, int] = {}  # Dictionary to store TTL for each combatant
        self.users_cache: dict[int, dict[str, Any]] = {}  # Cache of meal data by ID

    def clear_users(self):
        """
        Clears the list of combatants.
        """
        logger.info("Clearing the combatants list.")
        self.users.clear()


    def get_users(self) -> List[dict[str, Any]]:
        """
        Retrieves the current list of combatants for a battle.

        Returns:
            List[dict[str, Any]]: A list of dicts representing combatants.
        """
        logger.info("Retrieving current list of users.")
        return self.users

    def current_users(self, user_data: dict[str, Any]):
        """
        Prepares a combatant by adding it to the combatants list for an upcoming battle.

        Args:
            combatant_data (dict[str, Any]): A dict containing the combatant details.

        Raises:
            ValueError: If the combatants list already has two combatants (battle is full).
        """
        # if len(self.combatants) >= 2:
        #     logger.error("Attempted to add combatant '%s' but combatants list is full", combatant_data["meal"])
        #     raise ValueError("User list is full, cannot add more combatants.")

        # Log the addition of the combatant
        logger.info("Adding combatant '%s' to combatants list", user_data["symbol"])

        id = user_data["id"]
        self.combatants.append(id)
        self.users_cache[id] = user_data
        self.users_ttls[id] = time.time() + TTL

        # Log the current state of combatants
        logger.info("Current combatants list: %s", [self.users_cache[user]["symbol"] for user in self.users])