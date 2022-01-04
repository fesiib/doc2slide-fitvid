import os
import sys

sys.path.insert(1, os.path.abspath('./src/fitvid/'))
print(os.path.abspath('.'))

from google.protobuf.text_format import Error
from six import print_
import tensorflow as tf

import time
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.utils import config_util
from object_detection.builders import model_builder

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import warnings
import cv2
import csv


from parameters import PATH_TO_CFG, PATH_TO_CKPT, PATH_TO_LABELS, CLASS_LABELS

class LayoutDetection(object):
    def __init__(self):
        self.min_score_thresh = 0.5
        
        configs = config_util.get_configs_from_pipeline_file(PATH_TO_CFG)
        model_config = configs['model']
        
        self.detection_model = model_builder.build(model_config=model_config, is_training=False)
        # Restore checkpoint
        ckpt = tf.compat.v2.train.Checkpoint(model=self.detection_model )
        ckpt.restore(os.path.join(PATH_TO_CKPT, 'ckpt-141')).expect_partial()

        self.category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS,use_display_name=True)
        return
    
    def detect(self, image_np, slide_deck_id, slide_id):
        image_np = self._preprocess(image_np)

        input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
        detections = detect_fn(self.detection_model, input_tensor)
        num_detections = int(detections.pop('num_detections'))
        detections = { 
            key : value[0, :num_detections].numpy() for key, value in detections.items()
        }
        detections['num_detections'] = num_detections
        
        # Filter
        scores = detections['detection_scores']
        detections['detection_boxes'] = detections['detection_boxes'][scores >= self.min_score_thresh]
        detections['detection_classes'] = detections['detection_classes'][scores >= self.min_score_thresh]
        detections['detection_scores'] = detections['detection_scores'][scores >= self.min_score_thresh]
        
        cur_entries = self._get_entries(detections, image_np, slide_id, slide_deck_id)
        #print(cur_entries)
        return cur_entries

    def _preprocess(self, image_np):
        return image_np

    def _get_entries(self, detections, image_np, slide_id, slide_deck_id):
        entries = []
        height, width = image_np.shape[:2]

        bboxes = detections['detection_boxes']    
        scores = detections['detection_scores']
        classes_pred = detections['detection_classes']

        for i, box in enumerate(bboxes):
            ymin, xmin, ymax, xmax = box
            entry = {
                "slide_deck_id": slide_deck_id,
                "slide_id": slide_id,
                "image_height": height * 0.75,
                "image_width": width * 0.75,
                "type": CLASS_LABELS[classes_pred[i]],
                "confidence": round(scores[i] * 100),
                'x': int(xmin * width * 0.75),
                'y': int(ymin * height * 0.75),
                'width': int((xmax-xmin) * width * 0.75),
                'height': int((ymax-ymin) * height * 0.75),
            }
            entries.append(entry)
        return entries

@tf.function
def detect_fn(detection_model, image):
    """Detect objects in image."""
    image, shapes = detection_model.preprocess(image)
    prediction_dict = detection_model.predict(image, shapes)
    detections = detection_model.postprocess(prediction_dict, shapes)

    return detections

def load_image_into_numpy_array(path):
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    return np.array(img)


def print_boxes(detections, image_np):
    boxes = detections['detection_boxes']
    height, width = image_np.shape[:2]

    box = np.squeeze(boxes)
    scores = detections['detection_scores']

    classes_pred = detections['detection_classes']

    min_score_thresh = 0.7

    bboxes = boxes[scores > min_score_thresh]
    scores_new = scores[scores > min_score_thresh]
    classes_pred_new = classes_pred[scores > min_score_thresh]

    print('The boudning box details are organized as follow: \n')
    print('[ymin   xmin   ymax   xmax   confidence    class-label] \n')
    i = 0 
    for box in bboxes:
        ymin, xmin, ymax, xmax = box
        final_box = [int(ymin * height), int(xmin * width), int(ymax * height), int(xmax *width) , round(scores_new[i] * 100) , classes_pred_new[i] + 1 ]
        i += 1
        print(final_box)

def get_data_entries(detections, image_np, slide_id, slide_deck_id):
    entries = []
    height, width = image_np.shape[:2]

    boxes = detections['detection_boxes']    
    scores = detections['detection_scores']
    classes_pred = detections['detection_classes']

    min_score_thresh = 0.7

    bboxes = boxes[scores >= min_score_thresh]
    scores_new = scores[scores >= min_score_thresh]
    classes_pred_new = classes_pred[scores >= min_score_thresh]
    for i, box in enumerate(bboxes):
        ymin, xmin, ymax, xmax = box
        entry = {
            "Slide Deck Id": slide_deck_id,
            "Slide Id": slide_id,
            "Image Height": height,
            "Image Width": width,
            "Type": CLASS_LABELS[classes_pred_new[i]],
            'X': int(xmin * width),
            'Y': int(ymin * height),
            'BB Width': int((xmax-xmin) * width),
            'BB Height': int((ymax-ymin) * height),
        }
        entries.append(entry)
    return entries

def write_image(root_path, image_name, image):
    if (os.path.exists(root_path) is False):
        os.makedirs(root_path, 0o777, exist_ok=True)
    path = os.path.join(root_path, image_name)
    #print(path)
    cv2.imwrite(path, image)

def main(args):

    print('Loading model... ', args)

    # Load pipeline config and build a detection model
    configs = config_util.get_configs_from_pipeline_file(PATH_TO_CFG)
    model_config = configs['model']
    detection_model = model_builder.build(model_config=model_config, is_training=False)

    # Restore checkpoint
    ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
    ckpt.restore(os.path.join(PATH_TO_CKPT, 'ckpt-141')).expect_partial()

    category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS,use_display_name=True)
    
    dataset_root_path = "/home/fesiib/doc2slide/dev/Doc2Slide-DL/results_doc2slide"

    def process_presentation(image_parent_path, image_folder):
        all_dataset = []
        result_path = os.path.join(os.getcwd(), 'results')
        for _, _, files in os.walk(image_parent_path):
            for image_name in files:
                if image_name.endswith('.jpg') is False:
                    continue
                image_path = os.path.join(image_parent_path, image_name)
                image_np = load_image_into_numpy_array(image_path)
                print(image_path)
                input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
                detections = detect_fn(detection_model, input_tensor)
                num_detections = int(detections.pop('num_detections'))
                detections = { 
                    key : value[0, :num_detections].numpy() for key, value in detections.items()
                }
                detections['num_detections'] = num_detections
                
                # Filter
                min_score_thresh = 0.7
                scores = detections['detection_scores']
                detections['detection_boxes'] = detections['detection_boxes'][scores >= min_score_thresh]
                detections['detection_classes'] = detections['detection_classes'][scores >= min_score_thresh]
                detections['detection_scores'] = detections['detection_scores'][scores >= min_score_thresh]
                
                cur_entries = get_data_entries(detections, image_np, image_name.split('.')[0], 'presentation_' + image_folder)
                all_dataset.extend(cur_entries)

                detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

                label_id_offset = 1
                image_np_with_detections = cv2.copyMakeBorder(image_np, 10, 10, 0, 0, cv2.BORDER_CONSTANT, value=[255,255,255])
                viz_utils.visualize_boxes_and_labels_on_image_array(image_np_with_detections, detections['detection_boxes'],
                                                            detections['detection_classes']+label_id_offset,
                                                                        detections['detection_scores'],
                                                                                    category_index,
                                                                                                use_normalized_coordinates=True,
                                                                                                            max_boxes_to_draw=200,
                                                                                                                        min_score_thresh=.30,
                                                                                                                                    agnostic_mode=False)
                write_image(os.path.join(result_path, image_folder), image_name, image_np_with_detections)
            if len(all_dataset) > 0:
                csv_entries = []
                csv_entries.append(all_dataset[0].keys())
                for entry in all_dataset:
                    csv_entries.append(entry.values())
                csv_file = 'slide_deck_dataset_' + presentation + '.csv'
                csv_file_path = os.path.join(result_path, csv_file)
                with open(csv_file_path, 'w') as file:
                    writer = csv.writer(file)
                    writer.writerows(csv_entries)
            return
    for f, dirs, _ in os.walk(dataset_root_path):
        for presentation in dirs:
            presentation_root_path = os.path.join(dataset_root_path, presentation)
            process_presentation(presentation_root_path, presentation)
        break
        
if __name__ == "__main__":
    main(sys.argv[1:])

