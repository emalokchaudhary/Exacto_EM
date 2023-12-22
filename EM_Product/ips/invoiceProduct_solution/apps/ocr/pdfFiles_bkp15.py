from bs4 import BeautifulSoup as Soup
from wand.image import Image, Color
import os, shutil, sys
import cv2
from ocr.lseg import callOCR
from ocr.predictFunc import predClass
from ocr.autoRotatePDFPages import pdfRotate
import xml.etree.ElementTree as ET
#from xml_parser import xmlParser
#from txtTablesExtractor.TABLE_LOCALIZE import table_loc
#from txtMetaData.call import extractTxtMetaData
#from htmlMetaData.call import extractHTMLMetaData
#from htmlTableExtractor.html_sample_output import html_output
#from pdfReadableMetaData.ExtractDataFromPDF_V2 import main_function
#from pdfReadableTableExtractor.testTableSolution_v2_5_OUTPUT import callCode
#from split_pages import splitPages
#from paragraphTableExtractor.thomson import getMeasures
import subprocess
from xml.dom import minidom
from ocr.test import callPrediction
from PyPDF2 import PdfFileWriter, PdfFileReader

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
TXT_FILE = 'TXT_FILE'
HTML_FILE = 'HTML_FILE'

# EXTENSIONS SUPPORTED
imgExt = ['.png', '.jpg', '.jpeg', '.ppm', '.bmp']
imgMultExt = ['.tif', '.tiff']
pdfExt = ['.pdf']
txtExt = ['.txt']
htmlExt = ['.html']

# Image as noise threshold
nTH = 100

scannedPagesList = []

def printExtWarning(extension):
    allExt = imgExt[:]
    allExt.extend(imgMultExt[:])
    allExt.extend(pdfExt[:])
    print("Message: Document type {} is not currently supported.".format(extension))
    print("Please choose extension from - {}".format(allExt))

def pdftoimages2(filePath, fileName, outputPath):
	try:
		output_path = os.path.join(outputPath, fileName)
		if os.path.isdir(output_path):
			shutil.rmtree(output_path)
		os.makedirs(output_path)

		all_pages = Image(filename=filePath, resolution=300)
		for i, page in enumerate(all_pages.sequence):
			num = i + 1
			with Image(page) as img:
				img.format = 'png'
				img.background_color = Color('white')
				img.alpha_channel = 'remove'
				image_filename = fileName
				image_filename = '{}-{}.png'.format(image_filename, i + 1)
				image_filename = os.path.join(output_path, image_filename)
				img.save(filename=image_filename)
		return output_path
	except:
		print(traceback.print_exc())
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
    textNodes2 = soup.findAll('fontspec')

    if len(textNodes2) > len(textNodes):
        textNodes = textNodes2

    if len(pageNodes) >= len(textNodes):
        textNodes = []

        # if blackImages(output_path):
        # return NONREADABLE_DOC,output_path,[],len(pageNodes)

    if len(textNodes) > 0 and len(imgNodes) == 0:
        return READABLE_DOC, output_path, [], len(pageNodes)
    # elif len(textNodes) == 0 and len(imgNodes) > 0:
    #     return NONREADABLE_DOC, output_path, [], len(pageNodes)
    elif len(imgNodes) > 0:# and len(textNodes) > 0:
        pageCounter = 0
        non_readable = False
        for page in soup.findAll('page'):
            img = 0;
            txt = 0
            for child in page.findChildren():
                name = child.name
                if name.lower() == 'image':
                    img += 1
                elif name.lower() == 'text' or name.lower() == 'fontspec':
                    txt += 1
            if img > 0 and txt == 0:
                scannedPagesList.append(pageCounter)
                non_readable = True

            pageCounter = pageCounter + 1

        if non_readable:
            return NONREADABLE_DOC, output_path, [], len(pageNodes)
        imgList = processImages(output_path)
        if imgList:
            return COMBINED_DOC, output_path, imgList, len(pageNodes)
        else:
            return READABLE_DOC, output_path, [], len(pageNodes)


def pdftohtmlPrev(inputPath, fileName, outputPath):
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
    textNodes2 = soup.findAll('fontspec')

    if len(textNodes2) > len(textNodes):
        textNodes = textNodes2

    if len(pageNodes) >= len(textNodes):
        textNodes = []

    if blackImages(output_path):
        return NONREADABLE_DOC, output_path, [], len(pageNodes)

    if len(textNodes) > 0 and len(imgNodes) == 0:
        return READABLE_DOC, output_path, [], len(pageNodes)
    elif len(textNodes) > 0 and len(imgNodes) > 0:
        if len(imgNodes) > len(textNodes):
            return NONREADABLE_DOC, output_path, [], len(pageNodes)
        imgList = processImages(output_path)
        if imgList:
            return COMBINED_DOC, output_path, imgList, len(pageNodes)
        else:
            return READABLE_DOC, output_path, [], len(pageNodes)
    else:
        return NONREADABLE_DOC, output_path, [], len(pageNodes)


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
    outFilePath = os.path.join(folderPath, fileName + ".text")
    command = "pdftotext -layout '" + filePath + "' '" + outFilePath + "'"
    os.system(command)
    return outFilePath

def pdftotextsplit(filePath, fileName, folderPath):
    read_pdf = PdfFileReader(open(filePath, "rb"))
    number_of_pages = read_pdf.getNumPages()
    pdftxtfolder = 'pdftxt'
    outFilePath1 = os.path.join(folderPath,pdftxtfolder)
    if os.path.exists(outFilePath1):
        shutil.rmtree(outFilePath1)
    os.mkdir(outFilePath1)
    
    for pg in range(1,number_of_pages+1):
        outFilePath = os.path.join(outFilePath1, fileName)
        command = "pdftotext -layout -f {pg_num} -l {pg_num} '{fin}' '{fname}-{pg_num}.txt'".format(pg_num = pg,fin=filePath,fname = outFilePath)
        # print(command)
        os.system(command)
        
            #    return outFilePath


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

def combineScanTxts(folderPath, fileName, pgNum):
    filePath = os.path.join(folderPath, fileName + '-scan.txt')

    with open(filePath, 'a') as fw:
        for i in range(1, pgNum + 1):
            text = fileName + '-' + str(i) + '_1.txt'
            if os.path.isfile(os.path.join(folderPath, text)):
                f = open(os.path.join(folderPath, text))
                lines = f.read()
                fw.write(lines)
                fw.write('\n\n')

    return filePath


def combineTextMix(folderPath, fileName):
    filePath = os.path.join(folderPath, fileName + '-mix.txt')
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


def createBaseXMLFile(xmlFilePath, documentName):
    root = ET.Element('Document')
    ET.SubElement(root, 'DocumentName').text = documentName
    tree = ET.ElementTree(root)
    tree.write(xmlFilePath)


def startOcr(filePath,outputPath,checkpoint_path,checkpointPath,checkpointMeta,classModel,classModelDir,xmlDir):
    baseName = os.path.basename(filePath)
    extension = str((os.path.splitext(baseName)[-1]).lower())
    fileName = os.path.splitext(baseName)[0]
    phase = "phase1"
    
    if extension in imgExt:
        typeDoc = IMAGE
    elif extension in imgMultExt:
        typeDoc = NONREADABLE_DOC
    elif extension in pdfExt:
        typeDoc, folderPath, imgList, pgNums = pdftohtml(filePath, fileName, outputPath)
    elif extension in txtExt:
        typeDoc = TXT_FILE
    elif extension in htmlExt:
        typeDoc = HTML_FILE
    else:
        printExtWarning(extension)
        return

    xmlFilePath = os.path.join(xmlDir, fileName + '.xml')

    if typeDoc == TXT_FILE:
        print(typeDoc, fileName)
        
        createBaseXMLFile(xmlFilePath, fileName + extension)
        metaDataDict = extractTxtMetaData(filePath)
        xmlParser.appendTXTMetaDataXML(metaDataDict, xmlFilePath)

        tableDict = table_loc(filePath)
        xmlParser.appendTableXML(tableDict, xmlFilePath)

        paraTableDict = getMeasures(filePath, os.path.abspath('../paragraphTableExtractor/measures.txt'))
        xmlParser.appendParaTableXML(paraTableDict, xmlFilePath)

    elif typeDoc == HTML_FILE:
        print(typeDoc, fileName)

        createBaseXMLFile(xmlFilePath, fileName + extension)

        metaDataDict = extractHTMLMetaData(filePath)
        xmlParser.appendTXTMetaDataXML(metaDataDict, xmlFilePath)

        tableDictHTML = html_output(filePath)
        xmlParser.appendTableXML(tableDictHTML, xmlFilePath)

    elif typeDoc == IMAGE:
        print(typeDoc, fileName)

        ocr_inputs = callOCR(filePath, outputPath, typeDoc, 'Non')
        callPrediction(ocr_inputs, outputPath, baseName)

    # elif typeDoc == NONREADABLE_DOC:
        # print(typeDoc, fileName)
        # # outFilePath = pdftotext(filePath, fileName, folderPath)
        # # pdftotextsplit(filePath, fileName, folderPath)

        # folderPath = pdftoimages2(filePath, fileName, outputPath)
        # folderList = os.listdir(folderPath)
        # folderList.sort()
        # for fyl in folderList:
            # if os.path.splitext(fyl)[-1] in imgExt:
                # filePath = os.path.join(folderPath, fyl)
			
                # ocr_inputs = callOCR(filePath, folderPath, typeDoc, 'Non')
                # callPrediction(ocr_inputs, folderPath, fyl)

        # print(typeDoc, fileName)
        # inputpdf = PdfFileReader(open(filePath, "rb"))
        # pageCount = inputpdf.numPages

        # if (pageCount) > 2 and extension in imgMultExt:
        #     splitPages(os.path.join(outputPath, fileName), filePath)

        # typedPagesList = []
        # for page in range(pageCount):
        #     typedPagesList.append(page)
            
        # if len(scannedPagesList) > 0:
        #     pdftoimages(filePath, fileName, folderPath)
        #     pdfRotate(filePath, fileName, folderPath, pgNums)
        #     folderList = os.listdir(folderPath)
        #     for fyl in folderList:
        #         if os.path.splitext(fyl)[-1] in imgExt:
        #                 print(typeDoc, fyl)
        #                 pageNumber = int(os.path.basename(fyl).split('.')[0].split('-')[-1].split('_')[0]) - 1
        #                 if pageNumber in scannedPagesList:
        #                     filePath = os.path.join(folderPath, fyl)
        #                     ocr_inputs = callOCR(filePath, folderPath, typeDoc, 'Non')
        #                     callPrediction(ocr_inputs, folderPath, fyl)
        #     outTxtScanFilePath = combineScanTxts(folderPath, fileName, pgNums)
        return folderPath,phase+' '+typeDoc

    elif typeDoc == READABLE_DOC or typeDoc == COMBINED_DOC or typeDoc == NONREADABLE_DOC:
        print(typeDoc, fileName)
        outFilePath = pdftotext(filePath, fileName, folderPath)
        pdftotextsplit(filePath, fileName, folderPath)

        createBaseXMLFile(xmlFilePath, fileName + extension)
        return folderPath,phase+' '+typeDoc

    # elif typeDoc == COMBINED_DOC: 
        # outFilePath = pdftotext(filePath, fileName, folderPath)
        # pdftotextsplit(filePath, fileName, folderPath)
        
        # print(typeDoc, fileName)
        # if imgList:
            # for fyl in imgList:
                # filePath = os.path.join(folderPath, fyl)
                # ocr_inputs = callOCR(filePath, folderPath, typeDoc, 'Non')
                # # print(typeDoc, fyl, len(ocr_inputs))
                # # print("_______", folderPath, fyl)
                # callPrediction(ocr_inputs, folderPath, fyl)
        # outFilePath = combineTextMix(folderPath, fileName)

        # return folderPath,phase+' '+typeDoc

