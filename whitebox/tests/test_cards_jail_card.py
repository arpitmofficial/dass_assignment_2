import pytest
from moneypoly.game import Game

def test_jail_free_card_removed_from_deck():
    """
    Test Case: Verify that when a player draws 'Get Out of Jail Free', the card is removed from the deck until used.
    Reason: There are limited copies of this card. If it stays in the deck, players can draw infinite copies of it.
    Expected: The card cannot be drawn again immediately.
    Actual Error Found: The CardDeck just cycles endlessly using modulo arithmetic. It never actually pops/removes the card.
    """
    game = Game(["Alice"])
    alice = game.players[0]
    
    # We rig the chance deck up so the NEXT card is Get Out Of Jail Free
    # Card index 8 in CHANCE_CARDS is "Get Out of Jail Free"
    game.decks["chance"].index = 8
    
    # Draw it!
    card = game.decks["chance"].draw()
    assert card["action"] == "jail_free"
    game._apply_card(alice, card)
    
    # Alice now has 1 card
    assert alice.get_out_of_jail_cards == 1
    
    # Since there are only 12 cards, if we draw 12 more cards, we'll hit that exact spot in the cycle again.
    for _ in range(11):
        game.decks["chance"].draw()
        
    # The 12th card drawn will be the 'Get Out of Jail Free' card AGAIN, even though Alice holds it!
    next_card = game.decks["chance"].draw()
    
    # This will fail because the card is still fundamentally physically locked in the deck list cycle.
    assert next_card["action"] != "jail_free", "Get Out of Jail Free card was drawn again while already held by a player!"
