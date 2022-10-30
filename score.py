import numpy as np

SIZE = 15
LETTERS = {
    'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1, 'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1,
    'O': 1, 'P': 3, 'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10, '_': 0
}
DOUBLE_LETTERS = [(1, 4), (3, 7), (4, 1), (4, 8), (7, 3), (7, 7), (8, 4)]
TRIPLE_LETTERS = [(2, 6), (6, 2), (6, 6)]


class Letter:
    def __init__(self, row, column, letter):
        self.row = row
        self.column = column
        self.letter = letter

    def __str__(self):
        return str(self.row) + chr(ord('A') + self.column - 1) + ' ' + self.letter

    def get_letter_score(self):
        row1 = self.row
        row2 = SIZE - self.row + 1
        column1 = self.column
        column2 = SIZE - self.column + 1

        if (row1, column1) in DOUBLE_LETTERS \
                or (row1, column2) in DOUBLE_LETTERS\
                or (row2, column1) in DOUBLE_LETTERS\
                or (row2, column2) in DOUBLE_LETTERS:
            return 2
        if (row1, column1) in TRIPLE_LETTERS \
                or (row1, column2) in TRIPLE_LETTERS\
                or (row2, column1) in TRIPLE_LETTERS\
                or (row2, column2) in TRIPLE_LETTERS:
            return 3

        return 1

    def get_word_bonus(self):
        if self.row == self.column == 8:
            return 2
        if self.row in [1, 8, 15] and self.column in [1, 8, 15]:
            return 3
        if (self.row == self.column or self.row == SIZE - self.column + 1) and (self.row < 6 or self.row > 10):
            return 2
        return 1


class Turn:
    def __init__(self, tiles, board, bonus):
        self.tiles = tiles
        self.board = board
        self.bonus = bonus
        self.direction = np.array([0, 1]) if (len(tiles) == 1 or tiles[0][0] == tiles[1][0]) else np.array([1, 0])
        self.score = 50 if len(self.tiles) == 7 else 0
        self.get_score()

    def __str__(self):
        turn = ''
        for tile in self.tiles:
            turn += str(tile) + '\n'
        turn += str(self.score)
        return turn

    def get_before_score(self, row, column, direction):
        score = 0
        row -= direction[0]
        column -= direction[1]

        while row > 0 and column > 0 and self.board[row][column] != '.':
            score += LETTERS[self.board[row][column]]
            row -= direction[0]
            column -= direction[1]
        return score

    def get_after_score(self, row, column, direction):
        score = 0
        row += direction[0]
        column += direction[1]

        while row < SIZE + 1 and column < SIZE + 1 and self.board[row][column] != '.':
            score += LETTERS[self.board[row][column]]
            row += direction[0]
            column += direction[1]
        return score

    def get_side_score(self, row, column, letter_score, word_bonus):
        word_score = letter_score
        word_score += self.get_before_score(row, column, 1 - self.direction)
        word_score += self.get_after_score(row, column, 1 - self.direction)

        if word_score != letter_score:
            self.score += word_score * word_bonus

    def get_between_score(self, row_start, column_start, row_end, column_end):
        score = 0
        while (row_end - row_start > 0 or column_end - column_start > 0) and self.board[row_start][column_start] != '.':
            score += LETTERS[self.board[row_start][column_start]]
            row_start += self.direction[0]
            column_start += self.direction[1]
        return score

    def get_between_scores(self):
        score = 0
        for i in range(1, len(self.tiles)):
            score += self.get_between_score(self.tiles[i - 1].row + self.direction[0],
                                            self.tiles[i - 1].column + self.direction[1],
                                            self.tiles[i].row,
                                            self.tiles[i].column)
        return score

    def get_score(self):
        word_score = 0
        word_score += self.get_before_score(self.tiles[0][0], self.tiles[0][1], self.direction)
        word_score += self.get_after_score(self.tiles[-1][0], self.tiles[-1][1], self.direction)

        word_bonus = 1

        for i in range(len(self.tiles)):
            (row, column, letter) = self.tiles[i]
            letter_node = Letter(row, column, letter)
            self.tiles[i] = letter_node

            letter_score = LETTERS[letter]
            local_word_bonus = 1

            if self.bonus[row][column] == 0:
                local_word_bonus = letter_node.get_word_bonus()
                letter_score *= letter_node.get_letter_score()
                self.bonus[row][column] = -1

            self.get_side_score(row, column, letter_score, local_word_bonus)
            word_bonus *= local_word_bonus
            word_score += letter_score

        word_score += self.get_between_scores()
        word_score *= word_bonus
        self.score += word_score


class Board:
    def __init__(self):
        self.bonus = np.zeros((SIZE + 2, SIZE + 2))
        self.board = [['.' for _ in range(SIZE + 2)] for _ in range(SIZE + 2)]

    def __str__(self):
        board = ''
        for i in range(1, SIZE + 1):
            board += ''.join(self.board[i][1:SIZE + 1]) + '\n'
        return board

    def add_tiles(self, tiles):
        for tile in tiles:
            self.board[tile.row][tile.column] = tile.letter

    def add_turn(self, tiles, file_name):
        turn = Turn(tiles, self.board, self.bonus)
        self.add_tiles(turn.tiles)

        print(turn)
        f = open('results/' + file_name, 'w')
        f.write(str(turn))
        f.close()
