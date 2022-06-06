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
from torchvision import transforms
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor


def visualize_prediction(model, dataset, n_rows, n_columns, device, brut_data= None):
    """ Visualisation des prédictions """
    model.eval() # on définit le model en mode évaluation

    np.random.seed(40)

    # random d'indexs à tracer
    indexes = np.random.randint(0, len(dataset), n_rows * n_columns)
    
    fig, axs = plt.subplots(n_rows, n_columns, figsize=(17, 20))

    for idx, sample_idx in enumerate(indexes):
        img, true_roi = dataset[sample_idx] # selection random d'une image
        true_receipt = true_roi["boxes"][0]
        # true_total = true_roi["boxes"][1]

        # 
        #Obtention des resultats de prédition pour une image et copie du résultat du GPU vers le CPU
        
         
        prediction = model([img.to(device)])[0]#.detach().cpu().numpy()
        #On recupère toutes les prédictions sous forme de tuple(box,classe,score) par ordre de précision
        data_zip=list(zip(*[v for k,v in prediction.items()]))
        #0n recupère les tuples appartenant à la classe 1(detection de contour de reçu)
        print("value: ", data_zip)
        all_receipt_pred = [value for value in data_zip if value[1]==1]
        #0n recupère les tuples appartenant à la classe 2(zone délimitant le total)
        # all_total_pred = [value for value in data_zip if value[1]==2]

        #print('pred_roi',pred_roi[0:2])

        # transform the PyTorch Tensor to PIL format 
        #transformation du tensor pythorh au format PIL pour matplotlib
        img = transforms.ToPILImage()(img)

        axs[idx // n_columns, idx % n_columns].imshow(img)

        # create  de rectangle en rouge pour les vraies coordonnées délimitant le réçu et son total
     
        true_receipt = Rectangle(xy=(true_receipt[0], true_receipt[1]), width=true_receipt[2] - true_receipt[0],
                                  height=true_receipt[3] - true_receipt[1], 
                                  linewidth=1, edgecolor='red', facecolor='none', alpha=0.7)
          
        # true_total = Rectangle(xy=(true_total[0], true_total[1]), width=true_total[2] - true_total[0],
        #                           height=true_total[3] - true_total[1], 
        #                           linewidth=1, edgecolor='red', facecolor='none', alpha=0.7)

        if not brut_data:

            axs[idx // n_columns, idx % n_columns].add_patch(true_receipt)
            # axs[idx // n_columns, idx % n_columns].add_patch(true_total)


        #Si prédiction de zone de reçu alors on affiche le premiers élement avec le meilleur score
        if data_zip != [] and all_receipt_pred:
          print("all_receipt_pred: ", all_receipt_pred)
         
          all_receipt_pred = all_receipt_pred[0][0].detach().cpu().numpy()
          #print(all_receipt_pred)
         
          receipt_pred= Rectangle(xy=(all_receipt_pred[0], all_receipt_pred[1]), width=all_receipt_pred[2] - all_receipt_pred[0],
                                height=all_receipt_pred[3] - all_receipt_pred[1], 
                                linewidth=1, edgecolor='blue', facecolor='none', alpha=0.7)
          
          
        #Si prédiction de zone de total alors on affiche le premiers élement avec le meilleur score
        # if all_total_pred :
        #   all_total_pred = all_total_pred[0][0].detach().cpu().numpy()
        #   total_pred = Rectangle(xy=(all_total_pred[0], all_total_pred[1]), width=all_total_pred[2] - all_total_pred[0],
        #                                 height=all_total_pred[3] - all_total_pred[1], 
        #                                 linewidth=1, edgecolor='blue', facecolor='none', alpha=0.7)
          
          axs[idx // n_columns, idx % n_columns].add_patch(receipt_pred)
          # axs[idx // n_columns, idx % n_columns].add_patch(total_pred)


        legend_elements = [Patch(facecolor='none', edgecolor='red', 
                                label='True Smoke '),
                          Patch(facecolor='none', edgecolor='blue',
                                label='Pred Smoke'),]

        axs[idx // n_columns, idx % n_columns].legend(handles=legend_elements, loc='upper left')
        axs[idx // n_columns, idx % n_columns].axis('off')

    plt.subplots_adjust(wspace=0.25, hspace=0.2)
    plt.suptitle('Visualization of model predictions')
    plt.show()