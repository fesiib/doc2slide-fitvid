from fitvid.doc2slide_processor import LayoutDetection

from parser import get_image_np

# Models
layout_detector = LayoutDetection()

'''
background: {
    color: rgba
}

figure: {
    url: ????
}

text: {
    font_size: ???
    font_style: ???
    font_color: rgba
    content: "????"
}

'''

def process_example(url, example_deck_id, example_id):
    image_np = get_image_np(url)
    bbs = layout_detector.detect(image_np, example_deck_id, example_id)
    info = {
        "page": {
            "background": (255, 255, 255),
            "has_slide_number": False,
        },
        "elements": [],
    }
    for bb in bbs:
        element = dict(bb)
        element['design'] = {
            'url': url,
        }
        info["elements"].append(element)
    return info