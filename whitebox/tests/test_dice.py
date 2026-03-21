import pytest
from moneypoly.dice import Dice

def test_dice_initialization():
    """Verify dice initializes to 0."""
    dice = Dice()
    assert dice.die1 == 0
    assert dice.die2 == 0
    assert dice.doubles_streak == 0

def test_dice_reset():
    """Verify reset clears values."""
    dice = Dice()
    dice.die1, dice.die2, dice.doubles_streak = 3, 4, 1
    dice.reset()
    assert dice.die1 == 0 and dice.die2 == 0 and dice.doubles_streak == 0

def test_doubles_streak_tracking(monkeypatch):
    """Test Branch: doubles_streak increments on doubles, resets on non-doubles."""
    dice = Dice()
    # Mock to roll 3 Then 3
    monkeypatch.setattr('random.randint', lambda a, b: 3)
    dice.roll()
    assert dice.is_doubles() is True
    assert dice.doubles_streak == 1
    
    # Second double
    dice.roll()
    assert dice.doubles_streak == 2
    
    # Mock to roll non-double
    iterator = iter([2, 4])
    monkeypatch.setattr('random.randint', lambda a, b: next(iterator))
    dice.roll()
    assert dice.is_doubles() is False
    assert dice.doubles_streak == 0  # Branch: reset to 0

def test_dice_describe(monkeypatch):
    """Test Branch: describe() formatting for doubles and non-doubles"""
    dice = Dice()
    iterator = iter([3, 4])
    monkeypatch.setattr('random.randint', lambda a, b: next(iterator))
    dice.roll()
    assert dice.describe() == "3 + 4 = 7"
    
    monkeypatch.setattr('random.randint', lambda a, b: 5)
    dice.roll()
    assert dice.describe() == "5 + 5 = 10 (DOUBLES)"
