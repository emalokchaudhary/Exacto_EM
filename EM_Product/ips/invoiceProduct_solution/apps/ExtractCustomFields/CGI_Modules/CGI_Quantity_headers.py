import re
import os
import numpy as np
import datefinder
from ExtractCustomFields.EM_logging import logger

def date_formater(date):
    try:
        if(date!=""):
            temp=datefinder.find_dates(date)
            d=''
            for match in temp:
                d=match
            d=d.date().strftime('%Y-%m-%d')
            date=str(d)
    except:
        print('issue in date conversion')
        pass
    return date

def read_textfile(fileName):
    with open(fileName,encoding="utf-8") as f:
        text_data = f.read()
    return text_data

def cgi_quantity_headers_extraction(text_data,uuid_doc):

    data_dict={}
    vendor_name=activity_type=vessel_no=product_name=quantity=uom=file_no=date=job_location=ref_no=bill_to=''
    
    try:
        vendor_name=" ".join(re.findall(r'(.*)\n(.*)',text_data)[0]).replace("  ","")
    except:
        pass
    try:
        vessel_no=re.findall(r'Vessel: (.*)',text_data)[0].split('Date')[0].replace("  ","")
    except:
        pass
    try:    
        product_name=re.findall(r'Product: (.*)',text_data)[0].split('Terminal')[0].replace("  ","")
    except:
        pass
    try:        
        activity_type=re.findall(r'Subject: (.*)',text_data)[0].split('Port')[0].replace("  ","")
    except:
        pass
    try:
        trip_number=''
        ref_no=re.findall(r'EMCC Ref. #: (.*)',text_data)[0].split('File')[0].replace("  ","")
        if(re.search(r'[a-z]+[-]*[0-9]+',ref_no,re.I)):
            trip_number=ref_no
            ref_no=''
    except:
        ref_no=re.findall(r'ExxonMobil Ref. #: (.*)',text_data)[0].split('File')[0].replace("  ","")
        if(re.search(r'[a-z]+[-]*[0-9]+',ref_no,re.I)):
            trip_number=ref_no
            ref_no=''
        pass
    try:
        date=re.findall(r'Date: (.*)',text_data)[0].replace("  ","")
        date=date_formater(date)
    except:
        pass
    try:
        file_no=re.findall(r'File Number: (.*)',text_data)[0].replace("  ","")
    except:
        pass
    try:
        job_location=re.findall(r'Port: (.*)',text_data)[0].replace("  ","")
    except:
        pass 
    try:
        quantity=re.findall(r'Barrels (.*)',text_data)[0].split("Barrels")[0].split('F')[-1].replace("  ","").split()[-1]
    except:
        pass   
    try:
        bill_to=" ".join(re.findall(r'(.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0]).replace("  ","")
    except:
        pass                               
    
    if vendor_name:
        data_dict['VendorName']=vendor_name
    if vessel_no:
        data_dict['VesselName']=vessel_no
    if product_name:
        data_dict['ProductName']=product_name
    if activity_type:
        data_dict['ActivityType']=activity_type
    if ref_no:
        data_dict['NominationKey']=ref_no
    if trip_number:
        data_dict['TripNumber']=trip_number
    if date:
        data_dict['JobDate']=date
    if job_location:
        data_dict['JobLocation']=job_location
    if file_no:
        data_dict['VendorInternalReferencenumber']=file_no
    if quantity:
        data_dict['NominatedQuantity']=quantity
    if quantity:
        data_dict['UnitOfMeasure']="Barrels"
    if bill_to:
        data_dict['EmAffiliates']=bill_to
    data_dict['doc_uuid']= uuid_doc
    
    for i in data_dict:
        data_dict[i]=re.sub(r'^(\s+)',"",data_dict[i])
        data_dict[i]=re.sub(r'\s+$',"",data_dict[i])
    logger.info(f'CGI Quantity Header data - {data_dict}')
    return data_dict


#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/Extra_data/BR26799EMCC/BR26799EMCC.text"  #Chem-US
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/Extra_data/BR26970EMCC/BR26970EMCC.text"        #CHEM-US
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/Extra_data/BR26763ExxonMobil/BR26763ExxonMobil.text"   #US
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/Extra_data/103812ExxonMobil/103812ExxonMobil.text"    # US

#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/98889/98889.text"
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/99093/99093.text"
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/100139EMCC/100139EMCC.text"
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/XBR12766EMCC/XBR12766EMCC.text"
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/CGI/CHEM-US/308022/104110_EMCCReport.text"
# path=r'/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/CGI/CHEM-US/300801/BT11076_EMCC.text'
# print(cgi_quantity_headers_extraction(read_textfile(path),'2323'))



