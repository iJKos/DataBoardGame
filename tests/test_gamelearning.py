from DataBoardGame.gamelearning import GameFarm
import pytest


def test_manual_schedule_tag():
    gf = GameFarm(number_of_players_per_game=4, parallel=4)
    
    for i in range(5):
        gf.learn()
