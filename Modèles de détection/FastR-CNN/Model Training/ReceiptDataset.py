import os
import pandas as pd
import os
from PIL import Image as Im
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from matplotlib.patches import Patch
import xml.etree.ElementTree as ET
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
import torchvision
from torchvision.transforms import ToTensor
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor

class ReceiptDataset(Dataset):
    """ On hérite ici de la classe dataset pour sa modification """
 
    def __init__(self, dataframe, resize_img=None, resize_roi=None):
     
        self.dataframe=dataframe
        #initialisation des images-ids,on utilise le nom des fichiers comme id_unique
        self.image_ids=dataframe.img_name.unique()
        #initialisation des fonctions de redimentionnement
        self.resize_img = resize_img
        self.resize_roi = resize_roi
 
    def __len__(self) -> int:
        return self.image_ids.shape[0]
 
    def __getitem__(self, index):
         
         #lecture des images (on recupère la ligne associée à chaque index(coordonnées reçu et total)
        image_id = self.image_ids[index]
        row = self.dataframe[self.dataframe['img_name'] == image_id]
        # total_box=row.coord_total.values[0]
        receipt_box=row.roi.values[0]
        # print("receipt_box", receipt_box)
        image = Im.open(row.img_path.values[0])
        image = ToTensor()(image)
 
        if self.resize_roi:
           #Si une fonction de redimentionnement est fournie, on transforme l'image dans la nouvelle taille définie
            # total_box = self.resize_roi(total_box, original_shape=(image.size[1], image.size[0]))
            receipt_box = self.resize_roi(receipt_box, original_shape=(image.size[1], image.size[0]))
             
        if self.resize_img:
            #Si une fonction de redimentionnement est fournie, on met à l'échelle l'image
            image = self.resize_img(image)
        #concaténation des coodonnées du reçu et du total    
        boxes = [receipt_box]
        # print("boxes: ", boxes)
 
        # création de dictionnaire cible et formats appropriés de données pour tensorflow
        target = {}
        target['boxes']= torch.as_tensor(boxes,dtype=torch.float32)
        #on a ici 2 classes
        target['labels'] =torch.as_tensor([1],dtype=torch.int64)
        target['image_id'] = torch.tensor([index])
        target['area'] = torch.tensor([(receipt_box[3] - receipt_box[1]) * (receipt_box[2] - receipt_box[0])])
        # target['area'] = torch.tensor([(receipt_box[3] - receipt_box[1]) * (receipt_box[2] - receipt_box[0]), (total_box[3] - total_box[1]) * (total_box[2] - total_box[0])])
        target['iscrowd'] = torch.zeros((1,), dtype=torch.int64)
 
        return image, target
        # return image, target


class RoiRescale(object):
    """Classe de redimensionnement des images """
     
    def __init__(self, new_shape):
        assert isinstance(new_shape, tuple)
        self.new_shape = new_shape
 
    def __call__(self, sample, original_shape):
        w_ratio = self.new_shape[0] / original_shape[0]
        h_ratio = self.new_shape[1] / original_shape[1]
       
        #       xmin,              ymin,              xmax,              ymax
        return [sample[0]*h_ratio, sample[2]*w_ratio, sample[1]*h_ratio, sample[3]*w_ratio]