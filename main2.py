import pygame
import math
import time
import random
from text import draw_text
from calcs import distance
from calcs import ang, normalize_angle
from calcs import draw_arrow
import copy

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


class TileHandler:
    def __init__(self, width, height, size, tileType, spacing, backgroundBaseSearchedWallPathKnownCols, wallSpawnProb):
        self.maxWidth = width
        self.maxHeight = height
        self.size = size
        self.spacing = spacing
        self.tileType = tileType
        self.tiles = []
        self.tile_map = {}  # Position-to-tile map
        self.backgroundBaseSearchedWallPathKnownCols = backgroundBaseSearchedWallPathKnownCols
        self.shifter = [0, 0]
        self.shifterMomentum = [0, 0]
        self.wallProb = wallSpawnProb

        if tileType == Hex:
            self.horizontal_distance = (3 / 2 * size) + spacing
            self.vertical_distance = (math.sqrt(3) * size) + spacing
            self.gridSizeX = int(width / self.horizontal_distance) + 2
            self.gridSizeY = int(height / self.vertical_distance) + 2
        else:
            raise NotImplementedError("Tile type not supported")

        self._generate_tiles()
        self._assign_adjacent_tiles()
        self.aggregate()

    def _generate_tiles(self):
        for x in range(self.gridSizeX):
            for y in range(self.gridSizeY):
                if self.tileType == Hex:
                    x_pos = self.horizontal_distance * x
                    y_pos = self.vertical_distance * y
                    if x % 2 == 1:
                        y_pos += self.vertical_distance / 2
                    tile = self.tileType(x, y, x_pos, y_pos, self.size)
                else:
                    raise NotImplementedError("Tile type not supported")

                self.tiles.append(tile)
                self.tile_map[(round(tile.x), round(tile.y))] = tile  # Map position to tile

        for tile in self.tiles:
            dist = (distance((tile.x, tile.y), (self.maxWidth, self.maxHeight))) / (distance((0, 0), (self.maxWidth, self.maxHeight)))
            if random.random() < (self.wallProb * (1 - dist) ** 0.3):
                tile.isWall = True
                tile.momentum = 1

    def get_tile_at_grid_position(self, x, y):
        return self.tile_map.get((x, y), None)

    def _assign_adjacent_tiles(self):
        grid_dict = {(tile.grid_x, tile.grid_y): tile for tile in self.tiles}

        for tile in self.tiles:
            tile.adjacent = []

            if tile.grid_x % 2 == 0:
                offsets = [(1, 0), (-1, 0), (0, 1), (0, -1), (-1, -1), (1, -1)]
            else:
                offsets = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1)]

            for dx, dy in offsets:
                neighbor_grid_x = tile.grid_x + dx
                neighbor_grid_y = tile.grid_y + dy

                if (neighbor_grid_x, neighbor_grid_y) in grid_dict:
                    tile.adjacent.append(grid_dict[(neighbor_grid_x, neighbor_grid_y)])

    def aggregate(self):
        for _ in range(2):
            shifts = []
            for tile in self.tiles:
                momentumSum = sum([adj.momentum for adj in tile.adjacent]) / len(tile.adjacent)
                shifts.append((momentumSum - tile.momentum) / 3)
            for _, tile in enumerate(self.tiles):
                tile.momentum += shifts[_]
        for _, tile in enumerate(self.tiles):
            self.tiles[_].isWall = tile.momentum > 0.5

    def update(self):
        for _, tile in enumerate(self.tiles):
            tile.col = self.backgroundBaseSearchedWallPathKnownCols[1]
            tile.col2 = self.backgroundBaseSearchedWallPathKnownCols[2]
            tile.wallCol = self.backgroundBaseSearchedWallPathKnownCols[3]
            tile.pathCol = self.backgroundBaseSearchedWallPathKnownCols[4]
            tile.knownCol = self.backgroundBaseSearchedWallPathKnownCols[5]

    def draw(self, s, showArrows):
        for tile in self.tiles:
            tile.draw(s)
        if showArrows:
            for tile in self.tiles:
                tile.drawArrows(s)


class Tile:
    def __init__(self, grid_x, grid_y, x, y, size, col=(0, 0, 0), col2=(0, 0, 0), wallCol=(0, 0, 0), pathCol=(0, 0, 0), knownCol=(0, 0, 0)):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = x
        self.y = y
        self.originalSize = size
        self.size = size
        self.col = col
        self.col2 = col2
        self.wallCol = wallCol
        self.pathCol = pathCol
        self.knownCol = knownCol
        self.adjacent = []
        self.colIndex = random.uniform(0, 1)
        self.momentum = 0
        self.searched = False
        self.isWall = False
        self.isPartOfPath = False
        self.known = False

    def draw(self, s):
        pass


class Hex(Tile):
    def __init__(self, grid_x, grid_y, x, y, size):
        super().__init__(grid_x, grid_y, x, y, size)

    def draw(self, s):
        points = [(self.x + self.size * math.cos(math.pi / 3 * angle), self.y + self.size * math.sin(math.pi / 3 * angle)) for angle in range(6)]
        if self.isWall:
            pygame.draw.polygon(s, self.wallCol, points)
        elif self.isPartOfPath:
            pygame.draw.polygon(s, self.pathCol, points)
        else:
            if self.searched:
                pygame.draw.polygon(s, self.col2, points)
            elif self.known:
                pygame.draw.polygon(s, self.knownCol, points)
            else:
                pygame.draw.polygon(s, self.col, points)

    def drawArrows(self, s):
        for adj in self.adjacent:
            angle = normalize_angle(ang((self.x, self.y), (adj.x, adj.y)))
            dist = distance((self.x, self.y), (adj.x, adj.y))
            factor = 0.35
            draw_arrow(s, (self.x, self.y), (self.x + dist * factor * math.cos(angle), self.y + dist * factor * math.sin(angle)), Endesga.debug_red, pygame, 2, 5, 25)


class Node:
    def __init__(self, parent, tile, g=0, f=0, h=0, children=None):
        self.parent = parent
        self.tile = tile
        self.g = g
        self.f = f
        self.h = h
        self.children = [] if children is None else children


def getPath(finalNode):
    out = [finalNode]
    while finalNode.parent is not None:
        out.append(finalNode.parent)
        finalNode = finalNode.parent
    return out


class Tree:
    def __init__(self, root):
        self.root = Node(None, root)
        self.final = None
        self.open = [self.root]
        self.openPositions = {(self.root.tile.x, self.root.tile.y): self.root}
        self.closed = {}
        self.closedPositions = set()
        self.found = False

    def fullSearch(self, final):
        self.open = [self.root]
        self.openPositions = {(self.root.tile.x, self.root.tile.y): self.root}
        self.closed = {}
        self.final = final
        self.found = False

    def searchStep(self, nodeGraph):
        if not self.found:
            if len(self.open) > 0:
                # Get the node with the lowest f-value
                current = sorted(self.open, key=lambda n: n.f)[0]
                self.open.remove(current)
                self.closed[(current.tile.x, current.tile.y)] = current
                self.closedPositions.add((int(current.tile.x), int(current.tile.y)))

                # Check if we have reached the goal
                if (current.tile.x, current.tile.y) == (self.final.x, self.final.y):
                    self.found = True
                    self.final = None
                    return getPath(current)

                # Process adjacent tiles
                for adj in current.tile.adjacent:
                    if adj.isWall:
                        continue

                    # Check if the tile is already in the closed set
                    if (adj.x, adj.y) in self.closed:
                        continue

                    # Check if the tile is already in the open set
                    if (adj.x, adj.y) in self.openPositions:
                        node = self.openPositions[(adj.x, adj.y)]
                        tentative_g = current.g + 1
                        if tentative_g < node.g:
                            node.g = tentative_g
                            node.f = node.g + node.h
                            node.parent = current
                            nodeGraph.counter += 1  # nodeGraph.getNode((adj.x, adj.y)).parent.children.remove(nodeGraph.getNode((adj.x, adj.y)))  # nodeGraph.getNode((adj.x, adj.y)).parent = nodeGraph.getNode((current.tile.x, current.tile.y))
                        continue

                    # Add new child node
                    child = Node(current, adj)
                    child.g = current.g + 1
                    child.h = distance((self.final.x, self.final.y), (adj.x, adj.y))
                    child.f = child.g + child.h
                    self.open.append(child)
                    self.openPositions[(adj.x, adj.y)] = child
                    if not nodeGraph.checkExists((adj.x, adj.y)):
                        nodeGraph.addNode(nodeGraph.getNode((current.tile.x, current.tile.y)), (adj.x, adj.y), child.f)
        return None


class DrawingNode:
    def __init__(self, parent, pos, fScore):
        self.parent = parent
        self.children = []
        self.pos = pos
        self.depth = 0

        # Display stuff
        self.x = None
        self.y = None
        self.horizontalRank = 0
        self.fScore = fScore


class Graph:
    def __init__(self, backgroundBaseSearchedWallPathKnownCols):
        self.root = None
        self.knownPositions = {}
        self.counter = 0
        self.runningList = []
        self.maxDepth = 0
        self.displayPadding = 20

        self.prevPath = []

        self.backgroundBaseSearchedWallPathKnownCols = backgroundBaseSearchedWallPathKnownCols

    def addNode(self, parent, pos, fScore=0):
        new = DrawingNode(parent, (int(pos[0]), int(pos[1])), fScore)
        # passing a new root node (when parent == None) acts like a full object reset
        if parent is None:
            self.__init__(self.backgroundBaseSearchedWallPathKnownCols)
            new.depth = 0
            self.root = new
        else:
            new.depth = parent.depth + 1
            if new.depth > self.maxDepth:
                self.maxDepth = new.depth
            parent.children.append(new)
        self.knownPositions[(int(pos[0]), int(pos[1]))] = new

    def getNode(self, pos):
        return self.knownPositions[(int(pos[0]), int(pos[1]))]

    def checkExists(self, pos):
        return (int(pos[0]), int(pos[1])) in self.knownPositions

    def calculateSpacingRecursor(self, node, runningList, path=None):
        # Sorting children to alternate left and right moving inwards (smallest fScore, the best node, is in the middle)
        for c in node.children:
            if path is not None and c.pos in path:
                c.fScore -= 1e99
        sortedChildren = sorted(node.children, key=lambda x: (x.fScore, x.pos))
        node.children = []
        for childI, child in enumerate(sortedChildren):
            node.children.append(child) if childI % 2 == 0 else node.children.insert(0, child)

        for child in node.children:
            if child.depth > len(runningList) - 1:
                runningList.append(1)
            runningList[child.depth] += 1
            child.horizontalRank = runningList[child.depth] - 1
            runningList = self.calculateSpacingRecursor(child, runningList)
        return runningList

    def draw(self, width, height, path=None, closed=None):
        if path is not None:
            path = set([(int(t.tile.x), int(t.tile.y)) for t in path])
        if closed is not None:
            closed = set([(int(t[0]), int(t[1])) for t in closed])

        # Create surface
        sur = pygame.Surface((width, height)).convert_alpha()
        sur.fill((0, 0, 0, 0))
        if self.root is not None:
            #                                      running list starts with size 1 at row 0
            self.runningList = self.calculateSpacingRecursor(self.root, [1], path)
            if self.root.x is None:
                self.root.x = self.displayPadding + (width - 2 * self.displayPadding) / 2
                self.root.y = self.displayPadding
            self.surBuilderRecursor(sur, self.root, path, closed)
        return sur

    def surBuilderRecursor(self, sur, node, path=None, closed=None):
        for childI, child in enumerate(node.children):
            child.y = node.y + min(20, 1 / self.maxDepth * (sur.get_height() - 2 * self.displayPadding))
            child.x = self.displayPadding + ((child.horizontalRank - self.runningList[child.depth] / 2) / self.runningList[child.depth] + 0.5) * (sur.get_width() - 2 * self.displayPadding)
            pygame.draw.line(sur, (255, 255, 255), (node.x, node.y), (child.x, child.y))
            self.surBuilderRecursor(sur, child, path, closed)
        
        col = self.backgroundBaseSearchedWallPathKnownCols[5]
        if closed is not None:
            if node.pos in closed:
                col = self.backgroundBaseSearchedWallPathKnownCols[2]
        if path is not None:
            if node.pos in path:
                col = self.backgroundBaseSearchedWallPathKnownCols[4]
        pygame.draw.circle(sur, col, (node.x, node.y), 4)


# Defining some more variables to use in the game loop
oscillating_random_thing = 0
ShakeCounter = 0
toggle = 2
click = False

# Color scheme and node-graph size
backgroundBaseSearchedWallPathKnownColors = [[19, 2, 8], [49, 5, 30], [128, 45, 64], [24, 4, 12], [255, 130, 116], [82, 20, 47]]
splitProportion = 0.9

# Tile display params
tileSize = 10
tileSpacing = 3

# Wall spawning sparsity
wallProb = 0.5

# Create tile handler object
TH = TileHandler(screen_width * splitProportion, screen_height, tileSize, Hex, tileSpacing, backgroundBaseSearchedWallPathKnownColors, wallProb)
TH.update()

# Find non-wall starting tile
distanceFromTopLeft = 0.05
startingIndex = round(round(distanceFromTopLeft * TH.gridSizeX) * TH.gridSizeY + TH.gridSizeY + round(distanceFromTopLeft * TH.gridSizeX))
while TH.tiles[startingIndex].isWall:
    startingIndex += 1
tree = Tree(TH.tiles[startingIndex])

# Initialize user-clicked tile, (empty) path, and node-graph surface
tileIndex = None
stepOutput = None
treeSurface = None

# Create node-graph object
graph = Graph(backgroundBaseSearchedWallPathKnownColors)

# ---------------- Main Game Loop
last_time = time.time()
running = True
while running:

    # ---------------- Reset Variables and Clear screens
    mx, my = pygame.mouse.get_pos()
    screen.fill(backgroundBaseSearchedWallPathKnownColors[0])
    screen2.fill(backgroundBaseSearchedWallPathKnownColors[0])
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
                toggle += 1
                toggle = toggle % 3
        if event.type == pygame.KEYUP:
            pass

    # Reset searched and highlighted
    for til in TH.tiles:
        til.searched = False
        til.isPartOfPath = False
        til.known = False

    # Selectively set isPartOfPath if a path is found
    if stepOutput is not None:
        for nod in stepOutput:
            nod.tile.isPartOfPath = True

    # Selectively set known and searched regardless of if a path is found
    for tilePos in tree.openPositions:
        TH.get_tile_at_grid_position(round(tilePos[0]), round(tilePos[1])).known = True
    for nod in tree.closed:
        TH.get_tile_at_grid_position(round(nod[0]), round(nod[1])).searched = True

    # Draw tiles
    TH.draw(screen2, False)

    # User click
    if click:
        # Find the closest tile to the user's mouse, exclude walls
        distances = {}
        for i, til in enumerate(TH.tiles):
            d = distance((til.x, til.y), (mx, my))
            if d < TH.size * 50 and not til.isWall:
                distances[d] = i
        tileIndex = distances[sorted(distances.keys())[0]]

        # Begin search
        tree.fullSearch(TH.tiles[int(tileIndex)])

        # Add root to drawing node tree
        graph.addNode(None, (TH.tiles[startingIndex].x, TH.tiles[startingIndex].y))

    # Search step
    if tree.final is not None:
        for _ in range(int(len(TH.tiles) ** 0.8 / 200)):
            stepOutput = tree.searchStep(graph)
            if stepOutput is not None:
                break

    # Draw node graph
    treeSurface = graph.draw(screen_width * (1 - splitProportion - 0.02), screen_height, stepOutput, tree.closedPositions)
    if treeSurface is not None:
        screen2.blit(treeSurface, (screen_width * (splitProportion + 0.02), 0))

    # ---------------- Updating Screen
    if toggle:
        pygame.mouse.set_visible(False)
        pygame.draw.circle(screenUI, Endesga.black, (mx + 1, my + 1), 5, 1)
        pygame.draw.circle(screenUI, Endesga.white, (mx, my), 5, 1)
        if toggle == 2:
            items = {round(clock.get_fps()): None, }
            for i, label in enumerate(items.keys()):
                string = str(label)
                if items[label] is not None:
                    string = f"{items[label]}: " + string
                draw_text(screenUI, Endesga.debug_red, better_font40, 20, screen_height - (40 + 30 * i), string, Endesga.black, 3)
    screen.blit(screen2, (shake[0], shake[1]))
    screen.blit(screenT, (0, 0))
    screen.blit(screenUI, (0, 0))
    pygame.display.update()
    clock.tick(fps)
