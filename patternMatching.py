import numpy as np
import cv2

# images = [('board+letters/21.jpg', (490, 900), (2600, 3200)),
#           ('train/1_01.jpg', (1000, 430), (3050, 2650))]

alphabet = ('board+letters/14.jpg', (600, 1230), (2670, 3490))

LETTER_TILES = {
    'A': (5, 5), 'B': (5, 6), 'C': (5, 7), 'D': (5, 8), 'E': (5, 9),
    'F': (6, 5), 'G': (6, 6), 'H': (6, 7), 'I': (6, 8), 'J': (6, 9),
    'K': (7, 5), 'L': (7, 6), 'M': (7, 7), 'N': (7, 8), 'O': (7, 9),
    'P': (8, 5), 'Q': (8, 6), 'R': (8, 7), 'S': (8, 8), 'T': (8, 9),
    'U': (9, 5), 'V': (9, 6), 'W': (9, 7), 'X': (9, 8), 'Y': (9, 9),
    'Z': (10, 5), '_': (10, 6)
}

TEMPLATES = ['.', 'DL', 'DW', 'TL', 'TW'] + list(LETTER_TILES.keys())


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ')'


class Line:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return '[' + str(self.start) + ', ' + str(self.end) + ']'


class Rectangle:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def draw_rectangle(self, image, name):
        cv2.rectangle(image, (self.start.x, self.start.y), (self.end.x, self.end.y), (0, 255, 0), 5)
        cv2.imwrite('rectangle_' + name + '.jpg', image)


class Board:
    def __init__(self, image_name):
        self.image_name = image_name
        self.image = cv2.imread('train/' + image_name)
        self.edges = self.process_image()
        self.horizontal_lines, self.vertical_lines = self.get_lines()

        self.draw_lines()
        self.get_board()

        self.start = Point(1000, 430)
        self.end = Point(3050, 2650)

        self.board = Rectangle(self.start, self.end)
        self.tile_size = ((self.board.end.x - self.board.start.x) / 15, (self.board.end.y - self.board.start.y) / 15)

    def process_image(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        blur_gray = cv2.GaussianBlur(gray, (7, 7), 0)
        edges = cv2.Canny(blur_gray, 100, 200)

        cv2.imwrite('edges/' + self.image_name, edges)

        return edges

    def get_lines(self):
        lines = cv2.HoughLinesP(image=self.edges, rho=1, theta=np.pi / 180, threshold=300, lines=np.array([]),
                                minLineLength=1000, maxLineGap=800)

        horizontal, vertical = separate_lines(lines)

        return horizontal, vertical

    def get_board(self):
        threshold = 100
        if int(self.image_name[0]) < 3:
            threshold = 900

        # TODO: rotit + centrat imagine inainte de asta ca sa pot aplica threshold pe tot

        h_middle = self.edges.shape[1] / 2
        top = filter(lambda x: top_filter(x, h_middle - threshold), self.horizontal_lines)
        bottom = filter(lambda x: bottom_filter(x, h_middle + threshold), self.horizontal_lines)

        v_middle = self.edges.shape[0] / 2
        left = filter(lambda x: left_filter(x, v_middle - threshold), self.vertical_lines)
        right = filter(lambda x: right_filter(x, v_middle + threshold), self.vertical_lines)

        top_line = list(top)[-1]
        bottom_line = list(bottom)[0]
        left_line = list(left)[-1]
        right_line = list(right)[0]

        print(self.image_name)
        print(top_line, bottom_line, left_line, right_line)
        # (1000, 430), (3050, 2650)
        print(line_intersection(top_line, left_line))
        print(line_intersection(top_line, right_line))
        print(line_intersection(bottom_line, left_line))
        print(line_intersection(bottom_line, right_line))
        print()

        outline = np.copy(self.edges) * 0
        for line in [top_line, bottom_line, left_line, right_line]:
            cv2.line(outline, (line.start.x, line.start.y), (line.end.x, line.end.y), (255, 0, 0), 5)

        outline = cv2.addWeighted(self.edges, 0.8, outline, 1, 0)
        cv2.imwrite('outlines/' + self.image_name, outline)

    def draw_lines(self):
        line_image = np.copy(self.edges) * 0
        for line in (self.horizontal_lines + self.vertical_lines):
            cv2.line(line_image,
                     (line.start.x, line.start.y),
                     (line.end.x, line.end.y),
                     (255, 0, 0), 5)

        cv2.imwrite('image_lines/' + self.image_name, line_image)

        lines_edges = cv2.addWeighted(self.edges, 0.8, line_image, 1, 0)
        cv2.imwrite('image_with_lines/' + self.image_name, lines_edges)

    def get_tile_rectangle(self, row, column):
        start = Point(int(self.board.start.x + (column - 1) * self.tile_size[0]),
                      int(self.board.start.y + (row - 1) * self.tile_size[1]))
        end = Point(int(self.board.start.x + column * self.tile_size[0] + 10),
                    int(self.board.start.y + row * self.tile_size[1] + 10))

        return Rectangle(start, end)

    def draw_rectangle(self, row, column):
        tile = self.get_tile_rectangle(row, column)
        tile.draw_rectangle(self.image, self.image_name)

    def get_tile_image(self, row, column):
        tile = self.get_tile_rectangle(row, column)
        tile_image = self.image[tile.start.y:tile.end.y, tile.start.x:tile.end.x]

        return tile_image


def top_filter(line, middle):
    return line.start.x < middle and line.end.x < middle


def bottom_filter(line, middle):
    return line.start.x > middle and line.end.x > middle


def left_filter(line, middle):
    return line.start.y < middle and line.end.y < middle


def right_filter(line, middle):
    return line.start.y > middle and line.end.y > middle


def line_intersection(line1, line2):
    def det(a, b):
        return a.x * b.y - a.y * b.x

    div = (line1.start.x - line1.end.x) * (line2.start.y - line2.end.y) - \
          (line1.start.y - line1.end.y) * (line2.start.x - line2.end.x)

    px = det(line1.start, line1.end) * (line2.start.x - line2.end.x) - \
         (line1.start.x - line1.end.x) * det(line2.start, line2.end)

    py = det(line1.start, line1.end) * (line2.start.y - line2.end.y) - \
         (line1.start.y - line1.end.y) * det(line2.start, line2.end)

    return Point(px / div, py / div)


def separate_lines(lines):
    horizontal_lines = []
    vertical_lines = []

    for line in lines:
        for x1, y1, x2, y2 in line:
            if abs(x2 - x1) < abs(y2 - y1):
                horizontal_lines.append(Line(Point(x1, y1), Point(x2, y2)))
            else:
                vertical_lines.append(Line(Point(x1, y1), Point(x2, y2)))

    horizontal_lines = sorted(horizontal_lines, key=lambda h_line: h_line.start.x)
    vertical_lines = sorted(vertical_lines, key=lambda v_line: v_line.start.y)

    return horizontal_lines, vertical_lines


def get_best_correlation(tile_image):
    best_score = ('.', 0)

    for letter in TEMPLATES:
        letter_image = cv2.imread('templates_fit/' + letter + '.jpg')
        score = cv2.matchTemplate(tile_image, letter_image, cv2.TM_CCORR_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(score)

        if max_val > best_score[1]:
            best_score = (letter, max_val)

    return best_score
