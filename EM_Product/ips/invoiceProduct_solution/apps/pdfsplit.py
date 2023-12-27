# -*- coding: utf-8 -*-

import re, os, sys
from PyPDF4 import PdfFileWriter, PdfFileReader
import traceback
from collections import OrderedDict 
import shutil

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)
    
    
def pdftotext(filename,filepath,outfolder):

    read_pdf = PdfFileReader(open(filepath, "rb"),overwriteWarnings=True)
    page_count = read_pdf.getNumPages()

    text_files = []
    for pg in range(1,page_count+1):
        outFilePath = os.path.join(outfolder, filename)
        text_files.append(filename+'-'+str(pg)+'.txt')
        command = "pdftotext -layout -f {0} -l {0} '{1}' '{2}-{0}.txt'".format(pg,filepath,outFilePath)
        #print(command)
        os.system(command)
    return text_files
    

def doc_list(flist,tmpdir):
    
    pg_list,ptr = [],0
    pattern = "Page\s+\d+\s+of\s+\d+"
    
    while ptr < len(flist):
        pat_flag = False
        filepath = os.path.join(tmpdir,flist[ptr])
        
        with open(filepath, "r") as f:
            for line in f:
                search_obj = re.search(pattern,line)
                
                if search_obj:
                    pages = int(re.split("\s+",search_obj.group())[-1])
                    pg_list.append(pages)
                    ptr += pages
                    pat_flag = True
                    break

        if not pat_flag:
            ptr += 1
    return pg_list
    
    
def pdf_splitting(folderpath,filepath,doc_name,page_list):
    ptr,newfile_list = 0,[]
    inputpdf = PdfFileReader(open(filepath, "rb"),strict=False)
    page_num = inputpdf.getNumPages() 
    
    for doc_len in page_list:
        output = PdfFileWriter()
        
        for page in range(doc_len):
            output.addPage(inputpdf.getPage(ptr))
            ptr += 1

        file_name = doc_name+'_Part_'+str(ptr)+'.pdf'
        with open(os.path.join(folderpath,file_name), "wb") as outputStream:
            output.write(outputStream)
        newfile_list.append(file_name)
        
    return newfile_list


def main_split(folder_path,exception_folder):
    odict = OrderedDict([])
    documents = [i for i in os.listdir(folder_path) if i.lower().endswith('.pdf')]
    
    for document in documents:
        document_path = os.path.join(folder_path, document)
        doc_name,_ = os.path.splitext(os.path.basename(document_path))
        print(document_path)
        print(doc_name)
        
        tmpdir = os.path.join(folder_path,'tmp')
        os.makedirs(tmpdir)

        try:
            flist = pdftotext(doc_name,document_path,tmpdir)
            
        except:
            shutil.copy(document_path, os.path.join(exception_folder,document)) 
            print("Exception in pdftotext",document)
            print(traceback.print_exc())
            
        try:
            page_list = doc_list(flist,tmpdir)
            
        except:
            shutil.copy(document_path, os.path.join(exception_folder,document))
            print("Exception in generating list of pages",document)
            print(traceback.print_exc())
            

        new_pdf_list = []
        try:
            new_pdf_list = pdf_splitting(folder_path,document_path,doc_name,page_list)
            shutil.move(document_path,os.path.join(tmpdir,document))
            
        except:
            new_pdf_list.append(document)
            shutil.copy(document_path, os.path.join(exception_folder,document))
            print("Exception in splitting pdfs",document)
            print(traceback.print_exc())
            pass
        
        shutil.rmtree(tmpdir)
        odict[document] = new_pdf_list
        
        

    
    return odict
