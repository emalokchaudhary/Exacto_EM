import tensorflow as tf
import numpy as np
import cv2

classes = ['tables', 'nontables']
image_size = 256
num_channels = 3
classesL = ['liners', 'nonliners']



def predClass(image):
    sess = tf.Session()
    saver = tf.train.import_meta_graph('./data/models/TabNTab/TabNTab_model.meta')
    saver.restore(sess, tf.train.latest_checkpoint('./data/models/TabNTab/'))
    graph = tf.get_default_graph()
    y_pred = graph.get_tensor_by_name("y_pred:0")
    x = graph.get_tensor_by_name("x:0")
    y_true = graph.get_tensor_by_name("y_true:0")
    y_test_images = np.zeros((1, 2))

    images = []
    image = cv2.resize(image, (image_size, image_size), cv2.INTER_LINEAR)
    images.append(image)
    images = np.array(images, dtype=np.uint8)
    images = images.astype('float32')
    images = np.multiply(images, 1.0/255.0)
    x_batch = images.reshape(1, image_size,image_size,num_channels)
    feed_dict_testing = {x: x_batch, y_true: y_test_images}
    result=sess.run(y_pred, feed_dict=feed_dict_testing)
    tf.reset_default_graph()
    sess.close()
    return classes[list(result[0]).index(max(result[0]))]


def predClassLiner(image):
    sess = tf.Session()
    saver = tf.train.import_meta_graph('./data/models/Liners/liners_model.meta')
    saver.restore(sess, tf.train.latest_checkpoint('./data/models/Liners/'))
    graph = tf.get_default_graph()
    y_pred = graph.get_tensor_by_name("y_pred:0")
    x = graph.get_tensor_by_name("x:0")
    y_true = graph.get_tensor_by_name("y_true:0")
    y_test_images = np.zeros((1, 2))

    images = []
    image = cv2.resize(image, (image_size, image_size), cv2.INTER_LINEAR)
    images.append(image)
    images = np.array(images, dtype=np.uint8)
    images = images.astype('float32')
    images = np.multiply(images, 1.0/255.0)
    x_batch = images.reshape(1, image_size,image_size,num_channels)
    feed_dict_testing = {x: x_batch, y_true: y_test_images}
    result=sess.run(y_pred, feed_dict=feed_dict_testing)
    tf.reset_default_graph()
    sess.close()
    return classesL[list(result[0]).index(max(result[0]))]
