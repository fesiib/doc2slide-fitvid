import pytesseract
import cv2
import numpy as np

from tesserocr import PyTessBaseAPI, OEM, PSM, get_languages, RIL, iterate_level
from PIL import Image

from fitvid.doc2slide_processor import LayoutDetection

from parser import get_image_np
from adaptation import create_cropped_image, save_cropped_image
from detect import detect_background_color, detect_font_color
from parameters import CONF_THRESHOLD, INTERSECTION_THRESHOLD, SLIDE_WIDTH, SLIDE_HEIGHT

# Models
layout_detector = LayoutDetection()

def preprocess_for_detection(image_np, data):
    gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    image_height, image_width = gray.shape
    gray_masked = gray.copy()
    for entry in data:
        left, top, width, height = entry["left"], entry["top"], entry["width"], entry["height"]
        gray_masked = cv2.rectangle(gray_masked, (left, top), (left+width, top+height), 255, -1)
    if (np.sum(gray_masked < 123) > image_height * image_width / 2):
        image_np = 255 - image_np
        gray = 255 - gray
    
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 13, 5)
    save_cropped_image(gray_masked, "a_gray_masked")
    save_cropped_image(gray, "a_gray")
    save_cropped_image(image_np, "a_thresh")
    return image_np, gray

def calc_intersection_ratio(field, box):
    inter = (
        max(field[0], box[0]), 
        max(field[1], box[1]),
        min(field[0] + field[2], box[0] + box[2]),
        min(field[1] + field[3], box[1] + box[3]),
    )
    # inter[0] = x1
    # inter[1] = y1
    # inter[2] = x2
    # inter[3] = y2
    if inter[0] >= inter[2] or inter[1] > inter[3]:
        return 0
    return (inter[2] - inter[0]) * (inter[3] - inter[1]) / (box[2] * box[3])

def convert_paragraph_info(paragraph_info):
    paragraph_attributes = {
        "justification": paragraph_info[0],
        "is_list_item": paragraph_info[1],
        "is_crown": paragraph_info[2],
        "first_line_indent": paragraph_info[3],
    }
    if (paragraph_info[0] == 'RIGHT'):
        paragraph_attributes["justification"] = 'END'
    elif (paragraph_info[0] == 'CENTER'):
        paragraph_attributes["justification"] = 'CENTER'
    else:
        paragraph_attributes["justification"] = 'START'
    return paragraph_attributes

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
def get_data(api, image_np):
    pil_image_np = Image.fromarray(image_np)
    api.SetImage(pil_image_np)
    api.Recognize()
    ri = api.GetIterator()
    level = RIL.PARA
    data = []

    for r in iterate_level(ri, level):
        paragraph = r.GetUTF8Text(level).strip()
        conf = r.Confidence(level)
        font_attr = r.WordFontAttributes()
        left, top, right, bottom = r.BoundingBox(level)
        paragraph_info = r.ParagraphInfo()
        width = max(right - left, 0)
        height = max(bottom - top, 0)
        if font_attr is not None:
            font_attr["font_name"] = font_attr["font_name"].replace('_', ' ')

        if paragraph_info is not None:
            paragraph_info = convert_paragraph_info(paragraph_info)
        if paragraph:
            data.append({
                "text": paragraph,
                "conf": conf,
                "font_attr": font_attr,
                "paragraph_attr": paragraph_info,
                "left": left,
                "top": top,
                "width": width,
                "height": height
            })
    return data

def process_text(data):
    text_properties = {
        "paragraphs": [],
        "font_attributes": [],
        "paragraph_attributes": [],
        "bullet": False,
    }
    for entry in data:
        text = entry["text"]
        conf = int(entry["conf"])
        if (conf < CONF_THRESHOLD):
            continue
        print(text, conf, "x=", entry["left"], "y=", entry["top"], "w=", entry["width"], "h=", entry["height"])
        font_attr = entry["font_attr"]
        paragraph_attr = entry["paragraph_attr"]
        text_properties["paragraphs"].append(text)
        text_properties["font_attributes"].append(font_attr)
        text_properties["paragraph_attributes"].append(paragraph_attr)
    return text_properties

def process_example(url, example_deck_id, example_id):
    image_np = get_image_np(url)
    image_np = cv2.resize(image_np, (SLIDE_WIDTH, SLIDE_HEIGHT), interpolation=cv2.INTER_LINEAR)

    with PyTessBaseAPI(path='./tessdata', oem=OEM.TESSERACT_ONLY) as api:
        data = get_data(api, image_np)
        proc_image_np, gray_np = preprocess_for_detection(image_np.copy(), data)
        bbs = layout_detector.detect(proc_image_np, example_deck_id, example_id)
        backgorund_color = detect_background_color(image_np, gray_np)
        info = {
            "page": {
                "background_color": backgorund_color,
                "has_slide_number": False,
            },
            "elements": [],
        }
        for bb in bbs:
            element = dict(bb)
            example_width = element["image_width"]
            example_height = element["image_height"]
            w = element["width"] / example_width
            h = element["height"] / example_height
            x = element["x"] / example_width
            y = element["y"] / example_height

            # 'title',
            # 'header',
            # 'text',
            # 'footer',
            # 'figure',
            cropped_image_np = create_cropped_image(image_np, x, y, w, h)
            cropped_gray_np = create_cropped_image(gray_np, x, y, w, h)
            #data = pytesseract.image_to_data(cropped_image_np, output_type=pytesseract.Output.DICT)
            
            cur_data = []
            
            for entry in data:
                left, top, width, height = entry["left"], entry["top"], entry["width"], entry["height"]
                text = entry["text"]
                if (text == ''):
                    continue
                left /= SLIDE_WIDTH
                width /= SLIDE_WIDTH
                top /= SLIDE_HEIGHT
                height /= SLIDE_HEIGHT
                if calc_intersection_ratio((x, y, w, h), (left, top, width, height)) < INTERSECTION_THRESHOLD:
                    continue
                entry["font_attr"]["font_color"] = detect_font_color(cropped_image_np, cropped_gray_np)
                cur_data.append(entry)

            if len(cur_data) == 0:
                element["type"] = 'figure'

            if element["type"] == 'figure':
                element["design"] = {
                    'url': url,
                }
            else:
                element["design"] = process_text(cur_data)
            info["elements"].append(element)
    return info