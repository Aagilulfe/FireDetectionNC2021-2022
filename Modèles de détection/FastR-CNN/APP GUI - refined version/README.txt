PROJET CALEDONIE 2021/2022. Mines Nancy & Analytics.nc
Détection de départs d'incendie en forêts calédoniennes.

GUI programmée en langage Python pour la comparaison entre deux modèles FastRCNN sur des datasets de test.

STRUCTURE (Dossiers à créer avant le premier lancement du programme !)
Les modèles sont stockés dans models/
Les datasets de test sont dans test_images/

Les images analysées avec bbox seront stockées dans temp/
Les archives zip téléchargées seront dans results/

hiérarchie à respecter:
APP GUI
    /models
    /test_images
    /temp
    /results

UTILISATION
Exécuter GUI_FasterRCNN.py avec python

ATTENTION
L'exécution de l'application peut nécessiter une certaine version de torch ou torchvision.
Pour obtenir les bonnes versions, veuillez exécuter l'installation suivante (prend un certain temps mais à ne faire que la première fois):

pip3 install torch==1.10.0+cu113 torchvision==0.11.1+cu113 torchaudio===0.10.0+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html
