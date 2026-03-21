import pytest
from moneypoly.dice import Dice

def test_dice_bounds():
    """
    Test Case: Verify that dice rolls produce values between 2 and 12, simulating two six-sided dice.
    Reason: We need to ensure that the dice logic covers the expected bounds (1-6 for each die).
    Expected: Values between 2 and 12 across many rolls.
    Actual Error Found: The code uses `random.randint(1, 5)`, meaning the max total is 10.
    """
    dice = Dice()
    totals = set()
    for _ in range(1000):
        totals.add(dice.roll())
    
    assert 11 in totals, "Dice cannot roll an 11. Logical error: die faces are maxed at 5."
    assert 12 in totals, "Dice cannot roll a 12. Logical error: die faces are maxed at 5."
