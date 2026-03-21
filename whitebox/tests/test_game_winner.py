import pytest
from moneypoly.game import Game
from moneypoly.player import Player

def test_find_winner_uses_max_net_worth():
    """
    Test Case: Verify that find_winner() identifies the player with the HIGHEST net worth.
    Reason: The winner of Monopoly is the richest player.
    Expected: Player with max net worth is returned.
    Actual Error Found: find_winner() uses `min(..., key=lambda p: p.net_worth())`, returning the POOREST player!
    """
    game = Game(["Alice", "Bob", "Charlie"])
    
    game.players[0].balance = 500   # Alice
    game.players[1].balance = 2000  # Bob
    game.players[2].balance = 1000  # Charlie
    
    winner = game.find_winner()
    
    # The winner should be Bob (richest)
    # This will fail because it returns Alice (poorest)
    assert winner.name == "Bob", "The game declared the poorest player as the winner instead of the richest!"
