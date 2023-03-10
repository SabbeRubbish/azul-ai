import math
import random
import time
import sys

random.seed(0)

class TileFactory():
    def __init__(self, is_floor = False):
        """
        Initializes a set of tiles
        Consists of:
        - maximum 4 tiles
        - any tile can be of either color
        """
        self.tiles = []
        self.is_floor = is_floor

        self.produce_tiles()

    def produce_tiles(self):
        """
        Produces 4 tiles
        """
        if not self.is_floor:
            self.tiles = random.choices([Azul.BLUE, Azul.RED, Azul.YELLOW, Azul.WHITE, Azul.BLACK], k=4)
        else:
            self.tiles = [Azul.START_PLAYER_TILE]

    def has_tiles(self):
        return len(self.tiles)

    def take_tiles(self, color):
        """
        Takes all tiles of the given color. Returns the number of tiles of that color.
        """
        result = self.tiles.count(color)
        self.tiles.remove(color)
        return result

    def drop_tiles_on_floor(self, color, num):
        """
        Adds these tiles to the floor
        """
        if not self.is_floor:
            raise TypeError("This factory is not the floor and tiles can't be added to it!")
        self.tiles += [color]*num

    def __str__(self):
        return "".join(self.tiles)
    def __repr__(self):
        return self.__str__()

class PlayerBoard():
    def __init__(self, difficulty = 0):
        """
        Initializes a player's board
        Consists of:
        - a 5x5 2D wall
        - 1, 2, 3, 4, 5 wait piles that allow you to save tiles for use on the wall
        - difficulty: 0 for standard tile board, 1 for no predefined colors allowed on the board
        - foul tiles: tiles that are too many
        """
        self.wall = [[Azul.EMPTY]*5 for i in range(5)]
        self.allowed_colors = [[Azul.EMPTY]*5 for i in range(5)]
        self.piles = {i:{"color": Azul.EMPTY, "count" :0} for i in range(5)}
        self.difficulty = difficulty
        self.foul_tiles = []
        self.score = 0
        
        color_array = [Azul.BLUE, Azul.YELLOW, Azul.RED, Azul.BLACK, Azul.WHITE]
        # Initialize the board allowed colors
        if self.difficulty == 0:
            for i in range(5):
                self.allowed_colors[i] = color_array
                color_array.insert(0, color_array.pop(-1))

    def piles_that_can_receive_color(self, color):
        """
        Returns a list of piles to which the given color can be added
        This depends on 
            whether there is already a pile of that color and it isn't full
            AND 
            whether an empty pile could be used (but that pile should not have )
        """
        allowed_piles = []
        for p in self.piles:
            pile = self.piles[p]
            # Has tiles already of DIFFERENT color -> skip pile
            if pile["count"] > 0 and not pile["color"] == color:
                # print(f"pilecount {pile['count']} > 0 and not pilecolor {pile['color']} == {color}")
                continue
            # Has tiles already of SAME color and NOT full yet
            if pile["count"] > 0 and pile["color"] == color and pile["count"] < p+1:
                # print(f"pilecount {pile['count']} > 0 and colors match and pilecount < {p+1}")
                allowed_piles.append(p)

            # Has no tiles yet AND wall still allows this tile
            if pile["count"] == 0 and not color in self.wall[p]:
                allowed_piles.append(p)
        
        return allowed_piles

    def has_entire_horizontal_row(self):
        return any( (not any(t == Azul.EMPTY for t in row)) for row in self.wall)

    def __str__(self):
        result = ""
        for i in range(5):
            result += "".join(self.wall[i]) + " " + "".join(self.piles[i]["color"] * self.piles[i]["count"]) + "\n"
        return result

    """
    Save a number of tiles to a pile
    Will check that a pile can only contain the amount that is allowed in that pile and that it has the same colors!
    Pile numbering is 0 - 4
    """
    def save_tiles_to_pile(self, pileNumber, tileColor, numberOfTiles):
        pile = self.piles[pileNumber]
        if pile["count"] + numberOfTiles > pileNumber + 1:
            raise OverflowError(f"Pile {pileNumber} is at maximum capacity")
        if pile["count"] > 0 and not pile["color"] == tileColor:
            raise ValueError("This color is not allowed on this pile anymore")
        # Check other tiles don't have the same color
        if tileColor in [self.piles[p]["color"] for p in self.piles if not p == pileNumber]:
            raise ValueError("This color is already present in another pile")
        # Check that this pile doesn't correspond to a line in the wall that already has this color set
        if tileColor in self.wall[pileNumber]:
            raise OverflowError(f"This color is already present on the wall at line {pileNumber}")

        pile["count"] += numberOfTiles
        pile["color"] = tileColor

class Azul():
    BLUE = "????"
    YELLOW = "????"
    RED = "????"
    BLACK = "???"
    WHITE = "???"
    EMPTY = "??????"
    START_PLAYER_TILE = "1??????"

    def __init__(self, num_players = 2, difficulty = 0):
        """
        Initialize game board.
        Each game board has
            - 'player boards': a list of 5x5 2D player boards (one per player)
            - 'number of players': number of players playing (2-4)
            - 'player': 0-4 (but <= number of players) to indicate which player's turn
            - 'winner': array to indicate which players share victory or only 1 if only 1 winner
            - 'factories': piles of max 4 tiles that can be used to take tiles - can be any number of different colors
            - 'floor': tiles that fell on the floor (middle of the board) - can be any number of different colors
            - 'difficuly': 0 for standard tile board, 1 for no predefined colors allowed on the board
        """
        if num_players > 4 or num_players < 2:
            raise ValueError("Number of players must be 2, 3 or 4")
        if difficulty not in [0, 1]:
            raise ValueError("Difficulty must be either 0 or 1")

        self.boards = [PlayerBoard(difficulty) for p in range(1, num_players)]
        self.num_players = num_players
        self.player = 0
        self.winner = None
        self.factories = [TileFactory() for p in range(1, num_players + 5)]
        self.floor = TileFactory(True)
        self.difficulty = difficulty

    @classmethod
    def available_actions(cls, board, factories, floor):
        """
        available_actions(piles) returns all of the available actions '(i, j, k)' in that state (board, factories, floor).

        Action '(i, j, k)' represents the action of removing all items of color 'j'
        from factory 'i' (where factories are 0-indexed, -1 represents the floor) and adding
        them to pile k of this player's board

        STATE = always the current board, all factories and the floor
        """
        actions = set()
        for factory in [f for f in factories if f.has_tiles()]:
            colors = set(factory.tiles)
            for color in colors:
                for pile in board.piles_that_can_receive_color(color):
                    actions.add((color, factory, pile))
        
        floor_colors = set(floor.tiles)
        for color in floor_colors:
            if color == Azul.START_PLAYER_TILE:
                continue # Can't pick up start tile alone
            for pile in board.piles_that_can_receive_color(color):
                actions.add((color, floor, pile))

        return actions

    def next_player(self):
        """
        Switch the current player to the next player.
        """
        self.player = (self.player + 1) % self.num_players

    def move(self, action):
        """
        Make the move 'action' for the current player.
        'action' must be a tuple '(i, j, k)' where i is the color to remove from factory j (-1 for the floor)
        to pile k
        """
        color, factory, pile = action

        # Check for errors
        if self.winner is not None:
            raise Exception("Game already won")
        if len(factory.tiles) <= 0:
            raise Exception("Selected factory has no tiles left")
        if pile < 0 or pile >= len(self.piles):
            raise Exception("Invalid pile")
        if not action in self.available_actions(board, self.factories, self.floor):
            raise Exception("Invalid action")

        board = self.boards[self.player]

        # Update board
        # 1. Set the color (in case it wasn't set yet)
        board.piles[pile]["color"] = color
        # 2. Take tiles from the factory
        count = factory.take_tiles(color)
        # 3. Add them to the board
        board.piles[pile]["count"] += count
        # 4. If taken from the floor
        if factory == self.floor and Azul.START_PLAYER_TILE in self.floor.tiles:
            # Add the START PLAYER tile to the board and remove it from the floor
            self.floor.remove(Azul.START_PLAYER_TILE)
            board.foul_tiles.append(Azul.START_PLAYER_TILE)
        
        self.next_player()
        if self.player == 0:
            self.score_round()

        # Check for a winner
        if self.is_end_game():
            self.score_end_game()
        
        self.winner = max(self.boards, key = lambda b: b.score)

    def is_end_game(self):
        return any(board.has_entire_horizontal_row for board in self.boards)

    def score_round(self):
        for board in self.boards:
            # Go pile by pile
            added_score = 0
            for p in board.piles:
                pile = board.piles[p]
                pile_count = pile["count"]
                pile_color = pile["color"]
                # If the pile is full, shift to the wall
                if pile_count == p + 1:
                    # Shift to the wall
                    idx = board.allowed_colors[p].index(pile_color)
                    board.wall[p][idx] = pile_color
                    # Empty the pile
                    pile["count"] = 0
                    pile["color"] = Azul.EMPTY

                    # Now score
                    # TODO

    def score_end_game(self):

class NimAI():

    def __init__(self, alpha=0.5, epsilon=0.1):
        """
        Initialize AI with an empty Q-learning dictionary,
        an alpha (learning) rate, and an epsilon rate.

        The Q-learning dictionary maps '(state, action)'
        pairs to a Q-value (a number).
         - 'state' is a tuple of remaining piles, e.g. (1, 1, 4, 4)
         - 'action' is a tuple '(i, j)' for an action
        """
        self.q = dict()
        self.alpha = alpha
        self.epsilon = epsilon

    def update(self, old_state, action, new_state, reward):
        """
        Update Q-learning model, given an old state, an action taken
        in that state, a new resulting state, and the reward received
        from taking that action.
        """
        old = self.get_q_value(old_state, action)
        best_future = self.best_future_reward(new_state)
        self.update_q_value(old_state, action, old, reward, best_future)

    def get_q_value(self, state, action):
        """
        Return the Q-value for the state 'state' and the action 'action'.
        If no Q-value exists yet in 'self.q', return 0.
        """
        try:
            return self.q[tuple(state), action]
        except KeyError:
            return 0

    def update_q_value(self, state, action, old_q, reward, future_rewards):
        """
        Update the Q-value for the state 'state' and the action 'action'
        given the previous Q-value 'old_q', a current reward 'reward',
        and an estiamte of future rewards 'future_rewards'.

        Use the formula:

        Q(s, a) <- old value estimate
                   + alpha * (new value estimate - old value estimate)

        where 'old value estimate' is the previous Q-value,
        'alpha' is the learning rate, and 'new value estimate'
        is the sum of the current reward and estimated future rewards.
        """
        new_value = old_q + self.alpha * ( (reward + future_rewards) - old_q)
        self.q[tuple(state), action] = new_value

    def best_future_reward(self, state):
        """
        Given a state 'state', consider all possible '(state, action)'
        pairs available in that state and return the maximum of all
        of their Q-values.

        Use 0 as the Q-value if a '(state, action)' pair has no
        Q-value in 'self.q'. If there are no available actions in
        'state', return 0.
        """
        max = -sys.maxsize
        available_actions = Nim.available_actions(state)
        if len(available_actions) == 0:
            return 0

        for action in available_actions:
            q_value = 0
            try:
                q_value = self.q[tuple(state), action]
            except KeyError:
                pass

            if q_value > max:
                max = q_value

        return max

    def choose_action(self, state, epsilon=True):
        """
        Given a state 'state', return an action '(i, j)' to take.

        If 'epsilon' is 'False', then return the best action
        available in the state (the one with the highest Q-value,
        using 0 for pairs that have no Q-values).

        If 'epsilon' is 'True', then with probability
        'self.epsilon' choose a random available action,
        otherwise choose the best action available.

        If multiple actions have the same Q-value, any of those
        options is an acceptable return value.
        """
        epsilon_to_use = self.epsilon
        if epsilon == False:
            epsilon_to_use = 0
        
        # If epsilon = 0.4, any value UNDER 0.4 is according to epsilon
        if random.random() >= epsilon_to_use:
            return self.get_best_action(state)
        else:
            return self.get_random_action(state)

    def get_best_action(self, state):
        max = -sys.maxsize
        current_best = None
        for action in Nim.available_actions(state):
            q_value = 0
            try:
                q_value = self.q[tuple(state), action]
            except KeyError:
                pass

            if q_value > max:
                max = q_value
                current_best = action
        
        return current_best

    def get_random_action(self, state):
        return random.choice(list(Nim.available_actions(state)))

def train(n):
    """
    Train an AI by playing 'n' games against itself.
    """

    player = NimAI()

    # Play n games
    for i in range(n):
        print(f"Playing training game {i + 1}")
        game = Nim()

        # Keep track of last move made by either player
        last = {
            0: {"state": None, "action": None},
            1: {"state": None, "action": None}
        }

        # Game loop
        while True:

            # Keep track of current state and action
            state = game.piles.copy()
            action = player.choose_action(game.piles)

            # Keep track of last state and action
            last[game.player]["state"] = state
            last[game.player]["action"] = action

            # Make move
            game.move(action)
            new_state = game.piles.copy()

            # When game is over, update Q values with rewards
            if game.winner is not None:
                player.update(state, action, new_state, -1)
                player.update(
                    last[game.player]["state"],
                    last[game.player]["action"],
                    new_state,
                    1
                )
                break

            # If game is continuing, no rewards yet
            elif last[game.player]["state"] is not None:
                player.update(
                    last[game.player]["state"],
                    last[game.player]["action"],
                    new_state,
                    0
                )

    print("Done training")
    print(sorted(player.q.items()))

    # Return the trained AI
    return player


def play(ai, human_player=None):
    """
    Play human game against the AI.
    'human_player' can be set to 0 or 1 to specify whether
    human player moves first or second.
    """

    # If no player order set, choose human's order randomly
    if human_player is None:
        human_player = random.randint(0, 1)

    # Create new game
    game = Nim()

    # Game loop
    while True:

        # Print contents of piles
        print()
        print("Piles:")
        for i, pile in enumerate(game.piles):
            print(f"Pile {i}: {pile}")
        print()

        # Compute available actions
        available_actions = Nim.available_actions(game.piles)
        time.sleep(1)

        # Let human make a move
        if game.player == human_player:
            print("Your Turn")
            while True:
                pile = int(input("Choose Pile: "))
                count = int(input("Choose Count: "))
                if (pile, count) in available_actions:
                    break
                print("Invalid move, try again.")

        # Have AI make a move
        else:
            print("AI's Turn")
            pile, count = ai.choose_action(game.piles, epsilon=False)
            print(f"AI chose to take {count} from pile {pile}.")

        # Make move
        game.move((pile, count))

        # Check for winner
        if game.winner is not None:
            print()
            print("GAME OVER")
            winner = "Human" if game.winner == human_player else "AI"
            print(f"Winner is {winner}")
            return