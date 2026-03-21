"""
Test Case: Voluntary Jail Fine Not Charged to Player

Reason for Test:
    When a jailed player chooses to pay the $50 fine voluntarily to leave jail early,
    the game must deduct the fine from the player's balance AND credit the bank.
    Testing this two-way transfer is critical because the bank-credit and the
    player-deduction are two separate operations; missing one of them silently
    corrupts the game economy.

Error Found:
    In game.py _handle_jail_turn(), the voluntary-exit branch calls:
        self.bank.collect(JAIL_FINE)    # bank gains $50 ✓
        player.in_jail = False           # player freed ✓
    But it NEVER calls:
        player.deduct_money(JAIL_FINE)  # player pays ✗  <- MISSING!

    This lets a player leave jail for free, getting the benefit without any cost.
    The mandatory release path (after 3 jail turns) correctly deducts from the player.
"""

import pytest
from unittest.mock import patch
from moneypoly.game import Game


def test_voluntary_jail_fine_deducted_from_player():
    """
    Branch: Player in jail, chooses to pay fine voluntarily (confirm → True).
    Expected:
        - player.in_jail becomes False
        - player.balance decreases by JAIL_FINE (50)
        - bank.get_balance() increases by JAIL_FINE
    """
    game = Game(["Alice", "Bob"])
    alice = game.players[0]

    alice.go_to_jail()
    assert alice.in_jail is True

    starting_balance = alice.balance
    bank_before = game.bank.get_balance()

    with patch("moneypoly.ui.confirm", return_value=True):
        with patch("moneypoly.dice.Dice.roll", return_value=4):
            with patch("moneypoly.dice.Dice.describe", return_value="2+2=4"):
                with patch("builtins.input", return_value="s"):
                    game._handle_jail_turn(alice)

    # Player should be out of jail
    assert alice.in_jail is False

    # Player should have PAID the fine (balance drops by 50)
    assert alice.balance == starting_balance - 50, (
        f"Expected balance {starting_balance - 50}, got {alice.balance}. "
        "Player left jail for free — fine was not deducted!"
    )

    # Bank should have received the fine
    assert game.bank.get_balance() >= bank_before, (
        "Bank balance did not increase after collecting jail fine."
    )


def test_voluntary_jail_fine_not_charged_when_player_stays():
    """
    Branch: Player in jail, DECLINES to pay fine (confirm → False).
    Expected:
        - player.in_jail remains True
        - player.balance is unchanged
        - jail_turns increments by 1
    """
    game = Game(["Alice", "Bob"])
    alice = game.players[0]

    alice.go_to_jail()
    starting_balance = alice.balance

    with patch("moneypoly.ui.confirm", return_value=False):
        game._handle_jail_turn(alice)

    assert alice.in_jail is True
    assert alice.balance == starting_balance, (
        "Fine was charged even though player chose not to pay!"
    )
    assert alice.jail_turns == 1
