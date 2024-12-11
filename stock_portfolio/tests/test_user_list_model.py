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
        "cuisine": "Italian",
        "price": 12.5,
        "difficulty": "MED"
    }

@pytest.fixture
def sample_stock2():
    return {
        "id": 2,
        "stock": "Pizza",
        "cuisine": "Italian",
        "price": 15.0,
        "difficulty": "LOW"
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


##########################################################
# Battle
##########################################################

# def test_get_battle_score(battle_model, sample_meal1, sample_meal2):
#     """Test the get_battle_score method."""

#     """Test combatant 1"""
#     combatant_1, combatant_2 = sample_meal1, sample_meal2
#     expected_score_1 = (12.5 * 7) - 2  # 12.5 * 7 - 2 = 85.5
#     assert battle_model.get_battle_score(combatant_1) == expected_score_1, f"Expected score: {expected_score_1}, got {battle_model.get_battle_score(combatant_1)}"

#     expected_score_2 = (15.0 * 7) - 3  # 15.0 * 7 - 3 = 102.0
#     assert battle_model.get_battle_score(combatant_2) == expected_score_2, f"Expected score: {expected_score_2}, got {battle_model.get_battle_score(combatant_2)}"

# def test_battle(battle_model, sample_combatants, sample_meal1, sample_meal2, caplog, mocker):
#     """Test the battle method with sample combatants."""

#     battle_model.combatants.extend(sample_combatants)

#     # Mock the battle functions
#     mocker.patch("meal_max.models.battle_model.BattleModel.get_battle_score", side_effect=[85.5, 102.0])
#     mocker.patch("meal_max.models.battle_model.get_random", return_value=0.42)
#     mock_update_stats = mocker.patch("meal_max.models.battle_model.Meals.update_meal_stats")

#     # Mock the TTLs to simulate unexpired cache
#     battle_model.combatant_ttls = {
#         combatant: time.time() + 60 for combatant in sample_combatants
#     }

#     battle_model.meals_cache[1] = sample_meal1
#     battle_model.meals_cache[2] = sample_meal2

#     # Call the battle method
#     winner_meal = battle_model.battle()

#     # Ensure the winner is combatant_2 since score_2 > score_1
#     assert winner_meal == "Pizza", f"Expected combatant 2 to win, but got {winner_meal}"

#     # Ensure update_stats was called correctly for both winner and loser
#     mock_update_stats.assert_any_call(1, 'loss')  # combatant_1 is the loser
#     mock_update_stats.assert_any_call(2, 'win')   # combatant_2 is the winner

#     # Check that combatant_1 was removed from the combatants list
#     assert len(battle_model.combatants) == 1, "Losing combatant was not removed from the list."
#     assert battle_model.combatants[0] == 2, "Expected combatant 2 to remain in the list."

#     # Check that the logger was called with the expected message
#     assert "Two meals enter, one meal leaves!" in caplog.text, "Expected battle cry log message not found."
#     assert "The winner is: Pizza" in caplog.text, "Expected winner log message not found."

# def test_battle_with_empty_combatants(battle_model):
#     """Test that the battle method raises a ValueError when there are fewer than two combatants."""

#     # Call the battle method and expect a ValueError
#     with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
#         battle_model.battle()

# def test_battle_with_one_combatant(battle_model, sample_meal1):
#     """Test that the battle method raises a ValueError when there's only one combatant."""

#     # Mock the combatants list with only one combatant
#     battle_model.combatants.append(sample_meal1)

#     # Call the battle method and expect a ValueError
#     with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
#         battle_model.battle()