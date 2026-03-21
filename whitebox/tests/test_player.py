import pytest
from moneypoly.player import Player
from moneypoly.property import Property
from moneypoly.config import BOARD_SIZE, GO_SALARY, JAIL_POSITION

def test_player_initialization():
    p = Player("Alice", 1500)
    assert p.name == "Alice"
    assert p.balance == 1500
    assert p.position == 0
    assert not p.in_jail

def test_player_add_money():
    p = Player("A", 100)
    p.add_money(50)
    assert p.balance == 150
    with pytest.raises(ValueError):
        p.add_money(-10) # Branch: negative amount exception

def test_player_deduct_money():
    p = Player("A", 100)
    p.deduct_money(50)
    assert p.balance == 50
    with pytest.raises(ValueError):
        p.deduct_money(-10) # Branch: negative amount exception

def test_player_is_bankrupt():
    p = Player("A", 100)
    assert not p.is_bankrupt()
    p.deduct_money(100)
    assert p.is_bankrupt() # Branch: balance <= 0
    p.balance = -50
    assert p.is_bankrupt()

def test_player_move_normal():
    p = Player("A", 1500)
    p.move(5)
    assert p.position == 5
    assert p.balance == 1500

def test_player_move_pass_go():
    """Branch: passing Go should add GO_SALARY"""
    p = Player("A", 1500)
    p.position = BOARD_SIZE - 2
    p.move(4)
    assert p.position == 2
    assert p.balance == 1500 + GO_SALARY

def test_player_go_to_jail():
    p = Player("A", 1500)
    p.go_to_jail()
    assert p.position == JAIL_POSITION
    assert p.in_jail is True
    assert p.jail_turns == 0

def test_player_properties_list():
    p = Player("A")
    prop1 = Property("Test", 1, 100, 10)
    p.add_property(prop1)
    p.add_property(prop1) # Branch: add duplicate does nothing
    assert p.count_properties() == 1
    p.remove_property(prop1)
    p.remove_property(prop1) # Branch: remove non-existent doesn't crash
    assert p.count_properties() == 0

