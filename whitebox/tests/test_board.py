import pytest
from moneypoly.board import Board
from moneypoly.player import Player

def test_board_initialization():
    board = Board()
    assert len(board.properties) == 22
    assert len(board.groups) == 8

def test_board_get_property_at():
    board = Board()
    prop = board.get_property_at(1)
    assert prop is not None
    assert prop.name == "Mediterranean Avenue"
    
    # Non-property tile
    assert board.get_property_at(0) is None
    assert board.get_property_at(99) is None

def test_board_get_tile_type():
    board = Board()
    assert board.get_tile_type(0) == "go"
    assert board.get_tile_type(1) == "property"
    assert board.get_tile_type(2) == "community_chest"
    assert board.get_tile_type(4) == "income_tax"
    assert board.get_tile_type(5) == "railroad"
    assert board.get_tile_type(38) == "luxury_tax"
    assert board.get_tile_type(99) == "blank"

def test_board_is_purchasable():
    board = Board()
    assert board.is_purchasable(1) is True # Unowned property
    assert board.is_purchasable(0) is False # Special tile
    
    prop = board.get_property_at(1)
    prop.owner = Player("A")
    assert board.is_purchasable(1) is False # Owned property
    
    prop.owner = None
    prop.is_mortgaged = True
    assert board.is_purchasable(1) is False # Mortgaged property

def test_board_is_special_tile():
    board = Board()
    assert board.is_special_tile(0) is True
    assert board.is_special_tile(1) is False

def test_board_properties_queries():
    board = Board()
    player = Player("A")
    assert len(board.unowned_properties()) == 22
    assert len(board.properties_owned_by(player)) == 0
    
    prop = board.get_property_at(1)
    prop.owner = player
    assert len(board.properties_owned_by(player)) == 1
    assert len(board.unowned_properties()) == 21
