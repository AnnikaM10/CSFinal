import time

import pytest

from stock_portfolio.models.UserList_model import UserListModel


@pytest.fixture
def user_list_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return UserListModel()

# Fixtures providing sample meals as dictionaries
@pytest.fixture
def sample_stock1():
    return {
        "id": 1,
        "stock": "Spaghetti",
    }

@pytest.fixture
def sample_stock2():
    return {
        "id": 2,
        "stock": "Pizza",
    }

@pytest.fixture
def sample_users():
    return [1, 2]



##########################################################
# Combatant Prep
##########################################################

def test_clear_users(user_list_model, sample_users):
    """Test that clear_combatants empties the combatants list."""
    user_list_model.users.extend(sample_users)

    # Call the clear_combatants method
    user_list_model.clear_users()

    # Assert that the combatants list is now empty
    assert len(user_list_model.users) == 0, "users list should be empty after calling clear_users."

def test_clear_users_empty(user_list_model):
    """Test that calling clear_combatants on an empty list works."""

    # Call the clear_combatants method with an empty list
    user_list_model.clear_users()

    # Assert that the combatants list is still empty
    assert len(user_list_model.users) == 0, "users list should remain empty if it was already empty."

def test_get_users_empty(user_list_model):
    """Test that get_combatants returns an empty list when there are no combatants."""

    # Call the function and verify the result
    users = user_list_model.get_users()
    assert users == [], "Expected get_users to return an empty list when there are no users."

def test_get_users_with_data(user_list_model, sample_users):
    """Test that get_combatants returns the correct list when there are users."""

    user_list_model.users.extend(sample_users)

    # Call the function and verify the result
    users = user_list_model.get_users()
    assert users == user_list_model.users, "Expected get_users to return the correct users list."

def test_prep_user(user_list_model, sample_stock1):
    """Test that a combatant is correctly added to the list."""

    # Call prep_combatant with the combatant data
    user_list_model.prep_users(sample_stock1)

    # Assert that the combatant was added to the list
    assert len(user_list_model.users) == 1, "users list should contain one user after calling user."
    assert user_list_model.user_stocks_cache[user_list_model.users[0]]["stock"] == "Spaghetti", "Expected 'Spaghetti' in the users list."

def test_prep_user_full(user_list_model, sample_users):
    """Test that prep_combatant raises an error when the list is full."""

    # Mock the combatants list with 2 combatants
    user_list_model.users.extend(sample_users)

    # Define the combatant data to be passed to prep_combatant
    user_data = {"id": 3, "stock": "Burger", "cuisine": "American", "price": 10.0, "difficulty": "MED"}

    # Call prep_combatant and expect an error since the list is full
    with pytest.raises(ValueError, match="users list is full, cannot add more users."):
        user_list_model.prep_users(user_data)

    # Assert that the combatants list still contains only the original 2 combatants
    assert len(user_list_model.users) == 2, "users list should still contain only 2 users after trying to add a third."
