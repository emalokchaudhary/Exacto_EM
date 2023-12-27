import os
import glob
import PIL
import numpy
from numpy import (transpose, amax, amin, array, bitwise_and, clip, dtype, mean, minimum,nan, sin, sqrt)
from pylab import array, amax, vstack, zeros
from scipy.ndimage import filters,interpolation
from . import line_process
from ocr.config import charset

code2char = {}
char2code = {}
for code,char in enumerate(charset):
    code2char[code] = char
    char2code[char] = code

def size():
    return len(list(code2char.keys()))
def encode(s):
    dflt = char2code[""]
    #print(type(s[0]),type(dflt))
    return [char2code.get(c,dflt) for c in s]
def decode(l):
    s = [code2char.get(c,"") for c in l]
    return s


def read_image_gray(fname,pageno=0):
    if type(fname)==tuple: fname,pageno = fname
    assert pageno==0
    pil = PIL.Image.open(fname)
    a = pil2array(pil)
    #print(a.shape,a.dtype, a.ndim)
    if a.dtype==dtype('uint8'):
        a = a/255.0
    if a.dtype==dtype('int8'):
        a = a/127.0
    elif a.dtype==dtype('uint16'):
        a = a/65536.0
    elif a.dtype==dtype('int16'):
        a = a/32767.0
    elif isfloatarray(a):
        pass
    else:
        pass
    if a.ndim==3:
        a = mean(a,2)
    #print(a.shape)
    return a


def read_seg_lines_list(seg_array):
    # if type(fname)==tuple: fname,pageno = fname
    # assert pageno==0
    #pil = PIL.Image.open(seg_array)
    #a = pil2array(pil)
    #print(seg_array)
    a = seg_array
    #print(a.shape,a.dtype, a.ndim)
    if a.dtype==dtype('uint8'):
        a = a/255.0
    if a.dtype==dtype('int8'):
        a = a/127.0
    elif a.dtype==dtype('uint16'):
        a = a/65536.0
    elif a.dtype==dtype('int16'):
        a = a/32767.0
    elif isfloatarray(a):
        pass
    else:
        pass
    if a.ndim==3:
        a = mean(a,2)
    # xx,yy,zz = a.shape
    # a = a.reshape(xx,yy)
    #print(a.shape)
    return a

def isfloatarray(a):
    return a.dtype in [dtype('f'),dtype('float32'),dtype('float64')]

def pil2array(im,alpha=0):
    if im.mode=="L":
        a = numpy.fromstring(im.tobytes(),'B')
        a.shape = im.size[1],im.size[0]
        return a
    if im.mode=="RGB":
        a = numpy.fromstring(im.tobytes(),'B')
        a.shape = im.size[1],im.size[0],3
        return a
    if im.mode=="RGBA":
        a = numpy.fromstring(im.tobytes(),'B')
        a.shape = im.size[1],im.size[0],4
        if not alpha: a = a[:,:,:3]
        return a
    return pil2array(im.convert("L"))

def dewarp(self,img,cval=0,dtype=dtype('f')):
    assert img.shape==self.shape
    h,w = img.shape
    hpadding = self.r
    padded = vstack([cval*ones((hpadding,w)),img,cval*ones((hpadding,w))])
    center = self.center + hpadding
    dewarped = [padded[center[i]-self.r:center[i]+self.r,i] for i in range(w)]
    dewarped = array(dewarped,dtype=dtype).T
    return dewarped

def normalize(self,img,order=1,dtype=dtype('f'),cval=0):
    dewarped = self.dewarp(img,cval=cval,dtype=dtype)
    h,w = dewarped.shape
    scaled = scale_to_h(dewarped,self.target_height,order=order,dtype=dtype,cval=cval)
    return scaled

def prepare_line(line,pad=16):
    ##print(type(line), line.shape)
    #if(line.shape != (48,0))
    line = line * 1.0/amax(line)
    line = amax(line)-line
    line = line.T
    if pad>0:
        w = line.shape[1]
        line = vstack([zeros((pad,w)),line,zeros((pad,w))])
    #print("hh", line.shape)
    return line


def line_normalization(filename):
    #line = read_image_gray(filename)
    line = read_seg_lines_list(filename)
    #print(line.shape)
    #line = transpose(line)
    #print(line.shape)
    mv = line_process.CenterNormalizer()
    temp = amax(line)-line
    #print(amax(temp))
    if(amax(temp) == 0.0):
        return array([1,1])
    temp = temp*1.0/amax(temp)
    mv.measure(temp)
    line = mv.normalize(line,cval=amax(line))
    #print("here", line.shape)
    if(line.shape==(48,0)):
        return transpose(line)
    else:
        #print("Now here")
        line = prepare_line(line,16)
        return line
