import re
import os
import numpy as np

def read_textfile(fileName):
    with open(fileName,encoding="utf-8") as f:
        text_data = f.read()
       # print(text_data)
    return text_data

def cgi_quality_headers_extraction(text_data):
    data_dict={}
    vendor_name=activity_type=vessel_no=product_name=quantity=uom=file_no=date=job_location=ref_no=bill_to=''

    if re.search('Certificate of Analysis',text_data,re.IGNORECASE):
        print("THIS IS INSPECTION DOCUMENT FOR QUALITY")
        if re.search('cgi@coastalgulf.com',text_data):
            print("VENDOR MATCHED !!!!!!!!!")
            try:
                vessel_no=re.findall(r'Vessel/Equipment: (.*)',text_data)[0].split('File')[0].replace("  ","")
            except:
                pass
            try:    
                product_name=re.findall(r'Product: (.*)',text_data)[0].split('Client')[0].replace("  ","")
            except:
                pass
            try:        
                activity_type=re.findall(r'Subject: (.*)',text_data)[0].replace("  ","")
            except:
                pass
            try:
                ref_no=re.findall(r'Client Reference: (.*)',text_data)[0].replace("  ","")
            except:
                pass
            try:
                date=re.findall(r'Report Date: (.*)',text_data)[0].split()[0]
            except:
                pass
            try:
                file_no=re.findall(r'File Number: (.*)',text_data)[0].replace("  ","")
            except:
                pass
            try:
                job_location=re.findall(r'Terminal: (.*)',text_data)[0].split('Client')[0].replace("  ","")
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
            
            #data_dict['status']=0

        return data_dict


#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/100150-264_WEB264_VGO_B20201223001_XOM_FINALupdated/100150-264_WEB264_VGO_B20201223001_XOM_FINALupdated.text"  #US
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/102634_HTCO3100_Raffinate_B20210412002_XOM_Final/102634_HTCO3100_Raffinate_B20210412002_XOM_Final.text"     #US
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/103951_GM10061019_ResidV_B20210607003_XOM_Final/103951_GM10061019_ResidV_B20210607003_XOM_Final.text"      #US
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/102738_Chem3248_Benzene_B20210415002_EMCC_Final/102738_Chem3248_Benzene_B20210415002_EMCC_Final.text"      #Chem-US
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/101794_Chem3712_Benzene_B20210305003_EMCC_Final/101794_Chem3712_Benzene_B20210305003_EMCC_Final.text"      #Chem-US
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/BR26799_Chem3213_AromaticConcentrate_EMCC_Final/BR26799_Chem3213_AromaticConcentrate_EMCC_Final.text"      #Chem-US
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/BR26970_Chem3245_Benzene_B20201024002_EMCC_Final/BR26970_Chem3245_Benzene_B20201024002_EMCC_Final.text"     #Chem-US  date coming with time exception case
path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/9907599093_217_CSOMCB_L20201105004_Exxon_Final/9907599093_217_CSOMCB_L20201105004_Exxon_Final.text"       #US
print(cgi_quality_headers_extraction(read_textfile(path)))



