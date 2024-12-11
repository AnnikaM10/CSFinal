import logging
from typing import Any, List

from stock_portfolio.clients.mongo_client import sessions_collection
from stock_portfolio.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


def login_user(user_id: int, user_list_model) -> None:
    """
    Load the user's users from MongoDB into the BattleModel's users list.

    Checks if a session document exists for the given `user_id` in MongoDB.
    If it exists, clears any current users in `battle_model` and loads
    the stored users from MongoDB into `battle_model`.

    If no session is found, it creates a new session document for the user
    with an empty users list in MongoDB.

    Args:
        user_id (int): The ID of the user whose session is to be loaded.
        battle_model (BattleModel): An instance of `BattleModel` where the user's users
                                    will be loaded.
    """
    logger.info("Attempting to log in user with ID %d.", user_id)
    session = sessions_collection.find_one({"user_id": user_id})

    if session:
        logger.info("Session found for user ID %d. Loading users into BattleModel.", user_id)
        user_list_model.clear_users()
        for user in session.get("users", []):
            logger.debug("Preparing user: %s", user)
            user_list_model.users(user)
        logger.info("users successfully loaded for user ID %d.", user_id)
    else:
        logger.info("No session found for user ID %d. Creating a new session with empty users list.", user_id)
        sessions_collection.insert_one({"user_id": user_id, "users": []})
        logger.info("New session created for user ID %d.", user_id)

def logout_user(user_id: int, user_list_model) -> None:
    """
    Store the current users from the BattleModel back into MongoDB.

    Retrieves the current users from `user_list_model` and attempts to store them in
    the MongoDB session document associated with the given `user_id`. If no session
    document exists for the user, raises a `ValueError`.

    After saving the users to MongoDB, the users list in `user_list_model` is
    cleared to ensure a fresh state for the next login.

    Args:
        user_id (int): The ID of the user whose session data is to be saved.
        battle_model (UserListModel): An instance of `UserListModel` from which the user's
                                    current users are retrieved.

    Raises:
        ValueError: If no session document is found for the user in MongoDB.
    """
    logger.info("Attempting to log out user with ID %d.", user_id)
    users_data = user_list_model.get_users()
    logger.debug("Current users for user ID %d: %s", user_id, users_data)

    result = sessions_collection.update_one(
        {"user_id": user_id},
        {"$set": {"users": users_data}},
        upsert=False  # Prevents creating a new document if not found
    )

    if result.matched_count == 0:
        logger.error("No session found for user ID %d. Logout failed.", user_id)
        raise ValueError(f"User with ID {user_id} not found for logout.")

    logger.info("users successfully saved for user ID %d. Clearing BattleModel users.", user_id)
    user_list_model.clear_users()
    logger.info("BattleModel users cleared for user ID %d.", user_id)
