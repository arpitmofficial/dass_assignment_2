import pytest
from moneypoly.game import Game
from moneypoly.property import Property

def test_unmortgage_state_leak():
    """
    Test Case: Verify that if a player cannot afford to unmortgage a property, its state remains mortgaged.
    Reason: State should not be modified before a balance validation check passes.
    Expected: Property remains is_mortgaged = True.
    Actual Error Found: Property state is flipped to False before the game checks player.balance, giving a free unmortgage!
    """
    game = Game(["Alice", "Bob"])
    alice = game.players[0]
    
    # Alice has a mortgaged property but $0 balance
    prop = Property("Baltic", 3, 60, 4)
    prop.owner = alice
    prop.is_mortgaged = True
    alice.add_property(prop)
    alice.balance = 0
    
    # Needs $33 to unmortgage. Should fail and return False.
    result = game.unmortgage_property(alice, prop)
    
    assert result is False, "The unmortgage method should have aborted due to insufficient funds."
    
    # This will fail because prop is now illegally unmortgaged!
    assert prop.is_mortgaged is True, "The property was unmortgaged despite the player not having enough money!"
