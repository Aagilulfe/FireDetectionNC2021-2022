import sys
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Input, Dropout
from tensorflow.keras.optimizers import Adam
import tensorflow as tf
import keras_preprocessing
from keras_preprocessing import image
from keras_preprocessing.image import ImageDataGenerator
import numpy as np
import matplotlib.pyplot as plt
import os
from tensorflow.keras.optimizers import SGD
import sklearn
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

path = ""
size = 500
nb_epochs = 20
batch_size = 50

for i in range(1, len(sys.argv)):

    if sys.argv[i] == "--dataset":
        path = str(sys.argv[i+1])
        i = i+1
    if sys.argv[i] == "--size":
        size = int(sys.argv[i+1])
        i = i+1
    if sys.argv[i] == "--batch":
        batch_size = str(sys.argv[i+1])
        i = i+1
    if sys.argv[i] == "--epochs":
        nb_epochs = int(sys.argv[i+1])
        i = i+1


TRAINING_DIR = path+"/train"
training_datagen = ImageDataGenerator(rescale=1./255,
                                      rotation_range=10,
                                      height_shift_range=0.2,
                                      fill_mode='nearest')
VALIDATION_DIR = path+"/valid"
validation_datagen = ImageDataGenerator(rescale=1./255)
train_generator = training_datagen.flow_from_directory(TRAINING_DIR,
                                                       target_size=(
                                                           size, size),
                                                       class_mode='categorical',
                                                       batch_size=batch_size, shuffle=True)
validation_generator = validation_datagen.flow_from_directory(
    VALIDATION_DIR,
    target_size=(size, size),
    class_mode='categorical',
    batch_size=batch_size//2, shuffle=True)


input_tensor = Input(shape=(size, size, 3))
base_model = InceptionV3(input_tensor=input_tensor,
                         weights='imagenet', include_top=False)
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(2048, activation='relu')(x)
x = Dropout(0.25)(x)
x = Dense(1024, activation='relu')(x)
x = Dropout(0.2)(x)
predictions = Dense(2, activation='softmax')(x)
model = Model(inputs=base_model.input, outputs=predictions)
for layer in base_model.layers:
    layer.trainable = False
model.compile(optimizer='rmsprop',
              loss='categorical_crossentropy', metrics=['acc'])


history = model.fit(
    train_generator, epochs=nb_epochs, validation_data=validation_generator)
model.save("InceptionV3_final.h5")

plt.plot(history.epoch, history.history["loss"], 'g', label='Training loss')
plt.title('Training loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()
plt.plot(history.epoch, history.history["acc"], 'r', label='Accuracy')
plt.title('Accuracy')
plt.xlabel('Epochs')
plt.ylabel('acc')
plt.legend()
plt.show()

test_data = validation_generator
train_data = train_generator
predictions = model.predict(train_data)
results = model.evaluate(train_data, batch_size=75)
prediction_labels = list(np.argmax(predictions, axis=-1))
true_labels = train_data.classes
labels = (train_data.class_indices)
print("train loss : ", results[0])
print("train accuracy : ", results[1])
print('')
print("confusion matrix :\n", confusion_matrix(true_labels, prediction_labels))
print('')
print(labels)
print('')
print("classification report :\n", sklearn.metrics.classification_report(
    true_labels, prediction_labels))

print("end first step\n")

for layer in model.layers[:249]:
    layer.trainable = False
for layer in model.layers[249:]:
    layer.trainable = True
model.compile(optimizer=SGD(lr=0.0001, momentum=0.9),
              loss='categorical_crossentropy', metrics=['acc'])
history = model.fit(
    train_generator,
    epochs=10,
    validation_data=validation_generator)


plt.plot(history.epoch, history.history["loss"], 'g', label='Training loss')
plt.title('Training loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()
plt.plot(history.epoch, history.history["acc"], 'r', label='Accuracy')
plt.title('Accuracy')
plt.xlabel('Epochs')
plt.ylabel('acc')
plt.legend()
plt.show()

test_data = validation_generator
train_data = train_generator
predictions = model.predict(train_data)
results = model.evaluate(train_data, batch_size=75)
prediction_labels = list(np.argmax(predictions, axis=-1))
true_labels = train_data.classes
labels = (train_data.class_indices)
print("train loss : ", results[0])
print("train accuracy : ", results[1])
print('')
print("confusion matrix :\n", confusion_matrix(true_labels, prediction_labels))
print('')
print(labels)
print('')
print("classification report :\n", sklearn.metrics.classification_report(
    true_labels, prediction_labels))


history = model.fit(
    train_generator, epochs=nb_epochs, validation_data=validation_generator)
model.save("InceptionV3_final_2.h5")
