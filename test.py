from azul import Azul, PlayerBoard, TileFactory
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

def test_save_tiles_to_pile():
    board = PlayerBoard()
    board.wall[0][1] = Azul.BLUE
    with pytest.raises(OverflowError):
        board.save_tiles_to_pile(0, Azul.BLUE, 1)
    board.save_tiles_to_pile(0, Azul.RED, 1)

def test_tile_factory():
    fac = TileFactory()
    assert len(fac.tiles) == 4

def test_piles_that_can_receive_color():
    game = Azul()
    board = game.boards[game.player]
    assert board.piles_that_can_receive_color(Azul.BLUE) == [0, 1, 2, 3, 4]
    assert board.piles_that_can_receive_color(Azul.RED) == [0, 1, 2, 3, 4]
    assert board.piles_that_can_receive_color(Azul.YELLOW) == [0, 1, 2, 3, 4]
    assert board.piles_that_can_receive_color(Azul.WHITE) == [0, 1, 2, 3, 4]
    assert board.piles_that_can_receive_color(Azul.BLACK) == [0, 1, 2, 3, 4]

    board.save_tiles_to_pile(0, Azul.BLUE, 1)
    assert board.piles_that_can_receive_color(Azul.BLUE) == [1, 2, 3, 4]
    board.save_tiles_to_pile(1, Azul.RED, 1)
    assert board.piles_that_can_receive_color(Azul.RED) == [1, 2, 3, 4]
    board.save_tiles_to_pile(1, Azul.RED, 1)
    assert board.piles_that_can_receive_color(Azul.RED) == [2, 3, 4]
    board.save_tiles_to_pile(2, Azul.BLACK, 1)
    assert board.piles_that_can_receive_color(Azul.RED) == [3, 4]
    assert board.piles_that_can_receive_color(Azul.BLACK) == [2, 3, 4]

def test_available_actions():
    game = Azul()
    board = game.boards[game.player]
    actions = game.available_actions(board, game.factories, game.floor)
    for (color, factory_or_floor, pile) in actions:
        if type(factory_or_floor) == TileFactory:
            assert color in factory_or_floor.tiles

    # l = sorted(list(actions), key=lambda item: (item[0], item[1].tiles, item[2]))
    # print(l)

def test_has_entire_horizontal_row():
    game = Azul()
    board = game.boards[game.player]
    assert not board.has_entire_horizontal_row()
    board.wall[0][0] = Azul.BLUE
    board.wall[0][1] = Azul.RED
    board.wall[0][2] = Azul.BLACK
    board.wall[0][3] = Azul.WHITE
    assert not board.has_entire_horizontal_row()
    board.wall[0][4] = Azul.YELLOW
    assert board.has_entire_horizontal_row()

# def test_best_future_reward():
    # ai = NimAI()
    # assert ai.best_future_reward([1,3,5,7]) == 0
    # ai.q[(1,3,5,7),(1,3)] = 3
    # assert ai.best_future_reward([1,3,5,7]) == 3
    # ai.q[(1,3,5,7),(2,1)] = 7
    # ai.q[(1,3,5,7),(0,1)] = 4
    # assert ai.best_future_reward([1,3,5,7]) == 7