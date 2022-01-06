import numpy as np
from parameters import COLOR_SIM_THRESHOLD, CONF_THRESHOLD

def get_n_most_occuring(dict, n):
    ret_list = []
    sorted_dict = sorted(dict.items(), key=lambda x: -x[1])
    for key, value in sorted_dict:
        if len(ret_list) >= n:
            break
        #print(key, value)
        ret_list.append(key)
    return ret_list

def similar_colors(c_1, c_2):
    sum = abs(c_1[0] - c_2[0]) + abs(c_1[1] - c_2[1]) + abs(c_1[2] - c_2[2])
    return sum < COLOR_SIM_THRESHOLD

def detect_color(image_np, mask, default_color):
    color_cnt = np.sum(mask)
    color_sum = np.sum(image_np[mask], axis=0)
    if color_cnt == 0:
        color_sum = default_color
    else:
        color_sum = np.floor_divide(color_sum, color_cnt)
        color_sum = tuple(color_sum.tolist())[::-1]
    ret_color = tuple(t / 255 for t in color_sum)
    return ret_color

def detect_background_color(image_np, gray_np):
    return detect_color(image_np, gray_np == 0, (255, 255, 255))

def detect_font_color(image_np, gray_np):
    return detect_color(image_np, gray_np == 255, (0, 0, 0))
