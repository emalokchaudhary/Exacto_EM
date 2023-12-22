from ocr.config import (train_dir, test_dir, train_image_type, train_txt_type,test_image_type,
                    test_txt_type, line_shape_t,batch_size, line_shape)
import glob
import os
import shutil
import fnmatch
import time
import numpy as np
from ocr.config import charset
from numpy import (transpose, amax, amin, array, bitwise_and, clip, dtype, mean, minimum,nan, sin, sqrt, zeros)
from pylab import array, amax, vstack, zeros
from ocr.read_data import (size,encode,decode,read_image_gray,isfloatarray,pil2array,dewarp,normalize,prepare_line,line_normalization, charset)


def file_list(src,ext):
    files = []
    for root, dirnames, filenames in os.walk(src):
        for filename in fnmatch.filter(filenames, ext):
            files.append(os.path.join(root, filename))
    return files

def get_image_array(file):
        nrm = line_normalization(file)
        x, _ = nrm.shape
        b  = np.zeros((line_shape_t[0]-x, line_shape_t[1]))
        c = np.concatenate((nrm, b))
        return c

def get_gt_txt_array(file):
    f = open(file, 'r')
    gt_txt = f.read()
    cs = array(encode(gt_txt),'i')
    return cs, gt_txt

def load_train_data(counter = 20):
    x_train = []
    y_train = []

    train_dir2 = os.path.join(os.getcwd(), train_dir)
    train_images = file_list(train_dir2,train_image_type)
    train_txts = file_list(train_dir2,train_txt_type)
    #print(train_dir2)
    #print(len(train_images))
    ##print(train_txts)

    for idx, image in enumerate(train_images):

        if(idx>counter-1):
            break

        try:
            gt_file = image[:-1*len(train_image_type)+1]+train_txt_type
            #print(gt_file)
            #print(image)

            if(os.path.isfile(gt_file)):
                #print(gt_file)
                x = get_image_array(image)
                #print("Pass")
                y, gt_txt = get_gt_txt_array(gt_file)
                #print(x.shape,line_shape_t)

                if(x.shape==line_shape_t and len(y)>0):
                    x_train.append(x)
                    y_train.append(y)
                    print(idx,x.shape,len(y), gt_txt)
                else:
                    print("Some Error")
            else:
                pass

        except:
            print("Size large")

    return np.asarray(x_train), np.asarray(y_train)



def searchLastIndex(line,block):
    l = []
    xx,yy = line.shape
    x,y = block.shape
    flag1 = False
    flag2 = False
    for i in range(xx-1,-1,-1):
        ##print(i)
        ##print(i,i-x)
        ##print(line[i-x:i,].shape, block.shape)
        if(np.array_equal(line[i-x:i,],block)):
            l.append((i,1))
            flag1 = True
            if(flag1 and flag2):
                break
        else:
            l.append((i,0))
            flag2 = True
    return i

def line_break(line, p, images):
    xx, yy = line.shape
    ##print(line.shape)
    if(xx==p):
        images.append(line)
        #return (line,)
    elif(xx<p):
        b  = np.zeros((p-xx, 48))
        c = np.concatenate((line, b))
        images.append(c)
        #return (c,)
    else:
        block = np.zeros((5,48), dtype=np.float64)
        index = max(searchLastIndex(line[:p], block),p/2)
        line1 = line[:index]
        line2 = line[index+1:]
        b1  = np.zeros((p-index, 48), dtype=np.float64)
        line3 = np.concatenate((line1, b1))
        b2  = np.zeros((6, 48),dtype=np.float64)
        line4 = np.concatenate((b2, line2))
        #return (line3, line_break(line4,p))
        images.append(line3)
        line_break(line4,p, images)


def load_test_data(counter = 20):
    x_test = []
    y_test = []
    names = []

    test_dir2 = os.path.join(os.getcwd(), test_dir)
    test_images_list = file_list(test_dir2,test_image_type)
    #print(test_images_list)
    #print("Number of image : {}".format(len(test_images_list)))


    for idx,test_image in enumerate(test_images_list):
        #print(test_image)
        if(idx>counter-1):
            break
        nrm = line_normalization(test_image)
        pred_files_name = test_image[:-1*len(test_image_type)+1]+test_txt_type
        #print()
        ##print(pred_files_name)
        #name = xx[:-8]+".txt"

        lines = []

        line_break(nrm, line_shape[1], lines)
        #print(len(lines))

        if(len(lines)<5):
         for idx,line in enumerate(lines):
            if(line.shape==line_shape_t):
                x_test.append(line)
                names.append((pred_files_name,idx))
                #print("-----------------------------------------------", idx, pred_files_name, line.shape)
            else:
                print("Large Size Skipped")

    return np.asarray(x_test), np.asarray(y_test),names

def load_test_data2(lines_list, names, cordinates):
    x_test = []
    y_test = []
    names_return = []
    cordinates_return = []

    for idx2,test_image in enumerate(lines_list):
        #   #print(test_image)
        # if(idx2>counter-1):
        #     break
        nrm = line_normalization(test_image)
        #print(nrm.dtype)
        if(nrm.shape == (0,48)):
            print("This image will be skipped")
        else:
            try:
                pred_files_name = ""
                ##print()
                ##print(pred_files_name)
                #name = xx[:-8]+".txt"
                lines = []
                line_break(nrm, line_shape[1], lines)
                #print("number of sublines ",len(lines))
                if(len(lines)==1):
                    for line in lines:
                        if(line.shape==line_shape_t):
                            x_test.append(line)
                            names_return.append((names[idx2],-1))
                            cordinates_return.append(cordinates[idx2])
                            #print("-----------------------------------------------", idx,idx2, pred_files_name, line.shape)
                        else:
                            print("Large Size Skipped")
                elif(len(lines)<5):
                    for idx,line in enumerate(lines):
                        if(line.shape==line_shape_t):
                            x_test.append(line)
                            names_return.append((names[idx2],idx))
                            cordinates_return.append(cordinates[idx2])
                            #print("-----------------------------------------------", idx,idx2, pred_files_name, line.shape)
                        else:
                            print("Large Size Skipped")

            except:
                pass

    return np.asarray(x_test), np.asarray(y_test),names_return, cordinates_return


def get_sequence_length(x_test):
    seq_len_test = np.ones(x_test.shape[0]) * line_shape[1]
    #target_test1 = [np.asarray(i) for i in label_test]
    #target_test = sparse_tuple_from(target_test1)
    return seq_len_test


def sparse2(x):
    idx = list()
    a = 0
    b = []
    for delta, i_idx in enumerate(x[0]):
        i = i_idx[0]
        if i != a:
            idx.append(b)
            a = i
            b = list()
        b.append(delta)
    idx.append(b)
    sparse_list = []
    for k in idx:
        decoded = []
        for m in k:
            str = charset[x[1][m]]
            decoded.append(str)
        sparse_list.append(decoded)
    return sparse_list

def decode_s(indexes, spars_tensor):
    #print(len(indexes[0]), type(indexes))
    #print(indexes.shape)
    str_decoded = ''.join([charset[spars_tensor[m] - 0] for m in indexes])
    # Replacing blank label to none
    #str_decoded = str_decoded.replace(chr(ord('9') + 1), '')
    # Replacing space label to space
    #str_decoded = str_decoded.replace(chr(ord('0') - 1), ' ')
    # print("ffffffff", str_decoded)
    #print(str_decoded)
    #print(len(str_decoded))
    return str_decoded


def sparse(sparse_tensor):
    #print(len(sparse_tensor))
    #print(len(sparse_tensor[0]), len(sparse_tensor[1]), len(sparse_tensor[2]))
    # print(sparse_tensor)
    decoded_indexes = list()
    current_i = 0
    current_seq = []
    ll = []
    prev = 0
    st_0 = []
    st_1 = []
    for x,y in zip(sparse_tensor[0],sparse_tensor[1]):

        diff = x[0]-prev
        prev = x[0]
        for ii in range(diff-1):
            x_0 =  x[0] - diff + 1 + ii
            x_1 = ii
            y_0 = 0
            #print(x_0,x_1,y_0,".............................................................................")
            st_0.append(np.array([x_0, x_1]))
            st_1.append(y_0)
        #print(x[0],x[1],y)
        st_0.append(x)
        st_1.append(y)
    #for xxx,yyy in zip(st_0, st_1):
        #print(xxx,yyy)
    #print(len(st_0), len(st_1))


    for offset, i_and_index in enumerate(st_0):
        #print(offset, i_and_index, i_and_index[0], i_and_index[1])

        i = i_and_index[0]
        if i != current_i:
            decoded_indexes.append(current_seq)
            current_i = i
            current_seq = list()
        current_seq.append(offset)
        #print(current_seq)
    decoded_indexes.append(current_seq)


    #print(len(decoded_indexes))
    #print(decoded_indexes)
    #
    # print("mmmm", decoded_indexes)
    result = []
    #print(len(decoded_indexes))
    for index in decoded_indexes:
        result.append(decode_s(index, st_1))
    return result


def get_sparse(y, dtype=np.int32):
    idx = []
    yy = []
    for n, y_i in enumerate(y):
        idx.extend(zip([n] * len(y_i), range(len(y_i))))
        yy.extend(y_i)
    idx = np.asarray(idx, dtype=np.int64)
    yy = np.asarray(yy, dtype=dtype)
    dimensions = np.asarray([len(y), np.asarray(idx).max(0)[1] + 1], dtype=np.int64)
    return idx, yy, dimensions

def next_batch(batch_size, x, y):
    idx = np.arange(0 , len(x))
    np.random.shuffle(idx)
    idx = idx[:batch_size]
    x_new = [x[i] for i in idx]
    y_new = [y[i] for i in idx]
    batch_seq = [x[i].shape[0] for i in idx]
    y_new = [np.asarray(i) for i in np.asarray(y_new)]
    y_sparse = get_sparse(y_new)
    return np.asarray(x_new), y_sparse, batch_seq
#
# if __name__=="__main__":
#     x,y = load_train_data(25)
#     #print(x.shape, y.shape)
#     train_x, train_y, train_seq_len = next_batch(batch_size, x, y)
#     #print(len(train_x), train_x[0].shape)
