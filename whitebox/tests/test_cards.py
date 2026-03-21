import pytest
from moneypoly.cards import CardDeck, CHANCE_CARDS

def test_carddeck_initialization():
    deck = CardDeck(CHANCE_CARDS)
    assert len(deck) == len(CHANCE_CARDS)
    assert deck.cards_remaining() == len(CHANCE_CARDS)

def test_carddeck_draw_and_peek():
    cards = [{"action": "a"}, {"action": "b"}]
    deck = CardDeck(cards)
    
    assert deck.peek() == {"action": "a"}
    assert deck.draw() == {"action": "a"}
    assert deck.draw() == {"action": "b"}
    # Verify cyclic draw
    assert deck.draw() == {"action": "a"}
    assert deck.cards_remaining() == 1  # 2 - (3 % 2) = 1

def test_carddeck_empty():
    deck = CardDeck([])
    assert deck.draw() is None
    assert deck.peek() is None

def test_carddeck_reshuffle(monkeypatch):
    deck = CardDeck([{"id": 1}, {"id": 2}, {"id": 3}])
    deck.draw() # index becomes 1
    deck.reshuffle()
    assert deck.index == 0
    assert len(deck) == 3
