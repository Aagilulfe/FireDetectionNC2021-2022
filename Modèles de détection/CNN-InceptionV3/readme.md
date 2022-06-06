installation :
pip install -r dependencies.txt

test de l'installation :
python .\cnn_detect.py --model .\CNNFireTrackingTrained.h5 --size 500 --source .\images.jpg

• Pour entrainer un modèle CNN :

python cnn_train.py --dataset {dataset path} --size {size of image default=500}
--batch {size of the batch default=20} --epochs {number of epochs default=50}

• Pour lancer un test:

python cnn_val.py --model {location of the model} -- source {path} --size {size of image}

• Pour lancer une détection :

python cnn_detect.py --model {location of the model} -- source {xxx.png/jpeg} --size {size of image}
