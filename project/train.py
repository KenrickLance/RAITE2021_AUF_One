import tensorflow as tf
from tensorflow import keras
import numpy as np
import os
print("TensorFlow version:", tf.__version__)

batch_size = 32
IMG_SIZE = (160, 160)
data_dir = '../../Covid19-dataset/train'
data_dir_test = '../../Covid19-dataset/test'

train_dataset = tf.keras.utils.image_dataset_from_directory(
  data_dir,
  validation_split=0.2,
  subset="training",
  seed=123,
  image_size=(IMG_SIZE[0], IMG_SIZE[1]),
  batch_size=batch_size)
validation_dataset = tf.keras.utils.image_dataset_from_directory(
  data_dir,
  validation_split=0.2,
  subset="validation",
  seed=123,
  image_size=(IMG_SIZE[0], IMG_SIZE[1]),
  batch_size=batch_size)
test_dataset = tf.keras.utils.image_dataset_from_directory(
  data_dir_test,
  validation_split=0,
  seed=123,
  image_size=(IMG_SIZE[0], IMG_SIZE[1]),
  batch_size=batch_size)

data_augmentation = tf.keras.Sequential([tf.keras.layers.RandomFlip('horizontal'),tf.keras.layers.RandomRotation(0.2),])

preprocess_input = tf.keras.applications.mobilenet_v2.preprocess_input

rescale = tf.keras.layers.Rescaling(1./127.5, offset=-1)

IMG_SHAPE = IMG_SIZE + (3,)
base_model = tf.keras.applications.MobileNetV2(input_shape=IMG_SHAPE,
											   include_top=False,
											   weights='imagenet')

base_model.trainable = False

global_average_layer = tf.keras.layers.GlobalAveragePooling2D()
prediction_layer = tf.keras.layers.Dense(3)


model = tf.keras.Sequential()
model.add(tf.keras.Input(shape=(160,160,3)))
model.add(base_model)
model.add(global_average_layer)
model.add(tf.keras.layers.Dropout(0.2))
model.add(prediction_layer)


base_learning_rate = 0.001
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=base_learning_rate),
			  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
			  metrics=['accuracy'])

initial_epochs = 10

loss0, accuracy0 = model.evaluate(validation_dataset)

history = model.fit(train_dataset,
					epochs=initial_epochs,
					validation_data=validation_dataset)

base_model.trainable = True

# Let's take a look to see how many layers are in the base model
print("Number of layers in the base model: ", len(base_model.layers))

# Fine-tune from this layer onwards
fine_tune_at = 100

# Freeze all the layers before the `fine_tune_at` layer
for layer in base_model.layers[:fine_tune_at]:
  layer.trainable =  False

fine_tune_epochs = 10
total_epochs =  initial_epochs + fine_tune_epochs

history_fine = model.fit(train_dataset,
						 epochs=total_epochs,
						 initial_epoch=history.epoch[-1],
						 validation_data=validation_dataset)

loss, accuracy = model.evaluate(test_dataset)
print('Test accuracy :', accuracy)

model.save('./lung.h5')