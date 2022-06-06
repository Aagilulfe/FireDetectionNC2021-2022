lien utile : https://github.com/ultralytics/yolov5

installation :
cd yolov5
git pull
pip install -r requirements.txt # install

test de l'installation :
python .\yolov5\detect.py --weights .\YoloV5FireTrackingTrained.pt --img 500 --conf 0.5 --source .\images.jpg

• Pour entrainer un modèle YOLOv5 :
python yolov5/train.py --data {dataset path}/data.yaml
--img {size of image} --batch {size of the batch}
--epochs {number of epochs} --weights yolov5x.pt OR yolov5s.pt --cache

• Pour lancer une détection :
python yolov5/detect.py --weights {location of the model}
--img {size of image} --conf {threshold of detection}
--source 0 # webcam
img.jpg # image  
 vid.mp4 # video  
 path/ # directory  
 path/\*.jpg # glob

• Pour lancer un test:
python yolov5/val.py --data {dataset path}/data.yaml
--img {size of image} --weights {location of the model}
--iou {threshold of detection}
