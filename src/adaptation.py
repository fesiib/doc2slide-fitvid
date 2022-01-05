import os

from uuid import uuid4 as random
import numpy as np
import cv2

from parser import get_image_np

from parameters import CROPPED_IMAGES_PATH, CUR_URL

def create_cropped_image(image_np, xp, yp, wp, hp):
    h, w, _ = image_np.shape

    sy = round(yp * h)
    fy = round((yp + hp) * h)
    sx = round(xp * w)
    fx = round((xp + wp) * w)

    return image_np[sy:fy, sx:fx]

def save_cropped_image(image_np, image_name = None):
    if image_name is None:
        image_name = str(random()).replace('-', '')
    image_name += ".jpg"
    parent_path = CROPPED_IMAGES_PATH
    if os.path.exists(parent_path) is False:
        os.makedirs(parent_path)
    image_path = os.path.join(parent_path, image_name)
    if os.path.exists(image_path):
        os.remove(image_path)
    print(CUR_URL + '/cropped_image/' + image_name, cv2.imwrite(image_path, image_np))
    return CUR_URL + '/cropped_image/' + image_name

def get_optional_color(color_tup):
    return {
        "rgbColor": {
            "red": color_tup[0],
            "green": color_tup[1],
            "blue": color_tup[2]
        },
}   

def get_text_style(design):
    font_attributes = design["font_attributes"]
    return {
        # "backgroundColor": {
            
        # },
        "foregroundColor": {
            "opaqueColor": get_optional_color(design["font_color"])
        },
        "bold": font_attributes["bold"],
        "italic": font_attributes["italic"],
        "fontFamily": font_attributes["font_name"],
        "fontSize": {
            "magnitude": font_attributes["pointsize"], 
            "unit": 'PT'
        },
        # "link": {
        #     object (Link)
        # },
        #"baselineOffset": enum (BaselineOffset),
        "smallCaps": font_attributes["smallcaps"],
        #"strikethrough": font_attributes["smallcaps"],
        "underline": font_attributes["underlined"],
        # "weightedFontFamily": {
        #     object (WeightedFontFamily)
        # }
    }

def get_paragraph_style(design):
    return {
        "lineSpacing": 1,
        "alignment": "START",
        "indentStart": {
            "magnitude": 0, 
            "unit": 'PT'
        },
        "indentEnd": {
            "magnitude": 0, 
            "unit": 'PT'
        },
        "spaceAbove": {
            "magnitude": 0, 
            "unit": 'PT'
        },
        "spaceBelow": {
            "magnitude": 0, 
            "unit": 'PT'
        },
        "indentFirstLine": {
            "magnitude": 0, 
            "unit": 'PT'
        },
        "direction": "LEFT_TO_RIGHT",
        "spacingMode": "SPACING_MODE_UNSPECIFIED",
    }
def adapt_example_slide(slide_info, example_info):
    slide_id = slide_info["slide_id"]
    slide_width = slide_info["slide_width"]
    slide_height = slide_info["slide_height"]

    requests = []


    # Page Properties
    page_properties = {
        "pageBackgroundFill": {
            "solidFill": {
                "color": get_optional_color(example_info["page"]["background_color"]),
            }
        }
    }
    requests.append({
        "updatePageProperties": {
            "objectId": slide_id,
            "pageProperties": page_properties,
            "fields": "pageBackgroundFill.solidFill.color"
        }
    })

    # Page Elements
    for element in example_info["elements"]:
        object_id =  str(random()).replace('-', '')
        example_width = element["image_width"]
        example_height = element["image_height"]

        width = element["width"]
        height = element["height"]
        x = element["x"]
        y = element["y"]

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

        type = element["type"]

        if type == "figure":
            url = element["design"]["url"]
            image_np = get_image_np(url)
            image_np = create_cropped_image(image_np, x / example_width, y / example_height, width / example_width, height / example_height)
            url = save_cropped_image(image_np)
            requests.append({
                "createImage": {
                    "objectId": object_id,
                    "elementProperties": element_properties,
                    "url": url,
                }
            })
        else:
            requests.append({
                "createShape": {
                    "objectId": object_id,
                    "elementProperties": element_properties,
                    "shapeType": "TEXT_BOX", 
                }
            })
            paragraphs = element["design"]["paragraphs"]
            insertionIndex = 0
            for paragraph in paragraphs:
                requests.append({
                    "insertText": {
                        "objectId": object_id,
                        "text": paragraph,
                        "insertionIndex": insertionIndex
                    }
                })
                if len(paragraph) > 0:
                    requests.append({
                        "updateTextStyle": {
                            "objectId": object_id,
                            "style": get_text_style(element["design"]),
                            "textRange": {
                                "startIndex": insertionIndex,
                                "type": "FROM_START_INDEX"
                            },
                            "fields": "*",
                        }
                    })
                # requests.append({
                #     "updateParagraphStyle": {
                #         "objectId": object_id,
                #         "style": get_paragraph_style(element["design"]),
                #         "textRange": {
                #             "startIndex": insertionIndex,
                #             "type": "FROM_START_INDEX"
                #         },
                #         "fields": "*",
                #     }
                # })
                insertionIndex += len(paragraph)
    return requests