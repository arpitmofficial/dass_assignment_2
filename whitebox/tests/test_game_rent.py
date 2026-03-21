import pytest
from moneypoly.game import Game
from moneypoly.property import Property

def test_pay_rent_transfers_money_to_owner():
    """
    Test Case: Verify that when a player pays rent, the money is added to the property owner's balance.
    Reason: In Monopoly, rent is a transfer of wealth. It must be added to the owner's account.
    Expected: Owner's balance increases by the exact rent amount.
    Actual Error Found: game.pay_rent() deducts from the payer but forgets to add to the owner!
    """
    game = Game(["Alice", "Bob"])
    alice = game.players[0]
    bob = game.players[1]
    
    # Setup a property and assign to Bob
    prop = Property("Test Ave", 1, 100, 20)
    prop.owner = bob
    bob.balance = 1000
    
    # Alice lands on it and pays rent
    game.pay_rent(alice, prop)
    
    # The rent is 20. Bob's balance should be 1020.
    # This will fail because Bob's balance remains 1000.
    assert bob.balance == 1020, "Rent was deducted from payer, but not added to the owner!"
