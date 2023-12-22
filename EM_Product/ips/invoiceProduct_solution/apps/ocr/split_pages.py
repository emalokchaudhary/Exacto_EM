import os
import PyPDF2
import shutil
from pdfsplit import splitPages

# def Split_pages(Folder, pdf_name):
#     path = os.path.join(Folder,pdf_name)
#     reader = pyPdf.PdfFileReader(open(path, mode='rb' ))
#     n = reader.getNumPages()
#     #print(n)
#
#     new_folder=os.path.join(path.split('.')[0])
#     if os.path.exists(new_folder):
#             shutil.rmtree(new_folder, ignore_errors=True)
#     os.mkdir(new_folder)
#
#     for  i in range(n):
#         splitPages(path, [slice(i,i+1 , None)])
#         split_pdf_path=new_folder+"-split.pdf"
#         renamed_pdf=os.path.join(new_folder,pdf_name.split('.')[0])+"-Page"+str(i+1)+".pdf"
#         os.rename(split_pdf_path,renamed_pdf)


from PyPDF2 import PdfFileWriter, PdfFileReader

def splitPages(outFolder, pdfPath):
    inputpdf = PdfFileReader(open(pdfPath, "rb"))

    for i in xrange(inputpdf.numPages):
        output = PdfFileWriter()
        output.addPage(inputpdf.getPage(i))

        outPdfPath = os.path.join(outFolder, os.path.basename(pdfPath).split('.')[0] + '-' + str(i+1) + '.pdf')

        with open(outPdfPath, "wb") as outputStream:
            output.write(outputStream)
