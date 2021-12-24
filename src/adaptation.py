from uuid import uuid4 as random
import numpy as np

def px_to_pt(in_px):
    return in_px * 0.75

def adapt_example_slide(slide_info, example_info):
    requests = []
    for element in example_info["elements"]:
        object_id =  str(random()).replace('-', '')
        url = element["design"]["url"]
        element_properties = {
            "pageObjectId": slide_info["slide_id"],
            "size": {
                "width": {
                    "magnitude": px_to_pt(element["width"]), 
                    "unit": 'PT'
                },
                "height": {
                    "magnitude": px_to_pt(element["height"]), 
                    "unit": 'PT'
                }
            },
            "transform": {
                "scaleX": 1,
                "scaleY": 1,
                "shearX": 0,
                "shearY": 0,
                "translateX": px_to_pt(element["x"]),
                "translateY": px_to_pt(element["y"]),
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