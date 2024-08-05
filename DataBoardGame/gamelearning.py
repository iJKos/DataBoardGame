"""
This module contains classes and functions for implementing a Q-Learning player
and a game farm for training multiple Q-Learning players in parallel.
"""

from random import randint, random, shuffle
from DataBoardGame.game import Action, Game, Player
from DataBoardGame.utils import split_list_into_chunks


class QLearningPlayer(Player):
    """Class representing a player that uses Q-Learning for decision making."""

    q_learning_table: dict

    def __init__(self, learning_rate: float, discount_factor: float, random_rate: float) -> None:
        """Initialize the QLearningPlayer with learning parameters."""
        super().__init__()
        self.q_learning_table = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.random_rate = random_rate

    def decision(self, game_state, action_list: list[Action]) -> Action:
        """Make a decision based on the game state and action list."""
        if game_state not in self.q_learning_table:
            self.q_learning_table[game_state] = {action: 0 for action in action_list}
        else:
            for action in action_list:
                if action not in self.q_learning_table[game_state]:
                    self.q_learning_table[game_state][action] = 0

        if self.last_state and self.last_state != game_state:
            self.update_q_table(game_state)

        if random() < (1 - self.random_rate):
            _, max_action = self.find_max_reward_action(game_state)
            if max_action:
                return max_action

        i = randint(0, len(action_list) - 1)
        return action_list[i]

    def find_max_reward_action(self, game_state):
        """Find the action with the maximum reward for the given game state."""
        max_reward = float('-inf')
        max_action = None
        for action, reward in self.q_learning_table[game_state].items():
            if reward > max_reward:
                max_reward = reward
                max_action = action

        return max_reward, max_action

    def update_q_table(self, game_state):
        """Update the Q-Table based on the game state and last action."""
        reward = game_state.calc_value() - self.last_state.calc_value()
        max_potential_reward, _ = self.find_max_reward_action(game_state)
        current_q_value = self.q_learning_table[self.last_state][self.last_action]

        updated_q_value = (1 - self.learning_rate) * current_q_value + self.learning_rate * (reward + self.discount_factor * max_potential_reward)

        self.q_learning_table[self.last_state][self.last_action] = updated_q_value


class GameFarm:
    """Class representing a farm for running multiple games in parallel with Q-Learning players."""

    number_of_players_per_game: int
    players: list[Player]
    game_results = []

    def __init__(self, number_of_players_per_game: int, parallel: int) -> None:
        """Initialize the GameFarm with the number of players per game and parallel games."""
        self.number_of_players_per_game = number_of_players_per_game
        self.parallel = parallel
        self.number_of_players = number_of_players_per_game * parallel
        self.players = []

        for _ in range(self.number_of_players):
            self.players.append(QLearningPlayer(learning_rate=0.8 + random() * 0.1, discount_factor=0.8 + random() * 0.1, random_rate=random() * 0.1))

    def learn(self):
        """Run the learning process for the players."""
        shuffle(self.players)
        player_chunks = split_list_into_chunks(self.players, self.number_of_players_per_game)

        for i in range(self.parallel):
            self.make_learning(player_chunks[i])

    def make_learning(self, players: list[Player]):
        """Run a learning game for the given list of players."""
        game = Game()

        for player in players:
            game.add_player(player)

        game.play()

    def merge_q_tables(self) -> dict:
        """Merge the Q-tables of all players."""
        res = {}
        for player in self.players:
            for state, actions in player.q_learning_table.items():
                if state not in res:
                    res[state] = actions.copy()
                else:
                    for action, value in actions.items():
                        if action not in res[state]:
                            res[state][action] = value
                        else:
                            res[state][action] += value
        return res

    def merge_best_decision_state(self) -> dict:
        """Merge the best decision states of all players."""
        res = {}
        for player in self.players:
            for state, actions in player.best_decision_state.items():
                if state not in res:
                    res[state] = actions.copy()
                else:
                    for action, value in actions.items():
                        if action not in res[state]:
                            res[state][action] = value
                        else:
                            res[state][action] = max(res[state][action], value)
        return res
