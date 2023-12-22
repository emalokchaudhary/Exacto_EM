from __future__ import print_function
import os
import shutil
import time
from ocr.lseg import tl_resnet
import tensorflow as tf
from . import lstm
import time
import pickle
from PIL import Image
import numpy
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import scipy.misc
from ocr.helper import (load_test_data,load_test_data2, get_sequence_length,sparse)
from ocr.config import (batch_size,training_batch,total_epochs, line_shape_t,decay_factor,eta_initial,
                    decay_step, dropout, momentum, validation_step,num_training_images, num_testing_images)
from ocr.create_txt import getText

def edit_distance(a,b):
    n, m = len(a), len(b)
    if n > m: a,b = b,a; n,m = m,n
    current = range(n+1)
    for i in range(1,m+1):
        previous,current = current,[i]+[0]*n
        for j in range(1,n+1):
            add,delete = previous[j]+1,current[j-1]+1
            change = previous[j-1]
            if a[j-1]!=b[i-1]: change = change+1
            current[j] = min(add, delete, change)
    return current[n]

def callPrediction(seg_list, outpath, input, type_of_doc):

    path = "data/inputs/"
    #outpath = "data/outputs/"
    if True:
        start = time.time()
        if type_of_doc == 'IMAGE':
            output_file_path = os.path.join(outpath,input[:-4]+"-1.txt")
            output_file_path2 = os.path.join(outpath,input[:-4]+"-1_info.txt")
        else:
            output_file_path = os.path.join(outpath,input[:-4]+".txt")
            output_file_path2 = os.path.join(outpath,input[:-4]+"_info.txt")
        output_file_path3 = os.path.join(outpath,input[:-4])
        output_file_path3 = output_file_path3 + "/typed/"
        # print(output_file_path, output_file_path2, output_file_path3)
        #seg_list = tl_resnet(os.path.join(path,input), outpath)
    if not seg_list:
        return
    else:
        #return
        #print("prediction called")
        lines_list = []
        names2 = []
        #print(len(seg_list))
        #print(seg_list[0])
        #print(len(seg_list[1]))

        #print(seg_list[0][0])
        # print(len(seg_list), len(seg_list[0]), len(seg_list[1]), len(seg_list[2]) )
        names2 = seg_list[0][0] #+ seg_list[3]
        lines_list = seg_list[0][1] #+ seg_list[4]
        cordinates = seg_list[0][2] #+ seg_list[5]

        #print(len(names2), len(lines_list))
        #print(input_path, outpath,output_file_path)
        #print(outpath, output_file_path)
        #ocr_output = os.path.join(output_file_path,"ocr_folder")
        #os.makedirs(ocr_output)
        #print(len(lines_list))
        #output_file = open(output_file_path, 'w')

        # print("SEGMENTATION TIME : ",time.time()-start)
        # print("Number of image : {}".format(len(lines_list)))
        # print(len(lines_list), len(names2))
        #print(lines_list)

            #img.show()

        # print(len(seg_list))
        # print(len(lines_list))
        x_test,y_test,names, cordinates2  = load_test_data2(lines_list, names2, cordinates)

        # print("number of cordinates : ", len(cordinates2), len(names), len(x_test))

        test_seq_len =  get_sequence_length(x_test)

        if(len(x_test)==0):
            print("No Image from segmentation, this may a black image")
            return

        with tf.name_scope('input'):
            X = tf.placeholder(tf.float32, name='inputs_placeholder', shape=[None, None, line_shape_t[1]])
            #Y = tf.sparse_placeholder(tf.int32, name='output_placeholder')
            sequence_length = tf.placeholder(tf.int32, name="sequence_length_placeholder", shape=[None])
        #prediction_output(x_test,test_seq_len,names)

        #tf.reset_default_graph()
        #graph = tf.Graph
        model = lstm.Model(batch_size)
        logits,weight, bias  = model.LSTM(X, sequence_length)


        with tf.name_scope('searching'):
                #decoded, log_prob = tf.nn.ctc_beam_search_decoder(logits, sequence_length, merge_repeated=False)
                decoded, log_prob = tf.nn.ctc_greedy_decoder(logits, sequence_length)

        saver = tf.train.Saver()
        GPU_FRACTION = 0.33
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=GPU_FRACTION)
        config=tf.ConfigProto(gpu_options=gpu_options)

        with tf.Session(config=config) as session:
            #tf.reset_default_graph()
            #model_path = os.path.join(os.getcwd(),'checkpoints2/hclocr-cpkt-16000')
            #model_path = os.path.join(os.getcwd(),'checkpoints/hclocr-cpkt-55000')
            model_path = os.path.join(os.getcwd(),'./data/models/ocr/hclocr-multi-lang-cpkt-176000')
            # print(model_path)
            start = time.time()

            #saver.restore(session, tf.train.latest_checkpoint(model_path))
            saver.restore(session, model_path)
            #get_pep(1024,session, model_path, saver)
            end = time.time()
            # print("Load time is {}".format(end-start))

            decoded_output_list = session.run(decoded[0], feed_dict={X: x_test, sequence_length: test_seq_len})
            #session.close()
            # print("number of Predicted outputs", len(test_seq_len))
            # print("number of Predicted outputs", len(decoded_output_list))
            #print(decoded_output_list)
            detected_list = sparse(decoded_output_list)
            cer = 0
            # print("Prediction time is {}".format(time.time()-end))
            # print("number of lines ",len(x_test))
            # print("number of names", len(names))
            # print("number of Predicted outputs", len(detected_list))
            temp = " "
            list_cord = []
            counter = 0
            idx =0
            # print("Nunber of images for OCR : ",len(x_test), len(cordinates2), len(names))
            # print("lenght of the list ",len(detected_list))
            while(idx < len(detected_list)):
                #print(idx)
                try:
                #print(idx, names[idx])
                    if(names[idx][1] == -1):
                        try:
                            pred = "".join(detected_list[idx])
                        except:
                            print("Error 1")
                            pred = " "
                        pred = pred.strip()
                        out = pred
                        temp = " "
                        #if type(out)==unicode: out = out.encode("utf-8")


                        #print(idx, names[idx])
                        #print(out)
                        #print(cordinates2[idx])
                        #print(names[idx])
                        # print(out, names[idx])
                        try:
                            list_cord.append((out, cordinates2[idx], names[idx]))
                            with open(os.path.join(output_file_path3,names[idx][0][:-4]+".txt"), "w") as filewriter:
                                filewriter.write(out)
                        except:
                            pass

                        #print((out, cordinates2[idx-1], names[idx-1]))
                        idx+=1
                    else:
                        while True:
                            #print(idx)
                            try:
                                pred = "".join(detected_list[idx])
                            except:
                                print("Error 2")
                                pred = " "
                            pred = pred.strip()
                            temp = temp + pred
                            idx +=1
                            if(names[idx][1] == -1 or names[idx][1] == 0):
                                break
                        #print(idx-1, names[idx-1])
                        out = temp
                        temp = " "
                        #if type(out)==unicode: out = out.encode("utf-8")
                        #print(idx-1, names[idx-1])
                        list_cord.append((out, cordinates2[idx-1], names[idx-1]))
                        with open(os.path.join(output_file_path3,names[idx-1][0][:-4]+".txt"), "w") as filewriter:
                            filewriter.write(out)
                        #print((out, cordinates2[idx-1], names[idx-1]))
                except:
                    pass



        getText(list_cord, cordinates, names2, output_file_path2)
        # with open(output_file_path, "w") as stream:
        #     for line in txt:
        #         stream.write(str(line))
        #         stream.write('\n')
        tf.reset_default_graph()

if __name__=="__main__":
    run_test()
    #x_test,y_test,names  = load_test_data2(num_testing_images)
