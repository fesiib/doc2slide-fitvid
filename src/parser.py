import numpy as np
import cv2
import os

import urllib.request as request
import urllib.parse as parse

ROOT_URL = 'http://server.hyungyu.com:3001/frame_parsed/'
RATIO = 16 / 9

def crop_as_slide(image):
    h, w, _ = image.shape

    ch, cw = h // 2, w // 2

    half_h, half_w = round(w / RATIO) // 2, w // 2

    return image[(ch-half_h):(ch+half_h), (cw-half_w):(cw+half_w)]

def main():

    for parent in range(10000):
        last_slide = -1
        for slide in range(10000):
            parent_url = str(parent) + '/'
            slide_file = str(slide) + '.jpg'
            url = parse.urljoin(parse.urljoin(ROOT_URL, parent_url), slide_file)
            try:
                response = request.urlopen(url)
                image = np.asarray(bytearray(response.read()), dtype='uint8')
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)

                image = crop_as_slide(image)
                parent_path = os.path.join('/home/fesiib/doc2slide/dev/Doc2Slide-DL/results_doc2slide', str(parent))
                if os.path.exists(parent_path) is False:
                    os.makedirs(parent_path)
                
                image_path = os.path.join(parent_path, slide_file)
                last_slide = slide
                print(parent_path, slide_file, cv2.imwrite(image_path, image))
            except:
                break
            if last_slide < slide:
                break
                
        if last_slide == -1:
            break

if __name__ == "__main__":
    main()