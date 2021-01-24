from copy import deepcopy, copy
import os
import sys
from tkinter import *
from tkinter import messagebox
import chess
import pygame
import pprint
import chess.engine
import random

all_sprites = [[None for i in range(8)] for j in range(8)]
already = (0, 0)




def Check():
    global check
    x1, y1 = search_king()
    board_color[y1][x1] = (235, 52, 52)

def update_sprite(i, j, pos):
    all_sprites[i][j].rect = pos


def load_image(name):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def correct_coords(row, col):  # Проверка поля на корректность
    return 0 <= row < 8 and 0 <= col < 8


def opponent(color):  # Смена игрока
    if color == WHITE:
        return BLACK
    return WHITE


def transformation(row, col):  # трансформация на последней клетке
    figyre = input('Выбирете фигуру ')
    if figyre.lower() == 'q':
        board.field[row][col] = Queen(row, col, board.color)
    elif figyre.lower() == 'r':
        board.field[row][col] = Rook(row, col, board.color)
    elif figyre.lower() == 'k':
        board.field[row][col] = Knight(row, col, board.color)
    elif figyre.lower() == 'b':
        board.field[row][col] = Bishop(row, col, board.color)


def castling(row, col, row1, col1):  # vожможна ли Рокировка
    king = search_king()
    if king == (row, col) and not board.field[king[0]][king[1]].move and row == row1:
        if col1 == 6 and isinstance(board.field[row][7], Rook) and not board.field[row][7].move:
            for i in range(3):
                if board.is_under_attack(king[0], king[1] + i, opponent(board.color)):
                    return False
        elif col1 == 2 and isinstance(board.field[row][0], Rook) and not board.field[row][0].move:
            for i in range(3):
                if board.is_under_attack(king[0], king[1] - i, opponent(board.color)) or \
                        board.field[king[0]][king[1] - i] and i != 0:
                    return False
        else:
            return False
    else:
        return False
    return True


def search_king():
    for i in range(8):
        for j in range(8):
            if isinstance(board.field[i][j], King):
                if board.field[i][j].color == board.color:
                    return i, j


def king_is_under_attak(row, col, row1, col1):  # Стоит ли шах короллю
    test_board.field = deepcopy(board.field)
    board.field[row1][col1] = deepcopy(board.field[row][col])
    board.field[row][col] = None
    board.field[row1][col1].set_position(row1, col1)
    if board.is_under_attack(*search_king(), opponent(board.color)):
        board.field[row1][col1].set_position(row, col)
        board.field = deepcopy(test_board.field)
        return True
    return False


WHITE = 0
BLACK = 1


class Board:  # Класс доски
    def __init__(self):
        self.color = WHITE
        self.field = []
        for row in range(8):
            self.field.append([None] * 8)

        #  Расставляем фигуры
        self.field[7][0] = Rook(7, 0, WHITE)
        self.field[7][1] = Knight(7, 1, WHITE)
        self.field[7][2] = Bishop(7, 2, WHITE)
        self.field[7][3] = Queen(7, 3, WHITE)
        self.field[7][4] = King(7, 4, WHITE)
        self.field[7][5] = Bishop(7, 5, WHITE)
        self.field[7][6] = Knight(7, 6, WHITE)
        self.field[7][7] = Rook(7, 7, WHITE)

        self.field[0][0] = Rook(0, 0, BLACK)
        self.field[0][1] = Knight(0, 1, BLACK)
        self.field[0][2] = Bishop(0, 2, BLACK)
        self.field[0][3] = Queen(0, 3, BLACK)
        self.field[0][4] = King(0, 4, BLACK)
        self.field[0][5] = Bishop(0, 5, BLACK)
        self.field[0][6] = Knight(0, 6, BLACK)
        self.field[0][7] = Rook(0, 7, BLACK)

        self.field[6][0] = Pawn(6, 0, WHITE)
        self.field[6][1] = Pawn(6, 1, WHITE)
        self.field[6][2] = Pawn(6, 2, WHITE)
        self.field[6][3] = Pawn(6, 3, WHITE)
        self.field[6][4] = Pawn(6, 4, WHITE)
        self.field[6][5] = Pawn(6, 5, WHITE)
        self.field[6][6] = Pawn(6, 6, WHITE)
        self.field[6][7] = Pawn(6, 7, WHITE)

        self.field[1][0] = Pawn(1, 0, BLACK)
        self.field[1][1] = Pawn(1, 1, BLACK)
        self.field[1][2] = Pawn(1, 2, BLACK)
        self.field[1][3] = Pawn(1, 3, BLACK)
        self.field[1][4] = Pawn(1, 4, BLACK)
        self.field[1][5] = Pawn(1, 5, BLACK)
        self.field[1][6] = Pawn(1, 6, BLACK)
        self.field[1][7] = Pawn(1, 7, BLACK)
        self.width = 8
        self.height = 8
        self.left = 0
        self.top = 0
        self.cell_size = 100

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def start(self, surface):
        for i in range(self.height):
            for j in range(self.width):
                if self.field[i][j] and self.field[i][j].get_color() == BLACK:
                    image = load_image(self.field[i][j].__class__.__name__ + '.png')
                elif self.field[i][j]:
                    image = load_image('W' + self.field[i][j].__class__.__name__ + '.png')
                pygame.draw.rect(surface, (255, 255, 255),
                                 (self.left + i * self.cell_size, self.top + j * self.cell_size,
                                  self.cell_size, self.cell_size), 3)
                if self.field[i][j]:
                    temp_x = self.left + j * self.cell_size
                    temp_y = self.top + i * self.cell_size
                    sprite = pygame.sprite.Sprite()
                    sprite.image = image
                    sprite.rect = sprite.image.get_rect()
                    sprite.rect.x = temp_x
                    sprite.rect.y = temp_y
                    all_sprites[i][j] = sprite

    def render(self, surface):
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(surface,  board_color[i][j],
                                (self.left + i * self.cell_size, self.top + j * self.cell_size,
                                 self.cell_size, self.cell_size))

    def get_cell(self, mouse_pos):
        xx, yy = mouse_pos
        return (xx - self.left) // self.cell_size, \
               ((self.cell_size * 8 - (yy - self.top)) // self.cell_size)

    def current_player_color(self):  # возвращает цвет активного игрока
        return self.color

    def line(self):  # ну тип черные на 7 линии, белые на 0
        if self.color == BLACK:
            return 0
        return 7

    def cell(self, row, col):  # Это когда доску рисуем, функция возвращает или "  " если нет фигуры,
        # или название фигуры и цвет
        t_piece = self.field[row][col]
        if t_piece is None:
            return '  '
        color = t_piece.get_color()
        c = 'w' if color == WHITE else 'b'
        return c + t_piece.self.nickname

    def move_piece(self, row, col, row1, col1):  # Куча проверок если мы хотим сдвинуть фигуру,
        # правда, если мы можем переместить туда кого нибудь, иначе хер
        global all_sprites, board_color
        if not correct_coords(row, col) or not correct_coords(row1, col1):
            return False
        if row == row1 and col == col1:
            return False
        temp_piece = self.field[row][col]
        if temp_piece is None:
            return False
        if temp_piece.get_color() != self.color:
            return False
        if not temp_piece.can_move(row1, col1) and not castling(row, col, row1, col1):
            return False
        if castling(row, col, row1, col1):
            if col1 == 6:
                self.field[row][5] = copy(self.field[row][7])
                self.field[row][7] = None
                self.field[row][5].set_position(row, 5)
                update_sprite(row, 7, (5 * 100, row * 100))
                all_sprites[row][5], all_sprites[row][7] = all_sprites[row][7], None
            elif col1 == 2:
                self.field[row][3] = copy(self.field[row][0])
                self.field[row][0] = None
                self.field[row][3].set_position(row, 3)
                update_sprite(row, 0, (3 * 100, row * 100))
                all_sprites[row][3], all_sprites[row][0] = all_sprites[row][0], None
        elif king_is_under_attak(row, col, row1, col1):
            return False

        self.field[row][col] = None
        self.field[row1][col1] = temp_piece
        temp_piece.set_position(row1, col1)
        if isinstance(temp_piece, Pawn):
            if temp_piece.end_field == row1:
                transformation(row1, col1)
        if isinstance(temp_piece, (King, Rook)):
            temp_piece.move = True
        self.color = opponent(self.color)
        move = s[col] + str(8-row) + s[col1] + str(8-row1)
        chessboard.push_uci(move)
        update_sprite(row, col, (col1 * 100, row1 * 100))
        all_sprites[row][col], all_sprites[row1][col1] = \
            None, all_sprites[row][col]
        board_color = [[(196, 14, 0) if (i + j) % 2 == 1 else (255, 255, 255) for i in range(8)] for j in range(8)]
        if (chessboard.is_check()):
            Check()
        return True

    def is_under_attack(self, row, col, color):  # является ли поле под боем относительно
        # переданного цвета
        for i in range(8):
            for j in range(8):
                if self.field[i][j]:
                    q = self.field[i][j]
                    if q.get_color() == color and q.can_move(row, col):
                        return True
        return False


def helper():
    global helping
    result = str(engine.play(chessboard, chess.engine.Limit(time=0.5)).move)
    result = f[result[0]], int(result[1]) - 1, f[result[2]], int(result[3]) - 1
    x1, y1, x2, y2 = result[0], result[1], result[2], result[3]
    board_color[x1][7-y1] = (110, 52, 235)
    board_color[x2][7-y2] = (110, 52, 235)
    helping = 1


class Pawn:  # просто пешка
    def __repr__(self):
        return 'Пешка'

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.nickname = 'P'
        self.end_field = 7 if color == BLACK else 0

    def set_position(self, row, col):
        self.row = row
        self.col = col

    def get_color(self):
        return self.color

    def barrier(self, row, col):  # не стоит ли кто нить перед пешкой
        roww = 1 if row > self.row else -1
        for i in range(0, abs(self.row - row)):
            if board.field[row - i * roww][col]:
                return False
        return True

    def can_move(self, row, col):  # можно ли двинуть пешку туда
        if self.color == BLACK:
            direction = 1
            start_row = 1
        else:
            direction = -1
            start_row = 6
        if self.row + direction == row and abs(self.col - col) == 1 and board.field[row][col]:
            if board.field[row][col].color != self.color:
                return True
        if self.row + direction == row and self.col == col and not board.field[row][col]:
            return True
        if self.row == start_row and self.row + 2 * direction == row and \
                self.barrier(row, col) and self.col == col:
            return True
        return False


class Knight:  # все те же самые функции только про коня
    def __repr__(self):
        return 'Конь'

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.nickname = 'N'

    def set_position(self, row, col):
        self.row = row
        self.col = col

    def get_color(self):
        return self.color

    def can_move(self, row, col):
        if (abs(self.row - row) == 1 and abs(self.col - col) == 2 or abs(self.row - row) == 2 and
            abs(self.col - col) == 1) and 0 <= row < 8 and 0 <= col < 8 \
                and (not board.field[row][col] or self.can_kill(row, col)):
            return True
        return False

    def can_kill(self, row, col):
        if board.field[row][col].color != self.color:
            return True
        return False


class Bishop:  # слон
    def __repr__(self):
        return 'Слон'

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.nickname = 'B'

    def set_position(self, row, col):
        self.row = row
        self.col = col

    def get_color(self):
        return self.color

    def can_move(self, row, col):
        if abs(self.col - col) == abs(self.row - row) and 0 <= row < 8 and 0 <= col < 8:
            if self.barrier(row, col) and self.can_kill(row, col):
                return True
        return False

    def barrier(self, row, col):
        r = 1 if row > self.row else -1
        c = 1 if col > self.col else -1
        for i in range(1, abs(self.col - col)):
            if board.field[row - i * r][col - i * c]:
                return False
            if not self.can_kill(row, col):
                return False
        return True

    def can_kill(self, row, col):
        if board.field[row][col]:
            if board.field[row][col].color == self.color:
                return False
        return True


class Queen:  # ферзь
    def __repr__(self):
        return 'Ферзь'

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.nickname = 'Q'

    def set_position(self, row, col):
        self.row = row
        self.col = col

    def get_color(self):
        return self.color

    def can_move(self, row, col):
        if (abs(self.col - col) == abs(self.row - row) or self.row == row or self.col == col) \
                and 0 <= row < 8 and 0 <= col < 8:
            if self.barrier(row, col):
                return True
        return False

    def barrier(self, row, col):
        if not self.can_kill(row, col):
            return False
        if self.col == col:
            roww = 1 if row > self.row else -1
            for i in range(1, abs(self.row - row)):
                if board.field[row - i * roww][col]:
                    return False
            return True
        elif self.row == row:
            coll = 1 if col > self.col else -1
            for i in range(1, abs(self.col - col)):
                if board.field[row][col - coll * i]:
                    return False
            return True
        else:
            r = 1 if row > self.row else -1
            c = 1 if col > self.col else -1
            for i in range(1, abs(self.col - col)):
                if board.field[row - i * r][col - i * c]:
                    return False
            return True

    def can_kill(self, row, col):
        if board.field[row][col]:
            if board.field[row][col].color == self.color:
                return False
        return True


class King:  # король
    def __repr__(self):
        return 'Король'

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.move = False
        self.nickname = 'X'

    def set_position(self, row, col):
        self.row = row
        self.col = col

    def get_color(self):
        return self.color

    def can_move(self, row, col):
        if ((self.row - row) ** 2 + (self.col - col) ** 2) ** 0.5 < 1.5 and \
                not board.is_under_attack(row, col, opponent(self.color)) and self.can_kill(row,
                                                                                            col):
            return True
        return False

    def can_kill(self, row, col):
        if board.field[row][col]:
            if board.field[row][col].color == self.color:
                return False
        return True


class Rook:  # ладья
    def __repr__(self):
        return 'Ладья'

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.move = False
        self.nickname = 'R'

    def set_position(self, row, col):
        self.row = row
        self.col = col

    def get_color(self):
        return self.color

    def can_move(self, row, col):
        if self.row == row or self.col == col:
            if self.barrier(row, col):
                return True
        return False

    def barrier(self, row, col):
        if not self.can_kill(row, col):
            return False
        if self.col == col:
            roww = 1 if row > self.row else -1
            for i in range(1, abs(self.row - row)):
                if board.field[row - i * roww][col]:
                    return False
            return True
        elif self.row == row:
            coll = 1 if col > self.col else -1
            for i in range(1, abs(self.col - col)):
                if board.field[row][col - coll * i]:
                    return False
            return True

    def can_kill(self, row, col):
        if board.field[row][col]:
            if board.field[row][col].color == self.color:
                return False
        return True


def print_board(board_temp):  # рисуем доску
    print('     +----+----+----+----+----+----+----+----+')
    for row in range(7, -1, -1):
        print(' ', row, end='  ')
        for col in range(8):
            print('|', board_temp.cell(row, col), end=' ')
        print('|')
        print('     +----+----+----+----+----+----+----+----+')
    print(end='        ')
    for col in range(8):
        print(col, end='    ')
    print()


def end():
    global board, screen, chessboard, all_sprites, board_color
    messagebox.showinfo('Мат', 'Мат')
    board = Board()
    board_color = [[(196, 14, 0) if (i + j) % 2 == 1 else (255, 255, 255) for i in range(8)] for j in range(8)]
    all_sprites = [[None for _ in range(8)] for _ in range(8)]
    chessboard = chess.Board()
    board.start(screen)


def update_screen():
    for i in range(8):
        for j in range(8):
            if all_sprites[i][j]:
                screen.blit(all_sprites[i][j].image, all_sprites[i][j].rect)


if __name__ == '__main__':
    board = Board()
    Tk().wm_withdraw()
    test_board = Board()
    test_board.field = deepcopy(board.field)
    pygame.init()
    pygame.display.set_caption('Board')
    size = width, height = 800, 1000
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    screen.fill((255, 255, 255))
    chessboard = chess.Board()
    s = 'abcdefgh'
    f = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    prompt = load_image('prompt.png')
    engine = chess.engine.SimpleEngine.popen_uci('data/stockfish')
    board.start(screen)
    move_sound = sound1 = pygame.mixer.Sound('data/move.wav')
    helping = 0
    board_color = [[(196, 14, 0) if (i+j)%2 == 1 else (255, 255, 255) for i in range(8) ] for j in range(8)]
    check = 0
    clicked = False
    running = True
    piece = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                cell = board.get_cell(event.pos)
                j, i = cell[0], 7 - cell[1]
                x, y = event.pos
                if 300 <= x <= 400 and 840 <= y <= 940:
                    helper()
                    helping = 1
                    continue
                helping = 0
                if not (0 <= i < 8 and 0 <= j < 8):
                    continue
                if board.field[i][j] and board.field[i][j].color == board.current_player_color():
                    clicked = True
                    already = board.get_cell(event.pos)
                    already = already[0], 7 - already[1]
                    piece = board.field[i][j]
            if event.type == pygame.MOUSEBUTTONUP:
                if not clicked:
                    continue
                i, j = board.get_cell(event.pos)
                j = 7 - j
                if not board.move_piece(already[1], already[0], j, i):
                    update_sprite(already[1], already[0], (already[0] * 100, already[1] * 100))
                else:
                    move_sound.play()
                    # board_color = [[(196, 14, 0) if (i + j) % 2 == 1 else (255, 255, 255) for i in range(8)] for j in range(8)]
                    if chessboard.is_checkmate():
                        end()
                clicked = False
            if event.type == pygame.MOUSEMOTION:
                if clicked:
                    update_sprite(already[1], already[0], (event.pos[0] - 50, event.pos[1] - 50))

        screen.fill((255, 255, 255))
        screen.blit(prompt, (300, 840))
        board.render(screen)
        update_screen()
        pygame.display.flip()
    pygame.quit()
