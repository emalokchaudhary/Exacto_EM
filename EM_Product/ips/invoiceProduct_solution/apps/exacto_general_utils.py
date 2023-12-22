import os
import random
import shutil
import json
import time
import pandas as pd
from shutil import copyfile
import xlwt as xl
import xlrd
import json
import datetime, pprint
from datetime import timedelta
import traceback
import tensorflow as tf

from nlp.Harris_Invoice_Classifier import doc_classifier


def combine_excel_files(excel_file_path, dir_path):
    list_excel_path = os.listdir(dir_path)
    firstfile = True

    style = xl.easyxf('font:bold 1, color blue;')
    style1 = xl.easyxf('font:bold 1, color black;')

    wkbk = xl.Workbook()
    outsheet = wkbk.add_sheet('Sheet1')

    outrow_idx = 0
    for f in list_excel_path:
        fname = os.path.join(dir_path, f)
        insheet = xlrd.open_workbook(fname).sheets()[0]
        for row_idx in range(0 if firstfile else 1, insheet.nrows):
            for col_idx in range(insheet.ncols):
                if outrow_idx == 0:
                    outsheet.write(outrow_idx, col_idx, insheet.cell_value(row_idx, col_idx), style)
                else:
                    outsheet.write(outrow_idx, col_idx, insheet.cell_value(row_idx, col_idx), style1)
            outrow_idx += 1
        firstfile = False
        outrow_idx += 1
        

    wkbk.save(excel_file_path)

def write_to_excel2(original_filename, excel_file_path, static_dictionary, dynamic_dictionary):
    #print('dyn dictionary while writing to excel, ', dynamic_dictionary)
    dyn_cols =  ['Line No', 'Article Number', 'Order Number', 'Quantity', 'UOM', 'Description', 'Unit Price', 'Row Amount', 'Delivery Note']
    static_dictionary['originla_filename'] = original_filename
    table = dynamic_dictionary[1]
    row1 = []
    rows = []
    
    sta_keys = []
    for key in static_dictionary:
        sta_keys.append(key)
        val = static_dictionary[key]
        if type(val)==list:
            row1.append(val[0])
        else:
            row1.append(val)
    if table:
        row1 = row1 + table[0]
    else:
        row1 = row1 + ['']*len(dyn_cols)
    rows.append(row1)
    nsta = len(sta_keys)

    columns = sta_keys + dyn_cols
    if table:
        for tab in table[1:]:
            each_row = ['']*nsta + tab
            rows.append(each_row)
    exc_df = pd.DataFrame(data = rows)
    exc_df.columns = columns
    exc_df.to_excel(excel_file_path)


def stringFormate(data):
    data=str(data)
    formatedata=data.replace("\'","")
    return formatedata

def get_default_static_dict():
    defaut_conf = ""
    finaldict = {}
    finaldict['po_number'] = ['', defaut_conf]
    finaldict['invoice_number'] = ['', defaut_conf]
    finaldict['invoice_date'] = ['', defaut_conf]
    finaldict['tax_amount'] = ['', defaut_conf]
    finaldict["shipping_amount"] = ['', defaut_conf]
    finaldict['total_amount'] = ['', defaut_conf]
    finaldict['currency'] = ['', defaut_conf]
    finaldict['vendor_name'] = ['', defaut_conf]

    finaldict['invoice_address'] = ['', defaut_conf]
    finaldict['delivery_address'] = ['', defaut_conf]
    finaldict['account_number'] = ['', defaut_conf]
    finaldict['currency'] = ['', defaut_conf] 
    return finaldict

def save_output_to_json(sta, dyn, output_path):
    final_dict = {'static': sta, 'dynamic': dyn}
    fname = str(os.path.splitext(sta['file_name'])[0]) + '.json'
    fpath = os.path.join(output_path, fname)
    with open(fpath, 'w') as fjson:
        json.dump(final_dict, fjson)
    return


def get_default_dyn_dict():
	dyn = (['line_no', 'order_number', 'quantity', 'unit', 'description', 'unit_price', 'row_amount'],[])

	return dyn





def create_output_folder(text_files_path):
	info_folder_path = os.path.join(text_files_path, "outputs")
	if os.path.isdir(info_folder_path):
		shutil.rmtree(info_folder_path)
	os.makedirs(info_folder_path)
	return info_folder_path

def classify_scan_doc(text_files_path, info_folder_path, use_classifier=False):
    #print("text files path: ", text)
    if use_classifier:
	    correct_files_list = doc_classifier(text_files_path)
    else:
        correct_files_list = [f for f in os.listdir(text_files_path) if f.endswith('.txt')]
        print("correct_files_list", correct_files_list)
    for file_name in correct_files_list:
        if '_info.txt' not in file_name:
	        file_info = file_name.replace(".txt", "_info.txt")
        file_info=file_name
        shutil.copy2(os.path.join(text_files_path, file_name), os.path.join(info_folder_path, file_name))
        shutil.copy2(os.path.join(text_files_path, file_info), os.path.join(info_folder_path, file_info))
    invoices = True if correct_files_list else False
    return invoices

def classify_pdf_doc(text_files_path, info_folder_path, use_classifier=False):
    print("pdf location ", os.path.join(text_files_path,"pdftxt"))
    print(text_files_path)
    if os.path.exists(os.path.join(text_files_path,"pdftxt")):
        if use_classifier:
            correct_files_list = doc_classifier(os.path.join(text_files_path,"pdftxt"))
        else:
            correct_files_list = [f for f in os.listdir(os.path.join(text_files_path,"pdftxt")) if f.endswith('.txt')]
        pdftxtfolder = os.path.join(info_folder_path,'pdftxt')
        if os.path.exists(pdftxtfolder):
            shutil.rmtree(pdftxtfolder)
        os.mkdir(pdftxtfolder)
        for file_name in correct_files_list:
            shutil.copy2( os.path.join(os.path.join(text_files_path,"pdftxt"), file_name), os.path.join(pdftxtfolder, file_name))
    invoices = True if correct_files_list else False
    return invoices

