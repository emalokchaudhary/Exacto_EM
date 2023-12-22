# from bs4 import BeautifulSoup as Soup
from wand.image import Image, Color
import cv2
import os, shutil
import sys, time
import traceback
from lseg import callOCR
from test import callPrediction

# import prediction as pred

'''
-----------------------------------------------------------------------------
	 INPUT FILE ESTIMATOR & PDF TYPE DETECTOR SCRIPT FOR NOVARTIS DEMO
			-SS & JS
-----------------------------------------------------------------------------

'''

# DOC TYPES
IMAGE = 'IMAGE'
READABLE_DOC = 'TEXT'
NONREADABLE_DOC = 'SCAN'
COMBINED_DOC = 'MIXED'
OTHER_DOC = 'OTHER'

# EXTENSIONS SUPPORTED
imgExt = ['.png', '.jpg', '.jpeg', '.ppm', '.bmp', '.tif']
imgMultExt = ['.tiff']
pdfExt = ['.pdf']


def printExtWarning(extension):
    allExt = imgExt[:]
    allExt.extend(imgMultExt[:])
    allExt.extend(pdfExt[:])
    print("Message: Document type {} is not currently supported.".format(extension))
    print("Please choose extension from - {}".format(allExt))


def pdftohtml(inputPath, fileName, outputPath):
    output_path = os.path.join(outputPath, fileName)
    if os.path.isdir(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path)

    return NONREADABLE_DOC, output_path, [[], [], [], []], 0


def pdfImage(filePath, fileName, outputPath):
    fileList = os.listdir(outputPath)
    firstPath = ''
    for fyl in fileList:
        if os.path.splitext(fyl)[-1] in imgExt:
            os.remove(os.path.join(outputPath, fyl))
    try:
        all_pages = Image(filename=filePath, resolution=300)
        for i, page in enumerate(all_pages.sequence):
            with Image(page) as img:
                img.format = 'png'
                img.background_color = Color('white')
                img.alpha_channel = 'remove'
                image_filename = fileName
                image_filename = '{}-{}_1.png'.format(image_filename, i + 1)
                image_filename = os.path.join(outputPath, image_filename)
                img.save(filename=image_filename)
            if (i == 0):
                firstPath = image_filename
        return firstPath
    except:
        print('Problem in pdf, images not generated.')
        pass


def combineTextScan(folderPath, fileName, pgNum):
    filePath = os.path.join(folderPath, fileName + '.txt')
    fw = open(filePath, 'a')
    for i in range(1, pgNum + 1):
        text = fileName + '-' + str(i) + '_1.txt'
        if os.path.isfile(os.path.join(folderPath, text)):
            f = open(os.path.join(folderPath, text))
            lines = f.read()
            fw.write(lines)
            fw.write('\n\n')
    fw.close()
    return filePath


def combineTextMix(folderPath, fileName):
    filePath = os.path.join(folderPath, fileName + '.txt')
    fw = open(filePath, 'a')
    fileList = os.listdir(folderPath)
    for fyl in fileList:
        if os.path.splitext(fyl)[-1] in imgExt:
            text = fyl[0:-4] + '.txt'
            # print text
            if os.path.isfile(os.path.join(folderPath, text)):
                f = open(os.path.join(folderPath, text))
                lines = f.read()
                fw.write(lines)
                fw.write('\n\n')
    fw.close()
    return filePath


def checkFileType(inputPath, filePath, outputPath):
    baseName = os.path.basename(filePath)
    extension = str((os.path.splitext(baseName)[-1]).lower())
    fileName = os.path.splitext(baseName)[0]

    if extension in imgExt:
        typeDoc = IMAGE
    elif extension in imgMultExt:
        typeDoc = NONREADABLE_DOC
    elif extension in pdfExt:
        typeDoc, folderPath, varList, pgNums = pdftohtml(filePath, fileName, outputPath)
    else:
        printExtWarning(extension)
        return

    if typeDoc == IMAGE:
        print(typeDoc, fileName)
        #	fw.write(fileName+'\t'+typeDoc+'\n')

        ocr_inputs = callOCR(filePath, outputPath, typeDoc, 'Non')
        callPrediction(ocr_inputs, outputPath, baseName)

    elif typeDoc == NONREADABLE_DOC:
        # print(typeDoc,fileName)
        firstPath = pdfImage(filePath, fileName, folderPath)

        folderList = os.listdir(folderPath)
        for fyl in folderList:
            if os.path.splitext(fyl)[-1] in imgExt:
                print(typeDoc, fyl)
                filePath = os.path.join(folderPath, fyl)

                ocr_inputs = callOCR(filePath, folderPath, typeDoc, 'Non')

                callPrediction(ocr_inputs, folderPath, fyl)
            # outFilePath = combineTextScan(folderPath,fileName,pgNums)
    return


inputPath = './data/inputs'
outputPath = './data/outputs'

if os.path.isdir(outputPath):
    shutil.rmtree(outputPath)
os.makedirs(outputPath)

samplesList = os.listdir(inputPath)
for sample in samplesList:
    print('<-------{}----------->'.format(sample))
    filePath = os.path.join(inputPath, sample)
    try:
        stng = checkFileType(inputPath, filePath, outputPath)
        break
    except:
        pass
    # print traceback.print_exc()
