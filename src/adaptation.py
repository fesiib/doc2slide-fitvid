import os

from uuid import uuid4 as random
import numpy as np
import cv2

from parser import get_image_np

from parameters import CROPPED_IMAGES_PATH, CUR_URL

def create_cropped_image(image_np, xp, yp, wp, hp):
    h, w = 0, 0
    if len(image_np.shape) == 3:
        h, w, _ = image_np.shape
    else:
        h, w = image_np.shape    

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
    cv2.imwrite(image_path, image_np)
    #print(CUR_URL + '/cropped_image/' + image_name)
    return CUR_URL + '/cropped_image/' + image_name

def get_optional_color(color_tup):
    return {
        "rgbColor": {
            "red": color_tup[0],
            "green": color_tup[1],
            "blue": color_tup[2]
        },
}   

def get_text_style(font_attr):
    return {
        # "backgroundColor": {
            
        # },
        "foregroundColor": {
            "opaqueColor": get_optional_color(font_attr["font_color"])
        },
        "bold": font_attr["bold"],
        "italic": font_attr["italic"],
        "fontFamily": font_attr["font_family"],
        "fontSize": {
            "magnitude": font_attr["pointsize"], 
            "unit": 'PT'
        },
        # "link": {
        #     object (Link)
        # },
        #"baselineOffset": enum (BaselineOffset),
        "smallCaps": font_attr["smallcaps"],
        #"strikethrough": font_attributes["smallcaps"],
        "underline": font_attr["underlined"],
        # "weightedFontFamily": {
        #     object (WeightedFontFamily)
        # }
    }

def get_paragraph_style(paragraph_attr):
    return {
        "lineSpacing": 1.15,
        "alignment": paragraph_attr["justification"],
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

        width = element["width"] / example_width
        height = element["height"] / example_height
        left = element["left"] / example_width
        top = element["top"] / example_height

        element_properties = {
            "pageObjectId": slide_id,
            "size": {
                "width": {
                    "magnitude": int(width * slide_width), 
                    "unit": 'PT'
                },
                "height": {
                    "magnitude": int(height * slide_height), 
                    "unit": 'PT'
                }
            },
            "transform": {
                "scaleX": 1,
                "scaleY": 1,
                "shearX": 0,
                "shearY": 0,
                "translateX": round(left * slide_width),
                "translateY": round(top * slide_height),
                "unit": 'PT'
            },
        }

        type = element["type"]

        if type == "figure":
            url = element["design"]["url"]
            image_np = get_image_np(url)
            image_np = create_cropped_image(image_np, left, top, width, height)
            image_name = str(element["slide_deck_id"]) + '_' + str(element["slide_id"]) + '_' + str(element["object_id"])
            url = save_cropped_image(image_np, image_name)
            requests.append({
                "createImage": {
                    "objectId": object_id,
                    "elementProperties": element_properties,
                    "url": url,
                }
            })
        else:
            element_properties["size"]["width"]["magnitude"] += 40
            element_properties["size"]["height"]["magnitude"] += 40
            element_properties["transform"]["translateX"] -= 20
            element_properties["transform"]["translateY"] -= 20
            requests.append({
                "createShape": {
                    "objectId": object_id,
                    "elementProperties": element_properties,
                    "shapeType": "TEXT_BOX", 
                }
            })
            paragraphs = element["design"]["paragraphs"]
            font_attributes = element["design"]["font_attributes"]
            paragraph_attributes = element["design"]["paragraph_attributes"]
            insertionIndex = 0
            for paragraph, font_attr, paragraph_attr in zip(paragraphs, font_attributes, paragraph_attributes):
                paragraph += '\n'
                print(insertionIndex, paragraph, font_attr, paragraph_attr)
                requests.append({
                    "insertText": {
                        "objectId": object_id,
                        "text": paragraph,
                        "insertionIndex": insertionIndex
                    }
                })
                if len(paragraph) > 1:
                    requests.append({
                        "updateTextStyle": {
                            "objectId": object_id,
                            "style": get_text_style(font_attr),
                            "textRange": {
                                "startIndex": insertionIndex,
                                "endIndex": insertionIndex + len(paragraph),
                                "type": "FIXED_RANGE"
                            },
                            "fields": "*",
                        }
                    })
                    # requests.append({
                    #     "updateParagraphStyle": {
                    #         "objectId": object_id,
                    #         "style": get_paragraph_style(paragraph_attr),
                    #         "textRange": {
                    #             "startIndex": insertionIndex,
                    #             "endIndex": insertionIndex + len(paragraph),
                    #             "type": "FIXED_RANGE"
                    #         },
                    #         "fields": "*",
                    #     }
                    # })
                insertionIndex += len(paragraph)
    return requests