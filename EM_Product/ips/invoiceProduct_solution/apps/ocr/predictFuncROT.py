import tensorflow as tf
import numpy as np
import cv2 


def predictRotation(image_path):
    sess = tf.Session()
    saver = tf.train.import_meta_graph('data/models/TRClassifier/thomsonReuter-model.meta')
    saver.restore(sess, tf.train.latest_checkpoint('data/models/TRClassifier'))
    graph = tf.get_default_graph()
    y_pred = graph.get_tensor_by_name("y_pred:0")
    x= graph.get_tensor_by_name("x:0")
    y_true = graph.get_tensor_by_name("y_true:0")
    y_test_images = np.zeros((1, 2))
    
    classes = ['rotated','notrotated']

    image_size=256
    num_channels=3
    images = []
    image = cv2.imread(image_path)
    origImage = image
    image = cv2.resize(image, (image_size, image_size), cv2.INTER_LINEAR)
    images.append(image)
    images = np.array(images, dtype=np.uint8)
    images = images.astype('float32')
    images = np.multiply(images, 1.0/255.0)
    x_batch = images.reshape(1, image_size,image_size,num_channels)
    feed_dict_testing = {x: x_batch, y_true: y_test_images}
    result=sess.run(y_pred, feed_dict=feed_dict_testing) 
    
    if classes[list(result[0]).index(max(result[0]))] == "rotated":
        Img = origImage
        h,w=Img.shape[:2]
        gray = cv2.cvtColor(Img, cv2.COLOR_BGR2GRAY)
        binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)[1]
        contImg, contrs, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        countLeft = 0
        countRight = 0
        countTop = 0
        countBottom = 0
        for cont in contrs:
            (bx, by, ww, hh) = cv2.boundingRect(cont)
            if bx > 0 and bx <= 0.2*w and by > 0 and by <= h:
                countLeft += 1
            if bx >= 0.8*w and bx <= w and by > 0 and by <= h:
                countRight += 1
            if by > 0 and by <= 0.2*h and bx > 0 and bx <= w:
                countTop += 1
            if by >= 0.8*h and by <= h and bx > 0 and bx <= w:
                countBottom += 1
        if countTop < 50 or countRight < 50:
            outImg = np.fliplr(origImage.swapaxes(0, 1))
        elif countBottom < 50 or countLeft < 50:
            outImg = np.fliplr(origImage.swapaxes(0, 1))
            outImg = np.fliplr(outImg.swapaxes(0, 1))
            outImg = np.fliplr(outImg.swapaxes(0, 1))
        elif countTop < countBottom:    
            outImg = np.fliplr(origImage.swapaxes(0, 1))
        elif countTop > countBottom:        
            if abs(countTop-countBottom) < 300:
                outImg = np.fliplr(origImage.swapaxes(0, 1))
                outImg = np.fliplr(outImg.swapaxes(0, 1))
                outImg = np.fliplr(outImg.swapaxes(0, 1))
            else:
                outImg = np.fliplr(origImage.swapaxes(0, 1))
                
        cv2.imwrite(image_path,outImg)
    tf.reset_default_graph()
    sess.close()        