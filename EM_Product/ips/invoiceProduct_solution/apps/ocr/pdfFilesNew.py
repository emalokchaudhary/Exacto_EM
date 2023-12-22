from bs4 import BeautifulSoup as Soup
from wand.image import Image, Color
import os, shutil, sys
import cv2
import traceback
from lseg import callOCR
from predictFunc import predClass
from autoRotatePDFPages import pdfRotate, pdfRotateList
import xml.etree.ElementTree as ET
from xml_parser import xmlParser
from txtTablesExtractor.TABLE_LOCALIZE import table_loc
from txtMetaData.call import extractTxtMetaData
from htmlMetaData.call import extractHTMLMetaData
from htmlTableExtractor.html_sample_output import html_output
from pdfReadableMetaData.ExtractDataFromPDF_V5 import main_function
from pdfReadableTableExtractor.testTableSolution_v2_11UE_OUTPUT import createTable
from split_pages import splitPages as splitpagesCustom
from paragraphTableExtractor.thomson import getMeasures
from paraTableExtHTML.thomson_nltk_5 import getMeasures as getMeasuresHTML
import shutil
from ratingDefinitions.ratingDef import findRating
from metaDataTypedMultiPage.MetadataFrmText import extractContent
from companyReportingDate.thomson_2 import getCompany_date
from ocrTableExtractor.Thomson_table4 import Extract_Table_OCR
from fullyScannedTableExtractor.Thomson_OCR_table import Extract_Table_OCR as Extract_Table_OCR_FS
import subprocess
from xml.dom import minidom
from test import callPrediction
import glob
from pyPdf import PdfFileWriter, PdfFileReader

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
OTHER_DOC = 'OTHER'

# EXTENSIONS SUPPORTED
imgExt = ['.png', '.jpg', '.jpeg', '.ppm', '.bmp']
imgMultExt = ['.tif', '.tiff']
pdfExt = ['.pdf']
txtExt = ['.txt']
htmlExt = ['.html']

# Image as noise threshold
nTH = 100
rotFlag=True

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


    num = 0
    if (len(textNodes) > 0 or len(fontNodes) > 0) and len(imgNodes) == 0:
        return READABLE_DOC, output_path, [[],[],[],[]], len(pageNodes)
    elif (len(textNodes) == 0 and len(fontNodes) == 0) and len(imgNodes) > 0:
        return NONREADABLE_DOC, output_path, [[],[],[],[]], len(pageNodes)
    elif len(imgNodes) > 0 and len(textNodes) > 0:
        scanList = []
        typedList = []
        mixedList = []
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
                elif name.lower() == 'fontspec':
                    txt += 1

            if img > 0 and txt == 0:
                scanList.append(num)
            elif img == 0 and txt > 0:
                typedList.append(num)
            else:
                mixedList.append(num)
        # print scanList,typedList,mixedList
        if mixedList:
            nmixed, imgList = mixedImages(output_path, fileName, mixedList)
            # print 'yes'
            if imgList:
                for pg in mixedList:
                    if pg not in nmixed:
                        typedList.append(pg)
                mixedList = nmixed
            else:
                typedList.extend(mixedList)
                mixedList=[]
        if len(scanList) == 0 and len(imgList) == 0:
            return READABLE_DOC, output_path, [[],[],[],[]], len(pageNodes)
        return COMBINED_DOC, output_path, [scanList, typedList, mixedList, imgList], len(pageNodes)
    elif len(imgNodes) > 0 and len(fontNodes) > 0 and len(textNodes) == 0:
        return OTHER_DOC, output_path, [[],[],[],[]], len(pageNodes)


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
                if h > nTH and w > nTH and h <= 1600:
                    res = predClass(img)
                    if res == 'tables':
                        print  'InTABLES', fyl
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
    global rotFlag
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
                rotFlag=False
            except:
                pass

def pdfImage(filePath, fileName, outputPath):
    fileList = os.listdir(outputPath)
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
    except:
        outpath = os.path.join(outputPath, fileName)
        command = "pdfimages -png -p '" + filePath + "' '" + outpath + "'"
        os.system(command)


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
                    print  'InTABLES', fyl
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


def createBaseXMLFile(xmlFilePath, documentName):
    root = ET.Element('Document')
    ET.SubElement(root, 'DocumentName').text = documentName
    tree = ET.ElementTree(root)
    tree.write(xmlFilePath)


def combineTextFiles(filePaths, resultFilePath):
    fw = open(resultFilePath, 'a')
    for file in filePaths:
        f = open(file)
        lines = f.read()
        fw.write(lines)
        fw.write('\n\n')
    fw.close()

    return resultFilePath

#Change
def callAllTypedmodules(xmlFilePath, fileName, extension, typedFolder, folderPath, filePath):
    # Call all modules related to typed
    createBaseXMLFile(xmlFilePath, fileName + extension)

    # Amit solution
    metaDataDict = main_function(typedFolder)
    xmlParser.appendPDFMetaDataXML(metaDataDict, xmlFilePath)

    # # Call Jassi Solution
    # ratingsDict = findRating(filePath)
    # xmlParser.appendRatingDefXML(ratingsDict)


def callAllTypedmodulesM(xmlFilePath, fileName, extension, typedFolder, folderPath, filePath):
    # Call all modules related to typed
    createBaseXMLFile(xmlFilePath, fileName + extension)

    # Amit solution
    metaDataDict = main_function(typedFolder)
    xmlParser.appendPDFMetaDataXML(metaDataDict, xmlFilePath)

    # Generate XML file for text for Ankit and Manmita solution
    outXMLFilePath = os.path.join(os.path.dirname(folderPath),
                                  fileName, os.path.basename(filePath).split('.')[0] + '.xml')
    pdfTableDict = createTable(outXMLFilePath)
    xmlParser.appendTableXML(pdfTableDict, xmlFilePath)

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

def checkFileType(filePath, outputPath, xmlDir):
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
    elif extension in txtExt:
        typeDoc = TXT_FILE
    elif extension in htmlExt:
        typeDoc = HTML_FILE
    else:
        printExtWarning(extension)
        return

    xmlFilePath = os.path.join(xmlDir, fileName + '.xml')

    if varList:
        scanList = varList[0]
        typedList = varList[1]
        mixedList = varList[2]
        imgList = varList[3]

    if typeDoc == TXT_FILE:
        print("Call modules for txt files")
        # Call all the modules which work on txt files

        # Create a XML file for particular document
        # Add <Document> tag into file
        createBaseXMLFile(xmlFilePath, fileName + extension)

        # Call Shre txt module
        metaDataDict = extractTxtMetaData(filePath)
        xmlParser.appendTXTMetaDataXML(metaDataDict, xmlFilePath)

        # Call Shahruk module
        paraTableDict = getMeasures(filePath, os.path.abspath('paragraphTableExtractor/measures.txt'))
        xmlParser.appendParaTableXML(paraTableDict, xmlFilePath)

        # Call Arti txt module
        tableDict = table_loc(filePath)
        xmlParser.appendTableXML(tableDict, xmlFilePath)

        # p = subprocess.Popen(["xmllint", "-format", xmlFilePath, ">", xmlFilePath], stdout=subprocess.PIPE)

        # with open('myfile', 'w') as outfile:
        #     subprocess.call(["xmllint", "-format", xmlFilePath, ">", xmlFilePath], stdout=outfile)

        # command = "xmllint -format " + xmlFilePath + " > " + xmlFilePath
        # os.system(command)

        return metaDataDict

    elif typeDoc == HTML_FILE:
        print(".html file detected...")

        # Call all the modules which work on html files
        createBaseXMLFile(xmlFilePath, fileName + extension)

        # Call Shre txt module
        metaDataDict = extractHTMLMetaData(filePath)
        xmlParser.appendTXTMetaDataXML(metaDataDict, xmlFilePath)

        # Call Abhinivesh Solution
        tableDict = getMeasuresHTML(filePath, os.path.abspath('paraTableExtHTML/measures_html.txt'))
        xmlParser.appendHTMLParaTableXML(tableDict, xmlFilePath)

        # Call Aarti module for html table
        # Change
        tableDictHTML = html_output(filePath)
        xmlParser.appendTableXML(tableDictHTML, xmlFilePath, isHTML=True)

        return metaDataDict

    elif typeDoc == IMAGE:
        print(typeDoc, fileName)
        # fw.write(fileName + '\t' + typeDoc + '\n')
        ocr_inputs = callOCR(filePath, outputPath, typeDoc)
        callPrediction(ocr_inputs, outputPath, baseName)

        # Sharuk Solution
        comRepDict = getCompany_date(folderPath, 'companyReportingDate/company_name.txt')
        xmlParser.appendCompanyNameReportingDate(comRepDict, xmlFilePath)

        # Raushan Solution
        tableDict = Extract_Table_OCR_FS(folderPath)
        xmlParser.appendTableXML(tableDict, xmlFilePath)

        return {}

    elif typeDoc == NONREADABLE_DOC:
        print('Fully Scanned Document')
        # fw.write(fileName + '\t' + typeDoc + '\n')
        # pdftoimages(filePath, fileName, folderPath)
        # if rotFlag:
        #     pdfRotate(filePath, fileName, folderPath, pgNums)
        pdfImage(filePath, fileName, folderPath)
        folderList = os.listdir(folderPath)
        for fyl in folderList:
            if os.path.splitext(fyl)[-1] in imgExt:
                # print(typeDoc, fyl)
                filePath = os.path.join(folderPath, fyl)
                ocr_inputs = callOCR(filePath, folderPath, typeDoc)
                callPrediction(ocr_inputs, folderPath, fyl)
                # outFilePath = combineTextScan(folderPath, fileName, pgNums)

        createBaseXMLFile(xmlFilePath, fileName + extension)

        # Sharuk Solution
        comRepDict = getCompany_date(folderPath, 'companyReportingDate/company_name.txt')
        xmlParser.appendCompanyNameReportingDate(comRepDict, xmlFilePath)

        # Raushan Solution
        tableDict = Extract_Table_OCR_FS(folderPath)
        xmlParser.appendTableXML(tableDict, xmlFilePath)

        return {}

    elif typeDoc == READABLE_DOC:
        # fw.write(fileName + '\t' + typeDoc + '\n')
        print(typeDoc, fileName)
        outFilePath = pdftotext(filePath, fileName, folderPath)

        shutil.copy(filePath, folderPath)

        createBaseXMLFile(xmlFilePath, fileName + extension)

        # Change
        # Text file for Amit meta data
        # Only for One Page One Company and NS(filing)
        os.makedirs(os.path.join(folderPath, fileName + "_split"))
        splitFolder = os.path.join(folderPath, fileName + "_split")

        splitpagesCustom(splitFolder, filePath)

        for pdf in glob.glob(os.path.join(splitFolder, '*.pdf')):
            pdftotext(pdf, os.path.basename(pdf).split('.')[0], splitFolder)

        # Check number of pages
        fileList = glob.glob(os.path.join(splitFolder, "*"))
        if len(fileList)/2 == 1 or 'NS' in splitFolder or 'Download' in splitFolder:
            metaDataDict = main_function(splitFolder)
            # print(metaDataDict)
            xmlParser.appendPDFMetaDataXML(metaDataDict, xmlFilePath)
        elif len(fileList) / 2 > 1:
            metaDataDict = extractContent(splitFolder)
            xmlParser.appendMetaTypedMultiXML(metaDataDict, xmlFilePath)

        # Generate XML file for text for Ankit
        outXMLFilePath = os.path.join(os.path.dirname(outFilePath),
                                      os.path.basename(outFilePath).split('.')[0] + '.xml')
        pdfTableDict = createTable(outXMLFilePath)
        # print(len(pdfTableDict))
        xmlParser.appendTableXML(pdfTableDict, xmlFilePath)

        # Call Jassi Solution
        ratingsDict = findRating(filePath)
        xmlParser.appendRatingDefXML(ratingsDict, xmlFilePath)

        return metaDataDict

    elif typeDoc == COMBINED_DOC:
        # fw.write(fileName + '\t' + typeDoc + '\n')
        filePathTemp  = filePath
        print(typeDoc, fileName)
        from pdfsplit import splitPages
        blockPrint()
        for i in range(pgNums):
            splitPages(filePath, [slice(i, i + 1, None)])
            split_pdf_path = filePath.replace('.pdf', "-split.pdf")
            renamed_pdf_path = os.path.join(folderPath, fileName + "-" + str(i + 1) + ".pdf")
            os.rename(split_pdf_path, renamed_pdf_path)
        # outFilePath = pdftotext(filePath, fileName, folderPath)
        enablePrint()
        if typedList:
            pdftotextList(typedList, fileName, folderPath)

        if scanList:
            pdftoOCRList(scanList, filePath, fileName, folderPath, pgNums)

        if mixedList:
            pdftotextList(mixedList, fileName, folderPath)
            for fyl in imgList:
                filePath = os.path.join(folderPath, fyl)
                ocr_inputs = callOCR(filePath, folderPath, typeDoc)
                # print(typeDoc, fyl)
                callPrediction(ocr_inputs, folderPath, fyl)
                # outFilePath = combineTextMix(folderPath, fileName)
                # else:
                #	print('Only text file exists for processing.')

        os.makedirs(os.path.join(folderPath, fileName + "_typed"))
        typedFolder = os.path.join(folderPath, fileName + "_typed")

        for pageNumber in typedList:
            shutil.copy(os.path.join(folderPath, fileName + "-" + str(pageNumber) + ".txt"), typedFolder)
            shutil.copy(os.path.join(folderPath, fileName + "-" + str(pageNumber) + ".pdf"), typedFolder)

        os.makedirs(os.path.join(folderPath, fileName + "_scanned"))
        scannedFolder = os.path.join(folderPath, fileName + "_scanned")
        for pageNumber in scanList:
            shutil.copy(os.path.join(folderPath, fileName + "-" + str(pageNumber) + ".txt"), scannedFolder)
            shutil.copy(os.path.join(folderPath, fileName + "-" + str(pageNumber) + ".pdf"), scannedFolder)
            shutil.copy(os.path.join(folderPath, fileName + "-" + str(pageNumber) + "_info.txt"), scannedFolder)

        for pageNumber in mixedList:
            shutil.copy(os.path.join(folderPath, fileName + "-" + str(pageNumber) + ".txt"), typedFolder)
            shutil.copy(os.path.join(folderPath, fileName + "-" + str(pageNumber) + ".pdf"), typedFolder)
            pageImagesList = glob.glob(os.path.join(folderPath, fileName + "-" + str(pageNumber) + "_*.png"))
            for image in pageImagesList:
                txtFile = os.path.join(os.path.dirname(image), os.path.basename(image).split('.')[0] + '.txt')
                infoFile = os.path.join(os.path.dirname(image), os.path.basename(image).split('.')[0] + '_info.txt')
                shutil.copy(image, scannedFolder)
                shutil.copy(txtFile, scannedFolder)
                shutil.copy(infoFile, scannedFolder)

        # combineTextFilePath = combineTextFiles(typedTXTFilesList, os.path.abspath(os.path.join(folderPath, fileName + "_typed_combined.txt")))

        # #Change
        # # Generate XML file for text for Ankit and Manmita solution
        createBaseXMLFile(xmlFilePath, fileName + extension)

        try:
            # Text file for Amit meta data
            # Only for One Page One Company and NS(filing)
            os.makedirs(os.path.join(folderPath, fileName + "_split"))
            splitFolder = os.path.join(folderPath, fileName + "_split")

            splitpagesCustom(splitFolder, filePath)
            for pdf in glob.glob(os.path.join(splitFolder, '*.pdf')):
                pdftotext(pdf, os.path.basename(pdf).split('.')[0], splitFolder)
            # Check number of pages
            fileList = glob.glob(os.path.join(splitFolder, "*"))
            if len(fileList) / 2 == 1 or 'NS' in splitFolder or 'Download' in splitFolder:
                metaDataDict = main_function(splitFolder)
                xmlParser.appendPDFMetaDataXML(metaDataDict, xmlFilePath)
            elif len(fileList) / 2 > 1:
                metaDataDict = extractContent(splitFolder)
                xmlParser.appendMetaTypedMultiXML(metaDataDict, xmlFilePath)
        except:
            # Check number of pages
            fileList = glob.glob(os.path.join(typedFolder, "*"))
            if len(fileList) / 2 == 1 or 'NS' in typedFolder or 'Download' in splitFolder:
                metaDataDict = main_function(typedFolder)
                xmlParser.appendPDFMetaDataXML(metaDataDict, xmlFilePath)
            elif len(fileList) / 2 > 1:
                metaDataDict = extractContent(typedFolder)
                xmlParser.appendMetaTypedMultiXML(metaDataDict, xmlFilePath)

        # Ankit Solution
        outXMLFilePath = os.path.join(os.path.dirname(folderPath),
                                      fileName, os.path.basename(filePathTemp).split('.')[0] + '.xml')
        pdfTableDict = createTable(outXMLFilePath)
        xmlParser.appendTableXML(pdfTableDict, xmlFilePath)

        # # Sharuk Solution (Only for fully scanned)
        # comRepDict = getCompany_date(folderPath, 'companyReportingDate/company_name.txt')
        # xmlParser.appendCompanyNameReportingDate(comRepDict, xmlFilePath)

        # Raushan Solution
        os.makedirs(os.path.join(folderPath, fileName + "_info_files"))
        infoFolder = os.path.join(folderPath, fileName + "_info_files")

        infoFileList = glob.glob(os.path.join(folderPath, '*_info.txt'))
        for file in infoFileList:
            shutil.copy(file ,infoFolder)

        ocrTableDict = Extract_Table_OCR(infoFolder, outXMLFilePath)
        xmlParser.appendTableXML(ocrTableDict, xmlFilePath)
        # Raushan Ends

        # Jassi Solution
        ratingsDict = findRating(filePathTemp)
        xmlParser.appendRatingDefXML(ratingsDict, xmlFilePath)

        # Check number of pages
        # fileList = glob.glob(os.path.join(typedFolder, "*"))
        # if len(fileList) / 2 > 1:
        #     # metaDataDict = extractContent(typedFolder)

        return {}

    elif typeDoc == OTHER_DOC:
        filePathTemp = filePath
        # fw.write(fileName + '\t' + typeDoc + '\n')
        print(typeDoc, fileName)
        fileList = os.listdir(folderPath)
        for fyl in fileList:
            if os.path.splitext(fyl)[-1] in imgExt:
                os.remove(os.path.join(folderPath, fyl))
        pageList = []
        from pdfsplit import splitPages
        blockPrint()
        for i in range(pgNums):
            splitPages(filePath, [slice(i, i + 1, None)])
            split_pdf_path = filePath.replace('.pdf', "-split.pdf")
            renamed_pdf_path = os.path.join(folderPath, fileName + "-" + str(i + 1) + ".pdf")
            os.rename(split_pdf_path, renamed_pdf_path)
            pageList.append(i + 1)
        enablePrint()
        pdftotextList(pageList, fileName, folderPath)
        for pg in range(pgNums):
            line = 0
            fnm = fileName + "-" + str(pg + 1) + ".txt"
            if os.path.isfile(os.path.join(folderPath, fnm)):
                with open(os.path.join(folderPath, fnm)) as f:
                    lines = f.readlines()
                    # if lines:
                    #     line += 1
                if len(lines) < 3:
                    os.remove(os.path.join(folderPath, fnm))
                    scanList.append(pg + 1)

        if scanList:
            pdftoOCRList(scanList, filePath, fileName, folderPath, pgNums)

        if len(scanList) == 0:
            typedList = pageList[:]
        else:
            typedList = []
            for pageNumber in pageList:
                if pageNumber in scanList:
                    pass
                else:
                    typedList.append(pageNumber)

        # typedTXTFilesList = []
        # for pageNumber in typedList:
        #     typedTXTFilesList.append(os.path.join(folderPath, fileName + "-" + str(pageNumber) + ".txt"))
        #
        # combineTextFilePath = combineTextFiles(typedTXTFilesList, os.path.abspath(os.path.join(folderPath, fileName + "_typed_combined.txt")))

        os.makedirs(os.path.join(folderPath, fileName + "_typed"))
        typedFolder = os.path.join(folderPath, fileName + "_typed")

        for pageNumber in typedList:
            shutil.copy(os.path.join(folderPath, fileName + "-" + str(pageNumber) + ".txt"), typedFolder)
            shutil.copy(os.path.join(folderPath, fileName + "-" + str(pageNumber) + ".pdf"), typedFolder)

        os.makedirs(os.path.join(folderPath, fileName + "_scanned"))
        scannedFolder = os.path.join(folderPath, fileName + "_scanned")
        for pageNumber in scanList:
            shutil.copy(os.path.join(folderPath, fileName + "-" + str(pageNumber) + ".txt"), scannedFolder)
            shutil.copy(os.path.join(folderPath, fileName + "-" + str(pageNumber) + ".pdf"), scannedFolder)
            shutil.copy(os.path.join(folderPath, fileName + "-" + str(pageNumber) + "_info.txt"), scannedFolder)

        # #Change
        # # Generate XML file for text for Ankitsolution
        createBaseXMLFile(xmlFilePath, fileName + extension)

        try:
            # Text file for Amit meta data
            # Only for One Page One Company and NS(filing)
            os.makedirs(os.path.join(folderPath, fileName + "_split"))
            splitFolder = os.path.join(folderPath, fileName + "_split")

            splitpagesCustom(splitFolder, filePath)
            for pdf in glob.glob(os.path.join(splitFolder, '*.pdf')):
                pdftotext(pdf, os.path.basename(pdf).split('.')[0], splitFolder)
            # Check number of pages
            fileList = glob.glob(os.path.join(splitFolder, "*"))
            if len(fileList) / 2 == 1 or 'NS' in splitFolder or 'Download' in splitFolder:
                metaDataDict = main_function(splitFolder)
                xmlParser.appendPDFMetaDataXML(metaDataDict, xmlFilePath)
            elif len(fileList) / 2 > 1:
                metaDataDict = extractContent(splitFolder)
                xmlParser.appendMetaTypedMultiXML(metaDataDict, xmlFilePath)
        except:
            # Check number of pages
            fileList = glob.glob(os.path.join(typedFolder, "*"))
            if len(fileList) / 2 == 1 or 'NS' in typedFolder or 'Download' in splitFolder:
                metaDataDict = main_function(typedFolder)
                xmlParser.appendPDFMetaDataXML(metaDataDict, xmlFilePath)
            elif len(fileList) / 2 > 1:
                metaDataDict = extractContent(typedFolder)
                xmlParser.appendMetaTypedMultiXML(metaDataDict, xmlFilePath)


        # Ankit Solution
        outXMLFilePath = os.path.join(os.path.dirname(folderPath),
                                      fileName, os.path.basename(filePathTemp).split('.')[0] + '.xml')
        pdfTableDict = createTable(outXMLFilePath)
        xmlParser.appendTableXML(pdfTableDict, xmlFilePath)

        # # Sharuk Solution (Only for fully scanned)
        # comRepDict = getCompany_date(folderPath, 'companyReportingDate/company_name.txt')
        # xmlParser.appendCompanyNameReportingDate(comRepDict, xmlFilePath)

        # Raushan Solution
        os.makedirs(os.path.join(folderPath, fileName + "_info_files"))
        infoFolder = os.path.join(folderPath, fileName + "_info_files")

        infoFileList = glob.glob(os.path.join(folderPath, '*_info.txt'))
        for file in infoFileList:
            shutil.copy(file, infoFolder)

        ocrTableDict = Extract_Table_OCR(infoFolder, outXMLFilePath)
        xmlParser.appendTableXML(ocrTableDict, xmlFilePath)
        # Raushan Ends

        # Jassi Solution
        ratingsDict = findRating(filePathTemp)
        xmlParser.appendRatingDefXML(ratingsDict, xmlFilePath)

        return {}

def pdftotextList(typedList, fileName, folderPath):
    for pg in typedList:
        fnm = fileName + "-" + str(pg)
        outFilePath = os.path.join(folderPath, fnm + ".txt")
        filePath = os.path.join(folderPath, fnm + ".pdf")
        command = "pdftotext -layout '" + filePath + "' '" + outFilePath + "'"
        os.system(command)
    return


def pdftoOCRList(scanList, fileLoc, fileName, folderPath, pgNums):
    fileList=os.listdir(folderPath)
    for fyl in fileList:
        if os.path.splitext(fyl)[-1] in imgExt:
            imgpgNum = int(fyl.replace(fileName+"-","").split("_")[0])
            if imgpgNum in scanList:
                os.remove(os.path.join(folderPath,fyl))

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
            #pdfRotateList(fileLoc, fileName, folderPath, pg, pgNums)
            ocr_inputs = callOCR(outFilePath, folderPath, NONREADABLE_DOC)
            callPrediction(ocr_inputs, folderPath, fnm+'.png')
        except:
            pass
    return


inputPath = ''
outputPath = ''
xmlDir = ''
# fw = open('ONEt.xls', 'w')

def processDocument(inputPathPara, outputPathPara, xmlDirPara):
    inputPath = outputPathPara
    outputPath = outputPathPara
    xmlDir = xmlDirPara

    if os.path.isdir(outputPathPara):
        shutil.rmtree(outputPathPara)
    os.makedirs(outputPathPara)

    #if os.path.isdir(xmlDirPara):
     #   shutil.rmtree(xmlDirPara)
    #os.makedirs(xmlDirPara)

    samplesList = os.listdir(inputPathPara)

    for sample in samplesList:
        print('<-------{}----------->'.format(sample))
        filePath = os.path.join(inputPathPara, sample)
        metaData = {}
        try:
            metaData = checkFileType(filePath, outputPathPara, xmlDirPara)
        except:
            print traceback.print_exc()

        # metaData = checkFileType(filePath, outputPathPara, xmlDirPara)
    # fw.close()

    return metaData

#processDocument('./data/inputs', './data/outputs', './data/inputs')
