import collections
import shutil
import time
from platform import python_version

# import math
import numpy as np
import tensorflow as tf

import ocr.model as model
from ocr.eval import resize_image, sort_poly, detect
from ocr.post_merge import *

if python_version()[0] == "3":
    import functools as functools
else:
    import backports.functools_lru_cache as functools

# from config_mp import PER_PROCESS_GPU_USAGE



@functools.lru_cache(maxsize=100)
def get_predictor(checkpoint_path):
    input_images = tf.placeholder(dtype=tf.float32, shape=[None, None, None, 3], name='input_images')
    f_score, f_geometry = model.model(input_images, is_training=False)
    global_step = tf.get_variable(name='global_step', shape=[], initializer=tf.constant_initializer(0), trainable=False)
    variable_averages = tf.train.ExponentialMovingAverage(decay=0.997, num_updates=global_step)
    saver = tf.train.Saver(variable_averages.variables_to_restore())

    # gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=PER_PROCESS_GPU_USAGE)
    # sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
    GPU_FRACTION = 0.33
    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=GPU_FRACTION)
    config = tf.ConfigProto(gpu_options=gpu_options)
    sess = tf.Session(config=config)

    ckpt_state = tf.train.get_checkpoint_state(checkpoint_path)
    model_path = os.path.join(checkpoint_path, os.path.basename(ckpt_state.model_checkpoint_path))
    saver.restore(sess, model_path)

    def predictor(img):
        im_resized, (ratio_h, ratio_w) = resize_image(img,1500)
	
        score, geometry = sess.run([f_score, f_geometry], feed_dict={input_images: [im_resized[:,:,::-1]]})
        boxes = detect(score_map=score, geo_map=geometry)

        if boxes is not None:
            scores = boxes[:,8].reshape(-1)
            boxes = boxes[:, :8].reshape((-1, 4, 2))
            boxes[:, :, 0] /= ratio_w
            boxes[:, :, 1] /= ratio_h
        text_lines = []
        if boxes is not None:
            text_lines = []
            for box, score in zip(boxes, scores):
                box = sort_poly(box.astype(np.int32))
                if np.linalg.norm(box[0] - box[1]) < 5 or np.linalg.norm(box[3]-box[0]) < 5:
                    continue
                temp = zip(['x0', 'y0', 'x1', 'y1', 'x2', 'y2', 'x3', 'y3'], map(float, box.flatten()))
                tl = collections.OrderedDict(temp)
                tl['score'] = float(score)
                text_lines.append(tl)
        ret = {'text_lines': text_lines}
        return ret
    return predictor


def tl_resnet(input_path,output_path):
    checkpoint_path = './data/models/resnet'
    image_name=os.path.basename(input_path)
    fname = os.path.splitext(image_name)[0]

    line_path = output_path
    output_path = os.path.join(output_path, fname)
    if os.path.isdir(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path)
    os.makedirs(os.path.join(output_path,'typed'))

    img = cv2.imread(input_path)
    rst = get_predictor(checkpoint_path)(img)
    cord_list = post_nms(img.copy(), rst)
    if len(cord_list)==0:
        tf.reset_default_graph()
        return []

    ocr_inputs=crop_textboxes(output_path, img.copy(),cord_list,fname)

    tf.reset_default_graph()
    #sess.close()

    return ocr_inputs


def callOCR(inputPath, outputPath,typeDoc, category):
    try:
        return tl_resnet(inputPath, outputPath)
    except:
        print(traceback.print_exc())
        pass


def fmain():
#if __name__ == '__main__':
    inputPath   = './data/inputs'
    outputPath  = './data/outputs'

    if os.path.isdir(outputPath):
        shutil.rmtree(outputPath)
    os.makedirs(outputPath)

    samplesList = os.listdir(inputPath)
    for sample in samplesList:
        print(sample)
        start= time.time()
        ocr_inputs=tl_resnet("./data/models/resnet/",os.path.join(inputPath,sample), outputPath,'IMAGE')
        print(time.time() - start)
