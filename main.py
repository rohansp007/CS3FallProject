import pygame
import math
import time
import random
from text import draw_text
from calcs import distance
from calcs import ang, normalize_angle
from calcs import draw_arrow

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
toggle = 2
click = False


class TileHandler:
    def __init__(self, width, height, size, tileType, spacing, sizeVariance, backgroundBaseSearchedWallFoundCols, wallSpawnProb):
        self.maxWidth = width
        self.maxHeight = height
        self.size = size
        self.spacing = spacing
        self.tileType = tileType
        self.sizeVariance = sizeVariance
        self.tiles = []
        self.tile_map = {}  # Position-to-tile map
        self.backgroundBaseSearchedWallFoundCols = backgroundBaseSearchedWallFoundCols
        self.shifter = [0, 0]
        self.shifterMomentum = [0, 0]
        self.wallProb = wallSpawnProb

        if tileType == Hex:
            self.horizontal_distance = (3 / 2 * size) + spacing
            self.vertical_distance = (math.sqrt(3) * size) + spacing
            self.gridSizeX = int(width / self.horizontal_distance)
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
                    tile = self.tileType(x, y, x_pos, y_pos, self.size, self.sizeVariance)
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
            tile.col = self.backgroundBaseSearchedWallFoundCols[1]
            tile.col2 = self.backgroundBaseSearchedWallFoundCols[2]
            tile.wallCol = self.backgroundBaseSearchedWallFoundCols[3]
            tile.pathCol = self.backgroundBaseSearchedWallFoundCols[4]

    def draw(self, s, showArrows):
        for tile in self.tiles:
            tile.draw(s)
        if showArrows:
            for tile in self.tiles:
                tile.drawArrows(s)


class Tile:
    def __init__(self, grid_x, grid_y, x, y, size, sizeVariance, col=(0, 0, 0), col2=(0, 0, 0), wallCol=(0, 0, 0), pathCol=(0, 0, 0)):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = x
        self.y = y
        self.originalSize = size
        self.sizeVariance = sizeVariance
        self.size = size + random.randint(-self.sizeVariance, self.sizeVariance)
        self.col = col
        self.col2 = col2
        self.wallCol = wallCol
        self.pathCol = pathCol
        self.adjacent = []
        self.colIndex = random.uniform(0, 1)
        self.momentum = 0
        self.searched = False
        self.isWall = False
        self.isPartOfPath = False

    def draw(self, s):
        raise NotImplementedError


class Hex(Tile):
    def __init__(self, grid_x, grid_y, x, y, size, sizeVariance):
        super().__init__(grid_x, grid_y, x, y, size, sizeVariance)

    def draw(self, s):
        points = [(self.x + self.size * math.cos(math.pi / 3 * angle), self.y + self.size * math.sin(math.pi / 3 * angle)) for angle in range(6)]
        if self.isWall:
            pygame.draw.polygon(s, self.wallCol, points)
        elif self.isPartOfPath:
            pygame.draw.polygon(s, self.pathCol, points)
        else:
            if self.searched:
                pygame.draw.polygon(s, self.col2, points)
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

        self.displaySpacing = 0
        self.spacing = 10


class DrawingNode:
    def __init__(self, parent, depth):
        self.parent = parent
        self.depth = depth
        self.horizontalRank = 0
        self.children = []
        self.highlighted = False
        self.isPath = False


def getPath(finalNode):
    """
    Marks all nodes in the final path and returns the path.
    Resets previous path markings for consistency.
    """
    path = []
    current = finalNode

    # Clear all previous path markings
    while current:
        current.tile.isPartOfPath = False
        current = current.parent

    current = finalNode
    while current is not None:
        current.tile.isPartOfPath = True  # Mark as part of the path
        path.append(current)
        current = current.parent

    return path[::-1]  # Reverse to get the path from root to final


def calculateRowCountRecursor(node, tre, runningList, searchedPositions, drawingNodeParent, node_map):
    """
    Recursively calculates row counts and builds the drawing tree.
    Ensures all searched nodes are included and avoids incorrect path markings.
    """
    for adj in node.tile.adjacent:
        tile_key = (adj.x, adj.y)

        # Skip nodes already processed
        if tile_key in searchedPositions:
            continue

        # Process closed nodes
        if tile_key in tre.closed:
            # Retrieve or create a DrawingNode
            if tile_key in node_map:
                child_node = node_map[tile_key]
            else:
                child_node = DrawingNode(drawingNodeParent, drawingNodeParent.depth + 1)
                child_tile = tre.closed[tile_key].tile

                # Update child properties
                child_node.isPath = child_tile.isPartOfPath
                child_node.highlighted = child_tile.searched
                node_map[tile_key] = child_node

            # Append child node to parent's children
            drawingNodeParent.children.append(child_node)

            # Mark tile as searched
            searchedPositions.add(tile_key)

            # Update row counts for the depth
            depth_index = tre.closed[tile_key].g - 1
            if 0 <= depth_index < len(runningList):
                runningList[depth_index] += 1

            # Recursively process child node
            calculateRowCountRecursor(tre.closed[tile_key], tre, runningList, searchedPositions, child_node, node_map)

    return runningList


def calculateSpacingRecursor(node, runningNodeList, horizontalRankTracker, maxWidth):
    """
    Assigns horizontal ranks to nodes, ensuring parent nodes align with their children.
    """
    # Ensure the tracker has an entry for the current depth
    while len(horizontalRankTracker) <= node.depth:
        horizontalRankTracker.append(0)

    # Recurse for children first
    for child in node.children:
        calculateSpacingRecursor(child, runningNodeList, horizontalRankTracker, maxWidth)

    # Align parent node based on children
    if node.children:
        child_positions = [child.horizontalRank for child in node.children]
        node.horizontalRank = sum(child_positions) / len(child_positions)
    else:
        # Assign a unique rank for nodes without children
        node.horizontalRank = horizontalRankTracker[node.depth]
        horizontalRankTracker[node.depth] += 1

    # Add the node to its corresponding depth list
    while len(runningNodeList) <= node.depth:
        runningNodeList.append([])
    if node not in runningNodeList[node.depth]:
        runningNodeList[node.depth].append(node)

    return runningNodeList


def draw(width, height, tre, root, cols):
    """
    Draws the tree structure on a surface with parent nodes roughly aligned with their children,
    ensuring rows are centered horizontally when necessary.
    """
    path = 1000
    runningList = [0] * path
    searchedPositions = set()
    node_map = {}  # Map to ensure unique nodes per tile
    drawingRoot = DrawingNode(root, 0)
    drawingRoot.isPath = True

    # Calculate row counts and node hierarchy
    calculateRowCountRecursor(root, tre, runningList, searchedPositions, drawingRoot, node_map)
    runningNodeList = calculateSpacingRecursor(drawingRoot, [[] for _ in range(path)], [], width)

    # Create surface
    sur = pygame.Surface((width, height)).convert_alpha()
    sur.fill((0, 0, 0, 0))  # Transparent background

    # Calculate total depth
    total_depth = len([layer for layer in runningNodeList if layer])

    # Draw the tree
    displaySize = 5
    node_positions = {}
    for y, layer in enumerate(runningNodeList):
        if layer:
            # Sort nodes by their horizontal rank
            layer = sorted(layer, key=lambda n: n.horizontalRank)

            # Determine centering offset
            min_rank = min(node.horizontalRank for node in layer)
            max_rank = max(node.horizontalRank for node in layer)
            layer_width = max_rank - min_rank + 1

            # Center the row if it is shifted off-center
            total_width = layer_width * (width / (layer_width + 1))
            row_center = (min_rank + max_rank) / 2
            center_offset = (width / 2) - (row_center * (width / layer_width))

            for node in layer:
                # Adjust node positions based on `horizontalRank` and centering offset
                pos_x = (node.horizontalRank - min_rank) * (width / layer_width) + center_offset
                pos_y = 20 + y * (height // (total_depth + 1))

                # Draw nodes
                if node.isPath:
                    pygame.draw.circle(sur, cols[4], (int(pos_x), int(pos_y)), displaySize)
                elif node.highlighted:
                    pygame.draw.circle(sur, cols[2], (int(pos_x), int(pos_y)), displaySize)
                else:
                    pygame.draw.circle(sur, cols[1], (int(pos_x), int(pos_y)), displaySize)

                # Store node positions for connecting lines
                node_positions[node] = (int(pos_x), int(pos_y))

    # Draw lines between parent and children
    for node, pos in node_positions.items():
        for child in node.children:
            child_pos = node_positions.get(child, None)
            if child_pos:
                pygame.draw.line(sur, (200, 200, 200), pos, child_pos, 2)

    for node in node_positions:
        if node.isPath:
            pos_x, pos_y = node_positions[node]
            pygame.draw.circle(sur, cols[4], (int(pos_x), int(pos_y)), displaySize)

    return sur


class Tree:
    def __init__(self, root):
        self.root = Node(None, root)
        self.final = None
        self.open = [self.root]
        self.openPositions = {(self.root.tile.x, self.root.tile.y): self.root}
        self.closed = {}
        self.found = False

    def resetPathFlags(tre):
        """Reset all isPath flags to False before starting a new search."""
        for node in tre.closed.values():
            node.isPath = False
        for node in tre.open:
            node.isPath = False

    def fullSearch(self, final):
        self.open = [self.root]
        self.openPositions = {(self.root.tile.x, self.root.tile.y): self.root}
        self.closed = {}
        self.final = final
        self.found = False
        self.resetPathFlags()

    def searchStep(tre):
        """
        A* Search Step implementation ensuring proper path flagging
        and inclusion of all searched nodes without disrupting the final path.
        """
        if not tre.found:
            if len(tre.open) > 0:
                # Get the node with the lowest f-value
                current = min(tre.open, key=lambda n: n.f)
                tre.open.remove(current)
                tre.closed[(current.tile.x, current.tile.y)] = current

                # Check if the goal is reached
                if (current.tile.x, current.tile.y) == (tre.final.x, tre.final.y):
                    tre.found = True
                    tre.final = None
                    return getPath(current)

                # Process adjacent tiles
                for adj in current.tile.adjacent:
                    if adj.isWall:
                        continue

                    # Avoid nodes in the closed set
                    if (adj.x, adj.y) in tre.closed:
                        continue

                    # Check or update nodes in the open set
                    if (adj.x, adj.y) in tre.openPositions:
                        node = tre.openPositions[(adj.x, adj.y)]
                        tentative_g = current.g + 1
                        if tentative_g < node.g:
                            node.g = tentative_g
                            node.f = node.g + node.h
                            node.parent = current
                        continue

                    # Add new child node
                    child = Node(current, adj, g=current.g + 1, f=current.g + 1 + distance((adj.x, adj.y), (tre.final.x, tre.final.y)))
                    tre.open.append(child)
                    tre.openPositions[(adj.x, adj.y)] = child


backgroundBaseSearchedWallFoundColors = [[19, 2, 8], [49, 5, 30], [124, 24, 60], [24, 4, 12], [255, 130, 116]]
splitProportion = 0.5

tileSize = 10
tileSpacing = 0
tileSizeVariance = 0

wallProb = 0.5

distanceFromTopLeft = 0.05
TH = TileHandler(screen_width * splitProportion, screen_height, tileSize, Hex, tileSpacing, tileSizeVariance, backgroundBaseSearchedWallFoundColors, wallProb)
startingIndex = round(round(distanceFromTopLeft * TH.gridSizeX) * TH.gridSizeY + TH.gridSizeY + round(distanceFromTopLeft * TH.gridSizeX))
while TH.tiles[startingIndex].isWall:
    startingIndex += 1
tree = Tree(TH.tiles[startingIndex])
tileIndex = None
stepOutput = None
treeSurface = None

# ---------------- Main Game Loop
last_time = time.time()
running = True
while running:

    # ---------------- Reset Variables and Clear screens
    mx, my = pygame.mouse.get_pos()
    screen.fill(backgroundBaseSearchedWallFoundColors[0])
    screen2.fill(backgroundBaseSearchedWallFoundColors[0])
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

    for til in TH.tiles:
        til.searched = False
        til.isPartOfPath = False

    if stepOutput is not None:
        for nod in stepOutput:
            nod.tile.isPartOfPath = True

    for nod in tree.closed:
        TH.get_tile_at_grid_position(round(nod[0]), round(nod[1])).searched = True

    TH.tiles[startingIndex].isPartOfPath = True
    if tileIndex is not None:
        TH.tiles[tileIndex].isPartOfPath = True

    TH.draw(screen2, False)
    TH.update()

    if click:
        distances = {}
        for i, til in enumerate(TH.tiles):
            d = distance((til.x, til.y), (mx, my))
            if d < TH.size * 50 and not til.isWall:
                distances[d] = i
        tileIndex = distances[sorted(distances.keys())[0]]

        # Search
        tree.fullSearch(TH.tiles[int(tileIndex)])
    if tree.final is not None:
        for _ in range(int(len(TH.tiles) ** 0.8 / 100)):
            stepOutput = tree.searchStep()
            if stepOutput is not None:
                break

    treeSurface = draw(screen_width * (1 - splitProportion), screen_height, tree, tree.root, backgroundBaseSearchedWallFoundColors)
    if treeSurface is not None:
        screen2.blit(treeSurface, (screen_width * splitProportion, 0))

    # ---------------- Updating Screen
    if toggle:
        pygame.mouse.set_visible(False)
        pygame.draw.circle(screenUI, Endesga.black, (mx + 1, my + 1), 5, 1)
        pygame.draw.circle(screenUI, Endesga.white, (mx, my), 5, 1)
        if toggle == 2:
            draw_text(screenUI, Endesga.debug_red, better_font40, 20, screen_height - 40, str(round(clock.get_fps())), Endesga.black, 3)
    screen.blit(screen2, (shake[0], shake[1]))
    screen.blit(screenT, (0, 0))
    screen.blit(screenUI, (0, 0))
    pygame.display.update()
    clock.tick(fps)
