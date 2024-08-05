"""
This module contains classes and functions related to a Data Board Game.
It includes resource management, card deck handling, and employee roles.
"""

from enum import IntEnum
import queue
import copy
from DataBoardGame.utils import create_queue_from_list, random_sort_queue
from DataBoardGame.resources import ResourceType, ResourceConvertion, Resources, money_pay


class CardDeck:
    """Class representing a deck of cards."""

    open_size: int
    card_queue: queue.Queue
    open_cards: list
    trash_card: list
    all_cards: list

    def __init__(self, open_size: int, cards: list) -> None:
        """Initialize the CardDeck with a given size and list of cards."""
        self.open_size = open_size
        self.card_queue = create_queue_from_list(cards)
        self.open_cards = []
        self.trash_card = []
        self.all_cards = cards

    def __str__(self) -> str:
        """Return a string representation of the CardDeck."""
        return f'q:{self.card_queue.qsize()} o:{len(self.open_cards)} t:{len(self.trash_card)}'

    def __deepcopy__(self, memo):
        """Create a deep copy of the CardDeck."""
        new_card_deck = CardDeck(self.open_size, cards=self.all_cards)

        # Use deepcopy for all attributes except card_queue
        new_card_deck.open_cards = copy.copy(self.open_cards)
        new_card_deck.trash_card = copy.copy(self.trash_card)
        new_card_deck.all_cards = copy.copy(self.all_cards)

        # Manually copy the queue elements
        new_card_deck.card_queue = queue.Queue()
        for item in list(self.card_queue.queue):
            new_card_deck.card_queue.put(item)

        return new_card_deck

    def to_dict(self):
        """Convert the CardDeck to a dictionary representation."""
        card_flags = {}
        for card in self.all_cards:
            card_flags[str(card.__hash__()) + '_open'] = card in self.open_cards
            card_flags[str(card.__hash__()) + '_trash'] = card in self.trash_card

        return {'card_flags': card_flags}

    def __hash__(self) -> int:
        """Generate a hash for the CardDeck."""
        return hash((tuple(sorted(self.all_cards)), tuple(sorted(self.open_cards)), tuple(sorted(self.trash_card))))

    def __eq__(self, other) -> bool:
        """Check equality between two CardDeck objects."""
        if not isinstance(other, CardDeck):
            return NotImplemented
        return self.all_cards == other.all_cards and self.open_cards == other.open_cards and self.trash_card == other.trash_card

    def pre_game_init(self):
        """Initialize the card deck before starting the game."""
        self.reopen_cards()

    def get_closed_card(self):
        """Get a closed card from the queue."""
        return self.card_queue.get()

    def return_card(self, card):
        """Return a card to the trash pile."""
        self.trash_card.append(card)

    def move_open_cards_to_trash(self):
        """Move all open cards to the trash pile."""
        self.trash_card.extend(self.open_cards)
        self.open_cards.clear()

    def reopen_cards(self):
        """Reopen cards to match the open size."""
        self.move_open_cards_to_trash()
        while len(self.open_cards) < self.open_size:
            self.open_card()

    def move_trash_cards_to_queue(self):
        """Move all trash cards back to the queue and shuffle them."""
        self.card_queue = random_sort_queue(create_queue_from_list(self.trash_card + list(self.card_queue.queue)))
        self.trash_card.clear()

    def get_open_card(self, card):
        """Get an open card and replace it with a new one."""
        self.open_cards.remove(card)
        self.open_card()
        if self.card_queue.qsize() == 0:
            self.move_trash_cards_to_queue()
        return card

    def open_card(self):
        """Open a new card from the queue."""
        if self.card_queue.qsize() == 0:
            self.move_trash_cards_to_queue()
        self.open_cards.append(self.card_queue.get())
        if self.card_queue.qsize() == 0:
            self.move_trash_cards_to_queue()


EmployeeRoles = IntEnum('EmployeeRoles', 'DE SA BI BA PM')


def basic_resource_conversion(coef):
    """Create a dictionary of basic resource conversions based on a coefficient."""
    return {
        EmployeeRoles.DE: ResourceConvertion(resources_to_take=Resources(), resource_to_give=Resources(raw_data=coef)),
        EmployeeRoles.BI: ResourceConvertion(resources_to_take=Resources(marts=coef), resource_to_give=Resources(dashboards=coef)),
        EmployeeRoles.BA: ResourceConvertion(resources_to_take=Resources(dashboards=coef), resource_to_give=Resources(insights=coef)),
        EmployeeRoles.SA: ResourceConvertion(resources_to_take=Resources(raw_data=coef), resource_to_give=Resources(marts=coef)),
    }


class EmloyeeCard:
    """Class representing an employee card with role, salary, and resource conversion."""

    basic_resource_conversion = basic_resource_conversion(1)
    role: EmployeeRoles
    salary: ResourceConvertion = money_pay(1)
    umotivated_salary: ResourceConvertion = money_pay(3)
    _hash: int = None

    def __init__(self, role: EmployeeRoles, salary, basic_resource_conversion=None) -> None:
        """Initialize the EmloyeeCard with a role, salary, and optional resource conversion."""
        self.role = role
        if basic_resource_conversion:
            self.basic_resource_conversion = basic_resource_conversion
        self.salary = money_pay(salary)
        self._hash = hash(self)

    def __lt__(self, other):
        """Compare two EmloyeeCard objects by their hash values."""
        if not isinstance(other, EmloyeeCard):
            return NotImplemented
        return self._hash < other._hash

    def to_dict(self):
        """Convert the EmloyeeCard to a dictionary representation."""
        res = {}
        res['basic_resource_conversion'] = {str(key): value.to_dict() for key, value in self.basic_resource_conversion.items()}
        res['role'] = str(self.role)
        res['salary'] = self.salary.to_dict()
        return res

    def __eq__(self, other) -> bool:
        """Check equality between two EmloyeeCard objects."""
        if not isinstance(other, EmloyeeCard):
            return NotImplemented
        if self._hash:
            return self._hash == other._hash
        return self.basic_resource_conversion == other.basic_resource_conversion and self.role == other.role and self.salary == other.salary

    def __hash__(self) -> int:
        """Generate a hash for the EmloyeeCard."""
        if self._hash:
            return self._hash
        return hash((self.role, self.salary, frozenset(sorted(self.basic_resource_conversion.items()))))


employee_card_list = [
    EmloyeeCard(EmployeeRoles.DE, 0, basic_resource_conversion(1)),
    EmloyeeCard(EmployeeRoles.DE, 0, basic_resource_conversion(1)),
    EmloyeeCard(EmployeeRoles.DE, 1, basic_resource_conversion(1)),
    EmloyeeCard(EmployeeRoles.DE, 1, basic_resource_conversion(1)),
    EmloyeeCard(EmployeeRoles.DE, 2, basic_resource_conversion(2)),
    EmloyeeCard(EmployeeRoles.DE, 2, basic_resource_conversion(2)),
    EmloyeeCard(EmployeeRoles.DE, 3, basic_resource_conversion(3)),
    EmloyeeCard(EmployeeRoles.DE, 3, basic_resource_conversion(3)),
    EmloyeeCard(EmployeeRoles.DE, 4, basic_resource_conversion(4)),
    EmloyeeCard(EmployeeRoles.DE, 4, basic_resource_conversion(4)),
    EmloyeeCard(EmployeeRoles.DE, 5, basic_resource_conversion(5)),
    EmloyeeCard(EmployeeRoles.DE, 5, basic_resource_conversion(5)),
    EmloyeeCard(EmployeeRoles.SA, 0, basic_resource_conversion(1)),
    EmloyeeCard(EmployeeRoles.SA, 0, basic_resource_conversion(1)),
    EmloyeeCard(EmployeeRoles.SA, 1, basic_resource_conversion(1)),
    EmloyeeCard(EmployeeRoles.SA, 1, basic_resource_conversion(1)),
    EmloyeeCard(EmployeeRoles.SA, 2, basic_resource_conversion(2)),
    EmloyeeCard(EmployeeRoles.SA, 2, basic_resource_conversion(2)),
    EmloyeeCard(EmployeeRoles.SA, 3, basic_resource_conversion(3)),
    EmloyeeCard(EmployeeRoles.SA, 3, basic_resource_conversion(3)),
    EmloyeeCard(EmployeeRoles.SA, 4, basic_resource_conversion(4)),
    EmloyeeCard(EmployeeRoles.SA, 4, basic_resource_conversion(4)),
    EmloyeeCard(EmployeeRoles.SA, 5, basic_resource_conversion(5)),
    EmloyeeCard(EmployeeRoles.SA, 5, basic_resource_conversion(5)),
    EmloyeeCard(EmployeeRoles.BA, 0, basic_resource_conversion(1)),
    EmloyeeCard(EmployeeRoles.BA, 0, basic_resource_conversion(1)),
    EmloyeeCard(EmployeeRoles.BA, 1, basic_resource_conversion(1)),
    EmloyeeCard(EmployeeRoles.BA, 1, basic_resource_conversion(1)),
    EmloyeeCard(EmployeeRoles.BA, 2, basic_resource_conversion(2)),
    EmloyeeCard(EmployeeRoles.BA, 2, basic_resource_conversion(2)),
    EmloyeeCard(EmployeeRoles.BA, 3, basic_resource_conversion(3)),
    EmloyeeCard(EmployeeRoles.BA, 3, basic_resource_conversion(3)),
    EmloyeeCard(EmployeeRoles.BA, 4, basic_resource_conversion(4)),
    EmloyeeCard(EmployeeRoles.BA, 4, basic_resource_conversion(4)),
    EmloyeeCard(EmployeeRoles.BA, 5, basic_resource_conversion(5)),
    EmloyeeCard(EmployeeRoles.BA, 5, basic_resource_conversion(5)),
    EmloyeeCard(EmployeeRoles.BI, 0, basic_resource_conversion(1)),
    EmloyeeCard(EmployeeRoles.BI, 0, basic_resource_conversion(1)),
    EmloyeeCard(EmployeeRoles.BI, 1, basic_resource_conversion(1)),
    EmloyeeCard(EmployeeRoles.BI, 1, basic_resource_conversion(1)),
    EmloyeeCard(EmployeeRoles.BI, 2, basic_resource_conversion(2)),
    EmloyeeCard(EmployeeRoles.BI, 2, basic_resource_conversion(2)),
    EmloyeeCard(EmployeeRoles.BI, 3, basic_resource_conversion(3)),
    EmloyeeCard(EmployeeRoles.BI, 3, basic_resource_conversion(3)),
    EmloyeeCard(EmployeeRoles.BI, 4, basic_resource_conversion(4)),
    EmloyeeCard(EmployeeRoles.BI, 4, basic_resource_conversion(4)),
    EmloyeeCard(EmployeeRoles.BI, 5, basic_resource_conversion(5)),
    EmloyeeCard(EmployeeRoles.BI, 5, basic_resource_conversion(5)),
]
