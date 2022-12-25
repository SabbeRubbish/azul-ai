from azul import Azul, PlayerBoard
import pytest

def test_save_tiles_to_pile():
    board = PlayerBoard()
    board.save_tiles_to_pile(0, Azul.BLUE, 1)
    assert board.piles[0] == {"color": Azul.BLUE, "count": 1}
    with pytest.raises(OverflowError):
        board.save_tiles_to_pile(0, Azul.BLUE, 1)
    assert board.piles[0] == {"color": Azul.BLUE, "count": 1}
    assert board.piles[1] == {"color": Azul.EMPTY, "count": 0}
    with pytest.raises(ValueError):
        board.save_tiles_to_pile(1, Azul.BLUE, 1)
    board.save_tiles_to_pile(4, Azul.RED, 5)
    assert board.piles[4] == {"color": Azul.RED, "count": 5}
    board.save_tiles_to_pile(2, Azul.WHITE, 1)
    with pytest.raises(ValueError):
        board.save_tiles_to_pile(2, Azul.BLACK, 1)
    assert board.piles[2] == {"color": Azul.WHITE, "count": 1}
    print(board)

# def test_best_future_reward():
    # ai = NimAI()
    # assert ai.best_future_reward([1,3,5,7]) == 0
    # ai.q[(1,3,5,7),(1,3)] = 3
    # assert ai.best_future_reward([1,3,5,7]) == 3
    # ai.q[(1,3,5,7),(2,1)] = 7
    # ai.q[(1,3,5,7),(0,1)] = 4
    # assert ai.best_future_reward([1,3,5,7]) == 7