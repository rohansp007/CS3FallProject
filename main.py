import pygame
import math
import time
import random
from text import draw_text
from calcs import distance
from calcs import ang, normalize_angle
from calcs import draw_arrow
from calcs import linear_gradient
from calcs import generate_gradient
from calcs import normalize
import noise

pygame.init()

# ---------------- Setting up the screen, assigning some global variables, and loading text fonts
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
fps = 60
screen_width = screen.get_width()
screen_height = screen.get_height()
screen_center = [screen_width / 2, screen_height / 2]
screen2 = pygame.Surface((screen_width, screen_height)).convert_alpha()
screenT = pygame.Surface((screen_width, screen_height)).convert_alpha()
screenT.set_alpha(100)
screenUI = pygame.Surface((screen_width, screen_height)).convert_alpha()
timer = 0
shake = [0, 0]
shake_strength = 3
pygame.font.get_fonts()
font15 = pygame.font.Font("freesansbold.ttf", 15)
font20 = pygame.font.Font("freesansbold.ttf", 20)
font30 = pygame.font.Font("freesansbold.ttf", 30)
font40 = pygame.font.Font("freesansbold.ttf", 40)
better_font40 = pygame.font.SysFont("keyboard.ttf", 40)
font50 = pygame.font.Font("freesansbold.ttf", 50)
font100 = pygame.font.Font("freesansbold.ttf", 100)


class Endesga:
    maroon_red = [87, 28, 39]
    lighter_maroon_red = [127, 36, 51]
    dark_green = [9, 26, 23]
    light_brown = [191, 111, 74]
    black = [19, 19, 19]
    grey_blue = [66, 76, 110]
    cream = [237, 171, 80]
    white = [255, 255, 255]
    greyL = [200, 200, 200]
    grey = [150, 150, 150]
    greyD = [100, 100, 100]
    greyVD = [50, 50, 50]
    very_light_blue = [199, 207, 221]
    my_blue = [32, 36, 46]
    debug_red = [255, 96, 141]
    sebastian_lague_purple = [70, 74, 124]
    sebastian_lague_light_purple = [137, 133, 181]
    network_green = [64, 128, 67]
    network_red = [127, 45, 41]


# Defining some more variables to use in the game loop
oscillating_random_thing = 0
ShakeCounter = 0
toggle = True
click = False


class TileHandler:
    def __init__(self, width, height, size, tileType, spacing, sizeVariance, cols):
        self.size = size
        self.spacing = spacing
        self.tileType = tileType
        self.sizeVariance = sizeVariance
        self.tiles = []
        self.cols = cols
        self.shifter = [0, 0]
        self.shifterMomentum = [0, 0]

        if tileType == Hex:
            self.horizontal_distance = (3 / 2 * size) + spacing
            self.vertical_distance = (math.sqrt(3) * size) + spacing
            self.gridSizeX = int(width / self.horizontal_distance) + 2
            self.gridSizeY = int(height / self.vertical_distance) + 2
        elif tileType == Square:
            self.horizontal_distance = size + spacing
            self.vertical_distance = size + spacing
            self.gridSizeX = int(width / self.horizontal_distance) + 1
            self.gridSizeY = int(height / self.vertical_distance) + 1
        elif tileType == Triangle:
            self.horizontal_distance = size + spacing
            self.vertical_distance = (math.sqrt(3) / 2 * size) + spacing
            self.gridSizeX = int(width / self.horizontal_distance) + 2
            self.gridSizeY = int(height / self.vertical_distance) + 1
        else:
            raise NotImplementedError("Tile type not supported")

        self._generate_tiles()
        self._assign_adjacent_tiles()

    def _generate_tiles(self):
        for x in range(self.gridSizeX):
            for y in range(self.gridSizeY):
                if self.tileType == Hex:
                    x_pos = self.horizontal_distance * x
                    y_pos = self.vertical_distance * y
                    if x % 2 == 1:
                        y_pos += self.vertical_distance / 2
                    self.tiles.append(self.tileType(x, y, x_pos, y_pos, self.size, self.sizeVariance))
                elif self.tileType == Square:
                    x_pos = self.horizontal_distance * x
                    y_pos = self.vertical_distance * y
                    self.tiles.append(self.tileType(x, y, x_pos, y_pos, self.size, self.sizeVariance))
                elif self.tileType == Triangle:
                    x_pos = self.horizontal_distance * x
                    y_pos = self.vertical_distance * y
                    if y % 2 == 1:
                        x_pos -= self.horizontal_distance
                    self.tiles.append(self.tileType(x, y, x_pos, y_pos, self.size, self.sizeVariance, x))
                else:
                    raise NotImplementedError("Tile type not supported")

    def _assign_adjacent_tiles(self):
        grid_dict = {(tile.grid_x, tile.grid_y): tile for tile in self.tiles}

        for tile in self.tiles:
            tile.adjacent = []
            offsets = []

            if isinstance(tile, Hex):
                # Hex grid neighbors (cube coordinates or axial coordinates)
                if tile.grid_x % 2 == 0:
                    offsets = [(1, 0), (-1, 0), (0, 1), (0, -1), (-1, -1), (1, -1)]
                else:
                    offsets = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1)]

            elif isinstance(tile, Square):
                # Square grid neighbors
                offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            elif isinstance(tile, Triangle):
                # Triangle grid neighbors (assuming pointy-topped or flat-topped)
                if tile.index % 2 == 0:
                    offsets = [(0, -1), (-1, 1), (1, 1)]
                else:
                    offsets = [(0, 1), (-1, -1), (1, -1)]

            for dx, dy in offsets:
                neighbor_grid_x = tile.grid_x + dx
                neighbor_grid_y = tile.grid_y + dy

                if (neighbor_grid_x, neighbor_grid_y) in grid_dict:
                    tile.adjacent.append(grid_dict[(neighbor_grid_x, neighbor_grid_y)])

    def get_tile_at_position(self, x, y):
        for tile in self.tiles:
            if math.isclose(tile.x, x, abs_tol=self.horizontal_distance / 2) and math.isclose(tile.y, y, abs_tol=self.vertical_distance / 2):
                return tile
        return None

    def update(self):
        shifts = []
        for tile in self.tiles:
            sizesSum = sum([adj.size for adj in tile.adjacent]) / len(tile.adjacent)
            shifts.append((sizesSum - self.size) / 300)
        for i, tile in enumerate(self.tiles):
            tile.momentum += shifts[i]
            tile.momentum *= 0.98
            tile.size += tile.momentum
            tile.size = min(tile.originalSize + tile.sizeVariance, max(tile.originalSize - tile.sizeVariance, tile.size))
            tile.colIndex = normalize(tile.size, tile.originalSize - tile.sizeVariance, tile.originalSize + tile.sizeVariance, True)
            tile.col = linear_gradient(self.cols, tile.colIndex - 1e-10)

    def draw(self, s, showArrows):
        for tile in self.tiles:
            tile.draw(s)
        if showArrows:
            for tile in self.tiles:
                tile.drawArrows(s)


class Tile:
    def __init__(self, grid_x, grid_y, x, y, size, sizeVariance, col=(0, 0, 0)):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = x
        self.y = y
        self.originalSize = size
        self.sizeVariance = sizeVariance
        self.size = size + random.randint(-self.sizeVariance, self.sizeVariance)
        self.col = col
        self.adjacent = []
        self.colIndex = random.uniform(0, 1)
        self.momentum = 0

    def draw(self, s):
        pass


class Hex(Tile):
    def __init__(self, grid_x, grid_y, x, y, size, sizeVariance):
        super().__init__(grid_x, grid_y, x, y, size, sizeVariance)

    def draw(self, s):
        points = [(self.x + self.size * math.cos(math.pi / 3 * angle), self.y + self.size * math.sin(math.pi / 3 * angle)) for angle in range(6)]
        pygame.draw.polygon(s, self.col, points)

    def drawArrows(self, s):
        for adj in self.adjacent:
            angle = normalize_angle(ang((self.x, self.y), (adj.x, adj.y)))
            dist = distance((self.x, self.y), (adj.x, adj.y))
            factor = 0.35
            draw_arrow(s, (self.x, self.y), (self.x + dist * factor * math.cos(angle), self.y + dist * factor * math.sin(angle)), Endesga.debug_red, pygame, 2, 5, 25)


class Square(Tile):
    def __init__(self, grid_x, grid_y, x, y, size, sizeVariance):
        super().__init__(grid_x, grid_y, x, y, size, sizeVariance)

    def draw(self, s):
        half_size = self.size / 2
        points = [
            (self.x - half_size, self.y - half_size),
            (self.x + half_size, self.y - half_size),
            (self.x + half_size, self.y + half_size),
            (self.x - half_size, self.y + half_size)
        ]
        pygame.draw.polygon(s, self.col, points)


class Triangle(Tile):
    def __init__(self, grid_x, grid_y, x, y, size, sizeVariance, index):
        super().__init__(grid_x, grid_y, x, y, size, sizeVariance)
        self.index = index

    def draw(self, s):
        half_size = self.size / 2
        height = (math.sqrt(3) / 2) * self.size
        if self.index % 2 == 0:
            points = [
                (self.x, self.y - height / 2),
                (self.x - half_size, self.y + height / 2),
                (self.x + half_size, self.y + height / 2)
            ]
        else:
            points = [
                (self.x, self.y + height / 2),
                (self.x - half_size, self.y - height / 2),
                (self.x + half_size, self.y - height / 2)
            ]
        pygame.draw.polygon(s, self.col, points)


# ICE
# colRange = [[252, 9], [241, 59], [214, 64]]

# CARDBOARD WIREFRAME
# colRange = [[77, 172], [53, 152], [22, 118]]
# Turn on outlines and remove the black dots. Also make them move really slow

# RED
# colRange = [[16, 226], [2, 66], [6, 69]]
# colRange = [[226, 66, 69], [16, 2, 6]]

# SUNRISE
# colRange = [[61, 234], [20, 163], [15, 81]]

# CITY
# colRange = [[67, 155], [62, 149], [87, 159]]

# SUNSET
# colRange = [[40, 254], [8, 115], [15, 77]]

# Rishabh's Blue/Purple Thing
# colRange = [[104, 24, 28], [22, 12, 63]]

# My (better) analogous blue
# colRange = [[1, 155], [22, 193], [56, 253]]

# Embers
# colRange = [[40, 30, 40], [12, 9, 10]]

# White to Red
# colRange = [[255, 255, 255], [218, 205, 144], [174, 116, 84], [72, 44, 72], [120, 32, 61]]

# Dark Blue to Red to Yellow (THIS IS THE GOOD ONE FROM THE VIDEO)
# colRange = [[255, 207, 69], [255, 174, 70], [254, 78, 66], [104, 0, 52], [63, 0, 47], [32, 2, 47]]
# colRange.reverse()

# White to Blue Glower
# colRange = [[255, 255, 255], [133, 202, 242], [67, 115, 160], [44, 43, 65], [26, 26, 26]]
# colRange.reverse()

# # Noxus RED
# colRange = [[32, 25, 23], [81, 79, 80], [114, 63, 64], [207, 126, 43]]
# colRange.reverse()

# Pyke Bartender Scene
# colRange = [[38, 27, 7], [2, 2, 2]]

# Mint
# colRange = [[201, 210, 197], [132, 169, 139], [81, 121, 110], [54, 78, 81], [47, 62, 70]]
# colRange.reverse()

# Website
# colRange = [[253, 246, 227], [253, 246, 227], [220, 50, 47], [3, 7, 18], [3, 7, 18]]

# Dark Blurple
colRange = [(31, 8, 45), (33, 13, 55), (33, 21, 66), (34, 29, 77), (40, 43, 88)]

# Smutty Fire
# colRange = [(42, 18, 14), (59, 25, 18), (76, 34, 20), (93, 44, 21), (111, 56, 20)]

# Define starting and ending colors
dark = (31, 8, 45)
light = (40, 43, 88)

# Generate gradient
# colRange = generate_gradient(dark, light, 5)
print(colRange)

tileSize = 20
tileSpacing = 5
tileSizeVariance = 5
TH = TileHandler(screen_width, screen_height, tileSize, Hex, tileSpacing, tileSizeVariance, colRange)

# ---------------- Main Game Loop
last_time = time.time()
running = True
while running:

    # ---------------- Reset Variables and Clear screens
    mx, my = pygame.mouse.get_pos()
    screen.fill(colRange[0])
    screen2.fill(colRange[0])
    screenT.fill((0, 0, 0, 0))
    screenUI.fill((0, 0, 0, 0))
    dt = time.time() - last_time
    dt *= fps
    last_time = time.time()
    timer -= dt
    shake = [0, 0]
    oscillating_random_thing += math.pi / fps * dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            click = True
        if event.type == pygame.MOUSEBUTTONUP:
            click = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                toggle = not toggle
        if event.type == pygame.KEYUP:
            pass

    TH.draw(screen2, True)
    TH.update()

    # for t in TH.tiles:
    #     if distance((t.x, t.y), (mx, my)) < 50:
    #         t.size += random.randint(-10, 10)

    # ---------------- Updating Screen
    if toggle:
        draw_text(screenUI, Endesga.debug_red, better_font40, 20, screen_height - 40, str(round(clock.get_fps())), Endesga.black, 3)
        pygame.mouse.set_visible(False)
        pygame.draw.circle(screenUI, Endesga.black, (mx + 1, my + 1), 5, 1)
        pygame.draw.circle(screenUI, Endesga.white, (mx, my), 5, 1)
    screen.blit(screen2, (shake[0], shake[1]))
    screen.blit(screenT, (0, 0))
    screen.blit(screenUI, (0, 0))
    pygame.display.update()
    clock.tick(fps)
