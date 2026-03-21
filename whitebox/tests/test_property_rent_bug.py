import pytest
from moneypoly.property import Property, PropertyGroup
from moneypoly.player import Player

def test_property_monopoly_rent():
    """
    Test Case: Verify that rent is doubled only if ALL properties in a group are owned by the player.
    Reason: We must ensure edge condition is met (complete monopoly). 
    Expected: With one out of two properties owned, rent should be base_rent. 
    Actual Error Found: get_rent() uses `any()` instead of `all()`, so owning just 1 doubles the rent!
    """
    p1 = Property("Mediterranean Ave", 1, 60, 2)
    p2 = Property("Baltic Ave", 3, 60, 4)
    group = PropertyGroup("Brown", "brown")
    group.add_property(p1)
    group.add_property(p2)
    
    player = Player("Alice")
    p1.owner = player
    
    assert p1.get_rent() == 2, "Rent was doubled even though the player does not own the entire group."
