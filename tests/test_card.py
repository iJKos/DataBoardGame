import pytest
from DataBoardGame.utils import create_queue_from_list, random_sort_queue
from DataBoardGame.resources import Resources, ResourceType
from DataBoardGame.card import CardDeck  

def test_card_deck_initialization():
    cards = [1, 2, 3, 4, 5]
    deck = CardDeck(open_size=3, cards=cards)
    assert deck.open_size == 3
    assert deck.card_queue.qsize() == 5
    assert deck.open_cards == []
    assert deck.trash_card == []
    assert deck.all_cards == cards

def test_card_deck_pre_game_init():
    cards = [1, 2, 3, 4, 5]
    deck = CardDeck(open_size=3, cards=cards)
    deck.pre_game_init()
    assert len(deck.open_cards) == 3
    assert len(deck.trash_card) == 0

def test_card_deck_get_closed_card():
    cards = [1, 2, 3, 4, 5]
    deck = CardDeck(open_size=3, cards=cards)
    card = deck.get_closed_card()
    assert card in cards
    assert deck.card_queue.qsize() == 4

def test_card_deck_return_card():
    cards = [1, 2, 3, 4, 5]
    deck = CardDeck(open_size=3, cards=cards)
    card = deck.get_closed_card()
    deck.return_card(card)
    assert card in deck.trash_card

def test_card_deck_move_open_cards_to_trash():
    cards = [1, 2, 3, 4, 5]
    deck = CardDeck(open_size=3, cards=cards)
    deck.pre_game_init()
    deck.move_open_cards_to_trash()
    assert len(deck.open_cards) == 0
    assert len(deck.trash_card) == 3

def test_card_deck_reopen_cards():
    cards = [1, 2, 3, 4, 5]
    deck = CardDeck(open_size=3, cards=cards)
    deck.pre_game_init()
    deck.reopen_cards()
    assert len(deck.open_cards) == 3
    assert len(deck.trash_card) == 0

def test_card_deck_move_trash_cards_to_queue():
    cards = [1, 2, 3, 4, 5]
    deck = CardDeck(open_size=3, cards=cards)
    deck.pre_game_init()
    deck.move_open_cards_to_trash()
    deck.move_trash_cards_to_queue()
    assert deck.card_queue.qsize() == 5
    assert len(deck.trash_card) == 0

def test_card_deck_get_open_card():
    cards = [1, 2, 3, 4, 5]
    deck = CardDeck(open_size=3, cards=cards)
    deck.pre_game_init()
    open_card = deck.open_cards[0]
    retrieved_card = deck.get_open_card(open_card)
    assert retrieved_card == open_card
    assert open_card not in deck.open_cards

def test_card_deck_open_card():
    cards = [1, 2, 3, 4, 5]
    deck = CardDeck(open_size=3, cards=cards)
    deck.open_card()