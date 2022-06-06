import tensorflow as tf
from tensorflow.keras.preprocessing import image
import cv2
import numpy as np
import sys

path_model = "./model/model.h5"
path_img = ""
size = 500

for i in range(1, len(sys.argv)):

    if sys.argv[i] == "--source":
        path_img = str(sys.argv[i+1])
        i = i+1
    if sys.argv[i] == "--size":
        size = int(sys.argv[i+1])
        i = i+1
    if sys.argv[i] == "--model":
        path_model = str(sys.argv[i+1])
        i = i+1

model = tf.keras.models.load_model(path_model)

img = image.load_img(path_img, target_size=(size, size))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0) / 255
print("no_smoke          smoke")
classes = model.predict(x)
print(classes)
