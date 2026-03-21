import pytest
from unittest.mock import patch
from moneypoly.game import Game

def test_extra_turn_while_in_jail():
    """
    Test Case: Verify that rolling doubles and going to jail does NOT grant an extra turn.
    Reason: A core rule is if you are sent to jail, your turn ends immediately, regardless of doubles.
    Expected: Next turn should belong to the next player.
    Actual Error Found: game.play_turn() checks if dice is doubles at the end regardless of jail state, granting an illegal extra turn.
    """
    game = Game(["Alice", "Bob"])
    alice = game.players[0]
    
    # Mock dice to roll doubles, and force a Go To Jail scenario
    with patch("moneypoly.dice.Dice.roll", return_value=4):
        with patch("moneypoly.dice.Dice.is_doubles", return_value=True):
            with patch("moneypoly.dice.Dice.describe", return_value="2+2=4"):
                # Force alice to land on Go To Jail (position 30)
                alice.position = 26
                # play_turn will move her 4 spaces to 30, triggering Go To Jail
                game.play_turn()
    
    # After going to jail, Alice's turn should end and it should be Bob's turn.
    # This will fail because it's still Alice's turn.
    assert game.current_player().name == "Bob", "Alice got an extra turn even though she went to jail."
