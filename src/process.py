import pytesseract
from tesserocr import PyTessBaseAPI, OEM, PSM, get_languages
import cv2
from PIL import Image

from fitvid.doc2slide_processor import LayoutDetection

from parser import get_image_np
from adaptation import create_cropped_image

CONF_THRESHOLD = 50

# Models
layout_detector = LayoutDetection()

def preprocess_for_detection(image_np):
    gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

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
def process_font(api, image_np):
    pil_image_np = Image.fromarray(image_np)
    api.SetImage(pil_image_np)
    api.Recognize()
    iterator = api.GetIterator()
    return iterator.WordFontAttributes()

def process_text(data, font_attributes):
    text_properties = {
        "font_size": font_attributes["pointsize"],
        "font_style": font_attributes["font_name"],
        "font_color": (0, 0, 0),
        "paragraphs": [],
        "font_attributes": font_attributes,
        "bullet": False,
    }
    cur_line_num = 1
    paragraph = ""
    for i in range(len(data["text"])):
        text = data["text"][i]
        conf = int(data["conf"][i])
        if (conf < CONF_THRESHOLD):
            continue
        line_num = data["line_num"][i]
        
        if line_num == cur_line_num and i > 0:
            paragraph += ' '

        while (line_num > cur_line_num):
            paragraph += '\n'
            cur_line_num += 1
        paragraph += text
        
        left = data["left"][i]
        top = data["top"][i]
        height = data["height"][i]
        width = data["width"][i]
        #print(line_num, text, conf, "x=", left, "y=", top, "w=", width, "h=", height)
    
    text_properties["paragraphs"].append(paragraph)
    return text_properties

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
    with PyTessBaseAPI(path='./tessdata', oem=OEM.TESSERACT_ONLY) as api:
        for bb in bbs:
            element = dict(bb)

            element_type = element["type"]

            example_width = element["image_width"]
            example_height = element["image_height"]
            width = element["width"]
            
            height = element["height"]
            x = element["x"]
            y = element["y"]

            # 'title',
            # 'header',
            # 'text',
            # 'footer',
            # 'figure',
            cropped_image_np = create_cropped_image(image_np, x / example_width, y / example_height, width / example_width, height / example_height)
            #cropped_image_np = preprocess_for_detection(cropped_image_np)
            data = pytesseract.image_to_data(cropped_image_np, output_type=pytesseract.Output.DICT)
            font_attributes = process_font(api, cropped_image_np)

            if element_type == 'figure':
                element["design"] = {
                    'url': url,
                }
            else:
                element["design"] = process_text(data, font_attributes)
            info["elements"].append(element)
    return info