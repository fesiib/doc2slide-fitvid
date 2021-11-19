import os
import tensorflow as tf

import time
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.utils import config_util
from .builders import model_builder

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import warnings
import cv2

PATH_TO_MODEL_DIR = "/home/jykim/models/research/object_detection/models/models_for_centernet_finetuning"
PATH_TO_CFG = PATH_TO_MODEL_DIR + "/centernet_hourglass104_512x512_coco17_tpu-8_document_for_sharing_finetuning.config"
PATH_TO_CKPT = PATH_TO_MODEL_DIR + "/"  
PATH_TO_LABELS = "/home/jykim/models/research/object_detection/document_label_map.pbtxt"

print('Loading model... ', end='')
start_time = time.time()

# Load pipeline config and build a detection model
configs = config_util.get_configs_from_pipeline_file(PATH_TO_CFG)
model_config = configs['model']
detection_model = model_builder.build(model_config=model_config, is_training=False)

# Restore checkpoint
ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
ckpt.restore(os.path.join(PATH_TO_CKPT, 'ckpt-136')).expect_partial()



@tf.function
def detect_fn(image):
    """Detect objects in image."""
    image, shapes = detection_model.preprocess(image)
    prediction_dict = detection_model.predict(image, shapes)
    detections = detection_model.postprocess(prediction_dict, shapes)

    return detections

def load_image_into_numpy_array(path):
    return np.array(Image.open(path))
              
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS,use_display_name=True)
#image_path = "/hdd/jykim_archive/huge_OD/temp_move/ver123/video5_2_9_shot5.jpg"
image_path = "/home/jykim/models/research/object_detection/ppt_prof_kang_4_1/0008.jpg"
image_np = load_image_into_numpy_array(image_path)

# display the original image
ori_image = cv2.imread(image_path)
img_height, img_width, _ = ori_image.shape
cv2.imshow("ori_image",ori_image)
cv2.waitKey(0)
cv2.destroyAllWindows()


# Things to try:
# Flip horizontally
#image_np = np.fliplr(image_np).copy()
# Convert image to grayscale
#image_np = np.tile(np.mean(image_np, 2, keepdims=True), (1, 1, 3)).astype(np.uint8)
input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
detections = detect_fn(input_tensor)

num_detections = int(detections.pop('num_detections'))
detections = {key: value[0, :num_detections].numpy()

        
        
for key, value in detections.items()}

#print(num_detections)

detections['num_detections'] = num_detections


boxes = detections['detection_boxes']
width, height = image_np.shape[:2]

box = np.squeeze(boxes)
scores = detections['detection_scores']

classes_pred = detections['detection_classes']

min_score_thresh = 0.30

bboxes = boxes[scores > min_score_thresh]
scores_new = scores[scores > min_score_thresh]
classes_pred_new = classes_pred[scores > min_score_thresh]

width, height = image_np.shape[:2]
final_box = []
print('\n')

print('The boudning box details are organized as follow: \n')
print('[ymin   xmin   ymax   xmax   confidence    class-label] \n')
i = 0 
for box in bboxes:
    ymin, xmin, ymax, xmax = box
    final_box = [int(ymin * width), int(xmin * height), int(ymax * width), int(xmax *height) , round(scores_new[i] * 100) , classes_pred_new[i] + 1 ]
    i += 1
    print(final_box)

# for i in range(len(boxes)):
        
#     ymin = int((box[i,0]*height))
#     xmin = int((box[i,1]*width))
#     ymax = int((box[i,2]*height))
#     xmax = int((box[i,3]*width))

#     print(xmin, xmax, ymin , ymax)

# Result = np.array(img_np[ymin:ymax,xmin:xmax])


#print("Detections:", detections)
            # detection_classes should be ints.
detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

# print("Detections_2:", detections['detection_boxes'])

label_id_offset = 1
image_np_with_detections = image_np.copy()

viz_utils.visualize_boxes_and_labels_on_image_array(image_np_with_detections, detections['detection_boxes'],
                                            detections['detection_classes']+label_id_offset,
                                                        detections['detection_scores'],
                                                                    category_index,
                                                                                use_normalized_coordinates=True,
                                                                                            max_boxes_to_draw=200,
                                                                                                        min_score_thresh=.30,
                                                                                                                    agnostic_mode=False)

#plt.figure()
#plt.imshow(image_np_with_detections)
print('Done')
#plt.show()

#image_np_with_detections.show()
cv2.imshow("image",image_np_with_detections)
cv2.waitKey(0)
cv2.destroyAllWindows()

#@tf.function
#def detect_fn(image):
#        """Detect objects in image."""

#            image, shapes = detection_model.preprocess(image)

