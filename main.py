import patternMatching
import score
import cv2


def get_turn(board, image_board):
    tiles = []

    for row in range(1, score.SIZE + 1):
        for column in range(1, score.SIZE + 1):
            if board.board[row][column] != '.':
                continue

            tile_image = image_board.get_tile_image(row, column)
            # cv2.imwrite('tiles/' + str(row) + '_' + str(column) + '.jpg', tile_image)
            tile_value = patternMatching.get_best_correlation(tile_image)

            if len(tile_value[0]) == 1 and tile_value[0] != '.':
                tiles.append((row, column, tile_value[0]))

    return tiles


def main(path):
    for i in range(1, 6):
        board = score.Board()
        for j in range(1, 21):
            file_name = str(i) + '_' + ('0' if j < 10 else '') + str(j)
            print(file_name)
            image = patternMatching.Board(file_name + '.jpg', path)
            tiles = get_turn(board, image)
            board.add_turn(tiles, file_name + '.txt')


main('train')
