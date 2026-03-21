import pytest
from moneypoly.game import Game
from moneypoly.player import Player
from unittest.mock import patch
import io

def test_game_initialization():
    g = Game(["Alice", "Bob"])
    assert len(g.players) == 2
    assert g.turn_number == 0

def test_game_current_player():
    g = Game(["A", "B"])
    assert g.current_player().name == "A"
    g.advance_turn()
    assert g.current_player().name == "B"

def test_game_check_bankruptcy_wrap_around():
    """Branch coverage: if current index wraps around list size during bankrupt checks."""
    g = Game(["A", "B", "C"])
    g.current_index = 2
    g.players[2].deduct_money(g.players[2].balance + 10)
    g._check_bankruptcy(g.players[2])
    # index was 2, length is now 2. index subtracts to 1.
    assert g.current_index == 1
    assert len(g.players) == 2

def test_game_apply_card_branches():
    """100% Branch coverage for applying card actions."""
    g = Game(["A", "B"])
    p = g.players[0]
    
    g._apply_card(p, None) # Null card branch
    
    # Pay card
    g._apply_card(p, {"description": "Tax", "action": "pay", "value": 100})
    assert p.balance == 1400
    
    # Collect flat amount from bank
    g._apply_card(p, {"description": "Inherit", "action": "collect", "value": 200})
    assert p.balance == 1600
    
    # Jail action
    g._apply_card(p, {"description": "Jail", "action": "jail", "value": 0})
    assert p.in_jail is True
    
    # Move to card
    # move to Boardwalk (39).
    with patch("builtins.input", return_value="s"):
        g._apply_card(p, {"description": "Boardwalk", "action": "move_to", "value": 39})
    assert p.position == 39

def test_game_buy_property_branches():
    g = Game(["A"])
    p = g.players[0]
    prop = g.board.get_property_at(1)
    
    # Can afford
    success = g.buy_property(p, prop)
    assert success is True
    assert p.balance == 1440
    
    # Can't afford
    prop2 = g.board.get_property_at(39) # 400
    p.deduct_money(1400) # balance is now 40
    success = g.buy_property(p, prop2)
    assert success is False

def test_game_mortgage_branches():
    g = Game(["A", "B"])
    pA = g.players[0]
    pB = g.players[1]
    prop = g.board.get_property_at(1)
    
    success = g.mortgage_property(pA, prop)
    assert success is False # Player A doesn't own it
    
    g.buy_property(pA, prop)
    success = g.mortgage_property(pA, prop)
    assert success is True # Successfully mortgaged
    
    success = g.mortgage_property(pA, prop)
    assert success is False # Already mortgaged
