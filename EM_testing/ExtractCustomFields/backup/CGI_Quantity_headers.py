import re
import os
import numpy as np

def read_textfile(fileName):
    with open(fileName,encoding="utf-8") as f:
        text_data = f.read()
       # print(text_data)
    return text_data

def cgi_quantity_headers_extraction(text_data):
    data_dict={}
    vendor_name=activity_type=vessel_no=product_name=quantity=uom=file_no=date=job_location=ref_no=bill_to=''

    if re.search('RECAPITULATION',text_data,re.IGNORECASE):
        print("THIS IS INSPECTION DOCUMENT FOR QUANTITY")
        if re.search('Coastal Gulf & International, Inc.',text_data):
            print("VENDOR MATCHED !!!!!!!!!")
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
                ref_no=re.findall(r'EMCC Ref. #: (.*)',text_data)[0].split('File')[0].replace("  ","")
            except:
                ref_no=re.findall(r'ExxonMobil Ref. #: (.*)',text_data)[0].split('File')[0].replace("  ","")
                pass
            try:
                date=re.findall(r'Date: (.*)',text_data)[0].replace("  ","")
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
                quantity=re.findall(r'Barrels (.*)',text_data)[0].split("Barrels")[0].split('F')[-1].replace("  ","")
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
            #data_dict['status']=0

        return data_dict


#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/Extra_data/BR26799EMCC/BR26799EMCC.text"  #Chem-US
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/Extra_data/BR26970EMCC/BR26970EMCC.text"        #CHEM-US
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/Extra_data/BR26763ExxonMobil/BR26763ExxonMobil.text"   #US
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/Extra_data/103812ExxonMobil/103812ExxonMobil.text"    # US

#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/98889/98889.text"
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/99093/99093.text"
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/100139EMCC/100139EMCC.text"
path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/XBR12766EMCC/XBR12766EMCC.text"
#print(cgi_quantity_headers_extraction(read_textfile(path)))



