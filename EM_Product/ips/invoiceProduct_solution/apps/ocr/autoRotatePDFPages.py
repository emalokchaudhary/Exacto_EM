import os,shutil
import cv2
import numpy as np
import math
import traceback
from scipy import ndimage

imgExt = ['.png','.jpg','.jpeg','.ppm','.bmp']
kernel = np.ones((5, 5), np.uint8)

def pdfRotate(fileLoc,fileNm,outLoc,pgNums):
	try:
		#cmd="pdfinfo '" + fileLoc + "' | grep -i 'Pages:'"
		#pgs=os.popen(cmd).read()
		#pgs=pgs.replace('\n','')
		#pgs=pgs.replace(' ','')
		#l=pgs.split(':')[-1]
		#print 'l',l,pgNums
		l=pgNums
		cmd="pdfinfo -f 1 -l " + str(l) + " '" + fileLoc + "' | grep -i 'Page'"
		pgsRot=os.popen(cmd).read()
		
		pn=1
		pgDict={}
		for line in pgsRot.split('\n'):
			sline= line.split(' ')
			if 'rot:' in sline:
				rot=sline[-1]
				pgDict[pn]=rot
				pn+=1
		if len(pgDict)==0:
			return
		outFiles=os.listdir(outLoc)
		for imgF in outFiles:
			ext = str((os.path.splitext(imgF)[-1]).lower())
			if ext in imgExt:
				#print imgF,'--->'
				imgNum=int(imgF.replace(fileNm+'-','').split('_')[0])
				imgLoc=os.path.join(outLoc,imgF) 
				
				if pgDict[imgNum]=='270' or pgDict[imgNum]=='90':
					autoRot90(imgLoc,imgF,pgDict[imgNum])
	except:
		print('ERR:AUROT:::',traceback.print_exc())
		pass

def pdfRotateList(fileLoc,fileNm,outLoc,pg,pgNums):
	try:
		l=pgNums
		cmd="pdfinfo -f 1 -l " + str(l) + " '" + fileLoc + "' | grep -i 'Page'"
		pgsRot=os.popen(cmd).read()
		
		pn=1
		pgDict={}
		for line in pgsRot.split('\n'):
			sline= line.split(' ')
			if 'rot:' in sline:
				rot=sline[-1]
				pgDict[pn]=rot
				pn+=1
		if len(pgDict)==0:
			return
	
		imgF=fileNm+"-"+str(pg)+".png"
		imgLoc=os.path.join(outLoc,imgF) 
			
		if pgDict[pg]=='270' or pgDict[pg]=='90':
			autoRot90(imgLoc,imgF,pgDict[pg])
	except:
		print('ERR:AUROT:::',traceback.print_exc())
		pass

def autoRot90(imNm,imgName,pdfRot):
	img = cv2.imread(imNm)
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	gray = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)[1]
	gray = cv2.GaussianBlur(gray, (3, 3), 0)
	gray = cv2.GaussianBlur(gray, (3, 3), 0)
	edges = cv2.Canny(gray, 30, 150, apertureSize=3)
    
#	imgBin1 = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]	
	imdV = cv2.dilate(edges, kernel)
	imdV = cv2.threshold(imdV, 0, 255, cv2.THRESH_BINARY)[1]
	cnts = cv2.findContours(imdV, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
	#illu=img.copy()
#	cv2.drawContours(illu,cnts,-1,(0,255,0),1)

	countH=0;countW=0
	for c in reversed(cnts):
		x, y, w, h = cv2.boundingRect(c)

		if h<=20 or w<=20:
			continue
	#	cv2.rectangle(illu,(x,y),(x+w,y+h),(0,0,255),1)
		if h >w+15:
			countH+=1
		else:
			countW+=1

	angle=0
	if countH+5>countW:
		#print 'Rot needed'
		if pdfRot=='270':
			angle=90
		else:
			angle=-90
		h,w = img.shape[:2]
		#center = (w // 2, h // 2)
		#M = cv2.getRotationMatrix2D(center, angle, 1.0)
		#rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
		rotated=ndimage.rotate(img,angle)
		cv2.imwrite(imNm,rotated)
