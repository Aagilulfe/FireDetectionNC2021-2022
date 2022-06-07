import sys
import tensorflow as tf
from keras_preprocessing.image import ImageDataGenerator
import numpy as np
import sklearn
from sklearn.metrics import confusion_matrix


model = ""
source = ""
size = 500
for i in range(1, len(sys.argv)):

    if sys.argv[i] == "--model":
        model = str(sys.argv[i+1])
        i = i+1
    if sys.argv[i] == "--source":
        source = int(sys.argv[i+1])
        i = i+1
    if sys.argv[i] == "--size":
        size = int(sys.argv[i+1])
        i = i+1

model = tf.keras.models.load_model(model)

validation_datagen = ImageDataGenerator(rescale=1./255)

validation_generator = validation_datagen.flow_from_directory(
    source,
    target_size=(size, size),
    class_mode='categorical',
    shuffle=False)

test_data = validation_generator

predictions = model.predict(test_data)
prediction_labels = list(np.argmax(predictions, axis=-1))
true_labels = test_data.classes
labels = (test_data.class_indices)

print("confusion matrix :\n", confusion_matrix(true_labels, prediction_labels))
print('')
print(labels)
print('')
print("classification report :\n", sklearn.metrics.classification_report(
    true_labels, prediction_labels))
