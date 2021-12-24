from uuid import uuid4 as random
import numpy as np

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

        width = element["width"] / example_width * slide_width
        height = element["height"] / example_height * slide_height
        x = element["x"] / example_width * slide_width
        y = element["y"] / example_height * slide_height



        element_properties = {
            "pageObjectId": slide_id,
            "size": {
                "width": {
                    "magnitude": round(width), 
                    "unit": 'PT'
                },
                "height": {
                    "magnitude": round(height), 
                    "unit": 'PT'
                }
            },
            "transform": {
                "scaleX": 1,
                "scaleY": 1,
                "shearX": 0,
                "shearY": 0,
                "translateX": round(x),
                "translateY": round(y),
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