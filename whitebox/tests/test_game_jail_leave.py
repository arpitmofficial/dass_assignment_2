import pytest
from unittest.mock import patch
from moneypoly.game import Game

def test_missing_turn_advance_after_leaving_jail():
    """
    Test Case: Verify that after paying the jail fine and rolling, the turn advances to the next player.
    Reason: Leaving jail by paying a fine completes your turn sequence. You do not get infinite turns.
    Expected: Player pays fine, moves, and turn advances to the next player.
    Actual Error Found: _handle_jail_turn() just returns without calling self.advance_turn().
    """
    game = Game(["Alice", "Bob"])
    alice = game.players[0]
    
    # Put Alice in jail
    alice.go_to_jail()
    
    # Stub confirm to always choose 'yes' to pay the fine
    with patch("moneypoly.ui.confirm", return_value=True):
        # Prevent doubles to avoid the extra turn issue
        with patch("moneypoly.dice.Dice.is_doubles", return_value=False):
            with patch("moneypoly.dice.Dice.describe", return_value="1+2=3"):
                # Mock input so that the turn resolves cleanly without waiting for Stdin
                with patch("builtins.input", return_value="s"):
                    game.play_turn()
            
    # Alice should have moved out of jail
    assert alice.in_jail is False, "Alice failed to leave jail."
    
    # This will fail because the turn was not advanced!
    assert game.current_player().name == "Bob", "Turn did not advance to Bob after Alice paid fine to leave jail."
