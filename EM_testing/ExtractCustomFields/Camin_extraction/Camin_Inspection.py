import os
import sys
import re
sys.path.insert(0, "../")
import datetime
import time



# filepath=r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_input/Camin/US/1130448/539888EXXM00-12rp0jpa6220-38-08-0538.pdf"
# fileName=filepath.split("/")[-1]
# Outpath=r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234"

# def pdftotext(filePath, fileName, Outpath):
#     # out_path= Outpath(outpath, folder_path)
#     outFilePath = os.path.join(Outpath, fileName.replace(".pdf", ".text"))
#     print(outFilePath)
#     # outFilePath = os.path.join(folderPath, fileName + ".text")
#     command = "pdftotext -layout '" + filePath + "' '" + outFilePath + "'"
#     os.system(command)
#     return outFilePath

def read_textfile(fileName):
    with open(fileName,encoding="utf-8") as f:
        text_data = f.read()
        # data=
       # print(text_data)
    return text_data

def camin_inspection_headers_extraction(text_data,uuid_doc):
    data_dict={}
    vendor_name=activity_type=vessel_no=product_name=quantity=uom=file_no=date=job_location=ref_no=bill_to=''

   
    try:
        vessel_no=re.findall(r'VESSEL (.*)',text_data)[0].split('Vessel')[0].replace(":","").replace("  ","")
    except:
        pass
    # try:    
    #     product_name=re.findall(r'Product: (.*)',text_data)[0].split('Client')[0].replace("  ","")
    # except:
    #     pass
    try:        
        activity_type=re.findall(r'MOVEMENT (.*)',text_data)[0].split("Voyage")[0].replace(":","").replace("  ","")
    except:
        pass
    try:
        ref_no=re.findall(r'REFERENCE N° (.*)',text_data)[0].replace(":","").replace("  ","")
    except:
        pass
    # try:
    #     date=re.findall(r'Report Date: (.*)',text_data)[0].split()[0]
    # except:
    #     pass
    try:
        file_no=re.findall(r'File N° (.*)',text_data)[0].split("LOP")[0].replace(":","").replace("  ","")
    except:
        pass
    try:
        job_location=re.findall(r'LOCATION (.*)',text_data)[0].split('Line')[0].replace(":","").replace("  ","")
    except:
        pass

    try: 
        bill_to=" ".join(re.findall(r'(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0]).split('Attention')[0].replace("  ","")
        # print(bill_to)
    except:
        pass
    try:
        vendor_name=" ".join(re.findall(r'Yours Sincerely (.*)\n(.*)\n(.*)\n(.*)',text_data))#.replace("  ","")
        print(vendor_name)
    except:
        pass
    
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
    if bill_to:
        data_dict['EmAffiliates']=bill_to
    data_dict['doc_uuid']=uuid_doc

    return data_dict


path=r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/539888EXXM00-12rp0jpa6220-38-08-0538.text"
print(camin_inspection_headers_extraction(read_textfile(path),"22222"))
# print(camin_inspection_headers_extraction(read_textfile(path),"22222"))

# pdftotext(filepath,fileName,Outpath)