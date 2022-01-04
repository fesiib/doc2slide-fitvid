COLOR_SIM_THRESHOLD = 20

CONF_THRESHOLD = 50

CROPPED_IMAGES_PATH = "/home/bekzat/server/adaptation/cropped_images"
CUR_URL = "http://server.hyungyu.com:7777"

# FITVID MODEL
PATH_TO_MODEL_DIR = "/home/bekzat/models/fitvid"
PATH_TO_CFG = PATH_TO_MODEL_DIR + "/centernet_hourglass104_512x512_coco17_tpu-8_document_for_sharing_finetuning.config"
PATH_TO_CKPT = PATH_TO_MODEL_DIR + "/"  
PATH_TO_LABELS = "/home/bekzat/server/adaptation/src/fitvid/document_label_map.pbtxt"

ORIGINAL_CLASS_LABELS = [
    'title',
    'header',
    'text box',
    'footer',
    'picture',
    'instructor',
    'diagram',
    'table',
    'figure',
    'handwriting',
    'chart',
    'schematic diagram',
]

CLASS_LABELS = [
    'title',
    'header',
    'text',
    'footer',
    'figure',
    'figure',
    'figure',
    'figure',
    'figure',
    'figure',
    'figure',
    'figure',
]