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

    # def battle(self) -> str:
    #     """
    #     Simulates a battle between two users.

    #     Simulates a battle between two users. Computes their battle scores,
    #     normalizes the delta between the scores, and determines the winner
    #     based on a random number from random.org.

    #     Returns:
    #         str: The name of the winning users (meal).
    #     """
    #     logger.info("Two meals enter, one meal leaves!")

    #     if len(self.users) < 2:
    #         logger.error("Not enough users to start a battle.")
    #         raise ValueError("Two users must be prepped for a battle.")

    #     # Refresh users' data if TTLs have expired
    #     for meal_id in self.users:
    #         if time.time() > self.cuser_ttls.get(meal_id, 0):  # Check TTL expiration
    #             # Fetch latest data and update cache
    #             logger.info("Cache expired for meal ID %s, refreshing cache.", meal_id)
    #             updated_meal = Meals.get_meal_by_id(meal_id)
    #             self.user_ttls[meal_id] = time.time() + TTL  # Reset TTL
    #             self.meals_cache[meal_id] = updated_meal

    #     user_1 = self.meals_cache[self.users[0]]
    #     user_2 = self.meals_cache[self.users[1]]

    #     # Log the start of the battle
    #     logger.info("Battle started between %s and %s", user_1["meal"], user_2["meal"])

    #     # Get battle scores for both users
    #     score_1 = self.get_battle_score(user_1)
    #     score_2 = self.get_battle_score(user_2)

    #     # Log the scores for both users
    #     logger.info("Score for %s: %.3f", user_1["meal"], score_1)
    #     logger.info("Score for %s: %.3f", user_2["meal"], score_2)

    #     # Compute the delta and normalize between 0 and 1
    #     delta = abs(score_1 - score_2) / 100

    #     # Log the delta and normalized delta
    #     logger.info("Delta between scores: %.3f", delta)

    #     # Get random number from random.org
    #     random_number = get_random()

    #     # Log the random number
    #     logger.info("Random number from random.org: %.3f", random_number)

    #     # Determine the winner based on the normalized delta
    #     if delta > random_number:
    #         winner = user_1
    #         loser = user_2
    #     else:
    #         winner = user_2
    #         loser = cuser_1

    #     # Log the winner
    #     logger.info("The winner is: %s", winner["meal"])

    #     # Update stats for both users
    #     Meals.update_meal_stats(winner["id"], 'win')
    #     Meals.update_meal_stats(loser["id"], 'loss')

    #     # Remove the losing user from users
    #     self.users.remove(loser["id"])

    #     return winner["meal"]

    def clear_users(self):
        """
        Clears the list of users.
        """
        logger.info("Clearing the users list.")
        self.users.clear()

    # def get_battle_score(self, user: dict[str, Any]) -> float:
    #     """
    #     Calculates the battle score for a user based on the price and difficulty of the meal.

    #     Calculates the battle score for a user based on the following rule:
    #     - Multiply the price by the number of letters in the cuisine.
    #     - Subtract a difficulty modifier (HIGH = 1, MED = 2, LOW = 3).

    #     Args:
    #         user (dict[str, Any]): A dict representing the user.

    #     Returns:
    #         float: The calculated battle score.
    #     """
    #     difficulty_modifier = {"HIGH": 1, "MED": 2, "LOW": 3}

    #     # Log the calculation process
    #     logger.info("Calculating battle score for %s: price=%.3f, cuisine=%s, difficulty=%s",
    #                 user["meal"], user["price"], user["cuisine"], user["difficulty"])

    #     # Calculate score
    #     score = (user["price"] * len(user["cuisine"])) - difficulty_modifier[combatant["difficulty"]]

    #     # Log the calculated score
    #     logger.info("Battle score for %s: %.3f", combatant["meal"], score)

    #     return score

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