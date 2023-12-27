 
import os
import sys
import datetime
import traceback
import time
sys.path.insert(0, "../")  ## USAGE OF THIS CODE LINE FOR IMPORTING FILES FOR GETTING CORRECT DIRECTORY PATH 
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

import uuid
import shutil
from apps.configs import ExactoSettings
# from ExtractCustomFields.db_connection import connect_db
from ExtractCustomFields.CGI_Modules.CGI_nomination_headers_1 import Nomination_header_field, file_data
from ExtractCustomFields.Doc_Classification import read_file, CGI_classifcation, Camin_classifcation, Saybolt_classifcation
from ExtractCustomFields.CGI_Modules.CGI_Nomination_Table_main import *  # main_call
from ExtractCustomFields.CGI_Modules.CGI_Nomiantion_final_table_exxon import Quality_line_items
from ExtractCustomFields.CGI_Insertion import toscan_blob_sp,Nomination_Insertion, cgi_invoice_db_insertion, cgi_quality_db_insertion, cgi_quantity_db_insertion, camin_qnt_and_quality_db_insertion,api_procedure_byuuid_main_2
from ExtractCustomFields.db_insertion_toscana import api_tos_nomination_main, api_db_toscana_inv_main_call,api_tos_inspection_quality_main, api_tos_inspection_quantity_main
from ExtractCustomFields.CGI_error_insertion import Error_insert, Error_update,toscana_Error_update

from ExtractCustomFields.CGI_Modules.CGI_Invoice_headers import cgi_invoice_headers_extraction
from ExtractCustomFields.CGI_Modules.CGI_Invoice_lineitems import cgi_lineitem_main
from ExtractCustomFields.CGI_Modules.CGI_Quality_headers import cgi_quality_headers_extraction
from ExtractCustomFields.CGI_Modules.CGI_qlty_lineitem import cgi_qlty_lineitem_main
from ExtractCustomFields.CGI_Modules.CGI_Quantity_headers import cgi_quantity_headers_extraction

from ExtractCustomFields.Camin_Modules.camin_invoice_headers import camin_invoice_headers_extraction
from ExtractCustomFields.Camin_Modules.Camin_Inv_lineitem import camin_lineitem_main
from ExtractCustomFields.Camin_Modules.Camin_Inspection_header import camin_quantity_header,camin_quality_header
from ExtractCustomFields.Camin_Modules.Camin_quantity_lineitem import Camin_inspection_lineitem_main
from ExtractCustomFields.Camin_Modules.Camin_quality_lineitem import Camin_Ins_quality_li_main

from ExtractCustomFields.Saybolt_Modules.saybolt_invoice_headers import saybolt_invoice_headers_extraction
from ExtractCustomFields.Saybolt_Modules.saybolt_invoice_lineitems import saybolt_lineitem_main
from ExtractCustomFields.Saybolt_Modules.saybolt_inspection_headers import saybolt_quality_header, saybolt_quantity_header
from ExtractCustomFields.Saybolt_Modules.saybolt_inspection_quality_lineitems import saybolt_qlty_lineitem_main
from ExtractCustomFields.Saybolt_Modules.saybolt_inspection_quantity_lineitems import FinalQuantityLineItems
from ExtractCustomFields.blob import blob_main_call
from ExtractCustomFields.EM_logging import logger
global esett
esett = ExactoSettings()

######################### STORED PROCEDURE NAMES ###############
pronom='HCL_Nomination_Data_Trans'
proinv='HCL_Invoice_Data_Trans'
proqnt='HCL_Insepection_Data_Trans'
proqlt='HCL_Inspection_Data_Quality_Trans'
toscan_sp_name_for_blob='SP_SIGMADocuments_INS'

##### PROCEDURE FUNCTION
def stored_procedure_calling_toscana(InvNO,global_doc_nom_list,global_doc_inv_list,gloabl_doc_qnt_list,global_doc_qlty_list):
    Inv_tos_Row_Id='NA'
    try:
        print("#"*20,' GOING TO PUSH DATA FROM EXACTO STAGING TABLE TO TOSCANA WITH FILE NO. ',InvNO,'#'*20)
        logger.info(f'{"#"*20} GOING TO PUSH DATA FROM EXACTO STAGING TABLE TO TOSCANA WITH FILE NO. InvNO {"#"*20}')
        if(global_doc_nom_list):
            if(global_doc_nom_list[0][2]==6):
                res,rr=api_procedure_byuuid_main_2(pronom,global_doc_nom_list[0][0])
                # print(res)
                if(res==1):
                    global_doc_nom_list[0][2]=9
                    toscana_Error_update(global_doc_nom_list[0][0],9)
                    if(global_doc_inv_list[0][2]==6):
                        resinv,Inv_tos_Row_Id=api_procedure_byuuid_main_2(proinv,global_doc_inv_list[0][0])
                        if(resinv==1):
                            global_doc_inv_list[0][2]=9
                            toscana_Error_update(global_doc_inv_list[0][0],9)
                            for  j in gloabl_doc_qnt_list:
                                if(j[2]==6):
                                    j[2]=9
                                    resqnt,rr=api_procedure_byuuid_main_2(proqnt,j[0])
                                    if(resqnt==1):
                                        toscana_Error_update(j[0],9)
                                    else:
                                        toscana_Error_update(j[0],7)
                            for k in global_doc_qlty_list:
                                if(k[2]==6):
                                    k[2]=9
                                    resqlty,rr=api_procedure_byuuid_main_2(proqnt,k[0])
                                    if(resqlty==1):
                                        toscana_Error_update(k[0],9)
                                    else:
                                        toscana_Error_update(k[0],7)

                        else:
                            toscana_Error_update(global_doc_inv_list[0][0],7)
                else:
                    toscana_Error_update(global_doc_nom_list[0][0],7)

    except Exception as e:
        logger.info("ERROR IN SP CALLING ")
        logger.exception(e)
        print('Erroc during sp calling')
    # print("THIS IS THE ROWID WHICH IS BEING USED FOR DOCKER BLOB ",Inv_tos_Row_Id)
    logger.info(f'THIS IS THE ROWID WHICH IS BEING USED FOR DOCKER BLOB : {Inv_tos_Row_Id}')
    return Inv_tos_Row_Id,global_doc_nom_list,global_doc_inv_list,gloabl_doc_qnt_list,global_doc_qlty_list
##############################################################################################
def status_maintain_acc_to_blob(list_of_success_doc,list_of_failure_doc,Nested_list_of_success_doc):
    if(list_of_success_doc):
        for i in Nested_list_of_success_doc:
            if(i[1] in list_of_success_doc):
               toscana_Error_update(i[0],11)
    if(list_of_failure_doc):
        for i in Nested_list_of_success_doc:
            if(i[1] in list_of_failure_doc):
                toscana_Error_update(i[0],10)
def maintain_error_code_blob_sp(m,Nested_list_of_success_doc,error_code):
    for i in Nested_list_of_success_doc:
        if(i[1] == m):
            toscana_Error_update(i[0],error_code)



###########################################################################################
def movement_of_file_after_toscandb_status(error_dir,InvNO,global_doc_nom_list,global_doc_inv_list,gloabl_doc_qnt_list,global_doc_qlty_list):
    ### warning plese check the folder structure name for future movement of file ####
    try:
        try:
            if(global_doc_nom_list):
                if(global_doc_nom_list[0][2]!=9):
                    print(global_doc_nom_list[0][1])
                    global_doc_nom_list[0][1]=re.sub(r'EM_api_Input',"EM_Processed",global_doc_nom_list[0][1])
                    MovetoUnprocessed(error_dir,InvNO,global_doc_nom_list[0][1])
        except:
            pass
        try:
            if(global_doc_inv_list):
                if(global_doc_inv_list[0][2]!=9):
                    global_doc_inv_list[0][1]=re.sub(r'EM_api_Input',"EM_Processed",global_doc_inv_list[0][1])
                    MovetoUnprocessed(error_dir,InvNO,global_doc_inv_list[0][1])
        except:
            pass
        try:
            for  j in gloabl_doc_qnt_list:
                if(j[2]!=9):
                    j[1]=re.sub(r'EM_api_Input',"EM_Processed",j[1]) 
                    MovetoUnprocessed(error_dir,InvNO,j[1])
        except:
            print('SEEMS EITHER FILE IS ALREDY SHIFTED OR ERROR IN PATH')
        try:
            for  k in global_doc_qlty_list:
                if(k[2]!=9):
                    k[1]=re.sub(r'EM_api_Input',"EM_Processed",k[1])
                    MovetoUnprocessed(error_dir,InvNO,k[1])
        except:
            print('SEEMS EITHER FILE IS ALREDY SHIFTED OR ERROR IN PATH')
    except:
        print('ERROR DURING DOC. MOVEMENT')

##################################################################################################
############# AZURE BLOB CODE
def blob_call_api(Inv_tos_Row_Id,global_doc_nom_list,global_doc_inv_list,gloabl_doc_qnt_list,global_doc_qlty_list):
    list_of_success_doc=[]
    list_of_failure_doc=[]
    Nested_list_of_success_doc=[]
    try:
        l=[]
        try:
            if(global_doc_nom_list):
                if(global_doc_nom_list[0][2]==9):
                    print(global_doc_nom_list[0][1])
                    global_doc_nom_list[0][1]=re.sub(r'EM_api_Input',"EM_Processed",global_doc_nom_list[0][1])
                    l.append(global_doc_nom_list[0][1])
                    temp=[]
                    temp.append(global_doc_nom_list[0][0])
                    temp.append(global_doc_nom_list[0][1])
                    Nested_list_of_success_doc.append(temp)
        except:
            pass
        try:
            if(global_doc_inv_list):
                if(global_doc_inv_list[0][2]==9):
                    global_doc_inv_list[0][1]=re.sub(r'EM_api_Input',"EM_Processed",global_doc_inv_list[0][1])
                    l.append(global_doc_inv_list[0][1])
                    temp=[]
                    temp.append(global_doc_inv_list[0][0])
                    temp.append(global_doc_inv_list[0][1])
                    Nested_list_of_success_doc.append(temp)
        except:
            pass
        try:
            for  j in gloabl_doc_qnt_list:
                if(j[2]==9):
                    j[1]=re.sub(r'EM_api_Input',"EM_Processed",j[1]) 
                    l.append(j[1])
                    temp=[]
                    temp.append(j[0])
                    temp.append(j[1])
                    Nested_list_of_success_doc.append(temp)
        except:
            print('SEEMS EITHER FILE IS ALREADY SHIFTED OR ERROR IN PATH')
        try:
            for  k in global_doc_qlty_list:
                if(k[2]==9):
                    k[1]=re.sub(r'EM_api_Input',"EM_Processed",k[1])
                    l.append(k[1])
                    temp=[]
                    temp.append(k[0])
                    temp.append(k[1])
                    Nested_list_of_success_doc.append(temp)
        except:
            print('SEEMS EITHER FILE IS ALREADY SHIFTED OR ERROR IN PATH')

        print('HERE ARE ALL FILE PATH WHICH HAS MOVE TO BLOB',l)
        try:
            list_of_success_doc,list_of_failure_doc=blob_main_call(l,Inv_tos_Row_Id)
            
        except:

            print('ERROR DURING BLOB FILE MOVEMENT')
        try:
            status_maintain_acc_to_blob(list_of_success_doc,list_of_failure_doc,Nested_list_of_success_doc)
        except:
            print('ERROR DURING STATUS MAINTAIN OF BLOB')
        try:
            if(list_of_success_doc):
                for m in list_of_success_doc: 
                    file_name=m.split("/")[-1]
                    try:
                        error_code=toscan_blob_sp(toscan_sp_name_for_blob,file_name,Inv_tos_Row_Id)
                        try:
                            maintain_error_code_blob_sp(m,Nested_list_of_success_doc,error_code)
                        except:
                            print('ERROR DURING ERROR CODE MAINTIAN OF SP BLOB CONTAINER')
                    except:
                        print(' ERROR DURING TOSCAN BLOB SP')
        except:
            print('ERROR DURING BLOB SP TOSCANA')
    except:
        print('ERROR DURING DOC. MOVEMENT TO BLOB')
   


def output_path(folder_path):
    li = folder_path.split("/")
    
    output_dir = os.path.join(esett.OUTPUT_DIR, li[-3])
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    output_dir = os.path.join(esett.OUTPUT_DIR, li[-3], li[-2])
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    output_dir = os.path.join(esett.OUTPUT_DIR, li[-3], li[-2], li[-1])
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    return output_dir



def pdftotext(filePath, fileName, Outpath):
    # out_path= Outpath(outpath, folder_path)#add try except
    # if re.search(r'pdf',re.IGNORECASE)
        outFilePath = os.path.join(Outpath, fileName.replace(".pdf", ".text"))
        if re.search(r"PDF$",outFilePath):
            outFilePath=re.sub(r"\.PDF$",".text",outFilePath)

        # print(outFilePath)
        # outFilePath = os.path.join(folderPath, fileName + ".text")
        command = "pdftotext -layout '" + filePath + "' '" + outFilePath + "'"
        os.system(command)
        return outFilePath

#add try except and logging
def MovetoProcessed(dest_dir, InvNO, file_path):
    dest_folder = os.path.join(dest_dir, InvNO)
    if not os.path.exists(dest_folder):
        os.mkdir(dest_folder)

    shutil.move(file_path, dest_folder)

def MovetoUnprocessed(error_dir,InvNO, file_path):
    error_folder = os.path.join(error_dir, InvNO)
    if not os.path.exists(error_folder):
        os.mkdir(error_folder)

    shutil.move(file_path, error_folder)

def qnt_hd_li_merge(qnty_header_data,qnty_line_item):
    qnty_data=[]
    temp=qnty_header_data
    if qnty_line_item !={}:
        for i in qnty_line_item:
            d={}
            d=temp
            d['NominatedQuantity'] = qnty_line_item[i]
            d['UnitOfMeasure']=i
            qnty_data.append(d.copy()) # copy() for removing memory refrence 
    
    # for j in qnty_data:
    #     print("\n",j)
         
    return qnty_data 
        
def saybolt_qnt_li(qnty_header_data,qnty_line_item):
    if len(qnty_header_data)==len(qnty_line_item):
        qnty_li=[]
        for j in qnty_header_data:
            for z in qnty_line_item :
                if j.get("ProductName")==z.get("ProductName"):
                    z.pop("ProductName")                
                    
                    qnty_data =qnt_hd_li_merge(j,z)
                    for i in qnty_data:
                        qnty_li.append(i)
    else:
        qnty_li=[]
        print("Errorr in Quantity megre data ")
    # print(qnty_li)
    return qnty_li
      
################################################## CGI #########################################################################        

def CGI_process(folder_path, error_dir, dest_dir):
    logger.info("CGI DOCUMENT PROCESSING START...")
    # log_dict={}
    error_dict = {}
    # global_uuid=
    error_dict["StartTime"] = datetime.datetime.now()
    error_dict["ExtractionStatus"] = 0
    folder = os.listdir(folder_path)
    # global_nom_hd={}
    # global_nom_parcel={}
    # global_nom_li={}
    # global_inv_hd={}
    # global_inv_li={}
    # global_ins_qlt_hd={}
    # global_ins_qlt_li={}
    # global_ins_qnt_hd={}
    global_doc_nom_list=[]
    global_doc_inv_list=[]
    global_doc_qlty_list=[]
    gloabl_doc_qnt_list=[]
    Inv_tos_Row_Id=''

    for fyl in folder:
        # log_dict={}
        if fyl.lower().endswith('.pdf'):
            file_path = os.path.join(folder_path, fyl)
            output_dir = output_path(folder_path)
            txt_file = pdftotext(file_path, fyl, output_dir)
            temp_uuid='' # For temporay storage of doc_uuid
            uuid_doc = str(uuid.uuid4().hex[:8])
            temp_uuid=uuid_doc
            
            error_dict["doc_uuid"] = uuid_doc
            error_dict["VendorName"] = folder_path.split("/")[-3]
            error_dict["Region"] = folder_path.split("/")[-2]
            InvNO=folder_path.split("/")[-1]
            error_dict["InvNo"] = InvNO
            error_dict["FileName"] = file_path.split("/")[-1]
            error_dict['ExtractionStatus']=1
            temp_file_name=file_path # temp storage of file name for movement process
            
            logger.info(f'CGI DOCUMENT UUID is {error_dict["doc_uuid"]} VENDOR_NAME {error_dict["VendorName"]} INVOICE_NUMBER {error_dict["InvNo"]} FILE_NAME {error_dict["FileName"]}')       
            document_type = CGI_classifcation(read_file(txt_file))
            logger.info(f'THIS DOC IS CLASSIFIED AS {document_type}')

            # log_dict["doc_uuid"] = uuid_doc
            # log_dict["InvNo"] = InvNO
            # log_dict["FileName"] = file_path.split("/")[-1]
            # log_dict["VendorName"] = folder_path.split("/")[-3]
            # log_dict["document_type"]=document_type
            # print("aaaaaaaaaaaaaaaaaaaaaaa", document_type)
            if document_type == "Nomination":
                temp_list=[temp_uuid]
                temp_list.append(temp_file_name)
                error_dict["FileType"] = document_type

                try:
                    Nom_header_data = Nomination_header_field(
                        file_data(txt_file), uuid_doc)                    
                    Nom_parcel_item = main_call(read_file(txt_file))
                    Nom_line_item = Quality_line_items(file_data(txt_file))
                   
                    # global_nom_hd=Nom_header_data
                    # global_nom_parcel=Nom_parcel_item
                    # global_nom_li=Nom_line_item
                    
                    # log_dict["Nomination_Extraction"]="Success"
                    logger.info('EXTRACTION OF NOMINATION IS SUCCESSFULL ')
                except Exception as e:
                    # log_dict["Nomination_Extraction"]="Failed:status-2"
                    logger.info('ERRROR DURING EXTRACTION OF NOMINATION ')
                    logger.exception(e)
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                    
               
                if Nom_header_data and Nom_parcel_item:
                    
                    data_insert = Nomination_Insertion(
                        Nom_header_data, Nom_parcel_item, Nom_line_item, error_dict)
                    
                    if data_insert==0:
                        logger.info('EXACTO DB : NOMINATION DATA SUCCESSFULL')
                        # log_dict["Exacto_db_Nomination"]="Exacto DB Insertion Success"
                        MovetoProcessed(dest_dir,InvNO,file_path)
                        temp_list.append(6)
                        global_doc_nom_list.append(temp_list)

                    else:
                        logger.info('EXACTO DB : NOMINATION DATA FAILED')
                        # log_dict["Exacto_db_Nomination"]="Exacto DB Insertion Failed"
                        error_insert = Error_update(error_dict)
                        MovetoUnprocessed(error_dir, InvNO, file_path)
                        temp_list.append(5)
                        global_doc_nom_list.append(temp_list)                                       
                else:
                    logger.info('ERRROR DURING EXTRACTION OF NOMINATION !!!')
                    
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    # print("Nomination file not extracted")
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                    

            elif document_type == "Invoice":
                error_dict["FileType"] = document_type
                temp_list=[temp_uuid]
                temp_list.append(temp_file_name)
                try:
                    inv_header_data = cgi_invoice_headers_extraction(
                        read_file(txt_file), uuid_doc)
                    inv_line_item = cgi_lineitem_main(txt_file)
                    
                    global_inv_hd=inv_header_data
                    global_inv_li=inv_line_item
                    logger.info('EXTRACTION OF INVOICE IS SUCCESSFULL')
                    # log_dict["Invoice_Extraction"]="Success"
                except Exception as e:
                    logger.info('ERRROR DURING EXTRACTION OF INVOICE ')
                    logger.exception(e)
                    # log_dict["Invoice_Extraction"]="Failed:status-2"
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    # print("Nomination file not extracted")
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                    
                if inv_header_data:
                    inv_insert = cgi_invoice_db_insertion(
                        inv_header_data, inv_line_item, error_dict)
                    
                    if inv_insert==0:
                        logger.info('EXACTO DB : INVOICE DATA SUCCESSFULL')
                        # log_dict["Exacto_db_Invoice"]="Exacto DB Insertion Success"
                        MovetoProcessed(dest_dir, InvNO, file_path)
                        temp_list.append(6)
                        global_doc_inv_list.append(temp_list)
                    else:
                        logger.info('EXACTO DB : INVOICE DATA FAILED')
                        # log_dict["Exacto_db_Invoice"]="Exacto DB Insertion Failed"
                        Error_update(error_dict)                       
                        MovetoUnprocessed(error_dir, InvNO, file_path)
                        temp_list.append(5)
                        global_doc_inv_list.append(temp_list)                    
                else:
                    logger.info('ERRROR DURING EXTRACTION OF INVOICE !!!')
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                   

            elif document_type == "Quality":
                error_dict["FileType"] = document_type
                temp_list=[temp_uuid]
                temp_list.append(temp_file_name)
                try:
                    qlty_header_data = cgi_quality_headers_extraction(
                        read_file(txt_file), uuid_doc)
                    qlty_line_item = cgi_qlty_lineitem_main(txt_file)
                    
                    global_ins_qlt_hd = qlty_header_data
                    global_ins_qlt_li = qlty_line_item
                    logger.info('EXTRACTION OF QUALITY IS SUCCESSFULL ')
                    # log_dict["Quality_Extraction"]="Success"
                except Exception as e:
                    logger.info('ERRROR DURING EXTRACTION OF QUALITY ')
                    logger.exception(e)
                    # log_dict["Quality_Extraction"]="Failed:status-2"
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    # print("Nomination file not extracted")
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                    
                if qlty_header_data:
                    qlty_insert = cgi_quality_db_insertion(
                        qlty_header_data, qlty_line_item, error_dict)
                    if qlty_insert==0:
                        logger.info('EXACTO DB : QUALITY DATA SUCCESSFULL')
                        # log_dict["Exacto_db_Quality"]="Exacto DB Insertion Success" 
                        MovetoProcessed(dest_dir, InvNO, file_path)
                        temp_list.append(6)
                        global_doc_qlty_list.append(temp_list)
                    else:
                        logger.info('EXACTO DB : QUALITY DATA FAILED')
                        # log_dict["Exacto_db_Quality"]="Exacto DB Insertion Failed" 
                        Error_update(error_dict)
                        MovetoUnprocessed(error_dir, InvNO, file_path)
                        temp_list.append(5)
                        global_doc_qlty_list.append(temp_list)
                else:
                    logger.info('ERRROR DURING EXTRACTION OF QUALITY !!!')
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                    

            elif document_type == "Quantity":
                temp_list=[temp_uuid]
                temp_list.append(temp_file_name)
                error_dict["FileType"] = document_type
                try:
                    qnty_header_data = cgi_quantity_headers_extraction(
                        read_file(txt_file), uuid_doc)
                    
                    global_ins_qnt_hd = qnty_header_data
                    # log_dict["Quantity_Extraction"]="Success"
                    logger.info('EXTRACTION OF QUANTITY IS SUCCESSFULL')
                except Exception as e :
                    logger.info('ERRROR DURING EXTRACTION OF QUANTITY ')
                    logger.exception(e)
                    # log_dict["Quantity_Extraction"]="Failed:status-2"
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                # qlty_line_item = cgi_qlty_lineitem_main(txt_file)
                
                if qnty_header_data:
                    qlty_insert = cgi_quantity_db_insertion(
                        qnty_header_data, error_dict)
                    if qlty_insert==0:
                        logger.info('EXACTO DB : QUANTITY DATA SUCCESSFULL')
                        # log_dict["Exacto_db_Quantity"]="Exacto DB Insertion Success" 
                        MovetoProcessed(dest_dir, InvNO, file_path)
                        temp_list.append(6)
                        gloabl_doc_qnt_list.append(temp_list)
                    else:
                        logger.info('EXACTO DB : QUANTITY DATA FAILED')
                        # log_dict["Exacto_db_Quantity"]="Exacto DB Insertion Failed" 
                        Error_update(error_dict)
                        MovetoUnprocessed(error_dir, InvNO, file_path)
                        temp_list.append(5)
                        gloabl_doc_qnt_list.append(temp_list)
                else:
                    logger.info('ERRROR DURING EXTRACTION OF QUANTITY !!!')
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                    
            else:
                logger.info("NON-CATEGORIZED DOCUMENT")
                # log_dict["Extra documention"]="Non-categorized document: status-2"
                print("Extra documention ")
                error_dict["ExtractionStatus"] = 2
                error_dict["FileType"] = "Other documents"
                # print("Nomination file not classifeid ")
                error_insert = Error_insert(error_dict)
                MovetoUnprocessed(error_dir, InvNO, file_path)
                
        # if log_dict !={}:
        #     logger.info(log_dict)        
           
    ########################### CALLING PROCEDURE ####################

    Inv_tos_Row_Id,global_doc_nom_list,global_doc_inv_list,gloabl_doc_qnt_list,global_doc_qlty_list=stored_procedure_calling_toscana(InvNO,global_doc_nom_list,global_doc_inv_list,gloabl_doc_qnt_list,global_doc_qlty_list)
    
    print('THE ROW ID USED FRO DOCKER BLOB DATA TRANSFER IS : ',Inv_tos_Row_Id)

    print(global_doc_nom_list,global_doc_inv_list,gloabl_doc_qnt_list,global_doc_qlty_list)

    ###########################  MOVEMENT OF UNPROCESSED DOCUMENTS ###################
    try:
        movement_of_file_after_toscandb_status(error_dir,InvNO,global_doc_nom_list,global_doc_inv_list,gloabl_doc_qnt_list,global_doc_qlty_list)
    except:
        print('SOMETHING WENT WRONG ON MOVEMENT OF DOCUMENTS AFTER TOSCAN SP CALLING')

    
    ############################################################################################
    ## MOVEMENTS OF PROCESSED DOCUMNENTS TO TOSCANA ###
    if(Inv_tos_Row_Id!="NA"):
        blob_call_api(Inv_tos_Row_Id,global_doc_nom_list,global_doc_inv_list,gloabl_doc_qnt_list,global_doc_qlty_list)

            

    ############################
################################################# CAMIN #############################################################################################################

def Camin_process(folder_path, error_dir, dest_dir):
    logger.info("CAMIN DOCUMENT PROCESSING START...")
    error_dict = {}
    # global_uuid=
    error_dict["StartTime"] = datetime.datetime.now()
    error_dict["ExtractionStatus"] = 0
    folder = os.listdir(folder_path)
    global_nom_hd={}
    global_nom_parcel={}
    global_nom_li={}
    global_inv_hd={}
    global_inv_li={}
    global_ins_qlt_hd={}
    global_ins_qlt_li={}
    global_ins_qnt_hd={}
    global_doc_nom_list=[]
    global_doc_inv_list=[]
    global_doc_qlty_list=[]
    gloabl_doc_qnt_list=[]
    Inv_tos_Row_Id=''

    for fyl in folder:
        
        if fyl.lower().endswith('.pdf'):
            file_path = os.path.join(folder_path, fyl)
            output_dir = output_path(folder_path)
            txt_file = pdftotext(file_path, fyl, output_dir)
            uuid_doc = str(uuid.uuid4().hex[:8])
            tempuuid=uuid_doc
            error_dict["doc_uuid"] = uuid_doc
            error_dict["VendorName"] = folder_path.split("/")[-3]
            error_dict["Region"] = folder_path.split("/")[-2]
            InvNO=folder_path.split("/")[-1]
            error_dict["InvNo"] = InvNO
            error_dict["FileName"] = file_path.split("/")[-1]
            error_dict["ExtractionStatus"] = 1
            temp_file_name= file_path
            
            logger.info(f'CAMIN DOCUMENT UUID is {error_dict["doc_uuid"]} VENDOR_NAME {error_dict["VendorName"]} INVOICE_NUMBER {error_dict["InvNo"]} FILE_NAME {error_dict["FileName"]}')       
            document_type = Camin_classifcation(read_file(txt_file))
            logger.info(f'THIS DOC IS CLASSIFIED AS {document_type}')
            
            if document_type == "Nomination":
                
                temp_list=[tempuuid]
                temp_list.append(temp_file_name)
                error_dict["FileType"] = document_type
                try:
                    Nom_header_data = Nomination_header_field(file_data(txt_file), uuid_doc)
                    # print("Camin Nomination header data &&&&&&&&&&",Nom_header_data)
                    Nom_parcel_item = main_call(read_file(txt_file))
                    # print("Camin Nomination parcel data", Nom_parcel_item)
                    Nom_line_item = Quality_line_items(file_data(txt_file))
                    
                    
                    # print("Camin Nomination line data @@@@@@@@@@", Nom_line_item)
                    
                    logger.info('EXTRACTION OF NOMINATION IS SUCCESSFULL')
                except Exception as e:
                    logger.info('ERRROR DURING EXTRACTION OF NOMINATION ')
                    logger.exception(e)
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                
                if Nom_header_data and Nom_parcel_item:
                   
                    data_insert = Nomination_Insertion(
                        Nom_header_data, Nom_parcel_item, Nom_line_item, error_dict)
                    if data_insert==0:
                        logger.info('EXACTO DB : NOMINATION DATA SUCCESSFULL')
                        MovetoProcessed(dest_dir,InvNO,file_path)
                        temp_list.append(6)
                        global_doc_nom_list.append(temp_list)
                    else:
                        logger.info('EXACTO DB : NOMINATION DATA FAILED')
                        error_insert = Error_update(error_dict)
                        MovetoUnprocessed(error_dir, InvNO, file_path)   
                        temp_list.append(5)  
                        global_doc_nom_list.append(temp_list)           
                    
                else:
                    logger.info('ERRROR DURING EXTRACTION OF NOMINATION !!!')
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    print("Nomination file not extracted")
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                    

            elif document_type == "Invoice":
                # print("2222222222222222222222222222")
                temp_list=[tempuuid]
                temp_list.append(temp_file_name)
                error_dict["FileType"] = document_type
                try:
                    inv_header_data = camin_invoice_headers_extraction(
                        read_file(txt_file), uuid_doc)                    
                    inv_line_item = camin_lineitem_main(txt_file)
                    # global_inv_hd=inv_header_data
                    # global_inv_li=inv_line_item
                    logger.info('EXTRACTION OF INVOICE IS SUCCESSFULL')
                except Exception as e:
                    logger.info('ERRROR DURING EXTRACTION OF INVOICE ')
                    logger.exception(e)
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                
                if inv_header_data:
                    inv_insert = cgi_invoice_db_insertion(
                        inv_header_data, inv_line_item, error_dict)
                    
                    if inv_insert==0:
                        logger.info('EXACTO DB : INVOICE DATA SUCCESSFULL')
                        MovetoProcessed(dest_dir, InvNO, file_path)
                        temp_list.append(6)
                        global_doc_inv_list.append(temp_list)
                    else:
                        logger.info('EXACTO DB : INVOICE DATA FAILED')
                        Error_update(error_dict)                        
                        MovetoUnprocessed(error_dir, InvNO, file_path)
                        temp_list.append(5)
                        global_doc_inv_list.append(temp_list)
                    
                else:
                    logger.info('ERRROR DURING EXTRACTION OF INVOICE !!!')
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                    
            elif document_type == "Quality and Quantity":
                temp_list=[tempuuid]
                temp_list.append(temp_file_name)
                
                error_dict["FileType"] = document_type
                try:
                    qnty_header_data = camin_quantity_header(file_data(txt_file),read_file(txt_file), uuid_doc)
                    # print("Camin Quantity header data &&&&&&&&&&",qnty_header_data)
                    qnty_line_item = Camin_inspection_lineitem_main(read_file(txt_file), uuid_doc)
                    # print("Camin Quantity lineitem data &&&&&&&&&&",qnty_line_item)
                    qlty_header_data = camin_quality_header(file_data(txt_file),read_file(txt_file), uuid_doc)
                    # print("Camin Quality header data &&&&&&&&&&",qlty_header_data)
                    qlty_line_item = Camin_Ins_quality_li_main(txt_file)
                    # print("Camin Quality line item data &&&&&&&&&&",qlty_line_item)
                    logger.info('EXTRACTION OF QUALITY & QUANTITY IS SUCCESSFULL ')
                    # global_ins_qnt_hd = qnty_header_data
                except Exception as e:
                    logger.info('ERRROR DURING EXTRACTION OF QUALITY & QUANTITY ')
                    logger.exception(e)
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                    
                qnt_com_data=qnt_hd_li_merge(qnty_header_data,qnty_line_item)
                if qnty_header_data and qlty_header_data :
                    qnty_qlty_insert = camin_qnt_and_quality_db_insertion(qnt_com_data,qlty_header_data,qlty_line_item, error_dict)
                    
                    if qnty_qlty_insert==0:
                        logger.info('EXACTO DB : QUALITY & QUANTITY DATA SUCCESSFULL')
                        MovetoProcessed(dest_dir, InvNO, file_path)
                        temp_list.append(6)
                        gloabl_doc_qnt_list.append(temp_list)
                        global_doc_qlty_list.append(temp_list)
                                       
                    else:
                        logger.info('EXACTO DB : QUALITY & QUANTITY DATA FAILED')
                        Error_update(error_dict)
                        MovetoUnprocessed(error_dir, InvNO, file_path)
                        temp_list.append(5)
                        gloabl_doc_qnt_list.append(temp_list)
                        global_doc_qlty_list.append(temp_list)
                
                else:
                    logger.info('ERRROR DURING EXTRACTION OF QUALITY & QUANTITY ')
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                
                       
            
            elif document_type == "Quality":
                temp_list=[tempuuid]
                temp_list.append(temp_file_name)
                error_dict["FileType"] = document_type
                try:
                    qlty_header_data = camin_quality_header(file_data(txt_file),read_file(txt_file), uuid_doc)                    
                    qlty_line_item = Camin_Ins_quality_li_main(txt_file)
                    # global_ins_qlt_hd = qlty_header_data
                    # global_ins_qlt_li = qlty_line_item
                    logger.info('EXTRACTION OF QUALITY IS SUCCESSFULL ')
                except Exception as e:
                    logger.info('ERRROR DURING EXTRACTION OF QUALITY ')
                    logger.exception(e)
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                
                if qlty_header_data:
                    qlty_insert = cgi_quality_db_insertion(
                        qlty_header_data, qlty_line_item, error_dict)
                    if qlty_insert==0:
                        logger.info('EXACTO DB : QUALITY DATA SUCCESSFULL') 
                        MovetoProcessed(dest_dir, InvNO, file_path)
                        temp_list.append(6)
                        global_doc_qlty_list.append(temp_list)

                    else:
                        logger.info('EXACTO DB : QUALITY DATA FAILED') 
                        Error_update(error_dict)
                        MovetoUnprocessed(error_dir, InvNO, file_path)
                        temp_list.append(5)
                        global_doc_qlty_list.append(temp_list)
                
                else:
                    logger.info('ERRROR DURING EXTRACTION OF QUALITY ')
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                    

            elif document_type == "Quantity":
                temp_list=[tempuuid]
                temp_list.append(temp_file_name)
                error_dict["FileType"] = document_type
                try:
                    qnty_header_data = camin_quantity_header(file_data(txt_file),read_file(txt_file), uuid_doc)
                    # print("Camin Quantity header data &&&&&&&&&&",qnty_header_data)
                    qnty_line_item = Camin_inspection_lineitem_main(read_file(txt_file), uuid_doc)
                    # print("Camin Quantity lineitem data &&&&&&&&&&",qnty_line_item)
                    
                    # global_ins_qnt_hd = qnty_header_data
                    logger.info('EXTRACTION OF QUANTITY IS SUCCESSFULL')
                except Exception as e :
                    logger.info('ERRROR DURING EXTRACTION OF QUANTITY ')
                    logger.exception(e)
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                
                qnt_com=qnt_hd_li_merge(qnty_header_data,qnty_line_item)                    
                # qlty_line_item = cgi_qlty_lineitem_main(txt_file)
                if qnty_header_data:
                    qlty_insert = cgi_quantity_db_insertion(
                        qnt_com, error_dict)
                    if qlty_insert==0:
                        logger.info('EXACTO DB : QUANTITY DATA SUCCESSFULL')
                        MovetoProcessed(dest_dir, InvNO, file_path)
                        temp_list.append(6)
                        gloabl_doc_qnt_list.append(temp_list)
                    else:
                        logger.info('EXACTO DB : QUANTITY DATA FAILED')
                        Error_update(error_dict)
                        MovetoUnprocessed(error_dir, InvNO, file_path)
                        temp_list.append(5)
                        gloabl_doc_qnt_list.append(temp_list)
                else:
                    logger.info('ERRROR DURING EXTRACTION OF QUANTITY ')
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                    
            else:
                logger.info("NON-CATEGORIZED DOCUMENT")
                print("Extra documention ")
                error_dict["ExtractionStatus"] = 2
                error_dict["FileType"] = "Other documents"                
                error_insert = Error_insert(error_dict)
                MovetoUnprocessed(error_dir, InvNO, file_path)
    
    ########################### CAMIN TOSCAN DB MOVEMENT ###############################

    Inv_tos_Row_Id,global_doc_nom_list,global_doc_inv_list,gloabl_doc_qnt_list,global_doc_qlty_list=stored_procedure_calling_toscana(InvNO,global_doc_nom_list,global_doc_inv_list,gloabl_doc_qnt_list,global_doc_qlty_list)
    
    print('THE ROW ID USED FRO DOCKER BLOB DATA TRANSFER IS : ',Inv_tos_Row_Id)

    print(global_doc_nom_list,global_doc_inv_list,gloabl_doc_qnt_list,global_doc_qlty_list)

    
    ###########################  MOVEMENT OF UNPROCESSED DOCUMENTS ###################
    try:
        movement_of_file_after_toscandb_status(error_dir,InvNO,global_doc_nom_list,global_doc_inv_list,gloabl_doc_qnt_list,global_doc_qlty_list)
    except:
        print('SOMETHING WENT WRONG ON MOVEMENT OF DOCUMENTS AFTER TOSCAN SP CALLING')
    ## MOVEMENTS OF PROCESSED DOCUMNENTS TO TOSCANA ###
    if(Inv_tos_Row_Id!="NA"):
        blob_call_api(Inv_tos_Row_Id,global_doc_nom_list,global_doc_inv_list,gloabl_doc_qnt_list,global_doc_qlty_list)
    ############################

############################################# SAYBOLT #################################################################################
 

def Saybolt_process(folder_path, error_dir, dest_dir):
    error_dict = {}
    logger.info("SAYBOLT DOCUMENT PROCESSING START...")
    error_dict["StartTime"] = datetime.datetime.now()
    error_dict["ExtractionStatus"] = 0
    folder = os.listdir(folder_path)
    global_nom_hd={}
    global_nom_parcel={}
    global_nom_li={}
    global_inv_hd={}
    global_inv_li={}
    global_ins_qlt_hd={}
    global_ins_qlt_li={}
    global_ins_qnt_hd={}
    global_doc_nom_list=[]
    global_doc_inv_list=[]
    global_doc_qlty_list=[]
    gloabl_doc_qnt_list=[]
    Inv_tos_Row_Id=''

    for fyl in folder:
        
        if fyl.lower().endswith('.pdf'):
           
            file_path = os.path.join(folder_path, fyl)
            os.rename(file_path,re.sub("\'","_",file_path)) # rename file by deleting special chr are occured 
            output_dir = output_path(folder_path)
            txt_file = pdftotext(file_path, fyl, output_dir)
            # print("SAYBOLT tttttttttttttttt",txt_file)
            uuid_doc = str(uuid.uuid4().hex[:8])
            error_dict["doc_uuid"] = uuid_doc
            temp_uuid=uuid_doc
            error_dict["VendorName"] = folder_path.split("/")[-3]
            error_dict["Region"] = folder_path.split("/")[-2]
            InvNO=folder_path.split("/")[-1]
            error_dict["InvNo"] = InvNO
            error_dict["FileName"] = file_path.split("/")[-1]
            error_dict["ExtractionStatus"] = 1
            temp_file_name=file_path
            logger.info(f'SAYBOLT DOCUMENT UUID is {error_dict["doc_uuid"]} VENDOR_NAME {error_dict["VendorName"]} INVOICE_NUMBER {error_dict["InvNo"]} FILE_NAME {error_dict["FileName"]}')       
            document_type = Saybolt_classifcation(read_file(txt_file))
            logger.info(f'THIS DOC IS CLASSIFIED AS {document_type}')
            # print("Saybolt classifiction-------", document_type,",,,",fyl)    
            if document_type == "Nomination":
                
                error_dict["FileType"] = document_type
                temp_list=[temp_uuid]
                temp_list.append(temp_file_name)
                try:
                    Nom_header_data = Nomination_header_field(file_data(txt_file), uuid_doc)
                    # print("Saybolt Nomination header data &&&&&&&&&&",Nom_header_data)
                    Nom_parcel_item = main_call(read_file(txt_file))
                    # print("Saybolt Nomination parcel data", Nom_parcel_item)
                    try:
                        Nom_line_item = Quality_line_items(file_data(txt_file))
                        # print("Saybolt Nomination line data @@@@@@@@@@", Nom_line_item)
                    except:
                        print("either not present or error in Nom_line_item ")
                        Nom_line_item=[]
                    logger.info('EXTRACTION OF NOMINATION IS SUCCESSFULL ')
                except Exception as e:
                    logger.info('ERRROR DURING EXTRACTION OF NOMINATION ')
                    logger.exception(e)
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                
                if Nom_header_data and Nom_parcel_item:
                    data_insert = Nomination_Insertion(
                        Nom_header_data, Nom_parcel_item, Nom_line_item, error_dict)
                    if data_insert==0:
                        logger.info('EXACTO DB : NOMINATION DATA SUCCESSFULL')
                        MovetoProcessed(dest_dir,InvNO,file_path)
                        temp_list.append(6)
                        global_doc_nom_list.append(temp_list)
                    else:
                        logger.info('EXACTO DB : NOMINATION DATA FAILED')
                        error_insert = Error_update(error_dict)
                        MovetoUnprocessed(error_dir, InvNO, file_path)   
                        temp_list.append(5)
                        global_doc_nom_list.append(temp_list)             
                    
                else:
                    logger.info('ERRROR DURING EXTRACTION OF NOMINATION !!!')
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    print("Nomination file not extracted")
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                    
            elif document_type == "Invoice":
                
                error_dict["FileType"] = document_type
                temp_list=[temp_uuid]
                temp_list.append(temp_file_name)
                try:
                    inv_header_data = saybolt_invoice_headers_extraction(
                        read_file(txt_file), uuid_doc)
                    # print("Saybolt Invoice header data &&&&&&&&&&",inv_header_data)
                    inv_line_item = saybolt_lineitem_main(txt_file)
                    # print("Saybolt Invoice lineitem data ***************",inv_line_item)
                    # global_inv_hd=inv_header_data
                    # global_inv_li=inv_line_item
                    logger.info('EXTRACTION OF INVOICE IS SUCCESSFULL ')
                except Exception as e:
                    logger.info('ERRROR DURING EXTRACTION OF INVOICE ')
                    logger.exception(e)
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                
                if inv_header_data:
                    inv_insert = cgi_invoice_db_insertion(
                        inv_header_data, inv_line_item, error_dict)
                    
                    if inv_insert==0:
                        logger.info('EXACTO DB : INVOICE DATA SUCCESSFULL')
                        MovetoProcessed(dest_dir, InvNO, file_path)
                        temp_list.append(6)
                        global_doc_inv_list.append(temp_list)
                    else:
                        logger.info('EXACTO DB : INVOICE DATA FAILED')
                        Error_update(error_dict)                       
                        MovetoUnprocessed(error_dir, InvNO, file_path)
                        temp_list.append(5)
                        global_doc_inv_list.append(temp_list)
                    
                else:
                    logger.info('ERRROR DURING EXTRACTION OF INVOICE !!!')
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                
                
            elif document_type == "Quality":
                
                error_dict["FileType"] = document_type
                temp_list=[temp_uuid]
                temp_list.append(temp_file_name)
                try:
                    qlty_header_data = saybolt_quality_header(file_data(txt_file),read_file(txt_file), uuid_doc)
                    # print("Saybolt Quality header data &&&&&&&&&&",qlty_header_data)
                    qlty_line_item = saybolt_qlty_lineitem_main(txt_file)
                    # print("Saybolt Quality line item data &&&&&&&&&&",qlty_line_item)
                    # global_ins_qlt_hd = qlty_header_data
                    # global_ins_qlt_li = qlty_line_item
                    logger.info('EXTRACTION OF QUALITY IS SUCCESSFULL ')
                except Exception as e:
                    logger.info('ERRROR DURING EXTRACTION OF QUALITY ')
                    logger.exception(e)
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                
                if qlty_header_data:
                    qlty_insert = cgi_quality_db_insertion(
                        qlty_header_data, qlty_line_item, error_dict)
                    if qlty_insert==0: 
                        logger.info('EXACTO DB : QUALITY DATA SUCCESSFULL') 
                        MovetoProcessed(dest_dir, InvNO, file_path)
                        temp_list.append(6)
                        global_doc_qlty_list.append(temp_list)
                    else:
                        logger.info('EXACTO DB : QUALITY DATA FAILED')
                        Error_update(error_dict)
                        MovetoUnprocessed(error_dir, InvNO, file_path)
                        temp_list.append(5)
                        global_doc_qlty_list.append(temp_list)
                
                else:
                    logger.info('ERRROR DURING EXTRACTION OF QUALITY !!!!')
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                
            elif document_type == "Quantity":
               
                error_dict["FileType"] = document_type
                temp_list=[temp_uuid]
                temp_list.append(temp_file_name)
                try:
                    qnty_header_data = saybolt_quantity_header(file_data(txt_file),read_file(txt_file), uuid_doc)
                    # print("Saybolt Quantity header data &&&&&&&&&&",qnty_header_data)
                    qnty_line_item = FinalQuantityLineItems(read_file(txt_file),uuid_doc)
                    # print("Saybolt Quantity lineitem data &&&&&&&&&&",qnty_line_item)
                    
                    # global_ins_qnt_hd = qnty_header_data
                    logger.info('EXTRACTION OF QUANTITY IS SUCCESSFULL')
                except Exception as e :
                    logger.info('ERRROR DURING EXTRACTION OF QUANTITY ')
                    logger.exception(e)
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                               
                qnt_com=saybolt_qnt_li(qnty_header_data,qnty_line_item) 
                # print(qnt_com)               
                # qlty_line_item = cgi_qlty_lineitem_main(txt_file)
                if qnty_header_data:
                    qlty_insert = cgi_quantity_db_insertion(
                        qnt_com, error_dict)
                    
                    if qlty_insert==0:
                        logger.info('EXACTO DB : QUANTITY DATA SUCCESSFULL')
                        MovetoProcessed(dest_dir, InvNO, file_path)
                        temp_list.append(6)
                        gloabl_doc_qnt_list.append(temp_list)
                    else:
                        logger.info('EXACTO DB : QUANTITY DATA FAILED')
                        Error_update(error_dict)
                        MovetoUnprocessed(error_dir, InvNO, file_path)
                        temp_list.append(5)
                        gloabl_doc_qnt_list.append(temp_list)
                else:
                    logger.info('ERRROR DURING EXTRACTION OF QUANTITY !!!')
                    error_dict["ExtractionStatus"] = 2
                    error_insert = Error_insert(error_dict)
                    MovetoUnprocessed(error_dir, InvNO, file_path)
                    
            else:
                logger.info("NON-CATEGORIZED DOCUMENT")
                print("Extra documention ")
                error_dict["ExtractionStatus"] = 2
                error_dict["FileType"] = "Other documents"               
                error_insert = Error_insert(error_dict)
                MovetoUnprocessed(error_dir, InvNO, file_path)
    ####################### SAYBOLT TOSCAN DB MOVEMENT ###############################

    Inv_tos_Row_Id,global_doc_nom_list,global_doc_inv_list,gloabl_doc_qnt_list,global_doc_qlty_list=stored_procedure_calling_toscana(InvNO,global_doc_nom_list,global_doc_inv_list,gloabl_doc_qnt_list,global_doc_qlty_list)
    
    print('THE ROW ID USED FRO DOCKER BLOB DATA TRANSFER IS : ',Inv_tos_Row_Id)

    print(global_doc_nom_list,global_doc_inv_list,gloabl_doc_qnt_list,global_doc_qlty_list)

    ###############################################################################
    ###########################  MOVEMENT OF UNPROCESSED DOCUMENTS ###################
    try:
        movement_of_file_after_toscandb_status(error_dir,InvNO,global_doc_nom_list,global_doc_inv_list,gloabl_doc_qnt_list,global_doc_qlty_list)
    except:
        print('SOMETHING WENT WRONG ON MOVEMENT OF DOCUMENTS AFTER TOSCAN SP CALLING')
    ############################################################################################
    ## MOVEMENTS OF PROCESSED DOCUMNENTS TO TOSCANA ###
    if(Inv_tos_Row_Id!="NA"):
        blob_call_api(Inv_tos_Row_Id,global_doc_nom_list,global_doc_inv_list,gloabl_doc_qnt_list,global_doc_qlty_list)
    ############################

    ############################################################################################


#####################################################################################################################################################            
     
def process_folders(source_dir, dest_dir, error_dir, batch_size):
    
    folders = os.listdir(source_dir)
    
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
                 
                a = CGI_process(folder_path, error_dir, dest_dir)
                dest_folder = os.path.join(source_dir, folder)
                if os.path.exists(dest_folder):
                    shutil.rmtree(dest_folder)
            elif "Camin" in folder_path:
                proccessed_folder = os.path.join(dest_dir, folder)
                non_proccessed_folder = os.path.join(error_dir, folder)
                if os.path.exists(proccessed_folder):
                    shutil.rmtree(proccessed_folder)
                if os.path.exists(non_proccessed_folder):
                    shutil.rmtree(non_proccessed_folder)
                 
                b = Camin_process(folder_path, error_dir, dest_dir)
                dest_folder = os.path.join(source_dir, folder)
                if os.path.exists(dest_folder):
                    shutil.rmtree(dest_folder) 
                    
            elif "Saybolt" in folder_path:
                proccessed_folder = os.path.join(dest_dir, folder)
                non_proccessed_folder = os.path.join(error_dir, folder)
                if os.path.exists(proccessed_folder):
                    shutil.rmtree(proccessed_folder)
                if os.path.exists(non_proccessed_folder):
                    shutil.rmtree(non_proccessed_folder)
                 
                c = Saybolt_process(folder_path, error_dir, dest_dir)
                dest_folder = os.path.join(source_dir, folder)
                if os.path.exists(dest_folder):
                    shutil.rmtree(dest_folder) 
                       
            else:
                print("Not code for camin vendor")
                error_folder = os.path.join(error_dir, folder)
                if os.path.exists(error_folder):
                    shutil.rmtree(error_folder)
                shutil.move(folder_path, error_folder)
            

def main():
    
    source_dirs = [esett.INPUT_CGI_CHEM, esett.INPUT_CGI_US,
                   esett.INPUT_CAMIN_CHEM, esett.INPUT_CAMIN_US, esett.INPUT_CAMIN_INT,
                  esett.INPUT_SAYBOLT_INT,esett.INPUT_SAYBOLT_CHEM,esett.INPUT_SAYBOLT_EU,esett.INPUT_SAYBOLT_US]
    dest_dirs = [esett.PROCESSED_CGI_CHEM_PATH, esett.PROCESSED_CGI_US_PATH,
                 esett.PROCESSED_CAMIN_CHEM_PATH, esett.PROCESSED_CAMIN_US_PATH, esett.PROCESSED_CAMIN_INT_PATH,
                 esett.PROCESSED_SAYBOLT_INT_PATH,esett.PROCESSED_SAYBOLT_CHEM_PATH,esett.PROCESSED_SAYBOLT_EU_PATH,
                 esett.PROCESSED_SAYBOLT_US_PATH]
    
    error_dirs = [esett.ERROR_CGI_CHEM_PATH, esett.ERROR_CGI_US_PATH,
                  esett.ERROR_CAMIN_CHEM_PATH, esett.ERROR_CAMIN_US_PATH, esett.ERROR_CAMIN_INT_PATH,
                  esett.ERROR_SAYBOLT_INT_PATH,esett.ERROR_SAYBOLT_CHEM_PATH,esett.ERROR_SAYBOLT_EU_PATH,
                  esett.ERROR_SAYBOLT_US_PATH]
    # dest_dir = "/path/to/destination/directory"

    # process a batch of folders less than or equal to 10
    batch_size = 5

    # keep running the loop
    while True:
        # create a thread for each source directory
        threads = []
        for it in range(len(source_dirs)):
            thread = Thread(target=process_folders, args=(
                source_dirs[it], dest_dirs[it], error_dirs[it], batch_size))
            thread.start()
            threads.append(thread)

        # wait for all threads to finish
        for thread in threads:
            thread.join()

        # wait for some time before checking for new folders
        time.sleep(10) # wait for 60 seconds before checking for new folders again


if __name__ == '__main__':
    main()
