import pytest
from moneypoly.game import Game
from moneypoly.property import Property

def test_trade_adds_money_to_seller():
    """
    Test Case: Verify that during a trade, the cash amount paid by the buyer is given to the seller.
    Reason: Trade is an exchange of assets (property for cash).
    Expected: Seller's balance increases by cash_amount.
    Actual Error Found: game.trade() deducts cash from the buyer, but the money vanishes; the seller receives nothing.
    """
    game = Game(["Alice", "Bob"])
    alice = game.players[0]  # Seller
    bob = game.players[1]    # Buyer
    
    alice.balance = 1000
    bob.balance = 1000
    
    prop = Property("Park Place", 37, 350, 35)
    prop.owner = alice
    alice.add_property(prop)
    
    cash_amount = 300
    game.trade(seller=alice, buyer=bob, prop=prop, cash_amount=cash_amount)
    
    # Bob pays 300, his balance should be 700. This works.
    assert bob.balance == 700, "Buyer's balance was not deducted correctly."
    
    # Alice sells for 300, her balance should be 1300.
    # This will fail because the money is never added to her account!
    assert alice.balance == 1300, "Seller's balance did not increase after receiving cash for the trade."
