import numpy as np
from parameters import COLOR_SIM_THRESHOLD, CONF_THRESHOLD

def get_n_most_occuring(dict, n):
    ret_list = []
    sorted_dict = sorted(dict.items(), key=lambda x: -x[1])
    for key, value in sorted_dict:
        if len(ret_list) >= n:
            break
        print(key, value)
        ret_list.append(key)
    return ret_list

def similar_colors(c_1, c_2):
    sum = abs(c_1[0] - c_2[0]) + abs(c_1[1] - c_2[1]) + abs(c_1[2] - c_2[2])
    return sum < COLOR_SIM_THRESHOLD

def detect_background_color(image_np, bbs):
    n, m, _ = image_np.shape
    colors = {}
    for y in range(n):
        for x in range(m):
            color = tuple(image_np[y][x].tolist())
            if color not in colors:
                colors[color] = 0
            colors[color] += 1
    most_occuring = get_n_most_occuring(colors, 2)
    ret_color = (255, 255, 255)
    if len(most_occuring) > 0:
        ret_color = most_occuring[0]
    ret_color = tuple(t / 255 for t in ret_color)
    return ret_color

def detect_font_color(image_np, data, background_color):
    text = None
    left = None
    top = None
    height = None
    width = None
    for i in range(len(data["text"])):
        conf = int(data["conf"][i])
        if (conf < CONF_THRESHOLD):
            continue
        text = data["text"][i]
        left = data["left"][i]
        top = data["top"][i]
        height = data["height"][i]
        width = data["width"][i]
        break
    if text is None:
        return (0, 0, 0)
    print(text, left, top, width, height)
    colors = {}
    for y in range(top, top + height):
        for x in range(left, left + width):
            color = tuple(image_np[y][x].tolist())
            if color not in colors:
                colors[color] = 0
            colors[color] += 1
    most_occuring = get_n_most_occuring(colors, 5)
    ret_color = (0, 0, 0)
    for color in most_occuring:
        if similar_colors(color, background_color) is True:
            continue
        ret_color = color
        break
    ret_color = tuple(t / 255 for t in ret_color)
    return ret_color
