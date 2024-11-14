import math
import random
import colorsys
import numpy as np


def distance(point1, point2):
    return math.sqrt(math.pow(math.fabs(point1[0] - point2[0]), 2) + math.pow(math.fabs(point1[1] - point2[1]), 2))


def ang(start_pos, end_pos):
    return math.atan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0])


def normalize_angle(angle):
    return angle % (2 * math.pi)


def collide_circle(point1, point2, d):
    return math.sqrt(math.pow(math.fabs(point1[0] - point2[0]), 2) + math.pow(math.fabs(point1[1] - point2[1]), 2)) < d


def rgb_to_hsv(r, g, b):
    """
    Convert RGB to HSV.
    :param r: Red value (0-255)
    :param g: Green value (0-255)
    :param b: Blue value (0-255)
    :return: (hue, saturation, value) where hue is in [0, 1], saturation and value are in [0, 1]
    """
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    return colorsys.rgb_to_hsv(r, g, b)


def hsv_to_rgb(h, s, v):
    """
    Convert HSV to RGB.
    :param h: Hue (0-1)
    :param s: Saturation (0-1)
    :param v: Value (0-1)
    :return: (r, g, b) where r, g, b are in [0, 255]
    """
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)


def adjust_hue(color, hue_shift):
    """
    Adjust the hue of the RGB color.
    :param color:
    :param hue_shift: Hue shift (0-1)
    :return: New RGB values
    """
    h, s, v = rgb_to_hsv(color[0], color[1], color[2])
    h = (h + hue_shift) % 1.0
    return hsv_to_rgb(h, s, v)


def adjust_saturation(color, saturation_factor):
    """
    Adjust the saturation of the RGB color.
    :param color:
    :param saturation_factor: Saturation factor (0-1)
    :return: New RGB values
    """
    h, s, v = rgb_to_hsv(color[0], color[1], color[2])
    s = min(max(s * saturation_factor, 0), 1)
    return hsv_to_rgb(h, s, v)


def adjust_brightness(color, brightness_factor):
    """
    Adjust the brightness of the RGB color.
    :param color:
    :param brightness_factor: Brightness factor (0-1)
    :return: New RGB values
    """
    h, s, v = rgb_to_hsv(color[0], color[1], color[2])
    v = min(max(v * brightness_factor, 0), 1)
    return hsv_to_rgb(h, s, v)


def generate_gradient(start_color, end_color, steps):
    start_hsv = rgb_to_hsv(start_color[0], start_color[1], start_color[2])
    end_hsv = rgb_to_hsv(end_color[0], end_color[1], end_color[2])

    gradient = []
    for i in range(steps):
        factor = i / (steps - 1)
        h = start_hsv[0] + (end_hsv[0] - start_hsv[0]) * factor
        s = start_hsv[1] + (end_hsv[1] - start_hsv[1]) * factor
        v = start_hsv[2] + (end_hsv[2] - start_hsv[2]) * factor
        gradient.append(hsv_to_rgb(h, s, v))

    return gradient


def random_col():
    return [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]


def linear_gradient(colors, normalizedZero2One):
    if normalizedZero2One < 0:
        normalizedZero2One = 0
    percent = (len(colors) - 1) * normalizedZero2One % 1
    index = min(int((len(colors) - 1) * normalizedZero2One), len(colors) - 1)
    return [(int(colors[index][i] + percent * (colors[index + 1][i] - colors[index][i]))) for i in range(3)]


def normalize(value, minValue, maxValue, doesCap=False):
    output = (value - minValue) / (maxValue - minValue)
    if doesCap:
        if output > 1:
            output = 1
        if output < 0:
            output = 0
    return output


def clip(minVal, maxVal, val):
    return min(maxVal, max(minVal, val))


def point_to_line(point, two_points_of_line):
    point_x, point_y = point
    x1, y1 = two_points_of_line[0]
    x2, y2 = two_points_of_line[1]
    dx = x2 - x1
    dy = y2 - y1
    parameterization = ((point_x - x1) * dx + (point_y - y1) * dy) / (dx ** 2 + dy ** 2)
    if parameterization < 0:
        closest_x, closest_y = x1, y1
    elif parameterization > 1:
        closest_x, closest_y = x2, y2
    else:
        closest_x = x1 + parameterization * dx
        closest_y = y1 + parameterization * dy

    d = math.sqrt((point_x - closest_x) ** 2 + (point_y - closest_y) ** 2)
    return d, [closest_x, closest_y]


def circumcircle(vertices):
    # Extract the vertices
    (x1, y1), (x2, y2), (x3, y3) = vertices

    # Calculate the coordinates of the circumcircle center
    D = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    center_x = ((x1 ** 2 + y1 ** 2) * (y2 - y3) + (x2 ** 2 + y2 ** 2) * (y3 - y1) + (x3 ** 2 + y3 ** 2) * (y1 - y2)) / D
    center_y = ((x1 ** 2 + y1 ** 2) * (x3 - x2) + (x2 ** 2 + y2 ** 2) * (x1 - x3) + (x3 ** 2 + y3 ** 2) * (x2 - x1)) / D

    # Calculate the radius of the circumcircle
    radius = math.sqrt((x1 - center_x) ** 2 + (y1 - center_y) ** 2)

    return (center_x, center_y), radius


def random_sign():
    return random.randint(0, 1) * 2 - 1


def tanh(x):
    return np.tanh(x)


def tanh_prime(x):
    return 1 - np.tanh(x) ** 2


def reLu(x):
    return (x > 0) * x


def reLu_prime(x):
    return x > 0


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def sigmoid_prime(x):
    return sigmoid(x) * (1 - sigmoid(x))


def mse(y_true, y_pred):
    return np.mean(np.power(y_true - y_pred, 2))


def mse_prime(y_true, y_pred):
    return 2 * (y_pred - y_true) / np.size(y_true)


def draw_arrow(screen, start, end, color, pygameModel, thickness=3, arrowhead_length=10, arrowhead_angle=25):
    # Draw the main line (shaft of the arrow)
    pygameModel.draw.line(screen, color, start, end, thickness)

    # Calculate the angle of the line
    angle = math.atan2(end[1] - start[1], end[0] - start[0])

    # Calculate the two points of the arrowhead
    angle1 = angle + math.radians(arrowhead_angle)
    angle2 = angle - math.radians(arrowhead_angle)

    arrowhead_point1 = (end[0] - arrowhead_length * math.cos(angle1), end[1] - arrowhead_length * math.sin(angle1))

    arrowhead_point2 = (end[0] - arrowhead_length * math.cos(angle2), end[1] - arrowhead_length * math.sin(angle2))

    # Draw the two lines for the arrowhead
    pygameModel.draw.line(screen, color, end, arrowhead_point1, thickness)
    pygameModel.draw.line(screen, color, end, arrowhead_point2, thickness)
