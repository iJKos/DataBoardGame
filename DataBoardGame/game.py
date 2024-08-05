from DataBoardGame.board import GameBoard, PlayerBoard, PlayerDeck
from random import randint
from DataBoardGame.utils import log, make_dict_hashable
from DataBoardGame.resources import ResourceType
from functools import wraps
from typing import List, Callable
from DataBoardGame import globalvars as glb
from dataclasses import dataclass
import copy


class Action:
    """
    A class to encapsulate an Player action consisting of a function and its parameters.
    """

    _game: 'Game'
    _params: dict
    _player: 'Player'
    _hash: int = None

    def __init__(self, game, player, params):
        self._game = game
        self._params = params
        self._player = player
        self._hash = hash(self)

    def action(self, player, **kwargs):
        raise NotImplemented()

    def call_function(self):
        self.action(player=self._player, **self._params)

    def __str__(self):
        return f'{type(self).__name__}(params={self._params})'

    def __hash__(self):
        if self._hash:
            return self._hash
        return hash((type(self).__name__, frozenset(sorted(self._params.items()))))

    def __eq__(self, other):
        if not isinstance(other, Action):
            return NotImplemented

        return type(self).__name__ == type(other).__name__ and self._hash == other._hash

    def to_dict(self):
        res = {}

        for key, value in self._params.items():
            if hasattr(value, 'to_dict'):
                res[str(key)] = value.to_dict()
            else:
                res[str(key)] = str(value)

        return {'action_params': res, 'action_type': type(self).__name__}


class GenerateRsourceAction(Action):
    def action(self, player, resource_type):
        self._game.players_board[player].action_pay_resource_to_player(resource_type)


class HireEmployeeAction(Action):
    def action(self, player, employee, role):
        self._game.players_board[player].hire_employee(employee, role)
        self._game.game_board.employee_deck.get_open_card(employee)


class FireEmployeeAction(Action):
    def action(self, player, employee, role):
        self._game.players_board[player].fire_employee(employee)
        self._game.game_board.employee_deck.return_card(employee)


class EmptyAction(Action):
    def __init__(self, game=None, player=None, params={}):
        super().__init__(game, player, params)

    def action(self, player):
        pass


class GameState:
    """
    A class to represent the state of the game, including the game board,
    player board, and player deck.

    Attributes
    ----------
    game_board : GameBoard
        The state of the game board.
    player_board : PlayerBoard
        The state of the player's board.
    player_deck : PlayerDeck
        The state of the player's deck.
    """

    _hash: int = None
    _dict: dict = None
    _value: float = None

    def __init__(self, game_board: GameBoard, player_board: PlayerBoard, player_deck: PlayerDeck) -> None:
        self.game_board = game_board
        self.player_board = player_board
        self.player_deck = player_deck
        self._dict = self.to_dict()
        self._hash = hash(self)
        self._value = self.calc_value()

    def to_dict(self):
        if self._dict:
            return self._dict

        self._dict = {}
        self._dict.update(self.game_board.to_dict())
        self._dict.update(self.player_board.to_dict())
        self._dict.update(self.player_deck.to_dict())
        self._dict['state_value'] = self.calc_value()
        return self._dict

    def calc_value(self):
        if self._value:
            return self._value
        return (
            self.player_board.resources.money * 100.0
            + (
                self.player_board.resources.dashboards
                + self.player_board.resources.marts
                + self.player_board.resources.insights
                + self.player_board.resources.raw_data
            )
            * 5
            + self.player_board.employees_count()
        )

    def __hash__(self) -> int:
        if self._hash:
            return self._hash
        return hash((self.game_board, self.player_board, self.player_deck))

    def __eq__(self, other):
        if not isinstance(other, GameState):
            return NotImplemented

        if self._hash:
            return self._hash == other._hash  # and self._dict==other._dict

        return self.game_board == other.game_board and self.player_board == other.player_board and self.player_deck == other.player_deck


class Player:
    is_winner = False
    decision_history = {}
    observation_history = {}
    best_decision_state = {}

    last_state = None
    last_action = None
    max_game_value = 0

    def __init__(self) -> None:
        """
        Initialize the Player object with an empty decision history.
        """
        self.decision_history = {}  # Dictionary to store decision history
        self.observation_history = {}  # Dictionary to store observation history
        self.best_decision_state = {}
        self.max_game_value = 0

        self.last_state = None
        self.last_action = None
        self.is_winner = False

    def pre_game_init(self):
        self.max_game_value = 0
        self.decision_history = {}
        self.is_winner = False
        pass

    def make_decision(self, game_state, action_list: list[Action]) -> Action:
        if self.last_state:
            if self.last_state in self.observation_history:
                self.observation_history[self.last_state][self.last_action] = game_state
            else:
                self.observation_history[self.last_state] = {self.last_action: game_state}

        action = self.decision(game_state, action_list)

        self.max_game_value = max(game_state.calc_value(), self.max_game_value)

        self.decision_history[game_state] = action

        self.last_state = game_state
        self.last_action = action

        return action

    def post_gamme_init(self):
        for state, action in self.decision_history.items():
            if state not in self.best_decision_state:
                self.best_decision_state[state] = {}

            if action not in self.best_decision_state[state]:
                self.best_decision_state[state][action] = self.max_game_value

            else:
                self.best_decision_state[state][action] = max(self.best_decision_state[state][action], self.max_game_value)

    def decision(self, game_state, action_list: list[Action]) -> Action:
        raise NotImplementedError()


class RandomPlayer(Player):
    def decision(self, game_state, action_list: list[Action]) -> Action:
        i = randint(0, len(action_list) - 1)
        return action_list[i]


class Game:
    players_board: dict[Player, PlayerBoard]
    players_deck: dict[Player, PlayerDeck]
    game_board: GameBoard
    players: list[Player]

    current_round: int
    current_player: Player
    current_player_index: int

    def __init__(self) -> None:
        self.players = []
        self.players_board = {}
        self.players_deck = {}
        self.game_board = {}
        self.current_round = 0
        self.game_board = GameBoard()
        self.game_log = []

        pass

    def get_current_player_state(self) -> GameState:
        return self.get_player_state(self.current_player)

    def get_player_state(self, player: Player) -> GameState:
        return GameState(self.game_board, self.players_board[player], self.players_deck[player])

    def add_player(self, new_player: Player) -> None:
        self.players.append(new_player)

    def pre_game_init(self) -> None:
        for player in self.players:
            self.players_board[player] = PlayerBoard()
            self.players_deck[player] = PlayerDeck()
            player.pre_game_init()

        self.game_board.pre_game_init()
        self.game_log = []

        self.current_player = self.players[0]
        self.current_player_index = 0

    def generate_available_resource_actions(self, player, is_mandotory: bool = False):
        res_actions = []
        for item in ResourceType:
            if item == ResourceType.money:
                continue
            if self.players_board[player].check_pay_resource_to_player(item):
                res_actions.append(GenerateRsourceAction(self, player, {'resource_type': item}))

        if len(res_actions) == 0 or not is_mandotory:
            res_actions.append(EmptyAction())
        return res_actions

    def generate_available_employee_hire_actions(self, player, is_mandotory: bool = False):
        res_actions = []

        for card in self.game_board.employee_deck.open_cards:
            for role in self.players_board[player].get_available_roles():
                res_actions.append(HireEmployeeAction(self, player, {'employee': card, 'role': role}))

        if len(res_actions) == 0 or not is_mandotory:
            res_actions.append(EmptyAction())
        return res_actions

    def generate_available_employee_fire_actions(self, player, is_mandotory: bool = False):
        res_actions = [EmptyAction()]
        if not is_mandotory:
            res_actions.clear()

        for employee, role in self.players_board[player].get_employee_list():
            res_actions.append(FireEmployeeAction(self, player, {'employee': employee, 'role': role}))

        if len(res_actions) == 0 or not is_mandotory:
            res_actions.append(EmptyAction())

        return res_actions

    def log_player_state(self, player):
        log(f'\t player {self.players.index(player)}\n {self.players_board[player]}')

    def action_game_step(self, step_name, player, action_gen_function, is_mandotory=False):
        log(f'Game step: {step_name}')
        log(f'{self.game_board}')
        decision = player.make_decision(self.get_player_state(player), action_gen_function(player, is_mandotory))
        log(decision)
        decision.call_function()
        self.log_player_state(player)

    def next_game_step(self) -> int:
        log('')
        log(f'Game round {self.current_round} player {self.current_player_index}')
        for player in self.players:
            self.log_player_state(player)

        log(f'Game step: Money gain')
        self.players_board[self.current_player].generate_money()
        self.log_player_state(self.current_player)

        self.action_game_step('Resource decision', self.current_player, self.generate_available_resource_actions)

        self.action_game_step('Employee hire decision', self.current_player, self.generate_available_employee_hire_actions)

        self.action_game_step('Employee fire decision', self.current_player, self.generate_available_employee_fire_actions)

        while not self.players_board[self.current_player].check_is_salary_available():
            self.action_game_step(
                'Employee fire decision',
                self.current_player,
                self.generate_available_employee_fire_actions,
                is_mandotory=True,
            )

        log(f'Game step: Salary')
        self.players_board[self.current_player].pay_salary()
        self.log_player_state(self.current_player)

        self.current_player_index += 1
        if self.current_player_index == len(self.players):
            self.current_player_index = 0
            self.current_round += 1

        self.current_player = self.players[self.current_player_index]

        return self.is_game_over()

    def is_game_over(self):
        for player in self.players:
            if self.players_board[player].resources.money > glb.MONEY_TO_STOP:
                log(f'player {self.players.index(player)} gets {glb.MONEY_TO_STOP} money')
                player.is_winner = True
                return True

        if self.current_round >= glb.ROUND_TO_STOP:
            return True

        return False

    def post_game_init(self):
        for player in self.players:
            player.post_gamme_init()

    def play(self):
        self.pre_game_init()

        while not self.is_game_over():
            self.next_game_step()

        self.post_game_init()
