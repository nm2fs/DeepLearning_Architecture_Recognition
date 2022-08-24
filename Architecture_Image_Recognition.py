# -*- coding: utf-8 -*-
"""nm2fs_assignment_2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1q8_y54McChd64DGWPcl_qhXBFpCia4Qw

# Recognizing UVA landmarks with neural nets (80 pts)
![UVA Grounds](https://sworld.co.uk/img/img/131/photoAlbum/5284/originals/0.jpg) 

The UVA Grounds is known for its Jeffersonian architecture and place in U.S. history as a model for college and university campuses throughout the country. Throughout its history, the University of Virginia has won praises for its unique Jeffersonian architecture. 

In this assignment, you will attempt the build an image recognition system to classify different buildlings/landmarks on Grounds. You will earn 70 points for this assignment plus 10 bonus points if (1) your classifier performs exceed 94% accuracy.

To make it easier for you, some codes have been provided to help you process the data, you may modify it to fit your needs. You must submit the .ipynb file via UVA Collab with the following format: yourcomputingID_assignment_2.ipynb

Best of luck, and have fun!

# Load Packages
"""

# Commented out IPython magic to ensure Python compatibility.
import sys
import sklearn
import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from functools import partial
import PIL
import PIL.Image
import pandas as pd


# %tensorflow_version 2.x
import tensorflow as tf
from tensorflow import keras

np.random.seed(42) # note that you must use the same seed to ensure consistentcy in your training/validation/testing
tf.random.set_seed(42)

"""# Import Dataset
The full dataset is huge (+37GB) with +13K images of 18 classes. So it will take a while to download, extract, and process. To save you time and effort, a subset of the data has been resized and compressed to only 379Mb and stored in my Firebase server. This dataset will be the one you will benchmark for your grade. If you are up for a challenge (and perhaps bonus points), contact the instructor for the full dataset!
"""

# Download dataset from FirebaseStorage
!wget https://firebasestorage.googleapis.com/v0/b/uva-landmark-images.appspot.com/o/dataset.zip?alt=media&token=e1403951-30d6-42b8-ba4e-394af1a2ddb7

# Extract content
!unzip "/content/dataset.zip?alt=media"

from sklearn.datasets import load_files 
from keras.utils import np_utils

from keras.preprocessing import image
from tqdm import tqdm # progress bar

data_dir = "/content/dataset/"
batch_size = 32;
# IMPORTANT: Depends on what pre-trained model you choose, you will need to change these dimensions accordingly
img_height = 224; 
img_width = 224;

# Training Dataset
train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    data_dir,
    validation_split = 0.2,
    subset = "training",
    seed = 42,
    image_size= (img_height, img_width),
    batch_size = batch_size
)


# Validation Dataset
validation_ds = tf.keras.preprocessing.image_dataset_from_directory(
    data_dir,
    validation_split = 0.2,
    subset = "validation",
    seed = 42,
    image_size = (img_height, img_width),
    batch_size = batch_size
)

# Visualize some of the train samples of one batch
# Make sure you create the class names that match the order of their appearances in the "files" variable
class_names = ['AcademicalVillage', 'AldermanLibrary', 'AlumniHall', 'AquaticFitnessCenter', 
  'BavaroHall', 'BrooksHall', 'ClarkHall', 'MadisonHall', 'MinorHall', 'NewCabellHall', 
  'NewcombHall', 'OldCabellHall', 'OlssonHall', 'RiceHall', 'Rotunda', 'ScottStadium', 
  'ThorntonHall', 'UniversityChapel']

# Rows and columns are set to fit one training batch (32)
n_rows = 8
n_cols = 4
plt.figure(figsize=(n_cols * 3, n_rows * 3))
for images, labels in train_ds.take(1):
    for i in range (n_rows*n_cols):
        plt.subplot(n_rows, n_cols, i + 1)
        plt.imshow(images[i].numpy().astype("uint8"))
        plt.axis('off')
        plt.title(class_names[labels[i]], fontsize=12)
plt.subplots_adjust(wspace=.2, hspace=.2)

"""# It's your turn: Building a classifier for UVA Landmark Dataset
You may design your own architecture AND re-use any of the exising frameworks. 

Best of luck!

## Data Augmentation, Zero mean and shuffling the data:
"""

# Data Augmentation - rotate horizontally:
from tensorflow.keras import layers

data_augmentation_horz = keras.Sequential(
    [
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),
    ]
)

plt.figure(figsize=(10, 10))
for images, _ in train_ds.take(1):
    for i in range(9):
        augmented_images = data_augmentation_horz(images)
        ax = plt.subplot(3, 3, i + 1)
        plt.imshow(augmented_images[0].numpy().astype("uint8"))
        plt.axis("off")

augmented_train_ds = train_ds.map(
  lambda x, y: (data_augmentation_horz(x, training=True), y))

# Zero mean:
def zero_center(train_ds):
    return train_ds - np.mean(train_ds, axis=0)

def zero_center(validation_ds):
    return validation_ds - np.mean(validation_ds, axis=0)

# Shuffle the train set:
train_ds = train_ds.shuffle(1000)
train_ds = train_ds.prefetch(buffer_size=32)
validation_ds = validation_ds.prefetch(buffer_size=32)

"""## **Architecture No. 1:**"""

# from tensorflow.keras import datasets, layers, models


# model = models.Sequential()
# model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)))
# model.add(layers.MaxPooling2D((2, 2)))
# model.add(layers.Conv2D(64, (3, 3), activation='relu'))
# model.add(layers.MaxPooling2D((2, 2)))
# model.add(layers.Conv2D(64, (3, 3), activation='relu'))
# model.add(layers.MaxPooling2D((2, 2)))
# model.add(layers.Conv2D(64, (3, 3), activation='relu'))
# model.add(layers.MaxPooling2D((2, 2)))
# model.add(layers.Conv2D(64, (3, 3), activation='relu'))
## add more conv layers and pooling layers - less parameters

model = keras.Sequential([
   keras.layers.AveragePooling2D(6,3, input_shape=(224, 224, 3)),
   keras.layers.Conv2D(64, 3, activation='relu'),
   keras.layers.Conv2D(32, 3, activation='relu'),
   keras.layers.MaxPool2D(2,2),
   keras.layers.Dropout(0.5),
   keras.layers.Flatten(),
   keras.layers.Dense(128, activation='relu'),
   keras.layers.Dense(18, activation='softmax')
])

model.summary()

# from tensorflow.keras import datasets, layers, models

# model = keras.models.Sequential()
# model.add(keras.layers.Conv2D(64, 7, strides=2, input_shape=[224, 224, 3],
#                               padding="same", use_bias=False))
# model.add(keras.layers.BatchNormalization())
# model.add(keras.layers.Activation("relu"))
# model.add(keras.layers.MaxPool2D(pool_size=3, strides=2, padding="same"))
# prev_filters = 64
# for filters in [64] * 3 + [128] * 4 + [256] * 6 + [512] * 3:
#     strides = 1 if filters == prev_filters else 2
#     #model.add(ResidualUnit(filters, strides=strides))
#     prev_filters = filters
# model.add(keras.layers.GlobalAvgPool2D())
# model.add(keras.layers.Flatten())
# model.add(keras.layers.Dense(18, activation="softmax"))

# model.summary()

# model.add(layers.Flatten())
# model.add(layers.Dense(64, activation='relu'))
# model.add(layers.Dense(18))

# model.summary()

epochs = 100

callbacks = [
    keras.callbacks.ModelCheckpoint("save_at_{epoch}.h4"),
]

optimizer = keras.optimizers.SGD(lr=0.001, momentum=0.9, decay=0.0001)
model.compile(loss="sparse_categorical_crossentropy", optimizer=optimizer,
              metrics=["accuracy"])

history = model.fit(
    train_ds.take(50), epochs=epochs, callbacks=callbacks, validation_data=validation_ds,
)

pd.DataFrame(history.history).plot(figsize=(8, 5))                 # Creating a plot that shows the accuracy and the loss rate
plt.grid(True)
plt.gca().set_ylim(0, 5)
plt.show()

score1 = model.evaluate(validation_ds)

"""## **Architecture No. 2.** (add more layers and make the architecture more complex, Chaning learning rates):"""

model2 = keras.Sequential([
   keras.layers.AveragePooling2D(6,3, input_shape=(224, 224, 3)),
   keras.layers.Conv2D(64, 3, activation='relu'),
   keras.layers.Conv2D(32, 3, activation='relu'),
   keras.layers.BatchNormalization(),
   keras.layers.MaxPool2D(2,2),
   keras.layers.Dropout(0.2),
   keras.layers.Conv2D(64, 3, activation='relu'),
   keras.layers.Conv2D(32, 3, activation='relu'),
   keras.layers.BatchNormalization(),
   keras.layers.MaxPool2D(2,2),
   keras.layers.Dropout(0.2),
   keras.layers.Flatten(),
   keras.layers.Dense(128, activation='relu'),
   keras.layers.Dense(18, activation='softmax')
])

model2.summary()

epochs = 200

callbacks = [
    keras.callbacks.ModelCheckpoint("save_at_{epoch}.h5"),
]

optimizer = keras.optimizers.SGD(lr=0.001, momentum=0.9, decay=0.0001)
model2.compile(loss="sparse_categorical_crossentropy", optimizer=optimizer,
              metrics=["accuracy"])

history3 = model2.fit(
    train_ds.take(50), epochs=epochs, callbacks=callbacks, validation_data=validation_ds,
)

pd.DataFrame(history3.history).plot(figsize=(8, 5))                 # Creating a plot that shows the accuracy and the loss rate
plt.grid(True)
plt.gca().set_ylim(0, 4)
plt.show()

score2 = model2.evaluate(validation_ds)

"""## **Architecture No. 3.** - *Scenarion 1*: (add more Conv, Maxpooling, dropout and batch normalization layers, also adding regularizations to the Conv layers and make the architecture more complex, also changes optimizer to adam):"""

model4 = keras.Sequential([
   keras.layers.AveragePooling2D(6,3, padding="same", input_shape=(224, 224, 3)),
   keras.layers.Conv2D(64, 3, activation='relu'),
   keras.layers.Conv2D(32, 3, activation='relu'),
   keras.layers.BatchNormalization(),
   keras.layers.MaxPool2D(2,2),
   keras.layers.Dropout(0.2),
   keras.layers.Conv2D(128, 3, activation='relu'),
   keras.layers.Conv2D(32, 3, activation='relu'),
   keras.layers.BatchNormalization(),
   keras.layers.MaxPool2D(2,2),
   keras.layers.Dropout(0.2),
   keras.layers.Conv2D(256, 3, activation='relu'),
   keras.layers.Conv2D(32, 3, activation='relu'),
   keras.layers.BatchNormalization(),
   keras.layers.MaxPool2D(2,2),
   keras.layers.Dropout(0.2),
   keras.layers.Flatten(),
   keras.layers.Dense(128, activation='relu'),
   keras.layers.Dense(18, activation='softmax')
])

model4.summary()

epochs = 150

callbacks = [
    keras.callbacks.ModelCheckpoint("save_at_{epoch}.h8"),
]

model4.compile(optimizer='adam',
              loss=keras.losses.SparseCategoricalCrossentropy(),
              metrics=['accuracy'])

history5 = model4.fit(
    train_ds.take(50), epochs=epochs, callbacks=callbacks, validation_data=validation_ds,
)

pd.DataFrame(history5.history).plot(figsize=(8, 5))                 # Creating a plot that shows the accuracy and the loss rate
plt.grid(True)
plt.gca().set_ylim(0, 3)
plt.show()

score4 = model4.evaluate(validation_ds)

"""In architecture 3, I was able to reach the validation accuracy of 76.20%.

## **Architecture No. 3.** - *Scenarion 2*, with regulizers in all Conv layers to reduce gaps between val and training: (add more Conv, Maxpooling, dropout and batch normalization layers, also adding regularizations to the Conv layers and make the architecture more complex, also changes optimizer to adam):
"""

model3 = keras.Sequential([
   keras.layers.AveragePooling2D(6,3, padding="same", input_shape=(224, 224, 3)),
   keras.layers.Conv2D(64, 3, activation='relu', kernel_regularizer =tf.keras.regularizers.l1( l=0.01)),
   keras.layers.Conv2D(32, 3, activation='relu', kernel_regularizer =tf.keras.regularizers.l1( l=0.01)),
   keras.layers.BatchNormalization(),
   keras.layers.MaxPool2D(2,2),
   keras.layers.Dropout(0.2),
   keras.layers.Conv2D(128, 3, activation='relu', kernel_regularizer =tf.keras.regularizers.l1( l=0.01)),
   keras.layers.Conv2D(32, 3, activation='relu', kernel_regularizer =tf.keras.regularizers.l1( l=0.01)),
   keras.layers.BatchNormalization(),
   keras.layers.MaxPool2D(2,2),
   keras.layers.Dropout(0.2),
   keras.layers.Conv2D(256, 3, activation='relu', kernel_regularizer =tf.keras.regularizers.l1( l=0.01)),
   keras.layers.Conv2D(32, 3, activation='relu', kernel_regularizer =tf.keras.regularizers.l1( l=0.01)),
   keras.layers.BatchNormalization(),
   keras.layers.MaxPool2D(2,2),
   keras.layers.Dropout(0.2),
   keras.layers.Flatten(),
   keras.layers.Dense(128, activation='relu'),
   keras.layers.Dense(18, activation='softmax')
])

model3.summary()

epochs = 120

callbacks = [
    keras.callbacks.ModelCheckpoint("save_at_{epoch}.h7"),
]

model3.compile(optimizer='adam',
              loss=keras.losses.SparseCategoricalCrossentropy(),
              metrics=['accuracy'])

history4 = model3.fit(
    train_ds.take(50), epochs=epochs, callbacks=callbacks, validation_data=validation_ds,
)

pd.DataFrame(history4.history).plot(figsize=(8, 5))                 # Creating a plot that shows the accuracy and the loss rate
plt.grid(True)
plt.gca().set_ylim(0, 56)
plt.show()

score3 = model3.evaluate(validation_ds)

"""## **Architecture No. 4. (Add more complexity to the architecture No. 3.):**"""

model5 = keras.Sequential([
   keras.layers.AveragePooling2D(6,3, padding="same", input_shape=(224, 224, 3)),
   keras.layers.Conv2D(64, 3, activation='relu'),
   keras.layers.Conv2D(64, 3, activation='relu'),
   keras.layers.Conv2D(32, 3, activation='relu'),
   keras.layers.BatchNormalization(),
   keras.layers.MaxPool2D(2,2),
   keras.layers.Dropout(0.2),
   keras.layers.Conv2D(128, 3, activation='relu'),
   keras.layers.Conv2D(32, 3, activation='relu'),
   keras.layers.BatchNormalization(),
   keras.layers.MaxPool2D(2,2),
   keras.layers.Dropout(0.2),
   keras.layers.Conv2D(256, 3, activation='relu'),
   keras.layers.Conv2D(256, 3, activation='relu'),
   keras.layers.Conv2D(32, 3, activation='relu'),
   keras.layers.BatchNormalization(),
   keras.layers.MaxPool2D(2,2),
   keras.layers.Dropout(0.2),
   keras.layers.Flatten(),
   keras.layers.Dense(128, activation='relu'),
   keras.layers.Dense(18, activation='softmax')
])

model5.summary()

epochs = 120

callbacks = [
    keras.callbacks.ModelCheckpoint("save_at_{epoch}.h9"),
]

model5.compile(optimizer='adam',
              loss=keras.losses.SparseCategoricalCrossentropy(),
              metrics=['accuracy'])

history6 = model5.fit(
    train_ds.take(50), epochs=epochs, callbacks=callbacks, validation_data=validation_ds,
)

pd.DataFrame(history6.history).plot(figsize=(8, 5))                 # Creating a plot that shows the accuracy and the loss rate
plt.grid(True)
plt.gca().set_ylim(0, 5)
plt.show()

score5 = model5.evaluate(validation_ds)

"""In architecture 4, I was able to reach the validation accuracy of 77.81%. """