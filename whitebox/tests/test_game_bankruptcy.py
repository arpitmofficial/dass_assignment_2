import pytest
from moneypoly.game import Game

def test_skipped_player_after_bankruptcy():
    """
    Test Case: Verify that the turn progression works correctly when a player is bankrupt.
    Reason: Removing a player from the list shifts the indices of the remaining players. We need to ensure no player's turn is skipped.
    Expected: Player C takes their turn after Player B goes bankrupt.
    Actual Error Found: advance_turn() skips Player C since current_index increments past them.
    """
    game = Game(["Alice", "Bob", "Charlie"])
    
    # Make Bob play and go bankrupt.
    game.current_index = 1  # It's Bob's turn
    bob = game.players[1]
    
    # Bankrupt Bob
    bob.deduct_money(bob.balance + 100) 
    
    # Avoid doubles and chance/property things by directly calling _check_bankruptcy and advance_turn
    # We simulate end of play_turn manually for clarity
    game._check_bankruptcy(bob)
    # Bob is removed. List is now [Alice, Charlie]. 
    # current_index is STILL 1.
    
    game.advance_turn()
    # current_index becomes (1 + 1) % 2 = 0 -> Alice!
    
    # This will fail, indicating Charlie was skipped
    assert game.current_player().name == "Charlie", "Charlie's turn was skipped after Bob went bankrupt."
