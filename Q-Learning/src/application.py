import random
import sys
from enum import Enum

from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QSlider, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QPushButton, QSpacerItem
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, QTimer
import numpy as np


class Square:
    def __init__(self, size, x, y, color):
        self.size = size
        self.x = x
        self.y = y
        self.color = color

    def paint(self, painter):
        painter.setBrush(self.color)
        painter.drawRect(self.x, self.y, self.size, self.size)


class Player:

    def __init__(self, x, y, color):

        self.player_box = Square(Board.TILE_SIZE, x * Board.TILE_SIZE, y * Board.TILE_SIZE, color)

    @property
    def x(self):
        return int(self.player_box.x / Board.TILE_SIZE)

    @x.setter
    def x(self, x):
        self.player_box.x = x * Board.TILE_SIZE

    @property
    def y(self):
        return int(self.player_box.y / Board.TILE_SIZE)

    @y.setter
    def y(self, y):
        self.player_box.y = y * Board.TILE_SIZE

    @property
    def size(self):
        return self.player_box.size

    def move_up(self, board):
        if self.is_valid_move(board[self.y - 1][self.x]):
            self.y = self.y - 1
            return -1
        else:
            return -5

    def move_down(self, board):
        if self.is_valid_move(board[self.y + 1][self.x]):
            self.y = self.y + 1
            return -1
        else:
            return -5

    def move_right(self, board):
        if self.is_valid_move(board[self.y][self.x + 1]):
            self.x = self.x + 1
            return -1
        else:
            return -5

    def move_left(self, board):
        if self.is_valid_move(board[self.y][self.x - 1]):
            self.x = self.x - 1
            return -1
        else:
            return -5

    def paint(self, painter):
        self.player_box.paint(painter)

    def is_valid_move(self, move):
        return move.tile_type != TileType.WALL

    def has_won(self, board):
        return board[self.y][self.x].tile_type == TileType.GOAL


class TileType(Enum):
    WALL = 0
    PATH = 1
    GOAL = 2
    PLAYER = 3


class Tile:
    WALL_COLOR = QColor(0, 0, 0)
    PATH_COLOR = QColor(255, 255, 255)
    GOAL_COLOR = QColor(244, 200, 66)
    PLAYER_COLOR = QColor(65, 155, 244)

    def __init__(self, size, x, y, tile_type):
        self.tile_type = tile_type
        color = self.get_color(tile_type)
        self.tile = Square(size, x, y, color)

    def get_color(self, tile_type):
        if tile_type == TileType.WALL:
            return Tile.WALL_COLOR
        elif tile_type == TileType.PATH:
            return Tile.PATH_COLOR
        elif tile_type == TileType.GOAL:
            return Tile.GOAL_COLOR
        else:
            raise Exception(f'Invalid tile type: {tile_type}')

    def paint(self, painter):
        self.tile.paint(painter)


class Board:
    TILE_SIZE = 50

    def __init__(self, file):

        self.rows = None
        self.cols = None
        self.player_start_x = None
        self.player_start_y = None
        self.tiles = self.init_board(file)

    def init_board(self, file):

        with open(file, 'r') as f:
            lines = f.readlines()

        board = list()

        self.rows = len(lines)
        self.cols = len(lines[0])

        for line_index, line in enumerate(lines):

            board_row = list()

            line = line.strip()

            for col_index, col in enumerate(line):

                x = Board.TILE_SIZE * col_index
                y = Board.TILE_SIZE * line_index

                col = TileType(int(col))

                if col == TileType.WALL:
                    tile = Tile(Board.TILE_SIZE, x, y, TileType.WALL)
                elif col == TileType.PATH:
                    tile = Tile(Board.TILE_SIZE, x, y, TileType.PATH)
                elif col == TileType.GOAL:
                    tile = Tile(Board.TILE_SIZE, x, y, TileType.GOAL)
                elif col == TileType.PLAYER:
                    tile = Tile(Board.TILE_SIZE, x, y, TileType.PATH)
                    self.player_start_x = col_index
                    self.player_start_y = line_index
                else:
                    raise Exception(f'Invalid character in maze definition: {col}')

                board_row.append(tile)

            board.append(board_row)

        return board

    def paint(self, painter):

        for row in self.tiles:
            for tile in row:
                tile.paint(painter)


class Maze(QFrame):
    PLAYER_COLOR = QColor(65, 155, 244)
    BOARD_FILE = "../resources/maze.txt"

    def __init__(self, turn_delay):
        super().__init__()

        self.turn_delay = turn_delay

        self.setFocusPolicy(Qt.StrongFocus)
        self.board = Board(Maze.BOARD_FILE)
        self.player = Player(self.board.player_start_x, self.board.player_start_y, Maze.PLAYER_COLOR)

        self.setMinimumHeight(self.board.cols * Board.TILE_SIZE)
        self.setMinimumWidth(self.board.rows * Board.TILE_SIZE)

        self.timer = QTimer()
        self.timer.setInterval(self.turn_delay)
        self.timer.timeout.connect(self.make_move)

        self.epsilon = 0.8

        observation_space = self.board.rows * self.board.cols
        action_space = 4
        self.q_table = np.zeros([observation_space, action_space])

    def random_move(self):

        moves = [0, 1, 2, 3]
        move = random.choice(moves)

        return move

    def make_move(self):

        alpha = 0.1
        gamma = 0.6

        state = self.player.y * 10 + self.player.x

        if random.uniform(0, 1) < self.epsilon:
            move = self.random_move()
        else:
            move = np.argmax(self.q_table[state])

        if move == 0:
            reward = self.player.move_up(self.board.tiles)
        elif move == 1:
            reward = self.player.move_down(self.board.tiles)
        elif move == 2:
            reward = self.player.move_left(self.board.tiles)
        elif move == 3:
            reward = self.player.move_right(self.board.tiles)
        else:
            raise Exception(f'Invalid move: {move}')

        if self.player.has_won(self.board.tiles):
            self.player.x = self.board.player_start_x
            self.player.y = self.board.player_start_y
            reward = 50

        old_value = self.q_table[state, move]
        new_state = self.player.y * 10 + self.player.x
        new_max_value = np.max(self.q_table[new_state])

        new_value = (1 - alpha) * old_value + alpha * (reward + gamma * new_max_value)
        self.q_table[state, move] = new_value

        self.update()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)

        self.board.paint(painter)
        self.player.paint(painter)

        painter.end()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.player.move_up(self.board.tiles)
        if event.key() == Qt.Key_Down:
            self.player.move_down(self.board.tiles)
        if event.key() == Qt.Key_Left:
            self.player.move_left(self.board.tiles)
        if event.key() == Qt.Key_Right:
            self.player.move_right(self.board.tiles)

        self.update()

    def change_turn_delay(self, value):
        self.timer.setInterval(value)

    def change_epsilon(self, value):
        self.epsilon = value

    def toggle_timer(self):
        if self.timer.isActive():
            self.timer.stop()
            return False
        else:
            self.timer.start()
            return True


class CentralWidget(QWidget):
    MAX_TURN_DELAY = 200
    MIN_TURN_DELAY = 1
    EPSILON_MAX = 100
    EPSILON_DEFAULT = 80
    EPSILON_MIN = 0

    def __init__(self):
        super().__init__()

        self.maze = Maze(CentralWidget.MAX_TURN_DELAY)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.maze)

        horizontal_layout = QHBoxLayout()

        delay_label = QLabel()
        delay_label.setText('Turn Delay')
        horizontal_layout.addWidget(delay_label)

        self.delay_slider = QSlider()
        self.delay_slider.setOrientation(Qt.Horizontal)
        self.delay_slider.setMaximum(CentralWidget.MAX_TURN_DELAY)
        self.delay_slider.setMinimum(CentralWidget.MIN_TURN_DELAY)
        self.delay_slider.setValue(CentralWidget.MAX_TURN_DELAY)
        self.delay_slider.valueChanged.connect(self.change_speed)
        horizontal_layout.addWidget(self.delay_slider)

        epsilon_label = QLabel()
        epsilon_label.setText('Epsilon')
        horizontal_layout.addWidget(epsilon_label)

        epsilon_slider = QSlider()
        epsilon_slider.setOrientation(Qt.Horizontal)
        epsilon_slider.setMaximum(CentralWidget.EPSILON_MAX)
        epsilon_slider.setMinimum(CentralWidget.EPSILON_MIN)
        epsilon_slider.setValue(CentralWidget.EPSILON_DEFAULT)
        epsilon_slider.valueChanged.connect(self.change_epsilon)
        horizontal_layout.addWidget(epsilon_slider)

        self.start_button = QPushButton()
        self.start_button.setText('Start')
        self.start_button.clicked.connect(self.toggle_run)
        horizontal_layout.addWidget(self.start_button)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        horizontal_layout.addItem(spacer)

        vertical_layout.addLayout(horizontal_layout)

        self.setLayout(vertical_layout)

    def change_speed(self, value):
        self.maze.change_turn_delay(value)

    def change_epsilon(self, value):
        self.maze.change_epsilon(value / 100)

    def toggle_run(self):
        state = self.maze.toggle_timer()

        if state:
            self.start_button.setText('Pause')
        else:
            self.start_button.setText('Start')


class MainWindow(QMainWindow):
    TITLE = "Q-learning"

    def __init__(self):
        super().__init__()
        self.setWindowTitle(MainWindow.TITLE)
        self.central_widget = CentralWidget()
        self.setCentralWidget(self.central_widget)

        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
