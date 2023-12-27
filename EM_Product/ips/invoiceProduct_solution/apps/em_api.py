from ExtractCustomFields.CGI_nomination_headers_1 import Nomination_header_field, file_data
from ExtractCustomFields.CGI_Clssification import read_file,CGI_classifcation
from ExtractCustomFields.CGI_Nomination_Table_main import  * #main_call
from ExtractCustomFields.CGI_Nomiantion_final_table_exxon import Quality_line_items
from ExtractCustomFields.CGI_Insertion import Nomination_Insertion, cgi_invoice_db_insertion, cgi_quality_db_insertion, cgi_quantity_db_insertion
from ExtractCustomFields.CGI_error_insertion import Error_insert

from ExtractCustomFields.CGI_Invoice_headers import cgi_invoice_headers_extraction
from ExtractCustomFields.CGI_Invoice_lineitems import cgi_lineitem_main

from ExtractCustomFields.CGI_Quality_headers import cgi_quality_headers_extraction
from ExtractCustomFields.CGI_qlty_lineitem import cgi_qlty_lineitem_main

from ExtractCustomFields.CGI_Quantity_headers import cgi_quantity_headers_extraction

import os,sys
sys.path.insert(0,"../")
import shutil
import uuid
import time,datetime
from apps.configs import ExactoSettings
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

global esett
esett = ExactoSettings()

# folder_path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_api_Input/CGI/CHEM-US/305468"



def output_path(folder_path):
    li=folder_path.split("/")
    # print(li)
    output_dir = os.path.join(esett.OUTPUT_DIR, li[-3])
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    output_dir = os.path.join(esett.OUTPUT_DIR, li[-3], li[-2])
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    output_dir = os.path.join(esett.OUTPUT_DIR, li[-3], li[-2],li[-1])
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    # print(output_dir)
    return output_dir
# output_path(folder_path)

def pdftotext(filePath, fileName,Outpath):
    # out_path= Outpath(outpath, folder_path)
    outFilePath = os.path.join(Outpath, fileName.replace(".pdf", ".text"))
    print(outFilePath)
    # outFilePath = os.path.join(folderPath, fileName + ".text")
    command = "pdftotext -layout '" + filePath + "' '" + outFilePath + "'"
    os.system(command)
    return outFilePath


# def CGI_extraction(output_dir):
#     text_folder=os.listdir(output_dir)
#     for txt_file in text_folder:
#         # print("adddddddd",txt_file)
#         txt_file=os.path.join(output_dir,txt_file)
#         print(txt_file)
#         try:
#             Nom_header_data=Nomination_field(txt_file)
#             print("Complete header fields",Nom_header_data)
#         except:
#             print("Not Nomination file",txt_file)
    
# print(Outpath(outpath, folder_path))
def CGI_process(folder_path,error_dir,dest_dir):
    error_dict={}
    
    error_dict["StartTime"]= datetime.datetime.now()
    error_dict["ExtractionStatus"] = 0
    folder=os.listdir(folder_path)
    
    for fyl in folder:
        
        if fyl.lower().endswith('.pdf'):
            file_path = os.path.join(folder_path, fyl)
            output_dir=output_path(folder_path)
            txt_file = pdftotext(file_path, fyl, output_dir)
            
            uuid_doc = str(uuid.uuid4().hex[:8])
            error_dict["doc_uuid"] = uuid_doc
            error_dict["VendorName"] = folder_path.split("/")[-3]
            error_dict["Region"] = folder_path.split("/")[-2]
            error_dict["InvNo"] = folder_path.split("/")[-1]
            error_dict["FileName"] = file_path.split("/")[-1]
            
            document_type=CGI_classifcation(read_file(txt_file))
            print("aaaaaaaaaaaaaaaaaaaaaaa",document_type )
            if document_type == "Nomination":
                error_dict["FileType"] = document_type
                try:
                    Nom_header_data = Nomination_header_field(file_data(txt_file), uuid_doc)
                    Nom_parcel_item = main_call(read_file(txt_file))
                    # print("YOgeshssssssssYOgeshssssssssss",Nom_parcel_item)
                    Nom_line_item = Quality_line_items(file_data(txt_file))
                except :
                    pass
                if Nom_header_data and Nom_parcel_item:
                    
                    data_insert=Nomination_Insertion(Nom_header_data, Nom_parcel_item, Nom_line_item,error_dict)
                    dest_folder = os.path.join(dest_dir, error_dict["InvNo"])
                    if not os.path.exists(dest_folder):
                        os.mkdir(dest_folder)

                    shutil.move(file_path, dest_folder)
                    
                else:
                    error_dict["ExtractionStatus"] = 0
                    error_insert=Error_insert(error_dict)
                    error_folder = os.path.join(error_dir, error_dict["InvNo"])
                    if not os.path.exists(error_folder):
                        os.mkdir(error_folder)

                    shutil.move(file_path, error_folder)

            elif document_type=="Invoice":
                error_dict["FileType"] = document_type
                try:
                    inv_header_data = cgi_invoice_headers_extraction(read_file(txt_file),uuid_doc)
                    inv_line_item = cgi_lineitem_main(txt_file)
                except:
                    pass
                if inv_header_data :
                    
                    inv_insert=cgi_invoice_db_insertion(inv_header_data,inv_line_item,error_dict)
                    dest_folder = os.path.join(dest_dir, error_dict["InvNo"])
                    if not os.path.exists(dest_folder):
                        os.mkdir(dest_folder)

                    shutil.move(file_path, dest_folder)

                else:
                    error_dict["ExtractionStatus"] = 0
                    error_insert=Error_insert(error_dict)

                    error_folder = os.path.join(error_dir, error_dict["InvNo"])
                    if not os.path.exists(error_folder):
                        os.mkdir(error_folder)

                    shutil.move(file_path, error_folder)

            elif document_type == "Quality":
                error_dict["FileType"] = document_type
                try:
                    qlty_header_data = cgi_quality_headers_extraction(read_file(txt_file), uuid_doc)
                    qlty_line_item = cgi_qlty_lineitem_main(txt_file)
                except:
                    pass
                if qlty_header_data:
                    qlty_insert = cgi_quality_db_insertion(qlty_header_data, qlty_line_item, error_dict)
                    dest_folder = os.path.join(dest_dir, error_dict["InvNo"])
                    if not os.path.exists(dest_folder):
                        os.mkdir(dest_folder)

                    shutil.move(file_path, dest_folder)
                else:
                    error_dict["ExtractionStatus"] = 0
                    error_insert = Error_insert(error_dict)
                    error_folder = os.path.join(error_dir, error_dict["InvNo"])
                    if not os.path.exists(error_folder):
                        os.mkdir(error_folder)

                    shutil.move(file_path, error_folder)

            elif document_type == "Quantity":
                error_dict["FileType"] = document_type
                try:
                    qnty_header_data = cgi_quantity_headers_extraction(read_file(txt_file), uuid_doc)
                except:
                    pass
                # qlty_line_item = cgi_qlty_lineitem_main(txt_file)
                if qnty_header_data:
                    qlty_insert = cgi_quantity_db_insertion(qnty_header_data, error_dict)
                    dest_folder = os.path.join(dest_dir, error_dict["InvNo"])
                    if not os.path.exists(dest_folder):
                        os.mkdir(dest_folder)

                    shutil.move(file_path, dest_folder)
                else:
                    error_dict["ExtractionStatus"] = 0
                    error_insert = Error_insert(error_dict)
                    error_folder = os.path.join(error_dir, error_dict["InvNo"])
                    if not os.path.exists(error_folder):
                        os.mkdir(error_folder)

                    shutil.move(file_path, error_folder)
            # elif document_type == "Not classified":
            #     print("Extra documention ")
            else:
                # pass
                print("Extra documention ")
                error_dict["ExtractionStatus"] = 0
                error_dict["FileType"] = "Other documents"
                error_insert = Error_insert(error_dict)
                error_folder = os.path.join(error_dir, error_dict["InvNo"])
                if not os.path.exists(error_folder):
                    os.mkdir(error_folder)
                
                shutil.move(file_path, error_folder)
                # pass


    # return output_dir  
# CGI_process(folder_path)

def process_folders(source_dir, dest_dir, error_dir, batch_size):
    # get a list of all the folders in the source directory
    folders = os.listdir(source_dir)
    # process a batch of folders
    num_folders = min(batch_size, len(folders))
    for folder in folders[:num_folders]:
        # create the full path to the folder
        folder_path = os.path.join(source_dir, folder)
        print(folder_path)
        # check if the path is a directory
        if os.path.isdir(folder_path):
            print(folder_path)
            # process the folder
            if "CGI" in folder_path:
                proccessed_folder = os.path.join(dest_dir, folder)
                non_proccessed_folder = os.path.join(error_dir, folder)
                if os.path.exists(proccessed_folder):
                    shutil.rmtree(proccessed_folder)
                if os.path.exists(non_proccessed_folder):
                    shutil.rmtree(non_proccessed_folder)
                # print(folder_path)
                a=CGI_process(folder_path,error_dir,dest_dir)
                dest_folder = os.path.join(source_dir, folder)
                if os.path.exists(dest_folder):
                    shutil.rmtree(dest_folder)
                # shutil.move(folder_path, dest_folder)
                # print("YOgesh")
            else :
                print("Not code for camin vendor")
                error_folder = os.path.join(error_dir, folder)
                if os.path.exists(error_folder):
                    shutil.rmtree(error_folder)
                shutil.move(folder_path, error_folder)
            # else:
            #     print("errooorroorror")
            
def main():
    # specify the source and destination directories
    # source_dirs
    # dest_dirs

    source_dirs = [esett.INPUT_CGI_CHEM, esett.INPUT_CGI_US,
                   esett.INPUT_CAMIN_CHEM, esett.INPUT_CAMIN_US, esett.INPUT_CAMIN_INT]
    dest_dirs = [esett.PROCESSED_CGI_CHEM_PATH, esett.PROCESSED_CGI_US_PATH,
                 esett.PROCESSED_CAMIN_CHEM_PATH, esett.PROCESSED_CAMIN_US_PATH, esett.PROCESSED_CAMIN_INT_PATH]
    error_dirs = [esett.ERROR_CGI_CHEM_PATH, esett.ERROR_CGI_US_PATH,
                  esett.ERROR_CAMIN_CHEM_PATH, esett.ERROR_CAMIN_US_PATH, esett.ERROR_CAMIN_INT_PATH]
    # dest_dir = "/path/to/destination/directory"

    # process a batch of folders less than or equal to 10
    batch_size = 5

    # keep running the loop
    while True:
        # create a thread for each source directory
        threads = []
        for it in range(len(source_dirs)):
            thread = Thread(target=process_folders, args=(source_dirs[it], dest_dirs[it], error_dirs[it], batch_size))
            thread.start()
            threads.append(thread)

        # wait for all threads to finish
        for thread in threads:
            thread.join()

        # wait for some time before checking for new folders
        # time.sleep(60) # wait for 60 seconds before checking for new folders again

if __name__ == '__main__':
    main()
