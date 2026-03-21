import pytest
from moneypoly.player import Player
from moneypoly.property import Property

def test_player_net_worth_includes_properties():
    """
    Test Case: Verify that a player's net worth includes both their cash balance and the value of their properties.
    Reason: End-of-game tie-breakers (or bankruptcy evaluations) rely on total net worth, not just liquid cash.
    Expected: Net worth = Balance + Property Values.
    Actual Error Found: Player.net_worth() only returns `self.balance`.
    """
    player = Player("Alice", balance=100)
    
    # Give Alice a property worth 400
    prop = Property("Boardwalk", 39, price=400, base_rent=50)
    player.add_property(prop)
    
    # Her expected net worth should be > 100 (specifically 100 + 400 = 500, or at least adding mortgage value).
    # This will fail because it only returns 100.
    assert player.net_worth() > 100, "Player net worth only calculates cash on hand, entirely ignoring property values."
