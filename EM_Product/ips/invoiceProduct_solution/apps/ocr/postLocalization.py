#!/usr/bin/env python

import cv2
import math
import numpy as np
import os, shutil
import traceback
from shapely.geometry import Polygon

import matplotlib.pyplot as plt




## GLOBALS & DEFAULTS
kH = np.zeros((3, 3), np.uint8)
kV = np.zeros((3, 3), np.uint8)
kH[1, :] = 1
kV[:, 1] = 1
lTh = 10
hTh=10
wTh=8

def get_lines(lines_in):
    if cv2.__version__ < '3.0':
        return lines_in[0]
    return [l[0] for l in lines_in]


def lineHVremoval(img):
    MODULE = 'LREM_'

    sz = img.size
    h, w = img.shape[:2]
    channel = sz / (h * w)

    imgLines = img.copy()
    if channel > 1:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()
    gray = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)[1]
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(gray, 30, 150, apertureSize=3)
    imH = cv2.erode(edges, kH)
    imV = cv2.erode(edges, kV)
    imdV = cv2.dilate(imV, kH, iterations=1)
    imdH = cv2.dilate(imH, kV, iterations=1)
    blurH = cv2.GaussianBlur(imdH, (5, 5), 0)
    linesH = cv2.HoughLinesP(blurH, 1, np.pi / 180, 100, 30, 50)
    if linesH is not None:
        for x1, y1, x2, y2 in get_lines(linesH):
            if x2 != x1:
                slp = math.atan((y2 - y1) / (x2 - x1)) * 180 / np.pi
            else:
                slp = 90.0
            if slp > -10.0 and slp < 10.0:
                cv2.line(imgLines, (x1, y1), (x2, y2), (0, 255, 0), 1)
                cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 1)
                cv2.line(edges, (x1, y1), (x2, y2), (0, 0, 0), 1)
    blurV = cv2.GaussianBlur(imdV, (5, 5), 0)
    blurV = cv2.medianBlur(blurV, 9)
    linesV = cv2.HoughLinesP(blurV, 1, np.pi / 180, 80, 10, 60)
    if linesV is not None:
        for x1, y1, x2, y2 in get_lines(linesV):
            if x2 != x1:
                slp = math.atan((y2 - y1) / (x2 - x1)) * 180 / np.pi
            else:
                slp = 90.0
            if slp > 70.0 or slp < -70.0:
                cv2.line(imgLines, (x1, y1), (x2, y2), (0, 255, 0), 1)
                cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 1)
                cv2.line(edges, (x1, y1), (x2, y2), (0, 0, 0), 1)
    return (img, edges)


def cropContour(cords, c, img):
    [x, y, w, h] = cords
    cropRect = np.ones((h, w), np.uint8) * 255
    cropRectB = np.zeros((h, w), np.uint8)
    blacks = 0
    whites = 0
    for i in range(0, h):
        for j in range(0, w):
            res = cv2.pointPolygonTest(c, (j + x, i + y), False)
            if res > 0:
                cropRect[i, j] = img[i + y, j + x]
                cropRectB[i, j] = img[i + y, j + x]
            elif res == 0:
                if img[i + y, j + x] <= 200:
                    blacks += 1
                else:
                    whites += 1
    if whites < blacks:
        imc = cv2.bitwise_not(cropRectB)
    else:
        imc = cropRect
    return imc


def isNoise(img,w, h):
    aspect = h/(1.0*w)
    area = w*h
    res=0
    imc = img.copy()
    imc = cv2.medianBlur(imc, 3)
    # white = cv2.countNonZero(imc)
    black_pixels = area - np.count_nonzero(img)
    compactness = float(black_pixels) / area

    if area<=10:
        res = 2
    if h<=hTh:
        res=2
    if aspect>2 and w<=wTh:
        res=2
    if compactness<0.03:
        res=2
        #if w>wTh and w<35 and h/w>=2:
         #   res=2

    return res


def lineSmorph(imgBin,nnum,orig,height,fileLoc,debug=0):
    import ocr.post_merge as pm
    mT=200

    imgEdges = cv2.bitwise_not(imgBin.copy())

    sz = imgBin.size
    ht, wt = imgBin.shape[:2]
    channel = sz / (ht * wt)
    if channel > 1:
        imgBin1 = cv2.cvtColor(imgBin, cv2.COLOR_BGR2GRAY)
    else:
        imgBin1 = imgBin.copy()

    imgBin1 = cv2.threshold(imgBin1, mT, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    kernel = np.ones((3, 3), np.uint8)
    imdV = cv2.dilate(imgEdges, kernel,iterations=1)
    imdV = cv2.threshold(imdV, mT, 255, cv2.THRESH_BINARY)[1]
    cnts = cv2.findContours(imdV, cv2.RETR_LIST , cv2.CHAIN_APPROX_SIMPLE)[-2]

    if debug == 1:
        illu=imgBin.copy()
        cv2.drawContours(illu,cnts,-1,(0,255,0),1)
        cv2.imwrite(fileLoc+'/conts.jpg',illu)

    num = 0
    cords=[]
    height = np.array(height)
    height = np.unique(height)

    ht = height[int(height.size / 2)]
    bt_limit = int(0.6*ht)
    up_limit = int(1.2*ht)

    if debug == 1:
        print(height)
        print(up_limit)
        print(bt_limit)

    cord_dict = {}
    for c in reversed(cnts):
        x, y, w, h = cv2.boundingRect(c)

        if h < bt_limit or h > up_limit or w > int(0.3*wt):
            continue

        imc = cropContour([x, y, w, h], c, imgBin1)
        imc = cv2.threshold(imc, mT, 255, cv2.THRESH_BINARY)[1]
        resNz = isNoise(imc, w, h)
        if resNz==2:
            continue
        cords.append([num,x,y,w,h])
        cord_dict[num] = [x, y, w, h]
        # cv2.rectangle(orig, (x, y), (x + w, y + h), (255, 0, 0), 2)
        # cv2.putText(orig, str(num - nnum), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)
        num += 1

    lines_group = pm.create_line_groups(cords,int(0.4 * ht))

    fin_cords = []
    fin_num = nnum
    for line in lines_group:
        # print(line)
        line_sub = []
        for num in line:
            [x, y, w, h] = cord_dict[num]
            line_sub.append([num,x, y, w, h])
        line_sub = sorted(line_sub, key=lambda x: (x[0]))
        line_sub = pm.merge_near_contours(line_sub, int(1.5*ht))

        for [num,x, y, w, h] in line_sub:
            fin_cords.append([fin_num,x, y, w, h])
            cv2.rectangle(orig, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(orig, str(num), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)
            fin_num+=1

    if debug == 1:
        cv2.imwrite(fileLoc+'/conIm.jpg',orig)
    return fin_cords


def detect_salt_and_pepper_noise(img,filter_size=3):
    h, w = img.shape[:2]

    orig = img.copy()
    img = cv2.medianBlur(img, filter_size)

    tot = h * w
    bef = tot - cv2.countNonZero(orig)
    aft = tot - cv2.countNonZero(img)
    r = float(bef - aft) / tot

    if 0.01 <= r < 0.04:
        return img

    return orig


