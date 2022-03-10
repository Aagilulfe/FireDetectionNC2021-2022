import os
import random
# import numpy as np # linear algebra
# import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# import torch
# import torchvision
# import seaborn as sns
# import matplotlib.pyplot as plt

from PIL import Image, ImageDraw
import xml.etree.ElementTree as ET

# path = os.path.dirname(os.path.abspath(__file__))
os.chdir("D:/Luc/PROJET CALEDONIE/test RCNN")
path = "D:/Luc/PROJET CALEDONIE/test RCNN"
# os.chdir(path)
images_dir = path
annotations_dir = path

# for dirname, _, filenames in os.walk('/kaggle/input'):
#     for filename in filenames:
#         print(os.path.join(dirname, filename))

list_image = os.listdir('train/image')
image = list_image[random.randint(0,len(list_image))]

# sample_image = Image.open('draft/draft.jpeg')
sample_image = Image.open('train/image/'+image)

with open(path+'/train/xml/'+image[:-4]+'xml') as annot_file:
    print(''.join(annot_file.readlines()))



tree = ET.parse(path+'/train/xml/'+image[:-4]+'xml')
root = tree.getroot()

sample_annotations = []

for neighbor in root.iter('bndbox'):
    # xmin = int(neighbor.find('xmin').text[:-2])
    # ymin = int(neighbor.find('ymin').text[:-2])
    # xmax = int(neighbor.find('xmax').text[:-2])
    # ymax = int(neighbor.find('ymax').text[:-2])
    xmin = float(neighbor.find('xmin').text)
    ymin = float(neighbor.find('ymin').text)
    xmax = float(neighbor.find('xmax').text)
    ymax = float(neighbor.find('ymax').text)

#     print(xmin, ymin, xmax, ymax)
    sample_annotations.append([xmin, ymin, xmax, ymax])

print(sample_annotations)

sample_image_annotated = sample_image.copy()

img_bbox = ImageDraw.Draw(sample_image_annotated)

for bbox in sample_annotations:
    print(bbox)
    img_bbox.rectangle(bbox, outline="green")

sample_image_annotated.save(path+'/draft/annotated.jpeg')