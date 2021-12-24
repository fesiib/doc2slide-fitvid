import os

from uuid import uuid4 as random
import numpy as np
import cv2

from parser import get_image_np

CROPPED_IMAGES_PATH = "/home/fesiib/doc2slide/dev/Doc2Slide-DL/cropped_images"
CUR_URL = "http://192.168.1.147:7777"

def create_cropped_image(url, xp, yp, wp, hp):
    image_np = get_image_np(url)
    h, w, _ = image_np.shape

    sy = round(yp * h)
    fy = round((yp + hp) * h)
    sx = round(xp * w)
    fx = round((xp + wp) * w)

    image_np = image_np[sy:fy, sx:fx]

    image_name = str(random()).replace('-', '') + ".jpg"
    parent_path = CROPPED_IMAGES_PATH
    if os.path.exists(parent_path) is False:
        os.makedirs(parent_path)

    image_path = os.path.join(parent_path, image_name)
    print(CUR_URL + '/cropped_image/' + image_name, cv2.imwrite(image_path, image_np))
    return CUR_URL + '/cropped_image/' + image_name

def adapt_example_slide(slide_info, example_info):
    slide_id = slide_info["slide_id"]
    slide_width = slide_info["slide_width"]
    slide_height = slide_info["slide_height"]

    requests = []
    for element in example_info["elements"]:
        object_id =  str(random()).replace('-', '')
        url = element["design"]["url"]

        example_width = element["image_width"]
        example_height = element["image_height"]

        width = element["width"]
        height = element["height"]
        x = element["x"]
        y = element["y"]

        url = create_cropped_image(url, x / example_width, y / example_height, width / example_width, height / example_height)

        element_properties = {
            "pageObjectId": slide_id,
            "size": {
                "width": {
                    "magnitude": width, 
                    "unit": 'PT'
                },
                "height": {
                    "magnitude": height, 
                    "unit": 'PT'
                }
            },
            "transform": {
                "scaleX": slide_width / example_width,
                "scaleY": slide_height / example_height,
                "shearX": 0,
                "shearY": 0,
                "translateX": round(element["x"] / example_width * slide_width),
                "translateY": round(element["y"] / example_height * slide_height),
                "unit": 'PT'
            },
        }
        requests.append({
            "createImage": {
                "objectId": object_id,
                "elementProperties": element_properties,
                "url": url,
            }
        })

    return requests