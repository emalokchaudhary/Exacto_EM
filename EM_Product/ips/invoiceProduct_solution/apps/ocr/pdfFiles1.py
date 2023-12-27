from bs4 import BeautifulSoup as Soup
from wand.image import Image, Color
import os, shutil, sys
import cv2
import traceback
from lseg import callOCR
from predictFunc import predClass
from autoRotatePDFPages import pdfRotate, pdfRotateList
from test import callPrediction

'''
---------------------------------------------------------------------
	 INPUT FILE ESTIMATOR & PDF TYPE DETECTOR SCRIPT
			-SS & JS
--------------------------------------------------------------------

'''

# DOC TYPES
IMAGE = 'IMAGE'
READABLE_DOC = 'TEXT'
NONREADABLE_DOC = 'SCAN'
COMBINED_DOC = 'MIXED'
OTHER_DOC = 'OTHER'

# EXTENSIONS SUPPORTED
imgExt = ['.png', '.jpg', '.jpeg', '.ppm', '.bmp']
imgMultExt = ['.tif', '.tiff']
pdfExt = ['.pdf']

# Image as noise threshold
nTH = 100


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
    outpath = os.path.join(output_path, fileName)

    command = "pdftohtml -xml -q '" + inputPath + "' '" + outpath + "'"
    os.system(command)
    dirList = os.listdir(output_path)
    xml = [f for f in dirList if f.lower().endswith(".xml")]
    xmlPath = os.path.join(output_path, xml[0])
    handler = open(xmlPath).read()
    soup = Soup(handler, 'lxml')
    textNodes = soup.findAll('text')
    imgNodes = soup.findAll('image')
    pageNodes = soup.findAll('page')
    fontNodes = soup.findAll('fontspec')

    # if len(textNodes2) > len(textNodes):
    # textNodes=textNodes2

    # if len(pageNodes)>=len(textNodes):
    # textNodes=[]

    # if blackImages(output_path):
    # return NONREADABLE_DOC,output_path,[],len(pageNodes)

    num = 0
    if (len(textNodes) > 0 or len(fontNodes) > 0) and len(imgNodes) == 0:
        return READABLE_DOC, output_path, [], len(pageNodes)
    elif (len(textNodes) == 0 and len(fontNodes) == 0) and len(imgNodes) > 0:
        return NONREADABLE_DOC, output_path, [], len(pageNodes)
    elif len(imgNodes) > 0 and len(textNodes) > 0 and len(fontNodes) == 0:
        scanList = [];
        typedList = [];
        mixedList = [];
        imgList = []
        for page in soup.findAll('page'):
            img = 0;
            txt = 0;
            num += 1
            for child in page.findChildren():
                name = child.name
                if name.lower() == 'image':
                    img += 1
                elif name.lower() == 'text':
                    txt += 1

            if img > 0 and txt == 0:
                scanList.append(num)
            elif img == 0 and txt > 0:
                typedList.append(num)
            else:
                mixedList.append(num)
        # print scanList,typedList,mixedList
        if mixedList:
            nmixed, imgList = mixedImages(output_path, mixedList)
            # print 'yes'
            if imgList:
                for pg in mixedList:
                    if pg not in nmixed:
                        typedList.append(pg)
                mixedList = nmixed
            else:
                typedList.append(mixedList)
        if len(scanList) == 0 and len(imgList) == 0:
            return READABLE_DOC, output_path, [], len(pageNodes)
        return COMBINED_DOC, output_path, [scanList, typedList, mixedList, imgList], len(pageNodes)
    elif len(imgNodes) > 0 and len(fontNodes) > 0:
        return OTHER_DOC, output_path, [], len(pageNodes)


def mixedImages(folderPath, fileName, mixedList):
    imgList = [];
    newDict = {}
    folderList = os.listdir(folderPath)
    for fyl in folderList:
        if os.path.splitext(fyl)[-1] in imgExt:
            pg = int(fyl.replace(fileName + '-', '').split('_')[0])
            if pg in mixedList:
                img = cv2.imread(os.path.join(folderPath, fyl))
                h, w = img.shape[:2]
                if h > nTH and w > nTH and h <= 2200:
                    res = predClass(img)
                    if res == 'tables':
                        print('InTABLES', fyl)
                        newDict[pg] = fyl
                        imgList.append(fyl)
                    else:
                        os.remove(os.path.join(folderPath, fyl))
                else:
                    os.remove(os.path.join(folderPath, fyl))
    newMixed = []
    for k in newDict.keys():
        newMixed.append(k)
    return newMixed, imgList


def blackImages(outputPath):
    fileList = os.listdir(outputPath)
    countW = 0;
    countB = 0
    for fyl in fileList:
        if os.path.splitext(fyl)[-1] in imgExt:
            img = cv2.imread(os.path.join(outputPath, fyl))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            sumW = cv2.countNonZero(thresh)
            h, w = thresh.shape[:2]
            pixs = h * w
            sumB = pixs - sumW
            if sumW > sumB:
                countW += 1
            else:
                countB += 1
    if countB < countW:
        return False
    return True


def pdftoimages(filePath, fileName, outputPath):
    if blackImages(outputPath):
        fileList = os.listdir(outputPath)
        for fyl in fileList:
            if os.path.splitext(fyl)[-1] in imgExt:
                os.remove(os.path.join(outputPath, fyl))
        outpath = os.path.join(outputPath, fileName)
        command = "pdfimages -png -p '" + filePath + "' '" + outpath + "'"
        os.system(command)
        fileList = os.listdir(outputPath)
        for fyl in fileList:
            if os.path.splitext(fyl)[-1] in imgExt:
                imgNum = int(fyl.replace(fileName + '-', '').split('-')[0])
                # print 'inside if', imgNum
                newfyl = fileName + '-' + str(imgNum) + '_1.png'
                os.rename(os.path.join(outputPath, fyl), os.path.join(outputPath, newfyl))

        if blackImages(outputPath):
            fileList = os.listdir(outputPath)
            for fyl in fileList:
                if os.path.splitext(fyl)[-1] in imgExt:
                    os.remove(os.path.join(outputPath, fyl))

            num = -1
            try:
                all_pages = Image(filename=filePath, resolution=300)
                for i, page in enumerate(all_pages.sequence):
                    num = i + 1
                    with Image(page) as img:
                        img.format = 'png'
                        img.background_color = Color('white')
                        img.alpha_channel = 'remove'
                        image_filename = fileName
                        image_filename = '{}-{}_1.png'.format(image_filename, i + 1)
                        image_filename = os.path.join(outputPath, image_filename)
                        img.save(filename=image_filename)
            except:
                pass


def pdftotext(filePath, fileName, folderPath):
    outFilePath = os.path.join(folderPath, fileName + ".txt")
    command = "pdftotext -layout '" + filePath + "' '" + outFilePath + "'"
    os.system(command)
    return outFilePath


def processImages(folderPath):
    imgList = []
    folderList = os.listdir(folderPath)
    for fyl in folderList:
        if os.path.splitext(fyl)[-1] in imgExt:
            img = cv2.imread(os.path.join(folderPath, fyl))
            h, w = img.shape[:2]
            if h > nTH and w > nTH:
                res = predClass(img)
                if res == 'tables':
                    print('InTABLES', fyl)
                    imgList.append(fyl)
                else:
                    os.remove(os.path.join(folderPath, fyl))
            else:
                os.remove(os.path.join(folderPath, fyl))
    return imgList


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

    varList = [];
    scanList = [];
    typedList = [];
    mixedList = [];
    imgList = []
    if extension in imgExt:
        typeDoc = IMAGE
    elif extension in imgMultExt:
        typeDoc = NONREADABLE_DOC
    elif extension in pdfExt:
        typeDoc, folderPath, varList, pgNums = pdftohtml(filePath, fileName, outputPath)
    else:
        printExtWarning(extension)
        return

    if varList:
        scanList = varList[0]
        typedList = varList[1]
        mixedList = varList[2]
        imgList = varList[3]

    if typeDoc == IMAGE:
        print(typeDoc, fileName)
        fw.write(fileName + '\t' + typeDoc + '\n')
        # ocr_inputs = callOCR(filePath, outputPath, typeDoc)
        # callPrediction(ocr_inputs, outputPath, baseName)

    elif typeDoc == NONREADABLE_DOC:
        fw.write(fileName + '\t' + typeDoc + '\n')
        pdftoimages(filePath, fileName, folderPath)
        pdfRotate(filePath, fileName, folderPath, pgNums)
        folderList = os.listdir(folderPath)
        for fyl in folderList:
            if os.path.splitext(fyl)[-1] in imgExt:
                print(typeDoc, fyl)
                filePath = os.path.join(folderPath, fyl)
                # ocr_inputs = callOCR(filePath, folderPath, typeDoc)
                # callPrediction(ocr_inputs, folderPath, fyl)
            # outFilePath = combineTextScan(folderPath,fileName,pgNums)

    elif typeDoc == READABLE_DOC:
        fw.write(fileName + '\t' + typeDoc + '\n')
        print(typeDoc, fileName)
        outFilePath = pdftotext(filePath, fileName, folderPath)
        # outFilePath is the path of the corresponding .txt file
        print('NLP to be called')
        # callNLP(outFilePath)

    elif typeDoc == COMBINED_DOC:
        fw.write(fileName + '\t' + typeDoc + '\n')
        print(typeDoc, fileName)
        from pdfsplit import splitPages
        for i in range(pgNums):
            splitPages(filePath, [slice(i, i + 1, None)])
            split_pdf_path = filePath.replace('.pdf', "-split.pdf")
            renamed_pdf_path = os.path.join(folderPath, fileName + "-" + str(i + 1) + ".pdf")
            os.rename(split_pdf_path, renamed_pdf_path)
        # outFilePath = pdftotext(filePath, fileName, folderPath)

        if typedList:
            pdftotextList(typedList, fileName, folderPath)

        if scanList:
            pdftoOCRList(scanList, fileName, folderPath)

        if mixedList:
            pdftotextList(mixedList, fileName, folderPath)
            for fyl in imgList:
                filePath = os.path.join(folderPath, fyl)
                # ocr_inputs = callOCR(filePath, folderPath, typeDoc)
                print(typeDoc, fyl)
                # callPrediction(ocr_inputs, folderPath, fyl)
            # outFilePath = combineTextMix(folderPath,fileName)
            # else:
            #	print('Only text file exists for processing.')
    elif typeDoc == OTHER_DOC:
        fw.write(fileName + '\t' + typeDoc + '\n')
        print(typeDoc, fileName)
        fileList = os.listdir(folderPath)
        for fyl in fileList:
            if os.path.splitext(fyl)[-1] in imgExt:
                os.remove(os.path.join(folderPath, fyl))
        pageList = []
        from pdfsplit import splitPages

        for i in range(pgNums):
            splitPages(filePath, [slice(i, i + 1, None)])
            split_pdf_path = filePath.replace('.pdf', "-split.pdf")
            renamed_pdf_path = os.path.join(folderPath, fileName + "-" + str(i + 1) + ".pdf")
            os.rename(split_pdf_path, renamed_pdf_path)
            pageList.append(i + 1)
        pdftotextList(pageList, fileName, folderPath)
        for pg in range(pgNums):
            line = 0
            fnm = fileName + "-" + str(pg + 1) + ".txt"
            if os.path.isfile(os.path.join(folderPath, fnm)):
                with open(os.path.join(folderPath, fnm)) as f:
                    lines = f.readlines()
                    if lines:
                        line += 1
                if line < 3:
                    os.remove(os.path.join(folderPath, fnm))
                    scanList.append(pg + 1)

        if scanList:
            pdftoOCRList(scanList, fileName, folderPath)


def pdftotextList(typedList, fileName, folderPath):
    for pg in typedList:
        fnm = fileName + "-" + str(pg)
        outFilePath = os.path.join(folderPath, fnm + ".txt")
        filePath = os.path.join(folderPath, fnm + ".pdf")
        command = "pdftotext -layout '" + filePath + "' '" + outFilePath + "'"
        os.system(command)
    return


def pdftoOCRList(scanList, fileName, folderPath):
    for pg in scanList:
        fnm = fileName + "-" + str(pg)
        outFilePath = os.path.join(folderPath, fnm + ".png")
        filePath = os.path.join(folderPath, fnm + ".pdf")
        try:
            with Image(filename=filePath, resolution=300) as img:
                img.format = 'png'
                img.background_color = Color('white')
                img.alpha_channel = 'remove'
                image_filename = outFilePath
                img.save(filename=image_filename)
            pdfRotateList(filePath, fileName, folderPath, pg, pgNums)
            # ocr_inputs = callOCR(outFilePath, folderPath, NONREADABLE_DOC)
            # callPrediction(ocr_inputs, folderPath, fnm)
        except:
            pass
    return




inputPath = './data/inputs'
outputPath = './data/outputONE'
fw = open('ONEt.xls', 'w')

if os.path.isdir(outputPath):
    shutil.rmtree(outputPath)
os.makedirs(outputPath)

samplesList = os.listdir(inputPath)
for sample in samplesList:
    print('<-------{}----------->'.format(sample))
    filePath = os.path.join(inputPath, sample)
    try:
        checkFileType(inputPath, filePath, outputPath)
    except:
        print(traceback.print_exc())

fw.close()
