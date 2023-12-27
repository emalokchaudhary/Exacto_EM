import os
import random
import shutil
import json
import time
import pandas as pd
from shutil import copyfile
import xlwt as xl
import xlrd
import datetime, pprint
from datetime import timedelta
import traceback
import tensorflow as tf

from nlp.Harris_Invoice_Classifier import doc_classifier
from nlp.mainNLP import mainCallNLP
from nlp.nlp_utils import create_dict_log
from classify_inv import Invoice_Classification
from table.main import description_from_invoices
from ocr.pdfFiles import startOcr
import exacto_general_utils as egut

import nlp.nlp_utils as nut
import gc, inspect, sys

 


def nlp_extraction(info_folder_path, user_id, config_id):

    #static_dictionary = egut.get_default_static_dict()
    #dynamic_dictionary = egut.get_default_dyn_dict()
   
    output_dict_log_path = os.path.join(info_folder_path,'output_dict_logs')
    if not os.path.exists(output_dict_log_path):
        os.mkdir(output_dict_log_path)

   
    static_dictionary = mainCallNLP(info_folder_path)     
    dynamic_dictionary, invoice_type, page_rows = description_from_invoices(info_folder_path,user_id, config_id,'')
    dynamic_dictionary = nut.remove_table_conf(dynamic_dictionary)    
          
    try:
    	nut.create_dyn_log(dynamic_dictionary,output_dict_log_path, 'dyn_dict_before_br.txt') 
    	nut.create_dict_log(static_dictionary,output_dict_log_path, 'sta_dict_before_br.txt')   
    except Exception as e:
    	print("Exception in creating dictionary logs", e)
    
    tf.reset_default_graph()
    return (static_dictionary,dynamic_dictionary)



def drive_ocr_flow(paths, document_path, outputPath):

    checkpoint_path = paths['checkpoint_path']
    checkpointPath = paths['checkpointPath']
    checkpointMeta = paths['checkpointMeta']
    classModel = paths['classModel']
    classModelDir = paths['classModelDir']
    xml_dir = paths['xml_dir']


    if not os.path.isdir(outputPath):
        os.makedirs(outputPath)

    ocr_success = True
    try:
        text_files_path,phase,ocr_flag = startOcr(document_path, outputPath, checkpoint_path, checkpointPath, checkpointMeta,
                                classModel,classModelDir, "")
        
    except Exception as e:
        ocr_success = False
        print("Exception in OCR extraction ", e)
        
        tf.reset_default_graph()
    return ocr_success, text_files_path, phase, ocr_flag



def drive_nlp_flow(file_name, text_files_path, custom_extractor_obj, **kwargs):

             
    info_folder_path = egut.create_output_folder(text_files_path)
    

   

    try:

        _invoices = egut.classify_scan_doc(text_files_path, info_folder_path)

    except Exception as e:
        #print("exception in classfying scan doc ", e)
        #traceback.print_exc()
        tf.reset_default_graph()
        pass
    
    try:
        _invoices = egut.classify_pdf_doc(text_files_path, info_folder_path)
        
    except Exception as e:

        #print("exception in classfying pdf doc ", e)
        #traceback.print_exc()
        tf.reset_default_graph()
        pass
    
    invoices = Invoice_Classification(text_files_path, info_folder_path)

    if not invoices:
        print("WARNING:  No relevant pages found after classification, returning default values")
        sta = egut.get_default_static_dict()
        dyn = egut.get_default_dyn_dict()
        return sta, dyn

    if custom_extractor_obj.config_id is None:
        custom_extractor_obj.config_id = invoices
        kwargs['config'] = invoices

    try:
        sta, dyn = nlp_extraction(info_folder_path,user_id=kwargs['user'], config_id = kwargs['config'])
    except Exception as e:
        print('Error in nlp extraction', e)
        print(traceback.print_exc())
        pass

    infoN_folderpath = os.path.join(info_folder_path, 'RestructBiLSTM')

    custom_extractor_obj.folderpath = infoN_folderpath
    custom_field_dict = custom_extractor_obj.extract_custom_fields()

    for k, v in custom_field_dict.items():
        if v[0] is None:
            custom_field_dict[k] = ["",""]
    sta.update(custom_field_dict)
    sta = dict([(key, [str(v) for v in val]) for key,val in sta.items()])
    print("custom_field_dict ",custom_field_dict)

    return sta, dyn,invoices















