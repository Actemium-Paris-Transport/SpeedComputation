

from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
import numpy as np
import cv2
from PIL import Image
from tensorflow.python.saved_model import tag_constants
from core.functions import *
import core.utils as utils
from absl.flags import FLAGS
from absl import flags, logging
import tensorflow as tf
import os
from pydantic import BaseModel
import imageio.v2 as imageio
from imageio.v2 import imread
import base64
from io import BytesIO




from email.mime import base
import fastapi as FastAPI
from pydantic import BaseModel
import uvicorn 
from fastapi import Depends, FastAPI, HTTPException, Request, Response, Form,  File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware






# comment out below line to enable tensorflow outputs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)




app = FastAPI()


origins = ["http://localhost:7500",
           "http://apt.he.fr:80",
           "http://apt.he.fr:7500",
           "http://localhost:7500/",
           "http://localhost:4040/"]


methods = ["POST"]

headers = ["Accept, Accept-Language, Content-Language , Content-Type"]


app.add_middleware(
    CORSMiddleware, 
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = methods,
    allow_headers = headers    
)


class number_plate_detection(BaseModel):
    image_base64_1: bytes   
    image_base64_2 : bytes

@app.post('/inference_yolo', status_code=200)
async def test(param: number_plate_detection):
    image_encoded_64_1 = param.image_base64_1
    image_encoded_64_2 = param.image_base64_2
    

    # adjust the params
    weights = "./checkpoints/custom-416"
    size = 416
    output = "./detections/"
    iou = .45
    score = .50
    config = ConfigProto()
    config.gpu_options.allow_growth = True
    session = InteractiveSession(config=config)

    input_size = size

    image_encoded_64 = [image_encoded_64_1,image_encoded_64_2 ]
    saved_model_loaded = tf.saved_model.load(
        weights, tags=[tag_constants.SERVING])

    registration_plate = []
    # loop through images in list and run Yolov4 model on each
    for i in range(2) :
        
        image_encoded = image_encoded_64[i].decode('utf-8') #decode each image
        img = imread(BytesIO(base64.b64decode(image_encoded))) #read image in BRG
        try : 
            original_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #convert images from BRG to RGB
            print("great")
        except : # ("converting done !")
            print(  "prob convert from BGR to RGB")
        
        
        image_data = cv2.resize(original_image, (input_size, input_size))
        image_data = image_data / 255.

        # get image name by using split method
        image_name = "image"

        images_data = []
        for i in range(1):
            images_data.append(image_data)
        images_data = np.asarray(images_data).astype(np.float32)

        infer = saved_model_loaded.signatures['serving_default']
        batch_data = tf.constant(images_data)
        pred_bbox = infer(batch_data)
        for key, value in pred_bbox.items():
                boxes = value[:, :, 0:4]
                pred_conf = value[:, :, 4:]

            # run non max suppression on detections
        boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
                boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
                scores=tf.reshape(
                    pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
                max_output_size_per_class=50,
                max_total_size=50,
                iou_threshold=iou,  # iou
                score_threshold=score  # score
            )

        # format bounding boxes from normalized ymin, xmin, ymax, xmax ---> xmin, ymin, xmax, ymax
        original_h, original_w, _ = original_image.shape
        bboxes = utils.format_boxes(boxes.numpy()[0], original_h, original_w)

        # hold all detection data in one variable
        pred_bbox = [bboxes, scores.numpy()[0], classes.numpy()[0],
                        valid_detections.numpy()[0]]

        # read in all class names from config
        class_names = utils.read_class_names(cfg.YOLO.CLASSES)

        # by default allow all classes in .names file
        allowed_classes = list(class_names.values())

        crop_path = os.path.join(os.getcwd(), 'detections', 'crop', image_name)
        
        crop_objects(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB),
                        pred_bbox, crop_path, allowed_classes)

        ocr(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB), pred_bbox)

        image, plate_number = utils.draw_bbox(
                original_image, pred_bbox, info=True, allowed_classes=allowed_classes, read_plate=True)

        image = Image.fromarray(image.astype(np.uint8))
        image.show()
        image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
        registration_plate.append(plate_number)
    return {
        "registration_number_1":registration_plate[0],
        "registration_number_2":registration_plate[1]   
            }


def start(host="0.0.0.0", port=4040):
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start()
 